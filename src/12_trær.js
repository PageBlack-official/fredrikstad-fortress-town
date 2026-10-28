// ---- trær: posisjoner fra trykkfila; tegnet som i Messenger: stamme og greiner, krone av løvklaser med takket kant og 3 toner ----
let seed=11; const rnd=()=>{seed=(seed*16807)%2147483647; return seed/2147483647;};
// Kronene tegnes som løvklaser vendt mot kameraet: takket, buet silhuett og en kuleformet normal, så lys- og skyggetonene
// blir rene og myke som i Messenger. Dybden skrives som en kule, så klasene skjærer hverandre og blekkstreken følger dem.
// Alt er prosedyralt i shaderen (ingen tegnede omriss eller teksturer fra 2015-tegningene).
const KLASE=new THREE.SphereGeometry(1,14,10);   // glatte normaler: streken (blekkpasset) tegner silhuetten, ikke fasettene
const STAMME=new THREE.CylinderGeometry(0.55,1,1,7,1,true); STAMME.translate(0,0.5,0);
const SKYGGEKROPP=new THREE.IcosahedronGeometry(1,1);
const sunW=new THREE.Vector3(), tgtW=new THREE.Vector3(), camF=new THREE.Vector3();
const treU={ sunDir:{value:new THREE.Vector3(-0.5,0.7,0.5)} };   // stammene får solretningen herfra
// Kronene er geometri (kuler i klaser), tegnet med samme sol, skygge og strek som husene. De var tegnede skiver (billboards) med egen
// dybdeskriving og egen skyggeoppslag fram til 24.10; på iPhone forsvant de ved zoom og dra uten at noen av delene kunne pekes ut
// (?kroner=enkel/utendybde/utenskygge/nospeil ga samme feil). Vegar: «lås størrelsene og la dem zoomes som husene.»
function lovMatLag(){
  return new THREE.ShaderMaterial({
    lights:true,
    uniforms:THREE.UniformsUtils.merge([THREE.UniformsLib.lights,{ uStoy:{value:STIL.stoy} }]),
    vertexShader:GL_SOL_V+`varying vec3 vN; varying vec3 vCol;
      void main(){
        vec4 wp=modelMatrix*instanceMatrix*vec4(position,1.);
        vN=normalize(mat3(modelMatrix)*mat3(instanceMatrix)*normal);
        vCol=vec3(1.);
        #ifdef USE_INSTANCING_COLOR
        vCol=instanceColor;
        #endif
        gl_Position=projectionMatrix*viewMatrix*wp;`+glSolVMain('wp','vN')+`}`,
    fragmentShader:GL_SOL_F+`varying vec3 vN; varying vec3 vCol; uniform float uStoy;
      void main(){
        vec3 n=normalize(vN);
        float w=dot(normalize(mat3(viewMatrix)*n),solRetning())*0.5+0.5;   // solRetning() er i kamerarommet (three.js); normalen må dit, ellers dreier lyssiden med kameraet (28.10)
        w=mix(w, w*0.55, (1.-skyggeMask())*0.85);
        // tre toner som i tegningen: lys solside, grunnfarge, kjølig skyggeside
        float lys=smoothstep(0.60,0.64,w), mid=smoothstep(0.36,0.40,w);
        vec3 lysF=vCol*vec3(1.30,1.22,0.98)+vec3(0.04,0.045,0.0);
        vec3 mork=vCol*vec3(0.50,0.60,0.68);
        vec3 c=mix(mork, mix(vCol,lysF,lys), mid); c=mix(graavaer(c), c, solHer(vWq));
        gl_FragColor=vec4(c,1.);
        #include <colorspace_fragment>
      }`
  });
}
function stammeMatLag(){
  return new THREE.ShaderMaterial({
    lights:true,
    uniforms:THREE.UniformsUtils.merge([THREE.UniformsLib.lights,{ sunDir:{value:new THREE.Vector3()} }]),
    vertexShader:`#include <common>
      #include <shadowmap_pars_vertex>
      varying vec3 vN; varying vec3 vCol;
      void main(){
        #include <beginnormal_vertex>
        #include <defaultnormal_vertex>
        #include <begin_vertex>
        #include <project_vertex>
        #include <worldpos_vertex>
        #include <shadowmap_vertex>
        vN=normalize(mat3(modelMatrix)*mat3(instanceMatrix)*objectNormal);
        vCol=vec3(1.);
        #ifdef USE_INSTANCING_COLOR
        vCol=instanceColor;
        #endif
      }`,
    fragmentShader:`#include <common>
      #include <packing>
      #include <lights_pars_begin>
      #include <shadowmap_pars_fragment>
      #include <shadowmask_pars_fragment>
      uniform vec3 sunDir; varying vec3 vN; varying vec3 vCol;
      void main(){
        float w=dot(normalize(vN),sunDir)*0.5+0.5; w=mix(w,w*0.6,(1.-getShadowMask())*0.8);
        vec3 c=mix(vCol*0.62, vCol, smoothstep(0.50,0.53,w));
        gl_FragColor=vec4(c,1.);
        #include <colorspace_fragment>
      }`
  });
}
const lovMat=lovMatLag(), stammeMat=stammeMatLag();
stammeMat.uniforms.sunDir=treU.sunDir;
// usynlige kropper som bare kaster kroneskyggen (én per tre)
const skyggeMat=new THREE.MeshBasicMaterial({colorWrite:false, depthWrite:false});
// palett fra trykkfilas trær, med Messengers varmere lysgrønn
const GREENS=[[96,148,104],[86,140,98],[104,156,106],[90,136,104],[110,160,100],[80,130,96]].map(c=>new THREE.Color(`rgb(${c[0]},${c[1]},${c[2]})`));
const BARK=[[112,92,78],[100,84,74],[122,100,84]].map(c=>new THREE.Color(`rgb(${c[0]},${c[1]},${c[2]})`));
const TP = DATA.traer;
const klaseData=[], skyggeData=[], stammeData=[];
TP.forEach((p,i)=>{
  const s=p[2]?p[2]:2.6+rnd()*2.8; const g0=p[3]||0; const col=GREENS[(rnd()*GREENS.length)|0];
  const delay=0.6+1.6*((p[0]+p[1]+500)/1000);
  const x=p[0], z=-p[1];
  const kj=(k)=>col.clone().offsetHSL((rnd()-.5)*0.02,0,(rnd()-.5)*0.05+k);
  const legg=(liste,px,py,pz,r,sy,k)=>liste.push({pos:[px,py,pz],r,sy,rot:[rnd()*6.28,rnd()*6.28,rnd()*6.28],c:kj(k),delay});
  // hovedklase, sideklaser, toppklase
  legg(klaseData, x, g0+s*1.30, z, s*0.74, 0.92, 0);
  skyggeData.push({pos:[x,g0+s*1.35,z], r:s*0.95, sy:0.9, rot:[0,0,0], c:col, delay});
  const n=3+((rnd()*2)|0), a0=rnd()*6.28;
  for(let k=0;k<n;k++){ const a=a0+k*6.28/n+(rnd()-.5)*0.8, rr=s*(0.48+rnd()*0.18);
    legg(klaseData, x+Math.cos(a)*s*0.58, g0+s*(0.95+rnd()*0.55), z+Math.sin(a)*s*0.58, rr, 0.9, (rnd()-.5)*0.04); }
  legg(klaseData, x+(rnd()-.5)*s*0.3, g0+s*1.95, z+(rnd()-.5)*s*0.3, s*(0.42+rnd()*0.1), 0.88, 0.02);
  // små løvbiter som stikker ut
  for(let k=0;k<2;k++){ const a=rnd()*6.28; legg(klaseData, x+Math.cos(a)*s*1.0, g0+s*(0.8+rnd()*0.9), z+Math.sin(a)*s*1.0, s*(0.16+rnd()*0.08), 1.0, (rnd()-.5)*0.05); }
  // stamme og to greiner
  const bark=BARK[(rnd()*BARK.length)|0].clone().offsetHSL(0,0,(rnd()-.5)*0.04);
  const tr=0.22+s*0.05;
  stammeData.push({pos:[x,g0,z], r:tr, h:s*1.35, rx:0, rz:0, ry:0, c:bark, delay});
  for(let k=0;k<2;k++){ const a=a0+k*3.14+0.7; stammeData.push({pos:[x,g0+s*0.75,z], r:tr*0.45, h:s*0.75, rx:Math.sin(a)*0.75, rz:-Math.cos(a)*0.75, ry:0, c:bark, delay}); }
});
const trMesh=[];
function lagInst(geo,mat,data){ const m=new THREE.InstancedMesh(geo,mat,Math.max(1,data.length)); m.count=data.length; m.castShadow=true; m.receiveShadow=true; m.frustumCulled=false;
  data.forEach((d,i)=>m.setColorAt(i,d.c)); if(m.instanceColor) m.instanceColor.needsUpdate=true; m.userData.data=data; trMesh.push(m); scene.add(m); return m; }
