const $=s=>document.querySelector(s);
function deviceId(){
 let id=localStorage.getItem("kit_device_id");
 if(!id){id=(crypto.randomUUID?crypto.randomUUID():"dev-"+Date.now()+"-"+Math.random().toString(16).slice(2));localStorage.setItem("kit_device_id",id)}
 return id;
}
async function api(path,opts={}){
 const r=await fetch(path,{...opts,headers:{"Content-Type":"application/json",...(opts.headers||{})}});
 let data={}; try{data=await r.json()}catch(_){}
 if(!r.ok) throw new Error(data.detail||("HTTP "+r.status));
 return data;
}
async function activate(){
 const license=$("#license").value.trim(),deviceName=$("#deviceName").value.trim()||"PC CLIENTE";
 const st=$("#status");st.className="status";st.textContent="Validando licencia...";
 try{
  const r=await api("/api/auth/activate",{method:"POST",body:JSON.stringify({license,deviceId:deviceId(),deviceName})});
  st.className="status ok";st.textContent="Licencia válida. Entrando...";
  setTimeout(()=>location.href=r.redirect||"/app",350);
 }catch(e){st.className="status err";st.textContent=e.message}
}
async function trial(){
 const st=$("#status");st.className="status";st.textContent="Generando licencia de prueba...";
 try{const r=await api("/api/dev/trial",{method:"POST"});$("#license").value=r.license;st.className="status ok";st.textContent="Trial creado: "+r.days+" días. Ahora pulsa ACTIVAR."}
 catch(e){st.className="status err";st.textContent=e.message}
}
async function loadMe(){
 try{
  const r=await api("/api/me");
  $("#licenseLabel").textContent=r.license.label;
  $("#plan").textContent=r.license.plan;
  $("#devices").textContent=r.license.devicesUsed+" / "+r.license.maxDevices;
  $("#maxTvs").textContent=r.license.maxTvs;
  $("#expires").textContent=r.license.expiresAt?new Date(r.license.expiresAt*1000).toLocaleString():"Sin vencimiento";
 }catch(e){location.href="/"}
}
async function pairTv(){
 const code=$("#tvCode").value.trim(),name=$("#tvName").value.trim()||"TV SALA",st=$("#tvStatus");
 st.className="status";st.textContent="Vinculando "+code+"...";
 try{const r=await api("/api/tv/claim",{method:"POST",body:JSON.stringify({code,name})});st.className="status ok";st.textContent=(r.name||name)+" conectada ✓";loadLogs()}
 catch(e){st.className="status err";st.textContent=e.message;loadLogs()}
}
async function loadLogs(){
 const box=$("#logs"); if(!box)return;
 try{const r=await api("/api/logs");box.textContent=r.logs.map(x=>new Date(x.ts*1000).toLocaleString()+" | "+x.level+" | "+x.category+" | "+x.message).join("\n")||"Sin eventos todavía."}
 catch(e){box.textContent="ERROR | "+e.message}
}
async function logout(){try{await api("/api/auth/logout",{method:"POST"})}catch(_){}location.href="/"}
