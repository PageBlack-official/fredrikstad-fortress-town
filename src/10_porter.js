// ---- porter: huset står oppå en portblokk med buet passasje (retning = veien gjennom bygget) ----
(DATA.porter||[]).forEach(pt=>{
  const grp=buildings.find(g=>g.userData.i===pt.bygg); if(!grp) return;
  const b=DATA.bygg[pt.bygg]; const [cx,cy]=b.r;
  if(pt.typ==='mur'){ grp.clear(); } else { grp.children.forEach(c=>{ c.position.y += pt.h; }); }   // mur: portalen er hele bygget; hus: huset opp på portblokken (gruppa selv styres av hover-animasjonen)
  const W=pt.tvers, D=pt.dyp, H=pt.h, pw=pt.pw, ph=pt.ph;
  // tverrsnitt i (x=tvers, y=opp) med buet hull, ekstrudert langs passasjen
  const sh=new THREE.Shape(); sh.moveTo(-W/2,0); sh.lineTo(W/2,0); sh.lineTo(W/2,H); sh.lineTo(-W/2,H); sh.closePath();
  const hul=new THREE.Path(); const r=pw/2, yb=Math.max(0.2, ph-r);
  hul.moveTo(-r,0); hul.lineTo(-r,yb); hul.absarc(0,yb,r,Math.PI,0,true); hul.lineTo(r,0); hul.closePath(); sh.holes.push(hul);
  const eg=new THREE.ExtrudeGeometry(sh,{depth:D,bevelEnabled:false}); eg.translate(0,0,-D/2);
  const wall=b.vegg||[230,220,200];
  const m=new THREE.Mesh(eg,[mat(wall,false,b.veggs,{ds:true}),mat(wall,false,b.veggs,{ds:true})]); m.castShadow=m.receiveShadow=true;
  const ang=Math.atan2(pt.ret[1],pt.ret[0]);
  const y0=(pt.bunn!=null)?pt.bunn:hAt(cx,cy);                      // veien i porten (data), ellers terrenget midt under huset
  m.position.set(cx, y0, -cy); m.rotation.y=ang+Math.PI/2;   // ekstruderingsaksen (z) legges langs veien
  grp.add(m);
  // VINGEMURER (30.10): skrå murer som holder vollen ved porten. [x0, y0, x1, y1, h0, h1, tykk]: innerflaten fra porthjørnet ut til
  // foten, toppen fra h0 (ved porten) til h1 (ved foten) over veien i porten; tykkelsen legges bort fra huset. Mål: verktoy/landemerker.py
  (pt.vingemurer||[]).forEach(([ax,ay,bx,by,h0,h1,t])=>{
    const L=Math.hypot(bx-ax,by-ay); if(L<0.3) return; const ux=(bx-ax)/L, uy=(by-ay)/L; let nx=-uy, ny=ux;
    if(((ax+bx)/2-cx)*nx+((ay+by)/2-cy)*ny<0){ nx=-nx; ny=-ny; }
    const s2=new THREE.Shape(); s2.moveTo(0,-1); s2.lineTo(L,-1); s2.lineTo(L,h1); s2.lineTo(0,h0); s2.closePath();
    const g=new THREE.ExtrudeGeometry(s2,{depth:t,bevelEnabled:false});
    g.applyMatrix4(new THREE.Matrix4().makeBasis(new THREE.Vector3(ux,0,-uy),new THREE.Vector3(0,1,0),new THREE.Vector3(nx,0,-ny)));
    const vm=new THREE.Mesh(g,mat(wall,false,b.veggs,{ds:true})); vm.position.set(ax,y0,-ay); vm.castShadow=vm.receiveShadow=true; grp.add(vm);
  });
});
