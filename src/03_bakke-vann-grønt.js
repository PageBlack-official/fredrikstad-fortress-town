// ---- bakke, vann, grønt ----
const ground = new THREE.Mesh(new THREE.PlaneGeometry(6000,6000), new THREE.MeshBasicMaterial({color:0xefece4}));
ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);

function polyShape(pts){
  const s = new THREE.Shape(pts.map(p=>new THREE.Vector2(p[0], p[1])));
  return s;
}
function flat(pts, y, mat){
  if (pts.length<3) return null;
  const g = new THREE.ShapeGeometry(polyShape(pts));
  g.rotateX(-Math.PI/2); // (x,y)->(x,0,-y)
  const m = new THREE.Mesh(g, mat); m.position.y=y; m.receiveShadow=true; scene.add(m); return m;
}
// vann med levende overflate: malt blått som trykket, lysere grunt vann mot land, skumkant langs strendene og
// en tynn ring litt ute (som Townscaper), Vegars penselstrøk svakt over, og myke speilinger av hus og trær.
// Kanttypen kommer fra data (data/vann.json «kant», målt mot ortofoto 2024 i verktoy/vann.py, bakt inn i vannfeltets g-kanal):
// naturlig kant skyller inn med skum, kai og mur står rett og rolig
const VF = DATA.vannfelt || null;
const waterMat = new THREE.ShaderMaterial({
  uniforms:{t:{value:0}, strek:{value:null}, c1:{value:new THREE.Color('rgb(150,212,224)')}, c2:{value:new THREE.Color('rgb(112,186,206)')}, hi:{value:new THREE.Color(0xf4fbf8)},
    grunt:{value:new THREE.Color('rgb(190,230,230)')}, skum:{value:new THREE.Color('rgb(250,252,247)')}, fjern:{value:new THREE.Color('rgb(206,228,226)')},
    tFelt:{value:null}, felt:{value:new THREE.Vector4(0,0,1,1)}, maks:{value:VF?VF.maks:42}, harFelt:{value:VF?1:0},
    tRefl:{value:null}, res:{value:new THREE.Vector2(2,2)}, reflStyrke:{value:0}, sentrum:{value:new THREE.Vector2(10,0)}},
  vertexShader:`varying vec3 wp; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`uniform float t, maks, harFelt, reflStyrke; uniform sampler2D strek, tFelt, tRefl; uniform vec3 c1,c2,hi,grunt,skum,fjern; uniform vec4 felt; uniform vec2 res, sentrum; varying vec3 wp;
  float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
  float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
  // tynn linje i avstand r fra land, bredde w (meter), aldri tynnere enn én piksel (ingen flimring)
  float linje(float d, float r, float w, float pm){ float ww=max(w,pm*1.2); return (1.-smoothstep(ww*0.5, ww*0.5+pm, abs(d-r))) * min(1., w/ww+0.25); }
  void main(){ vec2 p=wp.xz*0.02; float a=n(p*1.3+vec2(t*.05,t*.03)); float b=n(p*3.1-vec2(t*.07,0.));
    float pm=max(fwidth(wp.x),fwidth(wp.z));                       // meter per piksel her
    vec3 c=mix(c1,c2,a*.8);
    float s1=texture2D(strek, wp.xz/vec2(140.,110.)+vec2(t*.006,t*.002)).a; float s2=texture2D(strek, wp.xz/vec2(220.,180.)*vec2(-1.,1.)+vec2(-t*.004,t*.003)+.37).a;
    float s=max(s1*smoothstep(.25,.75,b), s2*.7*smoothstep(.3,.8,a));
    float d=maks, kai=0.;
    // vannfeltet (verktoy/vann.py): r = avstand til land, g = 1 der nærmeste strandkant er kai, mur eller brygge
    if(harFelt>0.5){ vec4 fe=texture2D(tFelt, vec2((wp.x-felt.x)/felt.z, (-wp.z-felt.y)/felt.w)); d=fe.r*maks; kai=smoothstep(0.25,0.75,fe.g); }
    // grunt vann nær land: lysere og litt grønnere, med myk overgang; ved kaia er det dypt helt inn
    float grunn=(1.-smoothstep(0.,24.,d))*(1.-0.75*kai);
    c=mix(c, grunt, grunn*grunn*0.62);
    // speilinger av hus og trær (rendret speilvendt i et eget lag), med rolig krusning
    if(reflStyrke>0.){ vec2 uv=gl_FragCoord.xy/res; vec2 kr=vec2(n(wp.xz*0.18+vec2(0.,t*0.35))-0.5, n(wp.xz*0.07-vec2(t*0.2,0.))-0.5)*vec2(0.004,0.010);
      vec4 r=texture2D(tRefl, uv+kr); float rk=reflStyrke*r.a*(0.75+0.25*b); c=mix(c, mix(c,r.rgb,0.55)*0.97, rk); }
    // penselstrøkene, svakere enn før og borte i skumkanten
    c=mix(c,hi,s*.42*(1.-grunn*0.7));
    // skumkant langs land: bølgete, pustende, minst ca. halvannen piksel bred så den holder i oversikten
    float wob=(n(wp.xz*0.32+vec2(t*0.11,-t*0.07))-0.5)*1.1+(n(wp.xz*1.4-vec2(t*0.17,0.))-0.5)*0.45;
    float bw=max(1.7, pm*2.0);
    float skumK=1.-smoothstep(bw*0.55, bw*0.55+max(pm,0.35), d+wob*0.55);
    // lys glorie like utenfor skummet
    float glor=(1.-smoothstep(0.,8.,d))*0.26;
    // tynn ring et stykke ute som puster sakte inn og ut
    float rr=4.6+0.9*sin(t*0.55+n(wp.xz*0.02)*6.28)+wob*0.9;
    float ring=linje(d, rr, 0.45, pm)*0.42*(1.-smoothstep(8.,12.,rr));
    // naturlig kant (gress, stein, siv): vannet skyller inn med skum, glorie og ringen som puster.
    // kai og mur: rett, rolig kant uten skum; en smal, mørk stripe der muren går ned i vannet og en svak lys refleks like utenfor
    float nat=1.-kai;
    c=mix(c, skum, max(max(skumK, ring), glor)*nat);
    float kw=max(0.55, pm*1.3);
    float murK=(1.-smoothstep(kw*0.5, kw*0.5+max(pm,0.25), d))*kai;
    float refl=(1.-smoothstep(0.,3.5,d))*smoothstep(kw*0.5,kw*1.2,d)*kai*0.16;
    c=mix(c, hi, refl);
    c=mix(c, c*vec3(0.62,0.70,0.74), murK*0.85);
    // langt ute: vannet blir lysere og roligere, så byen står i fokus
    float u=smoothstep(650.,1500.,length(wp.xz-vec2(sentrum.x,-sentrum.y)));
    c=mix(c, fjern, u*0.55);
    gl_FragColor=vec4(c,1.);
  #include <colorspace_fragment>
  }`
});
const vTex=texLoader.load(TEX_VANN); vTex.wrapS=vTex.wrapT=THREE.RepeatWrapping; waterMat.uniforms.strek.value=vTex;
if(VF){ const ft=texLoader.load(VF.png); ft.minFilter=THREE.LinearFilter; ft.magFilter=THREE.LinearFilter; ft.generateMipmaps=false; ft.colorSpace=THREE.NoColorSpace;
  waterMat.uniforms.tFelt.value=ft; waterMat.uniforms.felt.value.set(VF.x0,VF.y0,VF.w,VF.h); }
const waterLayer = [];
function flatH(pts, holes, y, mat){
  if (pts.length<3) return null;
  const sh=polyShape(pts); (holes||[]).forEach(hh=>{ if(hh.length>2) sh.holes.push(new THREE.Path(hh.map(p=>new THREE.Vector2(p[0],p[1])))); });
  const g=new THREE.ShapeGeometry(sh); g.rotateX(-Math.PI/2);
  const m=new THREE.Mesh(g,mat); m.position.y=y; m.receiveShadow=true; scene.add(m); return m;
}
DATA.vann.forEach(w=>{ const t=w.t; if (t.natural==='water'||t.water||['riverbank','dock','canal'].includes(t.waterway)) { const m=flatH(w.p,w.h,0.15,waterMat); if(m) waterLayer.push(m);} });


// elva Glomma rundt byen: fallback-stripe hvis data mangler
