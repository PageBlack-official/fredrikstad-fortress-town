// ---- Statuer og skulpturer: Frederik II på Torvet (Wilhelm Rasmussen 1917), «Sittende pike» i Tamburparken (Arne Durban 1957/58) ----
// Alle mål, retning og plass står i data/statue.json med kilder (KILDER.md). Koden tegner bare det dataene sier:
// sokkelen er en stabel av ledd (b = bredde, d = dybde om leddet ikke er kvadratisk, b2 = bredde i toppen for skrå lister,
// stein: mørk | lys | bronse), figuren står på toppen i sin egen ramme (+z = fram, -x = figurens høyre side, y = 0 på sokkelen)
// og skaleres til figur.h. figur.form velger figuren i FIGUR (en ny form = en ny funksjon her; en ny statue med kjent form = bare data).
// Retning: kompassgrader (0 = nord, med klokka) for veien figuren ser. Poster med tegnes:false (plass ikke sikker) tegnes ikke.
(()=>{
const STEINFARGE={ 'mørk':[[66,68,72],[40,41,44]], lys:[[178,176,170],[124,122,118]], trinn:[[104,106,110],[66,67,70]], bronse:[[120,160,138],[70,98,86]] };
const PATINA=[120,160,138], PATINA_S=[70,98,86], RELIEFF=[96,128,112], GULL=[214,206,170];
const V=(a,b,c)=>new THREE.Vector3(a,b,c);
// dreid: omdreiningsflate fra profil [[radius, høyde]] (glatt rustning i stedet for sylindre), lukket topp og bunn
const dreid=(prof,n)=>{ const P=[new THREE.Vector2(0,prof[0][1]), ...prof.map(([r,y])=>new THREE.Vector2(r,y)), new THREE.Vector2(0,prof[prof.length-1][1])]; return new THREE.LatheGeometry(P,n); };
// pipekrage: skive med rillet kant (k riller), radius r, høyde h
const pipekrage=(r,h,k)=>{ const g=new THREE.CylinderGeometry(r,r*0.94,h,k*4,1); const p=g.getAttribute('position');
  for(let j=0;j<p.count;j++){ const x=p.getX(j), z=p.getZ(j), rr=Math.hypot(x,z); if(rr<1e-4) continue; const a=Math.atan2(z,x), f=1+0.09*Math.cos(a*k); p.setX(j,x*f); p.setZ(j,z*f); }
  g.computeVertexNormals(); return g; };
// figurene: får verktøyene (del, lem, kule) og returnerer modellhøyden (isse over sokkelen) som figur.h skalerer til
const FIGUR={
  // Frederik II: platerustning, kommandostav i høyre hånd, venstre hånd i siden. Målene er lest av kommunens frontfoto (kunstregisteret,
  // OBJECTID 4924) som andeler av høyden føtter–isse (kne 0,25, hoseskant 0,44, belte 0,59, skulder 0,81, hake 0,88),
  // kontrollert mot Wilse 1931 og nb.no 1969. Posituren rettet 30.10 etter Street View mai 2024 (rett forfra, fra vest-nordvest) og
  // aug. 2010 (figurens venstre side, fra sør-sørvest), sett i Vegars Chrome; andeler av høyden lest i bildene (isse 1,97 i modellen):
  // høyre hånd 1,58 foran skulderen, staven fra magen (1,17) opp gjennom hånda og 0,15 forbi, venstre albue ut og litt bak,
  // venstre fot ut til siden, slira fra venstre hofte ned bak beina med spissen nesten midt bak (0,18 over sokkelen), smal pipekrage.
  rustning_stav({k,del,lem,kule}){
    [[-0.13,0.03],[0.24,0.0]].forEach(([fx,fz])=>{
      kule(0.075,V(fx,0.045,fz+0.06),0.85,0.6,2.0);                              // jernsko (sabaton): avrundet, ikke kasse (30.10)
      lem(V(fx,0.08,fz),V(fx*0.97,0.48,fz*0.6),0.06,0.075);                     // legg
      kule(0.082,V(fx*0.95,0.51,fz*0.5+0.02));                                   // kne
      lem(V(fx*0.95,0.52,fz*0.5),V(fx*0.8,0.92,0),0.085,0.10);                  // lår
    });
    del(dreid([[0.20,0],[0.27,0.06],[0.285,0.16],[0.26,0.27],[0.225,0.32]],18),0,0.88,0).scale.set(1,1,0.78);   // pluderhoser/lårplater: buklet profil (30.10)
    del(new THREE.BoxGeometry(0.08,0.12,0.08),0,0.96,0.21);                      // skamkapsel
    del(new THREE.CylinderGeometry(0.225,0.23,0.05,24),0,1.205,0).scale.set(1,1,0.8);    // belte
    del(dreid([[0.215,0],[0.235,0.08],[0.258,0.2],[0.262,0.3],[0.245,0.37],[0.17,0.41]],20),0,1.23,0.01).scale.set(1,1,0.82); // brystharnisk: rundet bryst, smalt mot beltet (30.10)
    kule(0.105,V(-0.28,1.61,0),1,0.8,1); kule(0.105,V(0.28,1.61,0),1,0.8,1);     // skulderplater
    lem(V(-0.19,1.62,0.16),V(0.03,1.40,0.225),0.042,0.042); lem(V(0.03,1.40,0.225),V(0.23,1.18,0.15),0.042,0.042);   // bandolær
    const hode=new THREE.Group(); hode.position.set(0,1.66,0.0); hode.rotation.y=-0.17; k.add(hode);             // litt mot hans høyre (ca. 10°)
    del(new THREE.CylinderGeometry(0.06,0.07,0.12,8),0,0.0,0,hode);              // hals
    del(pipekrage(0.12,0.07,16),0,0.03,0.01,hode);                             // pipekrage: smal, rillet (bredde som hodet, Street View 2024)
    kule(0.115,V(0,0.18,0.0),0.92,1.12,1,hode);                                  // hode
    kule(0.08,V(0,0.11,0.05),1.0,0.95,0.7,hode); kule(0.042,V(0,0.05,0.085),0.9,1.45,0.8,hode);   // kortklipt helskjegg med spiss hake (Street View 2024)
    kule(0.03,V(0,0.135,0.105),2.2,0.55,0.7,hode);                                                    // barten
    const hS=V(-0.30,1.60,0), hA=V(-0.40,1.30,0.10), hH=V(-0.50,1.58,0.25);     // høyre arm: albuen ned langs siden, hånda i skulderhøyde foran
    lem(hS,hA,0.072,0.062); lem(hA,hH,0.06,0.05); kule(0.055,hH);
    lem(V(-0.58,1.70,0.36),V(-0.17,1.17,0.26),0.026,0.024);                     // staven: fra magen opp gjennom hånda, tuppen fram og ut
    const vS=V(0.30,1.60,0), vA=V(0.52,1.30,-0.12), vH=V(0.33,1.16,0.03);       // venstre hånd i siden, albuen ut og litt bak
    lem(vS,vA,0.072,0.062); lem(vA,vH,0.06,0.05); kule(0.055,vH);
    lem(V(0.26,1.10,0.0),V(0.28,1.22,0.16),0.016,0.016);                        // hjalt: fram og opp under venstre hånd
    lem(V(0.21,1.12,0.04),V(0.33,1.10,-0.03),0.012,0.012);                      // parerstang
    lem(V(0.27,1.08,-0.02),V(0.04,0.17,-0.46),0.024,0.018);                     // slire: fra venstre hofte ned bak beina, spissen nesten midt bak
    del(new THREE.BoxGeometry(0.1,0.28,0.06),0.33,0.95,0.05);                   // pung ved venstre hofte (0,8–1,1 i Street View 2024)
    return 1.97;
  },
  // «Sittende pike»: naken jente som sitter på hælene, armene strake ned med hendene på knærne, overkroppen litt fram, hodet løftet
  // (Fredrikstad Museum-foto 1958 og kommunens foto). Modellen er 0,88 til isse.
  knelende_pike({k,del,lem,kule}){
    [-0.1,0.1].forEach(sx=>{
      lem(V(sx,0.06,0.30),V(sx*0.9,0.05,-0.12),0.055,0.045);                    // legg på sokkelen, kne fram
      kule(0.06,V(sx,0.07,0.31));                                                // kne
      lem(V(sx,0.08,0.30),V(sx*0.8,0.2,-0.06),0.065,0.085);                     // lår ned mot hælene
    });
    kule(0.15,V(0,0.2,-0.08),1.05,0.8,0.9);                                      // hofte/sete på hælene
    lem(V(0,0.22,-0.07),V(0,0.62,0.03),0.12,0.105).scale.set(1,1,0.75);          // overkropp, litt fram
    const skS=[V(-0.12,0.6,0.04),V(0.12,0.6,0.04)], hand=[V(-0.1,0.13,0.34),V(0.1,0.13,0.34)];
    [0,1].forEach(i=>{ lem(skS[i],hand[i],0.035,0.028); kule(0.032,hand[i],1,0.7,1.3); });   // strake armer, hender på knærne
    lem(V(0,0.62,0.04),V(0,0.7,0.06),0.035,0.035);                               // hals
    const hode=new THREE.Group(); hode.position.set(0,0.78,0.08); hode.rotation.set(-0.2,-0.15,0); k.add(hode);   // løftet, litt til siden
    kule(0.075,V(0,0,0),0.9,1.08,1,hode); kule(0.08,V(0,0.03,-0.015),1,0.9,1,hode);          // ansikt og hår (kort, fyldig)
    return 0.88;
  },
};
(DATA.statue||[]).filter(st=>st.tegnes!==false && st.figur && FIGUR[st.figur.form]).forEach(st=>{
  const g=new THREE.Group(); const [x,y]=st.xy;
  const M=(f,sk)=>mat(f,false,sk,{ds:true});
  const legg=(geo,f,sk,px,py,pz,forelder=g)=>{ const m=new THREE.Mesh(geo,M(f,sk)); m.position.set(px,py,pz); m.castShadow=true; m.receiveShadow=true; forelder.add(m); return m; };
  // ledd: rett blokk (b x d), eller avkortet pyramide (4 sider, dreid 45°, så sidene står rett) når b2 er gitt (bare kvadratisk)
  const ledd=(l,y0,f,sk)=> l.b2==null
    ? legg(new THREE.BoxGeometry(l.b,l.h,l.d||l.b),f,sk,0,y0+l.h/2,0)
    : (m=>{ m.rotation.y=Math.PI/4; return m; })(legg(new THREE.CylinderGeometry(l.b2/Math.SQRT2,l.b/Math.SQRT2,l.h,4,1),f,sk,0,y0+l.h/2,0));
  let y0=0, front=null;
  (st.sokkel||[]).forEach(l=>{
    const stein=l.stein || (l.del==='trinn' ? 'trinn' : l.del==='bronseplate' ? 'bronse' : 'mørk');
    const [f,sk]=STEINFARGE[stein]||STEINFARGE['mørk'];
    ledd(l,y0,f,sk);
    if(l.front) front={y0, h:l.h, d:l.d||l.b};
    y0+=l.h;
  });
  // fronten (leddet med «front» i dataene): kronet riksvåpen (relieff) over innskriften, som på Frederik II
  if(front){ const zf=front.d/2+0.012;
    const skjold=legg(new THREE.CylinderGeometry(0.15,0.15,0.03,20),RELIEFF,PATINA_S,0,front.y0+front.h*0.58,zf); skjold.rotation.x=Math.PI/2; skjold.scale.set(1,1,1.42);
    legg(new THREE.BoxGeometry(0.2,0.07,0.03),RELIEFF,PATINA_S,0,front.y0+front.h*0.58+0.25,zf);            // krona
    legg(new THREE.BoxGeometry(0.46,0.05,0.01),GULL,[150,144,116],0,front.y0+front.h*0.22,zf-0.008);          // innskriften
  }
  const k=new THREE.Group(); k.position.y=y0; g.add(k);
  const del=(geo,px,py,pz,forelder=k)=>legg(geo,PATINA,PATINA_S,px,py,pz,forelder);
  const lem=(a,b,r1,r2,forelder=k)=>{ const d=b.clone().sub(a), L=d.length(); const m=del(new THREE.CylinderGeometry(r2,r1,L,16),(a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2,forelder);
    m.quaternion.setFromUnitVectors(V(0,1,0), d.normalize()); return m; };
  const kule=(r,p,sx=1,sy=1,sz=1,forelder=k)=>{ const m=del(new THREE.SphereGeometry(r,20,14),p.x,p.y,p.z,forelder); m.scale.set(sx,sy,sz); return m; };
  const hoyde=FIGUR[st.figur.form]({k,del,lem,kule});
  k.scale.setScalar(st.figur.h/hoyde);
  // retning: kompassgrader -> rotasjon om y (lokal +z = fram); verden: x = øst, -z = nord
  const b=(st.retning||0)*Math.PI/180; g.rotation.y=Math.atan2(Math.sin(b),-Math.cos(b));
  g.scale.setScalar(st.visningsskala||1);
  g.position.set(x,0,-y); g.userData={b:{navn:st.navn,adr:st.sted||'',tekst:st.tekst}}; flatGruppe(g); city.add(g);
});
})();
