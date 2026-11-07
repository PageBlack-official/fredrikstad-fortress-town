import * as THREE from 'three';
import { SENERE, TILSTAND, registrer } from './tilstand.js';
import { AZ0_GRADER, DATA, Q0, Z_HJEM, cam, gl2, kam, map, tilLngLat, tilModell, zoomFor } from './00_oppsett.js';
import { post } from './01_etterbehandling.js';
import { dekning } from './02_lys.js';
import { KVAL, feilsokTast } from './kvalitet.js';
import { city } from './05_bygg.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { husDeler } from './07_vinduer-dører-og-porter.js';
import { START, speil } from './14_speilinger-i-vannet.js';
import { BEV, SLIPP, glidKamera, hjulZoom, slippLogg } from './15_bevegelse.js';
import { lenkeSkriv } from './15_lenke.js';
import { hjemVisning, introIgjen, overta } from './15_loop.js';
// ---- klikk, peker, huskort, hjem, styreflate og feilsøking. Dra, klyp, vri, vipp og hjul er MapLibres egne; dobbeltklikk er vårt. ----
const ray=new THREE.Raycaster(); const ptr=new THREE.Vector2(); let valgt=null, hover=null;
const kort=document.getElementById('kort');
// adresser og virksomheter per bygg, slått opp på byggets faste id (data/adresser.json, data/virksomheter.json; verktoy/adresser.py)
const perBygg=liste=>{ const m=new Map(); (liste||[]).forEach(x=>{ if(x.skjul) return; if(!m.has(x.bygg_id)) m.set(x.bygg_id,[]); m.get(x.bygg_id).push(x); }); return m; };
const ADRESSER=perBygg(DATA.adresser), VIRKSOMHETER=perBygg(DATA.virksomheter); const BYGG_ID=new Map((DATA.bygg||[]).map(x=>[x.id,x])); const hjem=document.getElementById('hjem');
// treff: strålen mot alt i byen; i de sammenslåtte nettene gir trekantnummeret hvilket bygg som ble truffet (husDeler, 07)
function byggFraTreff(hit){
  if(hit.object.isInstancedMesh && hit.object.geometry.getAttribute('aBygg')){ const k=hit.object.geometry.getAttribute('aBygg').getX(hit.instanceId)-1; return k>=0 ? buildings.find(g=>g.userData.i===k) : null; }
  const f=hit.faceIndex*3;
  for(const [i,deler] of husDeler){ for(const d of deler){ if(d.mesh===hit.object && f>=d.start && f<d.start+d.antall) return buildings.find(g=>g.userData.i===i); } }
  let g=hit.object; while(g.parent && g.parent!==city) g=g.parent; return g.parent===city && g.userData && g.userData.b ? g : null;
}
// city.updateMatrixWorld: egne grupper (kirka, porthus) står på husfoten via gruppa (07.11); uten tegning (?tegn=0, flyt-testen) blir
// gruppenes verdensmatrise ellers aldri regnet, og strålen bommer
function treffHus(x,y){ ptr.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); ray.setFromCamera(ptr,cam); city.updateMatrixWorld();
  const hit=ray.intersectObjects(city.children,true).find(h=>h.object.isMesh); if(!hit) return null;
  const g=byggFraTreff(hit); return g ? {g, p:hit.point} : null; }
// testinngang (07.11): hva treffer et klikk i skjermpunktet (x, y)? Navn/id på de fem nærmeste treffene
window.__treff=(x,y)=>{ ptr.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); ray.setFromCamera(ptr,cam); city.updateMatrixWorld();
  return ray.intersectObjects(city.children,true).filter(h=>h.object.isMesh).slice(0,5).map(h=>{ const g=byggFraTreff(h); return {obj:h.object.type+(h.object.isInstancedMesh?'I':''), y:+h.point.y.toFixed(2), d:+h.distance.toFixed(1), bygg:g&&g.userData.b?(g.userData.b.id||g.userData.b.navn):null}; }); };
