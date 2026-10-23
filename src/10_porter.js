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
  m.position.set(cx, hAt(cx,cy), -cy); m.rotation.y=ang+Math.PI/2;   // ekstruderingsaksen (z) legges langs veien
  grp.add(m);
});
