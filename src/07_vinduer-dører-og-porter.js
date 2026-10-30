// ---- vinduer, dører og porter: plassering og størrelse fra Vegars kvartaltegninger (etter/42_fasader.py); alt tegnes her ----
const VIND_GEO=new THREE.PlaneGeometry(1,1); VIND_GEO.translate(0,0,0);
const vindMat=new THREE.ShaderMaterial({
  lights:true,
  uniforms:Object.assign({tHus:U_HUS}, THREE.UniformsUtils.clone(THREE.UniformsLib.lights)),
  vertexShader:GL_SOL_V+GL_HUS_V+`attribute vec4 aInfo; attribute vec3 aNorm; varying vec2 vUv; varying vec4 vInfo; varying vec2 vSz; varying vec3 vN;
    void main(){ vUv=uv; vInfo=aInfo; vSz=vec2(length(instanceMatrix[0].xyz),length(instanceMatrix[1].xyz));
      vN=normalize(mat3(modelMatrix)*aNorm);
      vec4 wp=modelMatrix*vec4(husPos((instanceMatrix*vec4(position,1.)).xyz),1.);
      gl_Position=projectionMatrix*viewMatrix*wp;`+glSolVMain('wp','vN')+`}`,
  fragmentShader:GL_SOL_F+`varying vec2 vUv; varying vec4 vInfo; varying vec2 vSz; varying vec3 vN;
    void main(){
      float typ=vInfo.x, bue=vInfo.y;
      vec2 m=vUv*vSz;
      float d=dot(normalize(mat3(viewMatrix)*vN),solRetning());   // kamerarom som husene (28.10)
      float lit=smoothstep(-0.12,0.52,d)*skyggeMask();
      vec3 sf=mix(vec3(1.),solFarge(),0.6*solHer(vWq));
      if(typ>2.5){ if(length(m-vSz*0.5)>vSz.x*0.5) discard; }   // oksøye: rundt vindu (typ 3)
      else if(typ>1.5 || (typ<0.5 && bue>0.5 && bue<1.5)){ float r=vSz.x*0.5; float cy=vSz.y-r; if(m.y>cy && length(vec2(m.x-r,m.y-cy))>r) discard; }   // buet topp: port (typ 2) og rundbuevindu (typ 0, bue 1; Tøihuset 30.10)
      float fw=max(fwidth(m.x),fwidth(m.y));
      float kant=min(min(m.x,vSz.x-m.x),min(m.y,vSz.y-m.y));
      if(typ>2.5) kant=vSz.x*0.5-length(m-vSz*0.5);
      else if(typ>1.5 || (typ<0.5 && bue>0.5 && bue<1.5)){ float r=vSz.x*0.5; float cy=vSz.y-r; if(m.y>cy) kant=min(kant, r-length(vec2(m.x-r,m.y-cy))); }
      vec3 hvit=mix(vec3(0.70,0.70,0.70)*KALD, vec3(0.96,0.94,0.90)*sf, lit);
      vec3 glas=mix(vec3(0.19,0.21,0.27), vec3(0.27,0.31,0.36), lit);
      vec3 c;
      if(typ<0.5 || typ>2.5){
        float ramme=0.08;
        // sprosser etter zoom (30.10): post og losholt (3,5 cm) og sprossene i nedre ramme (2 cm) holdes minst ~1 px brede
        // på nært hold og tones ut når én piksel blir for stor til å bære dem (fw = meter per piksel), så de ikke griser på avstand
        float lo=vSz.y*(typ>2.5?0.5:0.62);
        float pv=abs(m.x-vSz.x*0.5), ph=abs(m.y-lo);
        float qs=(typ<0.5 && vSz.y>1.0)?abs(m.y-lo*0.5):1e3;               // sprossen midt i nedre ramme: seks ruter
        // nærmeste zoom i kartet gir ~0,12–0,17 m per piksel på skjerm med pikseltetthet 1 (0,06–0,08 på mobil): korset (post og
        // losholt) står til 0,2 m/px og er borte ved 0,32; sprossen i nedre ramme bare der det er minst ~8 px per meter
        float bH=max(0.035,0.5*fw), bS=max(0.02,0.45*fw);                    // halv bredde: minst ~1 px
        float aH=1.-smoothstep(0.20,0.32,fw), aS=1.-smoothstep(0.075,0.13,fw);
        float spr=max(1.-smoothstep(bH-0.5*fw,bH+0.5*fw,pv),1.-smoothstep(bH-0.5*fw,bH+0.5*fw,ph))*aH;   // kanten midt på streken
        spr=max(spr,(1.-smoothstep(bS-0.5*fw,bS+0.5*fw,qs))*aS);
        float inn=smoothstep(ramme-0.5*fw,ramme+0.5*fw,kant);
        glas*=mix(1.,0.8,aS);                                                 // mørkere glass på nært hold: sprossene står ut
        c=mix(hvit, glas, inn); c=mix(c, hvit, spr*inn);
        c=mix(c, glas*1.4, smoothstep(0.25,-0.3,(m.x/vSz.x-0.5)+(m.y/vSz.y-0.5))*0.3*inn*(1.-spr));
      } else {
        vec3 dorf=mix(vec3(0.24,0.18,0.15), vec3(0.36,0.26,0.20)*sf, lit);
        if(typ>1.5) dorf=mix(vec3(0.14,0.13,0.13), vec3(0.22,0.20,0.19), lit);
        c=mix(hvit, dorf, smoothstep(0.07,0.07+fw,kant));
        c=mix(c, dorf*0.75, (1.-smoothstep(0.02,0.02+fw,abs(m.x-vSz.x*0.5)))*step(0.07,kant)*0.6);
        if(bue>1.5){   // grønn fløydør med overlys (bue=2, Kaserna etter ombyggingen)
          dorf=mix(vec3(0.10,0.17,0.13), vec3(0.19,0.30,0.23)*sf, lit);
          c=mix(hvit, dorf, smoothstep(0.07,0.07+fw,kant));
          c=mix(c, dorf*0.7, (1.-smoothstep(0.02,0.02+fw,abs(m.x-vSz.x*0.5)))*step(0.07,kant)*0.7);
          float ol=vSz.y-0.78; if(m.y>ol){ c=mix(glas, hvit, 1.-smoothstep(0.05,0.05+fw,min(kant,abs(m.y-ol)))); }
        }
      }
      c=mix(c, mix(glas,hvit,0.35), smoothstep(0.22,0.4,fw)*0.6);   // langt unna: vinduet blir en flate (etter sprossene)
      gl_FragColor=vec4(c,1.);
      #include <colorspace_fragment>
    }`
});
const _X=new THREE.Vector3(), _Y=new THREE.Vector3(0,1,0), _Z=new THREE.Vector3(), _M=new THREE.Matrix4();
// vinduer for ett bygg: instansmatriser + info. aBygg = byggindeks + 1 (0 = ikke et bygg), så løft og vekst leses fra hus-teksturen
function vindusData(V, i){
  const mats=[], info=new Float32Array(V.length*4), nrm=new Float32Array(V.length*3), bygg=new Float32Array(V.length).fill(i+1);
  V.forEach((v,k)=>{
    const [x,y,z,tx,ty,nx,ny,w,h,typ,bue,ant]=v;
    _X.set(-tx,0,ty); _Z.set(nx,0,-ny);   // høyrehendt basis (ellers snus trekantene og plata vises ikke)
    _M.makeBasis(_X.clone().multiplyScalar(w), _Y.clone().multiplyScalar(h), _Z);
    _M.setPosition(x+nx*0.05, z, -(y+ny*0.05));
    mats.push(_M.clone());
    info.set([typ,bue,ant,0],k*4); nrm.set([nx,0,-ny],k*3);
  });
  return {mats, info, nrm, bygg};
}
function lagVinduer(deler){
  const n=deler.reduce((a,d)=>a+d.mats.length,0);
  const im=new THREE.InstancedMesh(VIND_GEO.clone(), vindMat, n);
  const info=new Float32Array(n*4), nrm=new Float32Array(n*3), bygg=new Float32Array(n); let k=0;
  deler.forEach(d=>{ d.mats.forEach((m,j)=>{ im.setMatrixAt(k,m); info.set(d.info.subarray(j*4,j*4+4),k*4); nrm.set(d.nrm.subarray(j*3,j*3+3),k*3); bygg[k]=d.bygg[j]; k++; }); });
  im.geometry.setAttribute('aInfo',new THREE.InstancedBufferAttribute(info,4));
  im.geometry.setAttribute('aNorm',new THREE.InstancedBufferAttribute(nrm,3));
  im.geometry.setAttribute('aBygg',new THREE.InstancedBufferAttribute(bygg,1));
  im.frustumCulled=false; im.customDepthMaterial=husDybde;
  return im;
}
const PIPE_GEO=new THREE.BoxGeometry(0.9,3.4,0.75), KAPP_GEO=new THREE.BoxGeometry(1.08,0.2,0.92);
// utvider en takflate e meter i sitt eget plan (nabotak i en rekke overlapper, ingen lyse sprekker langs møner)
function utvidFlate(f,e){ const n=f.length; if(n<3) return f;
      let cx=0,cy=0; f.forEach(q=>{cx+=q[0]/n; cy+=q[1]/n;});
      // planet t = a*x + b*y + c fra de tre punktene som spenner størst trekant
      let best=null, A=0; for(let i=0;i<n;i++) for(let j=i+1;j<n;j++) for(let k=j+1;k<n;k++){ const p=f[i],q=f[j],r=f[k]; const ar=Math.abs((q[0]-p[0])*(r[1]-p[1])-(r[0]-p[0])*(q[1]-p[1])); if(ar>A){A=ar;best=[p,q,r];} if(n>12&&k>i+6) break; }
      if(!best||A<1e-6) return f; const [p,q,r]=best;
      const ux=q[0]-p[0],uy=q[1]-p[1],ut=q[2]-p[2], vx=r[0]-p[0],vy=r[1]-p[1],vt=r[2]-p[2];
      const nx=uy*vt-ut*vy, ny=ut*vx-ux*vt, nz=ux*vy-uy*vx; if(Math.abs(nz)<1e-9) return f;
      const pa=-nx/nz, pb=-ny/nz, pc=p[2]-pa*p[0]-pb*p[1];
      return f.map(v=>{ let dx=v[0]-cx, dy=v[1]-cy; const L=Math.hypot(dx,dy)||1; const x=v[0]+dx/L*e, y=v[1]+dy/L*e; return [x,y,Math.max(0,pa*x+pb*y+pc)]; }); }
