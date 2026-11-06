// Lenka husker utsikten (02.11): #view=lat,lon,zoom,pitch,bearing og &hus=<bygg-id>.
// Bruk: node verktoy/lenke_test.mjs ut/enkel/index.html [mappe for skjermbilder]   (exit 1 ved første feil)
// (a) view= setter kameraet, og hashen ryddes etter landing  (b) hus=pb-68 åpner kortet  (c) flytting skriver ikke hashen (06.11: intro ved
// hver ny lasting)  (d) lukk lukker  (e) ugyldige hasher krasjer ikke og gir ingen utsikt utenfor kartet  (f) nettleserens tilbake lukker kortet
// (g) «Del» kopierer lenka med view= og hus=  (h) uten hash går introen som før
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const file=process.argv[2]; const utDir=process.argv[3]||path.join(path.dirname(file),'..'); const dir=path.dirname(file);
const server=http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type', p.endsWith('.html')?'text/html; charset=utf-8':'application/octet-stream'); r.end(fs.readFileSync(p)); } else { r.statusCode=404; r.end(); } });
await new Promise(r=>server.listen(0,'127.0.0.1',r)); const port=server.address().port; const BASE=`http://127.0.0.1:${port}/index.html`;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const ctx=await browser.newContext({viewport:{width:1100,height:750}, permissions:['clipboard-read','clipboard-write']});
const T0=Date.now(); let feil=0; const sjekk=(navn,ok,info='')=>{ console.log(`${ok?'OK  ':'FEIL'} ${((Date.now()-T0)/1000)|0}s ${navn}${info?'  '+info:''}`); if(!ok) feil++; };
async function side(hash, query=''){
  const page=await ctx.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message));
  await page.goto(`${BASE}${query}${hash}`,{waitUntil:'load'}); await page.waitForFunction(()=>window.__kam && window.map && map.loaded(), null, {timeout:60000});
  return {page, errs};
}
// venter til kameraet står (programvare-GPU: mange sekunder per bilde)
async function ro(page, maks=60000){ const t0=Date.now(); await page.waitForTimeout(400); while(Date.now()-t0<maks){ const k=await page.evaluate(()=>({anim:map.isMoving(), intro:window.__kam().intro})); if(!k.anim && !k.intro) break; await page.waitForTimeout(300); } await page.waitForTimeout(300); }
const kamera=page=>page.evaluate(()=>{ const c=map.getCenter(); return {lat:c.lat, lon:c.lng, zoom:map.getZoom(), pitch:map.getPitch(), bearing:map.getBearing(), kam:window.__kam()}; });
const hash=page=>page.evaluate(()=>decodeURIComponent(location.hash));
const skjerm=async(page,n)=>{ const cdp=await page.context().newCDPSession(page); const {data}=await cdp.send('Page.captureScreenshot',{format:'png'}); const p=path.join(utDir,n); fs.writeFileSync(p,Buffer.from(data,'base64')); console.log('     bilde', p); };

// (a) view= setter kameraet, introen hoppes over
const V={lat:59.20262, lon:10.95215, zoom:17.6, pitch:52, bearing:-140};
{ const {page,errs}=await side(`#view=${V.lat},${V.lon},${V.zoom},${V.pitch},${V.bearing}`);
  await ro(page); const k=await kamera(page);
  const ok=Math.abs(k.lat-V.lat)<1e-5 && Math.abs(k.lon-V.lon)<1e-5 && Math.abs(k.zoom-V.zoom)<0.01 && Math.abs(k.pitch-V.pitch)<0.5 && Math.abs(k.bearing-V.bearing)<0.5;
  const kOk=Math.abs(k.kam.az-(-V.bearing*Math.PI/180))<0.01 && Math.abs(k.kam.pol-V.pitch*Math.PI/180)<0.01 && !k.kam.intro;
  sjekk('(a) view= setter kameraet', ok && kOk, `lat ${k.lat.toFixed(5)} lon ${k.lon.toFixed(5)} zoom ${k.zoom.toFixed(2)} pitch ${k.pitch.toFixed(1)} bearing ${k.bearing.toFixed(1)}; __kam az ${k.kam.az.toFixed(3)} pol ${k.kam.pol.toFixed(3)} intro ${k.kam.intro}`);
  sjekk('(a) hashen er ryddet etter landing', (await hash(page))==='', await hash(page));
  await page.waitForTimeout(1500); await skjerm(page,'lenke-a.png');
  // (c) flytt kameraet: hashen følger når kameraet har stoppet, og historikken vokser ikke
  const lengde0=await page.evaluate(()=>history.length);
  await page.evaluate(()=>map.jumpTo({center:[10.9535,59.2031], zoom:17.2, bearing:30, pitch:45})); await ro(page);
  const h=await hash(page);
  sjekk('(c) flytting skriver ikke hashen', h==='', h);
  // musedra (ekte gest), så hashen etter at kartet har stoppet
  await page.mouse.move(550,400); await page.mouse.down(); await page.mouse.move(450,350,{steps:8}); await page.mouse.up(); await ro(page);
  const h2=await hash(page), k2=await kamera(page);
  sjekk('(c) dra med mus skriver ikke hashen', h2==='' && !!k2, h2);
  sjekk('(c) replaceState: ingen nye historikkinnslag', await page.evaluate(()=>history.length)===lengde0);
  sjekk('(a,c) ingen JS-feil', errs.length===0, errs.join(' | '));
  await page.close(); }

