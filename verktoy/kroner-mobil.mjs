// Trekroner på mobil: klyp og dra med to fingre (CDP touch), skjermbilde underveis, teller kronegrønt per bilde.
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium, devices } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({...devices['iPhone 13'], deviceScaleFactor:2}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'}); await page.waitForTimeout(5000);
const cdp=await ctx.newCDPSession(page);
const shot=async n=>{ const {data}=await cdp.send('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(`${ut}-${n}.png`,Buffer.from(data,'base64')); const g=await page.evaluate(()=>{ const c=document.createElement('canvas'); const src=map.getCanvas(); c.width=src.width; c.height=src.height; return null; }); return n; };
const touch=async(type, pts)=>cdp.send('Input.dispatchTouchEvent',{type, touchPoints:pts.map((p,i)=>({x:p[0],y:p[1],id:i}))});
const kroner=async()=>page.evaluate(()=>{ const gl=map.getCanvas().getContext('webgl2'); const w=gl.drawingBufferWidth,h=gl.drawingBufferHeight; const px=new Uint8Array(w*h*4); gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px); let n=0; for(let i=0;i<px.length;i+=16){ const r=px[i],g=px[i+1],b=px[i+2]; if(g>r+20&&g>b+20&&g<180&&g>90) n++; } return n; });
map: {
}
await page.evaluate(()=>map.triggerRepaint()); await page.waitForTimeout(300);
console.log('i ro', await kroner());
// klyp ut og inn
const cx=195, cy=420; let logg=[];
await touch('touchStart',[[cx-40,cy],[cx+40,cy]]);
for(let k=1;k<=12;k++){ const d=40+k*8; await touch('touchMove',[[cx-d,cy],[cx+d,cy]]); await page.waitForTimeout(60); logg.push(await kroner()); if(k===6) await shot('klyp'); }
await touch('touchEnd',[]); await page.waitForTimeout(400); logg.push(await kroner());
console.log('klyp', logg.join(' '));
logg=[]; await touch('touchStart',[[cx-40,cy],[cx+40,cy]]);
for(let k=1;k<=12;k++){ await touch('touchMove',[[cx-40,cy-k*10],[cx+40,cy-k*10]]); await page.waitForTimeout(60); logg.push(await kroner()); if(k===6) await shot('dra2'); }
await touch('touchEnd',[]); await page.waitForTimeout(400); logg.push(await kroner());
console.log('to-finger-dra', logg.join(' '));
logg=[]; await touch('touchStart',[[cx,cy]]);
for(let k=1;k<=12;k++){ await touch('touchMove',[[cx+k*12,cy+k*6]]); await page.waitForTimeout(60); logg.push(await kroner()); if(k===6) await shot('dra1'); }
await touch('touchEnd',[]); await page.waitForTimeout(400); logg.push(await kroner());
console.log('en-finger-dra', logg.join(' '));
console.log('feil', JSON.stringify(errs)); await browser.close(); server.close();