// ---- samleren: alle vanlige hus slås sammen til ett nett per materiale (tegnekall: ett per materiale, ikke sju per hus).
// Spesielle bygg (kirka, bygg med deler, portbygg som 10_porter bygger om) beholdes som egne grupper.
const PORT_BYGG=new Set((DATA.porter||[]).map(p=>p.bygg));
const samler=new Map();            // materiale -> [geometrier]
const husDeler=new Map();          // byggindeks -> [{mesh, start, antall}] fylles når nettene er bygd (til peking)
const vinduSamling=[];             // vindusdata for alle vanlige hus -> ett instansert nett
const _mSamle=new THREE.Matrix4();
function samleMesh(mesh, matrise, i, topp){
  biterAv(mesh, matrise, []).forEach(([m,bit])=>{
    const k=bit.getAttribute('position').count;
    bit.setAttribute('aBygg', new THREE.BufferAttribute(new Float32Array(k).fill(i+1),1));
    bit.setAttribute('aTopp', new THREE.BufferAttribute(new Float32Array(k).fill(m===mesh.material?.[1] ? topp : 0),1));   // tegnede vinduer bare på sideveggene
    bit.userData.bygg=i;
    if(!samler.has(m)) samler.set(m,[]); samler.get(m).push(bit);
  });
}
function samleObjekt(obj, forelder, i, topp){   // mesh eller gruppe med barn; strek (LineSegments) hoppes over
  obj.updateMatrix(); _mSamle.multiplyMatrices(forelder, obj.matrix); const m=_mSamle.clone();
  if(obj.isMesh) samleMesh(obj, m, i, topp);
  obj.children.forEach(c=>samleObjekt(c, m, i, topp));
}
// polygon utvidet d meter utover (sokkel oppå veggen uten å flimre)
function utvidPoly(P,d){ let A=0; for(let k=0;k<P.length;k++){ const a=P[k],c=P[(k+1)%P.length]; A+=a[0]*c[1]-c[0]*a[1]; } const sg=A>0?1:-1;
  return P.map((q,k)=>{ const a=P[(k-1+P.length)%P.length], c=P[(k+1)%P.length];
    const n1=[(q[1]-a[1]),-(q[0]-a[0])], n2=[(c[1]-q[1]),-(c[0]-q[0])]; const l1=Math.hypot(...n1)||1, l2=Math.hypot(...n2)||1;
    const m=[(n1[0]/l1+n2[0]/l2)/2*sg,(n1[1]/l1+n2[1]/l2)/2*sg]; const lm=Math.hypot(...m)||1; const f=d/Math.max(lm,0.3);
    return [q[0]+m[0]/lm*f*lm, q[1]+m[1]/lm*f*lm]; }); }
