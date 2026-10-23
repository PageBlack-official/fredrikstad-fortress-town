// D-test: tegnekall før/etter, klikk på hus (løft), peker (hover), kirke-nærbilde. Bruk: node d-test.mjs <index.html> <utprefiks>
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:1100,height:750}}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message)); page.on('console',m=>{ if(m.type()==='error') errs.push('console: '+m.text().slice(0,160)); });
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'}); await page.waitForTimeout(4000);
const pt=await page.evaluate(()=>({kall:window.__pt.kall, tri:window.__pt.tri}));
console.log('tegnekall', pt.kall, 'trekanter', pt.tri);
const shot=async n=>{ const cdp=await ctx.newCDPSession(page); const {data}=await cdp.send('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(`${ut}-${n}.png`,Buffer.from(data,'base64')); await cdp.detach(); };
// klikk midt i bildet, litt opp: skal treffe et hus
await page.mouse.click(550,420); await page.waitForTimeout(1500);
const k=await page.evaluate(()=>window.__kam()); const kort=await page.evaluate(()=>({vis:document.getElementById('kort').classList.contains('vis'), h2:document.querySelector('#kort h2').textContent}));
console.log('klikk: valgt', JSON.stringify(k.valgt), 'kort', JSON.stringify(kort));
await shot('klikk');
await page.keyboard.press('Escape'); await page.waitForTimeout(1200);
await page.mouse.move(400,450); await page.waitForTimeout(300); await page.mouse.move(402,452); await page.waitForTimeout(900);
const cur=await page.evaluate(()=>map.getCanvas().style.cursor); console.log('peker over', JSON.stringify(cur));
await page.evaluate(()=>window.__vis(40,4,60,40)); await page.waitForTimeout(2500); await shot('naer');
console.log('feil', JSON.stringify(errs));
await browser.close(); server.close();
