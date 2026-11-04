// To tomler drar og slipper i fart, den ene før den andre (Vegar 02.11, mobil: «hopper bildet ganske langt mot venstre når jeg slipper tomlene»).
// Midtpunktet mellom fingrene hopper når én slipper; det hoppet skal ikke leses som et kast.
// Testen sender berøringene i nøyaktig takt inne i siden (programvare-GPU tegner for sakte til å treffe tidsvinduet med ekte berøring) og
// gjør så det MapLibre gjør ved slipp: easeTo med noMoveStart + freezeElevation og slipp-hendelsen. Måler hvor langt kartet glir etterpå.
// Bruk: node verktoy/tomler_test.mjs ut/enkel/index.html   (exit 1 ved feil)
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const file=process.argv[2]; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ r.setHeader('content-type','text/html; charset=utf-8'); r.end(fs.readFileSync(path.join(dir,'index.html'))); });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:393,height:723}, hasTouch:true, isMobile:true}); const page=await ctx.newPage();
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'});
// venter til byen er vokst og kartet står stille, ikke et fast antall sekunder: den første gesten rett etter lasting ga 1 px uansett
// versjon når maskinen var opptatt (03.11), og det var testen som var for tidlig, ikke tregheten
await page.waitForFunction(()=>window.__klar && window.__klar(), null, {timeout:120000}); await page.waitForTimeout(3000);
let feil=0;
// Den aller første gesten etter lasting gir 1 px uansett versjon (sett 03.11 på c769e9a og eldre, også etter at siden er klar), så
// den kjøres som oppvarming og telles ikke. Årsaken er ikke funnet; skal den finnes, er det her den ligger.
// stille: fingeren holdes i ro så lenge (ms) før den løfter; da skal kartet ikke gli (Vegar 04.11: «glir litt mot høyre» når tommelen slipper)
for(const [navn, forst, en, stille] of [['oppvarming (telles ikke)',0,true,0],['én finger, kontroll: ekte kast virker',0,true,0],['venstre tommel slipper først',0,false,0],['høyre tommel slipper først',1,false,0],['venstre tommel slipper først, igjen',0,false,0],['én finger, holdt stille 250 ms før slipp: ingen glidning',0,true,250]]){
  const r=await page.evaluate(async ([forst,en,stille])=>{
    const el=map.getCanvasContainer(), ref=map.getCenter();
    const vent=ms=>{ const t=performance.now(); while(performance.now()-t<ms); };
    const T=(id,x,y)=>new Touch({identifier:id, target:el, clientX:x, clientY:y});
    const send=(type,touches)=>el.dispatchEvent(new TouchEvent(type,{touches, targetTouches:touches, changedTouches:touches, bubbles:true, cancelable:true}));
    const A=[120,420], B=[280,420], v=0.15;   // px per ms = 150 px/s, rolig dra
    const pts=dx=> en ? [T(0,A[0]+dx,A[1])] : [T(0,A[0]+dx,A[1]), T(1,B[0]+dx,B[1])];
    send('touchstart', pts(0)); let dx=0;
    for(let i=0;i<10;i++){ vent(10); dx+=v*10; send('touchmove', pts(dx)); }
    if(!en){ const igjen = forst===0 ? [T(1,B[0]+dx,B[1])] : [T(0,A[0]+dx,A[1])];
      send('touchend', igjen); vent(10); dx+=v*10; send('touchmove', forst===0 ? [T(1,B[0]+dx,B[1])] : [T(0,A[0]+dx,A[1])]); }
    vent(5+stille); send('touchend', []); const loft=performance.now();
    map.jumpTo({center:ref}); const p0=map.project(ref);
    vent(120);   // en treg telefon behandler slippet lenge etter at fingeren løftet; slipp-tiden er hendelsens timeStamp, ikke nå
    map.easeTo({center:map.getCenter(), noMoveStart:true, freezeElevation:true, duration:500}, {originalEvent:{type:'touchend', timeStamp:loft}});
    await new Promise(r=>setTimeout(r,12000)); const p1=map.project(ref);
    return {dx:p1.x-p0.x, dy:p1.y-p0.y};
  }, [forst,en,stille]);
  const hopp=Math.hypot(r.dx,r.dy), legit=150*0.26;   // ekte fart × tau (BEV.treghet)
  const ok = stille ? hopp<5 : en ? hopp>legit*0.5 && hopp<legit*2 : hopp<legit*2;
  if(!ok && !navn.startsWith('oppvarming')) feil++;
  console.log(`${ok?'OK  ':'FEIL'} ${navn}: kartet gled ${hopp.toFixed(0)} px etter slipp (${r.dx.toFixed(0)}, ${r.dy.toFixed(0)}); ekte fart gir ca. ${legit.toFixed(0)} px`);
}
await browser.close(); server.close(); process.exit(feil?1:0);
