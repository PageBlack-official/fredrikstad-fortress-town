import * as maplibregl from 'maplibre-gl';
import { SENERE, registrer } from './tilstand.js';
import { Q0, map, tilLngLat } from './00_oppsett.js';
// ---- bevegelse: én modul for varighet og kurver i hele kartet (oppdrag 15; kilder: rapport/flyt/kilder.md) ----
// Kameraet glir med glid (eksponentiell inn og ut, v32, godkjent av Vegar): farten bygges opp like lenge som den dør ut, og avstanden
// til målet halveres jevnt mot slutten i stedet for å stoppe på et punkt. Korte flytt (knappene) bruker myk (kubisk inn og ut): glid
// på under et halvt sekund dobler farten for hvert bilde og ser ut som et hopp. Kortet og knappene på skjermen bruker Material-kurvene:
// inn = bremser (kommer inn i bildet), ut = akselererer (forlater bildet), og ut er kortere enn inn.
// Alle tider står her; stil.css leser dem som CSS-variabler (--t-…, --k-…), så JS og CSS aldri kan gli fra hverandre.
// ?glid=0 gir de gamle kurvene til sammenligning.
const GLID = Q0.get('glid')!=='0';
const glid = t => !GLID ? (t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2) : t<=0 ? 0 : t>=1 ? 1 : t<0.5 ? Math.pow(2,20*t-10)/2 : (2-Math.pow(2,-20*t+10))/2;
// kranløftet i introen (07.11): i bevegelse fra første bilde og lander mykt; glid står nesten stille det første kvarteret av et langt løft
const loft = t => t<=0 ? 0 : t>=1 ? 1 : 1-Math.pow(1-t,3);
const glidUt = t => !GLID ? 1-Math.pow(1-t,3) : t>=1 ? 1 : 1-Math.pow(2,-10*t);   // bare utglidning (når bevegelsen alt er i gang)
const myk = t => t<=0 ? 0 : t>=1 ? 1 : t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;     // korte flytt: kubisk inn og ut
const BEV = {
  kamera: { hus: 900, tilbake: 900, hjem: 1300, dobbel: 800, knapp: 420 },   // ms; glid under ~600 ms rykker (flyt-test: rykk)
  kort:   { inn: 380, ut: 240, innhold: 180 },                               // Material: lange inn, korte ut; innhold = kryssfade ved bytte av hus
  kurve:  { inn: 'cubic-bezier(.05,.7,.1,1)', ut: 'cubic-bezier(.3,0,.8,.15)', flytt: 'cubic-bezier(.2,0,0,1)' },   // M3 emphasized decelerate / accelerate / standard
  dobbelVindu: 300,   // ms mellom to klikk/trykk som regnes som dobbelt (samme som MapLibres og de fleste systemer)
  dobbelAvstand: 30,  // px
  husZoom: 2.4,       // zoomfaktor kameraet glir inn til ved klikk på et hus (aldri ut: står du nærmere, blir du stående)
  hentInn: 0.8,       // s: en avbrutt intro henter inn lyset og uskarpheten på denne tida 
  // treghet etter dra, klyp og vri (egen, se under): farten fra hånda dør ut eksponentielt med tidskonstant tau
  treghet: { tau: 0.26, k: 5, vindu: 70, maks: { pan: 1600, zoom: 4, bearing: 360, pitch: 90 } },   // s, -, ms, per sekund (pan i px)
  // musehjul (egen, se under): hvert hakk flytter målet; zoomen følger målet som en kritisk dempet fjær (ingen utslag per hakk)
  hjul: { perHakk: 0.4, omega: 15 },   // zoomnivå per hakk (deltaY 100 px), fjærstivhet (1/s): ~95 % framme på 0,3 s
  // speilet i vannet tegnes på nytt mens kartet beveger seg, høyst så ofte (ms); mellom gangene flyttes det forrige med kameraet (14)
  speilMs: 110,
};
// «Reduser bevegelse» (systeminnstilling) gjelder ikke kartet: Vegars Mac har den på, og han valgte selv at kartet og kortet skal bevege seg
// (CHANGELOG v27: «respectPrefersReducedMotion av ("Reduser bevegelse" i macOS slo av alle animasjoner)»).
// Valget het feil i MapLibre 6 og ble ignorert; riktig navn er reduceMotion:false i kartvalgene (00_oppsett).
(()=>{ const s=document.documentElement.style; s.setProperty('--t-kort-inn', BEV.kort.inn+'ms'); s.setProperty('--t-kort-ut', BEV.kort.ut+'ms');
  s.setProperty('--k-inn', BEV.kurve.inn); s.setProperty('--k-ut', BEV.kurve.ut); s.setProperty('--k-flytt', BEV.kurve.flytt); })();
