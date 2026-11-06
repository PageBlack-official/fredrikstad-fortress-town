import * as THREE from 'three';
import { BERORING, HJEM_PLAKAT, Q0, STAAENDE, cam, kam, map, renderer, scene } from './00_oppsett.js';
import { MAALT, maalVent } from './01_etterbehandling.js';
import { setSol, solposisjon } from './02_lys.js';
import { waterMat } from './03_bakke-vann-grønt.js';
import { city } from './05_bygg.js';
import { crowns } from './12_trær.js';
// ---- speilinger i vannet: hus, trær og terreng tegnes speilvendt om vannflaten i et eget, halvt så stort lag ----
// speilet toner ikke lenger ut når kartet beveger seg. Det tegnes på nytt høyst hvert BEV.speilMs ms i fart (og hvert bilde i ro
// når noe endrer seg), og mellom gangene slår vannet opp i det med kameraet fra da det ble tegnet, så det står fast i byen.
const speil=(()=>{
  const Y=0.15, LAG=1;
  const rt=new THREE.WebGLRenderTarget(2,2,{type:THREE.HalfFloatType});
  const deler=[city, ...[].concat(crowns)];
  scene.traverse(o=>{ if(o.isMesh && o.material && o.material.uniforms && o.material.uniforms.skyggeF) deler.push(o); });  // festningsterrenget skjuler det som står bak vollene
  deler.forEach(o=>o.traverse(c=>c.layers.enable(LAG)));
  let paa=!Q0.get('nospeil');
  const cc=new THREE.Color(), _speilKam=new THREE.Matrix4().set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), lagre=new Float64Array(2*deler.length);
  return {
    size(){ const w=renderer.domElement.width, h=renderer.domElement.height; const d=BERORING?2:1; rt.setSize(Math.max(2,Math.round(w/d)), Math.max(2,Math.round(h/d))); },   // speilet i full oppløsning på maskin, halv på telefon
    av(){ paa=false; waterMat.uniforms.reflStyrke.value=0; },
    render(endret){
      if(!paa){ waterMat.uniforms.reflStyrke.value=0; return; }
      // tegnes bare på nytt når kameraet eller husene har flyttet seg (stillestående bilde koster ingenting ekstra)
      if(!endret && _speilKam.equals(cam.projectionMatrix)) return; _speilKam.copy(cam.projectionMatrix);   // matrisen sammenlignes direkte, ingen ny tekst per bilde
      const _ts=performance.now();
      deler.forEach((o,i)=>{ lagre[2*i]=o.position.y; lagre[2*i+1]=o.scale.y; });
      deler.forEach(o=>{ o.position.y=2*Y-o.position.y; o.scale.y=-o.scale.y; });
      const bg=scene.background; scene.background=null; renderer.getClearColor(cc); const ca=renderer.getClearAlpha();
      const au=renderer.shadowMap.autoUpdate; renderer.shadowMap.autoUpdate=false;
      cam.layers.set(LAG); renderer.setRenderTarget(rt); renderer.setClearColor(0x000000,0); renderer.clear(); renderer.render(scene,cam);
      cam.layers.set(0); renderer.setRenderTarget(null); renderer.setClearColor(cc,ca); renderer.shadowMap.autoUpdate=au; scene.background=bg;
      deler.forEach((o,i)=>{ o.position.y=lagre[2*i]; o.scale.y=lagre[2*i+1]; });
      maalVent(); MAALT.speil+=performance.now()-_ts;   // måling (verktoy/flyt_maal.mjs)
      waterMat.uniforms.tRefl.value=rt.texture;
      // kameraets projeksjon da speilet ble tegnet: vannet slår opp i speilet med den (03), så speilet følger byen til neste tegning
      waterMat.uniforms.reflPV.value.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse); this.sist=performance.now();
      // speilingen tones ned i oversikten og kommer fram når man går nærmere, så den aldri popper
      waterMat.uniforms.reflStyrke.value=speilStyrke();
    }
  };
})();

const clock=new THREE.Clock();

const Q=Q0;
if(Q.get('sol')){ const dato=Q.get('dato')||new Date().toISOString().slice(0,10); const mnd=+dato.slice(5,7); const off=(mnd>=4&&mnd<=10)?'+02:00':'+01:00';
  const p=solposisjon(new Date(dato+'T'+Q.get('sol')+':00'+off)); setSol(p.asimut,p.hoyde); }
const MOBIL_START=[12,67];   // stående telefon: sentrum for sluttbildet (se 00_oppsett STAAENDE)
const START = Q.get('tx') ? [+Q.get('tx'), +Q.get('ty')] : (HJEM_PLAKAT ? [10,0] : (STAAENDE ? MOBIL_START : [25,25]));   // ny hjemmevisning : midt i byen, torget litt under midten   // ?tx=&ty= setter startpunktet (test)
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const easeUt=t=>1-Math.pow(1-t,4);
function speilStyrke(){ return THREE.MathUtils.clamp(0.16+0.10*Math.log2(Math.max(kam.zoomfaktor,0.5)),0.1,0.36); }
const _sisteKam=new THREE.Matrix4(); let _sisteZ=0;

// speilet følger vindusstørrelsen (som etterbehandlingen i 01)
map.on('resize', () => speil.size());

export { Q, START, clock, speil, speilStyrke };