// bygget som boks (til kamera og kort): egne grupper måles, sammenslåtte bygg regnes ut fra grunnrisset og høyden
function husBoks(g){ if(g.userData.spesiell || !g.userData.b || !g.userData.b.p) return new THREE.Box3().setFromObject(g);
  const bb=new THREE.Box3(); const f=g.userData.fot||0; g.userData.b.p.forEach(([x,y])=>{ bb.expandByPoint(new THREE.Vector3(x,f,-y)); bb.expandByPoint(new THREE.Vector3(x,f+g.userData.h+g.position.y,-y)); }); return bb; }
// ---- huskortet (oppdrag 15): klikk -> huset løfter seg og kameraet glir inn, kortet glir inn (mobil: bunnark fra bunnen, som
// Apple/Google Maps; bred skjerm: sidepanel fra venstre). Tilbake (×, Esc, trykk utenfor, nettleserens/Androids tilbake) går samme vei ut:
// kortet glir ut, og kameraet glir tilbake dit det stod, så lenge du ikke har flyttet kartet selv i mellomtida. Varighet og kurver: 15_bevegelse.
const kortInnhold=kort.querySelector('.innhold');
const kort_={apent:false, forKamera:null, egenFlytt:false, historikk:false, ferge:null, vedLukk:[], vedVelg:[]};   // vedLukk/vedVelg: andre moduler (24_sok, 26_turer) rydder når kortet lukkes eller et hus velges
const SIDEPANEL=window.matchMedia('(min-width: 720px)');
const kameraNaa=()=>({center:map.getCenter(), zoom:map.getZoom(), bearing:map.getBearing(), pitch:map.getPitch()});
function fyllKort(b){
  const adr=(ADRESSER.get(b.id)||[]).map(a=>a.adresse), her=VIRKSOMHETER.get(b.id)||[];
  kort.querySelector('h2').textContent = b.navn || adr[0] || b.adr || 'Bygg i Gamlebyen';
  kort.querySelector('.a').textContent = (b.navn ? adr.join(', ') : adr.slice(1).join(', ')) || b.adr || (b.tekst ? 'Fra kartbrosjyren til Visit Fredrikstad (2015)' : ''); // OSM-typen (engelsk, f.eks. «office») vises ikke
  kort.querySelector('.b').textContent = b.tekst || '';   // tomt kort fremfor plassholder: det som vises, er ferdig 
  const liste=(ul,vs)=>{ ul.innerHTML=''; vs.forEach(v=>{ const li=document.createElement('li'); li.textContent=v.navn; ul.appendChild(li); }); };
  // bygg delt i fløyer (husdeling «felles_tak», Tøihuset): fløyas egne steder øverst; de andre fløyenes og de uten kjent plass under «Også i …»
  const fl=b.floyer||[], hele=v=>v.hele_bygget;
  const ogsa=fl.flatMap(i=>(VIRKSOMHETER.get(i)||[]).filter(v=>i!==b.id||hele(v))).sort((x,y)=>(hele(x)?1:0)-(hele(y)?1:0));
  liste(kort.querySelector('.her'), her.filter(v=>!(fl.length&&hele(v))));
  liste(kort.querySelector('.ogsa'), ogsa);
  kort.querySelector('.ogsa-t').textContent = ogsa.length ? `Også i ${(b.navn||'bygget').split(',')[0]}` : '';
  const mb=(b.matrikkel&&b.matrikkel[0]) ? b : (b.floyer||[]).map(i=>BYGG_ID.get(i)).find(x=>x&&x.matrikkel&&x.matrikkel[0]) || b;   // fløyene deler bygningsnummeret
  const m=mb.matrikkel&&mb.matrikkel[0];   // statens nøkkel (Matrikkelen): bygningsnummer og kulturminne
  kort.querySelector('.id').textContent = m ? `Bygningsnr. ${m.bygningsnummer}${mb.matrikkel.some(x=>x.kulturminne)?' • Kulturminne':''}` : '';
  const f=kort.querySelector('.farge'); f.innerHTML='';
  if(b.vegg){ f.innerHTML += `<i style="background:rgb(${b.vegg})"></i>Godkjent fasadefarge`; }
}
// den delen av skjermen kortet ikke dekker (layoutmål uten transform, så det gjelder også mens kortet glir inn)
function friFlate(){
  if(!kort_.apent) return {x0:0, y0:0, x1:innerWidth, y1:innerHeight};
  if(SIDEPANEL.matches) return {x0:kort.offsetLeft+kort.offsetWidth+16, y0:0, x1:innerWidth, y1:innerHeight};
  return {x0:0, y0:0, x1:innerWidth, y1:Math.max(innerHeight*0.35, kort.offsetTop-12)};
}
// kameraet glir inn mot huset: midt i den frie flaten, minst husZoom nær (aldri ut). Står huset alt der, står kameraet stille.
function glidTilHus(g){
  const c=husBoks(g).getCenter(new THREE.Vector3()); const ll=tilLngLat(c.x,-c.z);
  const fri=friFlate(), mx=(fri.x0+fri.x1)/2, my=(fri.y0+fri.y1)/2;
  const zoom=Math.max(map.getZoom(), zoomFor(BEV.husZoom)); const s=map.project(ll);
  if(Math.hypot(s.x-mx, s.y-my) < 0.12*Math.min(fri.x1-fri.x0, fri.y1-fri.y0) && zoom-map.getZoom()<0.05) return;
  glidKamera({center:ll, zoom, offset:[mx-innerWidth/2, my-innerHeight/2]}, 'hus');
}
// et punkt uten eget bygg (stedene i søket, 24_sok): den som kaller fyller kortet; kameraet glir til punktet midt i den frie flaten
function velgPunkt(fyll, x, y){
  kort_.vedVelg.forEach(f=>f(null));
  if(valgt){ valgt.userData.lift=false; valgt=null; }
  kort_.ferge=null;
  if(!kort_.apent){ kort_.forKamera=kameraNaa(); kort_.egenFlytt=false; fyll(); visKort(true); }
  else { fyll(); kortInnhold.animate([{opacity:0},{opacity:1}], {duration:BEV.kort.innhold, easing:'ease-out'}); }
  const ll=tilLngLat(x,y), fri=friFlate(), mx=(fri.x0+fri.x1)/2, my=(fri.y0+fri.y1)/2;
  glidKamera({center:ll, zoom:Math.max(map.getZoom(), zoomFor(BEV.husZoom)), offset:[mx-innerWidth/2, my-innerHeight/2]}, 'hus');
  lenkeSkriv();
}
// byfergene (22_byferga): kortet viser hvor båten er og de neste avgangene, og fylles på nytt mens det står åpent
function fyllFergeKort(id){ const k=SENERE.ferge.kort(id); if(!k) return;
  kort.querySelector('h2').textContent=k.tittel; kort.querySelector('.a').textContent=k.a; kort.querySelector('.b').textContent=k.b;
  const ul=kort.querySelector('.her'); ul.innerHTML=''; k.linjer.forEach(t=>{ const li=document.createElement('li'); li.textContent=t; ul.appendChild(li); });
  kort.querySelector('.ogsa').innerHTML=''; kort.querySelector('.ogsa-t').textContent=''; kort.querySelector('.farge').innerHTML=''; kort.querySelector('.id').textContent=k.id; }
