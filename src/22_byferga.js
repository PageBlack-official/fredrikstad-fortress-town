// ---- Byferga (03.11, Vegar: «frisefett … se byferga entre kaia i gamlebyen i introswipen») ----
// Den enkleste formen (Vegars tegning 03.11): rødt skrog som dominerer, lang hvit salong med en rekke vinduer, et høyere hvitt
// styrhus bak salongen, åpent dekk med rekke bakerst. Alt om bane, mål og farger står i data/ferge.json. Ferga følger
// introsveipet: ved u = fart.start ligger den på Sentrum-siden, ved fart.slutt til kai, og der blir den liggende (også med
// ?skip og delte lenker). Kursen er banens tangent; baugen peker framover langs banen. ?ferge=0 slår av.
const ferge=(()=>{
  const F=DATA.ferge; if(!F || Q0.get('ferge')==='0') return {til(){}, grp:null};
  const VANN_Y=0.15, M=F.mål, C=F.farge, L=M.lengde, B=M.bredde;
  const g=new THREE.Group(); g.name='byferga';
  const m=(rgb)=>mat(rgb,false);
  const kloss=(dx,dy,dz,x,y,z,mt)=>{ const k=new THREE.Mesh(new THREE.BoxGeometry(dx,dy,dz),mt); k.position.set(x,y,z); k.castShadow=k.receiveShadow=true; g.add(k); return k; };
  // skroget: boks med avfasede ender. Rampeenden (+x, baugen mot kaia) er flat og bred, den andre enden er spisset (Vegar 03.11 22:46)
  const skrog=new THREE.Shape(); const hl=L/2, hb=B/2, fb=0.9, fh=2.4;
  skrog.moveTo(-hl+fh,-hb); skrog.lineTo(hl-fb,-hb); skrog.lineTo(hl,-hb*0.75); skrog.lineTo(hl,hb*0.75); skrog.lineTo(hl-fb,hb); skrog.lineTo(-hl+fh,hb); skrog.lineTo(-hl,hb*0.3); skrog.lineTo(-hl,-hb*0.3); skrog.closePath();
  const sg=new THREE.ExtrudeGeometry(skrog,{depth:M.fribord+0.5, bevelEnabled:false}); sg.rotateX(-Math.PI/2); sg.translate(0,-0.5,0);
  const s=new THREE.Mesh(sg, m(C.skrog)); s.castShadow=s.receiveShadow=true; g.add(s);
  const yd=M.fribord;
  kloss(L-fb-fh, 0.06, B-0.3, (fh-fb)/2, yd+0.03, 0, m(C.dekk));                              // dekket (salongenden spisset, rampeenden flat)
  // salongen: hvit boks, vindusrekka som mørke ruter på begge sider og i framkant
  const [sl,sb,sh]=M.salong, sx=M.salong_fra;
  kloss(sl, sh, sb, sx, yd+sh/2, 0, m(C.salong));
  const vh=sh-M.vindu_fra-0.35, vy=yd+M.vindu_fra+vh/2, n=M.vinduer, vb=(sl-0.6)/n;
  for(let i=0;i<n;i++){ const x=sx-sl/2+0.3+vb*(i+0.5); kloss(vb-0.35, vh, sb+0.06, x, vy, 0, m(C.vindu)); }
  kloss(0.06, vh, sb-0.8, sx-sl/2-0.01, vy, 0, m(C.vindu));                                    // endevinduet mot akterenden
  kloss(sl+0.5, 0.16, sb+0.5, sx, yd+sh+0.08, 0, m(C.tak));                                     // salongtaket, litt utenfor
  // styrhuset foran salongen, mot rampa: høyere, med vindusbånd rundt og eget tak
  const [hl2,hb2,hh]=M.styrhus, hx=sx+sl/2+hl2/2+0.1;
  kloss(hl2, hh, hb2, hx, yd+hh/2, 0, m(C.salong));
  kloss(hl2+0.06, hh*0.4, hb2+0.06, hx, yd+hh*0.62, 0, m(C.vindu));
  kloss(hl2+0.5, 0.16, hb2+0.5, hx, yd+hh+0.08, 0, m(C.tak));
  // baugrampa: ei rød plate hengslet i baugen på dekkshøyde; oppe (lukket) under overfarten, senkes ned på kaia når ferga er framme
  const R=F.rampe||{bredde:2.6,lengde:2.4,oppe_grader:92,nede_grader:-8,ned:[0.8,0.92]}; const R_B=()=>R.bredde;
  const rampe=new THREE.Group(); rampe.position.set(hl,yd,0); g.add(rampe);
  { const k=new THREE.Mesh(new THREE.BoxGeometry(R.lengde,0.08,R.bredde),m(C.skrog)); k.position.set(R.lengde/2,0,0); k.castShadow=k.receiveShadow=true; rampe.add(k); }
  const rampeTil=v=>{ rampe.rotation.z=THREE.MathUtils.degToRad(R.oppe_grader+(R.nede_grader-R.oppe_grader)*v); };   // v 0 = oppe, 1 = nede
  rampeTil(1);
  // åpent dekk mellom styrhuset og rampa, med rekke: tynne stolper og en topplist
  const rx0=hl-fb-0.2, rx1=hx+hl2/2+0.1, rl=rx0-rx1;
  [1,-1].forEach(sd=>{ kloss(rl, 0.05, 0.05, (rx0+rx1)/2, yd+M.rekke, sd*(hb-0.2), m(C.rekke)); for(let i=0;i<=3;i++) kloss(0.05, M.rekke, 0.05, rx1+rl*i/3, yd+M.rekke/2, sd*(hb-0.2), m(C.rekke)); });
  [1,-1].forEach(sd=>kloss(0.05, 0.05, (B-0.4-R_B())/2, rx0, yd+M.rekke, sd*((B-0.4)/2-(B-0.4-R_B())/4), m(C.rekke)));   // tverrekke i baugen, åpning for rampa
  g.scale.setScalar(F.skala||1); g.position.y=VANN_Y; scene.add(g);   // landemerke-skala (se data)
  // banen: kubisk Bézier i modellplanet; p(t) og tangent
  const [P0,P1,P2,P3]=F.bane.map(p=>new THREE.Vector2(p[0],p[1]));
  const pos=t=>{ const u=1-t; return new THREE.Vector2().addScaledVector(P0,u*u*u).addScaledVector(P1,3*u*u*t).addScaledVector(P2,3*u*t*t).addScaledVector(P3,t*t*t); };
  const tan=t=>{ const u=1-t; return new THREE.Vector2().addScaledVector(P1.clone().sub(P0),3*u*u).addScaledVector(P2.clone().sub(P1),6*u*t).addScaledVector(P3.clone().sub(P2),3*t*t).normalize(); };
  let sist=-1;
  // u = introens framdrift 0..1; ferga går fra fart.start til fart.slutt, med myk brems inn mot kaia (eksponentiell landing, teknikk 20)
  let sistR=-1;
  function til(u){ const r=THREE.MathUtils.clamp((u-R.ned[0])/(R.ned[1]-R.ned[0]),0,1); if(r!==sistR){ sistR=r; rampeTil(r*r*(3-2*r)); }
    let a=THREE.MathUtils.clamp((u-F.fart.start)/(F.fart.slutt-F.fart.start),0,1); a=1-Math.pow(1-a,2.2); if(Math.abs(a-sist)<1e-5) return; sist=a;
    const p=pos(a), d=tan(a); g.position.x=p.x; g.position.z=-p.y; g.rotation.y=Math.atan2(d.y,d.x);   // modell y nord = -z; baugen (+x) langs banen
    g.position.y=VANN_Y+0.04*Math.sin(a*9);                                                            // svak dupp
  }
  til(1);
  return {til, grp:g};
})();
