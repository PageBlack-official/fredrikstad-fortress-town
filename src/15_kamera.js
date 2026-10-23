// ---- kamera: alle bevegelser er myke (fjær/easing), zoom holder punktet under pekeren fast ----
const HOME={zoom:1, target:target.clone(), az:AZ0};
let anim=null, zoomMaal=cam.zoom, zoomAnker=null, sisteTid=performance.now();
const GRENSE=560;                                         // hvor langt fra byen man kan flytte seg (meter)
const _pl=new THREE.Plane(new THREE.Vector3(0,1,0),0), _rc=new THREE.Raycaster(), _v2=new THREE.Vector2();
function bakkeVed(x,y){ _v2.set(x/innerWidth*2-1, -(y/innerHeight)*2+1); _rc.setFromCamera(_v2,cam); const v=new THREE.Vector3(); return _rc.ray.intersectPlane(_pl,v)?v:null; }
function flytt(dx,dz){ controls.target.x+=dx; controls.target.z+=dz; cam.position.x+=dx; cam.position.z+=dz; }
function settZoom(z, anker){ // ortografisk: å skalere avstanden til ankeret med z/z' holder ankeret fast på skjermen
  z=THREE.MathUtils.clamp(z, controls.minZoom, controls.maxZoom);
  if(anker){ const f=cam.zoom/z; const tx=anker.x+(controls.target.x-anker.x)*f, tz=anker.z+(controls.target.z-anker.z)*f; flytt(tx-controls.target.x, tz-controls.target.z); }
  cam.zoom=z; cam.updateProjectionMatrix();
}
function innenforGrense(dt){ // myk fjær tilbake hvis man har dratt byen ut av syne
  const dx=controls.target.x-HOME.target.x, dz=controls.target.z-HOME.target.z, d=Math.hypot(dx,dz);
  if(d>GRENSE){ const k=1-Math.exp(-dt*6); const ny=(d-GRENSE)*k/d; flytt(-dx*ny,-dz*ny); }
}
function vinkler(off){ const r=off.length(); return {az:Math.atan2(off.x,off.z), pol:Math.acos(THREE.MathUtils.clamp(off.y/r,-1,1))}; }
function kortVei(a,b){ let d=b-a; while(d>Math.PI) d-=2*Math.PI; while(d<-Math.PI) d+=2*Math.PI; return a+d; }
// flyTo: myk bane for mål, zoom (logaritmisk), asimut (korteste vei) og helning. Med anker: punktet står stille under pekeren.
function flyTo(nyTarget, nyZoom, az, opt={}){
  const off=cam.position.clone().sub(controls.target); const v=vinkler(off);
  const tilAz = az===undefined ? v.az : kortVei(v.az, az);
  const tilPol = opt.pol!==undefined ? opt.pol : (az===undefined ? v.pol : Math.PI/2-ELEV);
  const z0=cam.zoom, z1=THREE.MathUtils.clamp(nyZoom, controls.minZoom, controls.maxZoom);
  const spenn=(cam.right-cam.left)/z0;
  const avst=nyTarget? Math.hypot(nyTarget.x-controls.target.x, nyTarget.z-controls.target.z) : 0;
  const dur = opt.dur || THREE.MathUtils.clamp(420 + 330*Math.abs(Math.log(z1/z0)) + 380*Math.abs(tilAz-v.az) + 260*Math.abs(tilPol-v.pol) + 520*Math.min(1, avst/spenn), 450, 1500);
  anim={t0:performance.now(), dur, e: opt.e || ease, fra:{t:controls.target.clone(), z:z0, az:v.az, pol:v.pol, r:off.length()}, til:{t:nyTarget?nyTarget.clone():controls.target.clone(), z:z1, az:tilAz, pol:tilPol}, anker:opt.anker||null};
  zoomAnker=null;
}
function stepAnim(){
  if(!anim) return; const k=Math.min(1,(performance.now()-anim.t0)/anim.dur); const e=anim.e(k);
  const z=Math.exp(THREE.MathUtils.lerp(Math.log(anim.fra.z), Math.log(anim.til.z), e));
  if(anim.anker){ const A=anim.anker, f=anim.fra.z/z; controls.target.set(A.x+(anim.fra.t.x-A.x)*f, 0, A.z+(anim.fra.t.z-A.z)*f); }
  else controls.target.lerpVectors(anim.fra.t, anim.til.t, e);
  const az=THREE.MathUtils.lerp(anim.fra.az, anim.til.az, e), pol=THREE.MathUtils.lerp(anim.fra.pol, anim.til.pol, e), r=anim.fra.r;
  cam.position.set(controls.target.x+r*Math.sin(pol)*Math.sin(az), controls.target.y+r*Math.cos(pol), controls.target.z+r*Math.sin(pol)*Math.cos(az));
  cam.zoom=z; cam.updateProjectionMatrix(); cam.lookAt(controls.target);
  if(k>=1){ anim=null; zoomMaal=cam.zoom; controls.update(); }
}
function stoppAnim(){ if(anim){ anim=null; zoomMaal=cam.zoom; } }

