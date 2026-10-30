// Kontrollbilder av huskortet: desktop (sidepanel) og mobil (bunnark), etter klikk på kirka. Bruk: node verktoy/kort-bilder.mjs <index.html> <utmappe>
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut, bare] = process.argv; const dir = path.dirname(file); fs.mkdirSync(ut, { recursive: true });   // bare: desktop, d1280, d1440 eller mobil
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const [navn, opt] of [['desktop', { viewport: { width: 1100, height: 700 } }], ['d1280', { viewport: { width: 1280, height: 800 } }], ['d1440', { viewport: { width: 1440, height: 900 } }], ['mobil', { viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 }]].filter(([n]) => !bare || n === bare)) {
  const ctx = await browser.newContext(opt); const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
  const bilde = async n => { const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(path.join(ut, n), Buffer.from(data, 'base64')); }; const feil = []; page.on('pageerror', e => feil.push(e.message));
  await page.clock.install(); await page.goto(`http://127.0.0.1:${port}/index.html?skip=1&pix=0.6`); await page.waitForFunction(() => window.__kam && window.__vaareBilder > 2, null, { timeout: 600000 });
  await page.clock.pauseAt(Date.now() + 1e7); for (let i = 0; i < 30; i++) await page.clock.runFor(16);   // falsk klokke: kamerabanen trinnes fram, uavhengig av hvor treg GPU-en er await bilde(`${navn}-0-for.png`);
  const kp = await page.evaluate(() => window.__skjerm3(-14.8, 8, 58.9));
  if (navn === 'mobil') await page.touchscreen.tap(kp[0], kp[1]); else await page.mouse.click(kp[0], kp[1]);
  for (let i = 0; i < 75; i++) await page.clock.runFor(16); await page.waitForTimeout(1500); await page.clock.runFor(16);
  await bilde(`${navn}-1-kort.png`);
  console.log(navn, 'kort', await page.evaluate(() => JSON.stringify(document.getElementById('kort').getBoundingClientRect())), 'feil', JSON.stringify(feil));
  await ctx.close();
}
await browser.close(); server.close();
