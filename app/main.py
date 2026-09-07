import asyncio
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from redis.asyncio import Redis

ROOT = Path(__file__).resolve().parent.parent
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PAIR_TTL = int(os.getenv("PAIR_TTL_SECONDS", "300"))
RECEIVER_TTL = int(os.getenv("RECEIVER_TTL_SECONDS", "86400"))
APP_VERSION = os.getenv("APP_VERSION", "tv1-dev")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("kitkaraoke-tv")

app = FastAPI(title="KITKARAOKE TV", version=APP_VERSION, docs_url=None, redoc_url=None)
redis = Redis.from_url(REDIS_URL, decode_responses=True)
receiver_sockets: Dict[str, WebSocket] = {}

class ClaimRequest(BaseModel):
    code: str = Field(pattern=r"^\d{4}$")
    name: str = Field(default="TV SALA", min_length=1, max_length=60)
    controllerId: str | None = Field(default=None, max_length=120)

async def rate_limit(request: Request, bucket: str, limit: int, seconds: int) -> None:
    ip = request.client.host if request.client else "unknown"
    key = f"rate:{bucket}:{ip}:{int(time.time()) // seconds}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, seconds + 2)
    if count > limit:
        log.warning("RATE_LIMIT bucket=%s ip=%s", bucket, ip)
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espera un momento.")

def now_ms() -> int:
    return int(time.time() * 1000)

async def load_receiver(receiver_id: str) -> dict | None:
    raw = await redis.get(f"receiver:{receiver_id}")
    return json.loads(raw) if raw else None

async def save_receiver(receiver_id: str, payload: dict, ttl: int = RECEIVER_TTL) -> None:
    await redis.set(f"receiver:{receiver_id}", json.dumps(payload), ex=ttl)

async def allocate_code(receiver_id: str) -> str:
    for _ in range(80):
        code = f"{secrets.randbelow(9000) + 1000:04d}"
        ok = await redis.set(f"pair:code:{code}", receiver_id, ex=PAIR_TTL, nx=True)
        if ok:
            return code
    raise HTTPException(status_code=503, detail="No se pudo generar código. Intenta nuevamente.")

@app.on_event("startup")
async def startup() -> None:
    await redis.ping()
    log.info("APP_START version=%s pair_ttl=%s", APP_VERSION, PAIR_TTL)

@app.on_event("shutdown")
async def shutdown() -> None:
    await redis.aclose()
    log.info("APP_STOP version=%s", APP_VERSION)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/health")
async def health():
    await redis.ping()
    return {"ok": True, "service": "kitkaraoke-tv1", "version": APP_VERSION}

@app.get("/api/version")
async def version():
    return {"version": APP_VERSION, "environment": "tv1"}

@app.post("/api/pair/create")
async def create_pair(request: Request):
    await rate_limit(request, "pair-create", 30, 60)
    receiver_id = secrets.token_urlsafe(18)
    token = secrets.token_urlsafe(32)
    code = await allocate_code(receiver_id)
    created = now_ms()
    payload = {
        "receiverId": receiver_id,
        "receiverToken": token,
        "code": code,
        "status": "waiting",
        "name": "TV",
        "createdAt": created,
        "expiresAt": created + PAIR_TTL * 1000,
    }
    await save_receiver(receiver_id, payload)
    log.info("PAIR_CREATE receiver=%s code=%s expires=%ss", receiver_id[:8], code, PAIR_TTL)
    return {"code": code, "receiverId": receiver_id, "receiverToken": token, "expiresAt": payload["expiresAt"], "mode": "live"}

@app.post("/api/pair/claim")
async def claim_pair(body: ClaimRequest, request: Request):
    await rate_limit(request, "pair-claim", 40, 60)
    code_key = f"pair:code:{body.code}"
    receiver_id = await redis.get(code_key)
    if not receiver_id:
        log.warning("PAIR_CLAIM_FAIL code=%s reason=invalid_or_expired", body.code)
        raise HTTPException(status_code=404, detail="Código inválido o vencido")

    payload = await load_receiver(receiver_id)
    if not payload or payload.get("status") != "waiting":
        await redis.delete(code_key)
        log.warning("PAIR_CLAIM_FAIL code=%s reason=session_unavailable", body.code)
        raise HTTPException(status_code=409, detail="La sesión ya no está disponible")

    payload["status"] = "paired"
    payload["name"] = body.name.strip() or "TV SALA"
    payload["controllerId"] = body.controllerId or secrets.token_urlsafe(12)
    payload["pairedAt"] = now_ms()

    await redis.delete(code_key)
    await save_receiver(receiver_id, payload)

    ws = receiver_sockets.get(receiver_id)
    if ws:
        try:
            await ws.send_json({"type": "paired", "receiverId": receiver_id, "name": payload["name"], "pairedAt": payload["pairedAt"]})
        except Exception:
            log.warning("PAIR_NOTIFY_FAIL receiver=%s", receiver_id[:8])

    log.info("PAIR_CLAIM_OK receiver=%s name=%s", receiver_id[:8], payload["name"])
    return {"ok": True, "receiverId": receiver_id, "name": payload["name"], "controllerId": payload["controllerId"], "mode": "live"}

@app.get("/api/pair/status/{receiver_id}")
async def pair_status(receiver_id: str, token: str, request: Request):
    await rate_limit(request, "pair-status", 120, 60)
    payload = await load_receiver(receiver_id)
    if not payload or not secrets.compare_digest(payload.get("receiverToken", ""), token):
        raise HTTPException(status_code=404, detail="Receptor no encontrado")
    return {"receiverId": receiver_id, "status": payload.get("status"), "name": payload.get("name"), "expiresAt": payload.get("expiresAt")}

@app.websocket("/ws/receiver/{receiver_id}")
async def receiver_ws(websocket: WebSocket, receiver_id: str, token: str):
    payload = await load_receiver(receiver_id)
    if not payload or not secrets.compare_digest(payload.get("receiverToken", ""), token):
        await websocket.close(code=4404)
        return
    await websocket.accept()
    receiver_sockets[receiver_id] = websocket
    log.info("TV_WS_CONNECTED receiver=%s", receiver_id[:8])
    try:
        await websocket.send_json({"type": "status", "status": payload.get("status", "waiting"), "name": payload.get("name", "TV")})
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=25)
                if message == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat", "at": now_ms()})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        log.warning("TV_WS_ERROR receiver=%s error=%s", receiver_id[:8], type(exc).__name__)
    finally:
        if receiver_sockets.get(receiver_id) is websocket:
            receiver_sockets.pop(receiver_id, None)
        log.info("TV_WS_DISCONNECTED receiver=%s", receiver_id[:8])

app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")

@app.get("/")
async def home():
    return FileResponse(ROOT / "index.html")

@app.get("/tv")
@app.get("/tv/")
async def tv():
    return FileResponse(ROOT / "tv" / "index.html")

@app.get("/control")
@app.get("/control/")
async def control():
    return FileResponse(ROOT / "control" / "index.html")

@app.get("/diagnostico")
@app.get("/diagnostico/")
async def diagnostico():
    return FileResponse(ROOT / "diagnostico" / "index.html")