// avbryt introen når brukeren tar tak: kameraet blir stående der det er, byen vokser ferdig av seg selv
function overta(){ if(introDone) return; introDone=true; zoomMaal=cam.zoom; controls.enabled=true; controls.update(); }

function tick(){
  maalYtelse();
  const naa=performance.now(), dt=Math.min(0.1,(naa-sisteTid)/1000); sisteTid=naa;
  const t=Q.get('t')?+Q.get('t'):clock.getElapsedTime();
  waterMat.uniforms.t.value=t;
  if(!vokst) vokse(t*VEKST_FART+0.45);
  if(!introDone){
    const k=THREE.MathUtils.clamp((t-SPIN_START)/SPIN,0,1); const e=1-Math.pow(1-k,4); // rask start, myk landing
    cam.zoom=THREE.MathUtils.lerp(Z0,1,e); cam.updateProjectionMatrix();
    place(AZ0 + SVEIP*(1-e), THREE.MathUtils.lerp(EL0,ELEV,e));
    if(t>SPIN_START){ if(k>=1){ introDone=true; zoomMaal=cam.zoom; controls.enabled=true; controls.update(); setTimeout(()=>document.getElementById('hint').style.opacity=1,300); setTimeout(()=>document.getElementById('hint').style.opacity=0,6000);} }
  } else {
    if(anim) stepAnim();
    else {
      // myk zoom mot målet (hjul/styreflate), ankeret står stille under pekeren
      if(Math.abs(Math.log(zoomMaal/cam.zoom))>1e-4){ const k=1-Math.exp(-dt*13); settZoom(Math.exp(Math.log(cam.zoom)+(Math.log(zoomMaal)-Math.log(cam.zoom))*k), zoomAnker); }
      innenforGrense(dt);
      controls.update();
    }
    visHjem();
  }
  // løftet hus (valgt) og svakt løftet hus (pekeren over), uavhengig av bildefrekvens
  const kl=1-Math.exp(-dt*11);
  let husBeveger=!vokst;
  buildings.forEach(g=>{ const ty=g.userData.lift?3:(g===hover?0.9:0); const dy=(ty-g.position.y)*kl; if(Math.abs(dy)>1e-4){ g.position.y+=dy; husBeveger=true; } });
  if(husBeveger) skyggeSkitten=true;
  if(!introDone) skyggeSkitten=true;
  oppdaterSol();
  // beveger kartet seg? da tegnes det raskt; står det stille, tegnes det skarpt én gang og deretter rolig (vannet lever)
  const kamFlytt = !_sisteKam.equals(cam.matrixWorld) || _sisteZ!==cam.zoom; _sisteKam.copy(cam.matrixWorld); _sisteZ=cam.zoom;
  // kvaliteten følger bare kameraet: hus som løfter seg tegnes i full kvalitet hvert bilde, så et klikk ikke bytter tilstand
  if(kamFlytt || anim || !introDone) sistBeveg=naa;
  const stille = naa-sistBeveg>300;
  post.settSkala(stille? skalaStille : skalaBeveg); post.setAO(stille? aoStille : aoBeveg); post.setSS(stille && perfNivaa<2 ? ssStille : 1);
  if(introDone && stille){ speilInn=Math.min(1,speilInn+dt*2.8); speil.render(husBeveger || speilInn<1 || !speilFrisk); speilFrisk=true; }
  else if(!stille){ speilFrisk=false; speilInn=Math.max(0,speilInn-dt*8); } // gammelt speil vises aldri mens kartet beveger seg
  waterMat.uniforms.reflStyrke.value=speilStyrke()*speilInn;
  if(!stille || husBeveger || !fullTegnet || naa-sistTegnet>100){ post.render(); sistTegnet=naa; fullTegnet=stille && !husBeveger; if(!_synlig){ _synlig=true; requestAnimationFrame(()=>renderer.domElement.style.opacity=1); } }
  dbgTegn(naa);
  requestAnimationFrame(tick);
}
