// ---- klikk, dobbeltklikk, hjul, klyp og tilbake til hele byen ----
const ray=new THREE.Raycaster(); const ptr=new THREE.Vector2(); let down=null, valgt=null, klikkTimer=null, sisteTrykk=0, hover=null;
const kort=document.getElementById('kort'); const hjem=document.getElementById('hjem');
function treffHus(x,y){ ptr.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); ray.setFromCamera(ptr,cam);
  const hit=ray.intersectObjects(city.children,true).find(h=>h.object.isMesh); if(!hit) return null;
  let g=hit.object; while(g.parent!==city) g=g.parent; return {g, p:hit.point}; }
function bakkepunkt(e){ const h=treffHus(e.clientX,e.clientY); if(h) return new THREE.Vector3(h.p.x,0,h.p.z); return bakkeVed(e.clientX,e.clientY); }
function velg(e){
  const h=treffHus(e.clientX,e.clientY);
  if(valgt){valgt.userData.lift=false; valgt=null;}
  if(!h){kort.classList.remove('vis'); return;}
  const g=h.g; valgt=g; g.userData.lift=true;
  const b=g.userData.b;
  kort.querySelector('h2').textContent = b.navn || b.adr || 'Bygg i Gamlebyen';
  kort.querySelector('.a').textContent = b.adr || (b.tekst ? 'Fra kartbrosjyren til Visit Fredrikstad (2015)' : ''); // OSM-typen (engelsk, f.eks. «office») vises ikke
  kort.querySelector('.b').textContent = b.tekst || 'Historie, bilder og bruk kommer her.';
  const f=kort.querySelector('.farge'); f.innerHTML='';
  if(b.vegg){ f.innerHTML += `<i style="background:rgb(${b.vegg})"></i>Godkjent fasadefarge`; }
  kort.classList.add('vis');
  // står huset under kortet eller utenfor bildet, glir kartet rolig så huset blir synlig over kortet
  const B=new THREE.Vector3(h.p.x,0,h.p.z); const s=B.clone().project(cam);
  const kortTopp = 1-2*Math.max(0.2, (kort.offsetTop||innerHeight*0.72)/innerHeight);   // kortets plass uten innglidningen
  if(s.y < kortTopp+0.12 || Math.abs(s.x)>0.85 || s.y>0.88){
    const G=bakkeVed(innerWidth/2, innerHeight*0.4); if(G) flyTo(new THREE.Vector3(controls.target.x+B.x-G.x,0,controls.target.z+B.z-G.z), cam.zoom, undefined, {dur:700});
  }
}
function zoomInn(e, ut){
  const p=bakkepunkt(e); if(!p) return;
  const z = ut ? Math.max(1, cam.zoom/2.2) : Math.min(controls.maxZoom, cam.zoom*2.2);
  if(ut && z<=1.01) flyTo(HOME.target, 1, undefined, {e:ease});
  else flyTo(null, z, undefined, {anker:p, e:easeUt, dur:560});   // punktet man dobbeltklikket står stille mens kartet zoomer
}
function hjemNaa(){ flyTo(HOME.target, HOME.zoom, HOME.az); if(valgt){valgt.userData.lift=false; valgt=null;} kort.classList.remove('vis'); }
hjem.onclick=()=>{ overta(); hjemNaa(); };
addEventListener('keydown',e=>{ if(e.key==='Escape'){ overta(); hjemNaa(); } });
const el=renderer.domElement;
// hjul og styreflate: myk zoom mot pekeren
const gest={t:0,hjul:false};
const dbg={paa:false, rader:[], el:null, fps:[]};
function dbgLogg(e,hjul){ if(!dbg.paa) return; dbg.rader.push(`${(performance.now()%100000|0)} dx${e.deltaX.toFixed(1)} dy${e.deltaY.toFixed(1)} w${e.wheelDeltaY} m${e.deltaMode} ${e.ctrlKey?'ctrl ':''}${hjul?'ZOOM':'flytt'}`); if(dbg.rader.length>40) dbg.rader.shift(); }
function dbgTegn(naa){ if(!dbg.paa) return; dbg.fps.push(naa); while(dbg.fps.length&&naa-dbg.fps[0]>1000) dbg.fps.shift();
  dbg.el.textContent=`fps ${dbg.fps.length}  zoom ${cam.zoom.toFixed(2)}  perfNivaa ${perfNivaa}  skalaBeveg ${skalaBeveg.toFixed(2)}  stille ${naa-sistBeveg>300?1:0}  anim ${anim?1:0}  ss ${ssStille} ao ${aoStille} skalaS ${skalaStille}  skygge ${sun.shadow.needsUpdate?1:0}\n3D ${(window.__pt||{}).scene|0} ms  blekk ${(window.__pt||{}).blekk|0} ms  kall ${(window.__pt||{}).kall}  tri ${(window.__pt||{}).tri}  tegnet ${naa-sistTegnet<20?1:0}`+String.fromCharCode(10)+dbg.rader.join(String.fromCharCode(10)); }
