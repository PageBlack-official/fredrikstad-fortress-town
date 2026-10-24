// ---- bygg ----
const city = new THREE.Group(); scene.add(city);
const edgeMat = new THREE.LineBasicMaterial({color:INK, transparent:true, opacity:.4}); edgeMat.visible=false; // blekkstreken tegnes i etterbehandlingen
const mats = new Map();
// ---- hustilstand i en tekstur: hvert bygg har løft (r) og vekst (g) i én texel, lest i vertex-shaderen. Slik kan alle hus med samme
// materiale tegnes som ett nett (under 50 tegnekall i stedet for 3 300) og likevel løfte seg og vokse hver for seg. Texel 0 er «ikke et bygg».
const HUS_N=512, husData=new Float32Array(HUS_N*4);
for(let i=0;i<HUS_N;i++){ husData[i*4]=0; husData[i*4+1]=1; husData[i*4+2]=0; husData[i*4+3]=1; }
const tHus=new THREE.DataTexture(husData, HUS_N, 1, THREE.RGBAFormat, THREE.FloatType); tHus.minFilter=tHus.magFilter=THREE.NearestFilter; tHus.needsUpdate=true;
const U_HUS={value:tHus};
function settHus(i, loft, vekst){ const k=(i+1)*4; if(husData[k]!==loft || husData[k+1]!==vekst){ husData[k]=loft; husData[k+1]=vekst; tHus.needsUpdate=true; } }
// GLSL som alle husmaterialer deler: aBygg (bygg + 1, 0 = ikke et bygg) peker på texelen; aTopp er hushøyden der veggen skal få tegnede vinduer
const GL_HUS_V=`attribute float aBygg; attribute float aTopp; uniform sampler2D tHus;
  vec3 husPos(vec3 p){ vec4 h=texture2D(tHus, vec2((aBygg+0.5)/${HUS_N}., 0.5)); p.y=p.y*h.g+h.r; return p; }`;
// skyggekartet må løfte og vokse husene likt: ett dybdemateriale for alle sammenslåtte nett
const husDybde=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});
husDybde.onBeforeCompile=sh=>{ sh.uniforms.tHus=U_HUS;
  // løft og vekst legges på etter instansmatrisen (vinduene er instanser), i byens rom; byen (city) står i origo
  sh.vertexShader=sh.vertexShader.replace('#include <common>', '#include <common>\n'+GL_HUS_V).replace('#include <project_vertex>',
    'vec4 mvPosition=vec4(transformed,1.0);\n#ifdef USE_INSTANCING\nmvPosition=instanceMatrix*mvPosition;\n#endif\nmvPosition.xyz=husPos(mvPosition.xyz); mvPosition=modelViewMatrix*mvPosition; gl_Position=projectionMatrix*mvPosition;'); };
