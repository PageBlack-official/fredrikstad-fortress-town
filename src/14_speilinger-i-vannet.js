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
const START = Q.get('tx') ? [+Q.get('tx'), +Q.get('ty')] : [10,0];   // ?tx=&ty= setter startpunktet (test)
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const easeUt=t=>1-Math.pow(1-t,4);
// ytelse: måler bildefrekvensen og senker oppløsning/AO på svake maskiner (mobil), så spinnet holder seg mykt
let perfN=0, perfSum=0, perfLast=performance.now(), perfNivaa=Q.get('noadapt')?9:0;
function speilStyrke(){ return THREE.MathUtils.clamp(0.16+0.10*Math.log2(Math.max(kam.zoomfaktor,0.5)),0.1,0.36); }
let ssStille=4;
let speilInn=0, speilFrisk=false, sistBeveg=0, sistTegnet=0, fullTegnet=false, aoStille=14, aoBeveg=6; const _sisteKam=new THREE.Matrix4(); let _sisteZ=0;
function maalYtelse(){ const n=performance.now(), dt=n-perfLast; perfLast=n; if(perfNivaa>=2 || document.hidden || (n-sistBeveg>300 && n-sistTegnet>40)) return;
  perfN++; if(perfN>15){ perfSum+=dt; if(perfN>=75){ const avg=perfSum/60; perfN=0; perfSum=0;
    if(avg>30){ perfNivaa++; if(perfNivaa===1){ skalaBeveg=Math.max(0.35,skalaBeveg*0.75); aoBeveg=0; } else { skalaBeveg=Math.max(0.3,skalaBeveg*0.8); aoStille=7; sun.shadow.mapSize.set(1024,1024); if(sun.shadow.map){ sun.shadow.map.dispose(); sun.shadow.map=null; } skyggeSkitten=true; } } } } }