function velgFerge(id){
  if(valgt){ valgt.userData.lift=false; valgt=null; }
  const nytt=kort_.ferge!==id; kort_.ferge=id;
  if(!kort_.apent){ kort_.forKamera=kameraNaa(); kort_.egenFlytt=false; fyllFergeKort(id); visKort(true); }
  else if(nytt){ fyllFergeKort(id); kortInnhold.animate([{opacity:0},{opacity:1}], {duration:BEV.kort.innhold, easing:'ease-out'}); }
  lenkeSkriv();
}
setInterval(()=>{ if(kort_.apent && kort_.ferge) fyllFergeKort(kort_.ferge); }, 10000);   // nye tider fra Entur fyller kortet med en gang (22_byferga)
function treffFerge(x,y){ ptr.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); ray.setFromCamera(ptr,cam); return SENERE.ferge.treff(ray); }
function velgHus(g){
  kort_.ferge=null; kort_.vedVelg.forEach(f=>f(g));
  if(valgt===g) return;
  if(valgt) valgt.userData.lift=false;
  valgt=g; g.userData.lift=true;
  if(!kort_.apent){ kort_.forKamera=kameraNaa(); kort_.egenFlytt=false; fyllKort(g.userData.b); visKort(true); }
  else { fyllKort(g.userData.b); kortInnhold.animate([{opacity:0},{opacity:1}], {duration:BEV.kort.innhold, easing:'ease-out'}); }   // nytt hus i åpent kort: innholdet tones over, kortet står
  glidTilHus(g); lenkeSkriv();   // hus= i lenka (15_lenke)
}
function visKort(vis){
  kort_.apent=vis; kort.style.transform='';
  kort.classList.toggle('vis', vis); kort.setAttribute('aria-hidden', vis?'false':'true');
  if(vis && !kort_.historikk){ try{ window.history.pushState({...(window.history.state||{}), kort:1}, ''); kort_.historikk=true; }catch(e){ /* innebygd uten historikk */ } }
}
// lukk: tilbake=true glir kameraet tilbake dit det stod før kortet (om du ikke har flyttet kartet selv); fraHistorikk: nettleserens tilbake
function lukkKort({tilbake=true, fraHistorikk=false}={}){
  if(valgt){ valgt.userData.lift=false; valgt=null; }
  kort_.ferge=null; kort_.vedLukk.forEach(f=>f());
  if(!kort_.apent) return;
  visKort(false);
  if(tilbake && kort_.forKamera && !kort_.egenFlytt) glidKamera(kort_.forKamera, 'tilbake');
  kort_.forKamera=null;
  if(kort_.historikk){ kort_.historikk=false; if(!fraHistorikk){ try{ window.history.back(); }catch(e){ /* innebygd */ } } }
  lenkeSkriv();   // hus= ut av lenka (15_lenke; etter tilbake skrives den på nytt ved popstate)
}
kort.addEventListener('transitionend', ()=>{ kort.style.transitionDuration=''; });   // farten fra et fingerkast gjelder bare den ene overgangen
addEventListener('popstate', ()=>{ if(kort_.apent){ kort_.historikk=false; lukkKort({fraHistorikk:true}); } });
// flytter du kartet selv mens kortet er åpent, blir kameraet der du la det når kortet lukkes (som Apple og Google Maps)
map.on('movestart', e=>{ if(e.originalEvent && kort_.apent) kort_.egenFlytt=true; });
function hjemNaa(){ lukkKort({tilbake:false}); glidKamera({...hjemVisning(), offset:[0,0]}, 'hjem'); }
// «Hele Gamlebyen» spiller introen på nytt (Vegar), på mobil og bred skjerm; Esc glir bare hjem som før
hjem.onclick=()=>{ lukkKort({tilbake:false}); if(TILSTAND.introDone) introIgjen(); else overta(); }; window.__hjem=()=>{ overta(); hjemNaa(); };
// Esc: lukker kortet først (samme vei ut), neste Esc går hjem
addEventListener('keydown',e=>{ if(e.key==='Escape'){ overta(); if(kort_.apent) lukkKort(); else hjemNaa(); } });
kort.querySelector('.lukk').onclick=()=>lukkKort();
// ---- klikk og trykk: ett klikk på et hus velger det med en gang; to klikk/trykk innen 300 ms zoomer inn mot punktet (shift = ut).
// Vi gjenkjenner dobbeltklikk selv fra klikkene, så det virker likt med mus og finger (MapLibres dobbeltklikk-zoom er av, se under).
// Klikk utenfor et hus lukker kortet, men først når det ikke kom et klikk til (ellers ville et dobbeltklikk lukke og zoome samtidig).
const klikk={t:-1e9, x:0, y:0}; let lukkTimer=null;
map.on('click', e=>{ if(!TILSTAND.introDone) return;
  const naa=performance.now(), p=e.point;
  const dobbel = naa-klikk.t < BEV.dobbelVindu && Math.hypot(p.x-klikk.x, p.y-klikk.y) < BEV.dobbelAvstand;
  if(dobbel){ klikk.t=-1e9; clearTimeout(lukkTimer); overta(); glidKamera({zoom: map.getZoom()+(e.originalEvent.shiftKey?-1:1), around:e.lngLat}, 'dobbel'); return; }
  klikk.t=naa; klikk.x=p.x; klikk.y=p.y;
  const fg=treffFerge(p.x,p.y); if(fg){ velgFerge(fg.id); return; }
  const h=treffHus(p.x,p.y); if(performance.now()-SLIPP.t<600) slippLogg(`klikk (${e.originalEvent.type}) ${h?'traff hus '+(h.g.userData.b.id||''):'traff ikke hus'}`);
  if(h) velgHus(h.g); else if(kort_.apent){ clearTimeout(lukkTimer); lukkTimer=setTimeout(()=>lukkKort(), BEV.dobbelVindu); }
});
// MapLibres dobbeltklikk/dobbelttrykk (300 ms, bråstopp) er av; vår glir på 800 ms med glid (regel 11)
map.doubleClickZoom.disable();
// ---- bunnarket på mobil: dra kortet ned for å lukke. Kortet følger fingeren; slippes det, regnes hvor det ville endt med farten
// (Apple, «Designing Fluid Interfaces»: prosjiser endepunktet), og det glir videre ned eller tilbake med farten det hadde.
const ark={id:null, y0:0, dy:0, spor:[]};
kort.addEventListener('pointerdown', e=>{ if(SIDEPANEL.matches || !kort_.apent || e.target.closest('button,a') || e.button>0) return;
  ark.id=e.pointerId; ark.y0=e.clientY; ark.dy=0; ark.spor=[[performance.now(), e.clientY]]; kort.setPointerCapture(e.pointerId); kort.style.transition='none'; });