// (b) hus=pb-68 åpner kortet (Tøihuset, nordfløya), (d) lukk fjerner hus=, (g) Del
{ const {page,errs}=await side('#hus=pb-68');
  await ro(page); await page.waitForTimeout(1500);
  const kort=await page.evaluate(()=>({vis:document.getElementById('kort').classList.contains('vis'), navn:document.querySelector('#kort h2').textContent, valgt:window.__kam().valgt}));
  sjekk('(b) hus=pb-68 åpner kortet', kort.vis && kort.navn==='Tøihuset, nordfløya', JSON.stringify(kort));
  const h=await hash(page); sjekk('(b) hashen er ryddet etter landing', h==='', h);
  // kameraet står på huset (huset midt i flaten kortet ikke dekker)
  const fri=await page.evaluate(()=>{ const k=document.getElementById('kort'); return {x0:k.offsetLeft+k.offsetWidth+16, x1:innerWidth, y1:innerHeight}; });
  sjekk('(b) kameraet har landet på huset', kort.valgt && Math.abs(kort.valgt[0]-(fri.x0+fri.x1)/2)<80 && Math.abs(kort.valgt[1]-fri.y1/2)<80, `huset på skjermen ${kort.valgt&&kort.valgt.map(v=>v|0)}`);
  await skjerm(page,'lenke-b.png');
  // (g) Del: lenka i utklippstavla er den samme som i adresselinja, og knappen viser haken
  await page.click('#kort .del'); await page.waitForTimeout(300);
  const delt=await page.evaluate(async()=>({tekst:await navigator.clipboard.readText(), haken:document.querySelector('#kort .del').classList.contains('delt'), knapp:document.querySelector('#kort .del').textContent}));
  sjekk('(g) Del kopierer lenka med view= og hus=', new RegExp('^'+BASE.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'#view=[-\\d.]+,[-\\d.]+,[\\d.]+,\\d+,-?\\d+&hus=pb-68$').test(decodeURIComponent(delt.tekst)) && delt.haken && delt.knapp==='Del', JSON.stringify(delt));
  // (d) lukk kortet med ×: hus= forsvinner
  await page.click('#kort .lukk'); await ro(page); await page.waitForTimeout(500);
  const hd=await hash(page); sjekk('(d) etter lukk er hashen ren', hd==='', hd);
  sjekk('(d) kortet er lukket', !(await page.evaluate(()=>document.getElementById('kort').classList.contains('vis'))));
  // (f) klikk på huset igjen (som en bruker), så nettleserens tilbake: kortet lukkes og hus= forsvinner
  const pk=await page.evaluate(()=>window.__skjerm3(-70,2.5,93));   // midt på nordfløya (modell x -70, y -93, halv vegghøyde)
  await page.mouse.click(pk[0],pk[1]); await page.waitForTimeout(400);
  const aapen=await page.evaluate(()=>document.getElementById('kort').classList.contains('vis'));
  await ro(page);
  const hf=await hash(page);
  sjekk('(f) kortet åpnet igjen', aapen, hf);
  await page.goBack(); await ro(page); await page.waitForTimeout(600);
  const etter=await page.evaluate(()=>({vis:document.getElementById('kort').classList.contains('vis'), hash:decodeURIComponent(location.hash), url:location.pathname}));
  sjekk('(f) tilbake lukker kortet, siden står', !etter.vis && !etter.hash.includes('hus=') && etter.url.endsWith('index.html'), JSON.stringify(etter));
  sjekk('(b,d,f,g) ingen JS-feil', errs.length===0, errs.join(' | '));
  await page.close(); }

