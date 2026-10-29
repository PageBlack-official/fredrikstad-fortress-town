// ---- Statuen på Torvet: Frederik II (Wilhelm Rasmussen, bronse, avduket 12.09.1917) ----
// Alle mål, retning og plass står i data/statue.json med kilder (KILDER.md). Koden tegner bare det dataene sier:
// sokkelen er en stabel av kvadratiske ledd (b = bredde, b2 = bredde i toppen for skrå lister), figuren står på toppen
// i sin egen ramme (+z = fram, -x = hans høyre side, føttene i y = 0) og skaleres til figur.h.
// Retning: kompassgrader (0 = nord, med klokka) for veien statuen ser. Ny statue = ny post i dataene, ingen ny kode.
(DATA.statue||[]).forEach(st=>{
  const g=new THREE.Group(); const [x,y]=st.xy;
  const STEIN=[66,68,72], STEIN_S=[40,41,44], TRINN=[104,106,110], TRINN_S=[66,67,70];
  const PATINA=[120,160,138], PATINA_S=[70,98,86], RELIEFF=[96,128,112], GULL=[214,206,170];
  const M=(f,sk)=>mat(f,false,sk,{ds:true});
  const legg=(geo,f,sk,px,py,pz,forelder=g)=>{ const m=new THREE.Mesh(geo,M(f,sk)); m.position.set(px,py,pz); m.castShadow=true; m.receiveShadow=true; forelder.add(m); return m; };
  // kvadratisk ledd: rett blokk, eller avkortet pyramide (4 sider, dreid 45° så sidene står rett) når b2 er gitt
  const ledd=(b,b2,h,y0,f,sk)=> b2==null
    ? legg(new THREE.BoxGeometry(b,h,b),f,sk,0,y0+h/2,0)
    : (m=>{ m.rotation.y=Math.PI/4; return m; })(legg(new THREE.CylinderGeometry(b2/Math.SQRT2,b/Math.SQRT2,h,4,1),f,sk,0,y0+h/2,0));
  let y0=0, skaft=null;
  (st.sokkel||[]).forEach(l=>{
    const [f,sk]= l.del==='trinn' ? [TRINN,TRINN_S] : l.del==='bronseplate' ? [PATINA,PATINA_S] : [STEIN,STEIN_S];
    ledd(l.b, l.b2, l.h, y0, f, sk);
    if(l.del==='skaft') skaft={y0, h:l.h, b:l.b};
    y0+=l.h;
  });
  // fronten på skaftet: kronet riksvåpen (relieff) over innskriften FREDERIK II (lys, som i fotoene)
  if(skaft){ const zf=skaft.b/2+0.012;
    const skjold=legg(new THREE.CylinderGeometry(0.15,0.15,0.03,20),RELIEFF,PATINA_S,0,skaft.y0+skaft.h*0.58,zf); skjold.rotation.x=Math.PI/2; skjold.scale.set(1,1,1.42);
    legg(new THREE.BoxGeometry(0.2,0.07,0.03),RELIEFF,PATINA_S,0,skaft.y0+skaft.h*0.58+0.25,zf);            // krona
    legg(new THREE.BoxGeometry(0.46,0.05,0.01),GULL,[150,144,116],0,skaft.y0+skaft.h*0.22,zf-0.008);          // innskriften
  }
  // ---- figuren ----
  const k=new THREE.Group(); k.position.y=y0; g.add(k);
  const V=(a,b,c)=>new THREE.Vector3(a,b,c);
  const del=(geo,px,py,pz,forelder=k)=>legg(geo,PATINA,PATINA_S,px,py,pz,forelder);
  // lem mellom to punkter: sylinder med radius r1 (i a) og r2 (i b)
  const lem=(a,b,r1,r2,forelder=k)=>{ const d=b.clone().sub(a), L=d.length(); const m=del(new THREE.CylinderGeometry(r2,r1,L,10),(a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2,forelder);
    m.quaternion.setFromUnitVectors(V(0,1,0), d.normalize()); return m; };
  const kule=(r,p,sx=1,sy=1,sz=1,forelder=k)=>{ const m=del(new THREE.SphereGeometry(r,12,9),p.x,p.y,p.z,forelder); m.scale.set(sx,sy,sz); return m; };
  // bein: føttene ca. 0,3 m fra hverandre, venstre (+x) litt ut og bak; leggskinner, kneskåler, lårskinner
  // Målene i figurens ramme er lest av kommunens frontfoto (kunstregisteret, OBJECTID 4924) som andeler av høyden føtter–isse
  // (kne 0,25, hoseskant 0,44, belte 0,59, skulder 0,81, hake 0,88), kontrollert mot Wilse 1931 og nb.no 1969.
  [[-0.14,0.03],[0.18,-0.04]].forEach(([fx,fz])=>{
    del(new THREE.BoxGeometry(0.12,0.08,0.30),fx,0.04,fz+0.06);                // jernsko
    lem(V(fx,0.08,fz),V(fx*0.97,0.48,fz*0.6),0.06,0.075);                     // legg
    kule(0.082,V(fx*0.95,0.51,fz*0.5+0.02));                                   // kne
    lem(V(fx*0.95,0.52,fz*0.5),V(fx*0.8,0.92,0),0.085,0.10);                  // lår
  });
  // pluderhoser/lårplater til hoseskanten, belte, brystharnisk (dypere foran: «peascod»)
  del(new THREE.CylinderGeometry(0.235,0.275,0.32,12),0,1.04,0).scale.set(1,1,0.78);
  del(new THREE.BoxGeometry(0.08,0.12,0.08),0,0.96,0.21);                      // skamkapsel
  del(new THREE.CylinderGeometry(0.225,0.23,0.05,12),0,1.205,0).scale.set(1,1,0.8);
  del(new THREE.CylinderGeometry(0.255,0.215,0.40,12),0,1.43,0.01).scale.set(1,1,0.82);
  kule(0.105,V(-0.28,1.61,0),1,0.8,1); kule(0.105,V(0.28,1.61,0),1,0.8,1);     // skulderplater
  // bandolær fra høyre skulder til venstre hofte, foran på harnisket
  lem(V(-0.19,1.62,0.16),V(0.03,1.40,0.225),0.042,0.042); lem(V(0.03,1.40,0.225),V(0.23,1.18,0.15),0.042,0.042);
  // hode: pipekrage, hode, helskjegg; vendt litt mot hans høyre
  const hode=new THREE.Group(); hode.position.set(0,1.66,0.0); hode.rotation.y=-0.26; k.add(hode);
  del(new THREE.CylinderGeometry(0.06,0.07,0.12,8),0,0.0,0,hode);              // hals
  del(new THREE.CylinderGeometry(0.15,0.14,0.07,16),0,0.03,0.01,hode);         // pipekrage
  kule(0.115,V(0,0.18,0.0),0.92,1.12,1,hode);                                  // hode
  const skjegg=del(new THREE.ConeGeometry(0.07,0.13,8),0,0.07,0.08,hode); skjegg.rotation.x=Math.PI+0.35;
  // høyre arm: albuen ned og ut, underarm opp; hånda nesten i skulderhøyde godt utenfor kroppen holder kommandostaven
  const hS=V(-0.30,1.60,0), hA=V(-0.40,1.28,0.08), hH=V(-0.55,1.52,0.2);
  lem(hS,hA,0.072,0.062); lem(hA,hH,0.06,0.05); kule(0.055,hH);
  lem(V(-0.64,1.64,0.2),V(-0.16,1.19,0.27),0.026,0.024);                      // staven: litt over hånda, ned mot magen
  // venstre arm i siden: albuen ut, hånda på hofta
  const vS=V(0.30,1.60,0), vA=V(0.56,1.31,-0.06), vH=V(0.32,1.19,0.04);
  lem(vS,vA,0.072,0.062); lem(vA,vH,0.06,0.05); kule(0.055,vH);
  // sverd ved venstre hofte: hjalt og parerstang, slira på skrå ned bak venstre bein; pung foran
  lem(V(0.27,1.10,0.02),V(0.29,1.28,0.1),0.016,0.016);                        // hjalt
  lem(V(0.22,1.11,0.05),V(0.34,1.11,-0.03),0.012,0.012);                      // parerstang
  lem(V(0.28,1.10,-0.01),V(0.30,0.06,-0.42),0.024,0.018);                     // slire
  del(new THREE.BoxGeometry(0.1,0.18,0.06),0.31,1.0,0.09);                    // pung
  k.scale.setScalar(((st.figur||{}).h||2.15)/1.97);                           // modellen er 1,97 m til isse
  // retning: kompassgrader -> rotasjon om y (lokal +z = fram); verden: x = øst, -z = nord
  const b=(st.retning||0)*Math.PI/180; g.rotation.y=Math.atan2(Math.sin(b),-Math.cos(b));
  g.scale.setScalar(st.visningsskala||1);
  g.position.set(x,0,-y); g.userData={b:{navn:st.navn,adr:'Torvet',tekst:st.tekst}}; flatGruppe(g); city.add(g);
});
