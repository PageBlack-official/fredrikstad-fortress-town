import * as THREE from 'three';
import { DATA, scene } from './00_oppsett.js';
import { medSkygge } from './02_lys.js';
import { BAKKELAG, BK, VANN_Y, alleIBrostein, bakke, bakkelag, flatH, waterMat } from './03_bakke-vann-grønt.js';
import { stoneMat } from './04_brostein-i-hele-gamlebyen.js';
import { mat } from './05_bygg.js';
// ---- festningsterrenget: voller med skråninger, grønt som plenene i tegningen ----
const TER0 = DATA.landskap && DATA.landskap.terreng;
// Med målt bakke (BK, 07.11) er terrenget hele DTM-rammen: én bakke for byen, vollene, kaiene og strendene ned til vannet.
// TER beskriver da bakkens rutenett (paaTerreng deler kantene etter det); det gamle festningsterrenget gir bare hvor det er gress.
const TER = BK ? {x0:BK.x0, y0:BK.y0, g:BK.g, nx:BK.nx, ny:BK.ny, off:0} : TER0;
let hAt = ()=>0, hTer = ()=>0;   // hTer: terrengnettets høyde (trekantene), se under
const terFarge = { lysF:{value:new THREE.Color('rgb(128,180,136)')}, skyggeF:{value:new THREE.Color('rgb(92,142,108)')}, bakkeF:{value:new THREE.Color(0xefece4)} };
if (BK){
  const nx=BK.nx, ny=BK.ny, G=BK.g, HV=new Float32Array(nx*ny);
  for(let j=0;j<ny;j++) for(let i=0;i<nx;i++) HV[j*nx+i]=bakke(BK.x0+i*G, BK.y0+j*G);
  const hv=(i,j)=>HV[Math.max(0,Math.min(ny-1,j))*nx+Math.max(0,Math.min(nx-1,i))];
  hAt=bakke;
  hTer=(x,y)=>{ const fx=(x-BK.x0)/G, fy=(y-BK.y0)/G; const i=Math.max(0,Math.min(nx-2,Math.floor(fx))), j=Math.max(0,Math.min(ny-2,Math.floor(fy)));
    const tx=Math.min(1,Math.max(0,fx-i)), ty=Math.min(1,Math.max(0,fy-j)), a=hv(i,j), b=hv(i+1,j), c=hv(i,j+1), d=hv(i+1,j+1);
    return (tx+ty<=1 ? a+(b-a)*tx+(c-a)*ty : d+(c-d)*(1-tx)+(b-d)*(1-ty))+0.03; };
  // gress der det gamle festningsterrenget var (vollene, plenene på festningen) og i festningsområdet (landskap.fest: vollgravenes
  // bredder); ellers bakkens lyse farge som før
  let gammel=()=>0;
  if(TER0){ const b=atob(TER0.m); const MB=new Uint8Array(b.length); for(let i=0;i<b.length;i++) MB[i]=b.charCodeAt(i);
    gammel=(x,y)=>{ const i=Math.round((x-TER0.x0)/TER0.g), j=Math.round((y-TER0.y0)/TER0.g); if(i<0||j<0||i>=TER0.nx||j>=TER0.ny) return 0; const k=j*TER0.nx+i; return (MB[k>>3]>>(7-(k&7)))&1; }; }
  const FEST=(DATA.landskap&&DATA.landskap.fest)||[];
  const iPol=(x,y,P)=>{ let inne=false; for(let k=0,j=P.length-1;k<P.length;j=k++){ const a=P[k],c=P[j]; if((a[1]>y)!==(c[1]>y) && x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1]+1e-12)+a[0]) inne=!inne; } return inne; };
  const gress=(x,y)=>gammel(x,y) || FEST.some(P=>iPol(x,y,P)) ? 1 : 0;
  const pos=new Float32Array(nx*ny*3), gr=new Float32Array(nx*ny);
  for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const k=j*nx+i, X=BK.x0+i*G, Y=BK.y0+j*G; pos[k*3]=X; pos[k*3+1]=HV[k]+0.03; pos[k*3+2]=-Y; gr[k]=gress(X,Y); }
  // gresset følger skråningen ned til vannet (07.11: vollgravens bredder fikk et lyst, tagget bånd mellom gresset og vannet):
  // punkter under 1,5 m over vannflaten med gress ved siden av blir gress, fire runder (8 m)
  for(let runde=0;runde<4;runde++){ const ny_=[];
    for(let j=1;j<ny-1;j++) for(let i=1;i<nx-1;i++){ const k=j*nx+i; if(gr[k] || HV[k]>VANN_Y+1.5) continue;
      if(gr[k-1]||gr[k+1]||gr[k-nx]||gr[k+nx]||gr[k-nx-1]||gr[k-nx+1]||gr[k+nx-1]||gr[k+nx+1]) ny_.push(k); }
    ny_.forEach(k=>gr[k]=1); }
  // ruter helt under vannflaten tegnes ikke (vannet dekker dem)
  const idx=[], under=VANN_Y-0.05;
  for(let j=0;j<ny-1;j++) for(let i=0;i<nx-1;i++){ const a=j*nx+i, b=a+1, c=a+nx, d=c+1; if(HV[a]<under && HV[b]<under && HV[c]<under && HV[d]<under) continue; idx.push(a,b,c, b,d,c); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('aGress',new THREE.BufferAttribute(gr,1));
  g.setIndex(idx); g.computeVertexNormals();
  // vannfeltet (src/03, verktoy/vann.py): r = avstand inn i vannet; bakken kuttes der vannflaten begynner, så strandkanten følger
  // vannets omriss og ikke rutenettets tagger
  const WU=waterMat.uniforms;
  const terMat=new THREE.ShaderMaterial({
    uniforms:Object.assign({ tFelt:WU.tFelt, felt:WU.felt, maks:WU.maks, harFelt:WU.harFelt, vannY:{value:VANN_Y} }, terFarge),
    vertexShader:`attribute float aGress; varying vec3 vn; varying vec3 wp; varying float ny; varying float vg; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; vn=normalize(normalMatrix*normal); ny=normal.y; vg=aGress; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`uniform vec3 lysF, skyggeF, bakkeF; uniform sampler2D tFelt; uniform vec4 felt; uniform float maks, harFelt, vannY; varying vec3 vn; varying vec3 wp; varying float ny; varying float vg;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      void main(){
        if(harFelt>0.5 && wp.y<vannY+1.5){ float r=texture2D(tFelt, vec2((wp.x-felt.x)/felt.z, (-wp.z-felt.y)/felt.w)).r*maks; if(r>0.08) discard; }   // (07.11: 0,3 m lot trekantene som krysser strandkanten stikke ut som tagger)
        vec3 nn=normalize(vn); float d=dot(nn,solRetning()); float hell=1.-ny;
        // gress (vollene): to toner som tegningen, skråninger bort fra sola får skyggegrønt
        float k = (1.-smoothstep(0.437,0.443,d)) * smoothstep(0.108,0.112,hell);
        vec3 g=mix(lysF, skyggeF, k);
        g=mix(g, lysF*1.06, smoothstep(0.62,0.75,d)*smoothstep(0.05,0.15,hell)*0.6);
        float m=n(wp.xz*0.025)*0.6+n(wp.xz*0.09)*0.4; g*=0.94+0.12*m;
        float gs=n(vec2(wp.x*0.55+wp.z*0.22, wp.z*1.9-wp.x*0.3))*0.6+n(vec2(wp.x*1.7, wp.z*4.3))*0.4; g*=0.975+0.05*gs;
        // bakken (byen, kaiene, strendene): den lyse grunnfargen; bratte skråninger bort fra sola litt mørkere, så kaikanten leses
        vec3 b=bakkeF*(1.-0.10*(1.-smoothstep(0.30,0.45,d))*smoothstep(0.15,0.35,hell));
        vec3 c=mix(b, g, smoothstep(0.35,0.65,vg));
        gl_FragColor=vec4(c,0.);
        #include <colorspace_fragment>
      }`
  });
  medSkygge(terMat); bakkelag(terMat, BAKKELAG.terreng);
  const ter=new THREE.Mesh(g,terMat); ter.receiveShadow=true; scene.add(ter);
}
else if (TER){
  const b64=s=>{ const b=atob(s); const a=new Uint8Array(b.length); for(let i=0;i<b.length;i++) a[i]=b.charCodeAt(i); return a; };
  const MB=b64(TER.m), nx=TER.nx, ny=TER.ny, G=TER.g;
  const inn0=i=>(MB[i>>3]>>(7-(i&7)))&1;
  // høydene ligger bare for punktene i masken (rad for rad); utenfor er bakken null
  const H=new Uint8Array(nx*ny); H.fill(Math.round((TER.off||0)*20)); { const hk=b64(TER.h); let c=0; for(let i=0;i<nx*ny;i++) if(inn0(i)) H[i]=hk[c++]; }
  const MK=new Uint8Array(nx*ny); for(let i=0;i<nx*ny;i++) MK[i]=inn0(i); const inn=i=>MK[i];
  // TERRENGFLIKER (data/terrengflikker.json): Kartverkets DTM lagt over det beregnede terrenget der det beregnede er feil
  // (verktoy/landemerker.py; første bruk: Voldporten, der vollen i terrenget stod 12 m for langt øst og porten stod på flat mark).
  // {x0, y0, g, nx, ny, h (cm, rad for rad fra sør), kant (m: myk overgang til terrenget rundt)}
  (DATA.terrengflikker||[]).forEach(F=>{ const fh=(i,j)=>F.h[Math.min(F.ny-1,Math.max(0,j))*F.nx+Math.min(F.nx-1,Math.max(0,i))]/100;
    const X1=F.x0+(F.nx-1)*F.g, Y1=F.y0+(F.ny-1)*F.g, off=TER.off||0;
    for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const X=TER.x0+i*G, Y=TER.y0+j*G; if(X<F.x0||X>X1||Y<F.y0||Y>Y1) continue;
      const fx=(X-F.x0)/F.g, fy=(Y-F.y0)/F.g, a=Math.floor(fx), b=Math.floor(fy), tx=fx-a, ty=fy-b;
      const p=(fh(a,b)*(1-tx)+fh(a+1,b)*tx)*(1-ty)+(fh(a,b+1)*(1-tx)+fh(a+1,b+1)*tx)*ty;
      const d=Math.min(X-F.x0,X1-X,Y-F.y0,Y1-Y), w=Math.min(1,Math.max(0,d/(F.kant||1))), w2=w*w*(3-2*w);
      const k=j*nx+i, gml=MK[k]?H[k]/20-off:0, ny_=w2*p+(1-w2)*gml;
      H[k]=Math.max(0,Math.min(255,Math.round((ny_+off)*20))); MK[k]=(ny_>0.02||MK[k]&&w2<1)?1:0; } });
  const hv=(i,j)=>H[j*nx+i]/20-(TER.off||0);
  hAt=(x,y)=>{ const fx=(x-TER.x0)/G, fy=(y-TER.y0)/G; const i=Math.floor(fx), j=Math.floor(fy); if(i<0||j<0||i>=nx-1||j>=ny-1) return 0;
    const tx=fx-i, ty=fy-j; return (hv(i,j)*(1-tx)+hv(i+1,j)*tx)*(1-ty)+(hv(i,j+1)*(1-tx)+hv(i+1,j+1)*tx)*ty; };
  // hTer: høyden på terrengnettet slik det tegnes (samme trekanter som indeksen under: (a,b,c) og (b,d,c), +0,03), ikke bilineær.
  // Flater og veier legges på den (avvik A16): med bilineær høyde og hjørner bare i polygonets punkter skar store flater
  // gjennom vollens nett, og grus og gress byttet plass når kameraet flyttet seg.
  hTer=(x,y)=>{ const fx=(x-TER.x0)/G, fy=(y-TER.y0)/G; const i=Math.floor(fx), j=Math.floor(fy); if(i<0||j<0||i>=nx-1||j>=ny-1) return 0;
    const tx=fx-i, ty=fy-j, a=hv(i,j), b=hv(i+1,j), c=hv(i,j+1), d=hv(i+1,j+1);
    return (tx+ty<=1 ? a+(b-a)*tx+(c-a)*ty : d+(c-d)*(1-tx)+(b-d)*(1-ty))+0.03; };
  const pos=new Float32Array(nx*ny*3);
  for(let j=0;j<ny;j++) for(let i=0;i<nx;i++){ const k=(j*nx+i)*3; pos[k]=TER.x0+i*G; pos[k+1]=hv(i,j)+0.03; pos[k+2]=-(TER.y0+j*G); }
  const idx=[];
  for(let j=0;j<ny-1;j++) for(let i=0;i<nx-1;i++){ const a=j*nx+i, b=a+1, c=a+nx, d=c+1; if(inn(a)+inn(b)+inn(c)+inn(d)>=2){ idx.push(a,b,c, b,d,c); } }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setIndex(idx); g.computeVertexNormals();
  const terMat=new THREE.ShaderMaterial({
    uniforms:{ lysF:{value:new THREE.Color('rgb(128,180,136)')}, skyggeF:{value:new THREE.Color('rgb(92,142,108)')} },
    vertexShader:`varying vec3 vn; varying vec3 wp; varying float ny; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; vn=normalize(normalMatrix*normal); ny=normal.y; gl_Position=projectionMatrix*viewMatrix*w; }`,
    fragmentShader:`uniform vec3 lysF, skyggeF; varying vec3 vn; varying vec3 wp; varying float ny;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      void main(){ vec3 nn=normalize(vn); float d=dot(nn,solRetning()); float hell=1.-ny;
        // to toner som tegningen: skråninger bort fra sola får skyggegrønt, med myk overgang
        float k = 1.-smoothstep(0.437,0.443,d);
        k *= smoothstep(0.108,0.112,hell) * smoothstep(2.2,3.4,wp.y);  // bare ekte voller (over ca. 3 m) får skyggegrønt, ikke små dumper                     // flat mark og slake banker er alltid lyse
        vec3 c=mix(lysF, skyggeF, k);
        // lys kant på vollkronen mot sola
        c=mix(c, lysF*1.06, smoothstep(0.62,0.75,d)*smoothstep(0.05,0.15,hell)*0.6);
        float m=n(wp.xz*0.025)*0.6+n(wp.xz*0.09)*0.4; c*=0.94+0.12*m;
        // gresset malt med korte penselstrøk som tegningens plener
        float gs=n(vec2(wp.x*0.55+wp.z*0.22, wp.z*1.9-wp.x*0.3))*0.6+n(vec2(wp.x*1.7, wp.z*4.3))*0.4; c*=0.975+0.05*gs;
        gl_FragColor=vec4(c,0.); // alfa 0 = terreng: ingen blekkstrek i rutenettets knekker, svakere hjørneskygge
        #include <colorspace_fragment>
      }`
  });
  medSkygge(terMat); bakkelag(terMat, BAKKELAG.terreng);
  const ter=new THREE.Mesh(g,terMat); ter.receiveShadow=true; scene.add(ter);
  // festningsområdet som flate under terrenget: gir eksakt kant mot bakken og vannet
  if(!BK) (DATA.landskap.fest||[]).forEach(p=>flatH(p,[],0.02,terMat));
}
// veiflatene på terrenget: kanten deles opp til terrengrutenettet, flaten trianguleres, og trekanter der flaten ville skåret
// gjennom terrenget (feil over 2 cm midt på lengste kant) deles til de følger det. Høyden er terrenget + 6 cm som båndene
// (gangvei 3 cm, brostein 5 cm som grunnen).
// paaTerreng: polygoner [[ytterkant, hull …], …] lagt på terrenget med høyden z(x,y) i hvert punkt. Kanten deles opp til
// terrengrutenettet, flaten trianguleres, og en trekant deles på lengste kant så lenge den er lengre enn maks, eller flaten
// ellers ville avveket over 2 cm fra z langs kanten (på flat mark blir trekantene store, på vollene små). Midtpunktene deles
// mellom naboene, så flaten henger sammen. Skriver til B {p, i} (x, høyde, -y).
function paaTerreng(deler, z, B, maks){
  const steg=TER?TER.g:1.5;
  const tett=r=>{ const u=[]; for(let k=0;k<r.length;k++){ const a=r[k], c=r[(k+1)%r.length], m=Math.max(1,Math.ceil(Math.hypot(c[0]-a[0],c[1]-a[1])/steg));
    for(let j=0;j<m;j++) u.push([a[0]+(c[0]-a[0])*j/m, a[1]+(c[1]-a[1])*j/m]); } return u; };
  deler.forEach(d=>{
    const ytre=tett(d[0]), hull=d.slice(1).map(tett), V=[...ytre, ...hull.flat()];
    const tri=THREE.ShapeUtils.triangulateShape(ytre.map(q=>new THREE.Vector2(q[0],q[1])), hull.map(h=>h.map(q=>new THREE.Vector2(q[0],q[1]))));
    const P=V.map(q=>[q[0],q[1],z(q[0],q[1])]), midt=new Map();
    const mid=(i,j)=>{ const k=i<j?i+','+j:j+','+i; let n=midt.get(k); if(n===undefined){ const x=(P[i][0]+P[j][0])/2, y=(P[i][1]+P[j][1])/2; n=P.length; P.push([x,y,z(x,y)]); midt.set(k,n); } return n; };
    const avvik=(a,c)=>[0.25,0.5,0.75].some(t=>Math.abs(z(a[0]+(c[0]-a[0])*t, a[1]+(c[1]-a[1])*t)-(a[2]+(c[2]-a[2])*t))>0.02);
    const ko=tri.map(t=>[t[0],t[1],t[2]]), ut=[];
    while(ko.length){ const t=ko.pop(); let L=-1, e=0;
      for(let s=0;s<3;s++){ const a=P[t[s]], c=P[t[(s+1)%3]], l=Math.hypot(c[0]-a[0],c[1]-a[1]); if(l>L){ L=l; e=s; } }
      const i=t[e], j=t[(e+1)%3], o=t[(e+2)%3];
      if(L>steg && (L>maks || avvik(P[i],P[j]) || avvik(P[j],P[o]) || avvik(P[o],P[i]))){ const m=mid(i,j); ko.push([i,m,o],[m,j,o]); continue; }
      ut.push(t); }
    const o0=B.p.length/3; P.forEach(q=>B.p.push(q[0],q[2],-q[1])); ut.forEach(t=>B.i.push(o0+t[0],o0+t[2],o0+t[1]));
  });
}
// ligger veibåndet på en av broene i data/broer.json (midtpunktet innenfor 6 m fra broas linje)?
function paaBro(P){ const m=P[Math.floor(P.length/2)]; const q=P.length>1 ? [(P[0][0]+P[P.length-1][0])/2,(P[0][1]+P[P.length-1][1])/2] : m;
  return (DATA.broer||[]).some(br=>br.p.some((a,k)=>{ if(k===0) return false; const b=br.p[k-1], dx=a[0]-b[0], dy=a[1]-b[1], L2=dx*dx+dy*dy||1;
    return [m,q].some(p=>{ const t=Math.max(0,Math.min(1,((p[0]-b[0])*dx+(p[1]-b[1])*dy)/L2)); return Math.hypot(p[0]-b[0]-t*dx, p[1]-b[1]-t*dy) < 6; }); })); }
// veiflatene (datalag.veiflater) på terrenget: terrenget + 6 cm som båndene (gangvei 3 cm)
function veiflater(VF, buf){
  // brosteinen (B) er grunnen i byen, gatene og brosteinsflatene i én: 5 cm på flat mark, 2 cm over terrenget der det er høyere
  Object.entries(VF).forEach(([gr, deler])=>{ const B=buf[gr]; if(!B) return; const lofT=gr==='G'?0.03:0.06;
    paaTerreng(deler, gr==='B' ? (BK ? (x,y)=>hTer(x,y)+0.05 : (x,y)=>Math.max(0.05, hTer(x,y)+0.02)) : (x,y)=>hTer(x,y)+lofT, B, gr==='B'?40:3*(TER?TER.g:1.5)); });
}
// veier som bånd i tegningens gategrå; bruer ligger over vannet med sider (slått sammen til tre mesher)
{
  // flate (data/landskap.json, verktoy/bakke.py gater): kjøreveier lagt med brostein tegnes med brosteinen, ikke gategrått
  // heller og grus (kaia, plassene, stiene på vollene) får flatens farge, som flatene i 17 
  const buf={K:{p:[],i:[]}, G:{p:[],i:[]}, S:{p:[],i:[]}, B:{p:[],i:[]}, H:{p:[],i:[]}, U:{p:[],i:[]}};
  const quad=(B,v)=>{ const o=B.p.length/3; B.p.push(...v); B.i.push(o,o+2,o+1, o+1,o+2,o+3); };
  // veiflatene (datalag.veiflater, 06.11): alle bånd med samme dekke smeltet til én flate, så de ikke ligger oppå hverandre
  // som et lappeteppe med strek rundt hvert bånd. Bruer og bånd over 0,5 m tegnes fortsatt som bånd under (med sider).
  const VF=DATA.landskap&&DATA.landskap.veiflater;
  if(VF) veiflater(VF, buf);
  (DATA.landskap?DATA.landskap.veier:[]).forEach(v=>{
    if(VF && !v.b && !v.p.some(q=>q[2]>0.5)) return;
    // bruer som har egen bro (data/broer.json, src/11) tegnes ikke som veibånd i tillegg (07.11: Vindebroa fikk to dekk i hver sin høyde
    // da broa ble lagt på terrenget)
    if(BK && v.b && paaBro(v.p)) return;
    // båndet legges på terrenget (avvik A8): punktene i dataene står med opptil 30 m mellomrom, og en rett bit mellom dem
    // skar gjennom vollens terreng (terrenget stakk opp som takker som flimret). Biten deles opp til halve terrengrutenettet, og
    // hver kant løftes til minst terrenget + 6 cm.
    const P0=v.p; if(P0.length<2) return; const w=v.w/2, dz=v.k==='gang'?-0.03:0; const B=v.flate==='brostein'?buf.B:v.flate==='heller'?buf.H:v.flate==='grus'?buf.U:(v.k==='gang'?buf.G:buf.K);
    const steg=TER?TER.g/2:2, P=[P0[0]];
    for(let k=1;k<P0.length;k++){ const a=P0[k-1], c=P0[k], m=Math.max(1,Math.ceil(Math.hypot(c[0]-a[0],c[1]-a[1])/steg));
      for(let j=1;j<=m;j++){ const t=j/m; P.push([a[0]+(c[0]-a[0])*t, a[1]+(c[1]-a[1])*t, a[2]+(c[2]-a[2])*t]); } }
    const n=P.length, L=[], R=[];
    for(let k=0;k<n;k++){
      const a=P[Math.max(0,k-1)], b=P[Math.min(n-1,k+1)]; let dx=b[0]-a[0], dy=b[1]-a[1]; const l=Math.hypot(dx,dy)||1; dx/=l; dy/=l;
      const nx=-dy*w, ny=dx*w;
      // brostein ligger i samme høyde som brosteinsgrunnen (5 cm over terrenget): samme stein, ingen kant for streken (A15)
      // med målt bakke (BK) følger veien bakken; bare bruer (v.b) beholder høyden i dataene der den er over bakken
      const zP=(BK && !v.b) ? -1e9 : P[k][2];
      const zL=B===buf.B ? hTer(P[k][0]+nx,P[k][1]+ny)+0.05 : Math.max(zP, hTer(P[k][0]+nx,P[k][1]+ny)+0.06)+dz,
            zR=B===buf.B ? hTer(P[k][0]-nx,P[k][1]-ny)+0.05 : Math.max(zP, hTer(P[k][0]-nx,P[k][1]-ny)+0.06)+dz;
      L.push([P[k][0]+nx, zL, -(P[k][1]+ny)]); R.push([P[k][0]-nx, zR, -(P[k][1]-ny)]);
    }
    for(let k=0;k<n-1;k++){
      if(!(B===buf.B && alleIBrostein([P[k],P[k+1],[L[k][0],-L[k][2]],[R[k][0],-R[k][2]],[L[k+1][0],-L[k+1][2]],[R[k+1][0],-R[k+1][2]]])))   // brostein på brostein: grunnen (A15)
        quad(B,[...L[k],...R[k],...L[k+1],...R[k+1]]);
      if(v.b && (P[k][2]>0.5 || P[k+1][2]>0.5)){
        [L,R].forEach(E=>{ const a=E[k], c=E[k+1]; quad(buf.S,[...a, ...c, a[0],Math.max(0.1,a[1]-0.8),a[2], c[0],Math.max(0.1,c[1]-0.8),c[2]]); });
      }
    }
  });
  [[buf.K,mat([128,124,120],false),0],[buf.G,mat([146,142,134],false),1],[buf.S,mat([120,112,104],false),0],[buf.H,mat([190,184,174],false),2],[buf.U,mat([214,204,182],false),3]].forEach(([B,m,under])=>{
    if(!B.p.length) return; const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(B.p,3)); g.setIndex(B.i);
    const mm=m.clone(); mm.side=THREE.DoubleSide; if(B!==buf.S) bakkelag(mm, BAKKELAG.vei, under); const me=new THREE.Mesh(g,mm); me.receiveShadow=true; me.castShadow=(B===buf.S); scene.add(me); });
  if(buf.B.p.length){ const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(buf.B.p,3)); g.setIndex(buf.B.i);
    stoneMat.side=THREE.DoubleSide; const me=new THREE.Mesh(g,stoneMat); me.receiveShadow=true; scene.add(me); }
}

export { TER, hAt, hTer, paaTerreng };