// MapLibres egne knapper (+/−, kompass) og tastatur bruker 300–500 ms med en annen kurve; knappene får vår korte kurve og tid
// (kompasset snur opptil 180°, så det får husets tid og glid)
['zoomIn','zoomOut'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.knapp, easing:myk, ...(opt||{})}, ev); });
['resetNorth','resetNorthPitch'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.hus, easing:glid, ...(opt||{})}, ev); });
// ett kameraflytt: alltid avbrytbart (MapLibre stopper en pågående easeTo så snart en gest starter; en ny easeTo starter fra der kameraet er)
function glidKamera(mal, type){ hjulZoom.stopp(); map.easeTo({...mal, duration: BEV.kamera[type], easing: glid, __fra:type}); }

// ---- treghet etter dra, klyp og vri ----
// MapLibre tar med 0,3 av farten fra klyp og vri (kan ikke stilles), og tregheten starter et bilde for sent, så det står ett bilde stille
// idet du slipper (flyt-test). Vi måler farten selv i de siste 70 ms av gesten: flytt = fingrenes midtpunkt på skjermen (som MapLibres
// dra), zoom/vri/vipp = kameraet. Farten dør ut eksponentielt, x(t) = v0·tau·(1 − e^(−t/tau)) regnet fra siste bevegelse, så første
// bilde etter slipp fortsetter med samme fart. Zoom og vri skjer rundt punktet mellom fingrene (MapLibres «around»), så det står under
// fingrene også mens tregheten virker. Vi kjenner igjen MapLibres treghetskall på at det er easeTo med noMoveStart + freezeElevation og en
// slipp-hendelse; endrer MapLibre det, får vi bare MapLibres egen treghet tilbake (ingen feil).
let fingerNede=false;   // settes av berøringslytterne under; leses av tegneløkka (15_loop) og skyggekartet (02_lys)
// slipplogg (Vegar: «den flytter seg fremdeles når jeg slipper tommelen»): hvert slipp og hvert kameraflytt de neste 600 ms
// skrives her med hvem som utløste det, og vises i feilsøkingsruta (?d=1). Måling før gjetning.
const SLIPP={t:0, rader:[]}; const slippLogg=(tekst)=>{ SLIPP.rader.push(`${((performance.now()-SLIPP.t)|0)} ms: ${tekst}`); if(SLIPP.rader.length>8) SLIPP.rader.shift(); };
const treghet=(()=>{
  const T=BEV.treghet, kam=[], fing=[]; let rid=0, anim=null;
  const kort=(a,tid)=>{ while(a.length>2 && tid-a[0].t>200) a.shift(); };
  map.on('move', e=>{ if(!e.originalEvent || anim || /up$|end$|cancel$/.test(e.originalEvent.type)) return;
    const t=performance.now(); kam.push({t, z:map.getZoom(), b:map.getBearing(), p:map.getPitch()}); kort(kam,t); });
  const el=map.getCanvasContainer();
  const fingre=(x,y)=>{ const t=performance.now(); fing.push({t,x,y}); kort(fing,t); };
  // Midtpunktet mellom fingrene hopper når en finger kommer til eller slipper (to tomler: det flytter seg til tommelen som er igjen).
  // Hoppet er ikke bevegelse. Tas det med, leses det som et kast (mobil: «hopper bildet ganske langt mot venstre når jeg
  // slipper tomlene» = den ene tommelen slapp først). Derfor skjøtes målingen: forskyvningen legges til de nye punktene, så farten fra
  // hånda fortsetter uten hoppet. Testen er verktoy/tomler_test.mjs.
  let antall=0, skjot=null, fx=0, fy=0;
  // fingerNede: minst én finger er på kartet (leses av 15_loop og 02_lys: ingen tunge pass mens fingeren er nede)
  const settFinger=e=>{ fingerNede=e.touches.length>0; };
  const midt=e=>{ let x=0,y=0; for(const f of e.touches){ x+=f.clientX; y+=f.clientY; } return [x/e.touches.length, y/e.touches.length]; };
  const nyttAntall=e=>{ if(e.touches.length===antall) return; antall=e.touches.length; if(antall>0 && fing.length) skjot=fing[fing.length-1]; };
  el.addEventListener('touchmove', e=>{ if(!e.touches.length) return; nyttAntall(e); const [x,y]=midt(e);
    if(skjot){ fx=skjot.x-x; fy=skjot.y-y; skjot=null; }   // første punkt etter skiftet står der det forrige sluttet
    fingre(x+fx, y+fy); }, {capture:true, passive:true});
  el.addEventListener('touchstart', e=>{ settFinger(e); if(e.touches.length===e.changedTouches.length){ fing.length=0; fx=fy=0; skjot=null; antall=e.touches.length; if(antall===1) stopp(); } else nyttAntall(e); }, {capture:true, passive:true});   // ny gest: alle fingrene er nye
  el.addEventListener('touchend', e=>{ settFinger(e); nyttAntall(e); }, {capture:true, passive:true});
  el.addEventListener('touchcancel', e=>{ settFinger(e); nyttAntall(e); }, {capture:true, passive:true});
  el.addEventListener('pointermove', e=>{ if(e.pointerType==='mouse' && e.buttons) fingre(e.clientX, e.clientY); }, {capture:true, passive:true});
  el.addEventListener('pointerdown', ()=>{ stopp(); kam.length=0; fing.length=0; }, {capture:true, passive:true});
  el.addEventListener('wheel', ()=>stopp(), {capture:true, passive:true});
  const F=s=>1-Math.exp(-T.k*s);
  const kl=(x,m)=>Math.max(-m,Math.min(m,x));
  const fart=(a,f,m)=>{ const siste=a[a.length-1]; const v=a.filter(x=>siste.t-x.t<=T.vindu); const forste=v[0]; const dt=(siste.t-forste.t)/1000; return dt<0.008 ? 0 : kl(f(siste,forste)/dt, m); };
  function steg(){ rid=0; if(!anim) return; const s=Math.min(1+anim.g, (performance.now()-anim.t0)/1000/(T.k*T.tau)); sett(s); if(s<1+anim.g) rid=requestAnimationFrame(steg); else anim=null; }
  function sett(s){ const A=anim, ut=T.tau*F(s), d=ut-A.ut; A.ut=ut;
    const o={duration:0}; if(A.vz) o.zoom=map.getZoom()+A.vz*d; if(A.vb) o.bearing=map.getBearing()+A.vb*d; if(A.vp) o.pitch=map.getPitch()+A.vp*d;
    if(A.around && (o.zoom!==undefined || o.bearing!==undefined || o.pitch!==undefined)){ o.around=A.around; easeTo0(o, A.ev); }
    else if(o.zoom!==undefined || o.bearing!==undefined || o.pitch!==undefined) easeTo0(o, A.ev);
    if(A.vx || A.vy){ map.panBy([-A.vx*d, -A.vy*d], {animate:false}); if(A.around) A.around=map.unproject(map.project(A.around).add(new maplibregl.Point(A.vx*d, A.vy*d))); } }
  function stopp(){ anim=null; if(rid){ window.cancelAnimationFrame(rid); rid=0; } }
  const easeTo0=map.easeTo.bind(map);
  map.easeTo=(opt,ev)=>{
    if(anim && !(opt && opt.duration===0)) stopp();   // et nytt kameraflytt avbryter tregheten (våre egne trinn har duration 0)
    const slipp = opt && opt.noMoveStart && opt.freezeElevation && ev && ev.originalEvent;
    if(!slipp && opt && opt.duration!==0 && performance.now()-SLIPP.t<600) slippLogg(`easeTo fra ${opt.__fra||(ev&&ev.originalEvent?ev.originalEvent.type:'ukjent')}: varighet ${opt.duration|0}${opt.center?' senter':''}${opt.zoom!==undefined?' zoom':''}${opt.bearing!==undefined?' vri':''}`);
    if(!slipp) return easeTo0(opt,ev);
    const naa=performance.now(); const siste=Math.max(kam.length?kam[kam.length-1].t:-1e9, fing.length?fing[fing.length-1].t:-1e9);
    // Slipp-tiden leses av selve berøringshendelsen (timeStamp, samme klokke som performance.now), ikke av når kartet rakk å behandle den.
    // På en treg telefon kan behandlingen komme 100–300 ms etter at fingeren løftet; da gikk vi til MapLibres treghet, som regner
    // farten med tommelhoppet inne (sprett). En senere versjon lot i stedet målevinduet vokse med bildetiden, og da fikk en finger som
    // hadde STOPPET fart fra bevegelsen før stoppet (Vegar: «kartet glir litt mot høyre» når tommelen slipper). Nå: har fingeren
    // ligget stille mer enn vinduet før den løftet, er det et dødt stopp, uansett hvor sent kartet behandler slippet. Mus: MapLibre avgjør.
    const loft=(ev.originalEvent.timeStamp>0 && ev.originalEvent.timeStamp<naa+1) ? ev.originalEvent.timeStamp : naa;
    const beroring=String(ev.originalEvent.type).startsWith('touch');
    SLIPP.t=naa; SLIPP.rader.length=0; SLIPP.p0=map.getCenter(); slippLogg(`slipp (${ev.originalEvent.type}): stille ${(loft-siste)|0} ms før løft, behandlet ${(naa-loft)|0} ms etter, fingerpunkter ${fing.length}, timeStamp ${ev.originalEvent.timeStamp>0&&ev.originalEvent.timeStamp<naa+1?'ok':'ubrukelig'}`);
    if(loft-siste>T.vindu+20){ kam.length=0; fing.length=0; slippLogg(beroring ? 'dødt stopp (vår)' : 'MapLibre avgjør (mus)'); return beroring ? map : easeTo0(opt,ev); }   // holdt stille før slipp
    const A={t0:siste, ut:0, ev, around:opt.around||null, vx:0, vy:0, vz:0, vb:0, vp:0};
    if(opt.center!==undefined && fing.length>1){ A.vx=fart(fing,(a,b)=>a.x-b.x,T.maks.pan); A.vy=fart(fing,(a,b)=>a.y-b.y,T.maks.pan); }
    if(kam.length>1){ if(opt.zoom!==undefined) A.vz=fart(kam,(a,b)=>a.z-b.z,T.maks.zoom); if(opt.bearing!==undefined) A.vb=fart(kam,(a,b)=>((a.b-b.b)%360+540)%360-180,T.maks.bearing); if(opt.pitch!==undefined) A.vp=fart(kam,(a,b)=>a.p-b.p,T.maks.pitch); }
    kam.length=0; fing.length=0;
    slippLogg(`fart vår: x ${A.vx|0} y ${A.vy|0} px/s, zoom ${A.vz.toFixed(2)}, vri ${A.vb|0}, vipp ${A.vp|0}`);
    if(!(A.vx||A.vy||A.vz||A.vb||A.vp)){ slippLogg('ingen fart: MapLibre avgjør'); return easeTo0(opt,ev); }
    stopp(); anim=A; A.g=(naa-siste)/1000/(T.k*T.tau);
    sett(A.g);   // MapLibre kaller dette i bildet der slippet behandles: flytt med en gang, så dette bildet ikke står stille
    rid=requestAnimationFrame(steg); return map;
  };
  const jumpTo0=map.jumpTo.bind(map); map.jumpTo=(opt,ev)=>{ if(performance.now()-SLIPP.t<600) slippLogg('jumpTo'); return jumpTo0(opt,ev); };
  const panBy0=map.panBy.bind(map); map.panBy=(o,opt,ev)=>{ if(!anim && performance.now()-SLIPP.t<600) slippLogg(`panBy ${o[0]|0},${o[1]|0}`); return panBy0(o,opt,ev); };
  map.on('moveend', ()=>{ if(performance.now()-SLIPP.t<2000) slippLogg(`moveend, senter flyttet ${SLIPP.p0 ? Math.hypot(map.project(SLIPP.p0).x-innerWidth/2, map.project(SLIPP.p0).y-innerHeight/2)|0 : '?'} px siden slippet`); });
  map.on('movestart', e=>{ if(performance.now()-SLIPP.t<600) slippLogg(`movestart (${e.originalEvent?e.originalEvent.type:'program'})`); });
  return {stopp};
})();