addEventListener('keydown',e=>{ if(!dbg.paa) return; if(e.key==='s'){ ssStille=ssStille===4?2:ssStille===2?1:4; } if(e.key==='a'){ aoStille=aoStille===14?7:aoStille===7?0:14; } if(e.key==='x'){ skalaStille=skalaStille===1?0.75:1; } if(e.key==='p'){ speil.av(); } });
addEventListener('keydown',e=>{ if(e.key==='d'&&!e.metaKey&&!e.ctrlKey){ dbg.paa=!dbg.paa; if(!dbg.el){ dbg.el=document.createElement('pre'); dbg.el.style.cssText='position:fixed;left:8px;top:8px;z-index:9;margin:0;padding:8px;font:11px/1.25 ui-monospace,monospace;background:rgba(255,255,255,.92);color:#222;max-height:92vh;overflow:hidden;pointer-events:none;border-radius:6px'; document.body.appendChild(dbg.el); } dbg.el.style.display=dbg.paa?'block':'none'; } });
el.addEventListener('wheel',e=>{ e.preventDefault(); overta(); stoppAnim();
  // vanlig kartpraksis på Mac: sveip med to fingre (styreflate/Magic Mouse) flytter kartet, klyp zoomer,
  // et vanlig musehjul (hakk) zoomer. Hjulhakk kjennes på wheelDeltaY i hele 120-steg uten sidelengs bevegelse.
  // én gest er én ting: første hendelse avgjør om det er flytting (to fingre) eller zoom (hjul/klyp); hendelser innen 120 ms arver valget
  const naa=performance.now();
  let hjul = !e.ctrlKey && (e.deltaMode!==0 || (e.deltaX===0 && e.wheelDeltaY && e.wheelDeltaY%120===0 && e.wheelDeltaY!==-3*e.deltaY));
  if(!e.ctrlKey && gest.t && naa-gest.t<120) hjul=gest.hjul;
  gest.t=naa; gest.hjul=hjul; dbgLogg(e,hjul);
  if(!e.ctrlKey && !hjul){
    const P0=bakkeVed(e.clientX,e.clientY), P1=bakkeVed(e.clientX-e.deltaX, e.clientY-e.deltaY);   // innholdet følger fingrene
    if(P0&&P1) flytt(P0.x-P1.x, P0.z-P1.z); zoomMaal=cam.zoom; return;
  }
  const dy=e.deltaMode===1? e.deltaY*16 : e.deltaMode===2? e.deltaY*400 : e.deltaY;
  const f=Math.exp(-dy*(e.ctrlKey?0.012:0.0018));                       // ctrl = klyp på styreflate
  zoomMaal=THREE.MathUtils.clamp(zoomMaal*f, controls.minZoom, controls.maxZoom);
  zoomAnker=bakkeVed(e.clientX,e.clientY);
},{passive:false});
el.addEventListener('pointerdown',e=>{ const varIntro=!introDone; overta(); down=varIntro?null:[e.clientX,e.clientY]; stoppAnim(); zoomMaal=cam.zoom; });   // klikket som stopper introen velger ikke et hus
el.addEventListener('pointerup',e=>{
  if(!introDone||!down) return; if(Math.hypot(e.clientX-down[0],e.clientY-down[1])>(e.pointerType==='touch'?12:6)) return;
  if(fingre.size>1 || toFinger) return;   // ett fingertrykk er et klikk (fingeren slippes først i slipp())
  const naa=performance.now();
  if(naa-sisteTrykk<300){ clearTimeout(klikkTimer); sisteTrykk=0; zoomInn(e, e.shiftKey||e.altKey); return; }
  sisteTrykk=naa; const ev={clientX:e.clientX, clientY:e.clientY};
  klikkTimer=setTimeout(()=>velg(ev),300);
});
// peker over et hus (bare mus): huset løfter seg litt
let sisteHover=0;
el.addEventListener('pointermove',e=>{ if(e.pointerType!=='mouse' || e.buttons || anim || !introDone) { if(e.buttons && hover){ hover=null; el.style.cursor=''; } return; }
  const n=performance.now(); if(n-sisteHover<45) return; sisteHover=n;
  const h=treffHus(e.clientX,e.clientY); hover=h?h.g:null; el.style.cursor=hover?'pointer':''; });
