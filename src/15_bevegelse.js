// ---- bevegelse: én modul for varighet og kurver i hele kartet (oppdrag 15, 29.10; kilder: rapport/flyt/kilder.md) ----
// Kameraet glir med glid (eksponentiell inn og ut, v32, godkjent av Vegar): farten bygges opp like lenge som den dør ut, og avstanden
// til målet halveres jevnt mot slutten i stedet for å stoppe på et punkt. Korte flytt (knappene) bruker myk (kubisk inn og ut): glid
// på under et halvt sekund dobler farten for hvert bilde og ser ut som et hopp. Kortet og knappene på skjermen bruker Material-kurvene:
// inn = bremser (kommer inn i bildet), ut = akselererer (forlater bildet), og ut er kortere enn inn.
// Alle tider står her; stil.css leser dem som CSS-variabler (--t-…, --k-…), så JS og CSS aldri kan gli fra hverandre.
// ?glid=0 gir de gamle kurvene til sammenligning.
const GLID = Q0.get('glid')!=='0';
const glid = t => !GLID ? (t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2) : t<=0 ? 0 : t>=1 ? 1 : t<0.5 ? Math.pow(2,20*t-10)/2 : (2-Math.pow(2,-20*t+10))/2;
const glidUt = t => !GLID ? 1-Math.pow(1-t,3) : t>=1 ? 1 : 1-Math.pow(2,-10*t);   // bare utglidning (når bevegelsen alt er i gang)
const myk = t => t<=0 ? 0 : t>=1 ? 1 : t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;     // korte flytt: kubisk inn og ut
const BEV = {
  kamera: { hus: 900, tilbake: 900, hjem: 1300, dobbel: 800, knapp: 420 },   // ms; glid under ~600 ms rykker (flyt-test: rykk)
  kort:   { inn: 380, ut: 240, innhold: 180 },                               // Material: lange inn, korte ut; innhold = kryssfade ved bytte av hus
  kurve:  { inn: 'cubic-bezier(.05,.7,.1,1)', ut: 'cubic-bezier(.3,0,.8,.15)', flytt: 'cubic-bezier(.2,0,0,1)' },   // M3 emphasized decelerate / accelerate / standard
  dobbelVindu: 300,   // ms mellom to klikk/trykk som regnes som dobbelt (samme som MapLibres og de fleste systemer)
  dobbelAvstand: 30,  // px
  husZoom: 2.4,       // zoomfaktor kameraet glir inn til ved klikk på et hus (aldri ut: står du nærmere, blir du stående)
  hentInn: 0.8,       // s: en avbrutt intro henter inn lyset og uskarpheten på denne tida (28.10)
  // treghet etter dra, klyp og vri (egen, se under): farten fra hånda dør ut eksponentielt med tidskonstant tau
  treghet: { tau: 0.26, k: 5, vindu: 70, maks: { pan: 1600, zoom: 4, bearing: 360, pitch: 90 } },   // s, -, ms, per sekund (pan i px)
  // musehjul (egen, se under): hvert hakk flytter målet; zoomen følger målet som en kritisk dempet fjær (ingen utslag per hakk)
  hjul: { perHakk: 0.4, omega: 15 },   // zoomnivå per hakk (deltaY 100 px), fjærstivhet (1/s): ~95 % framme på 0,3 s
  // speilet i vannet tegnes på nytt mens kartet beveger seg, høyst så ofte (ms); mellom gangene flyttes det forrige med kameraet (14)
  speilMs: 110,
};
// «Reduser bevegelse» (systeminnstilling) gjelder ikke kartet: Vegars Mac har den på, og han valgte selv at kartet og kortet skal bevege seg
// (CHANGELOG v27, 23.10: «respectPrefersReducedMotion av ("Reduser bevegelse" i macOS slo av alle animasjoner)»; bekreftet av hovedagenten
// 29.10). Valget het feil i MapLibre 6 og ble ignorert; riktig navn er reduceMotion:false i kartvalgene (00_oppsett).
(()=>{ const s=document.documentElement.style; s.setProperty('--t-kort-inn', BEV.kort.inn+'ms'); s.setProperty('--t-kort-ut', BEV.kort.ut+'ms');
  s.setProperty('--k-inn', BEV.kurve.inn); s.setProperty('--k-ut', BEV.kurve.ut); s.setProperty('--k-flytt', BEV.kurve.flytt); })();
