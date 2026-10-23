// Skjermbilde av en bygd index.html. Bruk: node bilde.mjs <index.html> <ut.png> [az zoom tx ty] [bredde høyde] [ventMs]
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, out, az, z, tx, ty, W='1100', H='750', vent='4000'] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+W,height:+H}}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message)); page.on('console',m=>{ if(m.type()==='error') errs.push('console: '+m.text().slice(0,160)); });
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${process.env.EKSTRA||''}`,{waitUntil:'load'}); await page.waitForTimeout(+vent);
if(az!==undefined){ await page.evaluate(a=>window.__vis(...a),[+az,+z,+tx,+ty]); await page.waitForTimeout(2500); }
const k=await page.evaluate(()=>window.__kam?window.__kam():null);
const cdp=await ctx.newCDPSession(page); const {data}=await cdp.send('Page.captureScreenshot',{format:'png'});
fs.writeFileSync(out,Buffer.from(data,'base64')); console.log('ok',out,'kam',JSON.stringify(k),'feil',JSON.stringify(errs));
await browser.close(); server.close();
