import * as THREE from 'three';
import { registrer } from './tilstand.js';
import { DATA, Q0, scene } from './00_oppsett.js';
import { VANN_Y } from './03_bakke-vann-grønt.js';
import { mat } from './05_bygg.js';
import { fyllFergeKort, kort_ } from './16_interaksjon.js';
// ---- Byfergene (Vegar: «se byferga entre kaia i gamlebyen i introswipen», «koble fergetider til fergen») ----
// To like båter (Vegars tegning): rødt skrog som dominerer, lang hvit salong med en rekke vinduer, styrhus og åpent dekk
// med rekke i enden mot rampa (baugen, flat). 803 Gamlebyfergen går fram og tilbake fra nordkaia til Cicignon; 805 Byferga går fra
// sørkaia til Smertu, Sentrum, Værste, Gressvik og Ålekilen og forsvinner i papirkanten på veien. Tidene er sanntid fra Entur
// (Journey Planner v3), med rutetabellen i data/ferge.json i reserve. Alt om kaier, veier, mål og farger står i data/ferge.json.
// Introen viser 803 sin siste overfart og lander der båten faktisk er når introen slutter. Klikk på en båt viser avgangene (16).
// ?ferge=0 slår av. ?fergetid=HH:MM[:SS] stiller fergeklokka, ?fergefrys=1 holder den (test). ?entur=0 bruker bare rutetabellen.
const ferge=(()=>{
  const F=DATA.ferge; if(!F || !F.ruter || Q0.get('ferge')==='0') return {til(){}, intro(){}, beveger:()=>false, treff:()=>null, kort:()=>null, grupper:[]};
  const M=F.mål, C=F.farge, L=M.lengde, B=M.bredde, SK=F.skala||1, HL=L/2*SK, MIN=60000;
  const R=F.rampe;
  const mats={}; const m=rgb=>mats[rgb] || (mats[rgb]=mat(rgb,false));
  // ---- båten (samme bygg for begge) ----
  function byggBaat(navn){
    const g=new THREE.Group(); g.name=navn;
    const kloss=(dx,dy,dz,x,y,z,mt)=>{ const k=new THREE.Mesh(new THREE.BoxGeometry(dx,dy,dz),mt); k.position.set(x,y,z); k.castShadow=k.receiveShadow=true; g.add(k); return k; };
    // skroget: boks med avfasede ender. Rampeenden (+x, baugen mot kaia) er flat og bred, den andre enden er spisset (Vegar)
    const skrog=new THREE.Shape(); const hl=L/2, hb=B/2, fb=0.9, fh=2.4;
    skrog.moveTo(-hl+fh,-hb); skrog.lineTo(hl-fb,-hb); skrog.lineTo(hl,-hb*0.75); skrog.lineTo(hl,hb*0.75); skrog.lineTo(hl-fb,hb); skrog.lineTo(-hl+fh,hb); skrog.lineTo(-hl,hb*0.3); skrog.lineTo(-hl,-hb*0.3); skrog.closePath();
    const sg=new THREE.ExtrudeGeometry(skrog,{depth:M.fribord+0.5, bevelEnabled:false}); sg.rotateX(-Math.PI/2); sg.translate(0,-0.5,0);
    const s=new THREE.Mesh(sg, m(C.skrog)); s.castShadow=s.receiveShadow=true; g.add(s);
    const yd=M.fribord;
    kloss(L-fb-fh, 0.06, B-0.3, (fh-fb)/2, yd+0.03, 0, m(C.dekk));
    // salongen: hvit boks, vindusrekka som mørke ruter på begge sider og i enden
    const [sl,sb,sh]=M.salong, sx=M.salong_fra;
    kloss(sl, sh, sb, sx, yd+sh/2, 0, m(C.salong));
    const vh=sh-M.vindu_fra-0.35, vy=yd+M.vindu_fra+vh/2, n=M.vinduer, vb=(sl-0.6)/n;
    for(let i=0;i<n;i++){ const x=sx-sl/2+0.3+vb*(i+0.5); kloss(vb-0.35, vh, sb+0.06, x, vy, 0, m(C.vindu)); }
    kloss(0.06, vh, sb-0.8, sx-sl/2-0.01, vy, 0, m(C.vindu));
    kloss(sl+0.5, 0.16, sb+0.5, sx, yd+sh+0.08, 0, m(C.tak));
    // styrhuset mellom salongen og rampa: høyere, med vindusbånd rundt og eget tak
    const [hl2,hb2,hh]=M.styrhus, hx=sx+sl/2+hl2/2+0.1;
    kloss(hl2, hh, hb2, hx, yd+hh/2, 0, m(C.salong));
    kloss(hl2+0.06, hh*0.4, hb2+0.06, hx, yd+hh*0.62, 0, m(C.vindu));
    kloss(hl2+0.5, 0.16, hb2+0.5, hx, yd+hh+0.08, 0, m(C.tak));
    // baugrampa: ei rød plate hengslet i baugen på dekkshøyde; oppe under overfarten, nede på flytebrygga ved kai
    const rampe=new THREE.Group(); rampe.position.set(hl,yd,0); g.add(rampe);
    { const k=new THREE.Mesh(new THREE.BoxGeometry(R.lengde,0.08,R.bredde),m(C.skrog)); k.position.set(R.lengde/2,0,0); k.castShadow=k.receiveShadow=true; rampe.add(k); }
    // åpent dekk mellom styrhuset og rampa, med rekke: tynne stolper og en topplist; åpning i baugen for rampa
    const rx0=hl-fb-0.2, rx1=hx+hl2/2+0.1, rl=rx0-rx1;
    [1,-1].forEach(sd=>{ kloss(rl, 0.05, 0.05, (rx0+rx1)/2, yd+M.rekke, sd*(hb-0.2), m(C.rekke)); for(let i=0;i<=3;i++) kloss(0.05, M.rekke, 0.05, rx1+rl*i/3, yd+M.rekke/2, sd*(hb-0.2), m(C.rekke)); });
    [1,-1].forEach(sd=>kloss(0.05, 0.05, (B-0.4-R.bredde)/2, rx0, yd+M.rekke, sd*((B-0.4)/2-(B-0.4-R.bredde)/4), m(C.rekke)));
    // (regel 19) båtene kaster ikke i skyggekartet: det skal stå stille når kartet står, og en båt i fart ville tegnet det på nytt hele tiden
    g.traverse(o=>{ o.castShadow=false; });
    g.scale.setScalar(SK); g.position.y=VANN_Y; scene.add(g);
    let sistR=-1;
    const rampeTil=v=>{ if(Math.abs(v-sistR)<1e-4) return; sistR=v; rampe.rotation.z=THREE.MathUtils.degToRad(R.oppe_grader+(R.nede_grader-R.oppe_grader)*v); };   // 0 oppe, 1 nede
    return {g, rampeTil};
  }
  // ---- geometri: kaiplasser og veier i modellplanet (x øst, y nord) ----
  const V2=(x,y)=>new THREE.Vector2(x,y);
  function kaiplass(k){ const ut=V2(k.ut[0],k.ut[1]).normalize(), tupp=V2(k.tupp[0],k.tupp[1]);
    return {p:tupp.clone().addScaledVector(ut,k.baug+HL), ut, h:Math.atan2(-ut.y,-ut.x), navn:k.navn, quay:k.quay}; }   // baugen (+x) mot land
  function vei(punkter, bak, snu){   // Catmull-Rom (sentripetal) gjennom punktene; bak: båten rygger ut fra kai og svinger rundt mellom snu[0] og snu[1] meter
    const c=new THREE.CatmullRomCurve3(punkter.map(p=>new THREE.Vector3(p.x,0,p.y)),false,'centripetal'); const lengde=c.getLength();
    return {c, lengde, bak, s0:snu?snu[0]/lengde:0, s1:snu?snu[1]/lengde:0};
  }
  const myk=x=>{ x=THREE.MathUtils.clamp(x,0,1); return x*x*(3-2*x); };
  function poseLangs(v, d){   // d = andel av veiens lengde
    d=THREE.MathUtils.clamp(d,0,1); const p=v.c.getPointAt(d), t=v.c.getTangentAt(d); let h=Math.atan2(t.z,t.x);
    if(v.bak) h+=Math.PI*(1-myk((d-v.s0)/(v.s1-v.s0)));   // akterenden først ut fra kai, så rundt (alltid samme vei rundt)
    return {x:p.x, y:p.z, h};
  }
  const R803=F.ruter['803'], R805=F.ruter['805'];
  const KAI={G:kaiplass(R803.kaier.G), C:kaiplass(R803.kaier.C), S:kaiplass(R805.kai)};
  const ut=k=>KAI[k].p.clone().addScaledVector(KAI[k].ut, R803.ut_m);
  const VEI={
    GC: vei([KAI.G.p, ut('G'), ut('C'), KAI.C.p], true, R803.snu_m),
    CG: vei([KAI.C.p, ut('C'), ut('G'), KAI.G.p], true, R803.snu_m),
    ut805: vei([KAI.S.p, KAI.S.p.clone().addScaledVector(KAI.S.ut,R805.bak_m), ...R805.ut.map(p=>V2(p[0],p[1]))], true, R805.snu_m),
    inn805: vei([...R805.inn.map(p=>V2(p[0],p[1])), KAI.S.p.clone().addScaledVector(KAI.S.ut,R805.inn_kai_m), KAI.S.p], false),
  };
  // tidsforløp langs en tur: 803 myk start og stopp; 805 myk start ut fra kai og myk stopp inn, full fart i papirkanten
  const GANG={ GC:myk, CG:myk, ut805:s=>s*s*(2-s), inn805:s=>1-(1-s)*(1-s)*(1+s) };
  // ---- klokka (Oslo) ----
  const osloForskyv=t=>{ const d=new Date(t); const s=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Oslo',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'}).format(d);
    const [a,b]=s.split(' '), [Y,Mo,D]=a.split('-').map(Number), [h,mi,se]=b.split(':').map(Number); return Date.UTC(Y,Mo-1,D,h,mi,se)-Math.floor(t/1000)*1000; };
  const osloMidnatt=t=>{ const o=osloForskyv(t), l=t+o; return l-(((l%86400000)+86400000)%86400000)-o; };
  const hhmm=s=>{ const [h,mi]=s.split(':').map(Number); return (h*60+mi)*MIN; };
  let forskyv=0; const ft=Q0.get('fergetid'), FRYS=Q0.get('fergefrys')==='1', T0=Date.now();
  if(ft && /^\d{1,2}:\d{2}(:\d{2})?$/.test(ft)){ const [h,mi,se=0]=ft.split(':').map(Number); forskyv=osloMidnatt(T0)+((h*60+mi)*60+se)*1000-T0; }
  const klokke=()=>(FRYS?T0:Date.now())+forskyv;   // ?fergefrys=1 holder fergeklokka stille (skjermbilder)
  const kl=t=>new Date(t).toLocaleTimeString('nb-NO',{timeZone:'Europe/Oslo',hour:'2-digit',minute:'2-digit'});
  // ---- turer: {rute, vei, fra, til, dep, arr, aimDep, aimArr, innstilt, sanntid} ----
  let turer=[], kilde='rutetabell', hentet=0;
  function reserve(T){
    const ut=[], r3=R803.reserve, r5=R805.reserve;
    for(const dag of [osloMidnatt(T)-86400000, osloMidnatt(T)]){
      for(let t=dag+hhmm(r3.fra_C); t<=dag+hhmm(r3.til_C); t+=r3.hvert_min*MIN){
        ut.push({rute:'803', vei:'CG', fra:'C', til:'G', dep:t, arr:t+r3.overfart_min*MIN});
        const g=t+r3.G_etter_min*MIN; ut.push({rute:'803', vei:'GC', fra:'G', til:'C', dep:g, arr:g+r3.overfart_min*MIN}); }
      let forste=true;
      for(let t=dag+hhmm(r5.fra); t<=dag+hhmm(r5.til); t+=r5.hvert_min*MIN){
        ut.push({rute:'805', vei:'ut805', fra:'S', dep:t, arr:t+R805.til_smertu_min*MIN});
        if(!forste){ const a=t-r5.ankomst_for_min*MIN; ut.push({rute:'805', vei:'inn805', til:'S', dep:a-R805.fra_smertu_min*MIN, arr:a}); } forste=false; }
    }
    return ut.map(x=>({...x, aimDep:x.dep, aimArr:x.arr, innstilt:false, sanntid:false}));
  }
  turer=reserve(klokke());
  const E=F.entur||{};
  async function hent(){
    if(Q0.get('entur')==='0' || !E.url) return;
    const T=klokke(), start=new Date(T-(E.bakover_min||20)*MIN).toISOString();
    const felt=`name estimatedCalls(startTime:"${start}", timeRange:${(E.vindu_timer||4)*3600}, numberOfDepartures:60, arrivalDeparture:both, includeCancelledTrips:true){ aimedArrivalTime expectedArrivalTime aimedDepartureTime expectedDepartureTime cancellation realtime forBoarding forAlighting serviceJourney{ id } }`;
    const query=`{ g: quay(id:"${KAI.G.quay}"){ ${felt} } c: quay(id:"${KAI.C.quay}"){ ${felt} } s: quay(id:"${KAI.S.quay}"){ ${felt} } }`;
    const ac=new AbortController(); const tid=setTimeout(()=>ac.abort(), 8000);
    try{
      const r=await fetch(E.url,{method:'POST', headers:{'Content-Type':'application/json','ET-Client-Name':E.klient}, body:JSON.stringify({query}), signal:ac.signal});
      const d=(await r.json()).data; if(!d||!d.g||!d.c||!d.s) throw new Error('tomt svar');
      const ms=s=>s?Date.parse(s):null, ny=[];
      // 803: hver tur har ett anrop på hver kai; avgangskaia er den med påstigning
      const per=new Map(); [['G',d.g],['C',d.c]].forEach(([k,q])=>q.estimatedCalls.forEach(c=>{ const id=c.serviceJourney.id; if(!per.has(id)) per.set(id,{}); per.get(id)[c.forBoarding?'fra':'til']={k,c}; }));
      per.forEach(({fra,til})=>{ if(!fra||!til) return;
        ny.push({rute:'803', vei:fra.k+til.k, fra:fra.k, til:til.k, dep:ms(fra.c.expectedDepartureTime), arr:ms(til.c.expectedArrivalTime), aimDep:ms(fra.c.aimedDepartureTime), aimArr:ms(til.c.aimedArrivalTime), innstilt:!!(fra.c.cancellation||til.c.cancellation), sanntid:!!fra.c.realtime}); });
      // 805: avgang (påstigning) går til Smertu; ankomst (bare avstigning) kommer fra Smertu
      d.s.estimatedCalls.forEach(c=>{
        if(c.forBoarding){ const t=ms(c.expectedDepartureTime); ny.push({rute:'805', vei:'ut805', fra:'S', dep:t, arr:t+R805.til_smertu_min*MIN, aimDep:ms(c.aimedDepartureTime), innstilt:!!c.cancellation, sanntid:!!c.realtime}); }
        else if(c.forAlighting){ const t=ms(c.expectedArrivalTime); ny.push({rute:'805', vei:'inn805', til:'S', dep:t-R805.fra_smertu_min*MIN, arr:t, aimArr:ms(c.aimedArrivalTime), innstilt:!!c.cancellation, sanntid:!!c.realtime}); } });
      // tomt svar er et svar: om natta går ingen av dem (803 ligger da ved Cicignon)
      ny.sort((a,b)=>a.dep-b.dep); turer=ny; kilde='entur'; hentet=klokke(); oppfrisk();
    }catch(e){ if(kilde!=='entur'){ turer=reserve(klokke()); } console.warn('[ferge] Entur svarte ikke:', e.message||e); }
    finally{ clearTimeout(tid); }
  }
  const oppfrisk=()=>{ if(kort_.apent && kort_.ferge) fyllFergeKort(kort_.ferge); };   // åpent fergekort får de nye tidene med en gang (16)
  hent(); setInterval(hent, (E.hvert_sek||120)*1000);
  addEventListener('visibilitychange', ()=>{ if(document.visibilityState==='visible' && klokke()-hentet>60000) hent(); });
  // ---- tilstand ved tid T: {x, y, h, r (rampe 0 oppe, 1 nede), vis, beveger} ----
  const rampeVed=(T,arr,dep)=>myk(arr==null?1:(T-arr-2000)/4000)*(1-myk(dep==null?0:(T-(dep-9000))/4000));
  function turPose(tur,T){ const s=THREE.MathUtils.clamp((T-tur.dep)/Math.max(1,tur.arr-tur.dep),0,1); return poseLangs(VEI[tur.vei], GANG[tur.vei](s)); }
  function tilstand803(T){
    const ts=turer.filter(t=>t.rute==='803' && !t.innstilt);
    const naa=ts.find(t=>t.dep<=T && T<t.arr); if(naa) return {...turPose(naa,T), r:0, vis:true, beveger:true, tur:naa};
    let forr=null; for(const t of ts) if(t.arr<=T && (!forr||t.arr>forr.arr)) forr=t;
    const neste=ts.find(t=>t.dep>T);
    const k=KAI[forr?forr.til:(neste?neste.fra:'C')];
    const r=rampeVed(T, forr?forr.arr:null, neste?neste.dep:null);
    return {x:k.p.x, y:k.p.y, h:k.h, r, vis:true, beveger:r>0.001&&r<0.999, ved:k.navn, neste};
  }
  function tilstand805(T){
    const ts=turer.filter(t=>t.rute==='805' && !t.innstilt);
    const naa=ts.filter(t=>t.dep<=T && T<t.arr).sort((a,b)=>(a.vei==='ut805'?a.dep:b.dep)-(a.vei==='ut805'?b.dep:a.dep))[0];   // står to på veien, vises den nærmest kai
    if(naa) return {...turPose(naa,T), r:0, vis:true, beveger:true, tur:naa};
    let inn=null; for(const t of ts) if(t.vei==='inn805' && t.arr<=T && (!inn||t.arr>inn.arr)) inn=t;
    const ut_=ts.find(t=>t.vei==='ut805' && t.dep>T);
    const ved = ut_ && (ut_.dep-T<=10*MIN || (inn && inn.arr>ut_.dep-25*MIN));
    if(!ved) return {vis:false, beveger:false};
    const k=KAI.S, r=rampeVed(T, inn&&inn.arr>ut_.dep-25*MIN?inn.arr:null, ut_.dep);
    return {x:k.p.x, y:k.p.y, h:k.h, r, vis:true, beveger:r>0.001&&r<0.999, ved:k.navn, neste:ut_};
  }
  // ---- båtene i scenen ----
  const baater={'803':{...byggBaat('ferge-803'), tilstand:tilstand803}, '805':{...byggBaat('ferge-805'), tilstand:tilstand805}};
  Object.entries(baater).forEach(([id,b])=>{ b.g.userData.ferge=id; b.vist=null; b.blend=null; });
  let beveg=false, intro=null, modus=null;
  const vinkel=(a,b,k)=>{ let d=((b-a)%(2*Math.PI)+3*Math.PI)%(2*Math.PI)-Math.PI; return a+d*k; };
  function sett(b, p){
    b.g.visible=!!p.vis; if(!p.vis){ b.vist=null; return; }
    b.g.position.x=p.x; b.g.position.z=-p.y; b.g.rotation.y=p.h; b.rampeTil(p.r);
    b.g.position.y=VANN_Y+(p.beveger?0.05*Math.sin(klokke()/700):0);   // svak dupp i fart
    b.vist={...p};
  }
  // introen: 803 sin siste overfart (eller den den er midt i) spilles av og lander der båten er når introen slutter
  function settIntro(ms){
    const T=klokke()+ms, s=tilstand803(T);
    if(s.tur){ const sl=THREE.MathUtils.clamp((T-s.tur.dep)/Math.max(1,s.tur.arr-s.tur.dep),0,1); intro={tur:s.tur, dEnd:GANG[s.tur.vei](sl), ferdig:false}; return; }
    const ts=turer.filter(t=>t.rute==='803' && !t.innstilt && t.arr<=T); const forr=ts.sort((a,b)=>b.arr-a.arr)[0];
    intro = forr ? {tur:forr, dEnd:1, ferdig:true} : null;
  }
  function introPose(u){
    if(!intro) return null;
    let d, r=0;
    if(intro.ferdig){ let a=THREE.MathUtils.clamp((u-F.fart.start)/(F.fart.slutt-F.fart.start),0,1); d=1-Math.pow(1-a,2.2);
      r=myk((u-R.ned[0])/(R.ned[1]-R.ned[0])); }
    else d=intro.dEnd*(1-Math.pow(1-THREE.MathUtils.clamp(u,0,1),2));
    return {...poseLangs(VEI[intro.tur.vei], d), r, vis:true, beveger:true};
  }
  // u: introens framdrift 0..1, eller null når introen er ferdig (sanntid). Bytte fra intro til sanntid glir over på 1,2 s.
  function til(u){
    if(u!=null && !intro) settIntro(0);
    const T=klokke(), nyModus=u==null?'live':'intro'; beveg=false;
    for(const [id,b] of Object.entries(baater)){
      let p=(id==='803' && u!=null) ? (introPose(u)||b.tilstand(T)) : b.tilstand(T);
      if(modus && nyModus!==modus && b.vist && p.vis) b.blend={fra:{...b.vist}, t0:performance.now()};
      if(b.blend){ const k=myk((performance.now()-b.blend.t0)/1200), f=b.blend.fra;
        if(k>=1 || !p.vis) b.blend=null; else p={...p, x:f.x+(p.x-f.x)*k, y:f.y+(p.y-f.y)*k, h:vinkel(f.h,p.h,k), r:f.r+(p.r-f.r)*k, beveger:true}; }
      sett(b,p); if(p.beveger) beveg=true;
    }
    modus=nyModus;
  }
  // klikk: strålen mot båtene
  const grupper=Object.values(baater).map(b=>b.g);
  function treff(ray){ const h=ray.intersectObjects(grupper.filter(g=>g.visible),true)[0]; if(!h) return null; let g=h.object; while(g && !g.userData.ferge) g=g.parent; return g?{id:g.userData.ferge, d:h.distance}:null; }
  // kortet: navn, strekning, hvor båten er, og de neste avgangene
  function tidTekst(t, tid, aim){ if(t.innstilt) return `${kl(aim||tid)} innstilt`; const f=aim!=null?Math.round((tid-aim)/MIN):0; return f>=1 ? `${kl(tid)} (${f} min forsinket)` : kl(tid); }
  function kort(id){
    const T=klokke(), ru=F.ruter[id], s=baater[id].tilstand(T), ts=turer.filter(t=>t.rute===id);
    const avg=(f,n)=>ts.filter(t=>f(t) && (t.innstilt?(t.aimDep||t.dep):t.dep)>T-30000).slice(0,n);
    let status='', linjer=[];
    if(id==='803'){
      const navn=k=>KAI[k].navn;
      if(s.tur) status=`På vei til ${navn(s.tur.til)}, fram ${kl(s.tur.arr)}`;
      else status=`Ved ${s.ved}${s.neste?`, går ${kl(s.neste.dep)}`:''}`;
      ['G','C'].forEach(k=>{ const a=avg(t=>t.fra===k,4); linjer.push(`Fra ${navn(k)}: ${a.length?a.map(t=>tidTekst(t,t.dep,t.aimDep)).join(' · '):'ingen de neste timene'}`); });
    } else {
      if(s.tur) status = s.tur.vei==='ut805' ? `På vei til Smertu og Sentrum, gikk ${kl(s.tur.dep)}` : `På vei inn, fram ${kl(s.tur.arr)}`;
      else if(s.vis) status=`Ved kaia${s.neste?`, går ${kl(s.neste.dep)}`:''}`;
      const a=avg(t=>t.vei==='ut805',4), i=ts.filter(t=>t.vei==='inn805' && t.arr>T).slice(0,4);
      linjer.push(`Avgang: ${a.length?a.map(t=>tidTekst(t,t.dep,t.aimDep)).join(' · '):'ingen de neste timene'}`);
      if(i.length) linjer.push(`Ankomst: ${i.map(t=>tidTekst(t,t.arr,t.aimArr)).join(' · ')}`);
    }
    const kildeT = kilde==='entur' ? `Sanntid fra Entur, hentet ${kl(hentet)}` : 'Rutetabell (Entur svarer ikke nå)';
    return {tittel:ru.navn, a:`Linje ${ru.linje} • ${ru.strekning}`, b:status, linjer, id:kildeT};
  }
  window.__ferge={turer:()=>turer, kilde:()=>kilde, tilstand:id=>baater[id].tilstand(klokke()), klokke, hent, vist:id=>baater[id].vist, skjerm:id=>{ const g=baater[id].g; return g.visible?window.__skjerm(g.position.x,g.position.z):null; }};
  til(null);
  return {til, intro:settIntro, beveger:()=>beveg, treff, kort, grupper};
})();
registrer({ ferge: () => ferge });   // brukes av tidligere moduler via SENERE (tilstand.js)
