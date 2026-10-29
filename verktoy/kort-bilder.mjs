// Kontrollbilder av huskortet: desktop (sidepanel) og mobil (bunnark), etter klikk på kirka. Bruk: node verktoy/kort-bilder.mjs <index.html> <utmappe>
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir = path.dirname(file); fs.mkdirSync(ut, { recursive: true });
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const [navn, opt] of [['desktop', { viewport: { width: 1100, height: 700 } }], ['mobil', { viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 }]]) {
  const ctx = await browser.newContext(opt); const page = await ctx.newPage(); const feil = []; page.on('pageerror', e => feil.push(e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&pix=0.6`); await page.waitForFunction(() => window.__kam && window.__vaareBilder > 2, null, { timeout: 600000 });
  await page.waitForTimeout(3000); await page.screenshot({ path: path.join(ut, `${navn}-0-for.png`) });
  const kp = await page.evaluate(() => window.__skjerm3(-14.8, 8, 58.9));
  if (navn === 'mobil') await page.touchscreen.tap(kp[0], kp[1]); else await page.mouse.click(kp[0], kp[1]);
  await page.waitForFunction(() => !map.isMoving(), null, { timeout: 120000 }).catch(() => {}); await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(ut, `${navn}-1-kort.png`) });
  console.log(navn, 'kort', await page.evaluate(() => JSON.stringify(document.getElementById('kort').getBoundingClientRect())), 'feil', JSON.stringify(feil));
  await ctx.close();
}
await browser.close(); server.close();
