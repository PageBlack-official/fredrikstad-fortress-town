import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { registrer } from './tilstand.js';
import { cam, scene } from './00_oppsett.js';
import { waterLayer } from './03_bakke-vann-grønt.js';
// ---- flyt uten lavere oppløsning (Vegar: «ikke dårligere oppløsning, heller motsatt») ----
// To ting som sparer arbeid per bilde uten å endre bildet:
// 1) Vannet i bildet: et grovt rutenett over vannflatene (8 m), så tegneløkka vet om vann er i bildet. Står kartet stille uten vann i bildet,
//    tegnes ingenting (før: 10 hele bilder i sekundet for at vannet skulle leve), og speilpasset hoppes over når vannet ikke synes.
// 2) Bakkeflatene (plener, flater, parkering, vann, brostein) var ett nett per polygon: 600+ tegnekall i hvert bilde og i speilet.
//    Nett med samme materiale og samme plass slås sammen til ett, så tegnekallene blir få. Rekkefølgen mellom materialene er den samme
//    (three.js sorterer på materiale før avstand), så ingenting bytter plass i dybden.
const vannRute=(()=>{
  const C=8; let x0=1e9, z0=1e9, x1=-1e9, z1=-1e9; const tri=[];
  const _a=new THREE.Vector3();
  waterLayer.forEach(m=>{ m.updateMatrixWorld(); const P=m.geometry.attributes.position, I=m.geometry.index, n=I?I.count:P.count;
    const pk=[]; for(let i=0;i<P.count;i++){ _a.fromBufferAttribute(P,i).applyMatrix4(m.matrixWorld); pk.push(_a.x,_a.z); x0=Math.min(x0,_a.x); x1=Math.max(x1,_a.x); z0=Math.min(z0,_a.z); z1=Math.max(z1,_a.z); }
    for(let k=0;k<n;k+=3){ const a=I?I.getX(k):k, b=I?I.getX(k+1):k+1, c=I?I.getX(k+2):k+2; tri.push(pk[2*a],pk[2*a+1],pk[2*b],pk[2*b+1],pk[2*c],pk[2*c+1]); } });
  if(!tri.length) return {har:()=>false};
  x0-=C; z0-=C; const nx=Math.ceil((x1-x0)/C)+2, nz=Math.ceil((z1-z0)/C)+2, g=new Uint8Array(nx*nz);
  // hver trekant merker rutene den dekker (sjekket i rutens hjørner og midte, pluss én rute rundt: heller for mye vann enn for lite)
  const inni=(px,pz,t)=>{ const [ax,az,bx,bz,cx,cz]=t, d1=(px-bx)*(az-bz)-(ax-bx)*(pz-bz), d2=(px-cx)*(bz-cz)-(bx-cx)*(pz-cz), d3=(px-ax)*(cz-az)-(cx-ax)*(pz-az);
    return !((d1<0||d2<0||d3<0) && (d1>0||d2>0||d3>0)); };
  for(let k=0;k<tri.length;k+=6){ const t=tri.slice(k,k+6);
    const i0=Math.floor((Math.min(t[0],t[2],t[4])-x0)/C), i1=Math.floor((Math.max(t[0],t[2],t[4])-x0)/C), j0=Math.floor((Math.min(t[1],t[3],t[5])-z0)/C), j1=Math.floor((Math.max(t[1],t[3],t[5])-z0)/C);
    for(let j=j0;j<=j1;j++) for(let i=i0;i<=i1;i++){ if(g[j*nx+i]) continue; const cx=x0+i*C, cz=z0+j*C;
      if(inni(cx+C/2,cz+C/2,t)||inni(cx,cz,t)||inni(cx+C,cz,t)||inni(cx,cz+C,t)||inni(cx+C,cz+C,t)||(t[0]>=cx&&t[0]<cx+C&&t[1]>=cz&&t[1]<cz+C)) g[j*nx+i]=1; } }
  const h=new Uint8Array(g); for(let j=1;j<nz-1;j++) for(let i=1;i<nx-1;i++) if(g[j*nx+i]) for(let dj=-1;dj<=1;dj++) for(let di=-1;di<=1;di++) h[(j+dj)*nx+i+di]=1;
  return { har:(x,z)=>{ const i=Math.floor((x-x0)/C), j=Math.floor((z-z0)/C); return i>=0&&j>=0&&i<nx&&j<nz&&h[j*nx+i]===1; } };
})();
// vann i bildet: 32 x 20 skjermpunkter legges ned på vannflaten (y 0,15); regnes på nytt bare når kameraet har flyttet seg
const _vannKam=new THREE.Matrix4(), _vp=new THREE.Vector3(), _vq=new THREE.Vector3(); let _vannSist=true, _vannKjent=false;
function vannISyne(){
  if(_vannKjent && _vannKam.equals(cam.projectionMatrix)) return _vannSist;
  _vannKam.copy(cam.projectionMatrix); _vannKjent=true; let ja=false;
  for(let j=0;j<=20 && !ja;j++) for(let i=0;i<=32;i++){ const x=i/16-1, y=1-j/10;
    _vp.set(x,y,-1).unproject(cam); _vq.set(x,y,1).unproject(cam); const dy=_vq.y-_vp.y; if(Math.abs(dy)<1e-9) continue;
    const t=(0.15-_vp.y)/dy; if(t<0||t>1) continue;
    if(vannRute.har(_vp.x+(_vq.x-_vp.x)*t, _vp.z+(_vq.z-_vp.z)*t)){ ja=true; break; } }
  _vannSist=ja; return ja;
}
// bakkeflatene slås sammen: bare nett rett under scenen, uten barn, utenfor speilet (lag 1), med samme materiale, plass og skyggevalg
const flaterSammen=(()=>{
  const grupper=new Map(); const ut=[];
  scene.children.forEach(o=>{
    if(!o.isMesh || o.isInstancedMesh || o.children.length || o.layers.mask!==1 || Array.isArray(o.material) || !o.visible || o.onBeforeRender!==THREE.Object3D.prototype.onBeforeRender || Object.keys(o.userData).length) return;
    const g=o.geometry; if(!g.isBufferGeometry || g.morphAttributes.position) return;
    o.updateMatrix();
    const k=[o.material.uuid, o.matrix.elements.join(','), o.castShadow, o.receiveShadow, o.renderOrder, o.frustumCulled, o.customDepthMaterial?o.customDepthMaterial.uuid:'', !!g.index, Object.keys(g.attributes).sort().join('+')].join('|');
    if(!grupper.has(k)) grupper.set(k,[]); grupper.get(k).push(o); });
  let for_=0, etter=0;
  grupper.forEach(liste=>{ for_+=liste.length; if(liste.length<2){ etter+=liste.length; return; }
    const geo=mergeGeometries(liste.map(o=>o.geometry), false); if(!geo){ etter+=liste.length; return; }
    const f=liste[0], m=new THREE.Mesh(geo, f.material);
    m.position.copy(f.position); m.quaternion.copy(f.quaternion); m.scale.copy(f.scale); m.castShadow=f.castShadow; m.receiveShadow=f.receiveShadow; m.renderOrder=f.renderOrder;
    m.frustumCulled=f.frustumCulled; if(f.customDepthMaterial) m.customDepthMaterial=f.customDepthMaterial;
    liste.forEach(o=>{ scene.remove(o); o.geometry.dispose(); }); scene.add(m); ut.push(m); etter++; });
  return {for:for_, etter};
})();
window.__flytInfo=()=>({flaterFor:flaterSammen.for, flaterEtter:flaterSammen.etter, vann:vannISyne()});
registrer({ vannISyne: () => vannISyne });   // brukes av tidligere moduler via SENERE (tilstand.js)
