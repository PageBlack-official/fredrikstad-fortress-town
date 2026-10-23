// ---- tegneløkka: MapLibre kaller lagets render() hvert bilde det tegner; vi ber om nye bilder når noe beveger seg ----
lysFraVenstre();
// byen tegner seg opp: høyden vokser kvartal for kvartal (sortert sørvest -> nordøst)
const order = buildings.map(g=>{const c=g.userData.b.r; return [g, c[0]+c[1]];}).sort((a,b)=>a[1]-b[1]);
order.forEach(([g],k)=>{ g.userData.delay = 1.1*k/order.length; g.scale.y=0.001; });
let vokst=false;   // husene og trærne har vokst ferdig
function vokse(t){
  let ferdig=true;
  buildings.forEach(g=>{ const k=THREE.MathUtils.clamp((t-g.userData.delay)/0.5,0,1); g.scale.y=Math.max(0.001, 1-Math.pow(1-k,3)); if(k<1) ferdig=false; });
  if(t<3.4){ setCrowns(t); ferdig=false; } else setCrowns(null);
  if(ferdig) vokst=true;
}
const SPIN=3.4, VEKST_FART=1.8, Z0=0.82, EL0=52, SVEIP=110;
let anim=false, husBeveger=false, sisteTid=performance.now();
const hjemVisning=()=>({center: tilLngLat(START[0],START[1]), zoom: Z_HJEM, bearing: -AZ0_GRADER, pitch: PITCH0});
const HOME={target:new THREE.Vector3(START[0],0,-START[1])};

// intro: starter høyere og nærmere, og svinger 110° inn mot plakatvinkelen mens byen vokser opp
function startIntro(){
  map.jumpTo({center: tilLngLat(START[0],START[1]), zoom: zoomFor(Z0), bearing: -(AZ0_GRADER+SVEIP), pitch: 90-EL0});
  map.easeTo({...hjemVisning(), duration: SPIN*1000, easing: t=>1-Math.pow(1-t,4), essential:true});
  map.once('moveend', ()=>{ if(!introDone){ introDone=true; setTimeout(()=>document.getElementById('hint').style.opacity=1,300); setTimeout(()=>document.getElementById('hint').style.opacity=0,6000); } });
}
function overta(){ if(introDone) return; introDone=true; map.stop(); }
map.on('movestart', e=>{ if(e.originalEvent) overta(); });

// tilstand per bilde: vekst, hus som løfter seg, sol/skygge, tegnekvalitet
const _sisteProj=new THREE.Matrix4();
function oppdater(){
  maalYtelse();
  const naa=performance.now(), dt=Math.min(0.1,(naa-sisteTid)/1000); sisteTid=naa;
  const t=Q.get('t')?+Q.get('t'):clock.getElapsedTime();
  waterMat.uniforms.t.value=t;
  if(!vokst) vokse(t*VEKST_FART+0.45);
  anim=map.isMoving();
  // løftet hus (valgt) og svakt løftet hus (pekeren over), uavhengig av bildefrekvens
  const kl=1-Math.exp(-dt*11);
  husBeveger=!vokst;
  // skyggekartet tegnes på nytt bare mens et hus flytter seg merkbart (over 2 cm per bilde); halen av glidningen synes ikke i skyggen
  buildings.forEach(g=>{ const ty=g.userData.lift?3:(g===hover?0.9:0); const dy=(ty-g.position.y)*kl; if(Math.abs(dy)>1e-3){ g.position.y+=dy; husBeveger=true; if(Math.abs(dy)>0.02) skyggeSkitten=true; } });
  if(!introDone) skyggeSkitten=true;
  oppdaterSol();
  U_SKRAVUR.value = STIL.skravur ? kam.mpp*5*innerWidth/renderer.domElement.width*renderer.getPixelRatio() : 0;   // skravur: 5 skjermpunkter mellom strekene
  // én kvalitet: oppløsning, hjørneskygge og strek er de samme i fart og i ro (se 00_oppsett). «stille» styrer bare speilet i vannet.
  const kamFlytt = !_sisteProj.equals(cam.projectionMatrix); _sisteProj.copy(cam.projectionMatrix);
  if(kamFlytt || anim || !introDone) sistBeveg=naa;
  const stille = naa-sistBeveg>300;
  post.settSkala(skalaStille); post.setAO(aoStille); post.setSS(ssStille);
  if(introDone && stille){ speilInn=Math.min(1,speilInn+dt*2.8); speil.render(husBeveger || speilInn<1 || !speilFrisk); speilFrisk=true; }
  else if(!stille){ speilFrisk=false; speilInn=Math.max(0,speilInn-dt*8); } // gammelt speil vises aldri mens kartet beveger seg
  waterMat.uniforms.reflStyrke.value=speilStyrke()*speilInn;
  sistTegnet=naa; fullTegnet=stille && !husBeveger;
  dbgTegn(naa);
}
// laget: kartet tegner byen gjennom dette
const byLag={ id:'byen', type:'custom', renderingMode:'3d',
  onAdd(){ post.size(); speil.size(); },
  render(gl,args){ window.__vaareBilder++; const t0=performance.now(); window.__mellom=t0-(window.__slutt||t0); kameraFraKartet(args); renderer.resetState(); gl.depthRange(0,1); oppdater(); post.render(); window.__slutt=performance.now(); window.__ramme=window.__slutt-t0; if(!_synlig){ _synlig=true; requestAnimationFrame(()=>map.getCanvas().style.opacity=1); } } };
