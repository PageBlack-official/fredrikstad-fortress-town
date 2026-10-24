// ---- trær: posisjoner fra trykkfila; tegnet som i Messenger: stamme og greiner, krone av løvklaser med takket kant og 3 toner ----
let seed=11; const rnd=()=>{seed=(seed*16807)%2147483647; return seed/2147483647;};
// Kronene tegnes som løvklaser vendt mot kameraet: takket, buet silhuett og en kuleformet normal, så lys- og skyggetonene
// blir rene og myke som i Messenger. Dybden skrives som en kule, så klasene skjærer hverandre og blekkstreken følger dem.
// Alt er prosedyralt i shaderen (ingen tegnede omriss eller teksturer fra 2015-tegningene).
const KLASE=new THREE.PlaneGeometry(2,2);
const STAMME=new THREE.CylinderGeometry(0.55,1,1,7,1,true); STAMME.translate(0,0.5,0);
const SKYGGEKROPP=new THREE.IcosahedronGeometry(1,1);
const sunW=new THREE.Vector3(), tgtW=new THREE.Vector3(), camF=new THREE.Vector3();
const treU={ sunDir:{value:new THREE.Vector3(-0.5,0.7,0.5)}, camDir:{value:new THREE.Vector3(0,-1,0)}, invSpan:{value:1/8000} };
const NOISE_GLSL=`float h2(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
      float n2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+vec2(1,1)),f.x),f.y); }`;
function lovMatLag(){
  return new THREE.ShaderMaterial({
    lights:true,
    uniforms:THREE.UniformsUtils.merge([THREE.UniformsLib.lights,{ sunDir:{value:new THREE.Vector3()}, camDir:{value:new THREE.Vector3()}, invSpan:{value:1}, uStoy:{value:STIL.stoy} }]),
    vertexShader:`#include <common>
      #include <shadowmap_pars_vertex>
      uniform vec3 sunDir;
      varying vec2 vUv; varying vec3 vCol; varying float vSeed; varying float vRad;
      void main(){
        vec3 c=(modelMatrix*instanceMatrix*vec4(0.,0.,0.,1.)).xyz;
        float sx=length(instanceMatrix[0].xyz), sy=length(instanceMatrix[1].xyz);
        vec3 right=vec3(viewMatrix[0][0],viewMatrix[1][0],viewMatrix[2][0]);
        vec3 up=vec3(viewMatrix[0][1],viewMatrix[1][1],viewMatrix[2][1]);
        vec3 wp=c+right*position.x*sx+up*position.y*sy;
        vUv=position.xy; vRad=sx;
        vSeed=fract(sin(dot(c.xz,vec2(12.9898,78.233)))*43758.5453);
        vCol=vec3(1.);
        #ifdef USE_INSTANCING_COLOR
        vCol=instanceColor;
        #endif
        gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);
        // skyggeoppslag fra klasens solside, så klasen ikke skygger seg selv
        vec4 worldPosition=vec4(wp+normalize(sunDir)*sx*1.05,1.);
        vec3 transformedNormal=vec3(0.,0.,1.);
        #include <shadowmap_vertex>
      }`,
    fragmentShader:`#include <common>
      #include <packing>
      #include <lights_pars_begin>
      #include <shadowmap_pars_fragment>
      #include <shadowmask_pars_fragment>
      uniform vec3 sunDir; uniform float invSpan, uStoy;
      varying vec2 vUv; varying vec3 vCol; varying float vSeed; varying float vRad;
      ${NOISE_GLSL}
      void main(){
        float r=length(vUv), th=atan(vUv.y,vUv.x);
        // buet, takket løvsilhuett: 8-12 buer, ujevne, med små løvtagger
        float k=8.+floor(vSeed*5.);
        float sc=0.80+0.13*pow(abs(sin(th*k*0.5+vSeed*31.)),0.55);
        sc+=(n2(vec2(th*3.2+vSeed*17.,vSeed*9.))-0.5)*0.12;
        sc+=(n2(vec2(th*26.+vSeed*7.,3.))-0.5)*0.05;
        if(r>sc) discard;
        // glatt kule (uavhengig av buene i kanten), så verken tonene eller dybden får stråler
        float rr=min(r/0.97,1.), z=sqrt(max(0.,1.-rr*rr));
        // svake buler i normalen gjør tonegrensene organiske
        vec2 b=vec2(n2(vUv*2.2+vSeed*13.),n2(vUv*2.2+vSeed*13.+5.3))-0.5;
        vec3 nV=normalize(vec3(vUv/0.97+b*0.6*uStoy, z+0.08));
        vec3 sV=normalize((viewMatrix*vec4(sunDir,0.)).xyz);
        float sm=${Q0.get('kroner')==='enkel' ? '1.0' : 'getShadowMask()'};   // ?kroner=enkel: feilsøking på mobil, uten dybdeskriving og skyggeoppslag
        float w=dot(nV,sV)*0.5+0.5;
        w=mix(w, w*0.55, (1.-sm)*0.85);
        float lys=smoothstep(0.60,0.62,w), mid=smoothstep(0.38,0.40,w);
        vec3 lysF=vCol*vec3(1.30,1.22,0.98)+vec3(0.04,0.045,0.0);
        vec3 mork=vCol*vec3(0.50,0.60,0.68);
        vec3 c=mix(mork, mix(vCol,lysF,lys), mid);
        // malte lyse flekker på solsiden, mørke løvmerker i skyggen
        float p=n2(vUv*1.7+vSeed*21.);
        c=mix(c, lysF*1.08+vec3(0.03,0.035,0.0), smoothstep(0.68,0.70,p)*lys*0.9*uStoy);
        float q=n2(vUv*6.5+vSeed*3.);
        c=mix(c, mork*0.82, smoothstep(0.80,0.82,q)*(1.-lys)*0.9*uStoy);
        gl_FragColor=vec4(c,1.);
        #include <colorspace_fragment>
        ${Q0.get('kroner')==='enkel' ? '' : 'gl_FragDepth=gl_FragCoord.z - z*vRad*invSpan;'}
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
lovMat.uniforms.sunDir=treU.sunDir; lovMat.uniforms.camDir=treU.camDir; lovMat.uniforms.invSpan=treU.invSpan; stammeMat.uniforms.sunDir=treU.sunDir;
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
crowns[0].onBeforeRender=(r,sc_,c)=>{ sun.getWorldPosition(sunW); sun.target.getWorldPosition(tgtW); treU.sunDir.value.copy(sunW).sub(tgtW).normalize(); c.getWorldDirection(camF); treU.camDir.value.copy(camF); if(c.isOrthographicCamera) treU.invSpan.value=1/(c.far-c.near); };
setCrowns(0);