function iPoly(p,f){ let inne=false; for(let k=0,j=f.length-1;k<f.length;j=k++){ const a=f[k],c=f[j]; if((a[1]>p[1])!==(c[1]>p[1]) && p[0]<(c[0]-a[0])*(p[1]-a[1])/(c[1]-a[1]+1e-12)+a[0]) inne=!inne; } return inne; }
function planZ(f,x,y){ const [a,b2,c]=f; const ux=b2[0]-a[0],uy=b2[1]-a[1],uz=b2[2]-a[2],vx=c[0]-a[0],vy=c[1]-a[1],vz=c[2]-a[2];
  const nx=uy*vz-uz*vy, ny=uz*vx-ux*vz, nz=ux*vy-uy*vx; if(Math.abs(nz)<1e-9) return a[2]; return a[2]-(nx*(x-a[0])+ny*(y-a[1]))/nz; }
DATA.bygg.forEach((b,i)=>{
  const pts=b.p; if(pts.length<3 || b.skjul) return;
  const spesiell = !!(b.kirke || (b.deler && b.deler.length) || PORT_BYGG.has(i));
  const dim=!b.gml;
  const wall = b.vegg || (dim? [214,210,198] : [238,230,214]);
  const roof = b.tak || (dim? [196,170,160] : [232,124,104]);
  const grp = new THREE.Group();
  const toppVindu = (b.vind&&b.vind.length)||b.gml ? 0 : Math.round(b.h*2)/2;
  const legg = spesiell ? (o=>grp.add(o)) : (o=>samleObjekt(o, new THREE.Matrix4(), i, toppVindu));
  const shape = polyShape(pts);
  (b.ph||[]).forEach(r=>{ if(r.length>2) shape.holes.push(new THREE.Path(r.map(V))); });
  const h = b.kirke ? 0.01 : b.h;   // kirka: formen tegnes av bygKirke (src/06); h og tak2 i data er silhuetten kontrolløren registrerer mot
  const eg = new THREE.ExtrudeGeometry(shape,{depth:h,bevelEnabled:false});
  eg.rotateX(-Math.PI/2);
  const walls = new THREE.Mesh(eg,[mat(roof,dim,b.taks),mat(wall,dim,b.veggs)]); // [tak/topp, sider]; tegnede vinduer styres av aTopp
  if(spesiell){ const k=eg.getAttribute('position').count; eg.setAttribute('aTopp', new THREE.BufferAttribute(new Float32Array(k).fill(toppVindu),1)); }   // egne grupper: tegnede vinduer via attributt, løft via gruppa (aBygg=0)
  walls.castShadow=true; walls.receiveShadow=true; legg(walls);
  // sokkel / natursteinsetasje i egen farge (29.10: tegningen og Street View viser «rød tegl over grå natursteinsetasje»)
  if(b.sokkel && b.sokkel.h>0.2 && !dim){
    const sg=new THREE.ExtrudeGeometry(polyShape(utvidPoly(pts,0.03)),{depth:Math.min(b.sokkel.h,h-0.05),bevelEnabled:false}); sg.rotateX(-Math.PI/2);
    const sm=new THREE.Mesh(sg,[mat(roof,dim,b.taks),mat(b.sokkel.farge,dim,b.sokkel.skygge)]); sm.receiveShadow=true; legg(sm);
  }
  // tak: én saltak-prisme per rektangel i bygget (L, T og U får riktige møner)
  if (b.tak2 && !b.kirke){
    // felles tak for husrekka (beregnet i etter/10_tak.py): flater + gavler/brannmurer
    const SLOPE=b.th||0.82; const pos=[];   // takhelning per hus (th) fra Kartverkets høydemodell der den er målt (24.10)
    b.tak2.forEach(f0=>{
      // hver takflate utvides 6 cm i sitt eget plan, så nabotak i en rekke overlapper og ingen lyse sprekker vises langs møner og grenser
      const f=utvidFlate(f0,0.06);
      const v2=f.map(q=>new THREE.Vector2(q[0],q[1])); const tri=THREE.ShapeUtils.triangulateShape(v2,[]);
      tri.forEach(t=>{ const P=t.map(k=>{const q=f[k]; return new THREE.Vector3(q[0], h+q[2]*SLOPE, -q[1]);}); const nrm=new THREE.Vector3().subVectors(P[1],P[0]).cross(new THREE.Vector3().subVectors(P[2],P[0])); if(nrm.y<0) P.reverse(); P.forEach(v=>pos.push(v.x,v.y,v.z)); });
    });
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.computeVertexNormals();
    const rm=new THREE.Mesh(g,mat(roof,dim,b.taks,{ds:true})); rm.castShadow=rm.receiveShadow=true; legg(rm);
    if (b.gavl2 && b.gavl2.length){
      const gp=[];
      b.gavl2.forEach(pl=>{ for(let k=0;k<pl.length-1;k++){ const a=pl[k], c=pl[k+1]; const za=h+a[2]*SLOPE, zc=h+c[2]*SLOPE;
        if(za-h<0.02 && zc-h<0.02) continue;
        gp.push(a[0],h,-a[1], c[0],h,-c[1], c[0],zc,-c[1],  a[0],h,-a[1], c[0],zc,-c[1], a[0],za,-a[1]); } });
      const gg=new THREE.BufferGeometry(); gg.setAttribute('position',new THREE.Float32BufferAttribute(gp,3)); gg.computeVertexNormals();
      const gm=new THREE.Mesh(gg,mat(wall,dim,b.veggs,{ds:true})); gm.castShadow=gm.receiveShadow=true; legg(gm);
    }
  } else if (b.sk && !b.flatt && !b.kirke){
    const SLOPE=b.th||0.82, CAP=7.5*(b.th||0.82)/0.82; const pos=[];
    b.sk.forEach(f=>{
      const v2=f.map(q=>new THREE.Vector2(q[0],q[1])); let tri=THREE.ShapeUtils.triangulateShape(v2,[]); if(tri.length<f.length-2){ tri=[]; for(let j=1;j<f.length-1;j++) tri.push([0,j,j+1]); }
      tri.forEach(t=>{ const P=t.map(k=>{const q=f[k]; return new THREE.Vector3(q[0], h+Math.min(q[2]*SLOPE,CAP), -q[1]);}); const nrm=new THREE.Vector3().subVectors(P[1],P[0]).cross(new THREE.Vector3().subVectors(P[2],P[0])); if(nrm.y<0) P.reverse(); P.forEach(v=>pos.push(v.x,v.y,v.z)); });
    });
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.computeVertexNormals();
    const rm=new THREE.Mesh(g,mat(roof,dim,b.taks,{ds:true})); rm.castShadow=rm.receiveShadow=true; legg(rm);
  }
  let rects = (b.sk||b.tak2||b.flatt||b.kirke) ? [] : (b.tk && b.tk.length) ? b.tk.filter((r,k)=>k===0 || Math.min(r[2],r[3])>=4.5).slice(0,3) : (b.rf>0.78 ? [[b.r[0],b.r[1],b.r[2],b.r[3],b.r[4]]] : []);
  rects.forEach(([rx,ry,rw,rh,ang])=>{
    const long=Math.max(rw,rh), short=Math.min(rw,rh);
    if (short<2.5 || short>24) return;
    const rise=Math.min(short*0.48,7.5)*(b.th||0.82)/0.82;
    const a = THREE.MathUtils.degToRad(ang) + (rw<rh? Math.PI/2:0);
    const L=long/2+0.25, S=short/2+0.35;
    const geo=new THREE.BufferGeometry();
    const v=[-L,0,-S, L,0,-S, L,0,S, -L,0,S, -L,rise,0, L,rise,0];
    geo.setAttribute('position',new THREE.Float32BufferAttribute(v,3)); geo.setIndex([0,1,5, 0,5,4, 3,4,5, 3,5,2, 0,4,3, 1,2,5]); geo.computeVertexNormals(); geo.addGroup(0,12,0); geo.addGroup(12,6,1);
    const rm=new THREE.Mesh(geo,[mat(roof,dim,b.taks,{ds:true}),mat(wall,dim,b.veggs,{ds:true})]); rm.castShadow=true; rm.receiveShadow=true;
    rm.position.set(rx,h,-ry); rm.rotation.y=a; legg(rm);
  });
  if (b.kirke) bygKirke(b.kirke, grp);
  // bygningsdeler (eldre vei)
  (b.kirke?[]:(b.deler||[])).forEach(dp=>{
    const sh=polyShape(dp.p); const mh=dp.mh||0; let top=dp.h, rh=0;
    if (dp.roof==='pyramidal'){ rh = (top-mh)<=6 ? (top-mh) : Math.min(5,(top-mh)*0.3); } else if (dp.roof==='gabled'){ rh=5; }
    const wallTop=top-rh;
    const white=[244,242,236], copper=[122,172,142], slate=[132,134,142];
    if (wallTop-mh>0.3){
      const eg=new THREE.ExtrudeGeometry(sh,{depth:wallTop-mh,bevelEnabled:false}); eg.rotateX(-Math.PI/2); eg.translate(0,mh,0);
      const m=new THREE.Mesh(eg,[mat(dp.tak||(dp.roof==='gabled'?slate:copper),false),mat(dp.vegg||white,false)]); m.castShadow=m.receiveShadow=true; grp.add(m);
    }
    if (dp.roof==='pyramidal'){
      const c=dp.p.reduce((a,q)=>[a[0]+q[0]/dp.p.length,a[1]+q[1]/dp.p.length],[0,0]);
      const pos=[], idx=[]; dp.p.forEach(q=>pos.push(q[0],wallTop,-q[1])); pos.push(c[0],top,-c[1]); const n=dp.p.length;
      for(let k=0;k<n;k++) idx.push(k,(k+1)%n,n);
      const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.setIndex(idx); g.computeVertexNormals();
      const m=new THREE.Mesh(g,new THREE.MeshLambertMaterial({color:new THREE.Color(dp.tak?`rgb(${dp.tak})`:'rgb(122,172,142)'),side:THREE.DoubleSide,flatShading:true})); m.castShadow=true; grp.add(m);
    } else if (dp.roof==='gabled'){
      const P2=dp.p; let best=0,ang=0; for(let k=0;k<P2.length;k++){const q=P2[k],w=P2[(k+1)%P2.length];const l=Math.hypot(w[0]-q[0],w[1]-q[1]); if(l>best){best=l;ang=Math.atan2(w[1]-q[1],w[0]-q[0]);}}
      // bredde = utstrekning vinkelrett på lengste kant
      const ca=Math.cos(ang), sa=Math.sin(ang); let mn=[1e9,1e9],mx=[-1e9,-1e9];
      P2.forEach(q=>{const u=q[0]*ca+q[1]*sa, v=-q[0]*sa+q[1]*ca; mn=[Math.min(mn[0],u),Math.min(mn[1],v)]; mx=[Math.max(mx[0],u),Math.max(mx[1],v)];});
      const L=(mx[0]-mn[0])/2, S=(mx[1]-mn[1])/2, cu=(mx[0]+mn[0])/2, cv=(mx[1]+mn[1])/2; const rise=rh;
      const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.Float32BufferAttribute([-L,0,-S, L,0,-S, L,0,S, -L,0,S, -L,rise,0, L,rise,0],3)); geo.setIndex([0,1,5, 0,5,4, 3,4,5, 3,5,2, 0,4,3, 1,2,5]); geo.computeVertexNormals();
      const m=new THREE.Mesh(geo,mat([132,134,142],false)); m.castShadow=true; m.position.set(cu*ca-cv*sa, wallTop-rise*0.0, -(cu*sa+cv*ca)); m.rotation.y=ang; m.position.y=wallTop; grp.add(m);
    }
  });
  // piper på mønet (posisjoner fra etter/40_detaljer_piper.py)
  if(b.piper && !dim){ b.piper.forEach(([x,y,z,ang])=>{
    const r=THREE.MathUtils.degToRad(ang);
    const pm=new THREE.Mesh(PIPE_GEO, mat([204,98,82],false,[150,76,64])); pm.position.set(x,z-0.3,-y); pm.rotation.y=r; pm.castShadow=true; legg(pm);
    const ck=new THREE.Mesh(KAPP_GEO, mat([74,68,66],false)); ck.position.set(x,z+1.48,-y); ck.rotation.y=r; legg(ck);
  }); }
  // takarker (antall og fordeling fra tegningene): front i veggfarge, saltak i takfarge
  if(b.arker && !dim) b.arker.forEach(([x,y,z,nx,ny,bw,hb])=>{
    const D=1.9, ang=Math.atan2(ny,nx);
    const g=new THREE.Group(); g.position.set(x,z-0.25,-y); g.rotation.y=ang;
    const kropp=new THREE.Mesh(new THREE.BoxGeometry(D,hb+0.25,bw), mat(wall,dim,b.veggs)); kropp.position.set(-D/2,(hb+0.25)/2,0); kropp.castShadow=true; g.add(kropp);
    const rr=bw*0.55; const tg=new THREE.BufferGeometry();
    const H=hb+0.25, r0=-bw/2-0.08, r1=bw/2+0.08, xf=0.12, xb=-D;
    tg.setAttribute('position',new THREE.Float32BufferAttribute([xf,H,r0, xf,H+rr,0, xb,H+rr,0,  xf,H,r0, xb,H+rr,0, xb,H,r0,  xf,H,r1, xb,H,r1, xb,H+rr,0,  xf,H,r1, xb,H+rr,0, xf,H+rr,0],3));
    tg.computeVertexNormals();
    const tk=new THREE.Mesh(tg, mat(roof,dim,b.taks,{ds:true})); tk.castShadow=true; g.add(tk);
    const gv=new THREE.BufferGeometry(); gv.setAttribute('position',new THREE.Float32BufferAttribute([0,H,-bw/2, 0,H,bw/2, 0,H+rr*0.98,0],3)); gv.computeVertexNormals();
    g.add(new THREE.Mesh(gv, mat(wall,dim,b.veggs,{ds:true})));
    legg(g);
  });
  // veggfelt: del av en vegg i egen farge (to fasader under ett omriss i kommunekartet, f.eks. teglgård + pussgård; 29.10)
  if(b.veggfelt && !dim){
    b.veggfelt.forEach(([x1,y1,x2,y2,r,g,bb])=>{
      const L=Math.hypot(x2-x1,y2-y1); if(L<0.3) return; let nx=(y2-y1)/L, ny=-(x2-x1)/L;
      if(iPoly([(x1+x2)/2+nx*0.2,(y1+y2)/2+ny*0.2],pts)){ nx=-nx; ny=-ny; }
      const o=0.025, A=[x1+nx*o,y1+ny*o], B=[x2+nx*o,y2+ny*o];
      const gg=new THREE.BufferGeometry(); gg.setAttribute('position',new THREE.Float32BufferAttribute([A[0],0,-A[1], B[0],0,-B[1], B[0],h,-B[1],  A[0],0,-A[1], B[0],h,-B[1], A[0],h,-A[1]],3));
      gg.computeVertexNormals(); legg(new THREE.Mesh(gg,mat([r,g,bb],dim,null,{ds:true})));
    });
  }
  // fasadesegmenter (30.10): én kropp etter DOM/Matrikkelen, men tegningen viser flere fasader på veggen. Hvert segment er en
  // veggflate i egen farge (fra_m–til_m langs veggen a→b); brannmurlinjen mellom to segmenter er en tynn mørk loddrett kant
  if(b.fasadesegmenter && !dim){
    const flate=(A,B,c)=>{ const gg=new THREE.BufferGeometry(); gg.setAttribute('position',new THREE.Float32BufferAttribute([A[0],0,-A[1], B[0],0,-B[1], B[0],h,-B[1],  A[0],0,-A[1], B[0],h,-B[1], A[0],h,-A[1]],3));
      gg.computeVertexNormals(); legg(new THREE.Mesh(gg,mat(c,dim,null,{ds:true}))); };
    b.fasadesegmenter.forEach(v=>{
      const [ax,ay]=v.a, [bx,by]=v.b, L=Math.hypot(bx-ax,by-ay); if(L<0.5) return;
      const ux=(bx-ax)/L, uy=(by-ay)/L;
      // omrissets kanter som ligger på segmentveggen (veggen a–b er rettet ut; omrisset kan ha små knekker langs den)
      const kanter=[];
      for(let k=0;k<pts.length;k++){ const p=pts[k], q=pts[(k+1)%pts.length], l=Math.hypot(q[0]-p[0],q[1]-p[1]); if(l<0.05) continue;
        if(Math.abs(((q[0]-p[0])*ux+(q[1]-p[1])*uy)/l)<0.97) continue;
        const d=pp=>Math.abs((pp[0]-ax)*uy-(pp[1]-ay)*ux); if(d(p)>0.6||d(q)>0.6) continue;
        let nx=(q[1]-p[1])/l, ny=-(q[0]-p[0])/l; if(iPoly([(p[0]+q[0])/2+nx*0.1,(p[1]+q[1])/2+ny*0.1],pts)){ nx=-nx; ny=-ny; }
        const s0=(p[0]-ax)*ux+(p[1]-ay)*uy, s1=(q[0]-ax)*ux+(q[1]-ay)*uy;
        kanter.push({p,q,s0,s1,nx,ny}); }
      const punkt=(K,s,o)=>{ const t=(s-K.s0)/(K.s1-K.s0); return [K.p[0]+(K.q[0]-K.p[0])*t+K.nx*o, K.p[1]+(K.q[1]-K.p[1])*t+K.ny*o]; };
      v.segmenter.forEach((sg,k)=>{
        kanter.forEach(K=>{ const lo=Math.max(sg.fra_m,Math.min(K.s0,K.s1)), hi=Math.min(sg.til_m,Math.max(K.s0,K.s1)); if(hi-lo<0.02) return;
          flate(punkt(K,lo,0.025),punkt(K,hi,0.025),sg.vegg); });
        if(k>0){ const c=v.segmenter[k-1].vegg, m=sg.fra_m;       // brannmurlinjen: 14 cm, mørk tone av de to fasadene
          const mork=[0,1,2].map(j=>Math.round(Math.min(c[j],sg.vegg[j])*0.42));
          const K=kanter.find(K=>m>=Math.min(K.s0,K.s1)-0.01 && m<=Math.max(K.s0,K.s1)+0.01);
          if(K){ const sn=Math.sign(K.s1-K.s0)||1; flate(punkt(K,m-0.07*sn,0.035),punkt(K,m+0.07*sn,0.035),mork); } }
      });
    });
  }
  // takvinduer: flate vinduer i takflaten (x, y, bredde, høyde langs fallet), som i kvartaltegningene (29.10)
  if(b.takvinduer && b.tak2 && !dim){ const S=b.th||0.82;
    b.takvinduer.forEach(([x,y,bw,bh])=>{
      const f=b.tak2.find(f=>iPoly([x,y],f)); if(!f) return;
      const W=f.slice(0,3).map(q=>new THREE.Vector3(q[0], h+q[2]*S, -q[1]));
      let nr=new THREE.Vector3().subVectors(W[1],W[0]).cross(new THREE.Vector3().subVectors(W[2],W[0])).normalize(); if(nr.y<0) nr.negate();
      if(nr.y>0.995) return;                                  // flatt tak: ingen takvindu
      const z=h+planZ(f,x,y)*S, P=new THREE.Vector3(x,z,-y);
      const oppF=new THREE.Vector3(0,1,0).sub(nr.clone().multiplyScalar(nr.y)).normalize(), tan=new THREE.Vector3().crossVectors(oppF,nr).normalize();
      [[bw+0.16,bh+0.16,0.03,[244,242,236]],[bw,bh,0.05,[52,58,68]]].forEach(([w2,h2,off,c])=>{
        const g=new THREE.PlaneGeometry(w2,h2); g.applyMatrix4(new THREE.Matrix4().makeBasis(tan,oppF,nr)); g.translate(P.x+nr.x*off,P.y+nr.y*off,P.z+nr.z*off);
        legg(new THREE.Mesh(g,mat(c,false))); });
    });
  }
  if(b.vind && b.vind.length && !dim){ const vd=vindusData(b.vind, spesiell?-1:i); if(spesiell) grp.add(lagVinduer([vd])); else vinduSamling.push(vd); }
  grp.userData={i, b, h, spesiell};
  if(spesiell){ flatGruppe(grp); city.add(grp); }
  buildings.push(grp);
});
// ---- nettene: ett per materiale, med byggindeks per punkt. Skyggekartet bruker husDybde, så løft og vekst følger med.
const husNett=[];
samler.forEach((biter, m)=>{
  const geo=mergeGeometries(biter, false); if(!geo) return;
  const mesh=new THREE.Mesh(geo, m); mesh.castShadow=mesh.receiveShadow=true; mesh.customDepthMaterial=husDybde; mesh.frustumCulled=false;
  city.add(mesh); husNett.push(mesh);
  let start=0; biter.forEach(bit=>{ const n=bit.getAttribute('position').count; if(!husDeler.has(bit.userData.bygg)) husDeler.set(bit.userData.bygg,[]); husDeler.get(bit.userData.bygg).push({mesh, start, antall:n}); start+=n; bit.dispose(); });
});
if(vinduSamling.length) city.add(lagVinduer(vinduSamling));
samler.clear();
// kontaktskygge rundt alle husføtter: ett nett for hele byen
{ const pos=[], alfa=[];
  DATA.bygg.forEach(b=>{ if(!b.p || b.p.length<3 || b.skjul) return; const f=fotBaand(b.p, 1.3, 0.04); pos.push(...f.pos); alfa.push(...f.alfa); });
  const g=new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3)); g.setAttribute('aAlfa', new THREE.Float32BufferAttribute(alfa,1));
  const m=new THREE.Mesh(g, kontaktMat); m.frustumCulled=false; m.renderOrder=1; city.add(m); }
