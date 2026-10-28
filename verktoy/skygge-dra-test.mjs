// Skyggekartet under dra (regel 19): dekning mot bildets radius, og hvor mange ganger kartet tegnes på nytt per bilde under et dra.
// Bruk: node verktoy/skygge-dra-test.mjs <index.html> <ut.json> [az] [zoom]   (skriver også <ut>-a/-b.png: før og etter dra)
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut, azS='40', zS='2.5'] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:900,height:600}, deviceScaleFactor:1}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'}); await page.waitForTimeout(4000);
const res={}; const sol=async()=>page.evaluate(()=>{ const s=window.__sol(); return {grunner:{...s.grunner}, R:s.R, r:s.r, bilder:window.__vaareBilder}; });
for(const z of [1.2, 2.5, 5]){
  const n0=await page.evaluate(()=>window.__vaareBilder);
  await page.evaluate(({a,z})=>window.__vis(a,z,40,-20),{a:+azS,z});
  await page.waitForFunction(n=>window.__vaareBilder>=n+3, n0, {timeout:120000});   // vent til bildet faktisk er tegnet med den nye visningen (programvare-GPU er treg)
  const s0=await sol();
  // bilder i ro: tegnes kartet på nytt uten grunn?
  await page.waitForFunction(n=>window.__vaareBilder>=n+5, s0.bilder, {timeout:120000}); const s1=await sol();
  // dra 40 skjermpunkter (innenfor marginen)
  await page.mouse.move(450,300); await page.mouse.down(); await page.mouse.move(490,300,{steps:8}); await page.mouse.up(); await page.waitForFunction(n=>window.__vaareBilder>=n+3, s1.bilder, {timeout:120000});
  const s2=await sol();
  const diff=(a,b)=>Object.fromEntries(Object.keys(b.grunner).map(k=>[k,(b.grunner[k]||0)-(a.grunner[k]||0)]).filter(([,v])=>v));
  res['zoom'+z]={R:s0.R, r:s0.r, dekning:+(s0.R/s0.r).toFixed(2), iRo:diff(s0,s1), iRoBilder:s1.bilder-s0.bilder, dra:diff(s1,s2), draBilder:s2.bilder-s1.bilder};
}
fs.writeFileSync(ut, JSON.stringify({res, feil:errs},null,1)); console.log(JSON.stringify(res));
await browser.close(); server.close();
