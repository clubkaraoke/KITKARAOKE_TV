(function(){
  const cfg=window.KIT_CONFIG||{};
  const listeners=new Set();
  let socket=null;
  let heartbeat=null;
  let currentSession=null;

  function emit(type,data){listeners.forEach(fn=>{try{fn(type,data)}catch(_){}})}
  function on(fn){listeners.add(fn);return()=>listeners.delete(fn)}
  function api(path){return (cfg.apiBase||"")+path}
  function wsUrl(path){
    if(cfg.wsBase) return cfg.wsBase+path;
    const proto=location.protocol==="https:"?"wss:":"ws:";
    return proto+"//"+location.host+path;
  }

  function connectReceiverWs(session){
    currentSession=session;
    if(socket){try{socket.close()}catch(_){}}
    socket=new WebSocket(wsUrl("/ws/receiver/"+encodeURIComponent(session.receiverId)+"?token="+encodeURIComponent(session.receiverToken)));
    socket.onopen=()=>{
      emit("ws",{status:"connected"});
      clearInterval(heartbeat);
      heartbeat=setInterval(()=>{if(socket&&socket.readyState===1)socket.send("ping")},15000);
    };
    socket.onmessage=e=>{
      if(e.data==="pong") return;
      try{
        const m=JSON.parse(e.data);
        if(m.type==="paired") emit("paired",m);
        else emit(m.type||"message",m);
      }catch(_){}
    };
    socket.onclose=()=>{clearInterval(heartbeat);emit("ws",{status:"disconnected"})};
    socket.onerror=()=>emit("ws",{status:"error"});
  }

  function sendReceiver(message){
    if(!socket||socket.readyState!==1) return false;
    try{
      socket.send(typeof message==="string"?message:JSON.stringify(message));
      return true;
    }catch(_){return false}
  }

  async function createReceiver(){
    const r=await fetch(api("/api/pair/create"),{method:"POST",headers:{"Accept":"application/json"}});
    if(!r.ok) throw new Error("No se pudo crear el código de TV");
    const session=await r.json();
    localStorage.setItem("kit_tv_receiver",JSON.stringify(session));
    connectReceiverWs(session);
    return session;
  }

  async function claim(code,name){
    code=String(code||"").trim();
    if(!/^\d{4}$/.test(code)) throw new Error("El código debe tener 4 dígitos");
    let controllerId=localStorage.getItem("kit_controller_id");
    if(!controllerId){
      controllerId=(crypto.randomUUID?crypto.randomUUID():"ctrl-"+Date.now()+"-"+Math.random().toString(16).slice(2));
      localStorage.setItem("kit_controller_id",controllerId);
    }
    const r=await fetch(api("/api/pair/claim"),{
      method:"POST",
      headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify({code,name:name||"TV SALA",controllerId})
    });
    let data={};
    try{data=await r.json()}catch(_){}
    if(!r.ok) throw new Error(data.detail||"Código inválido o vencido");
    localStorage.setItem("kit_paired_tv",JSON.stringify(data));
    return data;
  }

  function getSession(){return currentSession}

  window.KIT_PAIR={createReceiver,claim,on,sendReceiver,getSession,mode:cfg.mode};
})();
