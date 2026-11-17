// dag/natt fra samme gatekamera: node dagnatt.mjs <index.html> <standpunkter.json> <utdir> [navn...]
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, punktFil, utdir, ...bare] = process.argv;
const dir = path.dirname(file); const W=1280, H=720;
let punkter = JSON.parse(fs.readFileSync(punktFil,'utf8')); if (bare.length) punkter = punkter.filter(p=>bare.includes(p.navn));
const server = http.createServer((q,r)=>{ const u=q.url.split('?')[0]; const p=path.join(dir,u==='/'?'index.html':u); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser = await chromium.launch({ args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
fs.mkdirSync(utdir,{recursive:true});
for (const [tag, q] of [['dag','tid=13:00&vaer=sol'],['natt','tid=22:30&vaer=sol']]) {
  const ctx = await browser.newContext({ viewport:{width:W,height:H}, deviceScaleFactor:1 }); const page = await ctx.newPage();
  const feil=[]; page.on('pageerror',e=>feil.push(e.message));
  await page.goto(`http://127.0.0.1:${port}/${path.basename(file)}?skip=1&${q}`,{waitUntil:'load'});
  await page.waitForFunction(()=>typeof window.__gate==='function',null,{timeout:60000});
  await page.waitForTimeout(6000);
  await page.addStyleTag({content:'#hjem,#hint,#kort,#lekkasje,.maplibregl-ctrl,#vaer,#vaerknapp{display:none!important}'});
  for (const p of punkter) {
    await page.evaluate(a=>window.__gate(a),{lat:p.lat,lon:p.lon,heading:p.heading,pitch:Math.min(p.pitch??88.5,88.5),fov:p.fov??75,oye:p.oye??2.5});
    let f=''; for(let i=0;i<40;i++){ await page.waitForTimeout(250); const k=await page.evaluate(()=>JSON.stringify(window.__gateKamera())); if(k===f) break; f=k; }
    await page.waitForTimeout(2500);
    await page.screenshot({path:path.join(utdir,`${p.navn}_${tag}.png`)});
    console.log(tag, p.navn, JSON.stringify(await page.evaluate(()=>window.__vaer&&window.__vaer().natt)));
  }
  if (feil.length) console.log('JS-feil', feil.slice(0,3));
  await ctx.close();
}
await browser.close(); server.close();
