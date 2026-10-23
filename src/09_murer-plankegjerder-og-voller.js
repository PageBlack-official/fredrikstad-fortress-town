// ---- murer, plankegjerder og voller ----
function wallAlong(pts, hgt, thick, color, y0=0){
  const m=mat(color,false);
  for(let k=0;k<pts.length-1;k++){
    const a=pts[k], c=pts[k+1]; const dx=c[0]-a[0], dy=c[1]-a[1]; const len=Math.hypot(dx,dy); if(len<0.3) continue;
    const g=new THREE.BoxGeometry(len+thick*0.5,hgt,thick); const w=new THREE.Mesh(g,m);
    w.position.set((a[0]+c[0])/2, y0+hAt((a[0]+c[0])/2,(a[1]+c[1])/2)+hgt/2, -(a[1]+c[1])/2); w.rotation.y=Math.atan2(dy,dx); w.castShadow=w.receiveShadow=true; scene.add(w);
    const e=new THREE.LineSegments(new THREE.EdgesGeometry(g),edgeMat); e.position.copy(w.position); e.rotation.copy(w.rotation); scene.add(e);
  }
}
(DATA.murer||[]).forEach(w=>{ if(w.t==='ruin') wallAlong(w.p, 3.6, 2.2, [196,188,174]); else wallAlong(w.p, w.t==='fence'?1.8:2.4, 0.6, w.t==='fence'?[206,192,170]:[214,206,192]); });
(DATA.gjerder||[]).forEach(p=>wallAlong(p, 1.5, 0.35, [196,184,166]));
