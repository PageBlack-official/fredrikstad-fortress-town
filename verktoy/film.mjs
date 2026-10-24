// Film av kartet med styrt klokke: performance.now og requestAnimationFrame byttes ut, og hvert bilde skyver klokka 1/30 s og kjører
// bildekallene selv. Bevegelsen blir riktig uansett hvor treg testmaskinen er (programvare-GPU bruker sekunder per bilde). Manus: intro → dobbeltklikk (zoom inn) → klikk på hus (kort, glidning) → Esc (hjem). Bruk: node film.mjs <index.html> <ut.mp4> [sek]
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { execSync } from 'node:child_process';
const [,, file, ut, sekArg='11'] = process.argv; const dir=path.dirname(file); const FPS=+(process.env.FPS||20), SEK=+sekArg;
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.json')?'application/json':p.endsWith('.js')?'text/javascript':'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:+(process.env.W||640),height:+(process.env.H||400)}}); const page=await ctx.newPage();
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.addInitScript(()=>{ let T=1000; const koe=[]; const p0=performance.now.bind(performance);
  performance.now=()=>T; Date.now=()=>1.7e12+T;
  window.requestAnimationFrame=cb=>{ koe.push(cb); return koe.length; }; window.cancelAnimationFrame=()=>{};
  // bildet hentes fra lerretet i samme oppgave som tegningen (tegnebufferet lever bare til oppgaven er ferdig); skjermbilde via CDP tar 15 s per bilde i programvare-GPU
  window.__tick=(dt,bilde)=>{ T+=dt; const k=koe.splice(0); k.forEach(cb=>{ try{ cb(T); }catch(e){ console.error(e); } }); if(!bilde) return koe.length; const c=document.querySelector('#kart canvas'); return c ? c.toDataURL('image/jpeg',0.9) : null; };
  window.__ekte=p0; });
await page.goto(`http://127.0.0.1:${port}/index.html?${process.env.EKSTRA||'nivaa=2'}`,{waitUntil:'load'}); await page.waitForTimeout(1500);
for(let i=0;i<10;i++){ await page.evaluate(()=>window.__tick(16)); }   // la kartet laste og laget komme på plass
await page.addStyleTag({content:'#hint{display:none!important}'});
const rammer=path.join(path.dirname(ut),'_rammer'); fs.rmSync(rammer,{recursive:true,force:true}); fs.mkdirSync(rammer,{recursive:true});
const steg=async()=>page.evaluate(dt=>window.__tick(dt,true), 1000/FPS);
const manus={ [Math.round(5.2*FPS)]: async()=>page.mouse.dblclick(520,330), [Math.round(7.4*FPS)]: async()=>{ await page.mouse.click(430,300); }, [Math.round(9.2*FPS)]: async()=>page.keyboard.press('Escape') };
const N=SEK*FPS;
for(let i=0;i<N;i++){ if(manus[i]) await manus[i](); const url=await steg(); if(url) fs.writeFileSync(path.join(rammer,`r${String(i).padStart(4,'0')}.jpg`),Buffer.from(url.split(',')[1],'base64')); if(i%30===0) process.stdout.write(`${i/FPS}s `); }
console.log('\nfeil', JSON.stringify(errs));
await browser.close(); server.close();
execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i "${rammer}/r%04d.jpg" -c:v libx264 -pix_fmt yuv420p -crf 20 "${ut}"`);
fs.rmSync(rammer,{recursive:true,force:true}); console.log('film', ut);
