// Finner hvite bilder under bevegelse: dra, animer hjem, og mål lysheten i hvert bilde. Bruk: node blink-test.mjs <index.html> [W H]
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, W='1100', H='750'] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+W,height:+H}}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&noadapt=1`,{waitUntil:'load'}); await page.waitForTimeout(4000);
// lysheten måles i selve canvaset (readPixels via toDataURL går ikke uten preserveDrawingBuffer): bruk CDP-skjermbilde
const cdp=await ctx.newCDPSession(page);
async function lys(){ const {data}=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:40}); const b=Buffer.from(data,'base64'); fs.writeFileSync('/tmp/blink.jpg',b); const {execSync}=await import('node:child_process'); return +execSync(`python3 -c "from PIL import Image,ImageStat;print(round(ImageStat.Stat(Image.open('/tmp/blink.jpg').convert('L')).mean[0],1))"`).toString(); }
console.log('i ro', await lys());
await page.mouse.move(550,400); await page.mouse.down(); for(let i=1;i<=6;i++){ await page.mouse.move(550+i*30,400+i*10); console.log('dra', i, await lys()); } await page.mouse.up();
await page.evaluate(()=>window.__hjem()); for(let i=1;i<=5;i++){ console.log('hjem', i, await lys()); }
console.log('feil', JSON.stringify(errs));
await browser.close(); server.close();
