// Én kvalitet: oppløsning, hjørneskygge og strek skal være like mens musa drar og når den slippes. Bruk: node kvalitet-test.mjs <index.html>
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:1100,height:750}}); const page=await ctx.newPage();
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&noadapt=1`,{waitUntil:'load'}); await page.waitForTimeout(4000);
const k=()=>page.evaluate(()=>window.__kval());
const ro1=await k();
await page.mouse.move(550,400); await page.mouse.down();
let fart=null; for(let i=1;i<=12;i++){ await page.mouse.move(550+i*8,400+i*4); await page.waitForTimeout(60); if(i===8) fart=await k(); }
await page.mouse.up(); await page.waitForTimeout(900);
const ro2=await k();
const lik=(a,b)=>a.skala===b.skala && a.ao===b.ao && a.ss===b.ss;
console.log('i ro før  ', JSON.stringify(ro1)); console.log('under dra ', JSON.stringify(fart)); console.log('i ro etter', JSON.stringify(ro2));
console.log(lik(ro1,fart)&&lik(fart,ro2) ? 'OK   én kvalitet i fart og i ro' : 'FEIL kvaliteten byttet');
await browser.close(); server.close();