// MapLibres egne knapper (+/−, kompass) og tastatur bruker 300–500 ms med en annen kurve; knappene får vår korte kurve og tid
// (kompasset snur opptil 180°, så det får husets tid og glid)
['zoomIn','zoomOut'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.knapp, easing:myk, ...(opt||{})}, ev); });
['resetNorth','resetNorthPitch'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.hus, easing:glid, ...(opt||{})}, ev); });
// ett kameraflytt: alltid avbrytbart (MapLibre stopper en pågående easeTo så snart en gest starter; en ny easeTo starter fra der kameraet er)
function glidKamera(mal, type){ hjulZoom.stopp(); map.easeTo({...mal, duration: BEV.kamera[type], easing: glid}); }

// ---- treghet etter dra, klyp og vri (29.10) ----
// MapLibre tar med 0,3 av farten fra klyp og vri (kan ikke stilles), og tregheten starter et bilde for sent, så det står ett bilde stille
// idet du slipper (flyt-test). Vi måler farten selv (kameraet i de siste 70 ms av gesten) og lar den dø ut eksponentielt:
// x(t) = v0·tau·(1 − e^(−t/tau)), regnet fra siste bevegelse i gesten, så første bilde etter slipp fortsetter med samme fart.
// Kjøres som én vanlig easeTo (avbrytbar, riktige hendelser). Vi kjenner igjen MapLibres treghetskall på at det er easeTo med
// noMoveStart + freezeElevation og en slipp-hendelse; endrer MapLibre det, får vi bare MapLibres egen treghet tilbake (ingen feil).
const treghet=(()=>{
  const spor=[]; const T=BEV.treghet;
  const merc=ll=>maplibregl.MercatorCoordinate.fromLngLat(ll,0);
  map.on('move', e=>{ if(!e.originalEvent || /up$|end$|cancel$/.test(e.originalEvent.type)) return;
    spor.push({t:performance.now(), c:merc(map.getCenter()), z:map.getZoom(), b:map.getBearing(), p:map.getPitch()}); if(spor.length>12) spor.shift(); });
  ['pointerdown','touchstart','wheel'].forEach(t=>map.getCanvasContainer().addEventListener(t,()=>{ spor.length=0; },{capture:true,passive:true}));
  const F=s=>1-Math.exp(-T.k*s);
  const easeTo0=map.easeTo.bind(map);
  map.easeTo=(opt,ev)=>{
    const slipp = opt && opt.noMoveStart && opt.freezeElevation && ev && ev.originalEvent;
    if(!slipp) return easeTo0(opt,ev);
    const naa=performance.now(), siste=spor[spor.length-1];
    const v=siste && spor.filter(x=>siste.t-x.t<=T.vindu); const forste=v && v[0];
    if(!forste || siste.t-forste.t<8 || naa-siste.t>T.vindu){ spor.length=0; return easeTo0(opt,ev); }   // holdt stille før slipp: MapLibre avgjør
    const dt=(siste.t-forste.t)/1000, mpp=1/(512*Math.pow(2,siste.z));   // mercator per skjermpunkt
    const kl=(x,m)=>Math.max(-m,Math.min(m,x));
    const vx=kl((siste.c.x-forste.c.x)/dt/mpp, T.maks.pan)*mpp, vy=kl((siste.c.y-forste.c.y)/dt/mpp, T.maks.pan)*mpp;
    const vz=kl((siste.z-forste.z)/dt, T.maks.zoom), vb=kl((((siste.b-forste.b)%360+540)%360-180)/dt, T.maks.bearing), vp=kl((siste.p-forste.p)/dt, T.maks.pitch);
    const D=T.k*T.tau, g=(naa-siste.t)/1000/D;   // g: tida siden siste bevegelse, som andel av D
    const ved=s=>{ const ut=T.tau*F(s); return {center:new maplibregl.MercatorCoordinate(siste.c.x+vx*ut, siste.c.y+vy*ut, 0).toLngLat(), zoom:siste.z+vz*ut, bearing:siste.b+vb*ut, pitch:siste.p+vp*ut}; };
    // MapLibre kaller dette i bildet der slippet behandles, og easeTo flytter først i neste bilde: hopp derfor til der kameraet skal være nå
    // (dette bildet tegnes med det), og gli videre derfra med samme fart
    spor.length=0; map.jumpTo(ved(g));
    return easeTo0({...ved(1+g), duration:D*1000, noMoveStart:true, freezeElevation:true, easing:u=>(F(u+g)-F(g))/(F(1+g)-F(g))}, ev);
  };
  return {spor};
})();

// ---- musehjul (29.10): jevn zoom i stedet for ett utslag per hakk ----
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
      overta(); const r=map.getCanvas().getBoundingClientRect(); px=[e.clientX-r.left, e.clientY-r.top]; anker=map.unproject(px);
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
