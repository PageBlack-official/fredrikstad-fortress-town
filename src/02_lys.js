// ---- lys: sola ----
// Plakatsolen (standard): sola står øverst til venstre i bildet uansett hvordan byen snus, som i trykkfila.
// Ekte sol: setSol(asimut, høyde) i radianer, asimut fra nord med klokka. Skyggene følger sola i begge moduser.
const hemi = new THREE.HemisphereLight(0xffffff, 0xe6e2d6, 1.0); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 0.85);
sun.castShadow = true;
sun.shadow.mapSize.set(innerWidth*devicePixelRatio>=2000?3072:2048, innerWidth*devicePixelRatio>=2000?3072:2048); // kartet dekker 40 % mer enn bildet (se oppdaterSol), så store skjermer får flere tekster
const sc = sun.shadow.camera; sc.left=-520; sc.right=520; sc.top=520; sc.bottom=-520; sc.near=1; sc.far=6000;   // sola står 2500 m ute (se oppdaterSol), så R opptil 1650 m ligger foran kameraet
sun.shadow.bias=-0.0005; sun.shadow.normalBias=0.25; sun.shadow.radius=4; sun.shadow.blurSamples=12;
const LYS = new THREE.Vector3(-0.66, 0.52, 0.54).normalize(); // lyset penselmatcapen til trærne er tegnet med (kamerarommet)
// plakatsolen i kamerarommet: fra venstre og litt over, så venstre fasader og tak er lyse, høyre fasader i skygge (som trykket),
// og kastskyggene faller mot høyre i bildet der de synes, ikke bak husene
const PLAKAT = new THREE.Vector3(-0.75, 0.65, 0.10).normalize();
const GRAD=Math.PI/180;
// solposisjon (samme formler som SunCalc): asimut fra nord med klokka og høyde over horisonten, i radianer
function solposisjon(dato, lat=59.2075, lon=10.9545){
  const dager=dato.valueOf()/864e5-0.5+2440588-2451545;
  const M=GRAD*(357.5291+0.98560028*dager);
  const C=GRAD*(1.9148*Math.sin(M)+0.02*Math.sin(2*M)+0.0003*Math.sin(3*M));
  const L=M+C+GRAD*102.9372+Math.PI, e=GRAD*23.4397;
  const dek=Math.asin(Math.sin(e)*Math.sin(L)), ra=Math.atan2(Math.sin(L)*Math.cos(e),Math.cos(L));
  const phi=GRAD*lat, H=GRAD*(280.16+360.9856235*dager)+GRAD*lon-ra;
  const hoyde=Math.asin(Math.sin(phi)*Math.sin(dek)+Math.cos(phi)*Math.cos(dek)*Math.cos(H));
  const azSor=Math.atan2(Math.sin(H),Math.cos(H)*Math.sin(phi)-Math.tan(dek)*Math.cos(phi));
  return {asimut:azSor+Math.PI, hoyde};
}
const SOL={modus:'plakat', asimut:0, hoyde:35*GRAD};
// sollyset blir varmere jo lavere sola står
function solFargeFor(hoyde){ const k=THREE.MathUtils.smoothstep(hoyde,4*GRAD,34*GRAD);
  sun.color.setRGB(1.0, THREE.MathUtils.lerp(0.80,0.985,k), THREE.MathUtils.lerp(0.62,0.95,k)); }
