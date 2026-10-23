// ---- festningsterrenget: voller med skråninger, grønt som plenene i tegningen ----
const TER = DATA.landskap && DATA.landskap.terreng;
let hAt = ()=>0;
if (TER){
  const b64=s=>{ const b=atob(s); const a=new Uint8Array(b.length); for(let i=0;i<b.length;i++) a[i]=b.charCodeAt(i); return a; };
  const MB=b64(TER.m), nx=TER.nx, ny=TER.ny, G=TER.g;
  const inn=i=>(MB[i>>3]>>(7-(i&7)))&1;
  // høydene ligger bare for punktene i masken (rad for rad); utenfor er bakken null
  const H=new Uint8Array(nx*ny); H.fill(Math.round((TER.off||0)*20)); { const hk=b64(TER.h); let c=0; for(let i=0;i<nx*ny;i++) if(inn(i)) H[i]=hk[c++]; }
  const hv=(i,j)=>H[j*nx+i]/20-(TER.off||0);
  hAt=(x,y)=>{ const fx=(x-TER.x0)/G, fy=(y-TER.y0)/G; const i=Math.floor(fx), j=Math.floor(fy); if(i<0||j<0||i>=nx-1||j>=ny-1) return 0;
    const tx=fx-i, ty=fy-j; return (hv(i,j)*(1-tx)+hv(i+1,j)*tx)*(1-ty)+(hv(i,j+1)*(1-tx)+hv(i+1,j+1)*tx)*ty; };
  const pos=new Float32Array(nx*ny*3);
  for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const k=(j*nx+i)*3; pos[k]=TER.x0+i*G; pos[k+1]=hv(i,j)+0.03; pos[k+2]=-(TER.y0+j*G); }
  const idx=[];
  for(let j=0;j<ny-1;j++) for(let i=0;i<nx-1;i++){ const a=j*nx+i, b=a+1, c=a+nx, d=c+1; if(inn(a)+inn(b)+inn(c)+inn(d)>=2){ idx.push(a,b,c, b,d,c); } }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setIndex(idx); g.computeVertexNormals();
  const terMat=new THREE.ShaderMaterial({
    uniforms:{ lysF:{value:new THREE.Color('rgb(128,180,136)')}, skyggeF:{value:new THREE.Color('rgb(92,142,108)')} },
    vertexShader:`varying vec3 vn; varying vec3 wp; varying float ny; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; vn=normalize(normalMatrix*normal); ny=normal.y; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`uniform vec3 lysF, skyggeF; varying vec3 vn; varying vec3 wp; varying float ny;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      void main(){ vec3 nn=normalize(vn); float d=dot(nn,solRetning()); float hell=1.-ny;
        // to toner som tegningen: skråninger bort fra sola får skyggegrønt, med myk overgang
        float k = 1.-smoothstep(0.437,0.443,d);
        k *= smoothstep(0.108,0.112,hell) * smoothstep(2.2,3.4,wp.y);  // bare ekte voller (over ca. 3 m) får skyggegrønt, ikke små dumper                     // flat mark og slake banker er alltid lyse
        vec3 c=mix(lysF, skyggeF, k);
        // lys kant på vollkronen mot sola
        c=mix(c, lysF*1.06, smoothstep(0.62,0.75,d)*smoothstep(0.05,0.15,hell)*0.6);
        float m=n(wp.xz*0.025)*0.6+n(wp.xz*0.09)*0.4; c*=0.94+0.12*m;
        // gresset malt med korte penselstrøk som tegningens plener
        float gs=n(vec2(wp.x*0.55+wp.z*0.22, wp.z*1.9-wp.x*0.3))*0.6+n(vec2(wp.x*1.7, wp.z*4.3))*0.4; c*=0.975+0.05*gs;
        gl_FragColor=vec4(c,0.); // alfa 0 = terreng: ingen blekkstrek i rutenettets knekker, svakere hjørneskygge
        #include <colorspace_fragment>
      }`
  });
  medSkygge(terMat);
  const ter=new THREE.Mesh(g,terMat); ter.receiveShadow=true; scene.add(ter);
  // festningsområdet som flate under terrenget: gir eksakt kant mot bakken og vannet
  (DATA.landskap.fest||[]).forEach(p=>flatH(p,[],0.02,terMat));
}
// veier som bånd i tegningens gategrå; bruer ligger over vannet med sider (slått sammen til tre mesher)
{
  const buf={K:{p:[],i:[]}, G:{p:[],i:[]}, S:{p:[],i:[]}};
  const quad=(B,v)=>{ const o=B.p.length/3; B.p.push(...v); B.i.push(o,o+2,o+1, o+1,o+2,o+3); };
  (DATA.landskap?DATA.landskap.veier:[]).forEach(v=>{
    const P=v.p, n=P.length; if(n<2) return; const w=v.w/2, dz=v.k==='gang'?-0.03:0; const B=v.k==='gang'?buf.G:buf.K;
    const L=[], R=[];
    for(let k=0;k<n;k++){
      const a=P[Math.max(0,k-1)], b=P[Math.min(n-1,k+1)]; let dx=b[0]-a[0], dy=b[1]-a[1]; const l=Math.hypot(dx,dy)||1; dx/=l; dy/=l;
      const nx=-dy*w, ny=dx*w, z=P[k][2]+dz;
      L.push([P[k][0]+nx, z, -(P[k][1]+ny)]); R.push([P[k][0]-nx, z, -(P[k][1]-ny)]);
    }
    for(let k=0;k<n-1;k++){
      quad(B,[...L[k],...R[k],...L[k+1],...R[k+1]]);
      if(v.b && (P[k][2]>0.5 || P[k+1][2]>0.5)){
        [L,R].forEach(E=>{ const a=E[k], c=E[k+1]; quad(buf.S,[...a, ...c, a[0],Math.max(0.1,a[1]-0.8),a[2], c[0],Math.max(0.1,c[1]-0.8),c[2]]); });
      }
    }
  });
  [[buf.K,mat([128,124,120],false)],[buf.G,mat([146,142,134],false)],[buf.S,mat([120,112,104],false)]].forEach(([B,m])=>{
    if(!B.p.length) return; const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(B.p,3)); g.setIndex(B.i);
    const mm=m.clone(); mm.side=THREE.DoubleSide; const me=new THREE.Mesh(g,mm); me.receiveShadow=true; me.castShadow=(B===buf.S); scene.add(me); });
}
