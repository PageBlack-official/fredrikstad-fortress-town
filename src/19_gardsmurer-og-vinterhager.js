// ---- gårdsmurer i tegl med rundbueport, glasshus (vinterhager) og granittsokkel (27.10, Kaserna etter ombyggingen; data fra verktoy/kaserna.py) ----
{
  const anlegg=new THREE.Group(); scene.add(anlegg);
  const fra=id=>DATA.bygg.find(b=>b.id===id)||{};
  // murene: tegl som huset de hører til, lys dekkstein på toppen. Porten er en høyere pilar med rundbue gjennom.
  (DATA.teglmurer||[]).forEach(mu=>{
    if(mu.skjul) return;
    const hus=fra(mu.farge_fra); const tegl=mat(hus.vegg||[200,120,100],false,hus.veggs,{ds:true}), dekk=mat([214,208,198],false,undefined,{ds:true});
    const [a,c]=mu.p; const dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy), ang=Math.atan2(dy,dx);
    const del=(s0,s1)=>{ if(s1-s0<0.2) return;
      const mx=a[0]+dx*(s0+s1)/2/L, my=a[1]+dy*(s0+s1)/2/L, y0=hAt(mx,my);
      const w=new THREE.Mesh(new THREE.BoxGeometry(s1-s0,mu.h,mu.tykk),tegl); w.position.set(mx,y0+mu.h/2,-my); w.rotation.y=ang; w.castShadow=w.receiveShadow=true; anlegg.add(w);
      const k=new THREE.Mesh(new THREE.BoxGeometry(s1-s0+0.1,0.16,mu.tykk+0.16),dekk); k.position.set(mx,y0+mu.h+0.08,-my); k.rotation.y=ang; k.castShadow=true; anlegg.add(k); };
    const pt=mu.port;
    if(!pt){ del(0,L); return; }
    const sp=pt.s*L, P=pt.pilar; del(0,sp-P/2); del(sp+P/2,L);
    // portpilaren: rektangel med rundbuehull, ekstrudert gjennom muren
    const sh=new THREE.Shape(); sh.moveTo(-P/2,0); sh.lineTo(P/2,0); sh.lineTo(P/2,pt.pilar_h); sh.lineTo(-P/2,pt.pilar_h); sh.closePath();
    const r=pt.bredde/2, yb=pt.hoyde-r; const hul=new THREE.Path(); hul.moveTo(-r,0); hul.lineTo(-r,yb); hul.absarc(0,yb,r,Math.PI,0,true); hul.lineTo(r,0); hul.closePath(); sh.holes.push(hul);
    const D=mu.tykk+0.4; const eg=new THREE.ExtrudeGeometry(sh,{depth:D,bevelEnabled:false,curveSegments:16}); eg.translate(0,0,-D/2);
    const mx=a[0]+dx*pt.s, my=a[1]+dy*pt.s, y0=hAt(mx,my);
    const m=new THREE.Mesh(eg,tegl); m.position.set(mx,y0,-my); m.rotation.y=ang; m.castShadow=m.receiveShadow=true; anlegg.add(m);
    const k=new THREE.Mesh(new THREE.BoxGeometry(P+0.2,0.22,D+0.2),dekk); k.position.set(mx,y0+pt.pilar_h+0.11,-my); k.rotation.y=ang; k.castShadow=true; anlegg.add(k);
    // lys buekant (stikk) rundt åpningen på begge sider
    const bk=new THREE.Shape(); bk.absarc(0,yb,r+0.32,0,Math.PI,false); bk.lineTo(-r,yb); bk.absarc(0,yb,r,Math.PI,0,true); bk.closePath();
    [1,-1].forEach(sd=>{ const g=new THREE.Mesh(new THREE.ShapeGeometry(bk,16),dekk); g.position.set(mx,y0,-my); g.rotation.y=ang; g.translateZ(sd*(D/2+0.01)); if(sd<0) g.rotateY(Math.PI); anlegg.add(g); });
  });
  // glasshus: mørkt grønne sprosser, glass, flatt tak med lanterne (som i illustrasjonene)
  (DATA.vinterhager||[]).forEach(v=>{
    if(v.skjul) return;
    const p=v.p, H=v.h; const y0=Math.min(...p.map(q=>hAt(q[0],q[1])));
    const glass=mat([168,182,170],false,[120,132,124]), ramme=mat([52,78,60],false), tak=mat([92,112,98],false);   // lyst glass med varmt innhold bak, grønne sprosser (SG&CO-illustrasjonene)
    const sh=polyShape(p); const eg=new THREE.ExtrudeGeometry(sh,{depth:H,bevelEnabled:false}); eg.rotateX(-Math.PI/2); eg.translate(0,y0,0);
    const kropp=new THREE.Mesh(eg,[tak,glass]); kropp.castShadow=kropp.receiveShadow=true; anlegg.add(kropp);
    // sprosser: stolper hver 1,1 m langs de tre frie sidene, losholt i dørhøyde og takgesims
    const gx=p.reduce((s,q)=>s+q[0],0)/p.length, gy=p.reduce((s,q)=>s+q[1],0)/p.length;
    for(let i=1;i<p.length;i++){ const a=p[i], c=p[(i+1)%p.length];   // første kant står mot husveggen
      const dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy), ang=Math.atan2(dy,dx), n=Math.max(1,Math.round(L/1.1));
      let nx=dy/L, ny=-dx/L; if(nx*((a[0]+c[0])/2-gx)+ny*((a[1]+c[1])/2-gy)<0){ nx=-nx; ny=-ny; }   // utover fra glasshusets midte
      for(let j=0;j<=n;j++){ const s=j/n; const st=new THREE.Mesh(new THREE.BoxGeometry(0.12,H,0.12),ramme); st.position.set(a[0]+dx*s+nx*0.03, y0+H/2, -(a[1]+dy*s+ny*0.03)); anlegg.add(st); }
      [2.5, H-0.12].forEach(z=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(L,z>3?0.3:0.1,0.14),ramme); b.position.set((a[0]+c[0])/2+nx*0.03, y0+z, -((a[1]+c[1])/2+ny*0.03)); b.rotation.y=ang; anlegg.add(b); });
    }
    const cx=p.reduce((s,q)=>s+q[0],0)/p.length, cy=p.reduce((s,q)=>s+q[1],0)/p.length;
    const a=Math.atan2(p[1][1]-p[0][1],p[1][0]-p[0][0]), L=Math.hypot(p[1][0]-p[0][0],p[1][1]-p[0][1]);
    const lt=new THREE.Mesh(new THREE.BoxGeometry(L*0.45,0.45,1.8),glass); lt.position.set(cx,y0+H+0.22,-cy); lt.rotation.y=a; lt.castShadow=true; anlegg.add(lt);
  });
  // granittsokkel: lys stein rundt foten av huset (bygg med feltet sokkel)
  DATA.bygg.forEach(b=>{
    if(!b.sokkel || b.skjul || !b.p) return;
    const stein=mat(b.sokkel.farge,false); const p=b.p;
    const A=p.reduce((s,q,i)=>{ const c=p[(i+1)%p.length]; return s+q[0]*c[1]-c[0]*q[1]; },0), sg=A<0?1:-1;   // med klokka: utover er til venstre
    for(let i=0;i<p.length;i++){ const a=p[i], c=p[(i+1)%p.length]; const dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy); if(L<0.3) continue;
      const nx=-dy/L*sg, ny=dx/L*sg;   // sokkelen står 0,16 m utenfor veggen, kjellervinduene ligger foran den
      const mx=(a[0]+c[0])/2+nx*0.08, my=(a[1]+c[1])/2+ny*0.08, y0=hAt(mx,my);
      const s=new THREE.Mesh(new THREE.BoxGeometry(L+0.32,b.sokkel.h,0.16),stein); s.position.set(mx,y0+b.sokkel.h/2,-my); s.rotation.y=Math.atan2(dy,dx); s.receiveShadow=true; anlegg.add(s); }
  });
  flatGruppe(anlegg);
}
