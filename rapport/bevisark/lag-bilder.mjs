// Bevisark: tar modellbilder forfra (az 40) og bakfra (az 220) for hver tegning i én nettleserøkt.
// Bruk: node lag-bilder.mjs <index.html> <views.json> <utmappe>
// views.json: [{n, cx, cy, zoom}, ...]  (modellkoordinater i meter, x øst, y nord)
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, viewsFile, utdir] = process.argv; const dir=path.dirname(file);
const W=1000, H=700;
const views=JSON.parse(fs.readFileSync(viewsFile,'utf8'));
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:W,height:H}}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'}); await page.waitForTimeout(5000);
const cdp=await ctx.newCDPSession(page);
fs.mkdirSync(utdir,{recursive:true});
for(const v of views){
  for(const [az,navn] of [[40,'forfra'],[220,'bakfra']]){
    const ut=path.join(utdir,`${v.n}-${navn}.png`);
    if(fs.existsSync(ut)){ console.log('finnes',ut); continue; }
    const t0=Date.now();
    await page.evaluate(a=>window.__vis(...a),[az,v.zoom,v.cx,v.cy]); await page.waitForTimeout(3500);
    const {data}=await cdp.send('Page.captureScreenshot',{format:'png'});
    fs.writeFileSync(ut,Buffer.from(data,'base64'));
    console.log('ok',ut,((Date.now()-t0)/1000).toFixed(0)+'s','feil',errs.length);
  }
}
await browser.close(); server.close();
