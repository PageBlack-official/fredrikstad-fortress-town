// Kroner under dra på mobilflate: musedra oppover i 10 steg, skjermbilde ved hvert steg. Bruk: node kroner-dra.mjs <index.html> <utprefiks> [ekstra-param]
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut, ekstra=''] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${ekstra}`,{waitUntil:'load'}); await page.waitForTimeout(4000);
await page.evaluate(()=>window.__vis(40,2.5,40,-20)); await page.waitForTimeout(2500);
const cdp=await ctx.newCDPSession(page);
const shot=async n=>{ const {data}=await cdp.send('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(`${ut}-${n}.png`,Buffer.from(data,'base64')); };
await shot('00');
await page.mouse.move(195,600); await page.mouse.down();
for(let k=1;k<=8;k++){ await page.mouse.move(195,600-k*40,{steps:3}); await page.waitForTimeout(120); await shot(String(k).padStart(2,'0')); const kam=await page.evaluate(()=>{ const k=window.__kam(); return {naer:k.naer.toFixed(1), fjern:k.fjern.toFixed(0), kval:window.__kval()}; }); console.log(k, JSON.stringify(kam)); }
await page.mouse.up(); await page.waitForTimeout(800); await shot('09');
console.log('feil', JSON.stringify(errs)); await browser.close(); server.close();
