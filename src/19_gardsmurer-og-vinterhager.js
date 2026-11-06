import * as THREE from 'three';
import { DATA, scene } from './00_oppsett.js';
import { flat, polyShape } from './03_bakke-vann-grønt.js';
import { plenMat } from './04_brostein-i-hele-gamlebyen.js';
import { flatGruppe, mat } from './05_bygg.js';
import { hAt } from './08_festningsterrenget.js';
// ---- gårdsmurer i tegl med rundbueport, glasshus (vinterhager) (Kaserna etter ombyggingen; data fra verktoy/kaserna.py) ----
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
    // åpninger der et portbygg står i muren ([fra, til, id] i meter langs muren, verktoy/kaserna.py): muren tegnes ikke gjennom buen (avvik A2)
    const hull=(mu.aapninger||[]).map(q=>[q[0],q[1]]);
    const pt=mu.port; if(pt) hull.push([pt.s*L-pt.pilar/2, pt.s*L+pt.pilar/2]);
    hull.sort((u,v)=>u[0]-v[0]); let s0=0; hull.forEach(([h0,h1])=>{ del(s0,h0); s0=Math.max(s0,h1); }); del(s0,L);
    if(!pt) return;
    const P=pt.pilar;
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
  // glasshus: lyse olivengrønne sprosser, glassvegger og saltak i glass med mønet langs husveggen (SG&CO «Utefølelse inne»,
  // Metropolis 06.11; før: mørk grønn kasse med flatt tak og lanterne). Første kant i p står mot husveggen.
  (DATA.vinterhager||[]).forEach(v=>{
    if(v.skjul) return;
    const p=v.p, H=v.h; const y0=Math.min(...p.map(q=>hAt(q[0],q[1])));
    const glass=mat([196,212,206],false,[146,164,160]), glassD=mat([196,212,206],false,[146,164,160],{ds:true}), ramme=mat([128,134,102],false,[92,98,74]), innhold=mat([92,122,80],false);
    const gx=p.reduce((s,q)=>s+q[0],0)/p.length, gy=p.reduce((s,q)=>s+q[1],0)/p.length;
    // glassveggene
    const kropp=new THREE.Mesh((()=>{ const g=new THREE.ExtrudeGeometry(polyShape(p),{depth:H,bevelEnabled:false}); g.rotateX(-Math.PI/2); g.translate(0,y0,0); return g; })(),[glass,glass]);
    kropp.castShadow=kropp.receiveShadow=true; anlegg.add(kropp);
    // grønt innenfor glasset (trærne i potter): lave kroner som skimtes gjennom
    const S2=polyShape(p.map(q=>[gx+(q[0]-gx)*0.7, gy+(q[1]-gy)*0.7])); const ig=new THREE.ExtrudeGeometry(S2,{depth:0.05,bevelEnabled:false}); ig.rotateX(-Math.PI/2); ig.translate(0,y0+H*0.55,0);
    anlegg.add(new THREE.Mesh(ig,[innhold,innhold]));
    for(let i=0;i<p.length;i++){ const a=p[i], c=p[(i+1)%p.length];
      const dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy), ang=Math.atan2(dy,dx), n=Math.max(1,Math.round(L/1.1));
      let nx=dy/L, ny=-dx/L; if(nx*((a[0]+c[0])/2-gx)+ny*((a[1]+c[1])/2-gy)<0){ nx=-nx; ny=-ny; }
      if(i===0) continue;   // mot husveggen: ingen sprosser
      for(let j=0;j<=n;j++){ const s=j/n; const st=new THREE.Mesh(new THREE.BoxGeometry(0.09,H,0.09),ramme); st.position.set(a[0]+dx*s+nx*0.03, y0+H/2, -(a[1]+dy*s+ny*0.03)); anlegg.add(st); }
      [[0.35,0.16],[2.6,0.08],[H-0.1,0.2]].forEach(([z,t])=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(L,t,0.11),ramme); b.position.set((a[0]+c[0])/2+nx*0.03, y0+z, -((a[1]+c[1])/2+ny*0.03)); b.rotation.y=ang; anlegg.add(b); });
    }
    // saltaket: mønet parallelt med husveggen midt over glasshuset, takflater i glass med sperrer, gavltrekanter i glass
    const a=p[0], c=p[1], ux=c[0]-a[0], uy=c[1]-a[1], L=Math.hypot(ux,uy), tx=ux/L, ty=uy/L;
    const D=Math.hypot(p[3][0]-p[0][0],p[3][1]-p[0][1]), ex=(p[3][0]-p[0][0])/D, ey=(p[3][1]-p[0][1])/D, RISE=v.rise||Math.min(1.8,D*0.28);
    const P=(s,d,z)=>new THREE.Vector3(a[0]+tx*s+ex*d, y0+H+z, -(a[1]+ty*s+ey*d));
    const flate=(q)=>{ const g=new THREE.BufferGeometry().setFromPoints(q); g.setIndex([0,1,2,0,2,3]); g.computeVertexNormals(); const m=new THREE.Mesh(g,glassD); m.castShadow=m.receiveShadow=true; anlegg.add(m); };
    flate([P(0,0,0),P(L,0,0),P(L,D/2,RISE),P(0,D/2,RISE)]); flate([P(0,D,0),P(0,D/2,RISE),P(L,D/2,RISE),P(L,D,0)]);
    [0,L].forEach(s=>{ const g=new THREE.BufferGeometry().setFromPoints([P(s,0,0),P(s,D,0),P(s,D/2,RISE)]); g.computeVertexNormals(); anlegg.add(new THREE.Mesh(g,glassD)); });
    const bjelke=(A,B,t)=>{ const d=new THREE.Vector3().subVectors(B,A), len=d.length(); const m=new THREE.Mesh(new THREE.BoxGeometry(t,t,len),ramme); m.position.copy(A).addScaledVector(d,0.5); m.lookAt(B); anlegg.add(m); };
    const ns=Math.max(2,Math.round(L/1.1)); for(let j=0;j<=ns;j++){ const s=L*j/ns; bjelke(P(s,0,0),P(s,D/2,RISE),0.08); bjelke(P(s,D,0),P(s,D/2,RISE),0.08); }
    bjelke(P(0,D/2,RISE),P(L,D/2,RISE),0.16); bjelke(P(0,0,0),P(L,0,0),0.12); bjelke(P(0,D,0),P(L,D,0),0.12);
    // hagen foran: plen, lave klippede hekker langs kanten og blomstrende busker (v.hage fra verktoy/kaserna.py)
    const hg=v.hage; if(!hg) return;
    const hekk=mat([70,112,62],false,[50,84,46]), blomst=[mat([142,108,170],false,[104,80,128]), mat([232,226,236],false,[180,174,186])];
    // plenen tegnes som alle plenene i kartet (flat 0,28 m, plenMat i gresslaget, src/03/04/17): samme farge og samme lag over
    // gårdsflaten (06.11: egen plate i egen farge ble enten dekket av gårdsflaten eller stod som et grønt bord)
    const yp=0.28; flat(hg.p, yp, plenMat); const PL=0;
    (hg.hekker||[]).forEach(lin=>{ for(let i=0;i+1<lin.length;i++){ const A=lin[i], B=lin[i+1], len=Math.hypot(B[0]-A[0],B[1]-A[1]);
      const m=new THREE.Mesh(new THREE.BoxGeometry(len,0.7,0.55),hekk); m.position.set((A[0]+B[0])/2, yp+PL+0.35, -(A[1]+B[1])/2); m.rotation.y=Math.atan2(B[1]-A[1],B[0]-A[0]); m.castShadow=m.receiveShadow=true; anlegg.add(m); } });
    (hg.busker||[]).forEach(([x,y,r],i)=>{ const m=new THREE.Mesh(new THREE.IcosahedronGeometry(r,1),i%2?blomst[0]:hekk); m.scale.y=0.75; m.position.set(x,yp+PL+r*0.7,-y); m.castShadow=true; anlegg.add(m); });
  });
  // verandaer: uteservering langs fasaden som i SG&CO-kveldsbildet: lavt dekke, plantekasser langs ytterkanten med åpning
  // midt foran, parasoller med bord under (te-, verktoy/kaserna.py)
  (DATA.terrasser||[]).forEach(v=>{
    if(v.skjul) return;
    const p=v.p, y0=Math.min(...p.map(q=>hAt(q[0],q[1])));
    const dekk=mat([150,122,98],false), kasse=mat([70,58,48],false), gront=mat([86,124,72],false), duk=mat([222,214,198],false,undefined,{ds:true}), jern=mat([46,46,44],false), bord=mat([120,92,70],false);
    const eg=new THREE.ExtrudeGeometry(polyShape(p),{depth:v.h,bevelEnabled:false}); eg.rotateX(-Math.PI/2); eg.translate(0,y0,0);
    const pl=new THREE.Mesh(eg,[dekk,kasse]); pl.receiveShadow=true; anlegg.add(pl);
    const top=y0+v.h, a0=p[0], a1=p[1], ux=(a1[0]-a0[0]), uy=(a1[1]-a0[1]), L=Math.hypot(ux,uy), tx=ux/L, ty=uy/L;
    const nx=p[3][0]-p[0][0], ny=p[3][1]-p[0][1], D=Math.hypot(nx,ny), ex=nx/D, ey=ny/D, ang=Math.atan2(ty,tx);
    const P=(s,d)=>[a0[0]+tx*s+ex*d, a0[1]+ty*s+ey*d];
    // plantekasser: ytterkanten (åpning midt foran) og begge ender
    const kasseLangs=(s0,s1,d)=>{ if(s1-s0<0.3) return; const [x,y]=P((s0+s1)/2,d);
      const k=new THREE.Mesh(new THREE.BoxGeometry(s1-s0,0.55,0.5),kasse); k.position.set(x,top+0.275,-y); k.rotation.y=ang; k.castShadow=true; anlegg.add(k);
      const g=new THREE.Mesh(new THREE.BoxGeometry(s1-s0-0.1,0.35,0.42),gront); g.position.set(x,top+0.72,-y); g.rotation.y=ang; g.castShadow=true; anlegg.add(g); };
    const ap=v.aapning||2.4; kasseLangs(0,(L-ap)/2,D-0.25); kasseLangs((L+ap)/2,L,D-0.25);
    [0.25,L-0.25].forEach(s=>{ const [x,y]=P(s,(D-0.5)/2+0.2); const k=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.55,D-0.9),kasse); k.position.set(x,top+0.275,-y); k.rotation.y=ang; k.castShadow=true; anlegg.add(k);
      const g=new THREE.Mesh(new THREE.BoxGeometry(0.42,0.35,D-1.0),gront); g.position.set(x,top+0.72,-y); g.rotation.y=ang; anlegg.add(g); });
    // parasoller med bord: jevnt fordelt langs dekket, halvveis ut
    const n=v.parasoller||4;
    for(let i=0;i<n;i++){ const [x,y]=P(L*(i+0.5)/n, D*0.52);
      const st=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,2.5,6),jern); st.position.set(x,top+1.25,-y); anlegg.add(st);
      const sk=new THREE.Mesh(new THREE.ConeGeometry(1.55,0.55,8,1,true),duk); sk.position.set(x,top+2.55,-y); sk.castShadow=true; anlegg.add(sk);
      [-0.75,0.75].forEach(o=>{ const b=new THREE.Mesh(new THREE.CylinderGeometry(0.38,0.38,0.06,10),bord); b.position.set(x+tx*o,top+0.74,-(y+ty*o)); b.castShadow=true; anlegg.add(b);
        const f=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,0.72,5),jern); f.position.set(x+tx*o,top+0.36,-(y+ty*o)); anlegg.add(f); });
    }
  });
  // (granittsokkelen som eget bånd 16 cm utenfor veggen er tatt ut avvik A9: på Artillerigården (sokkel 3,1 m) dekket den
  // vinduene og dørene i første etasje og ble stående når huset ble løftet. Sokkelen tegnes nå bare av src/07, med huset.)
  flatGruppe(anlegg);
}
