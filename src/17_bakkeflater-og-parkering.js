// ---- bakkeflater og parkering (27.10): plenene (OSM, rettet mot ortofoto 2024), gresset i gårdsrommene slik ortofotoet viser det,
// flatene målt i ortofotoet (grus, heller, asfalt) og parkeringsplassene fra kommunens lag. Flate farger, tynn strek fra
// etterbehandlingen (høydesprang mellom flatene), ingen tekst på bakken. Skjulte objekter (rettelse «skjul») tegnes ikke.
{
  // én flat farge med svak flekk i stor skala, som plenene; tar kastskygge
  const flateMat=(rgb)=>medSkygge(new THREE.ShaderMaterial({
    uniforms:{ c1:{value:new THREE.Color(`rgb(${rgb[0]},${rgb[1]},${rgb[2]})`)} },
    vertexShader:`varying vec3 wp; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`uniform vec3 c1; varying vec3 wp;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      void main(){ float m=n(wp.xz*0.03)*0.6+n(wp.xz*0.12)*0.4; gl_FragColor=vec4(c1*(0.95+0.08*m),1.);
      #include <colorspace_fragment>
      }`
  }));
  // bed (bar jord) og brostein utenfor brosteinsflaten kommer fra ortofotoet (verktoy/bakke.py overflater, 29.10)
  const FARGE={ grus:[214,204,182], heller:[190,184,174], asfalt:[150,146,140], gress:[126,180,134], parkering:[160,157,152], bed:[132,108,86], brostein:[146,140,132] };
  const MAT={brostein:stoneMat}; const matFor=k=>MAT[k]||(MAT[k]=bakkelag(flateMat(FARGE[k]), k==='parkering'?BAKKELAG.parkering:BAKKELAG.flate, {asfalt:0,grus:1,heller:2,bed:3}[k]||0));   // lagene: src/03 (avvik A8)
  // flaten legges på terrenget (vollene og kaiene ligger på terrengnettet), aldri lavere enn y0
  // deler trekantene i g til lengste kant er under maks (midtpunktdeling), så de følger terrengnettet
  const delPaaTerreng=(g0, maks)=>{ const g=g0.index?g0.toNonIndexed():g0; let T=Array.from(g.attributes.position.array); let ut=[];
    for(let runde=0;runde<10;runde++){ let delt=false; ut=[];
      for(let k=0;k<T.length;k+=9){ const A=T.slice(k,k+3), B=T.slice(k+3,k+6), C=T.slice(k+6,k+9);
        const l=(p,q)=>Math.hypot(p[0]-q[0],p[2]-q[2]); const ab=l(A,B), bc=l(B,C), ca=l(C,A), m=Math.max(ab,bc,ca);
        if(m<=maks){ ut.push(...A,...B,...C); continue; } delt=true;
        const mid=(p,q)=>[(p[0]+q[0])/2,(p[1]+q[1])/2,(p[2]+q[2])/2];
        if(m===ab){ const M=mid(A,B); ut.push(...A,...M,...C, ...M,...B,...C); }
        else if(m===bc){ const M=mid(B,C); ut.push(...A,...B,...M, ...A,...M,...C); }
        else { const M=mid(C,A); ut.push(...A,...B,...M, ...M,...B,...C); } }
      T=ut; if(!delt) break; }
    const n=new THREE.BufferGeometry(); n.setAttribute('position', new THREE.Float32BufferAttribute(T,3)); return n; };
  const legg=(pts, y0, mat)=>{
    if(!pts || pts.length<3) return null;
    let g=new THREE.ShapeGeometry(polyShape(pts)); g.rotateX(-Math.PI/2);
    // på terrenget: trekantene deles til de er mindre enn terrengrutene, og hvert punkt får terrengnettets høyde (hTer, src/08),
    // så flaten ligger på nettet og ikke skjærer gjennom det (avvik A16)
    if(pts.some(q=>hTer(q[0],q[1])>0.05) || (()=>{ const P0=g.attributes.position; for(let i=0;i<P0.count;i++) if(hTer(P0.getX(i),-P0.getZ(i))>0.05) return true; return false; })())
      g=delPaaTerreng(g, TER?TER.g/2:1);
    const P=g.attributes.position; for(let i=0;i<P.count;i++){ const t=hTer(P.getX(i), -P.getZ(i)); P.setY(i, t>0.05 ? t+y0 : Math.max(y0, hAt(P.getX(i), -P.getZ(i))+y0)); }
    P.needsUpdate=true; g.computeVertexNormals();
    const m=new THREE.Mesh(g, mat); m.receiveShadow=true; scene.add(m); return m;
  };
  // plenene (flyttet hit fra 04)
  DATA.gront.forEach(g=>{ if(!g.skjul) flat(g.p,0.28,plenMat); });
  // gårdsrommene: målt gress (felt «gress») tegnes som polygoner; uten måling gjelder typen for hele gårdsrommet
  (DATA.gardsrom||[]).forEach(g=>{ if(g.skjul) return;
    if(g.gress) g.gress.forEach(p=>flat(p,0.3,plenMat)); else if(g.typ==='gress') flat(g.p,0.3,plenMat); });
  // flater målt i ortofotoet
  (DATA.flater||[]).forEach(f=>{ if(!f.skjul && FARGE[f.typ] && !(f.typ==='brostein' && alleIBrostein(f.p))) legg(f.p, f.typ==='gress'?0.28:f.typ==='brostein'?0.05:0.09, f.typ==='gress'?plenMat:matFor(f.typ)); });
  // oppmerkede parkeringsfelt (kommunens lag, verktoy/bakke.py parkeringsfelt): hvite streker på tvers av raden, oppmerket+1 stk
  { const strek=new THREE.MeshBasicMaterial({color:0xf4f2ec}); const G=new THREE.Group(); scene.add(G);
    (DATA.flater||[]).forEach(f=>{ if(f.skjul || !f.linje || !f.oppmerket) return;
      const [a,c]=f.linje, dx=c[0]-a[0], dy=c[1]-a[1], L=Math.hypot(dx,dy), ang=Math.atan2(dy,dx);
      for(let i=0;i<=f.oppmerket;i++){ const t=i/f.oppmerket, x=a[0]+dx*t, y=a[1]+dy*t;
        const m=new THREE.Mesh(new THREE.PlaneGeometry(0.12, f.bredde*0.9), strek); m.rotation.x=-Math.PI/2; m.rotation.z=ang;
        m.position.set(x, hAt(x,y)+0.14, -y); G.add(m); } });
    flatGruppe(G); }
  // parkering: bare plasser med målt flate; punktene (uten flate) finnes i dataene, men tegnes ikke på bakken
  // Er raden målt som flate i ortofotoet (flater[].parkering_id, verktoy/bakke.py parkeringsfelt), er det flatens type som gjelder
  // (brostein i Gamlebyen) og bare oppmerkingen tegnes: den glatte parkeringsflaten oppå brosteinen var «noe rart foran huset» (avvik A3, 02.11)
  const maaltFlate=new Set((DATA.flater||[]).filter(f=>!f.skjul && f.parkering_id).map(f=>f.parkering_id));
  (DATA.parkering||[]).forEach(p=>{ if(!p.skjul && p.p && !maaltFlate.has(p.id)) legg(p.p, 0.12, matFor('parkering')); });
}
