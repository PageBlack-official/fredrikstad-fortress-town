// Hus under bakken mot gata (07.11, regel 48): node verktoy/fot-test.mjs ut/enkel/index.html [grense] → JSON-liste på stdout
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, grense = '0.3'] = process.argv; const dir = path.dirname(file);
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch(); const page = await (await browser.newContext({ viewport: { width: 600, height: 400 } })).newPage();
const feil = []; page.on('pageerror', e => feil.push(e.message));
await page.goto(`http://127.0.0.1:${port}/${path.basename(file)}?skip=1&tegn=0`, { waitUntil: 'load' });
await page.waitForFunction(() => typeof window.__fotSjekk === 'function', null, { timeout: 60000 });
const ut = await page.evaluate(g => window.__fotSjekk(g), +grense);
console.log(JSON.stringify({ under: ut, feil }));
await browser.close(); server.close();
