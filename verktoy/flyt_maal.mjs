// Flytmåler (02.11): ms per bilde i vårt lag og i hele siden, i ro, under panorering, zoom og klikk på hus (kortet inn), med samme kamera
// for to eller flere bygg side om side (før/etter). Rundene går på omgang mellom byggene, så støy fra maskinen fordeles likt.
// Programvare-GPU (swiftshader) gir ikke ekte bildefrekvens, men forholdet før/etter og fordelingen på delene er nyttig.
// Bruk: node verktoy/flyt_maal.mjs <ut.json> <navn>=<index.html> [<navn>=<index.html> ...]   (miljø: RUNDER=3, SCEN=ro,roNaer,pan,zoom,klikk, GPU=1 venter på GPU-en etter hvert pass
//       ved å lese én piksel (GPU=finish: gl.finish som tast m), BREDDE/HOYDE/DPR for vinduet)
// Per bilde logger siden (15_loop: window.__logg): r = hele render() i laget, o = oppdater(), sp = speilpasset, sk = skyggekartet,
// s/b/f = 3D-passet, blekkstrek+AO og FXAA (01_etterbehandling). «hele siden» er tida mellom kartets bilder (map 'render').
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, utfil, ...varianter] = process.argv;
const V = varianter.map(a => { const [n, f] = a.split('='); return { navn: n, fil: path.resolve(f) }; });
const RUNDER = +(process.env.RUNDER || 3), GPU = !!process.env.GPU, W = +(process.env.BREDDE || 900), H = +(process.env.HOYDE || 560), DPR = +(process.env.DPR || 1);
const server = http.createServer((q, r) => { const navn = q.url.split('?')[0].slice(1).split('/')[0]; const v = V.find(x => x.navn === navn);
  if (v) { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(v.fil)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const HJEM = [200, 1.3, 25, 25];   // hjemmevisningen (az, zoomfaktor, tx, ty)
const SCEN = (process.env.SCEN || 'ro,roNaer,pan,zoom,klikk').split(',');
const KLIKK = (process.env.KLIKK || '').split(',').filter(Boolean).map(Number);
const res = { vindu: { W, H, DPR }, gpu: GPU, runder: RUNDER, varianter: V.map(v => v.navn), maal: {}, feil: [] };

async function still(page, ms = 1500) { const t0 = Date.now(); while (Date.now() - t0 < 120000) { await page.waitForTimeout(250); if (!(await page.evaluate(() => map.isMoving()))) break; } await page.waitForTimeout(ms); }
async function hjem(page) { await page.evaluate(a => window.__vis(...a), HJEM); await still(page, 2000); }
async function start(page) { await page.evaluate(() => { window.__logg = []; window.__kl = []; window.__t0 = performance.now(); if (!window.__klPaa) { window.__klPaa = 1; map.on('render', () => { if (window.__kl) window.__kl.push(performance.now()); }); } }); }
async function slutt(page) { return page.evaluate(() => { const d = { logg: window.__logg, kl: window.__kl, ms: performance.now() - window.__t0 }; window.__logg = null; window.__kl = null; return d; }); }
const med = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const p95 = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]; };
const snitt = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
function oppsummer(d) {
  const L = d.logg || [], K = d.kl || []; const iv = []; for (let i = 1; i < K.length; i++) iv.push(K[i] - K[i - 1]);
  const f = k => +((snitt(L.map(x => x[k] || 0)) || 0).toFixed(2));
  return { ms: Math.round(d.ms), vaare: L.length, kart: K.length, perSek: +(L.length * 1000 / d.ms).toFixed(2),
    ramme_med: +(med(L.map(x => x.r)) || 0).toFixed(1), ramme_snitt: +(snitt(L.map(x => x.r)) || 0).toFixed(1), ramme_p95: +(p95(L.map(x => x.r)) || 0).toFixed(1),
    side_med: +(med(iv) || 0).toFixed(1), side_p95: +(p95(iv) || 0).toFixed(1),
    oppdater: f('o'), speil: f('sp'), skygge: f('sk'), scene: f('s'), blekk: f('b'), fxaa: f('f'), speilBilder: L.filter(x => x.sp > 0).length, skyggeBilder: L.filter(x => x.sk > 0).length };
}
async function finnHus(page) {
  // et skjermpunkt som treffer et hus i hjemmevisningen (kortet åpnes); samme punkt brukes for alle byggene
  for (const [fx, fy] of [[0.5, 0.5], [0.45, 0.55], [0.55, 0.45], [0.4, 0.5], [0.6, 0.5], [0.5, 0.6], [0.5, 0.4], [0.35, 0.6], [0.65, 0.4]]) {
    const x = Math.round(W * fx), y = Math.round(H * fy); await page.mouse.click(x, y); await page.waitForTimeout(600);
    if (await page.evaluate(() => document.getElementById('kort').classList.contains('vis'))) { await page.keyboard.press('Escape'); await still(page, 800); return [x, y]; }
    await page.waitForTimeout(400); }
  return null;
}
async function scenarier(v) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR }); const page = await ctx.newPage();
  page.on('pageerror', e => res.feil.push(v.navn + ': ' + e.message));
  await page.goto(`http://127.0.0.1:${port}/${v.navn}/index.html?skip=1`);
  await page.waitForFunction(() => window.__kam && window.__vaareBilder > 2, null, { timeout: 600000 });
  if (GPU) await page.evaluate(m => { window.__maal = m; }, process.env.GPU === 'finish' ? true : 'les');
  await hjem(page); const ut = {};
  // (a) ro: kartet står i hjemmevisningen (vannet i bildet)
  if (SCEN.includes('ro')) { await start(page); await page.waitForTimeout(4000); ut.ro = oppsummer(await slutt(page)); }
  // (a2) ro tett på et hus inne i byen (zoom 4: lite eller ikke noe vann i bildet)
  if (SCEN.includes('roNaer')) { await page.evaluate(() => window.__vis(200, 4, 40, 40)); await still(page, 2000);
  await start(page); await page.waitForTimeout(4000); ut.roNaer = oppsummer(await slutt(page));
  await hjem(page); }
  // (b) panorering: musa drar 240 px på ca. 1,2 s, så tregheten
  if (SCEN.includes('pan')) { await start(page); await page.mouse.move(W / 2, H / 2); await page.mouse.down();
  for (let i = 1; i <= 24; i++) { await page.mouse.move(W / 2 - i * 10, H / 2 - i * 3); await page.waitForTimeout(50); }
  await page.mouse.up(); await still(page, 300); ut.pan = oppsummer(await slutt(page));
  await hjem(page); }
  // (c) zoom: tre hjulhakk midt i bildet (egen fjær, 15_bevegelse)
  if (SCEN.includes('zoom')) { await start(page); await page.mouse.move(W / 2, H / 2);
  for (let i = 0; i < 3; i++) { await page.mouse.wheel(0, -100); await page.waitForTimeout(100); }
  await still(page, 300); ut.zoom = oppsummer(await slutt(page));
  await hjem(page); }
  // (d) klikk på hus: huset løfter seg, kameraet glir inn og kortet glir inn
  if (SCEN.includes('klikk')) { if (!res.klikk) res.klikk = KLIKK.length ? KLIKK : await finnHus(page);
  if (res.klikk) { await start(page); await page.mouse.click(...res.klikk); await page.waitForTimeout(300); await still(page, 300); ut.klikk = oppsummer(await slutt(page));
    ut.klikk.kortVis = await page.evaluate(() => document.getElementById('kort').classList.contains('vis')); await page.keyboard.press('Escape'); await still(page, 300); } }
  await ctx.close(); return ut;
}
for (let r = 0; r < RUNDER; r++) for (const v of (r % 2 ? [...V].reverse() : V)) {
  const ut = await scenarier(v); (res.maal[v.navn] ||= []).push(ut);
  console.log(`runde ${r + 1} ${v.navn}: ` + Object.entries(ut).map(([k, m]) => `${k} ${m.ramme_med} ms/${m.side_med} ms ${m.perSek}/s`).join(' | '));
}
// median over rundene per tall
res.median = {};
for (const v of V) { const rs = res.maal[v.navn]; const o = {}; for (const sc of Object.keys(rs[0])) { o[sc] = {}; for (const k of Object.keys(rs[0][sc])) { const xs = rs.map(x => x[sc] && x[sc][k]).filter(x => typeof x === 'number'); o[sc][k] = xs.length ? med(xs) : rs[0][sc][k]; } } res.median[v.navn] = o; }
fs.mkdirSync(path.dirname(utfil), { recursive: true }); fs.writeFileSync(utfil, JSON.stringify(res, null, 1));
for (const sc of Object.keys(res.median[V[0].navn])) console.log(sc.padEnd(7), V.map(v => { const m = res.median[v.navn][sc]; return `${v.navn}: lag ${m.ramme_med} ms (p95 ${m.ramme_p95}), side ${m.side_med} ms (p95 ${m.side_p95}), ${m.perSek} bilder/s, oppd ${m.oppdater} speil ${m.speil} skygge ${m.skygge} 3D ${m.scene} blekk ${m.blekk} fxaa ${m.fxaa}`; }).join('  ||  '));
if (res.feil.length) console.log('FEIL:', res.feil.slice(0, 5));
await browser.close(); server.close();