const crowns=[lagInst(KLASE,lovMat,klaseData)]; crowns[0].receiveShadow=true; crowns[0].castShadow=false;
const skyggeKropper=lagInst(SKYGGEKROPP,skyggeMat,skyggeData); skyggeKropper.receiveShadow=false;
const stammer=lagInst(STAMME,stammeMat,stammeData); stammer.userData.stamme=true;
// kontaktskygge under hvert tre: en skive på bakken, alfa 1 i midten og 0 i kanten
{ const SKIVE=new THREE.CircleGeometry(1,20); SKIVE.rotateX(-Math.PI/2);
  const n=SKIVE.getAttribute('position').count, al=new Float32Array(n); const p=SKIVE.getAttribute('position');
  for(let i=0;i<n;i++) al[i]=1-Math.min(1, Math.hypot(p.getX(i),p.getZ(i)));
  SKIVE.setAttribute('aAlfa', new THREE.BufferAttribute(al,1));
  const skiver=new THREE.InstancedMesh(SKIVE, kontaktMat, Math.max(1,TP.length)); skiver.count=TP.length; skiver.frustumCulled=false; skiver.renderOrder=1;
  const d=new THREE.Object3D();
  TP.forEach((pt,i)=>{ const s=pt[2]||3.5, g0=pt[3]||0; d.position.set(pt[0], g0+0.04, -pt[1]); d.scale.setScalar(s*0.8); d.updateMatrix(); skiver.setMatrixAt(i,d.matrix); });
  scene.add(skiver); }
