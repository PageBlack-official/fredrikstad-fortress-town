import * as THREE from 'three';
import { DATA, scene } from './00_oppsett.js';
import { BAKKELAG, bakkelag, flat, polyShape } from './03_bakke-vann-grønt.js';
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
  // glasshus (SG&CO-illustrasjonen av gården, Vegar 06.11): mørk grønne stolper og flatt tak med lav glasslanterne midt på,
  // høye glassfelt med en rad småruter øverst, dobbeltdør midt foran; varmt lys innenfor. Første kant i p står mot husveggen.
  (DATA.vinterhager||[]).forEach(v=>{
    if(v.skjul) return;
    const p=v.p, H=v.h; const y0=Math.min(...p.map(q=>hAt(q[0],q[1])));
    const glass=mat([196,184,150],false,[140,130,104]), ramme=mat([62,84,68],false,[44,60,48]), tak=mat([96,104,98],false,[72,78,74]), lanterne=mat([170,128,96],false,[124,94,70]);   // taket mørkt grått som på illustrasjonen, men lyst nok til kartets palett (06.11: [58,64,60] ble en svart kasse sett ovenfra)
    const kropp=new THREE.Mesh((()=>{ const g=new THREE.ExtrudeGeometry(polyShape(p),{depth:H,bevelEnabled:false}); g.rotateX(-Math.PI/2); g.translate(0,y0,0); return g; })(),[tak,glass]);
    kropp.castShadow=kropp.receiveShadow=true; anlegg.add(kropp);
    const gx=p.reduce((s,q)=>s+q[0],0)/p.length, gy=p.reduce((s,q)=>s+q[1],0)/p.length;
    for(let i=1;i<p.length;i++){ const a=p[i], c=p[(i+1)%p.length];   // første kant (mot husveggen) uten sprosser
      const dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy), ang=Math.atan2(dy,dx), n=Math.max(1,Math.round(L/1.05));
      let nx=dy/L, ny=-dx/L; if(nx*((a[0]+c[0])/2-gx)+ny*((a[1]+c[1])/2-gy)<0){ nx=-nx; ny=-ny; }
      for(let j=0;j<=n;j++){ const s=j/n; const st=new THREE.Mesh(new THREE.BoxGeometry(0.09,H,0.09),ramme); st.position.set(a[0]+dx*s+nx*0.03, y0+H/2, -(a[1]+dy*s+ny*0.03)); anlegg.add(st); }
      // sokkel, losholt under smårutene, smårutenes midtpost og takgesimsen
      [[0.2,0.4],[H-1.05,0.1],[H-0.55,0.05],[H-0.15,0.32]].forEach(([z,t])=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(L+0.1,t,0.16),ramme); b.position.set((a[0]+c[0])/2+nx*0.03, y0+z, -((a[1]+c[1])/2+ny*0.03)); b.rotation.y=ang; anlegg.add(b); });
      // dobbeltdøra midt på langsiden mot gården
      if(i===2){ const [mx,my]=[(a[0]+c[0])/2+nx*0.05,(a[1]+c[1])/2+ny*0.05]; [-0.45,0,0.45].forEach(o=>{ const d=new THREE.Mesh(new THREE.BoxGeometry(o?0.08:0.1,2.5,0.16),ramme); d.position.set(mx+dx/L*o, y0+1.25, -(my+dy/L*o)); d.rotation.y=ang; anlegg.add(d); }); }
    }
    // lanterna: lav glassoverbygning midt på det flate taket
    const a=Math.atan2(p[1][1]-p[0][1],p[1][0]-p[0][0]), L=Math.hypot(p[1][0]-p[0][0],p[1][1]-p[0][1]), D=Math.hypot(p[3][0]-p[0][0],p[3][1]-p[0][1]);
    const lt=new THREE.Mesh(new THREE.BoxGeometry(L*0.3,0.4,D*0.4),lanterne); lt.position.set(gx,y0+H+0.2,-gy); lt.rotation.y=a; lt.castShadow=true; anlegg.add(lt);
    // uteplassen foran (v.uteplass fra verktoy/kaserna.py): lyst steindekke i laget over gresset, kafébord med kurvstoler, bed med
    // hortensia, små trær
    const u=v.uteplass; if(!u) return;
    const belegg=bakkelag(mat([206,198,184],false,[160,152,140]), BAKKELAG.gress);
    // uteplassen ligger 28 cm over bakken midt på plassen (målt bakke, 07.11; 0 uten bakke.json)
    const yp=0.28+hAt(u.p.reduce((s,q)=>s+q[0],0)/u.p.length, u.p.reduce((s,q)=>s+q[1],0)/u.p.length); flat(u.p, yp, belegg);
    const bordMat=mat([214,196,160],false), kurv=mat([168,128,84],false), jern=mat([46,46,44],false), blad=mat([96,132,84],false,[70,100,62]), horts=[mat([156,142,196],false,[118,106,150]), mat([206,196,226],false,[156,148,172])], stamme=mat([96,78,62],false);
    (u.bord||[]).forEach(([x,y],i)=>{ const b=new THREE.Mesh(new THREE.CylinderGeometry(0.55,0.55,0.05,14),bordMat); b.position.set(x,yp+0.74,-y); b.castShadow=true; anlegg.add(b);
      const f=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.07,0.72,6),jern); f.position.set(x,yp+0.36,-y); anlegg.add(f);
      for(let k=0;k<4;k++){ const w=k*Math.PI/2+i*0.4; const st=new THREE.Mesh(new THREE.BoxGeometry(0.46,0.75,0.46),kurv); st.position.set(x+Math.cos(w)*0.85,yp+0.375,-(y+Math.sin(w)*0.85)); st.rotation.y=-w; st.castShadow=true; anlegg.add(st); } });
    (u.bed||[]).forEach(([x,y,r],i)=>{ const m=new THREE.Mesh(new THREE.IcosahedronGeometry(r,1),i%3===0?blad:horts[i%2]); m.scale.y=0.6; m.position.set(x,yp+r*0.45,-y); m.castShadow=true; anlegg.add(m); });
    (u.traer||[]).forEach(([x,y,r])=>{ const st=new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.13,2.2,6),stamme); st.position.set(x,yp+1.1,-y); anlegg.add(st);
      const k=new THREE.Mesh(new THREE.IcosahedronGeometry(r,1),blad); k.position.set(x,yp+2.6,-y); k.castShadow=true; anlegg.add(k); });
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
    [0.25,L-0.25].filter((s,i)=>!(i===0 && (v.uten_kasse||[]).includes('start'))).forEach(s=>{ const [x,y]=P(s,(D-0.5)/2+0.2); const k=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.55,D-0.9),kasse); k.position.set(x,top+0.275,-y); k.rotation.y=ang; k.castShadow=true; anlegg.add(k);
      const g=new THREE.Mesh(new THREE.BoxGeometry(0.42,0.35,D-1.0),gront); g.position.set(x,top+0.72,-y); g.rotation.y=ang; anlegg.add(g); });
    // parasoller med bord: jevnt fordelt langs dekket, halvveis ut
    const n=v.parasoller||4, R=v.rader||1;   // rader: kvadratisk veranda (innerhjørnet) får parasollene i flere rader
    for(let r=0;r<R;r++) for(let i=0;i<n;i++){ const [x,y]=P(L*(i+0.5)/n, R===1 ? D*0.52 : D*(r+0.6)/(R+0.3));
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