kort.addEventListener('pointermove', e=>{ if(e.pointerId!==ark.id) return;
  const dy=e.clientY-ark.y0; ark.dy = dy>0 ? dy : dy*0.15;   // opp gir motstand (gummistrikk), ned følger fingeren
  kort.style.transform=`translateY(${ark.dy}px)`; ark.spor.push([performance.now(), e.clientY]); if(ark.spor.length>6) ark.spor.shift(); });
function arkSlipp(e){ if(e.pointerId!==ark.id) return; ark.id=null; kort.style.transition='';
  const [t0,y0]=ark.spor[0], [t1,y1]=ark.spor[ark.spor.length-1]; const v = t1>t0 ? (y1-y0)/(t1-t0) : 0;   // px/ms
  const ende = ark.dy + v*250;   // prosjisert endepunkt
  if(ende > kort.offsetHeight*0.4){ const igjen=kort.offsetHeight+24-ark.dy;
    kort.style.transitionDuration = Math.round(THREE.MathUtils.clamp(v>0 ? igjen/v : BEV.kort.ut, 120, BEV.kort.ut))+'ms';   // farten fra fingeren tas med
    kort.style.transform=''; lukkKort(); }
  else kort.style.transform='';   // tilbake på plass (kortets egen overgang, fra der fingeren slapp)
}
kort.addEventListener('pointerup', arkSlipp); kort.addEventListener('pointercancel', arkSlipp);
// peker over et hus (bare mus): huset løfter seg litt
let sisteHover=0;
map.on('mousemove', e=>{ if(e.originalEvent.buttons || map.isMoving() || !TILSTAND.introDone){ if(hover){ hover=null; map.getCanvas().style.cursor=''; } return; }
  const n=performance.now(); if(n-sisteHover<45) return; sisteHover=n;
  const h=treffHus(e.point.x,e.point.y); hover=h?h.g:null; map.getCanvas().style.cursor=(hover||treffFerge(e.point.x,e.point.y))?'pointer':''; });
