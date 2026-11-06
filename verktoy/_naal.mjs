import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, ut] = process.argv; const dir = path.dirname(file);
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r));
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await b.newContext({ viewport: { width: 1100, height: 750 }, deviceScaleFactor: 2 }); const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
const bilde = async f => { const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(f, Buffer.from(data, 'base64')); };
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/index.html?skip=1&vaer=sol`); await page.waitForTimeout(9000);
await page.click('#sok'); await page.waitForTimeout(500); await page.click('[data-k="spise"]'); await page.waitForTimeout(800);
await bilde(ut + '-panel.png');
await page.keyboard.press('Escape'); await page.waitForTimeout(6000);
await bilde(ut + '-naaler.png');
const n = await page.$$('.naal'); if (n.length) { await n[2].evaluate(e => e.click()); await page.waitForTimeout(6000); }
await bilde(ut + '-valgt.png');
console.log('naaler', n.length, 'feil', JSON.stringify(feil)); await b.close(); server.close();