// ---- sammenslåing: en gruppe av mange små nett (kirka, broer, murer, bygg med deler) blir ett nett per materiale.
// Gruppa beholdes (den flyttes ved løft), strek-objektene (EdgesGeometry, usynlige) kastes, instanserte nett (vinduer) står urørt.
// Attributtene aBygg/aTopp følger med der de finnes (0 ellers), uv kastes (ingen av stoffene bruker den).
const _mFlat=new THREE.Matrix4();
function bitAv(geo, start, antall, ekstra){
  const ut=new THREE.BufferGeometry(), n=antall;
  for(const navn of ['position','normal']){ const a=geo.getAttribute(navn); ut.setAttribute(navn, new THREE.BufferAttribute(a.array.slice(start*a.itemSize,(start+n)*a.itemSize), a.itemSize)); }
  ekstra.forEach(navn=>{ const a=geo.getAttribute(navn); ut.setAttribute(navn, new THREE.BufferAttribute(a ? a.array.slice(start,start+n) : new Float32Array(n), 1)); });
  return ut;
}
function biterAv(mesh, matrise, ekstra){   // [materiale, geometri] per materialgruppe, i gitt koordinatsystem
  let geo=mesh.geometry.index ? mesh.geometry.toNonIndexed() : mesh.geometry;
  if(!geo.getAttribute('normal')) geo.computeVertexNormals();
  const n=geo.getAttribute('position').count;
  const grupper = Array.isArray(mesh.material) && geo.groups.length ? geo.groups.map(g=>[mesh.material[g.materialIndex], g.start, Math.min(g.count, n-g.start)]) : [[Array.isArray(mesh.material)?mesh.material[0]:mesh.material, 0, n]];
  return grupper.map(([m,start,antall])=>[m, bitAv(geo,start,antall,ekstra).applyMatrix4(matrise)]);
}
function flatGruppe(grp, ekstra=['aBygg','aTopp']){
  const samling=new Map(), vekk=[];
  (function gaa(o, forelder){ o.children.forEach(c=>{ c.updateMatrix(); const m=_mFlat.multiplyMatrices(forelder, c.matrix).clone();
    if(c.isLine){ vekk.push(c); return; }
    if(c.isMesh && !c.isInstancedMesh && c.geometry){ biterAv(c, m, ekstra).forEach(([mt,g])=>{ if(!samling.has(mt)) samling.set(mt,{biter:[], cs:false, rs:false}); const s=samling.get(mt); s.biter.push(g); s.cs=s.cs||c.castShadow; s.rs=s.rs||c.receiveShadow; }); vekk.push(c); }
    gaa(c, m); }); })(grp, new THREE.Matrix4());
  vekk.forEach(o=>o.removeFromParent());
  samling.forEach((s,mt)=>{ const geo=mergeGeometries(s.biter,false); if(!geo) return; s.biter.forEach(b=>b.dispose()); const mesh=new THREE.Mesh(geo,mt); mesh.castShadow=s.cs; mesh.receiveShadow=s.rs; mesh.customDepthMaterial=husDybde; grp.add(mesh); });
  grp.children.filter(c=>c.isGroup && !c.children.length).forEach(c=>c.removeFromParent());
  return grp;
}
// ---- kontaktskygge (lys-og-bevegelse pkt. 1, 24.10): et mykt mørke på bakken der hus og trær står, i tillegg til kastskyggen.
// Geometri på bakken (ikke skjermeffekt): et bånd rundt hver husfot og en skive under hvert tre, med alfa 1 inne og 0 ute,
// multiplisert inn i bakken. Stabilt i fart, ingen prikking, skalerer som husene. Styrken er KONTAKT_STYRKE, bredden settes der båndene lages.
const KONTAKT_STYRKE = Q0.get('kontakt')==='0' ? 0 : 0.42;
const kontaktMat=new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, blending:THREE.MultiplyBlending, polygonOffset:true, polygonOffsetFactor:-2, polygonOffsetUnits:-2,
  uniforms:{ styrke:{value:KONTAKT_STYRKE} },
  vertexShader:`attribute float aAlfa; varying float vA; void main(){ vA=aAlfa; vec4 p=vec4(position,1.);
    #ifdef USE_INSTANCING
    p=instanceMatrix*p;
    #endif
    gl_Position=projectionMatrix*modelViewMatrix*p; }`,
  fragmentShader:`uniform float styrke; varying float vA; void main(){ float a=vA*vA*(3.-2.*vA)*styrke; gl_FragColor=vec4(mix(vec3(1.), vec3(0.62,0.66,0.78), a), 1.); }`
});
// bånd rundt et polygon (modellkoordinater x,y → verden x,-y), bredde d meter; returnerer posisjoner og alfa
function fotBaand(pts, d, y){
  const n=pts.length; let areal=0; for(let i=0;i<n;i++){ const a=pts[i], c=pts[(i+1)%n]; areal+=a[0]*c[1]-c[0]*a[1]; }
  const ut=areal>0 ? 1 : -1;                        // orientering avgjør hvilken side som er ut
  const pos=[], alfa=[], nrm=[];
  for(let i=0;i<n;i++){ const a=pts[i], c=pts[(i+1)%n]; const ex=c[0]-a[0], ey=c[1]-a[1], L=Math.hypot(ex,ey)||1; nrm.push([ -ey/L*ut, ex/L*ut ]); }
  const P=(x,yy,al)=>{ pos.push(x,y,-yy); alfa.push(al); };
  for(let i=0;i<n;i++){ const a=pts[i], c=pts[(i+1)%n], m=nrm[i];
    const a2=[a[0]+m[0]*d, a[1]+m[1]*d], c2=[c[0]+m[0]*d, c[1]+m[1]*d];
    P(a[0],a[1],1); P(c[0],c[1],1); P(c2[0],c2[1],0);  P(a[0],a[1],1); P(c2[0],c2[1],0); P(a2[0],a2[1],0);
    // hjørnevifte mellom dette og neste bånd (bare utvendige hjørner)
    const m2=nrm[(i+1)%n]; const kryss=(m[0]*m2[1]-m[1]*m2[0])*ut;
    if(kryss>1e-6){ P(c[0],c[1],1); P(c[0]+m[0]*d,c[1]+m[1]*d,0); P(c[0]+m2[0]*d,c[1]+m2[1]*d,0); }
    else if(kryss<-1e-6){ P(c[0],c[1],1); P(c[0]+m2[0]*d,c[1]+m2[1]*d,0); P(c[0]+m[0]*d,c[1]+m[1]*d,0); }
  }
  return {pos, alfa};
}
// to toner som i tegningen: flater som vender mot sola (alltid øverst til venstre i bildet) får full farge, resten skyggetonen
function mat(rgb, dim, sk, opt={}){
  const key = rgb.join(',')+(dim?'d':'')+(sk?'s'+sk.join(','):'')+(opt.ds?'D':'');
  if(!mats.has(key)){
    const c=new THREE.Color(`rgb(${rgb[0]},${rgb[1]},${rgb[2]})`); if(dim) c.lerp(new THREE.Color(0xe4e2d8),.8);
    // skyggetonen hentes fra trykkfila når bygget har en; ellers samme forhold som tegningen bruker
    let s; if(sk && !dim){ s=new THREE.Color(`rgb(${sk[0]},${sk[1]},${sk[2]})`); } else { s=c.clone(); s.r*=0.72; s.g*=0.80; s.b*=0.80; }
    const m=new THREE.ShaderMaterial({
      lights:true,
      uniforms:Object.assign({ farge:{value:c}, skygge:{value:s}, tHus:U_HUS, uVask:{value:STIL.vask}, skravur:U_SKRAVUR }, THREE.UniformsUtils.clone(THREE.UniformsLib.lights)),
      vertexShader:GL_SOL_V+GL_HUS_V+`varying vec3 vp; varying vec3 lp; varying vec3 wq; varying float topp; void main(){ topp=aTopp; vec3 pos=husPos(position); lp=pos; vec4 wp=modelMatrix*vec4(pos,1.); wq=wp.xyz; vec4 mv=viewMatrix*wp; vp=mv.xyz; gl_Position=projectionMatrix*mv;
        vec3 wn=normalize(mat3(modelMatrix)*normal+vec3(0.,1e-5,0.));`+glSolVMain('wp','wn')+`}`,
      fragmentShader:GL_SOL_F+`uniform mat3 normalMatrix; uniform vec3 farge, skygge; uniform float uVask; varying float topp; varying vec3 vp; varying vec3 lp; varying vec3 wq;
        float hh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
        float nn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hh(i),hh(i+vec2(1,0)),f.x),mix(hh(i+vec2(0,1)),hh(i+vec2(1,1)),f.x),f.y);}
        void main(){ vec3 n=normalize(normalMatrix*cross(dFdx(lp),dFdy(lp))); float d=dot(n,solRetning()); // normal fra lokale koordinater: presist, ingen stripete skygge
          // tegningens to toner (lys- og skyggetonen fra trykkfila) blandes av ekte lys: Lambert mot sola og kastskygger, myk overgang
          float lam=smoothstep(-0.12,0.52,d);
          float lit=lam*skyggeMask();
          float k=1.-lit;
          vec3 c = mix(skygge*KALD, farge*mix(vec3(1.),solFarge(),0.6), lit);
          // ---- malte flater: akvarellvask og penselstrøk, forankret i byen (ikke skjermen) ----
          vec3 nq=normalize(cross(dFdx(lp),dFdy(lp)));
          float vask=nn(wq.xz*0.045+wq.y*0.031)*0.62+nn(wq.xz*0.17+vec2(wq.y*0.23,3.1))*0.38;
          c*=1.-0.28*skravurMaske(wq, k);
          c*=1.+(vask-0.5)*0.09*uVask;   // akvarellvask, av i stil a/b
          float fwq=max(fwidth(wq.x)+fwidth(wq.z)+fwidth(wq.y),1e-4);
          float naerhet=1.-smoothstep(0.12,0.45,fwq);   // detaljer forsvinner på avstand
          if(abs(nq.y)<0.3){
            // vegg: vannrette penselstrøk
            vec2 tq=normalize(vec2(-nq.z,nq.x)); float uq=dot(wq.xz,tq);
            float strok=nn(vec2(uq*0.7, wq.y*6.0))*0.7+nn(vec2(uq*2.1, wq.y*15.))*0.3;
            c*=1.+(strok-0.5)*0.05*naerhet*uVask;
          } else if(abs(nq.y)<0.985){
            // tak: rader med takstein langs fallet, antydet, borte på avstand
            vec2 ned=normalize(nq.xz); vec2 lang=vec2(-ned.y,ned.x);
            float sF=dot(lp.xz,ned)/max(abs(nq.y),0.2)/0.38; float rF=dot(lp.xz,lang)/0.30;
            float rad=floor(sF); float fr=fract(sF);
            float fws=max(fwidth(sF),1e-4);
            float rLinje=1.-smoothstep(0.,fws*1.4,fr);
            float sk=fract(rF+0.5*mod(rad,2.)); float fwr=max(fwidth(rF),1e-4);
            float sLinje=(1.-smoothstep(0.,fwr*1.2,sk))*0.45;
            float vis=(1.-smoothstep(0.22,0.55,max(fws,fwr)))*naerhet;
            c*=1.-0.11*max(rLinje,sLinje)*vis; c*=1.-0.055*(1.-fr)*vis;
            c*=1.+(hh(vec2(floor(rF+0.5*mod(rad,2.)),rad))-0.5)*0.06*vis;
            // strøk langs fallet
            c*=1.+(nn(vec2(dot(wq.xz,lang)*1.3, dot(wq.xz,ned)*0.25))-0.5)*0.05;
          }
          if(topp>0.){
            vec3 nl=normalize(cross(dFdx(lp),dFdy(lp)));
            if(abs(nl.y)<0.3){
              vec2 t=normalize(vec2(-nl.z,nl.x)); float u=dot(lp.xz,t);
              float rad=floor(lp.y/3.0); float fy=lp.y-rad*3.0; float fu=mod(u,2.6);
              vec2 q=vec2(fu-1.3, fy-1.55); vec2 dd=abs(q)-vec2(0.42,0.68); float inn=max(dd.x,dd.y);
              float fw=max(fwidth(u),fwidth(lp.y));
              float ok = step(rad*3.0+2.35, topp-0.25);
              float ramme=(1.-smoothstep(0.,fw,inn))*ok;
              float glass=(1.-smoothstep(-0.08,-0.08+fw,inn))*ok;
              float post=(1.-smoothstep(0.03,0.03+fw,abs(q.x)))*(1.-smoothstep(0.03,0.03+fw,abs(q.y-0.18)));
              float kryss=max(1.-smoothstep(0.03,0.03+fw,abs(q.x)), 1.-smoothstep(0.03,0.03+fw,abs(q.y-0.18)));
              vec3 hvit=vec3(0.96,0.94,0.90)*mix(1.,0.74,k);
              vec3 glas=mix(vec3(0.27,0.31,0.36),vec3(0.20,0.22,0.27),k);
              glas=mix(glas, glas*1.35, smoothstep(0.2,-0.4,q.x+q.y*0.5)*0.6);
              vec3 w=mix(hvit, glas, glass*(1.-kryss));
              float fjern=smoothstep(0.12,0.3,fw);
              // dør på gateplan i annenhver fjerde akse, som i tegningen
              float akse=floor(u/2.6);
              float dor = (rad<0.5 && mod(akse,4.)==1. && topp>3.2) ? 1. : 0.;
              vec2 qd=vec2(fu-1.3, fy-1.15); vec2 ddd=abs(qd)-vec2(0.55,1.15); float innd=max(ddd.x,ddd.y);
              float dramme=(1.-smoothstep(0.,fw,innd))*dor; float dfyll=(1.-smoothstep(-0.09,-0.09+fw,innd))*dor;
              vec3 dorf=mix(vec3(0.33,0.24,0.19),vec3(0.24,0.18,0.15),k);
              ramme*=1.-dor;
              vec3 naer=mix(c, w, ramme); naer=mix(naer, hvit, dramme); naer=mix(naer, dorf, dfyll);
              vec3 langt=mix(c, glas, 0.16*ok);
              c=mix(naer, langt, fjern);
              // sokkel og gesims
              float fwy=max(fwidth(lp.y),0.001);
              c*=mix(1.,0.84, 1.-smoothstep(0.42,0.42+fwy,lp.y));
              float ges=smoothstep(topp-0.42,topp-0.42+fwy,lp.y)*(1.-smoothstep(topp-0.12,topp-0.12+fwy,lp.y));
              c=mix(c, hvit, ges*0.55);
            }
          }
          gl_FragColor=vec4(c,1.);
          #include <colorspace_fragment>
        }`
    });
    if(opt.ds) m.side=THREE.DoubleSide;
    mats.set(key,m);
  }
  return mats.get(key);
}
