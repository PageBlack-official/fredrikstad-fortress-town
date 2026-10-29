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
};
// redusert bevegelse (systeminnstilling): kortet toner inn og ut i stedet for å gli (stil.css). Kameraet glir som før: Vegars Mac har
// «Reduser bevegelse» på, og han valgte selv at kartet skal bevege seg (v26: MapLibres valg «respectPrefersReducedMotion» av, som i 6.x
// heter reduceMotion; 00_oppsett). ?bevegelse=redusert prøver det redusert i en vanlig nettleser.
const REDUSERT = Q0.get('bevegelse')==='redusert' || window.matchMedia('(prefers-reduced-motion: reduce)').matches;
(()=>{ const s=document.documentElement.style; s.setProperty('--t-kort-inn', BEV.kort.inn+'ms'); s.setProperty('--t-kort-ut', BEV.kort.ut+'ms');
  s.setProperty('--k-inn', BEV.kurve.inn); s.setProperty('--k-ut', BEV.kurve.ut); s.setProperty('--k-flytt', BEV.kurve.flytt);
  if(REDUSERT) document.documentElement.dataset.bevegelse='redusert'; })();
// MapLibres egne knapper (+/−, kompass) og tastatur bruker 300–500 ms med en annen kurve; knappene får vår korte kurve og tid
// (kompasset snur opptil 180°, så det får husets tid og glid)
['zoomIn','zoomOut'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.knapp, easing:myk, ...(opt||{})}, ev); });
['resetNorth','resetNorthPitch'].forEach(f=>{ const o=map[f].bind(map); map[f]=(opt,ev)=>o({duration:BEV.kamera.hus, easing:glid, ...(opt||{})}, ev); });
// ett kameraflytt: alltid avbrytbart (MapLibre stopper en pågående easeTo så snart en gest starter; en ny easeTo starter fra der kameraet er)
function glidKamera(mal, type){ map.easeTo({...mal, duration: BEV.kamera[type], easing: glid}); }
window.__tilLngLat=tilLngLat; window.__BEV=BEV;
