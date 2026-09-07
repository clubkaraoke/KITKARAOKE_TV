import hashlib
import json
import os
import secrets
import sqlite3
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR","/data"))
DB_PATH = DATA_DIR / "kitkaraoke_client.db"
LICENSE_PEPPER = os.getenv("LICENSE_PEPPER","dev-only-change-me")
SESSION_TTL = int(os.getenv("SESSION_TTL_SECONDS","2592000"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE","0") == "1"
TV_API_BASE = os.getenv("TV_API_BASE","http://host.docker.internal:8791")
ENVIRONMENT = os.getenv("ENVIRONMENT","app1")
DEV_TRIALS = os.getenv("DEV_TRIALS","1") == "1"

app = FastAPI(title="KITKARAOKE APP", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")

class ActivateBody(BaseModel):
    license: str = Field(min_length=8, max_length=80)
    deviceId: str = Field(min_length=6, max_length=120)
    deviceName: str = Field(default="PC CLIENTE", min_length=1, max_length=80)

class TvClaimBody(BaseModel):
    code: str = Field(pattern=r"^\d{4}$")
    name: str = Field(default="TV SALA", min_length=1, max_length=60)

def now() -> int:
    return int(time.time())

def db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def hash_license(code:str)->str:
    normalized=code.strip().upper()
    return hashlib.sha256((LICENSE_PEPPER+"|"+normalized).encode()).hexdigest()

def hash_session(token:str)->str:
    return hashlib.sha256((LICENSE_PEPPER+"|session|"+token).encode()).hexdigest()

def audit(conn, license_id, category, level, message):
    conn.execute("insert into audit_log(license_id,ts,category,level,message) values(?,?,?,?,?)",(license_id,now(),category,level,message[:500]))
    conn.commit()

def init_db():
    conn=db()
    conn.executescript("""
    create table if not exists licenses(
      id integer primary key autoincrement,
      code_hash text not null unique,
      label text not null,
      plan text not null default 'TRIAL',
      status text not null default 'active',
      expires_at integer,
      max_devices integer not null default 1,
      max_tvs integer not null default 1,
      created_at integer not null
    );
    create table if not exists activations(
      id integer primary key autoincrement,
      license_id integer not null,
      device_id text not null,
      device_name text not null,
      first_seen integer not null,
      last_seen integer not null,
      unique(license_id,device_id)
    );
    create table if not exists sessions(
      token_hash text primary key,
      license_id integer not null,
      device_id text not null,
      expires_at integer not null,
      created_at integer not null
    );
    create table if not exists audit_log(
      id integer primary key autoincrement,
      license_id integer,
      ts integer not null,
      category text not null,
      level text not null,
      message text not null
    );
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

def require_session(session:str|None):
    if not session:
        raise HTTPException(401,"Sesión no iniciada")
    conn=db()
    row=conn.execute("""select s.*,l.label,l.plan,l.status,l.expires_at,l.max_devices,l.max_tvs
      from sessions s join licenses l on l.id=s.license_id where s.token_hash=?""",(hash_session(session),)).fetchone()
    if not row or row["expires_at"] <= now() or row["status"]!="active":
        conn.close()
        raise HTTPException(401,"Sesión vencida")
    if row["expires_at"] and row["expires_at"] <= now():
        conn.close()
        raise HTTPException(403,"Licencia vencida")
    return conn,row

def set_session_cookie(response:Response, token:str):
    response.set_cookie("kit_session",token,max_age=SESSION_TTL,httponly=True,samesite="lax",secure=COOKIE_SECURE,path="/")

@app.middleware("http")
async def headers(request:Request,call_next):
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="same-origin"
    response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"]="no-store"
    return response

@app.get("/health")
def health():
    return {"ok":True,"service":"kitkaraoke-app1","environment":ENVIRONMENT}

@app.get("/")
def home():
    return FileResponse(ROOT/"web"/"index.html")

@app.get("/app")
@app.get("/app/")
def dashboard():
    return FileResponse(ROOT/"web"/"app.html")

@app.get("/api/me")
def me(kit_session:str|None=Cookie(default=None)):
    conn,row=require_session(kit_session)
    devices=conn.execute("select count(*) c from activations where license_id=?",(row["license_id"],)).fetchone()["c"]
    conn.close()
    return {"ok":True,"license":{"label":row["label"],"plan":row["plan"],"expiresAt":row["expires_at"],"maxDevices":row["max_devices"],"maxTvs":row["max_tvs"],"devicesUsed":devices},"deviceId":row["device_id"]}

@app.post("/api/auth/activate")
def activate(body:ActivateBody,response:Response):
    conn=db()
    lic=conn.execute("select * from licenses where code_hash=?",(hash_license(body.license),)).fetchone()
    if not lic:
        audit(conn,None,"AUTH","WARN","Licencia inválida")
        conn.close()
        raise HTTPException(404,"Licencia inválida")
    if lic["status"]!="active":
        audit(conn,lic["id"],"AUTH","WARN","Licencia desactivada")
        conn.close()
        raise HTTPException(403,"Licencia desactivada")
    if lic["expires_at"] and lic["expires_at"] <= now():
        audit(conn,lic["id"],"AUTH","WARN","Licencia vencida")
        conn.close()
        raise HTTPException(403,"Licencia vencida")

    existing=conn.execute("select * from activations where license_id=? and device_id=?",(lic["id"],body.deviceId)).fetchone()
    if not existing:
        count=conn.execute("select count(*) c from activations where license_id=?",(lic["id"],)).fetchone()["c"]
        if count >= lic["max_devices"]:
            audit(conn,lic["id"],"AUTH","WARN","Límite de dispositivos alcanzado")
            conn.close()
            raise HTTPException(409,"Esta licencia ya alcanzó su límite de dispositivos")
        conn.execute("insert into activations(license_id,device_id,device_name,first_seen,last_seen) values(?,?,?,?,?)",(lic["id"],body.deviceId,body.deviceName,now(),now()))
    else:
        conn.execute("update activations set device_name=?,last_seen=? where id=?",(body.deviceName,now(),existing["id"]))

    token=secrets.token_urlsafe(32)
    conn.execute("insert into sessions(token_hash,license_id,device_id,expires_at,created_at) values(?,?,?,?,?)",(hash_session(token),lic["id"],body.deviceId,now()+SESSION_TTL,now()))
    audit(conn,lic["id"],"AUTH","INFO",f"Activación correcta en {body.deviceName}")
    conn.commit(); conn.close()
    set_session_cookie(response,token)
    return {"ok":True,"plan":lic["plan"],"redirect":"/app"}

@app.post("/api/auth/logout")
def logout(response:Response,kit_session:str|None=Cookie(default=None)):
    if kit_session:
        conn=db()
        conn.execute("delete from sessions where token_hash=?",(hash_session(kit_session),))
        conn.commit(); conn.close()
    response.delete_cookie("kit_session",path="/")
    return {"ok":True}

@app.post("/api/dev/trial")
def dev_trial():
    if not DEV_TRIALS:
        raise HTTPException(404,"No disponible")
    code="KTK-"+secrets.token_hex(2).upper()+"-"+secrets.token_hex(2).upper()+"-"+secrets.token_hex(2).upper()
    conn=db()
    conn.execute("insert into licenses(code_hash,label,plan,status,expires_at,max_devices,max_tvs,created_at) values(?,?,?,?,?,?,?,?)",(hash_license(code),"LICENCIA DE PRUEBA","TRIAL","active",now()+7*86400,1,1,now()))
    lic_id=conn.execute("select last_insert_rowid() id").fetchone()["id"]
    audit(conn,lic_id,"LICENSE","INFO","Licencia TRIAL de 7 días creada en APP1")
    conn.commit(); conn.close()
    return {"ok":True,"license":code,"days":7}

@app.post("/api/tv/claim")
def tv_claim(body:TvClaimBody,kit_session:str|None=Cookie(default=None)):
    conn,row=require_session(kit_session)
    payload=json.dumps({"code":body.code,"name":body.name,"controllerId":"app1-"+row["device_id"][:32]}).encode()
    req=urllib.request.Request(TV_API_BASE+"/api/pair/claim",data=payload,headers={"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=5) as r:
            data=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: detail=json.loads(e.read().decode()).get("detail","No se pudo vincular la TV")
        except Exception: detail="No se pudo vincular la TV"
        audit(conn,row["license_id"],"TV","WARN",f"Vinculación fallida: {detail}")
        conn.close()
        raise HTTPException(e.code,detail)
    except Exception:
        audit(conn,row["license_id"],"TV","ERROR","TV API no disponible")
        conn.close()
        raise HTTPException(503,"Servidor de TV no disponible")
    audit(conn,row["license_id"],"TV","INFO",f"TV vinculada: {body.name}")
    conn.close()
    return data

@app.get("/api/logs")
def logs(kit_session:str|None=Cookie(default=None)):
    conn,row=require_session(kit_session)
    rows=conn.execute("select ts,category,level,message from audit_log where license_id=? order by id desc limit 100",(row["license_id"],)).fetchall()
    conn.close()
    return {"ok":True,"logs":[dict(x) for x in rows]}
