import * as THREE from 'three';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { SENERE } from './tilstand.js';
import { BERORING, Q0, STIL, cam, gl2, kam, map, penselTex, renderer, scene } from './00_oppsett.js';
// måling per bilde (verktoy/flyt_maal.mjs, tast d): ms brukt på oppdater(), speilpasset og skyggekartet i dette bildet
const MAALT={oppdater:0, speil:0, skygge:0};
window.__pt={scene:0, blekk:0, fxaa:0, kall:0, tri:0, skygge:0, maal:false, minTex:false};
// window.__maal: true = gl.finish etter hvert pass (tast m); 'les' = les én piksel, så tida tar med alt GPU-en har igjen (programvare-GPU)
const _px1=new Uint8Array(4);
function maalVent(){ const m=window.__maal; if(!m) return; if(m!=='les'){ gl2.finish(); return; }
  const rb=gl2.getParameter(gl2.READ_FRAMEBUFFER_BINDING); gl2.bindFramebuffer(gl2.READ_FRAMEBUFFER,null); gl2.readPixels(0,0,1,1,gl2.RGBA,gl2.UNSIGNED_BYTE,_px1); gl2.bindFramebuffer(gl2.READ_FRAMEBUFFER,rb); }
{ const sr=renderer.shadowMap.render.bind(renderer.shadowMap); renderer.shadowMap.render=(l,s,c)=>{ if(!SENERE.sun.shadow.needsUpdate) return sr(l,s,c); const t=performance.now(); sr(l,s,c); maalVent(); MAALT.skygge+=performance.now()-t; }; }
// ---- etterbehandling: blekkstrek rundt alle former og skygge i hjørner, som i tegningen ----
const post=(()=>{
  let W=2, H=2, skala=1;
  const rt=new THREE.WebGLRenderTarget(2,2,{samples: (BERORING && devicePixelRatio>=1.5)?2:4,   /* (Vegar: «refresh-raten + oppløsningen») maskin: alltid 4x MSAA */ type:THREE.HalfFloatType});
  rt.depthTexture=new THREE.DepthTexture(2,2); rt.depthTexture.type=THREE.UnsignedIntType;
  // minimum-dybden til streken: R32F i samme oppløsning som 3D-passet; uten flyttallsmål (svært gamle nettlesere) regnes den i streken som før
  const MIN_TEX=renderer.extensions.has('EXT_color_buffer_float') && !Q0.get('mintex0');
  const rtM=new THREE.WebGLRenderTarget(2,2,{type:THREE.FloatType, format:THREE.RedFormat, minFilter:THREE.NearestFilter, magFilter:THREE.NearestFilter, depthBuffer:false, generateMipmaps:false});
  const mM=new THREE.ShaderMaterial({ uniforms:{tDep:{value:rt.depthTexture}, res:{value:new THREE.Vector2(2,2)}},
    vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
    fragmentShader:`uniform sampler2D tDep; uniform vec2 res; varying vec2 vUv;
      void main(){ float a=texture2D(tDep,vUv).x, b=texture2D(tDep,vUv+vec2(1.,0.)/res).x, c=texture2D(tDep,vUv+vec2(0.,1.)/res).x; gl_FragColor=vec4(min(a,min(b,c)),0.,0.,1.); }` });
  const qM=new THREE.Mesh(new THREE.PlaneGeometry(2,2),mM); qM.frustumCulled=false; const msc=new THREE.Scene(); msc.add(qM);
  const m=new THREE.ShaderMaterial({ defines: MIN_TEX ? {MIN_TEX:1} : {},
    uniforms:{uNatt:{value:0}, tMin:{value:rtM.texture}, tCol:{value:rt.texture}, tDep:{value:rt.depthTexture}, res:{value:new THREE.Vector2(2,2)}, mpp:{value:1}, span:{value:8000}, naer:{value:1}, fjern:{value:10000}, px:{value:1}, tilt:{value:0}, aoN:{value:14}, ssN:{value:1}, tid:{value:0}, sk:{value:1}, dpr:{value:1}, invPV:{value:new THREE.Matrix4()}, blekk:{value:new THREE.Color(0x24211f)}, tPensel:{value:penselTex}, uPensel:{value:STIL.pensel}, uKorn:{value:STIL.korn}, uVignett:{value:STIL.vignett}, uKurve:{value:STIL.kurve}, uSky:{value:STIL.sky}, uPunch:{value:Q0.get('punch')==='0'?0:+(Q0.get('punch')||1)}, uMetning:{value:+(Q0.get('metning')||0.93)}},
    vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
    fragmentShader:`uniform sampler2D tCol, tDep, tPensel; uniform vec2 res; uniform float uKurve, uPunch, uMetning, uNatt; uniform float mpp, span, px, tilt, aoN, tid, sk, dpr, ssN, naer, fjern, uPensel, uKorn, uVignett, uSky; uniform mat4 invPV; uniform vec3 blekk;
 varying vec2 vUv;
      // dybde i meter langs synsretningen (perspektiv: dybdebufferet lineariseres med kartets nær/fjern-plan)
      float D(vec2 o){ float d=texture2D(tDep, vUv+o/res).x*2.-1.; return (2.*naer*fjern/(fjern+naer-d*(fjern-naer)))*span; }
      // dybde med lukking: hårfine sprekker mellom takflater (1 px) lukkes, så de ikke blir prikker i streken
      #ifdef MIN_TEX
      // minimum av pikselen og naboen til høyre og over er regnet i et eget pass (tMin, rå dybde): én oppslag i stedet for tre, samme tall
      uniform sampler2D tMin;
      float Dm(vec2 o){ float d=texture2D(tMin, vUv+o/res).x*2.-1.; return (2.*naer*fjern/(fjern+naer-d*(fjern-naer)))*span; }
      #else
      float Dm(vec2 o){ return min(D(o), min(D(o+vec2(1.,0.)), D(o+vec2(0.,1.)))); }
      #endif
      // strekstyrke ved en forskyvning (piksler): knekker (inner) og dybdesprang (silhuett)
      float strekVed(vec2 o, float s1, float s2, float mpp){
        float ec=Dm(o);
        float a1=Dm(o+vec2(-s1,0.)), b1=Dm(o+vec2(s1,0.)), c1=Dm(o+vec2(0.,s1)), d1=Dm(o+vec2(0.,-s1));
        float a2=Dm(o+vec2(-s2,0.)), b2=Dm(o+vec2(s2,0.)), c2=Dm(o+vec2(0.,s2)), d2=Dm(o+vec2(0.,-s2));
        float L1=max(abs(a1+b1-2.*ec), abs(c1+d1-2.*ec))/(mpp*s1);
        float L2=max(abs(a2+b2-2.*ec), abs(c2+d2-2.*ec))/(mpp*s2);
        return max(smoothstep(0.34,0.85,L1)*0.78, smoothstep(3.5,7.0,L2));
      }
      float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
      float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      // filmkurve (teknikk 15): toppen bøyes av over KNE (230/255) mot TAK (241/255), alt under står urørt, så husfargene (fasit) ikke flytter seg.
      // Målet er satt i skjermverdier (99,9-persentilen i hjemmevisningen 222–243, ingen piksel over ca. 240), men dette passet skriver
      // lineært til et sRGB-mål (skjermkoden legges på av grafikkortet), så knekk og tak står her som lineære verdier: 230/255 → 0,787, 241/255 → 0,880.
      const float KNE=0.787, TAK=0.880;
      const float PUNCH_METNING=0.45, PUNCH_KONTRAST=0.18;
      vec3 kurve(vec3 c){ vec3 t=max(c-KNE,0.); vec3 b=KNE+(TAK-KNE)*(1.-exp(-t/(TAK-KNE))); return mix(c, b, step(KNE,c)*uKurve); }
      // punch (Vegar: «før» så mer imponerende ut): i skjermrom, etter fargekoden. Metningen løftes mest der den er svak
      // (vibrance), så fargetonen står og de dømte husfargene beholder kuløren; og en svak S-kurve gir kontrast rundt midten. Papiret rundt får ingenting.
      vec3 punch(vec3 c, float p){ if(p<=0.) return c; float l=dot(c,vec3(0.2126,0.7152,0.0722)); float mx=max(c.r,max(c.g,c.b)), mn=min(c.r,min(c.g,c.b));
        c=clamp(mix(vec3(l), c, 1.+p*PUNCH_METNING*(1.-(mx-mn))),0.,1.); return mix(c, c*c*(3.-2.*c), p*PUNCH_KONTRAST); }
      void main(){
        vec3 col=texture2D(tCol,vUv).rgb;
        // miniatyr-effekt: myk uskarphet øverst og nederst i bildet (sterkest i introen)
        float tb=tilt*smoothstep(0.16,0.5,abs(vUv.y-0.52));
        if(tb>0.01){ vec3 acc=col; float wsum=1.;
          for(int i=0;i<12;i++){ float a=float(i)*2.39996; float r=tb*7.*sqrt((float(i)+.5)/12.);
            acc+=texture2D(tCol, vUv+vec2(cos(a),sin(a))*r/res).rgb; wsum+=1.; }
          col=acc/wsum; }
        float zc=D(vec2(0.));
        if(texture2D(tDep,vUv).x>0.99999){ gl_FragColor=vec4(col,1.);   // bakgrunn (ingenting tegnet): dybden står på fjernplanet
          #include <colorspace_fragment>
          gl_FragColor.rgb=kurve(gl_FragColor.rgb);
          return; }
        // verdensposisjon for pikselen: støyen i streken forankres i byen, så den ikke kryper når kameraet beveger seg
        vec4 wp4=invPV*vec4(vUv*2.-1., texture2D(tDep,vUv).x*2.-1., 1.); vec2 wxz=wp4.xz/wp4.w;
        float zl=D(vec2(-px,0.)), zr=D(vec2(px,0.)), zu=D(vec2(0.,px)), zd=D(vec2(0.,-px));
        // ---- organisk blekkstrek ----
        // tykkelse etter zoom: tynn i oversikten, fyldigere tett på
        // strekbredden regnes i skjermpunkter (CSS-px), så den er lik på alle skjermer og i både rask og skarp tegning
        float mppC=mpp*sk/dpr;                              // meter per skjermpunkt
        float wi=clamp(0.22/mppC, 0.65, 1.5);               // tynn i oversikten, fyldigere tett på
        float s1=max(1.,floor(wi*dpr*sk*0.75+0.5)), s2=max(s1+1.,floor(wi*dpr*sk*1.2+0.5)); // hele piksler: ingen falske linjer på flat mark
        // lavfrekvent skjelving (bølgelengde ca. 40 px), som en tusj som ikke følger linjalen
        float fq=1./(40.*mpp);
        vec2 wob=vec2(vn(wxz*fq)-0.5, vn(wxz*fq+17.3)-0.5)*0.5*px*uPensel; // skjelving bare i stil c; stikkstreken (a/b) er rett
        float ec=Dm(wob);
        float a1=Dm(wob+vec2(-s1,0.)), b1=Dm(wob+vec2(s1,0.)), c1=Dm(wob+vec2(0.,s1)), d1=Dm(wob+vec2(0.,-s1));
        float a2=Dm(wob+vec2(-s2,0.)), b2=Dm(wob+vec2(s2,0.)), c2=Dm(wob+vec2(0.,s2)), d2=Dm(wob+vec2(0.,-s2));
        // sprekkpiksel: dypere enn alle naboene -> vis naboenes farge i stedet for det som ligger bak
        if(zc>min(min(zl,zr),min(zu,zd))+0.4 && zc>max(max(zl,zr),max(zu,zd))-0.05){
          col=0.25*(texture2D(tCol,vUv+vec2(px,0.)/res).rgb+texture2D(tCol,vUv-vec2(px,0.)/res).rgb+texture2D(tCol,vUv+vec2(0.,px)/res).rgb+texture2D(tCol,vUv-vec2(0.,px)/res).rgb); }
        // kantutjevnet strek: snitt av fire forskjøvne prøver (roterte rutenett), så skrå linjer blir glatte og ikke trappete
        float ink;
        if(ssN>1.5){ ink=0.25*(strekVed(wob+vec2(0.375,-0.125)*2.,s1,s2,mpp)+strekVed(wob+vec2(-0.125,-0.375)*2.,s1,s2,mpp)
                              +strekVed(wob+vec2(-0.375,0.125)*2.,s1,s2,mpp)+strekVed(wob+vec2(0.125,0.375)*2.,s1,s2,mpp)); ink=smoothstep(0.,0.85,ink); }
        else ink=strekVed(wob,s1,s2,mpp);
        // trykkvariasjon og små brudd langs streken
        // trykk og brudd fra penselpakken: teksturen leses i byens koordinater, så strøket står stille når kameraet går
        float pen=texture2D(tPensel, wxz*fq*0.55).r;
        float pen2=texture2D(tPensel, wxz*fq*1.7+vec2(0.37,0.61)).r;
        ink*=mix(1., 0.62+0.38*pen2, uPensel);
        float brudd=smoothstep(0.36,0.52, pen);
        ink*=mix(1., mix(0.10,1.,brudd), uPensel);
        // terrenget (alfa 0) får ikke strek i egne knekker, men kanten mot hus, trær og vann får strek
        float aC=texture2D(tCol,vUv).a;
        float aN=max(max(texture2D(tCol,vUv+(wob+vec2(s2,0.))/res).a,texture2D(tCol,vUv+(wob-vec2(s2,0.))/res).a),max(texture2D(tCol,vUv+(wob+vec2(0.,s2))/res).a,texture2D(tCol,vUv+(wob-vec2(0.,s2))/res).a));
        ink*=max(aC,aN);
        // strekfargen er en mørk versjon av flaten som ligger foran (som i tegningen), ikke ren svart
        vec3 cn=texture2D(tCol,vUv+wob/res).rgb; float zn=ec;
        if(a2<zn){ zn=a2; cn=texture2D(tCol,vUv+(wob+vec2(-s2,0.))/res).rgb; }
        if(b2<zn){ zn=b2; cn=texture2D(tCol,vUv+(wob+vec2(s2,0.))/res).rgb; }
        if(c2<zn){ zn=c2; cn=texture2D(tCol,vUv+(wob+vec2(0.,s2))/res).rgb; }
        if(d2<zn){ zn=d2; cn=texture2D(tCol,vUv+(wob+vec2(0.,-s2))/res).rgb; }
        vec3 blekkF=mix(blekk, cn*0.38, 0.65); // strekfarge nær flatens egen mørke tone: ingen svart halo
        // skygge i hjørner og der hus møter bakken (planbevisst, så flat bakke ikke mørkner)
        float gX=abs(zr-zc)<abs(zc-zl)? zr-zc : zc-zl; float gY=abs(zu-zc)<abs(zc-zd)? zu-zc : zc-zd;
        float R=clamp(2.4/mpp, 4., 48.); float ao=0.; float j=h(gl_FragCoord.xy)*6.2831;
        for(int i=0;i<14;i++){
          if(float(i)>=aoN) break;
          float a=float(i)*2.39996+j; float r=R*sqrt((float(i)+.5)/aoN);
          vec2 o=vec2(cos(a),sin(a))*r;
          float zs=D(o); float zp=zc+(gX*o.x+gY*o.y)/px;
          float dz=zp-zs;
          ao+=smoothstep(0.12,0.7,dz)*(1.-smoothstep(3.5,7.,dz));
        }
        ao/=max(aoN,1.);
        col*=mix(vec3(1.),vec3(0.60,0.645,0.76),ao*aC); // hjørneskygge i himmeltone, ikke grå
        // skyskygger som driver sakte over byen
        vec2 cp=wxz*0.0035+vec2(tid*0.006,tid*0.0025);
        float sky=vn(cp)*0.6+vn(cp*2.3+3.1)*0.3+vn(cp*5.1-1.7)*0.1;
        col*=1.-0.09*smoothstep(0.52,0.78,sky)*uSky;
        col=mix(col, blekkF, ink*0.9*(1.-tb*0.8));
        // kartet toner ut i papiret rundt Gamlebyen, så kantene av kartdataene aldri synes
        float rr=length((wxz-vec2(10.,0.))*vec2(0.85,1.0));
        col=mix(col, mix(vec3(0.925,0.915,0.885), vec3(0.030,0.036,0.060), uNatt/0.9), smoothstep(380.,600.,rr));   // om kvelden (23_vaer) er papiret også mørkt
        // svak vignett, som papir under lampe
        vec2 vv=vUv-0.5; col*=1.-0.10*pow(clamp(length(vv)*1.35,0.,1.),2.2)*uVignett;
        // papirkorn
        col*=1.+(0.03*h(floor(gl_FragCoord.xy*0.5))-0.015)*uKorn;
        gl_FragColor=vec4(col,1.);
        #include <colorspace_fragment>
        gl_FragColor.rgb=punch(gl_FragColor.rgb, uPunch*(1.-smoothstep(380.,600.,rr)));
        // metning ned 7 % (Vegar: «litt glorete»): etter punchen, i skjermrom, bare på kartet (papiret rundt står). ?metning=1 gir urørt.
        { float lm=dot(gl_FragColor.rgb,vec3(0.2126,0.7152,0.0722)); gl_FragColor.rgb=mix(vec3(lm), gl_FragColor.rgb, uMetning*(1.-smoothstep(380.,600.,rr))+smoothstep(380.,600.,rr)); }
        gl_FragColor.rgb=kurve(gl_FragColor.rgb);
      }`
  });
  const q=new THREE.Mesh(new THREE.PlaneGeometry(2,2),m); q.frustumCulled=false;
  // kantutjevning til slutt (FXAA): blekkstreken regnes fra dybden og får ellers trappetrinn
  const rtF=new THREE.WebGLRenderTarget(2,2); rtF.texture.colorSpace=THREE.SRGBColorSpace;
  const fx=new THREE.ShaderMaterial({ uniforms:{ tDiffuse:{value:rtF.texture}, resolution:{value:new THREE.Vector2(0.5,0.5)} },
    vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
    fragmentShader:FXAAShader.fragmentShader.replace(/\}\s*$/, '  #include <colorspace_fragment>\n}') });
  const fq=new THREE.Mesh(new THREE.PlaneGeometry(2,2),fx); fq.frustumCulled=false; const fs=new THREE.Scene(); fs.add(fq);
  const ps=new THREE.Scene(); ps.add(q); const pc=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
  return {
    setAO(n){ m.uniforms.aoN.value=n; },
    msaa(n){ rt.samples=n; rt.dispose(); },   // kantutjevning i 3D-passet av/på (feilsøking: tast n)
    samples(){ return rt.samples; },
    setSS(n){ m.uniforms.ssN.value=n; },
    size(){ const w=renderer.domElement.width, h=renderer.domElement.height; W=w; H=h; SENERE.beregnSkala(); this.settSkala(skala,true); rtF.setSize(w,h); fx.uniforms.resolution.value.set(1/w,1/h); },
    settNatt(v){ m.uniforms.uNatt.value=v; },   // kvelden (23_vaer)
    settSkala(s,tving){ if(!tving && Math.abs(s-skala)<0.02) return; skala=s; const w=Math.max(2,Math.round(W*s)), h=Math.max(2,Math.round(H*s)); rt.setSize(w,h); m.uniforms.res.value.set(w,h); rtM.setSize(w,h); mM.uniforms.res.value.set(w,h); try{ SENERE.waterMat.uniforms.res.value.set(w,h); }catch(_){} }, // vannet slår opp speilet i samme pikselrom som bildet det tegnes i
    skala(){ return skala; },
    render(){ const u=m.uniforms; u.mpp.value=kam.mpp*innerWidth/u.res.value.x; u.span.value=kam.mpp; u.naer.value=kam.naer; u.fjern.value=kam.fjern; u.px.value=Math.max(1.,renderer.getPixelRatio()*skala*0.9); u.sk.value=skala; u.dpr.value=renderer.getPixelRatio(); u.tid.value=performance.now()/1000; u.invPV.value.multiplyMatrices(cam.projectionMatrix,cam.matrixWorldInverse).invert(); u.tilt.value=SENERE.introTilt(); // miniatyr-uskarphet bare i introen
      // måling (tast m i feilsøkingsruta): gl.finish() etter hvert pass gir ekte GPU-tid per pass, ikke bare CPU-tid
      const maal=!!window.__maal, fin=maalVent, skyggeNaa=SENERE.sun.shadow.needsUpdate;
      const _t0=performance.now(); renderer.setRenderTarget(rt); renderer.render(scene,cam); const kall=renderer.info.render.calls, tri=renderer.info.render.triangles; fin(); const _t1=performance.now();
      if(MIN_TEX){ renderer.setRenderTarget(rtM); renderer.render(msc,pc); }
      renderer.setRenderTarget(rtF); renderer.render(ps,pc); fin(); const _t2=performance.now();
      renderer.setRenderTarget(null); renderer.render(fs,pc); fin(); const _t3=performance.now();
      const P=window.__pt; P.scene=_t1-_t0; P.blekk=_t2-_t1; P.fxaa=_t3-_t2; P.kall=kall; P.tri=tri; P.skygge=skyggeNaa?1:0; P.maal=maal; P.minTex=MIN_TEX; }   // samme objekt hvert bilde
  };
})();

// koordinater: x = øst, z = -nord
const V = (p)=> new THREE.Vector2(p[0], p[1]);
// lerretet har endret størrelse: målene til etterbehandlingen følger (fra 00, der post ennå ikke fantes)
function fit(){ post.size(); }
map.on('resize',fit);

export { MAALT, V, maalVent, post };
