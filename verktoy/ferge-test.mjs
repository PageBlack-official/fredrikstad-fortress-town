// Byfergene (22_byferga): skjermbilder og tilstand ved gitte fergetider. Bruk: node ferge-test.mjs <index.html> <ut-mappe> [HH:MM:SS ...]
// Miljø: AZ ZOOM TX TY (kamera), INTRO=sek (introen i sakte film, bilde etter VENT ms), ENTUR=1 (hent sanntid; ellers rutetabellen), KLIKK=1 (klikk på 803 og ta bilde av kortet)
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut, ...tider]=process.argv; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const W=+(process.env.W||1100), H=+(process.env.H||750);
for(const tid of (tider.length?tider:['22:02:30'])){
  const ctx=await browser.newContext({viewport:{width:W,height:H}}); const page=await ctx.newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(e.message)); page.on('console',m=>{ if(['error','warning'].includes(m.type())) errs.push(m.type()+': '+m.text().slice(0,200)); });
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${process.env.INTRO?'&spin='+process.env.INTRO:''}&fergetid=${tid}&fergefrys=1${process.env.TEGN0?'&tegn=0':''}${process.env.ENTUR==='1'?'':'&entur=0'}`,{waitUntil:'load'});
  { const t0=Date.now(); while(Date.now()-t0<60000){ await page.waitForTimeout(500); if(await page.evaluate(()=>window.__klar&&window.__klar()).catch(()=>false)) break; } }
  if(process.env.AZ){ await page.evaluate(a=>window.__vis(...a),[+process.env.AZ,+process.env.ZOOM,+process.env.TX,+process.env.TY]); const t1=Date.now(); while(Date.now()-t1<60000){ await page.waitForTimeout(500); const k=await page.evaluate(()=>window.__kam()); if(!k.anim) break; } }
  await page.waitForTimeout(2500);
  if(process.env.INTRO){ // «Hele Gamlebyen» spiller introen (sakte, ?spin=INTRO sek); bilder underveis
    await page.evaluate(()=>document.getElementById('hjem').onclick()); const t2=Date.now(); const cdp0=await ctx.newCDPSession(page);
    for(const ms of (process.env.VENT||'6000,14000,22000').split(',').map(Number)){ await page.waitForTimeout(Math.max(0,ms-(Date.now()-t2)));
      const v=await page.evaluate(()=>({u:window.__solvei().u, v:window.__ferge.vist('803')})); console.log(' intro', ms, JSON.stringify(v,(k,x)=>typeof x==='number'?Math.round(x*100)/100:x));
      fs.writeFileSync(path.join(ut,`ferge-${tid.replace(/:/g,'')}-intro${ms}.png`),Buffer.from((await cdp0.send('Page.captureScreenshot',{format:'png'})).data,'base64')); }
    const t3=Date.now(); while(Date.now()-t3<120000){ await page.waitForTimeout(500); if(await page.evaluate(()=>window.__klar())) break; } await page.waitForTimeout(2500); }
  if(errs.length) console.log("FEIL", errs.join(" | "));
  const st=await page.evaluate(()=>({kilde:window.__ferge.kilde(), a:window.__ferge.tilstand('803'), b:window.__ferge.tilstand('805')}));
  const rund=o=>JSON.stringify(o,(k,v)=>typeof v==='number'?Math.round(v*10)/10:(k==='tur'||k==='neste')?(v&&{vei:v.vei,dep:new Date(v.dep).toISOString().slice(11,19)}):v);
  console.log(tid, st.kilde, '803', rund(st.a), '805', rund(st.b), errs.length?'FEIL: '+errs.join(' | '):'');
  const navn=tid.replace(/:/g,'');
  const cdp=await ctx.newCDPSession(page); fs.writeFileSync(path.join(ut,`ferge-${navn}.png`),Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  if(process.env.KLIKK){ for(const id of ['803','805']){ const p=await page.evaluate(id=>{ return window.__ferge.skjerm(id); },id).catch(e=>'feil '+e.message);
    if(!p||typeof p==='string'){ console.log('  klikk',id,p); continue; }
    await page.mouse.click(p[0],p[1]-6); await page.waitForTimeout(1500);
    const kt=await page.evaluate(()=>document.querySelector('#kort.vis')?document.querySelector('#kort .innhold').innerText:null); console.log('  kort',id,JSON.stringify(kt));
    fs.writeFileSync(path.join(ut,`ferge-${navn}-kort${id}.png`),Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png'})).data,'base64'));
    await page.keyboard.press('Escape'); await page.waitForTimeout(800); } }
  await ctx.close();
}
await browser.close(); server.close();
