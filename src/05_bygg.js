// ---- bygg ----
const city = new THREE.Group(); scene.add(city);
const edgeMat = new THREE.LineBasicMaterial({color:INK, transparent:true, opacity:.4}); edgeMat.visible=false; // blekkstreken tegnes i etterbehandlingen
const mats = new Map();
// to toner som i tegningen: flater som vender mot sola (alltid øverst til venstre i bildet) får full farge, resten skyggetonen
function mat(rgb, dim, sk, opt={}){
  const topp = (opt.vindu && !dim) ? Math.round(opt.vindu*2)/2 : 0;
  const key = rgb.join(',')+(dim?'d':'')+(sk?'s'+sk.join(','):'')+(opt.ds?'D':'')+'v'+topp;
  if(!mats.has(key)){
    const c=new THREE.Color(`rgb(${rgb[0]},${rgb[1]},${rgb[2]})`); if(dim) c.lerp(new THREE.Color(0xe4e2d8),.8);
    // skyggetonen hentes fra trykkfila når bygget har en; ellers samme forhold som tegningen bruker
    let s; if(sk && !dim){ s=new THREE.Color(`rgb(${sk[0]},${sk[1]},${sk[2]})`); } else { s=c.clone(); s.r*=0.72; s.g*=0.80; s.b*=0.80; }
    const m=new THREE.ShaderMaterial({
      lights:true,
      uniforms:Object.assign({ farge:{value:c}, skygge:{value:s}, topp:{value:topp}, uVask:{value:STIL.vask}, skravur:U_SKRAVUR }, THREE.UniformsUtils.clone(THREE.UniformsLib.lights)),
      vertexShader:GL_SOL_V+`varying vec3 vp; varying vec3 lp; varying vec3 wq; void main(){ lp=position; vec4 wp=modelMatrix*vec4(position,1.); wq=wp.xyz; vec4 mv=viewMatrix*wp; vp=mv.xyz; gl_Position=projectionMatrix*mv;
        vec3 wn=normalize(mat3(modelMatrix)*normal+vec3(0.,1e-5,0.));`+glSolVMain('wp','wn')+`}`,
      fragmentShader:GL_SOL_F+`uniform mat3 normalMatrix; uniform vec3 farge, skygge; uniform float topp, uVask; varying vec3 vp; varying vec3 lp; varying vec3 wq;
        float hh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
        float nn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hh(i),hh(i+vec2(1,0)),f.x),mix(hh(i+vec2(0,1)),hh(i+vec2(1,1)),f.x),f.y);}
        void main(){ vec3 n=normalize(normalMatrix*cross(dFdx(lp),dFdy(lp))); float d=dot(n,solRetning()); // normal fra lokale koordinater: presist, ingen stripete skygge
          // tegningens to toner (lys- og skyggetonen fra trykkfila) blandes av ekte lys: Lambert mot sola og kastskygger, myk overgang
          float lam=smoothstep(-0.12,0.52,d);
          float lit=lam*skyggeMask();
          float k=1.-lit;
          vec3 c = mix(skygge*KALD, farge*mix(vec3(1.),solFarge(),0.6), lit);
          // ---- malte flater: akvarellvask og penselstrøk, forankret i byen (ikke skjermen) ----
          vec3 nq=normalize(cross(dFdx(lp),dFdy(lp)));
          float vask=nn(wq.xz*0.045+wq.y*0.031)*0.62+nn(wq.xz*0.17+vec2(wq.y*0.23,3.1))*0.38;
          c*=1.-0.28*skravurMaske(wq, k);
          c*=1.+(vask-0.5)*0.09*uVask;   // akvarellvask, av i stil a/b
          float fwq=max(fwidth(wq.x)+fwidth(wq.z)+fwidth(wq.y),1e-4);
          float naerhet=1.-smoothstep(0.12,0.45,fwq);   // detaljer forsvinner på avstand
          if(abs(nq.y)<0.3){
            // vegg: vannrette penselstrøk
            vec2 tq=normalize(vec2(-nq.z,nq.x)); float uq=dot(wq.xz,tq);
            float strok=nn(vec2(uq*0.7, wq.y*6.0))*0.7+nn(vec2(uq*2.1, wq.y*15.))*0.3;
            c*=1.+(strok-0.5)*0.05*naerhet*uVask;
          } else if(abs(nq.y)<0.985){
            // tak: rader med takstein langs fallet, antydet, borte på avstand
            vec2 ned=normalize(nq.xz); vec2 lang=vec2(-ned.y,ned.x);
            float sF=dot(lp.xz,ned)/max(abs(nq.y),0.2)/0.38; float rF=dot(lp.xz,lang)/0.30;
            float rad=floor(sF); float fr=fract(sF);
            float fws=max(fwidth(sF),1e-4);
            float rLinje=1.-smoothstep(0.,fws*1.4,fr);
            float sk=fract(rF+0.5*mod(rad,2.)); float fwr=max(fwidth(rF),1e-4);
            float sLinje=(1.-smoothstep(0.,fwr*1.2,sk))*0.45;
            float vis=(1.-smoothstep(0.22,0.55,max(fws,fwr)))*naerhet;
            c*=1.-0.11*max(rLinje,sLinje)*vis; c*=1.-0.055*(1.-fr)*vis;
            c*=1.+(hh(vec2(floor(rF+0.5*mod(rad,2.)),rad))-0.5)*0.06*vis;
            // strøk langs fallet
            c*=1.+(nn(vec2(dot(wq.xz,lang)*1.3, dot(wq.xz,ned)*0.25))-0.5)*0.05;
          }
          if(topp>0.){
            vec3 nl=normalize(cross(dFdx(lp),dFdy(lp)));
            if(abs(nl.y)<0.3){
              vec2 t=normalize(vec2(-nl.z,nl.x)); float u=dot(lp.xz,t);
              float rad=floor(lp.y/3.0); float fy=lp.y-rad*3.0; float fu=mod(u,2.6);
              vec2 q=vec2(fu-1.3, fy-1.55); vec2 dd=abs(q)-vec2(0.42,0.68); float inn=max(dd.x,dd.y);
              float fw=max(fwidth(u),fwidth(lp.y));
              float ok = step(rad*3.0+2.35, topp-0.25);
              float ramme=(1.-smoothstep(0.,fw,inn))*ok;
              float glass=(1.-smoothstep(-0.08,-0.08+fw,inn))*ok;
              float post=(1.-smoothstep(0.03,0.03+fw,abs(q.x)))*(1.-smoothstep(0.03,0.03+fw,abs(q.y-0.18)));
              float kryss=max(1.-smoothstep(0.03,0.03+fw,abs(q.x)), 1.-smoothstep(0.03,0.03+fw,abs(q.y-0.18)));
              vec3 hvit=vec3(0.96,0.94,0.90)*mix(1.,0.74,k);
              vec3 glas=mix(vec3(0.27,0.31,0.36),vec3(0.20,0.22,0.27),k);
              glas=mix(glas, glas*1.35, smoothstep(0.2,-0.4,q.x+q.y*0.5)*0.6);
              vec3 w=mix(hvit, glas, glass*(1.-kryss));
              float fjern=smoothstep(0.12,0.3,fw);
              // dør på gateplan i annenhver fjerde akse, som i tegningen
              float akse=floor(u/2.6);
              float dor = (rad<0.5 && mod(akse,4.)==1. && topp>3.2) ? 1. : 0.;
              vec2 qd=vec2(fu-1.3, fy-1.15); vec2 ddd=abs(qd)-vec2(0.55,1.15); float innd=max(ddd.x,ddd.y);
              float dramme=(1.-smoothstep(0.,fw,innd))*dor; float dfyll=(1.-smoothstep(-0.09,-0.09+fw,innd))*dor;
              vec3 dorf=mix(vec3(0.33,0.24,0.19),vec3(0.24,0.18,0.15),k);
              ramme*=1.-dor;
              vec3 naer=mix(c, w, ramme); naer=mix(naer, hvit, dramme); naer=mix(naer, dorf, dfyll);
              vec3 langt=mix(c, glas, 0.16*ok);
              c=mix(naer, langt, fjern);
              // sokkel og gesims
              float fwy=max(fwidth(lp.y),0.001);
              c*=mix(1.,0.84, 1.-smoothstep(0.42,0.42+fwy,lp.y));
              float ges=smoothstep(topp-0.42,topp-0.42+fwy,lp.y)*(1.-smoothstep(topp-0.12,topp-0.12+fwy,lp.y));
              c=mix(c, hvit, ges*0.55);
            }
          }
          gl_FragColor=vec4(c,1.);
          #include <colorspace_fragment>
        }`
    });
    if(opt.ds) m.side=THREE.DoubleSide;
    mats.set(key,m);
  }
  return mats.get(key);
}
