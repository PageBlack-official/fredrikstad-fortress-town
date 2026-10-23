import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const file=process.argv[2]; const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const ctx=await browser.newContext({viewport:{width:900,height:600}}); const page=await ctx.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`); await page.waitForTimeout(3000);
await page.keyboard.press('d');
await page.mouse.move(450,300);
if(!process.env.BAREHJUL) for(let i=0;i<8;i++){ await page.mouse.wheel(-30,4); await page.waitForTimeout(30); }
await page.waitForTimeout(600); const k3=await page.evaluate(()=>window.__kam()); console.log('styreflate (wheel dx=-30,dy=4 x8): x',k3.x.toFixed(1),'z',k3.z.toFixed(1),'zoom',k3.zoom.toFixed(2));
await page.waitForTimeout(300);
await page.waitForTimeout(+(process.env.VENT||300)); await page.mouse.wheel(0,-120); await page.waitForTimeout(900); await page.mouse.wheel(0,-120); await page.waitForTimeout(900); const k4=await page.evaluate(()=>window.__kam()); console.log('hjulhakk (dy=-120): zoom',k4.zoom.toFixed(2));
const logg=await page.evaluate(()=>document.querySelector('pre')?document.querySelector('pre').textContent.split('\n').slice(2).join(' | '):'ingen'); console.log('logg:',logg.slice(0,600));
console.log('feil',JSON.stringify(errs)); await browser.close(); server.close();
