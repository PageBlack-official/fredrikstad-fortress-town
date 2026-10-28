// Stillbilder av «sola finner byen» ved u = 0, 0.25, 0.5, 0.75, 1 langs introens kameravei (programvare-GPU-en er for treg til å se introen i fart).
// Bruk: node verktoy/sol-intro-stills.mjs <index.html> <utmappe>
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir=path.dirname(file); fs.mkdirSync(ut,{recursive:true});
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type','text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:900,height:600}}); const page=await ctx.newPage();
const errs=[]; page.on("pageerror",e=>errs.push(e.message)); page.on("console",m=>{ if(m.type()==="error") errs.push(m.text().slice(0,300)); });
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`,{waitUntil:'load'}); await page.waitForTimeout(3000);
const cdp=await ctx.newCDPSession(page);
const frames=async n=>{ const n0=await page.evaluate(()=>window.__vaareBilder); await page.waitForFunction(k=>window.__vaareBilder>=k, n0+n, {timeout:240000}); };
for(const u of [0,0.25,0.5,0.75,1]){
  await page.evaluate(u=>window.__introStill(u), u);
  await frames(3);
  const {data}=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:85}); fs.writeFileSync(`${ut}/u${u}.jpg`,Buffer.from(data,'base64'));
  console.log('u', u, await page.evaluate(()=>JSON.stringify({...window.__solvei(), sol:window.__sol().sd.map(v=>+v.toFixed(2))})));
}
// samme kamera (hjemmevisningen), lyset ved u 0 / 0,5 / 1: viser solkanten uten at kameraet flytter seg
for(const u of [0,0.5,1]){
  await page.evaluate(u=>{ window.__introStill(1); window.__solTil(u); }, u); await frames(3);
  const {data}=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:85}); fs.writeFileSync(`${ut}/hjem-u${u}.jpg`,Buffer.from(data,'base64'));
}
console.log('feil', JSON.stringify(errs.slice(0,3))); await browser.close(); server.close();
