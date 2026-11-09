// Oversiktsbilde av kartet med skjermpunkt for en liste hus, til dom-ark der husene ringes inn (09.11).
// Bruk: PW_GPU=1 node verktoy/oversikt_ring.mjs ut/enkel/index.html <utmappe> <lat> <lon> <heading> <pitch> <oye> <fov> id1 id2 ...
// Skriver <utmappe>/oversikt.png og oversikt.json {id: [x,y]}; hus utenfor bildet mangler i json.
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, utdir, lat, lon, heading, pitch, oye, fov, ...ider] = process.argv;
const dir = path.dirname(file);
const W = +(process.env.BREDDE || 1800), H = +(process.env.HOYDE || 1200);
const typer = { '.json': 'application/json', '.js': 'text/javascript', '.png': 'image/png', '.html': 'text/html; charset=utf-8' };
const server = http.createServer((q, r) => { const u = q.url.split('?')[0]; const p = path.join(dir, u === '/' ? 'index.html' : u); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', typer[path.extname(p)] || 'application/octet-stream'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 }); const page = await ctx.newPage();
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${port}/${path.basename(file)}?skip=1`, { waitUntil: 'load' });
await page.waitForFunction(() => typeof window.__gate === 'function', null, { timeout: 60000 });
await page.waitForTimeout(4000);
await page.addStyleTag({ content: '#hjem,#hint,#kort,#lekkasje,.maplibregl-ctrl,.maplibregl-marker{display:none!important}' });
await page.evaluate(a => window.__gate(a), { lat: +lat, lon: +lon, heading: +heading, pitch: +pitch, fov: +fov, oye: +oye });
let forrige = '';
for (let i = 0; i < 40; i++) { await page.waitForTimeout(250); const k = await page.evaluate(() => JSON.stringify(window.__gateKamera())); if (k === forrige) break; forrige = k; }
await page.waitForTimeout(5000);
fs.mkdirSync(utdir, { recursive: true });
await page.screenshot({ path: path.join(utdir, 'oversikt.png') });
const hus = await page.evaluate(() => window.__gateHus());
const ut = {}; for (const h of hus) if (ider.includes(h.id)) ut[h.id] = h.skjerm;
fs.writeFileSync(path.join(utdir, 'oversikt.json'), JSON.stringify(ut, null, 1));
console.log('funnet', Object.keys(ut).length, 'av', ider.length, 'mangler:', ider.filter(i => !ut[i]).join(' '));
if (feil.length) console.log('JS-feil:', feil.slice(0, 5).join(' | '));
await browser.close(); server.close();
