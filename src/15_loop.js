// ---- tegneløkka: MapLibre kaller lagets render() hvert bilde det tegner; vi ber om nye bilder når noe beveger seg ----
lysFraVenstre();
// byen tegner seg opp: høyden vokser kvartal for kvartal (sortert sørvest -> nordøst)
const order = buildings.map(g=>{const c=g.userData.b.r; return [g, c[0]+c[1]];}).sort((a,b)=>a[1]-b[1]);
order.forEach(([g],k)=>{ g.userData.delay = 1.1*k/order.length; g.scale.y=0.001; });
let vokst=false;   // husene og trærne har vokst ferdig
function vokse(t){
  let ferdig=true;
  buildings.forEach(g=>{ const k=THREE.MathUtils.clamp((t-g.userData.delay)/0.5,0,1); g.scale.y=Math.max(0.001, 1-Math.pow(1-k,3)); if(k<1) ferdig=false; husTil(g); });
  if(t<3.4){ setCrowns(t); ferdig=false; } else setCrowns(null);
  if(ferdig) vokst=true;
}
const SPIN=3.4, VEKST_FART=1.8, Z0=0.82, EL0=52, SVEIP=110;
// kamerabevegelser uten bråstopp (lys-og-bevegelse pkt. 2, teknikk 18 og 20): alle animerte flytt bruker samme kurve, eksponentiell inn og ut:
// farten bygges opp like lenge som den dør ut, og avstanden til målet halveres jevnt mot slutten i stedet for å stoppe på et punkt.
// ?glid=0 gir de gamle kurvene til sammenligning.
const GLID = Q0.get('glid')!=='0';
const glid = t => !GLID ? (t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2) : t<=0 ? 0 : t>=1 ? 1 : t<0.5 ? Math.pow(2,20*t-10)/2 : (2-Math.pow(2,-20*t+10))/2;
const glidUt = t => !GLID ? 1-Math.pow(1-t,3) : t>=1 ? 1 : 1-Math.pow(2,-10*t);   // bare utglidning (når bevegelsen alt er i gang)
let anim=false, husBeveger=false, sisteTid=performance.now();
const hjemVisning=()=>({center: tilLngLat(START[0],START[1]), zoom: Z_HJEM, bearing: -AZ0_GRADER, pitch: PITCH0});
const HOME={target:new THREE.Vector3(START[0],0,-START[1])};

// intro: starter høyere og nærmere, og svinger 110° inn mot plakatvinkelen mens byen vokser opp
function startIntro(){
  map.jumpTo({center: tilLngLat(START[0],START[1]), zoom: zoomFor(Z0), bearing: -(AZ0_GRADER+SVEIP), pitch: 90-EL0});
  map.easeTo({...hjemVisning(), duration: SPIN*1000, easing: GLID ? glid : (t=>1-Math.pow(1-t,4)), essential:true});
  map.once('moveend', ()=>{ if(!introDone){ introDone=true; setTimeout(()=>document.getElementById('hint').style.opacity=1,300); setTimeout(()=>document.getElementById('hint').style.opacity=0,6000); } });
}
function overta(){ if(introDone) return; introDone=true; map.stop(); }
// ---- Sola finner byen (28.10, Vegar: «A») ----
// Introen starter overskyet: tegningens to toner, ingen kastskygger, litt kjøligere. Mens kameraet svinger inn, vandrer en solkant
// over byen fra solsiden (høye punkter først), kastskyggene vokser fram der kanten har passert, og sola synker fra 58° til de
// godkjente 42° (23.10), så skyggene blir lange idet kameraet lander. Lyset er bundet til kameraets vei (bearing), ikke til klokka
// (teknikk 12): stopper du introen, henter solkanten seg inn på 0,8 s. ?solintro=0 hopper over det hele.
const SOLINTRO = SOL_FAST && !Q0.get('sol') && Q0.get('solintro')!=='0' && !Q.get('skip');   // ?solintro=0 gir den gamle introen med fast sol
const solVei={ v0:0, v1:0, u:0, ferdig:!SOLINTRO, tHent:0 };
function solStart(){
  // kanten vandrer langs solas horisontale retning: solsiden av byen først
  const ca=Math.cos(42*GRAD); U_SOL.dir.value.set(Math.sin(250*GRAD)*ca, 0, -Math.cos(250*GRAD)*ca).normalize();
  let lo=1e9, hi=-1e9; buildings.forEach(g=>{ const r=g.userData.b.r; const v=r[0]*U_SOL.dir.value.x+(-r[1])*U_SOL.dir.value.z; lo=Math.min(lo,v); hi=Math.max(hi,v); });
  solVei.v0=hi+U_SOL.bredde.value+40; solVei.v1=lo-U_SOL.bredde.value-40;   // fra «ingenting lyst» til «alt lyst», litt utenfor byen i begge ender
  U_SOL.ute.value=0; U_SOL.front.value=solVei.v0; setSol(250*GRAD, 58*GRAD);
}
function solTil(u){   // u 0..1 langs kameraets vei
  const k=glid(THREE.MathUtils.clamp((u-0.08)/0.80, 0, 1));            // kanten går mellom 8 % og 88 % av veien, med samme kurve som kameraet
  U_SOL.front.value=solVei.v0+(solVei.v1-solVei.v0)*k;
  setSol(250*GRAD, (58-16*k)*GRAD);
  if(k>=1 && u>=0.999){ U_SOL.ute.value=1; U_SOL.front.value=-1e6; solVei.ferdig=true; }
}
function solOppdater(dt){
  if(solVei.ferdig) return;
  if(!introDone){ const b0=-(AZ0_GRADER+SVEIP), b1=-AZ0_GRADER; solVei.u=THREE.MathUtils.clamp((map.getBearing()-b0)/(b1-b0),0,1); solTil(solVei.u); }
  else { solVei.u=Math.min(1, solVei.u+dt/0.8); solTil(solVei.u); if(solVei.u>=1) solTil(1); }   // introen ble avbrutt: hent inn resten
  skyggeSkitten=true;
}
window.__solvei=()=>({u:solVei.u, front:U_SOL.front.value, ute:U_SOL.ute.value, ferdig:solVei.ferdig});
window.__introStill=u=>{ window.__vis(AZ0_GRADER+SVEIP*(1-u), Z0+(1-Z0)*u, START[0], START[1]); window.__solTil(u); };   // kamera + lys ved u langs introveien
window.__solTil=u=>{ if(solVei.v0===0) solStart(); solVei.ferdig=true; U_SOL.ute.value=0; solTil(u); if(u>=1){ U_SOL.ute.value=1; U_SOL.front.value=-1e6; } skyggeSkitten=true; map.triggerRepaint(); };   // stillbilder av introlyset (verktoy/sol-intro-stills.mjs); u 0..1
map.on('movestart', e=>{ if(e.originalEvent) overta(); });