map.on('mouseout', ()=>{ hover=null; map.getCanvas().style.cursor=''; });
// styreflate på Mac: to fingre flytter kartet (som Apple og Google Maps), klyp zoomer (ctrl+hjul), et musehjul zoomer.
// Én gest er én ting: første hendelse avgjør, hendelser innen 120 ms arver valget.
const gest={t:0,hjul:false};
map.getCanvasContainer().addEventListener('wheel', e=>{
  if(e.ctrlKey || e.metaKey) return;                      // klyp på styreflaten (ctrl) eller ⌘ og rull (Magic Mouse) = zoom, MapLibre tar den
  const naa=performance.now();
  let hjul = e.deltaMode!==0 || (e.deltaX===0 && e.wheelDeltaY && e.wheelDeltaY%120===0 && e.wheelDeltaY!==-3*e.deltaY);
  if(gest.t && naa-gest.t<120) hjul=gest.hjul;
  gest.t=naa; gest.hjul=hjul; dbgLogg(e,hjul);
  if(hjul){                                               // musehjul = zoom, jevn (15_bevegelse: hjulZoom), ikke MapLibres utslag per hakk
    e.preventDefault(); e.stopImmediatePropagation(); if(kort_.apent) kort_.egenFlytt=true;
    const px = e.deltaMode===1 ? e.deltaY*40 : e.deltaMode===2 ? e.deltaY*800 : e.deltaY;   // linjer/sider til piksler; ett hakk ≈ 100 px
    hjulZoom.hakk(e, -px/100*BEV.hjul.perHakk); return; }
  e.preventDefault(); e.stopImmediatePropagation(); overta();
  map.panBy([e.deltaX, e.deltaY], {animate:false});       // innholdet følger fingrene
}, {capture:true, passive:false});
function visHjem(){ const c=tilModell(map.getCenter()); const borte = Math.abs(map.getZoom()-Z_HJEM)>0.07 || Math.hypot(c[0]-START[0], c[1]-START[1])>8 || Math.abs(((map.getBearing()+AZ0_GRADER+540)%360)-180)>4; hjem.classList.toggle('vis', TILSTAND.introDone && borte); }
map.on('move', visHjem); map.on('moveend', visHjem);
// feilsøkingsrute (tast d): bildefrekvens, tegnetilstand og styreflatehendelser som tall. Taster s/a/x/p prøver stillbildekvalitet.
const dbg={paa:false, rader:[], el:null, fps:[], pek:{ned:0,flytt:0,opp:0,sist:'',knapper:0,type:''}};
// pekerhendelser som når kartet (for å se om dra virker der kartet vises)
['pointerdown','pointermove','pointerup'].forEach(t=>map.getCanvasContainer().addEventListener(t,e=>{ if(!dbg.paa) return; dbg.pek[t==='pointerdown'?'ned':t==='pointermove'?'flytt':'opp']++; dbg.pek.sist=`${t} ${e.clientX|0},${e.clientY|0}`; dbg.pek.knapper=e.buttons; dbg.pek.type=e.pointerType; },{capture:true,passive:true}));
function dbgLogg(e,hjul){ if(!dbg.paa) return; dbg.rader.push(`${(performance.now()%100000|0)} dx${e.deltaX.toFixed(1)} dy${e.deltaY.toFixed(1)} w${e.wheelDeltaY} m${e.deltaMode} ${e.ctrlKey?'ctrl ':''}${hjul?'ZOOM':'flytt'}`); if(dbg.rader.length>40) dbg.rader.shift(); }
// bildefrekvens i siste bevegelse (dra, animasjon): telles mens kartet beveger seg og står igjen etterpå, så den kan leses av i ro
const fart={i:false, t0:0, n:0, sist:''};
function dbgTegn(naa){ if(!dbg.paa) return; dbg.fps.push(naa); while(dbg.fps.length&&naa-dbg.fps[0]>1000) dbg.fps.shift();
  const pt=window.__pt||{};
  if(map.isMoving()){ if(!fart.i){ fart.i=true; fart.t0=naa; fart.n=0; fart.s=0; fart.b=0; fart.f=0; fart.sk=0; fart.r=0; fart.m=0; fart.k0=window.__kartBilder; fart.v0=window.__vaareBilder; } fart.n++; fart.s+=pt.scene||0; fart.b+=pt.blekk||0; fart.f+=pt.fxaa||0; fart.sk+=pt.skygge||0; fart.r+=window.__ramme||0; fart.m+=window.__mellom||0; }
  else if(fart.i){ fart.i=false; const ms=naa-fart.t0, n=fart.n; if(ms>150) fart.sist=`siste bevegelse ${ms|0} ms, ${n} bilder = ${(n*1000/ms).toFixed(0)}/s  (snitt per bilde: 3D ${(fart.s/n).toFixed(0)} ms, blekk ${(fart.b/n).toFixed(0)} ms, fxaa ${(fart.f/n).toFixed(0)} ms, skyggekart i ${fart.sk} av ${n}, hele render() ${(fart.r/n).toFixed(0)} ms, mellom bildene ${(fart.m/n).toFixed(0)} ms, kartet tegnet ${window.__kartBilder-fart.k0} bilder, laget vårt ${window.__vaareBilder-fart.v0}${pt.maal?', GPU-målt':', CPU-målt, tast m for GPU'})`; }
  const glFeil=gl2.getError();
  dbg.el.textContent=`v${document.querySelector('meta[name=description]').content.match(/Versjon ([\d.]+)/)[1]}  nær ${kam.naer.toFixed(1)} fjern ${kam.fjern.toFixed(0)}  glFeil ${glFeil}  kall ${(window.__pt||{}).kall}  dpr ${devicePixelRatio}  ${innerWidth}x${innerHeight}\ntegnet/s ${dbg.fps.length} (i ro tegnes det 10/s med vilje)  zoom ${map.getZoom().toFixed(2)} (x${kam.zoomfaktor.toFixed(2)})  pitch ${kam.pitch.toFixed(0)}  bearing ${kam.bearing.toFixed(0)}  perfNivaa ${KVAL.nivaa}  skala ${KVAL.skalaStille.toFixed(2)}  stille ${naa-TILSTAND.sistBeveg>300?1:0}  ss ${KVAL.ssStille} ao ${KVAL.aoStille} msaa ${post.samples()}`
    +String.fromCharCode(10)+fart.sist+String.fromCharCode(10)+'siste slipp: '+(SLIPP.rader.join(' | ')||'ingen')
    +String.fromCharCode(10)+`3D ${pt.scene|0} ms  blekk ${pt.blekk|0} ms  fxaa ${pt.fxaa|0} ms  kall ${pt.kall}  tri ${pt.tri}  skyggekart ${pt.skygge} (grunner: ${JSON.stringify(dekning.grunner)})  ${pt.maal?'GPU-målt':'CPU-målt'}`+String.fromCharCode(10)+`peker: ned ${dbg.pek.ned} flytt ${dbg.pek.flytt} opp ${dbg.pek.opp}  sist ${dbg.pek.sist}  knapper ${dbg.pek.knapper} ${dbg.pek.type}  senter ${tilModell(map.getCenter()).map(v=>v.toFixed(0)).join(',')}  dragPan ${map.dragPan.isEnabled()?'på':'av'} aktiv ${map.dragPan.isActive()?'ja':'nei'}`+String.fromCharCode(10)+dbg.rader.join(String.fromCharCode(10)); }
