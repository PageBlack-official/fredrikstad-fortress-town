// ---- brygger (27.10): fergeleiet, gjestebrygga i Toldbodgaten, Isegran og båtplassene langs Glomma, fra data/brygger.json
// (verktoy/brygger.py: OSM rettet mot ortofoto 2024 og målt for hånd). Husstilen som broene: treplanker i flat farge med mørke
// skjøter på tvers, blekkstreken kommer fra etterbehandlingen. Faste brygger står på stolper ca. 1 m over vannet, flytebrygger
// ligger lavt (ca. 0,4 m) som en ponton uten stolper, utriggerne er smale bommer på vannet. Bryggene kaster skygge og står
// oppå vannflaten (y = 0,15); vannets skum ligger under dem. Et mykt mørke på vannet rundt hver brygge (kontaktskyggen fra
// husene) gir skyggen der vannet selv ikke tar kastskygge. Skjulte brygger (rettelse «skjul») tegnes ikke.
{
  const VANN_Y=0.15, PLANKE=0.9, STOLPE_AVSTAND=2.6;
  const FARGE={ tre:[[150,112,78],[96,70,48]], metall:[[168,170,168],[92,94,96]], plast:[[218,186,78],[140,112,40]] };
  const T_DEKK={ fast:0.28, flytebrygge:0.42, utrigger:0.32 };   // dekket for faste brygger; flytebrygga og bommen er pontonen helt ned i vannet
  const g=new THREE.Group(); g.name='brygger';
  const mork=f=>mat((FARGE[f]||FARGE.tre)[1],false), lys=f=>mat((FARGE[f]||FARGE.tre)[0],false);
  // én kloss (lengde langs retningen v i modellplanet), sentrert i (x,y), mellom høydene y0 og y1
  const kloss=(x,y,v,lengde,bredde,y0,y1,m)=>{ const k=new THREE.Mesh(new THREE.BoxGeometry(lengde,y1-y0,bredde),m);
    k.position.set(x,(y0+y1)/2,-y); k.rotation.y=v; k.castShadow=k.receiveShadow=true; g.add(k); return k; };
  const kontakt={pos:[], alfa:[]};
  (DATA.brygger||[]).forEach(b=>{
    if(b.skjul || !b.p || b.p.length<3) return;
    const topp=VANN_Y+b.z, t=b.typ==='fast' ? T_DEKK.fast : topp-VANN_Y+0.1, bunn=topp-t;
    // dekket (fast) eller pontonen (flytebrygge, utrigger): omrisset ekstrudert, plant oppå
    const geo=new THREE.ExtrudeGeometry(polyShape(b.p),{depth:t, bevelEnabled:false}); geo.rotateX(-Math.PI/2);
    const dekk=new THREE.Mesh(geo, lys(b.flate)); dekk.position.y=bunn; dekk.castShadow=dekk.receiveShadow=true; g.add(dekk);
    // planker: mørke skjøter på tvers av bryggas lange side, klippet mot omrisset (tre; metall og plast er glatte)
    const a=b.retning||0, ux=Math.cos(a), uy=Math.sin(a), vx=-uy, vy=ux;
    if(b.flate==='tre' && b.typ!=='utrigger'){
      const U=b.p.map(q=>q[0]*ux+q[1]*uy), V=b.p.map(q=>q[0]*vx+q[1]*vy), n=b.p.length;
      for(let s=Math.min(...U)+PLANKE/2; s<Math.max(...U); s+=PLANKE){
        const kr=[];
        for(let i=0;i<n;i++){ const j=(i+1)%n, di=U[i]-s, dj=U[j]-s; if((di<0)!==(dj<0)) kr.push(V[i]+(V[j]-V[i])*di/(di-dj)); }
        kr.sort((p,q)=>p-q);
        for(let k=0;k+1<kr.length;k+=2){ const L=kr[k+1]-kr[k]-0.08; if(L<0.2) continue; const w=(kr[k]+kr[k+1])/2;
          kloss(s*ux+w*vx, s*uy+w*vy, Math.atan2(vy,vx), L, 0.05, topp, topp+0.015, mork(b.flate)); }
      }
    }
    // stolper under faste brygger: langs kantene, litt inn fra kanten, ned i vannet
    if(b.typ==='fast'){
      let areal=0; for(let i=0;i<b.p.length;i++){ const p=b.p[i], q=b.p[(i+1)%b.p.length]; areal+=p[0]*q[1]-q[0]*p[1]; }
      const inn=areal>0 ? 1 : -1;   // mot klokka: innsiden er til venstre for kanten
      for(let i=0;i<b.p.length;i++){ const p=b.p[i], q=b.p[(i+1)%b.p.length], dx=q[0]-p[0], dy=q[1]-p[1], L=Math.hypot(dx,dy); if(L<0.8) continue;
        const nx=-dy/L*inn*0.16, ny=dx/L*inn*0.16, m=Math.max(1,Math.round(L/STOLPE_AVSTAND));
        for(let k=0;k<m;k++){ const f=Math.max(k/m, 0.12/L); const x=p[0]+dx*f+nx, y=p[1]+dy*f+ny;   // én stolpe i hvert hjørne og hver ~2,6 m
          kloss(x, y, Math.atan2(dy,dx), 0.2, 0.2, VANN_Y-0.3, bunn, mork(b.flate)); } }
    }
    // mørket på vannet rundt brygga (skygge og kontakt), bredere under de høye
    const f=fotBaand(b.p, b.typ==='fast' ? 1.1 : 0.55, VANN_Y+0.01); kontakt.pos.push(...f.pos); kontakt.alfa.push(...f.alfa);
  });
  flatGruppe(g); city.add(g);
  if(kontakt.pos.length){ const kg=new THREE.BufferGeometry(); kg.setAttribute('position', new THREE.Float32BufferAttribute(kontakt.pos,3)); kg.setAttribute('aAlfa', new THREE.Float32BufferAttribute(kontakt.alfa,1));
    const km=new THREE.Mesh(kg, kontaktMat); km.frustumCulled=false; km.renderOrder=1; city.add(km); }
  g.traverse(c=>c.layers.enable(1));   // speilingen i vannet (14_speilinger) tar med bryggene
}
