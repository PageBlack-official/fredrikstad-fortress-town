// ---- klikk, peker, huskort, hjem, styreflate og feilsøking. Dra, klyp, vri, vipp, hjul og dobbeltklikk er MapLibres egne. ----
const ray=new THREE.Raycaster(); const ptr=new THREE.Vector2(); let valgt=null, klikkTimer=null, hover=null;
const kort=document.getElementById('kort'); const hjem=document.getElementById('hjem');
function treffHus(x,y){ ptr.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); ray.setFromCamera(ptr,cam);
  const hit=ray.intersectObjects(city.children,true).find(h=>h.object.isMesh); if(!hit) return null;
  let g=hit.object; while(g.parent!==city) g=g.parent; return {g, p:hit.point}; }
function velg(x,y){
  const h=treffHus(x,y);
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
  const s=new THREE.Vector3(h.p.x,0,h.p.z).project(cam);
  const kortTopp = 1-2*Math.max(0.2, (kort.offsetTop||innerHeight*0.72)/innerHeight);   // kortets plass uten innglidningen
  if(s.y < kortTopp+0.12 || Math.abs(s.x)>0.85 || s.y>0.88){
    const px=(s.x+1)/2*innerWidth, py=(1-s.y)/2*innerHeight;
    map.panBy([px-innerWidth/2, py-innerHeight*0.4], {duration:700, easing:t=>1-Math.pow(1-t,3)});
  }
}
function hjemNaa(){ map.easeTo({...hjemVisning(), duration:900, easing:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}); if(valgt){valgt.userData.lift=false; valgt=null;} kort.classList.remove('vis'); }
hjem.onclick=()=>{ overta(); hjemNaa(); };
addEventListener('keydown',e=>{ if(e.key==='Escape'){ overta(); hjemNaa(); } });
// ett klikk velger et hus (ventes 300 ms så et dobbeltklikk kan zoome i stedet)
map.on('click', e=>{ if(!introDone) return; clearTimeout(klikkTimer); const p=e.point; klikkTimer=setTimeout(()=>velg(p.x,p.y),300); });
map.on('dblclick', ()=>clearTimeout(klikkTimer));
// peker over et hus (bare mus): huset løfter seg litt
let sisteHover=0;
map.on('mousemove', e=>{ if(e.originalEvent.buttons || map.isMoving() || !introDone){ if(hover){ hover=null; map.getCanvas().style.cursor=''; } return; }
  const n=performance.now(); if(n-sisteHover<45) return; sisteHover=n;
  const h=treffHus(e.point.x,e.point.y); hover=h?h.g:null; map.getCanvas().style.cursor=hover?'pointer':''; });
map.on('mouseout', ()=>{ hover=null; map.getCanvas().style.cursor=''; });
// styreflate på Mac: to fingre flytter kartet (som Apple og Google Maps), klyp zoomer (ctrl+hjul), et musehjul zoomer.
// Én gest er én ting: første hendelse avgjør, hendelser innen 120 ms arver valget.
const gest={t:0,hjul:false};
map.getCanvasContainer().addEventListener('wheel', e=>{
  if(e.ctrlKey) return;                                   // klyp på styreflaten = zoom, MapLibre tar den
  const naa=performance.now();
  let hjul = e.deltaMode!==0 || (e.deltaX===0 && e.wheelDeltaY && e.wheelDeltaY%120===0 && e.wheelDeltaY!==-3*e.deltaY);
  if(gest.t && naa-gest.t<120) hjul=gest.hjul;
  gest.t=naa; gest.hjul=hjul; dbgLogg(e,hjul);
  if(hjul) return;                                        // musehjul = zoom, MapLibre tar den
  e.preventDefault(); e.stopImmediatePropagation(); overta();
  map.panBy([e.deltaX, e.deltaY], {animate:false});       // innholdet følger fingrene
}, {capture:true, passive:false});
function visHjem(){ const c=tilModell(map.getCenter()); const borte = Math.abs(map.getZoom()-Z_HJEM)>0.07 || Math.hypot(c[0]-START[0], c[1]-START[1])>8 || Math.abs(((map.getBearing()+AZ0_GRADER+540)%360)-180)>4; hjem.classList.toggle('vis', introDone && borte); }
map.on('move', visHjem); map.on('moveend', visHjem);
kort.querySelector('.lukk').onclick=()=>{kort.classList.remove('vis'); if(valgt){valgt.userData.lift=false; valgt=null;}};
// feilsøkingsrute (tast d): bildefrekvens, tegnetilstand og styreflatehendelser som tall. Taster s/a/x/p prøver stillbildekvalitet.
const dbg={paa:false, rader:[], el:null, fps:[]};
function dbgLogg(e,hjul){ if(!dbg.paa) return; dbg.rader.push(`${(performance.now()%100000|0)} dx${e.deltaX.toFixed(1)} dy${e.deltaY.toFixed(1)} w${e.wheelDeltaY} m${e.deltaMode} ${e.ctrlKey?'ctrl ':''}${hjul?'ZOOM':'flytt'}`); if(dbg.rader.length>40) dbg.rader.shift(); }
function dbgTegn(naa){ if(!dbg.paa) return; dbg.fps.push(naa); while(dbg.fps.length&&naa-dbg.fps[0]>1000) dbg.fps.shift();
  const pt=window.__pt||{};
  dbg.el.textContent=`fps ${dbg.fps.length}  zoom ${map.getZoom().toFixed(2)} (x${kam.zoomfaktor.toFixed(2)})  pitch ${kam.pitch.toFixed(0)}  bearing ${kam.bearing.toFixed(0)}  perfNivaa ${perfNivaa}  skalaBeveg ${skalaBeveg.toFixed(2)}  stille ${naa-sistBeveg>300?1:0}  ss ${ssStille} ao ${aoStille}`
    +String.fromCharCode(10)+`3D ${pt.scene|0} ms  blekk ${pt.blekk|0} ms  kall ${pt.kall}  tri ${pt.tri}`+String.fromCharCode(10)+dbg.rader.join(String.fromCharCode(10)); }
addEventListener('keydown',e=>{ if(!dbg.paa) return; if(e.key==='s'){ ssStille=ssStille===4?2:ssStille===2?1:4; } if(e.key==='a'){ aoStille=aoStille===14?7:aoStille===7?0:14; } if(e.key==='x'){ skalaStille=skalaStille===1?0.75:1; } if(e.key==='p'){ speil.av(); } });
addEventListener('keydown',e=>{ if(e.key==='d'&&!e.metaKey&&!e.ctrlKey){ dbg.paa=!dbg.paa; if(!dbg.el){ dbg.el=document.createElement('pre'); dbg.el.style.cssText='position:fixed;left:8px;top:8px;z-index:9;margin:0;padding:8px;font:11px/1.25 ui-monospace,monospace;background:rgba(255,255,255,.92);color:#222;max-height:92vh;overflow:hidden;pointer-events:none;border-radius:6px'; document.body.appendChild(dbg.el); } dbg.el.style.display=dbg.paa?'block':'none'; } });