// husets løft og vekst: egne grupper (kirka, portbygg, bygg med deler) flyttes som objekter; alle andre ligger i de sammenslåtte nettene og styres per bygg via hus-teksturen (05_bygg)
function husTil(g){ if(!g.userData.spesiell) settHus(g.userData.i, g.position.y, g.scale.y); }
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
  buildings.forEach(g=>{ const ty=g.userData.lift?3:(g===hover?0.9:0); const dy=(ty-g.position.y)*kl; if(Math.abs(dy)>1e-3){ g.position.y+=dy; husTil(g); husBeveger=true; if(Math.abs(dy)>0.02) skyggeSkitten=true; } });
  if(!introDone) skyggeSkitten=true;
  solOppdater(dt);
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
  kobleSol(); if(SOLINTRO) solStart();
  if(Q.get('skip')){ introDone=true; vokst=true; buildings.forEach(g=>{ g.scale.y=1; husTil(g); }); setCrowns(null); map.jumpTo({...hjemVisning(), bearing: Q.get('az')?-(+Q.get('az')):-AZ0_GRADER, zoom: Q.get('zoom')?zoomFor(+Q.get('zoom')):Z_HJEM}); }
  else startIntro();
  puls();
});
// testkroker (skjermbilder uten ny sidelasting)
window.__skjerm=(x,z)=>{ const v=new THREE.Vector3(x,0,z).project(cam); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; };
window.__kam=()=>{ const v=vinkler(); let vs=null; if(valgt){ const c=husBoks(valgt).getCenter(new THREE.Vector3()); vs=window.__skjerm(c.x,c.z); } return {x:kam.senter.x,z:kam.senter.z,zoom:kam.zoomfaktor,az:v.az,pol:v.pol,anim:map.isMoving(),valgt:vs,intro:!introDone,t:clock.getElapsedTime(),oye:kam.oye.toArray(), naer:kam.naer, fjern:kam.fjern, fov:kam.fov, mpp:kam.mpp}; };
window.__vis=(az,zoom,tx,ty)=>{ introDone=true; vokst=true; buildings.forEach(g=>{ g.scale.y=1; husTil(g); }); setCrowns(null); map.jumpTo({center: tilLngLat(tx,ty), zoom: zoomFor(zoom), bearing: -az, pitch: PITCH0}); };
window.__kontakt=v=>{ kontaktMat.uniforms.styrke.value=v; map.triggerRepaint(); };   // regel 12: av/på i samme økt, samme kamera og skyggekart
window.__scene=()=>({scene, city});   // feilsøk: tell objekter i scenen (verktoy/tell.mjs)
window.__kval=()=>({skala:post.skala(), ao:aoStille, ss:ssStille, perfNivaa, stille:performance.now()-sistBeveg>300, beveger:map.isMoving()});
window.__skjerm3=(x,y,z)=>{ const v=new THREE.Vector3(x,y,z).project(cam); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; };