function setSol(asimut, hoyde){
  SOL.modus='ekte'; SOL.asimut=asimut; SOL.hoyde=Math.max(hoyde,3*GRAD);
  solFargeFor(SOL.hoyde); skyggeSkitten=true;
}
function plakatSol(){
  SOL.modus='plakat';
  if(sun.parent!==scene){ sun.parent&&sun.parent.remove(sun); sun.target.parent&&sun.target.parent.remove(sun.target); scene.add(sun); scene.add(sun.target); }
  solFargeFor(35*GRAD); skyggeSkitten=true;
}
window.__skyggeNy=()=>{ dekning.r=0; };   // test: tvinger skyggekartet tegnet på nytt om samme senter (verktoy/skygge-dra-test.mjs)
window.__sol=()=>({sd:_sd.toArray(), q:cam.quaternion.toArray(), grunner:dekning.grunner, R:dekning.r, r:dekning.rBilde}); window.setSol=setSol; window.plakatSol=plakatSol; window.solposisjon=solposisjon;
// fast sol: asimut 250° (VSV) og 42° høyde gir samme lysside som plakaten i hjemmevisningen, litt høyere så baksiden fortsatt leser som farge
function lysFraVenstre(){ plakatSol(); if(SOL_FAST) setSol(250*GRAD, 42*GRAD); }
// skravur i skyggene (stil b): parallelle streker forankret i byen; avstanden settes per bilde i meter (0 = av)
const U_SKRAVUR={value:0};
// skyggekartet er forankret i byen og tegnes på nytt bare når det må: bildet har gått ut av dekningen, zoomen eller
// solretningen har endret seg merkbart, eller sola/husene har flyttet seg. Flytting (dra) innenfor dekningen koster ingen skyggetegning.
sun.shadow.autoUpdate=false; let skyggeSkitten=true, kameraBeveget=true; const sistKam=new THREE.Matrix4();
const dekning={r:0, senter:new THREE.Vector3(), retning:new THREE.Vector3(), grunner:{}, sist:0};
const _sd=new THREE.Vector3(), _st=new THREE.Vector3(), _q=new THREE.Quaternion(), _m4=new THREE.Matrix4(), _hoyre=new THREE.Vector3(), _opp=new THREE.Vector3(), _senter=new THREE.Vector3();
function oppdaterSol(){
  const tg=kam.senter;
  cam.updateMatrixWorld(); kameraBeveget = !sistKam.equals(cam.projectionMatrix) || !introDone; if(kameraBeveget) sistKam.copy(cam.projectionMatrix);
  // solretningen (lyset på fasadene) følger kameraet hvert bilde; skyggekartet følger etter i steg
  if(SOL.modus==='ekte'){ const ca=Math.cos(SOL.hoyde); _sd.set(Math.sin(SOL.asimut)*ca, Math.sin(SOL.hoyde), -Math.cos(SOL.asimut)*ca); }
  else _sd.copy(PLAKAT).applyQuaternion(cam.quaternion);   // plakatsola: øverst til venstre i bildet uansett hvordan byen snus
  sun.target.position.copy(tg); sun.position.copy(tg).addScaledVector(_sd,2500); sun.target.updateMatrixWorld(); // lysretningen hvert bilde; skyggekartets matriser oppdateres bare når kartet tegnes på nytt
  // bildet dekkes av skyggekameraet med margin, så skyggene er skarpe nok tett på og et dra ikke går ut av kartet med en gang
  const hw=kam.mpp*innerWidth/2, hh=kam.mpp*innerHeight/2;
  const r=Math.min(950, Math.max(hw, hh/Math.sin((90-kam.pitch)*GRAD))*1.08+45); dekning.rBilde=r;
  let grunn = dekning.r===0 ? 'start' : (r>dekning.r*0.78 || r<dekning.r*0.45) ? 'zoom'   // zoomet: kartet dekker for lite eller er for grovt
    : Math.hypot(tg.x-dekning.senter.x, tg.z-dekning.senter.z) > dekning.r*0.3 ? 'dratt'    // dratt ut av marginen
    : _sd.angleTo(dekning.retning) > 1.5*GRAD ? 'snudd'                                      // snudd eller vippet: sola står et annet sted
    : skyggeSkitten ? 'by' : '';                                                             // sola, husene eller introen
  // myke grunner (litt snudd, hus som glir) ventes med til 150 ms har gått mens kameraet er i fart, så et dra ikke tegner skyggekartet hvert bilde;
  // står kameraet stille, tegnes det med en gang, så det siste bildet alltid er riktig
  const naa=performance.now();
  if((grunn==='snudd' || grunn==='by') && kameraBeveget && naa-dekning.sist<150 && introDone) grunn='';   // i introen tegnes skyggekartet hvert bilde: sola synker og skyggene vokser
  if(grunn){ dekning.grunner[grunn]=(dekning.grunner[grunn]||0)+1; dekning.sist=naa;
    // Stabilt skyggekart (24.10, Vegar på mobil: «skyggene tegnes hele tiden så det flakker»): på en liten skjerm går et dra ut av
    // marginen ofte, og hver ny tegning med ny skala og nytt senter flyttet tekselrutenettet, så de myke kantene krøp. Nå er
    // dekningen trinnvis (1100 m delt på 1,5^k) og senteret låst til tekselrutenettet i lysets plan, så to tegninger av samme
    // sted gir samme teksler; bare innholdet (hus som løfter seg) kan endre seg.
    // 28.10: trinnet rundes NED, så R alltid er minst 1,4·r. Med Math.ceil (24.10–27.10) ble R ofte mindre enn bildet: skyggene
    // kuttet i kanten av dekningen, kanten fulgte kameraet, og «zoom» tegnet kartet på nytt hvert bilde (Vegar: «trærnes skygge
    // tegnes på nytt hver gang jeg flytter meg»). Regel 19 måler at dekningen holder og at et dra ikke tegner kartet på nytt.
    const trinn=Math.max(-1, Math.floor(Math.log(1100/(r*1.4))/Math.log(1.5)));
    const R=1100/Math.pow(1.5,trinn);                                                        // minst 40 % margin rundt bildet (maks 1650 m)
    if(Math.abs(sc.right-R)>0.5){ sc.left=-R; sc.right=R; sc.top=R; sc.bottom=-R; sc.updateProjectionMatrix(); }
    sun.shadow.radius=THREE.MathUtils.clamp(1.1/(2*R/sun.shadow.mapSize.x),1.5,9);
    const teksel=2*R/sun.shadow.mapSize.x;
    _hoyre.set(0,1,0).cross(_sd).normalize(); _opp.copy(_sd).cross(_hoyre).normalize();     // lysets plan: høyre og opp
    const cx=tg.dot(_hoyre), cy=tg.dot(_opp);
    _senter.copy(tg).addScaledVector(_hoyre, Math.round(cx/teksel)*teksel-cx).addScaledVector(_opp, Math.round(cy/teksel)*teksel-cy);
    sun.target.position.copy(_senter); sun.position.copy(_senter).addScaledVector(_sd,2500); sun.target.updateMatrixWorld(); sun.updateMatrixWorld();
    dekning.r=R; dekning.senter.copy(_senter); dekning.retning.copy(_sd);
    sun.shadow.needsUpdate=true; skyggeSkitten=false;
  }
  // trærne henter solretningen selv (se tre-blokken)
}
// felles GLSL for materialer som skal ta imot kastskygger og følge sola
const GL_SOL_V=`#include <common>
#include <shadowmap_pars_vertex>
varying vec3 vWq;
`;
const glSolVMain=(wp,wn)=>`
#if defined(USE_SHADOWMAP) && NUM_DIR_LIGHT_SHADOWS>0
  vDirectionalShadowCoord[0]=directionalShadowMatrix[0]*(${wp}+vec4((${wn})*directionalLightShadows[0].shadowNormalBias,0.));
#endif
  vWq=(${wp}).xyz;
`;
const GL_SOL_F=`#include <common>
#include <packing>
#include <shadowmap_pars_fragment>
varying vec3 vWq;
// Sola finner byen (28.10, Vegar: «A»): i introen er byen overskyet (ingen kastskygger, kjølig), og en solkant vandrer over byen.
// Kanten er et plan i verden (solFrontDir), flyttet av solFront, myk over solBredde meter; høye punkter (kirketårnet) får lys litt før.
// Etter introen er solUte 1 og alt dette er én sammenligning per piksel. Ingen overlegg: skyggene som vokser fram er ekte skygger.
uniform float solUte, solFront, solBredde; uniform vec3 solFrontDir;
float solHer(vec3 wq){ if(solUte>=1.) return 1.; float v=dot(wq.xz, solFrontDir.xz)+0.8*wq.y; return smoothstep(solFront, solFront+solBredde, v); }
const vec3 OVERSKYET=vec3(0.86,0.90,0.97);   // overskyet: mørkere og kjøligere enn sol, så det synes at sola kommer
#if NUM_DIR_LIGHTS>0
struct DirectionalLight { vec3 direction; vec3 color; };
uniform DirectionalLight directionalLights[NUM_DIR_LIGHTS];
#endif
// myk kastskygge: 16 prøver i en roterende spiral, halvskyggen er ca. én meter bred uansett zoom
float skyggeMask(){ float s=1.;
#if defined(USE_SHADOWMAP) && NUM_DIR_LIGHT_SHADOWS>0
  DirectionalLightShadow dl=directionalLightShadows[0];
  vec4 sc=vDirectionalShadowCoord[0]; vec3 p=sc.xyz/sc.w; p.z+=dl.shadowBias;
  if(p.x>=0.&&p.x<=1.&&p.y>=0.&&p.y<=1.&&p.z<=1.){
    vec2 tx=dl.shadowRadius/dl.shadowMapSize; float acc=0.;
    float ang=fract(52.9829189*fract(dot(gl_FragCoord.xy,vec2(0.06711056,0.00583715))))*6.2831853;
    for(int i=0;i<16;i++){ float r=sqrt((float(i)+0.5)/16.); float a=float(i)*2.3999632+ang;
      acc+=texture2DCompare(directionalShadowMap[0], p.xy+vec2(cos(a),sin(a))*r*tx, p.z); }
    s=acc/16.;
  }
#endif
  return mix(1., s, solHer(vWq)); }
vec3 solRetning(){
#if NUM_DIR_LIGHTS>0
  return directionalLights[0].direction;
#else
  return normalize(vec3(-0.66,0.52,0.54));
#endif
}
vec3 solFarge(){
#if NUM_DIR_LIGHTS>0
  vec3 c=directionalLights[0].color; return c/max(max(c.r,c.g),max(c.b,1e-4));
#else
  return vec3(1.);
#endif
}
uniform float skravur;
// skravurmaske: 1 der det skal ligge en strek, 0 ellers; k er skyggemengden (0 lys, 1 skygge). Tynnes ut når strekene blir for tette på skjermen
float skravurMaske(vec3 wq, float k){ if(skravur<=0.) return 0.;
  float t=dot(wq, normalize(vec3(0.6,1.0,0.4)))/skravur; float fw=fwidth(t);
  float f=abs(fract(t)*2.-1.); float linje=smoothstep(0.62-fw*1.5, 0.62+fw*1.5, f);
  float tetthet=1.-smoothstep(0.25,0.5,fw);
  return linje*tetthet*smoothstep(0.15,0.6,k); }
const vec3 KALD=vec3(0.92,0.96,1.07);   // skyggetonen litt kjølig
const vec3 KASTSKYGGE=vec3(0.57,0.62,0.80); // kastskygge på bakken: mørkere og blålig
`;
// solfronten deles av alle materialer: ett objekt per uniform, koblet inn etter at scenen er bygd (kobleSol, kalles fra 15_loop)
const U_SOL={ ute:{value:1}, front:{value:-1e6}, bredde:{value:90}, dir:{value:new THREE.Vector3(1,0,0)} };
function kobleSol(){ let n=0; scene.traverse(o=>{ const ms=o.material?[].concat(o.material):[]; for(const m of ms){ if(m.isShaderMaterial && m.fragmentShader.includes('solHer(')){ m.uniforms.solUte=U_SOL.ute; m.uniforms.solFront=U_SOL.front; m.uniforms.solBredde=U_SOL.bredde; m.uniforms.solFrontDir=U_SOL.dir; m.needsUpdate=true; n++; } } }); return n; }
// gjør et eksisterende ShaderMaterial for flater (bakke, plen, brostein) mottakelig for kastskygger
function medSkygge(m){
  m.lights=true; Object.assign(m.uniforms, THREE.UniformsUtils.clone(THREE.UniformsLib.lights), {skravur:U_SKRAVUR});
  m.vertexShader=GL_SOL_V+m.vertexShader.replace(/}\s*$/, glSolVMain('(modelMatrix*vec4(position,1.))','vec3(0.,1.,0.)')+'}');
  m.fragmentShader=GL_SOL_F+m.fragmentShader.replace('#include <colorspace_fragment>','{ float su=solHer(vWq); vec3 sol=mix(gl_FragColor.rgb*KASTSKYGGE, gl_FragColor.rgb*mix(vec3(1.),solFarge(),0.5), skyggeMask()); gl_FragColor.rgb=mix(gl_FragColor.rgb*OVERSKYET, sol, su); gl_FragColor.rgb*=1.-0.28*skravurMaske(vWq, 1.-skyggeMask()); }\n#include <colorspace_fragment>');
  m.needsUpdate=true; return m;
}
