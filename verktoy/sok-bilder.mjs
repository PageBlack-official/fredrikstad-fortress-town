// Skjermbilder av Finn-panelet (24_sok) for hver kategori, nålene i kartet og kortet for et sted med flere plasser.
// Bruk: node verktoy/sok-bilder.mjs <index.html> <ut-prefiks> [bredde høyde]   (på Mac minien med PW_GPU=1)
// Skriver også en kort sjekk per kategori: like linjer i lista, høyden på turkortene, om noe tekst er kuttet.
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut, W = '451', H = '840'] = process.argv; const dir = path.dirname(file);
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await b.newContext({ viewport: { width: +W, height: +H }, deviceScaleFactor: 2 }); const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
const bilde = async f => { const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(f, Buffer.from(data, 'base64')); };
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/index.html?skip=1&vaer=sol`); await page.waitForTimeout(8000);
await page.click('#sok'); await page.waitForTimeout(500);
const sjekk = {};
for (const k of await page.$$eval('#sokpanel [data-k]', x => x.map(e => e.dataset.k))) {
  await page.$eval(`#sokpanel [data-k="${k}"]`, e => e.click()); await page.waitForTimeout(500);
  sjekk[k] = await page.evaluate(() => {
    const li = [...document.querySelectorAll('#sokpanel .treff li[data-i]')].map(l => l.querySelector('b').textContent + ' | ' + l.querySelector('small').textContent);
    const tur = [...document.querySelectorAll('#sokpanel .turer button')].map(t => Math.round(t.getBoundingClientRect().height));
    return { linjer: li.length, like: li.length - new Set(li).size, turhoyde: tur, naaler: document.querySelectorAll('.naal').length };
  });
  await bilde(`${ut}-${k}.png`);
  await page.$eval(`#sokpanel [data-k="${k}"]`, e => e.click()); await page.waitForTimeout(200);
}
await page.$eval('#sokpanel [data-k="parkering"]', e => e.click()); await page.waitForTimeout(300);
await page.click('#sokpanel .lukk'); await page.waitForTimeout(5000); await bilde(`${ut}-naaler.png`);
await page.evaluate(() => window.__sok.velgSted('Færgeportgaten')); await page.waitForTimeout(5000); await bilde(`${ut}-kort.png`);
const kort = await page.evaluate(() => document.querySelector('#kort').innerText.slice(0, 300));
console.log(JSON.stringify({ sjekk, kort, feil })); await b.close(); server.close();
