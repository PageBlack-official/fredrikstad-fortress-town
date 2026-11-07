// Kontrollbilder av kartet (07.11): faste utsikter (az, zoom, tx, ty) på PC og mobil. node verktoy/vis-test.mjs ut/enkel/index.html utmappe
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir = path.dirname(file); fs.mkdirSync(ut, { recursive: true });
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const V = JSON.parse(process.env.VIS_FIL ? fs.readFileSync(process.env.VIS_FIL, 'utf8') : (process.env.VIS || '[]'));
const browser = await chromium.launch();
// nettbrett (07.11): NETTBRETT=1 tar også iPad-format (820 × 1180, berøring)
for (const [navn, vp, mob] of [['pc', { width: 1400, height: 900 }, false], ['mobil', { width: 390, height: 844 }, true], ['nettbrett', { width: 820, height: 1180 }, true]]) {
  if (navn === 'mobil' && !process.env.MOBIL) continue;
  if (navn === 'nettbrett' && !process.env.NETTBRETT) continue;
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: mob, hasTouch: mob }); const page = await ctx.newPage();
  const feil = []; page.on('pageerror', e => feil.push(e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`, { waitUntil: 'load' });
  await page.waitForFunction(() => typeof window.__vis === 'function', null, { timeout: 60000 }); await page.waitForTimeout(3000);
  for (const v of V) {
    await page.evaluate(v => window.__vis(v.az, v.zoom, v.tx, v.ty), v); await page.waitForTimeout(2500);
    await page.screenshot({ path: path.join(ut, `${navn}-${v.navn}.jpg`), type: 'jpeg', quality: 75 });
  }
  console.log(navn, 'feil:', feil.slice(0, 3).join(' | ') || 'ingen'); await ctx.close();
}
await browser.close(); server.close();
