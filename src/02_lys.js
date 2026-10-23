// ---- lys: sola ----
// Plakatsolen (standard): sola står øverst til venstre i bildet uansett hvordan byen snus, som i trykkfila.
// Ekte sol: setSol(asimut, høyde) i radianer, asimut fra nord med klokka. Skyggene følger sola i begge moduser.
const hemi = new THREE.HemisphereLight(0xffffff, 0xe6e2d6, 1.0); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 0.85);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
const sc = sun.shadow.camera; sc.left=-520; sc.right=520; sc.top=520; sc.bottom=-520; sc.near=1; sc.far=4000;
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
window.setSol=setSol; window.plakatSol=plakatSol; window.solposisjon=solposisjon;
function lysFraVenstre(){ plakatSol(); }
// skyggekartet tegnes bare på nytt når kameraet, sola eller byen beveger seg
sun.shadow.autoUpdate=false; let skyggeSkitten=true, skyggeTakt=0, kameraBeveget=true; const sistKam=new THREE.Matrix4(); let sistZoom=0;
const _sd=new THREE.Vector3(), _st=new THREE.Vector3(), _q=new THREE.Quaternion(), _m4=new THREE.Matrix4();
function oppdaterSol(){
  const tg=kam.senter;
  if(SOL.modus==='ekte'){
    const ca=Math.cos(SOL.hoyde);
    sun.target.position.copy(tg); sun.position.set(tg.x+Math.sin(SOL.asimut)*ca*1500, tg.y+Math.sin(SOL.hoyde)*1500, tg.z-Math.cos(SOL.asimut)*ca*1500);
  } else {
    // plakatsola: står øverst til venstre i bildet uansett hvordan byen snus (retningen følger kameraet)
    _sd.copy(PLAKAT).applyQuaternion(cam.quaternion); sun.target.position.copy(tg); sun.position.copy(tg).addScaledVector(_sd,1500);
  }
  sun.target.updateMatrixWorld();
  // skyggekameraet dekker det som er i bildet, så skyggene er skarpe nok også tett på
  const hw=kam.mpp*innerWidth/2, hh=kam.mpp*innerHeight/2;
  const r=Math.min(950, Math.max(hw, hh/Math.sin((90-kam.pitch)*GRAD))*1.08+45);
  if(Math.abs(sc.right-r)>0.5){ sc.left=-r; sc.right=r; sc.top=r; sc.bottom=-r; sc.updateProjectionMatrix(); skyggeSkitten=true; }
  sun.shadow.radius=THREE.MathUtils.clamp(1.1/(2*r/sun.shadow.mapSize.x),1.5,9);
  cam.updateMatrixWorld();
  kameraBeveget = !sistKam.equals(cam.projectionMatrix) || !introDone;
  if(kameraBeveget){ sistKam.copy(cam.projectionMatrix); skyggeSkitten=true; }
  skyggeTakt++; if(skyggeSkitten && (skyggeTakt%3===0 || !kameraBeveget)){ sun.shadow.needsUpdate=true; skyggeSkitten=false; }
  // trærne henter solretningen selv (se tre-blokken)
}
// felles GLSL for materialer som skal ta imot kastskygger og følge sola
const GL_SOL_V=`#include <common>
#include <shadowmap_pars_vertex>
`;
const glSolVMain=(wp,wn)=>`
#if defined(USE_SHADOWMAP) && NUM_DIR_LIGHT_SHADOWS>0
  vDirectionalShadowCoord[0]=directionalShadowMatrix[0]*(${wp}+vec4((${wn})*directionalLightShadows[0].shadowNormalBias,0.));
#endif
`;
const GL_SOL_F=`#include <common>
#include <packing>
#include <shadowmap_pars_fragment>
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
  return s; }
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
const vec3 KALD=vec3(0.92,0.96,1.07);   // skyggetonen litt kjølig
const vec3 KASTSKYGGE=vec3(0.57,0.62,0.80); // kastskygge på bakken: mørkere og blålig
`;
// gjør et eksisterende ShaderMaterial for flater (bakke, plen, brostein) mottakelig for kastskygger
function medSkygge(m){
  m.lights=true; Object.assign(m.uniforms, THREE.UniformsUtils.clone(THREE.UniformsLib.lights));
  m.vertexShader=GL_SOL_V+m.vertexShader.replace(/}\s*$/, glSolVMain('(modelMatrix*vec4(position,1.))','vec3(0.,1.,0.)')+'}');
  m.fragmentShader=GL_SOL_F+m.fragmentShader.replace('#include <colorspace_fragment>','gl_FragColor.rgb=mix(gl_FragColor.rgb*KASTSKYGGE, gl_FragColor.rgb*mix(vec3(1.),solFarge(),0.5), skyggeMask());\n#include <colorspace_fragment>');
  m.needsUpdate=true; return m;
}
