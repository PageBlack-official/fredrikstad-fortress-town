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
for(const [navn, forst, en] of [['oppvarming (telles ikke)',0,true],['én finger, kontroll: ekte kast virker',0,true],['venstre tommel slipper først',0,false],['høyre tommel slipper først',1,false],['venstre tommel slipper først, igjen',0,false]]){
  const r=await page.evaluate(async ([forst,en])=>{
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
    vent(5); send('touchend', []);
    map.jumpTo({center:ref}); const p0=map.project(ref);
    map.easeTo({center:map.getCenter(), noMoveStart:true, freezeElevation:true, duration:500}, {originalEvent:{type:'touchend'}});
    await new Promise(r=>setTimeout(r,12000)); const p1=map.project(ref);
    return {dx:p1.x-p0.x, dy:p1.y-p0.y};
  }, [forst,en]);
  const hopp=Math.hypot(r.dx,r.dy), legit=150*0.26;   // ekte fart × tau (BEV.treghet)
  const ok = en ? hopp>legit*0.5 && hopp<legit*2 : hopp<legit*2;
  if(!ok && !navn.startsWith('oppvarming')) feil++;
  console.log(`${ok?'OK  ':'FEIL'} ${navn}: kartet gled ${hopp.toFixed(0)} px etter slipp (${r.dx.toFixed(0)}, ${r.dy.toFixed(0)}); ekte fart gir ca. ${legit.toFixed(0)} px`);
}
await browser.close(); server.close(); process.exit(feil?1:0);
