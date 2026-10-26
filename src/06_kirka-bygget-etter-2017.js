// ---- kirka, bygget etter 2017-tegningen: hvitt tårn, grønt kobber, korsformet skip med valmede skifertak ----
function sentr(p){ return p.reduce((a,q)=>[a[0]+q[0]/p.length,a[1]+q[1]/p.length],[0,0]); }
function skaler(p,f){ const c=sentr(p); return p.map(q=>[c[0]+(q[0]-c[0])*f, c[1]+(q[1]-c[1])*f]); }
function oktagon(c,r,rot){ const o=[]; for(let i=0;i<8;i++){ const a=rot+i*Math.PI/4+Math.PI/8; o.push([c[0]+Math.cos(a)*r, c[1]+Math.sin(a)*r]); } return o; }
function loft(pb, pt, y0, y1, farge, grp, lukk=true){
  const pos=[]; const n=pb.length;
  for(let i=0;i<n;i++){ const a=pb[i], b2=pb[(i+1)%n], c=pt[(i+1)%n], d=pt[i];
    pos.push(a[0],y0,-a[1], b2[0],y0,-b2[1], c[0],y1,-c[1],  a[0],y0,-a[1], c[0],y1,-c[1], d[0],y1,-d[1]); }
  if(lukk){ const cc=sentr(pt); for(let i=0;i<n;i++){ const a=pt[i], b2=pt[(i+1)%n]; pos.push(a[0],y1,-a[1], b2[0],y1,-b2[1], cc[0],y1,-cc[1]); } }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  // sørg for at flatene vender utover
  const m=new THREE.Mesh(g,mat(farge,false)); m.material.side=THREE.FrontSide; m.castShadow=true;
  const g2=g.clone(); g2.computeVertexNormals();
  const dbl=new THREE.Mesh(g, new THREE.ShaderMaterial(Object.assign({}, mat(farge,false)))); 
  const mm=new THREE.Mesh(g,mat(farge,false)); mm.castShadow=true; mm.material=mm.material.clone(); mm.material.side=THREE.DoubleSide; grp.add(mm);
  grp.add(new THREE.LineSegments(new THREE.EdgesGeometry(g,20),edgeMat));
}
function spiss(pb, y0, y1, farge, grp){ loft(pb, pb.map(()=>sentr(pb)), y0, y1, farge, grp, false); }
function bygKirke(k, grp){
  // Domkirken slik den er tegnet i trykkfila 2019: korsformet skip med saltak i skifer, hvitt tårn med salviegrønn hjelm, lanterne og spir
  const HVIT=[252,252,252], HVIT_S=[192,196,196], SKIFER=[128,128,132], SKIFER_S=[68,68,72];
  const SALVIE=[196,228,202], SALVIE_S=[128,146,138], LANT=[176,212,190], LANT_S=[92,100,100], MORK=[92,100,100], MORK_S=[52,52,52];
  const GLASS=[62,70,82], GLASS_S=[44,50,60];
  const M=(f,sk)=>mat(f,false,sk,{ds:true});
  const add=(g,f,sk)=>{ const m=new THREE.Mesh(g,M(f,sk)); m.castShadow=true; m.receiveShadow=true; grp.add(m); return m; };
  const W3=(p,y)=>new THREE.Vector3(p[0],y,-p[1]);
  function loftK(pb, pt, y0, y1, f, sk, lukk=true){
    const pos=[]; const n=pb.length;
    for(let i=0;i<n;i++){ const a=pb[i], b2=pb[(i+1)%n], c=pt[(i+1)%n], d=pt[i];
      pos.push(a[0],y0,-a[1], b2[0],y0,-b2[1], c[0],y1,-c[1],  a[0],y0,-a[1], c[0],y1,-c[1], d[0],y1,-d[1]); }
    if(lukk){ const cc=sentr(pt); for(let i=0;i<n;i++){ const a=pt[i], b2=pt[(i+1)%n]; pos.push(a[0],y1,-a[1], b2[0],y1,-b2[1], cc[0],y1,-cc[1]); } }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); g.computeVertexNormals(); return add(g,f,sk);
  }
  // flat ornament (vindu, urskive) lagt på en flate: basis = tangent, opp, normal
  function legg(geo, P, tan, opp, nor, off, f, sk){
    const m4=new THREE.Matrix4().makeBasis(tan,opp,nor); m4.setPosition(P.clone().addScaledVector(nor,off)); geo.applyMatrix4(m4); return add(geo,f,sk);
  }
  function bue(w,h){ const s=new THREE.Shape(); const r=w/2; s.moveTo(-r,0); s.lineTo(r,0); s.lineTo(r,h-r); s.absarc(0,h-r,r,0,Math.PI,false); s.lineTo(-r,0); return s; }
  function buevindu(P, tan, opp, nor, w, h, sprosser=true){
    legg(new THREE.ShapeGeometry(bue(w+0.36,h+0.18),10), P.clone().addScaledVector(opp,-0.09), tan, opp, nor, 0.06, HVIT, HVIT_S);
    legg(new THREE.ShapeGeometry(bue(w,h),10), P, tan, opp, nor, 0.10, GLASS, GLASS_S);
    if(sprosser){
      legg(new THREE.PlaneGeometry(0.09,h-0.05).translate(0,(h-0.05)/2,0), P, tan, opp, nor, 0.13, HVIT, HVIT_S);
      legg(new THREE.PlaneGeometry(w,0.09).translate(0,h-w/2,0), P, tan, opp, nor, 0.13, HVIT, HVIT_S);
    }
  }
  function rundvindu(P, tan, opp, nor, r, kors=true){
    legg(new THREE.CircleGeometry(r+0.17,20), P, tan, opp, nor, 0.06, HVIT, HVIT_S);
    legg(new THREE.CircleGeometry(r,20), P, tan, opp, nor, 0.10, GLASS, GLASS_S);
    if(kors){ legg(new THREE.PlaneGeometry(0.08,2*r), P, tan, opp, nor, 0.13, HVIT, HVIT_S); legg(new THREE.PlaneGeometry(2*r,0.08), P, tan, opp, nor, 0.13, HVIT, HVIT_S); }
  }
  // flatene til en mangekant: utovervendt normal og tangent
  function flater(poly){
    const c=sentr(poly); const out=[];
    for(let i=0;i<poly.length;i++){ const p0=poly[i], p1=poly[(i+1)%poly.length]; const dx=p1[0]-p0[0], dy=p1[1]-p0[1]; const L=Math.hypot(dx,dy);
      let nx=dy/L, ny=-dx/L; const mx=(p0[0]+p1[0])/2, my=(p0[1]+p1[1])/2; if((mx-c[0])*nx+(my-c[1])*ny<0){ nx=-nx; ny=-ny; }
      out.push({p0,p1,L,mid:[mx,my],tan:new THREE.Vector3(dx/L,0,-dy/L), nor:new THREE.Vector3(nx,0,-ny)}); }
    return out;
  }
  // tårnet tegnes bredere enn grunnrisset i kartdataene (som i trykkfila): skaler 1,3 om midten av siden som møter skipet
  const t0=k.torn, skc=sentr(k.skip);
  const øst=t0.map((p,i)=>[p,t0[(i+1)%t0.length]]).reduce((a,e)=>{ const m=[(e[0][0]+e[1][0])/2,(e[0][1]+e[1][1])/2]; const dd=Math.hypot(m[0]-skc[0],m[1]-skc[1]); return (!a||dd<a.d)?{m,d:dd}:a; },null).m;
  const t=t0.map(p=>[øst[0]+(p[0]-øst[0])*1.3, øst[1]+(p[1]-øst[1])*1.3]);
  const tc=sentr(t); const side=Math.hypot(t[1][0]-t[0][0],t[1][1]-t[0][1]); const rot=Math.atan2(t[1][1]-t[0][1],t[1][0]-t[0][0]);
  const nærTårn=(p)=>Math.hypot(p[0]-tc[0],p[1]-tc[1])<side*0.75;

  // ---- skipet ----
  const WH=8.8, RISE=5.6, OH=0.35;   // målt i Kartverkets DOM−DTM 25.10: takfot ca. 8,8 m, møne 14,4 m (før 9,5 + 8,2 = 17,7, 3 m for høyt)
  const sk=k.skip;
  const eg=new THREE.ExtrudeGeometry(polyShape(sk),{depth:WH,bevelEnabled:false}); eg.rotateX(-Math.PI/2);
  add(eg,HVIT,HVIT_S);
  // korsarmene: endeveggene er de lange kantene (>12 m); motstående ende ligger seks kanter unna
  const kanter=sk.map((p,i)=>[i,Math.hypot(sk[(i+1)%sk.length][0]-p[0],sk[(i+1)%sk.length][1]-p[1])]);
  const ender=kanter.filter(e=>e[1]>12).map(e=>e[0]);
  const armer=[]; ender.forEach(i=>{ const j=(i+sk.length/2)%sk.length; if(ender.includes(j) && i<j) armer.push([i,j]); });
  armer.forEach(([i,j])=>{
    const a0=sk[i], a1=sk[(i+1)%sk.length], b0=sk[j], b1=sk[(j+1)%sk.length];
    const m1=[(a0[0]+a1[0])/2,(a0[1]+a1[1])/2], m2=[(b0[0]+b1[0])/2,(b0[1]+b1[1])/2];
    const ax=[m2[0]-m1[0],m2[1]-m1[1]]; const L=Math.hypot(ax[0],ax[1]); const u=[ax[0]/L,ax[1]/L], n=[-u[1],u[0]];
    const w=Math.hypot(a1[0]-a0[0],a1[1]-a0[1])/2;
    const P=(s_,t_,y)=>new THREE.Vector3(m1[0]+u[0]*s_+n[0]*t_, y, -(m1[1]+u[1]*s_+n[1]*t_));
    const s0=-0.3, s1=L+0.3, we=w+OH, yE=WH-OH*RISE/w, yR=WH+RISE;
    const q=(A,B,C,D,arr)=>arr.push(...[A,B,C,A,C,D].flatMap(v=>[v.x,v.y,v.z]));
    const tak=[]; q(P(s0,-we,yE),P(s1,-we,yE),P(s1,0,yR),P(s0,0,yR),tak); q(P(s0,we,yE),P(s0,0,yR),P(s1,0,yR),P(s1,we,yE),tak);
    const tg=new THREE.BufferGeometry(); tg.setAttribute('position',new THREE.Float32BufferAttribute(tak,3)); add(tg,SKIFER,SKIFER_S);
    const gv=[]; [[0,1],[L,-1]].forEach(([s_])=>{ const A=P(s_,-w,WH),B=P(s_,w,WH),C=P(s_,0,yR-0.25); gv.push(A.x,A.y,A.z,B.x,B.y,B.z,C.x,C.y,C.z); });
    const gg=new THREE.BufferGeometry(); gg.setAttribute('position',new THREE.Float32BufferAttribute(gv,3)); add(gg,HVIT,HVIT_S);
    // rundvindu i gavlene som ikke står mot tårnet
    [[0,-1],[L,1]].forEach(([s_,sg])=>{ const mid=[m1[0]+u[0]*s_, m1[1]+u[1]*s_]; if(nærTårn(mid)) return;
      const nor=new THREE.Vector3(u[0]*sg,0,-u[1]*sg), tan=new THREE.Vector3(n[0],0,-n[1]); rundvindu(P(s_,0,WH+RISE*0.38), tan, new THREE.Vector3(0,1,0), nor, 1.05); });
  });
  // høye buevinduer i alle frie skipsvegger
  flater(sk).forEach(f=>{
    if(nærTårn(f.mid) || f.L<3) return;
    const n=f.L>12 ? 3 : 2; const step=f.L/n;
    for(let i=0;i<n;i++){ const s_=step*(i+0.5); const p=[f.p0[0]+(f.p1[0]-f.p0[0])*s_/f.L, f.p0[1]+(f.p1[1]-f.p0[1])*s_/f.L];
      buevindu(W3(p,2.6), f.tan, new THREE.Vector3(0,1,0), f.nor, 1.55, 5.0); }
  });

  // ---- tårnet ----
  const SH=34, SK1=40.1, OV1=46.0, LA0=47.6, LA1=51.2, KU1=53.3, SP1=60.0;   // høyder etter forholdene i trykkfila
  const te=new THREE.ExtrudeGeometry(polyShape(t),{depth:SH,bevelEnabled:false}); te.rotateX(-Math.PI/2); add(te,HVIT,HVIT_S);
  loftK(t, skaler(t,1.06), SH, SH+0.5, HVIT, HVIT_S);                     // gesims
  const ov=skaler(t,0.52);
  loftK(skaler(t,1.06), ov, SH+0.5, SK1, SALVIE, SALVIE_S);                // salviegrønt skjørt
  loftK(ov, ov, SK1, OV1, SALVIE, SALVIE_S);                               // øvre etasje
  loftK(ov, skaler(t,0.58), OV1, OV1+0.4, SALVIE, SALVIE_S);               // gesims
  const o3=oktagon(tc, side*0.235, rot);
  loftK(skaler(t,0.58), o3, OV1+0.4, LA0, LANT, LANT_S);                  // overgang til lanterne
  loftK(o3, o3, LA0, LA1, LANT, LANT_S);                                   // lanterne
  loftK(o3, oktagon(tc, side*0.265, rot), LA1, LA1+0.35, LANT, LANT_S);    // gesims
  // klokkeformet kuppel over lanternen (åttekantet dreiing)
  const R0=side*0.25, prof=[[R0,0],[R0*0.98,0.35],[R0*0.8,0.95],[R0*0.52,1.5],[R0*0.3,1.85],[R0*0.18,2.15],[R0*0.2,2.4],[R0*0.12,2.6],[0.001,2.75]];
  const lat=new THREE.LatheGeometry(prof.map(([r,y])=>new THREE.Vector2(r,y)),8); lat.rotateY(-rot+Math.PI/8);
  const kup=new THREE.Mesh(lat,M(LANT,LANT_S)); kup.position.set(tc[0],LA1+0.35,-tc[1]); kup.castShadow=true; grp.add(kup);
  const sp=oktagon(tc, 0.3, rot); loftK(sp, sp.map(()=>tc), KU1+0.6, SP1, MORK, MORK_S, false);   // spir
  const kule=new THREE.Mesh(new THREE.SphereGeometry(0.28,10,8), M(MORK,MORK_S)); kule.position.set(tc[0],SP1-1.6,-tc[1]); grp.add(kule);
  const fløy=new THREE.Mesh(new THREE.PlaneGeometry(1.1,0.55), M(MORK,MORK_S)); fløy.position.set(tc[0]+0.45,SP1-0.7,-tc[1]); fløy.rotation.y=-rot; grp.add(fløy);
  // vinduer, urskiver og takarker på alle fire sider
  const opp=new THREE.Vector3(0,1,0);
  flater(t).forEach(f=>{
    const c2=f.mid;
    buevindu(W3(c2,SH*0.6), f.tan, opp, f.nor, 1.8, 4.4);
    rundvindu(W3(c2,SH*0.42), f.tan, opp, f.nor, 0.95);
    rundvindu(W3(c2,SH*0.27), f.tan, opp, f.nor, 0.95);
    // øvre etasje: buevindu og urskive
    const ov2=[tc[0]+(c2[0]-tc[0])*0.52, tc[1]+(c2[1]-tc[1])*0.52];
    buevindu(W3(ov2,SK1+1.3), f.tan, opp, f.nor, 1.35, 3.9);        // høyt buevindu i øvre etasje, som i tegningen
    // liten takark med lydluke midt på skjørtet
    const fr=0.5, ys=SH+0.5+(SK1-SH-0.5)*fr; const k1=1.06+(0.52-1.06)*fr;
    const ap=[tc[0]+(c2[0]-tc[0])*k1, tc[1]+(c2[1]-tc[1])*k1];
    const box=new THREE.BoxGeometry(1.5,1.9,1.4); const bm=new THREE.Mesh(box,M(SALVIE,SALVIE_S));
    bm.position.copy(W3(ap,ys+0.55)).addScaledVector(f.nor,0.25); bm.lookAt(bm.position.clone().add(f.nor)); bm.castShadow=true; grp.add(bm);
    const hatt=new THREE.Mesh(new THREE.ConeGeometry(1.12,0.9,4,1), M(LANT,LANT_S)); hatt.position.copy(bm.position).add(new THREE.Vector3(0,1.4,0)); hatt.rotation.y=-rot+Math.PI/4; grp.add(hatt);
    const luke=W3(ap,ys+0.05).addScaledVector(f.nor,0.95);
    legg(new THREE.ShapeGeometry(bue(0.9,1.3),8), luke, f.tan, opp, f.nor, 0.0, MORK, MORK_S);
    for(let r=0;r<3;r++) legg(new THREE.PlaneGeometry(0.9,0.07).translate(0,0.3+r*0.3,0), luke, f.tan, opp, f.nor, 0.03, LANT, LANT_S);
  });
  // lanternens smale vinduer
  flater(o3).forEach(f=>{ buevindu(W3(f.mid,LA0+1.0), f.tan, opp, f.nor, 0.5, 2.4, false); });
  // inngangsdør i tårnfoten mot vest (siden lengst fra skipet)
  const fot=flater(t).reduce((a,f)=>{ const d=Math.hypot(f.mid[0]-sentr(sk)[0],f.mid[1]-sentr(sk)[1]); return (!a||d>a.d)?{f,d}:a; },null).f;
  legg(new THREE.ShapeGeometry(bue(2.6,4.8),12), W3(fot.mid,0).addScaledVector(opp,-0.05), fot.tan, opp, fot.nor, 0.06, HVIT, HVIT_S);
  legg(new THREE.ShapeGeometry(bue(2.1,4.4),12), W3(fot.mid,0), fot.tan, opp, fot.nor, 0.10, [104,86,72], [72,60,52]);
}

const buildings=[];
