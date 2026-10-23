import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:1100,height:750}}); const page=await ctx.newPage();
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&noadapt=1`,{waitUntil:'load'}); await page.waitForTimeout(4000);
await page.evaluate(()=>map.panBy([300,100],{animate:false})); await page.waitForTimeout(500); await page.evaluate(()=>window.__hjem()); for(const d of [1,2,3,4,5,6]){ await page.waitForTimeout(150); console.log(JSON.stringify(await page.evaluate(()=>({p:map.getPitch(),b:map.getBearing(),z:map.getZoom(),c:map.getCenter(),oye:window.__kam().oye.map(v=>v|0)})))); console.log(JSON.stringify(d), JSON.stringify(await page.evaluate(()=>{const s=window.__sol(); return {sd:s.sd.map(v=>+v.toFixed(4)), q:s.q.map(v=>+v.toFixed(4)), grunner:s.grunner};}))); }
await browser.close(); server.close();
