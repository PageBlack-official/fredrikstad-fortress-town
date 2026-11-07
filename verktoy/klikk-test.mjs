// Feilsøk 22_flyt (07.11): klikk på kirka som flyt-testen gjør, og se om kortet kommer. node klikk-test.mjs ut/enkel/index.html
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file] = process.argv; const dir = path.dirname(file);
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch(); const ctx = await browser.newContext({ viewport: { width: 900, height: 560 }, deviceScaleFactor: 1 }); const page = await ctx.newPage();
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?pix=0.2&skip=1${process.env.TEGN0 ? '&tegn=0' : ''}`, { waitUntil: 'load' });
await page.waitForFunction(() => typeof window.__klar === 'function' && window.__klar(), null, { timeout: 60000 }); await page.waitForTimeout(2000);
for (const h of [8, 6, 10]) {
  const kp = await page.evaluate(([x, h, y]) => window.__skjerm3(x, h, -y), [-14.8, h, -58.9]);
  console.log(JSON.stringify(await page.evaluate(([x, y]) => window.__treff ? window.__treff(x, y) : null, kp)));
  await page.mouse.click(kp[0], kp[1]); await page.waitForTimeout(2500);
  const vis = await page.evaluate(() => document.getElementById('kort').classList.contains('vis'));
  const tittel = await page.evaluate(() => (document.querySelector('#kort h2, #kort .navn') || {}).textContent || '');
  console.log('h', h, 'skjerm', kp.map(Math.round), 'kort', vis, tittel);
  await page.screenshot({ path: `/tmp/gate/klikk-${h}.jpg`, type: 'jpeg', quality: 70 });
  if (vis) await page.evaluate(() => document.querySelector('#kort .lukk').click()); await page.waitForTimeout(2500);
}
console.log('feil', feil.join(' | ') || 'ingen');
await browser.close(); server.close();
