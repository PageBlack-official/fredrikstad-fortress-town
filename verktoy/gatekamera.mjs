// Gatekamera (06.11, Vegar: «gå rundt i gatene og dokumenter»): kartet sett fra øyehøyde, fra samme punkt og i samme retning som et
// Street View-bilde, så modell og virkelighet kan legges side om side og leses hus for hus.
// Bruk:  PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html kilder/gate/standpunkter.json rapport/gate [navn ...]
// standpunkter.json: [{navn, pano, dato, lat, lon, heading, pitch, fov, oye}] – tallene rett fra Street View-lenka:
//   …/@59.2029732,10.9560839,10a,75y,285.23h,88.51t/…!1s<pano>… → lat, lon, fov 75 (loddrett, målt 07.11), heading 285.23, pitch 88.51 (90 = vannrett).
//   oye = kamerahøyde over bakken i meter (standard 2,5: Street View-kameraet sitter på biltaket).
// Skriver <utmappe>/<navn>.png og <navn>.json (kamera, bakkehøyde, husene som står i bildet med skjermpunkt).
// Kartet har en egen testinngang window.__gate i src/15_loop.js; den rører ikke kartet slik brukeren ser det.
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
// pitch over 88,5 (vannrett eller opp, som Street View-bildene 93t) kan ikke tegnes: MapLibre regner kameraet fra et senterpunkt på bakken.
const [,, file, punktFil, utdir, ...bare] = process.argv;
if (!file || !punktFil || !utdir) { console.error('bruk: node verktoy/gatekamera.mjs <index.html> <standpunkter.json> <utmappe> [navn ...]'); process.exit(1); }
const dir = path.dirname(file);
const W = +(process.env.BREDDE || 1568), H = +(process.env.HOYDE || 765);   // samme format som et Street View-skjermbilde i Chrome
let punkter = JSON.parse(fs.readFileSync(punktFil, 'utf8')); if (bare.length) punkter = punkter.filter(p => bare.includes(p.navn));
const typer = { '.json': 'application/json', '.js': 'text/javascript', '.png': 'image/png', '.html': 'text/html; charset=utf-8' };
const server = http.createServer((q, r) => { const u = q.url.split('?')[0]; const p = path.join(dir, u === '/' ? 'index.html' : u); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', typer[path.extname(p)] || 'application/octet-stream'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });   // pw.mjs bytter til skjermkortet med PW_GPU=1
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 }); const page = await ctx.newPage();
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${port}/${path.basename(file)}?skip=1`, { waitUntil: 'load' });
await page.waitForFunction(() => typeof window.__gate === 'function', null, { timeout: 60000 });
await page.waitForTimeout(4000);
await page.addStyleTag({ content: '#hjem,#hint,#kort,#lekkasje,.maplibregl-ctrl{display:none!important}' });
fs.mkdirSync(utdir, { recursive: true });
for (const p of punkter) {
  const t0 = Date.now();
  const svar = await page.evaluate(a => window.__gate(a), { lat: p.lat, lon: p.lon, heading: p.heading, pitch: Math.min(p.pitch ?? 88.5, 88.5), fov: p.fov ?? 75, oye: p.oye ?? 2.5 });
  let forrige = '';   // vent til kameraet står: to like avlesninger på rad
  for (let i = 0; i < 40; i++) { await page.waitForTimeout(250); const k = await page.evaluate(() => JSON.stringify(window.__gateKamera())); if (k === forrige) break; forrige = k; }
  await page.waitForTimeout(2000);
  const ut = path.join(utdir, `${p.navn}.png`);
  await page.screenshot({ path: ut });
  const hus = await page.evaluate(() => window.__gateHus());
  fs.writeFileSync(ut.replace(/\.png$/, '.json'), JSON.stringify({ standpunkt: p, kamera: svar, synlige_hus: hus }, null, 1));
  console.log(`OK ${p.navn}  bakke ${(+svar.bakke).toFixed(2)} m  ${hus.length} hus i bildet  ${Date.now() - t0} ms`);
}
if (feil.length) console.log('JS-feil:', feil.slice(0, 5).join(' | '));
await browser.close(); server.close();
