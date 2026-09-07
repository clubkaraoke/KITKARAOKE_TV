(function(){
  const cfg=window.KIT_CONFIG||{};
  const listeners=new Set();
  function emit(type,data){listeners.forEach(fn=>{try{fn(type,data)}catch(_){}})}
  function on(fn){listeners.add(fn);return()=>listeners.delete(fn)}
  function randomCode(){return String(Math.floor(1000+Math.random()*9000))}
  async function createReceiver(){
    if(cfg.mode==="live"&&cfg.apiBase){
      const r=await fetch(cfg.apiBase+"/api/pair/create",{method:"POST"});
      if(!r.ok) throw new Error("No se pudo crear sesión");
      return await r.json();
    }
    const code=randomCode();
    localStorage.setItem("kit_preview_receiver",JSON.stringify({code,createdAt:Date.now(),name:"TV PREVIEW"}));
    window.addEventListener("storage",e=>{
      if(e.key==="kit_preview_claim"&&e.newValue){
        const v=JSON.parse(e.newValue);
        if(v.code===code) emit("paired",v);
      }
    });
    return {code,receiverId:"preview-"+code,mode:"preview"};
  }
  async function claim(code,name){
    code=String(code||"").trim();
    if(!/^\d{4}$/.test(code)) throw new Error("El código debe tener 4 dígitos");
    if(cfg.mode==="live"&&cfg.apiBase){
      const r=await fetch(cfg.apiBase+"/api/pair/claim",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code,name})});
      if(!r.ok) throw new Error("Código inválido o vencido");
      return await r.json();
    }
    const rec=JSON.parse(localStorage.getItem("kit_preview_receiver")||"null");
    const ok=!!rec&&rec.code===code;
    const payload={code,name:name||"TV SALA",claimedAt:Date.now(),ok};
    localStorage.setItem("kit_preview_claim",JSON.stringify(payload));
    if(!ok) throw new Error("En PREVIEW, abre primero /tv en este mismo navegador");
    return {ok:true,receiverId:"preview-"+code,name:payload.name,mode:"preview"};
  }
  window.KIT_PAIR={createReceiver,claim,on,mode:cfg.mode};
})();