const dummy=new THREE.Object3D();
function setCrowns(t){
  trMesh.forEach(m=>{ const st=m.userData.stamme;
    m.userData.data.forEach((c,i)=>{ const k=t===null?1:THREE.MathUtils.clamp((t-c.delay)/0.7,0,1); const e=1-Math.pow(1-k,3);
      if(st){ dummy.position.set(c.pos[0],c.pos[1],c.pos[2]); dummy.rotation.set(c.rx,0,c.rz); dummy.scale.set(c.r*(0.3+0.7*e)+0.001, c.h*e+0.001, c.r*(0.3+0.7*e)+0.001); }
      else { const g0=c.pos[1]; dummy.position.set(c.pos[0], g0*e, c.pos[2]); dummy.rotation.set(c.rot[0],c.rot[1],c.rot[2]); dummy.scale.set(c.r*e+0.001, c.r*c.sy*e+0.001, c.r*e+0.001); }
      dummy.updateMatrix(); m.setMatrixAt(i,dummy.matrix); });
    m.instanceMatrix.needsUpdate=true; });
}
// solretningen hentes fra sola hver ramme, så trærne følger samme lys som byen
crowns[0].onBeforeRender=(r,sc_,c)=>{ sun.getWorldPosition(sunW); sun.target.getWorldPosition(tgtW); treU.sunDir.value.copy(sunW).sub(tgtW).normalize(); c.getWorldDirection(camF); };
setCrowns(0);
