// måler hvor lang tid ett styrt bilde tar
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const file=process.argv[2]; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const page=await (await browser.newContext({viewport:{width:640,height:400}})).newPage();
page.on('console',m=>{ if(m.type()==='error') console.log('console', m.text().slice(0,120)); });
await page.addInitScript(()=>{ let T=1000; const koe=[]; performance.now=()=>T; Date.now=()=>1.7e12+T;
  window.requestAnimationFrame=cb=>{ koe.push(cb); return koe.length; }; window.cancelAnimationFrame=()=>{};
  window.__tick=dt=>{ T+=dt; const k=koe.splice(0); k.forEach(cb=>{ try{ cb(T); }catch(e){ console.error(e); } }); return koe.length; }; });
let t=Date.now(); await page.goto(`http://127.0.0.1:${port}/index.html?nivaa=2`,{waitUntil:'load'}); console.log('last', Date.now()-t, 'ms');
for(let i=0;i<5;i++){ t=Date.now(); const n=await page.evaluate(()=>window.__tick(33)); console.log('tick', i, Date.now()-t, 'ms, kø', n); }
t=Date.now(); await page.screenshot({path:'../rapport/lys/prove.jpg', type:'jpeg', quality:80}); console.log('skjermbilde', Date.now()-t,'ms');
await browser.close(); server.close();
