// Intromåler (13.11, Vegar: «introen lagger på Mac-en»): laster siden UTEN ?skip, logger hvert bilde fra første egne bilde
// til introen er ferdig (TILSTAND.introDone via window.__klar), og gir bildetid (median, p95, maks), antall bilder over 33 ms
// og 50 ms, og tida til første bilde. Med GPU=finish venter siden på GPU-en etter hvert pass (ekte GPU-tid per pass).
// Bruk: PW_GPU=1 node verktoy/intro_maal.mjs <ut.json> <navn>=<index.html> [...]   (miljø: RUNDER=3, BREDDE, HOYDE, DPR, GPU)
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, utfil, ...varianter] = process.argv;
const V = varianter.map(a => { const [n, f] = a.split('='); return { navn: n, fil: path.resolve(f) }; });
const RUNDER = +(process.env.RUNDER || 3), W = +(process.env.BREDDE || 1280), H = +(process.env.HOYDE || 720), DPR = +(process.env.DPR || 2);
const server = http.createServer((q, r) => { const navn = q.url.split('?')[0].slice(1).split('/')[0]; const v = V.find(x => x.navn === navn);
  if (v) { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(v.fil)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const med = a => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const p95 = a => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]; };
const snitt = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
const res = { vindu: { W, H, DPR }, runder: RUNDER, maal: {}, feil: [] };
async function en(v) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR }); const page = await ctx.newPage();
  page.on('pageerror', e => res.feil.push(v.navn + ': ' + e.message));
  await page.addInitScript(g => { window.__logg = []; window.__kl = []; window.__tLast = performance.now(); if (g) window.__maal = g === 'finish' ? true : 'les'; }, process.env.GPU || '');
  await page.goto(`http://127.0.0.1:${port}/${v.navn}/index.html`);
  await page.waitForFunction(() => window.map && window.__kartBilder > 0, null, { timeout: 600000 });
  await page.evaluate(() => map.on('render', () => window.__kl.push(performance.now())));
  await page.waitForFunction(() => window.__klar && window.__klar(), null, { timeout: 120000, polling: 200 });
  await page.waitForTimeout(500);
  const d = await page.evaluate(() => ({ logg: window.__logg, kl: window.__kl, forste: window.__logg.length ? window.__logg[0].t - window.__tLast : null }));
  await ctx.close();
  const L = d.logg.filter(x => x && x.r != null), K = d.kl; const iv = []; for (let i = 1; i < K.length; i++) iv.push(K[i] - K[i - 1]);
  const f = k => +snitt(L.map(x => x[k] || 0)).toFixed(2);
  return { bilder: L.length, forsteBilde_ms: Math.round(d.forste || 0), lag_med: +med(L.map(x => x.r)).toFixed(1), lag_p95: +p95(L.map(x => x.r)).toFixed(1), lag_maks: +Math.max(0, ...L.map(x => x.r)).toFixed(1),
    side_med: +med(iv).toFixed(1), side_p95: +p95(iv).toFixed(1), side_maks: +Math.max(0, ...iv).toFixed(1), over33: iv.filter(x => x > 33.4).length, over50: iv.filter(x => x > 50).length,
    oppdater: f('o'), speil: f('sp'), skygge: f('sk'), scene: f('s'), blekk: f('b'), fxaa: f('f'), skyggeBilder: L.filter(x => x.sk > 0).length };
}
for (let r = 0; r < RUNDER; r++) for (const v of (r % 2 ? [...V].reverse() : V)) {
  const ut = await en(v); (res.maal[v.navn] ||= []).push(ut);
  console.log(`runde ${r + 1} ${v.navn}: side ${ut.side_med}/${ut.side_p95}/${ut.side_maks} ms, >33 ${ut.over33}, >50 ${ut.over50}, lag ${ut.lag_med} ms, 3D ${ut.scene} blekk ${ut.blekk} skygge ${ut.skygge} (${ut.skyggeBilder} bilder), første ${ut.forsteBilde_ms} ms`);
}
res.median = {}; for (const v of V) { const rs = res.maal[v.navn]; const o = {}; for (const k of Object.keys(rs[0])) o[k] = med(rs.map(x => x[k])); res.median[v.navn] = o; }
fs.mkdirSync(path.dirname(utfil), { recursive: true }); fs.writeFileSync(utfil, JSON.stringify(res, null, 1));
for (const v of V) console.log('MEDIAN', v.navn, JSON.stringify(res.median[v.navn]));
if (res.feil.length) console.log('FEIL:', res.feil.slice(0, 5));
await browser.close(); server.close();
