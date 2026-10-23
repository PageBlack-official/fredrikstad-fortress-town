// Prøver intro, klikk på hus, huskort, hjem, styreflate-flytting og dobbeltklikk i hodeløs Chromium.
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const file=process.argv[2]; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const ctx=await browser.newContext({viewport:{width:900,height:600}}); const page=await ctx.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message+' @ '+(e.stack||'').split('\n').slice(0,3).join(' | ')));
const cdp=await ctx.newCDPSession(page); const shot=async n=>{ const {data}=await cdp.send('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(`ut/ia-${n}.png`,Buffer.from(data,'base64')); };
await page.goto(`http://127.0.0.1:${port}/index.html`); await page.waitForTimeout(1500);
const k0=await page.evaluate(()=>window.__kam()); await shot('intro'); await page.waitForTimeout(6000);
const k1=await page.evaluate(()=>window.__kam()); console.log('intro: underveis az',k0.az.toFixed(2),'zoom',k0.zoom.toFixed(2),'→ ferdig az',k1.az.toFixed(2),'zoom',k1.zoom.toFixed(2),'intro',k1.intro);
// klikk på kirka
const kp=await page.evaluate(()=>window.__skjerm3(-14.8,8,58.9)); await page.mouse.click(kp[0],kp[1]); await page.waitForTimeout(1500);
const kort=await page.evaluate(()=>({vis:document.getElementById('kort').classList.contains('vis'), navn:document.querySelector('#kort h2').textContent})); console.log('klikk kirka:',JSON.stringify(kort));
await shot('kort');
// hjem via Esc
await page.keyboard.press('Escape'); await page.waitForTimeout(1500); const k2=await page.evaluate(()=>window.__kam()); console.log('esc → hjem: x',k2.x.toFixed(1),'z',k2.z.toFixed(1),'zoom',k2.zoom.toFixed(2),'kort vis',await page.evaluate(()=>document.getElementById('kort').classList.contains('vis')));
// styreflate: to fingre sidelengs (wheel med deltaX)
await page.evaluate(()=>{ const el=map.getCanvas(); for(let i=0;i<10;i++) el.dispatchEvent(new WheelEvent('wheel',{deltaX:-20,deltaY:3,deltaMode:0,bubbles:true,cancelable:true})); });
await page.waitForTimeout(600); const k3=await page.evaluate(()=>window.__kam()); console.log('styreflate-dra: x',k3.x.toFixed(1),'z',k3.z.toFixed(1),'zoom',k3.zoom.toFixed(2));
// musehjul (hakk): zoom
await page.evaluate(()=>{ const el=map.getCanvas(); el.dispatchEvent(new WheelEvent('wheel',{deltaX:0,deltaY:-100,deltaMode:0,bubbles:true,cancelable:true})); });
await page.waitForTimeout(800); const k4=await page.evaluate(()=>window.__kam()); console.log('hjul: zoom',k4.zoom.toFixed(2));
// dobbeltklikk
await page.mouse.dblclick(450,300); await page.waitForTimeout(1200); const k5=await page.evaluate(()=>window.__kam()); console.log('dobbeltklikk: zoom',k5.zoom.toFixed(2),'kort vis',await page.evaluate(()=>document.getElementById('kort').classList.contains('vis')));
// dra med mus = flytt
await page.mouse.move(450,300); await page.mouse.down(); await page.mouse.move(550,350,{steps:8}); await page.mouse.up(); await page.waitForTimeout(800);
const k6=await page.evaluate(()=>window.__kam()); console.log('musedra: x',k6.x.toFixed(1),'z',k6.z.toFixed(1),'az',k6.az.toFixed(2));
await shot('slutt'); console.log('feil',JSON.stringify(errs)); await browser.close(); server.close();
