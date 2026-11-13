// Bilde A/B (13.11): samme kamera, flere varianter (spørrestreng), skjermbilde av hjemmevisningen og et nærbilde inne i byen.
// Bruk: PW_GPU=1 node verktoy/bilde_ab.mjs <ut-mappe> <index.html>   (miljø: VAR=json [{navn,q}], BREDDE, HOYDE, DPR)
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, ut, fil] = process.argv; const W = +(process.env.BREDDE || 1280), H = +(process.env.HOYDE || 720), DPR = +(process.env.DPR || 2);
const VAR = JSON.parse(process.env.VAR || '[{"navn":"grunn","q":""}]');
const server = http.createServer((q, r) => { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(path.resolve(fil))); });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
fs.mkdirSync(ut, { recursive: true });
const still = async p => { for (let i = 0; i < 60; i++) { await p.waitForTimeout(250); if (!(await p.evaluate(() => map.isMoving()))) break; } await p.waitForTimeout(2500); };
for (const v of VAR) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR }); const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${v.q}`);
  await page.waitForFunction(() => window.__klar && window.__klar() && window.__vaareBilder > 5, null, { timeout: 120000, polling: 200 });
  await page.evaluate(() => window.__vis(200, 1.3, 25, 25)); await still(page);
  await page.screenshot({ path: path.join(ut, `${v.navn}-hjem.png`) });
  await page.evaluate(() => window.__vis(200, 4, 40, 40)); await still(page);
  await page.screenshot({ path: path.join(ut, `${v.navn}-naer.png`) });
  await ctx.close(); console.log('bilde', v.navn);
}
await browser.close(); server.close();
