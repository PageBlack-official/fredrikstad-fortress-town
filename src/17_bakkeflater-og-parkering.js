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
  const FARGE={ grus:[214,204,182], heller:[190,184,174], asfalt:[150,146,140], gress:[126,180,134], parkering:[160,157,152] };
  const MAT={}; const matFor=k=>MAT[k]||(MAT[k]=flateMat(FARGE[k]));
  // flaten legges på terrenget (vollene og kaiene ligger på terrengnettet), aldri lavere enn y0
  const legg=(pts, y0, mat)=>{
    if(!pts || pts.length<3) return null;
    const g=new THREE.ShapeGeometry(polyShape(pts)); g.rotateX(-Math.PI/2);
    const P=g.attributes.position; for(let i=0;i<P.count;i++) P.setY(i, Math.max(y0, hAt(P.getX(i), -P.getZ(i))+y0));
    P.needsUpdate=true; g.computeVertexNormals();
    const m=new THREE.Mesh(g, mat); m.receiveShadow=true; scene.add(m); return m;
  };
  // plenene (flyttet hit fra 04)
  DATA.gront.forEach(g=>{ if(!g.skjul) flat(g.p,0.28,plenMat); });
  // gårdsrommene: målt gress (felt «gress») tegnes som polygoner; uten måling gjelder typen for hele gårdsrommet
  (DATA.gardsrom||[]).forEach(g=>{ if(g.skjul) return;
    if(g.gress) g.gress.forEach(p=>flat(p,0.3,plenMat)); else if(g.typ==='gress') flat(g.p,0.3,plenMat); });
  // flater målt i ortofotoet
  (DATA.flater||[]).forEach(f=>{ if(!f.skjul && FARGE[f.typ]) legg(f.p, f.typ==='gress'?0.28:0.09, f.typ==='gress'?plenMat:matFor(f.typ)); });
  // parkering: bare plasser med målt flate; punktene (uten flate) finnes i dataene, men tegnes ikke på bakken
  (DATA.parkering||[]).forEach(p=>{ if(!p.skjul && p.p) legg(p.p, 0.12, matFor('parkering')); });
}