addEventListener('keydown',e=>{ if(!dbg.paa) return; feilsokTast(e.key); if(e.key==='p'){ speil.av(); } if(e.key==='m'){ window.__maal=!window.__maal; } if(e.key==='n'){ post.msaa(post.samples()?0:2); } });
function dbgVeksle(){ dbg.paa=!dbg.paa; if(!dbg.el){ dbg.el=document.createElement('pre'); dbg.el.style.cssText='position:fixed;left:8px;top:8px;z-index:9;margin:0;padding:8px;font:11px/1.25 ui-monospace,monospace;background:rgba(255,255,255,.92);color:#222;max-height:92vh;overflow:hidden;pointer-events:none;border-radius:6px'; document.body.appendChild(dbg.el); } dbg.el.style.display=dbg.paa?'block':'none'; }
addEventListener('keydown',e=>{ if(e.key==='d'&&!e.metaKey&&!e.ctrlKey) dbgVeksle(); });
// mobil: ?d=1 slår ruta på fra start (ingen tastatur), større skrift, og glen-feil + nær/fjern tas med
if(Q0.get('d')){ dbgVeksle(); dbg.el.style.font='13px/1.3 ui-monospace,monospace'; dbg.el.style.maxWidth='96vw'; dbg.el.style.whiteSpace='pre-wrap'; }
registrer({ dbgTegn: () => dbgTegn, hover: () => hover, husBoks: () => husBoks, valgt: () => valgt, velgHus: () => velgHus });   // brukes av tidligere moduler via SENERE (tilstand.js)

export { velgHus, BYGG_ID, fyllFergeKort, kort, kortInnhold, kort_, lukkKort, velgPunkt };