// (e) ugyldige hasher: ingen krasj, ingen utsikt utenfor kartet; tall utenfor grensene klemmes
for(const [h, forventet] of [
  ['#view=abc,def,1,2,3', 'intro'], ['#view=59.2,10.95', 'intro'], ['#view=NaN,10.95,17,50,0', 'intro'], ['#view=,,,,', 'intro'],
  ['#view=60.5,10.95,17,50,0', 'intro'],          // senter 140 km unna: ignoreres
  ['#view=1e400,10.95,17,50,0', 'intro'], ['#hus=finnes-ikke', 'intro'], ['#hus=<script>', 'intro'], ['#view=%E0%A4%A', 'intro'],
  ['#view=59.20262,10.95215,99,999,-9999', 'klemt'] ]){
  const {page,errs}=await side(h,'?tegn=0');
  await page.waitForTimeout(1200);
  const k=await kamera(page);
  const r=await page.evaluate(()=>({min:map.getMinZoom(), max:map.getMaxZoom(), maxP:map.getMaxPitch()}));
  let ok=errs.length===0;
  if(forventet==='intro') ok = ok && k.kam.intro;   // introen går som uten hash
  else ok = ok && !k.kam.intro && Math.abs(k.zoom-r.max)<0.01 && Math.abs(k.pitch-r.maxP)<0.5 && Math.abs(k.bearing-(((-9999%360)+540)%360-180))<0.5;
  sjekk(`(e) ugyldig ${h}`, ok, `${forventet}: intro ${k.kam.intro} zoom ${k.zoom.toFixed(2)} pitch ${k.pitch.toFixed(0)} bearing ${k.bearing.toFixed(0)} ${errs.join(' | ')}`);
  await page.close(); }

// (h) uten hash: introen som før, og hashen skrives først når introen er ferdig
{ const {page,errs}=await side('','?tegn=0');
  await page.waitForTimeout(800);
  const k=await kamera(page), h=await hash(page);
  sjekk('(h) uten hash: introen går, ingen hash underveis', k.kam.intro && h==='', `intro ${k.kam.intro} hash «${h}»`);
  sjekk('(h) ingen JS-feil', errs.length===0, errs.join(' | '));
  await page.close(); }

// sandbox: history og localStorage som kaster (claude.ai-artefakten) – kartet skal virke og kortet åpnes
{ const page=await ctx.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message));
  await page.addInitScript(()=>{ const kast=()=>{ throw new DOMException('sandbox','SecurityError'); };
    history.replaceState=kast; history.pushState=kast; Object.defineProperty(window,'localStorage',{get:kast}); });
  await page.goto(`${BASE}?tegn=0#view=59.20262,10.95215,17.6,52,-140&hus=pb-68`,{waitUntil:'load'}); await page.waitForFunction(()=>window.__kam && map.loaded(), null, {timeout:60000});
  await ro(page); await page.waitForTimeout(1000);
  const kort=await page.evaluate(()=>({vis:document.getElementById('kort').classList.contains('vis'), navn:document.querySelector('#kort h2').textContent}));
  await page.evaluate(()=>map.jumpTo({zoom:17})); await ro(page);
  await page.click('#kort .lukk'); await ro(page);
  sjekk('(sandbox) uten history/localStorage: kortet åpnes og lukkes uten feil', kort.vis && kort.navn==='Tøihuset, nordfløya' && errs.length===0, JSON.stringify(kort)+' '+errs.join(' | '));
  await page.close(); }

await browser.close(); server.close();
console.log(feil ? `${feil} feil` : 'alle lenkesjekkene er grønne');
process.exit(feil?1:0);
