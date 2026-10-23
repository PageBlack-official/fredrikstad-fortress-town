// ---- brostein i hele Gamlebyen ----
const stoneMat = new THREE.ShaderMaterial({
  uniforms:{ base:{value:new THREE.Color('rgb(146,140,132)')}, fuge:{value:new THREE.Color('rgb(96,92,88)')}, ang:{value:THREE.MathUtils.degToRad(DATA.gatevinkel||0)} },
  vertexShader:`varying vec3 wp; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`uniform vec3 base,fuge; uniform float ang; varying vec3 wp;
  float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
  float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
  void main(){
    float c0=cos(ang), s0=sin(ang); vec2 q=vec2(c0*wp.x+s0*wp.z, -s0*wp.x+c0*wp.z);
    // brostein lagt i rader langs gatenettet, forskjøvet annenhver rad
    vec2 S=vec2(1.05,0.8); vec2 p=q/S; float rad=floor(p.y); p.x+=fract(rad*0.5)*1.0+h(vec2(rad,3.))*0.3;
    vec2 id=floor(p), f=fract(p);
    vec2 e=min(f,1.-f)*S; float kant=min(e.x,e.y);
    float j=smoothstep(0.03,0.11,kant);
    float v=h(id);
    vec3 stein=base*(0.92+0.14*v);
    // sola øverst til venstre: lys kant oppe til venstre på hver stein
    float lys=smoothstep(0.30,0.0,f.x)*0.5+smoothstep(0.70,1.0,f.y)*0.5; stein*=1.0+0.07*lys*j;
    vec3 c=mix(fuge,stein,j);
    // akvarell-flekker i stor skala, som i tegningen
    float m=n(q*0.035)*0.6+n(q*0.11)*0.4; vec3 flekk=c*(0.93+0.13*m);
    float px=length(fwidth(p));
    vec3 fjern=mix(base,fuge,0.18)*(0.94+0.12*m);
    c=mix(flekk, fjern, smoothstep(0.22,0.6,px));
    gl_FragColor=vec4(c,1.);
    #include <colorspace_fragment>
  }`
});
medSkygge(stoneMat);
if (DATA.brostein){ const m=flat(DATA.brostein,0.05,stoneMat); }
const greenMat = new THREE.MeshLambertMaterial({color:0x9dcfa5});
const plenMat=new THREE.ShaderMaterial({
  uniforms:{ c1:{value:new THREE.Color('rgb(126,180,134)')} },
  vertexShader:`varying vec3 wp; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }`,
  fragmentShader:`uniform vec3 c1; varying vec3 wp;
    float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
    void main(){ float m=n(wp.xz*0.03)*0.6+n(wp.xz*0.12)*0.4; float gs=n(vec2(wp.x*0.55+wp.z*0.22, wp.z*1.9-wp.x*0.3))*0.6+n(vec2(wp.x*1.7, wp.z*4.3))*0.4; gl_FragColor=vec4(c1*(0.93+0.13*m)*(0.975+0.05*gs),1.);
    #include <colorspace_fragment>
    }`
});
medSkygge(plenMat);
DATA.gront.forEach(g=>{ const m=flat(g.p,0.28,plenMat); });
(DATA.gardsrom||[]).forEach(g=>{ if(g.typ==='gress') flat(g.p,0.3,plenMat); });
