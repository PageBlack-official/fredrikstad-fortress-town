// ---- murer, plankegjerder og voller ----
const murer=new THREE.Group(); scene.add(murer);
function wallAlong(pts, hgt, thick, color, y0=0){
  const m=mat(color,false);
  for(let k=0;k<pts.length-1;k++){
    const a=pts[k], c=pts[k+1]; const dx=c[0]-a[0], dy=c[1]-a[1]; const len=Math.hypot(dx,dy); if(len<0.3) continue;
    const g=new THREE.BoxGeometry(len+thick*0.5,hgt,thick); const w=new THREE.Mesh(g,m);
    w.position.set((a[0]+c[0])/2, y0+hAt((a[0]+c[0])/2,(a[1]+c[1])/2)+hgt/2, -(a[1]+c[1])/2); w.rotation.y=Math.atan2(dy,dx); w.castShadow=w.receiveShadow=true; murer.add(w);
  }
}
(DATA.murer||[]).forEach(w=>{ if(w.t==='ruin') wallAlong(w.p, 3.6, 2.2, [196,188,174]); else wallAlong(w.p, w.t==='fence'?1.8:2.4, 0.6, w.t==='fence'?[206,192,170]:[214,206,192]); });
// gjerdelinjer som ligger i sporet til en teglmur (data/teglmurer.json), tegnes ikke: teglmuren erstatter dem (27.10, Kaserna)
const _iMur=(q)=>(DATA.teglmurer||[]).some(m=>{ const [a,c]=m.p, dx=c[0]-a[0], dy=c[1]-a[1], L2=dx*dx+dy*dy; const t=Math.max(0,Math.min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/L2)); return Math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)<3; });
// gjerder, murer og hekker sett i ortofoto 2024 (data/gjerder.json, verktoy/bakke.py gjerder 29.10): {typ, p, h}; gammel form (bare punkter) = gjerde
(DATA.gjerder||[]).forEach(g=>{ const p=Array.isArray(g)?g:g.p, typ=Array.isArray(g)?'gjerde':g.typ, h=Array.isArray(g)?1.5:(g.h||1.2);
  if(!Array.isArray(g)&&g.skjul) return; if(p.every(_iMur)) return;
  const art=Array.isArray(g)?'':(g.art||'');   // art fra Street View: stakitt hvitt, plankegjerde/-port grått tre, smijern mørkt og tynt
  const FG={stakitt:[236,234,226], plankegjerde:[150,136,120], plankeport:[150,136,120], smijern:[52,54,56], kjetting:[70,70,70], netting:[150,154,150], rekkverk:[200,200,196]};
  if(typ==='hekk') wallAlong(p, h, 0.9, [104,146,96]); else if(typ==='mur') wallAlong(p, h, 0.45, [206,198,184]); else wallAlong(p, h, art==='smijern'||art==='kjetting'?0.06:0.14, FG[art]||[196,184,166]); });
flatGruppe(murer);   // ett nett per murfarge
