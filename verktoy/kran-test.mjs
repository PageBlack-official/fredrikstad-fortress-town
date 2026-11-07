// Kranløftet (07.11): bilder av introen på faste tider etter lasting, PC og mobil. node verktoy/kran-test.mjs ut/enkel/index.html utmappe
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir = path.dirname(file); fs.mkdirSync(ut, { recursive: true });
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', p.endsWith('.json') ? 'application/json' : p.endsWith('.js') ? 'text/javascript' : p.endsWith('.css') ? 'text/css' : 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch();
for (const [navn, vp, mob] of [['pc', { width: 1280, height: 800 }, false], ['mobil', { width: 390, height: 844 }, true]]) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: mob, hasTouch: mob }); const page = await ctx.newPage();
  const feil = []; page.on('pageerror', e => feil.push(e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html${process.env.Q || ''}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__kam && window.__kam().t > 0.05, null, { timeout: 60000 }).catch(() => {});
  const t0 = Date.now();
  for (const s of [0.3, 1.3, 2.4, 3.6, 4.8, 7.0]) {
    const vent = s * 1000 - (Date.now() - t0); if (vent > 0) await page.waitForTimeout(vent);
    const k = await page.evaluate(() => { const k = window.__kam(); return { pol: k.pol?.toFixed?.(1), az: k.az?.toFixed?.(1), zoom: k.zoom?.toFixed?.(2), intro: k.intro, hopp: !!document.querySelector('#hopp.synlig') }; });
    await page.screenshot({ path: path.join(ut, `${navn}-${s}.jpg`), type: 'jpeg', quality: 70 });
    console.log(navn, s, JSON.stringify(k));
  }
  console.log(navn, 'feil:', feil.slice(0, 3).join(' | ') || 'ingen');
  await ctx.close();
}
await browser.close(); server.close();