// ---- musehjul : jevn zoom i stedet for ett utslag per hakk ----
// Hvert hakk flytter et mål; zoomen følger målet som en kritisk dempet fjær (Apple: fjær uten oversving), så farten er sammenhengende
// også når hakkene kommer tett. Punktet under pekeren står. Styreflate (to fingre = flytt, klyp = ctrl+hjul) går ikke hit (16_interaksjon).
const hjulZoom=(()=>{
  let mal=null, z=0, v=0, anker=null, px=null, sist=0, rid=0;
  function steg(){ rid=0; if(mal===null) return;
    const naa=performance.now(), dt=Math.min(0.05,(naa-sist)/1000); sist=naa; const w=BEV.hjul.omega;
    v+=(w*w*(mal-z)-2*w*v)*dt; z+=v*dt;
    const ferdig=Math.abs(mal-z)<0.001 && Math.abs(v)<0.01; if(ferdig) z=mal;
    map.easeTo({zoom:z, around:anker, duration:0});   // around: punktet under pekeren står
    if(ferdig){ mal=null; return; } rid=requestAnimationFrame(steg); }
  return {
    hakk(e, delta){   // delta i zoomnivå (+ = inn)
      SENERE.overta(); const r=map.getCanvas().getBoundingClientRect(); px=[e.clientX-r.left, e.clientY-r.top]; anker=map.unproject(px);
      if(mal===null){ z=map.getZoom(); v=0; mal=z; sist=performance.now(); }
      mal=Math.max(map.getMinZoom(), Math.min(map.getMaxZoom(), mal+delta));
      if(!rid) rid=requestAnimationFrame(steg);
    },
    stopp(){ mal=null; if(rid){ window.cancelAnimationFrame(rid); rid=0; } },
    aktiv:()=>mal!==null,
  };
})();
window.__tilLngLat=tilLngLat; window.__BEV=BEV;
// en ny gest stopper hjulzoomen (dra, klyp)
map.getCanvasContainer().addEventListener('pointerdown', ()=>hjulZoom.stopp(), {capture:true, passive:true});
registrer({ fingerNede: () => fingerNede });   // brukes av tidligere moduler via SENERE (tilstand.js)

export { BEV, GLID, SLIPP, fingerNede, glid, glidKamera, hjulZoom, loft, myk, slippLogg, treghet };
