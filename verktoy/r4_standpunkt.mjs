// Runde 4: 6 faste standpunkt, instant __vis-kamera (deterministisk), skjermbilde per standpunkt.
// Bruk: PW_GPU=1 node verktoy/r4_standpunkt.mjs <index.html> <ut-mappe>
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir = path.dirname(file);
const W = 1280, H = 720;
const STAND = [
  { navn: '1-v75krysset', az: 200, z: 3.6, tx: 122, ty: 66 },
  { navn: '2-theresem',   az: 110, z: 3.8, tx: 128, ty: 66 },
  { navn: '3-torvet',     az: 200, z: 2.8, tx: 21,  ty: 50 },
  { navn: '4-kirkegaten', az: 250, z: 3.4, tx: 78,  ty: 126 },
  { navn: '5-raadhus',    az: 30,  z: 3.4, tx: 115, ty: 68 },
  { navn: '6-toihuset',   az: 200, z: 3.2, tx: -57, ty: -131 },
];
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', p.endsWith('.json') ? 'application/json' : p.endsWith('.js') ? 'text/javascript' : 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
fs.mkdirSync(ut, { recursive: true });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 }); const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&vaer=sol`, { waitUntil: 'load' });
await page.waitForTimeout(6000);
const still = async () => { for (let i = 0; i < 60; i++) { await page.waitForTimeout(250); if (!(await page.evaluate(() => map.isMoving()))) break; } await page.waitForTimeout(2000); };
for (const s of STAND) {
  await page.evaluate(v => window.__vis(v.az, v.z, v.tx, v.ty), s);
  await still();
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(ut, `${s.navn}.png`), Buffer.from(data, 'base64'));
  console.log('bilde', s.navn);
}
console.log('FEIL', JSON.stringify(feil.slice(0, 5)));
await browser.close(); server.close();