// ber kartet tegne på nytt når noe beveger seg; i ro tegnes det 10 ganger i sekundet (vannet lever)
function puls(){ const naa=performance.now(); if(!vokst || !introDone || husBeveger || map.isMoving() || naa-sistTegnet>100) map.triggerRepaint(); requestAnimationFrame(puls); }
// teller kartets egne bilder mot våre: tegner kartet et bilde uten å kalle laget vårt, blir det et papirfarget blink
window.__kartBilder=0; window.__vaareBilder=0; map.on('render', ()=>{ window.__kartBilder++; });
map.on('load', ()=>{
  map.addLayer(byLag);
  if(Q.get('skip')){ introDone=true; vokst=true; buildings.forEach(g=>g.scale.y=1); setCrowns(null); map.jumpTo({...hjemVisning(), bearing: Q.get('az')?-(+Q.get('az')):-AZ0_GRADER, zoom: Q.get('zoom')?zoomFor(+Q.get('zoom')):Z_HJEM}); }
  else startIntro();
  puls();
});
// testkroker (skjermbilder uten ny sidelasting)
window.__skjerm=(x,z)=>{ const v=new THREE.Vector3(x,0,z).project(cam); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; };
window.__kam=()=>{ const v=vinkler(); let vs=null; if(valgt){ const bb=new THREE.Box3().setFromObject(valgt); const c=bb.getCenter(new THREE.Vector3()); vs=window.__skjerm(c.x,c.z); } return {x:kam.senter.x,z:kam.senter.z,zoom:kam.zoomfaktor,az:v.az,pol:v.pol,anim:map.isMoving(),valgt:vs,intro:!introDone,t:clock.getElapsedTime(),oye:kam.oye.toArray(), naer:kam.naer, fjern:kam.fjern, fov:kam.fov, mpp:kam.mpp}; };
window.__vis=(az,zoom,tx,ty)=>{ introDone=true; vokst=true; buildings.forEach(g=>g.scale.y=1); setCrowns(null); map.jumpTo({center: tilLngLat(tx,ty), zoom: zoomFor(zoom), bearing: -az, pitch: PITCH0}); };
window.__kval=()=>({skala:post.skala(), ao:aoStille, ss:ssStille, perfNivaa, stille:performance.now()-sistBeveg>300, beveger:map.isMoving()});
window.__skjerm3=(x,y,z)=>{ const v=new THREE.Vector3(x,y,z).project(cam); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; };