el.addEventListener('pointerleave',()=>{ hover=null; el.style.cursor=''; });
// to fingre: klyp = zoom rundt midtpunktet, vri = snu byen, flytt = flytte kartet, parallelt opp/ned = vippe. Kort trykk med to fingre = zoom ut.
let fingre=new Map(), toFinger=null;
el.addEventListener('pointerdown',e=>{ if(e.pointerType==='mouse') return; fingre.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(fingre.size===2){ const [a,b]=[...fingre.values()]; toFinger={t0:performance.now(), d:Math.hypot(b.x-a.x,b.y-a.y), v:Math.atan2(b.y-a.y,b.x-a.x), m:{x:(a.x+b.x)/2,y:(a.y+b.y)/2}, flyttet:0}; clearTimeout(klikkTimer); } });
el.addEventListener('pointermove',e=>{ if(!fingre.has(e.pointerId)) return; fingre.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(fingre.size!==2 || !toFinger) return;
  const [a,b]=[...fingre.values()]; const d=Math.hypot(b.x-a.x,b.y-a.y), v=Math.atan2(b.y-a.y,b.x-a.x), m={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
  // to fingre som glir parallelt opp/ned = vippe kartet (som Google og Apple Maps); ellers følger kartet fingrene
  const mdx=m.x-toFinger.m.x, mdy=m.y-toFinger.m.y, a0=[...fingre.values()];
  const parallellVipp = Math.abs(mdy)>2*Math.abs(mdx) && Math.abs(Math.log(d/toFinger.d))<0.01 && Math.abs(a.y-b.y)<0.35*Math.abs(a.x-b.x)+60;
  if(parallellVipp){ const off=cam.position.clone().sub(controls.target); const sp=new THREE.Spherical().setFromVector3(off);
    sp.phi=THREE.MathUtils.clamp(sp.phi-mdy*0.006, controls.minPolarAngle, controls.maxPolarAngle); off.setFromSpherical(sp); cam.position.copy(controls.target).add(off); cam.lookAt(controls.target); }
  else { const P0=bakkeVed(toFinger.m.x,toFinger.m.y), P1=bakkeVed(m.x,m.y); if(P0&&P1) flytt(P0.x-P1.x, P0.z-P1.z); }
  // klyp
  const A=bakkeVed(m.x,m.y); if(toFinger.d>0) settZoom(cam.zoom*d/toFinger.d, A); zoomMaal=cam.zoom;
  // vri: snu kameraet rundt midtpunktet
  let dv=v-toFinger.v; if(dv>Math.PI) dv-=2*Math.PI; if(dv<-Math.PI) dv+=2*Math.PI;
  if(A && Math.abs(dv)>0.0005){ const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0), dv);   // innholdet følger fingrene
    const ot=controls.target.clone().sub(A).applyQuaternion(q), oc=cam.position.clone().sub(A).applyQuaternion(q);
    controls.target.copy(A).add(ot); cam.position.copy(A).add(oc); cam.lookAt(controls.target); }
  toFinger.flyttet+=Math.abs(Math.log(d/toFinger.d))*120+Math.hypot(m.x-toFinger.m.x,m.y-toFinger.m.y)+Math.abs(dv)*120;
  toFinger.d=d; toFinger.v=v; toFinger.m=m; });
function slipp(e){ if(!fingre.has(e.pointerId)) return; fingre.delete(e.pointerId);
  if(toFinger && fingre.size<2){ const kort_=performance.now()-toFinger.t0<260 && toFinger.flyttet<14; toFinger=null; down=null;
    if(kort_ && introDone){ clearTimeout(klikkTimer); const z=Math.max(1,cam.zoom/2.2); if(z<=1.01) flyTo(HOME.target,1); else flyTo(null, z, undefined, {anker:controls.target.clone(), e:easeUt, dur:520}); } } }
el.addEventListener('pointerup',slipp); el.addEventListener('pointercancel',slipp);
el.addEventListener('dblclick',e=>e.preventDefault());
function visHjem(){ const borte = Math.abs(Math.log(cam.zoom))>0.05 || controls.target.distanceTo(HOME.target)>8 || Math.abs(controls.getAzimuthalAngle()-HOME.az)>0.08; hjem.classList.toggle('vis', introDone && borte); }
kort.querySelector('.lukk').onclick=()=>{kort.classList.remove('vis'); if(valgt){valgt.userData.lift=false; valgt=null;}};
speil.size(); addEventListener('resize',()=>speil.size());
tick();
