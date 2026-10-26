// ---- speilinger i vannet: hus, trær og terreng tegnes speilvendt om vannflaten i et eget, halvt så stort lag ----
const speil=(()=>{
  const Y=0.15, LAG=1;
  const rt=new THREE.WebGLRenderTarget(2,2,{type:THREE.HalfFloatType});
  const deler=[city, ...[].concat(crowns)];
  scene.traverse(o=>{ if(o.isMesh && o.material && o.material.uniforms && o.material.uniforms.skyggeF) deler.push(o); });  // festningsterrenget skjuler det som står bak vollene
  deler.forEach(o=>o.traverse(c=>c.layers.enable(LAG)));
  let paa=!Q0.get('nospeil');
  const cc=new THREE.Color();
  return {
    size(){ const w=renderer.domElement.width, h=renderer.domElement.height; rt.setSize(Math.max(2,w>>1), Math.max(2,h>>1)); },
    av(){ paa=false; waterMat.uniforms.reflStyrke.value=0; },
    render(endret){
      if(!paa){ waterMat.uniforms.reflStyrke.value=0; return; }
      // tegnes bare på nytt når kameraet eller husene har flyttet seg (stillestående bilde koster ingenting ekstra)
      const e=cam.projectionMatrix.elements, nok=e.join(',')+(endret?Math.random():'');
      if(nok===this._sist) return; this._sist=nok;
      const lagre=deler.map(o=>[o.position.y,o.scale.y]);
      deler.forEach(o=>{ o.position.y=2*Y-o.position.y; o.scale.y=-o.scale.y; });
      const bg=scene.background; scene.background=null; renderer.getClearColor(cc); const ca=renderer.getClearAlpha();
      const au=renderer.shadowMap.autoUpdate; renderer.shadowMap.autoUpdate=false;
      cam.layers.set(LAG); renderer.setRenderTarget(rt); renderer.setClearColor(0x000000,0); renderer.clear(); renderer.render(scene,cam);
      cam.layers.set(0); renderer.setRenderTarget(null); renderer.setClearColor(cc,ca); renderer.shadowMap.autoUpdate=au; scene.background=bg;
      deler.forEach((o,i)=>{ o.position.y=lagre[i][0]; o.scale.y=lagre[i][1]; });
      waterMat.uniforms.tRefl.value=rt.texture;
      // speilingen tones ned i oversikten og kommer fram når man går nærmere, så den aldri popper
      waterMat.uniforms.reflStyrke.value=speilStyrke();
    }
  };
})();

const clock=new THREE.Clock(); let _synlig=false;

const Q=Q0; let introDone=false;
if(Q.get('sol')){ const dato=Q.get('dato')||new Date().toISOString().slice(0,10); const mnd=+dato.slice(5,7); const off=(mnd>=4&&mnd<=10)?'+02:00':'+01:00';
  const p=solposisjon(new Date(dato+'T'+Q.get('sol')+':00'+off)); setSol(p.asimut,p.hoyde); }
const START = Q.get('tx') ? [+Q.get('tx'), +Q.get('ty')] : (HJEM_PLAKAT ? [10,0] : [25,25]);   // ny hjemmevisning (26.10): midt i byen, torget litt under midten   // ?tx=&ty= setter startpunktet (test)
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const easeUt=t=>1-Math.pow(1-t,4);
// ytelse: måler bildefrekvensen mens kartet beveger seg og senker kvaliteten ett trinn for godt på svake maskiner.
// Trinnet gjelder både i fart og i ro, så bildet aldri bytter utseende når en gest starter eller slutter.
let perfN=0, perfSum=0, perfLast=performance.now(), perfNivaa=Q.get('noadapt')?9:0;
function speilStyrke(){ return THREE.MathUtils.clamp(0.16+0.10*Math.log2(Math.max(kam.zoomfaktor,0.5)),0.1,0.36); }
let ssStille=4;
let speilInn=0, speilFrisk=false, sistBeveg=0, sistTegnet=0, fullTegnet=false, aoStille=14; const _sisteKam=new THREE.Matrix4(); let _sisteZ=0;
// Måler tiden vår egen tegning tar (render(), CPU-siden), ikke avstanden mellom bildene: den styres også av verten og skjermen, og
// lavere kvalitet hjelper ikke mot den. Introen (vekst + skygge hvert bilde) måles ikke; den er dyrere enn vanlig bruk.
function maalYtelse(){ const n=performance.now(); perfLast=n; if(perfNivaa>=2 || document.hidden || !introDone || !vokst || (n-sistBeveg>300 && n-sistTegnet>40)) return;
  const dt=window.__ramme||0;
  perfN++; if(perfN>15){ perfSum+=dt; if(perfN>=75){ const avg=perfSum/60; perfN=0; perfSum=0;
    if(avg>30){ settNivaa(perfNivaa+1); } } } }
// trinnene som egen funksjon, så de kan tvinges fram (?nivaa=2) og testes uten å vente på måleren
function settNivaa(n){ perfNivaa=n;
  if(n===1){ ssStille=2; skalaMaskin=0.8; }                                    // trinn 1: strek med to prøver, 80 % oppløsning
  else if(n>=2){ ssStille=1; skalaMaskin=0.6; aoStille=8; sun.shadow.mapSize.set(1024,1024); if(sun.shadow.map) sun.shadow.map.setSize(1024,1024); skyggeSkitten=true; }   // setSize beholder teksturobjektet; dispose+null ga skyggekart uten skygger og ødelagte kroner på mobil (24.10) // trinn 2: mobil som sliter
  beregnSkala(); }
if(Q.get('nivaa')) settNivaa(+Q.get('nivaa'));
