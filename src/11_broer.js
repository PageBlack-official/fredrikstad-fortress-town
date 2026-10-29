// ---- broer: tredekke, gitterrekkverk, pilarer; vindebro får heiseverk (to stolper, tverrbjelke, vippebommer) som i brosjyretegningen ----
(DATA.broer||[]).forEach((br,bi)=>{
  const g=new THREE.Group(); g.userData={i:-1-bi, b:{navn:br.navn||'Bro', tekst:br.tekst||'', nr:br.nr}, h:2};
  const tre=mat([150,112,78],false), mork=mat([96,70,48],false), stein=mat([176,170,156],false);
  const pts=br.p; const W=br.w; const yd=1.35;
  const kant=geo=>new THREE.LineSegments(new THREE.EdgesGeometry(geo,20),edgeMat);
  for(let k=0;k<pts.length-1;k++){
    const a=pts[k], c=pts[k+1]; const dx=c[0]-a[0], dy=c[1]-a[1]; const len=Math.hypot(dx,dy); if(len<0.5) continue;
    const ang=Math.atan2(dy,dx); const mx=(a[0]+c[0])/2, my=(a[1]+c[1])/2;
    // lokalt: x langs broa, z tvers (mot høyre sett i kjøreretning), y opp
    const place=(mesh,ox,oy,oz,rz=0,rx=0)=>{ mesh.position.set(mx+Math.cos(ang)*ox + Math.sin(ang)*oz, oy, -(my+Math.sin(ang)*ox - Math.cos(ang)*oz)); mesh.rotation.set(rx,ang,rz,'YXZ'); mesh.castShadow=mesh.receiveShadow=true; g.add(mesh); return mesh; };
    const L=len+0.8;
    const dekke=place(new THREE.Mesh(new THREE.BoxGeometry(L,0.35,W),tre),0,yd,0);
    const kd=kant(dekke.geometry); kd.position.copy(dekke.position); kd.rotation.copy(dekke.rotation); g.add(kd);
    // plankeskjøter som tynne mørke striper tvers over dekket
    for(let q=-L/2+0.6;q<L/2;q+=1.2) place(new THREE.Mesh(new THREE.BoxGeometry(0.06,0.03,W-0.1),mork),q,yd+0.19,0);
    // gitterrekkverk: topp- og midtlist, stolper, kryss i hvert fag
    const RH=1.25, n=Math.max(2,Math.round(L/2.2)), fag=L/n;
    [-1,1].forEach(s=>{ const z=s*(W/2-0.1);
      const topp=place(new THREE.Mesh(new THREE.BoxGeometry(L,0.12,0.12),mork),0,yd+RH,z); const kt=kant(topp.geometry); kt.position.copy(topp.position); kt.rotation.copy(topp.rotation); g.add(kt);
      place(new THREE.Mesh(new THREE.BoxGeometry(L,0.08,0.08),mork),0,yd+0.45,z);
      for(let q=0;q<=n;q++) place(new THREE.Mesh(new THREE.BoxGeometry(0.14,RH+0.1,0.14),mork),-L/2+fag*q,yd+RH/2,z);
      const dl=Math.hypot(fag,RH-0.4), v=Math.atan2(RH-0.4,fag);
      for(let q=0;q<n;q++){ const x=-L/2+fag*(q+0.5); place(new THREE.Mesh(new THREE.BoxGeometry(dl,0.05,0.05),mork),x,yd+0.45+(RH-0.4)/2,z,v); place(new THREE.Mesh(new THREE.BoxGeometry(dl,0.05,0.05),mork),x,yd+0.45+(RH-0.4)/2,z,-v); }
    });
    // pilarer i vannet
    const np=Math.max(1,Math.round(len/7)); for(let q=1;q<=np;q++){ const pil=place(new THREE.Mesh(new THREE.BoxGeometry(1.0,1.6,W*0.8),stein),-len/2+len*(q-0.5)/np,yd-1.0,0); const kp=kant(pil.geometry); kp.position.copy(pil.position); kp.rotation.copy(pil.rotation); g.add(kp); }
    // heiseverket: to stolper med tverrbjelke, og to vippebommer som peker skrått opp over broa
    if(br.vindebro && k===0){
      const PH=5.2, x0=-L/2+L*0.42;
      [-1,1].forEach(s=>{ const z=s*(W/2-0.05); const st=place(new THREE.Mesh(new THREE.BoxGeometry(0.3,PH,0.3),mork),x0,yd+PH/2,z); const ks=kant(st.geometry); ks.position.copy(st.position); ks.rotation.copy(st.rotation); g.add(ks);
        place(new THREE.Mesh(new THREE.BoxGeometry(0.25,0.25,0.25),mork),x0+0.6,yd+PH+0.1,z);
        const bom=place(new THREE.Mesh(new THREE.BoxGeometry(6.0,0.22,0.22),mork),x0+2.3,yd+PH+0.9,z,0.32); const kb=kant(bom.geometry); kb.position.copy(bom.position); kb.rotation.copy(bom.rotation); g.add(kb); });
      const tv=place(new THREE.Mesh(new THREE.BoxGeometry(0.25,0.25,W),mork),x0,yd+PH+0.05,0); const kv=kant(tv.geometry); kv.position.copy(tv.position); kv.rotation.copy(tv.rotation); g.add(kv);
      place(new THREE.Mesh(new THREE.BoxGeometry(0.2,0.2,W),mork),x0+2.3+2.8*Math.cos(0.32),yd+PH+0.9+2.8*Math.sin(0.32),0);
    }
  }
  flatGruppe(g); city.add(g);
});
// voller: tegnes nå som terreng (se festningsterrenget)
