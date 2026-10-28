// Kvartal-QA (28.10): modellbilder per kvartaltegning fra flere vinkler i én nettleserøkt, og skjermposisjonen til hvert koblet bygg.
// Bruk: node verktoy/kvartal_bilder.mjs ut/enkel/index.html rapport/kvartal-qa/_arbeid/visninger.json rapport/kvartal-qa/_arbeid [navn ...]
// visninger.json lages av `python3 -I verktoy/kvartal_qa.py kobling`: [{n, cx, cy, zoom, vinkler:[az...], bygg:[{id,x,y,h}]}]
// cx, cy er modellmeter (x øst, y nord) og går rett inn i window.__vis(az, zoom, x, y) (src/15_loop.js -> tilLngLat(x, y), y nord).
// Skriver <utmappe>/<n>-az<az>.png og <n>-az<az>.json ({kam, bygg:[{id, tak:[sx,sy], bakke:[sx,sy]}]}); hopper over det som finnes.
// Mal: rapport/bevisark/lag-bilder.mjs og verktoy/bilde.mjs (venter til kameraet står, UI skjult som UI=0).
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, viewsFile, utdir, ...bare] = process.argv; const dir = path.dirname(file);
const W = 1100, H = 760;
let views = JSON.parse(fs.readFileSync(viewsFile, 'utf8')); if (bare.length) views = views.filter(v => bare.includes(v.n));
const server = http.createServer((q, r) => { const u = q.url.split('?')[0]; const p = path.join(dir, u === '/' ? 'index.html' : u); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', p.endsWith('.json') ? 'application/json' : p.endsWith('.js') ? 'text/javascript' : p.endsWith('.png') ? 'image/png' : 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: W, height: H } }); const page = await ctx.newPage();
const errs = []; page.on('pageerror', e => errs.push(e.message));
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`, { waitUntil: 'load' }); await page.waitForTimeout(6000);
await page.addStyleTag({ content: '#hjem,#hint,#kort,#lekkasje,.maplibregl-ctrl{display:none!important}' });
const cdp = await ctx.newCDPSession(page);
fs.mkdirSync(utdir, { recursive: true });
for (const v of views) {
  for (const az of v.vinkler) {
    const ut = path.join(utdir, `${v.n}-az${az}.png`);
    if (fs.existsSync(ut) && fs.existsSync(ut.replace(/\.png$/, '.json'))) { console.log('finnes', ut); continue; }
    const t0 = Date.now();
    await page.evaluate(a => window.__vis(...a), [az, v.zoom, v.cx, v.cy]);
    // venter til kameraet faktisk står på målet (jumpTo slår først inn ved neste bilde, så __kam() viser forrige visning en stund):
    // senter = (cx, -cy) i verden, asimut = az, og deretter to like avlesninger på rad
    let forrige = null, fremme = false;
    while (Date.now() - t0 < 180000) {
      await page.waitForTimeout(500);
      const k = await page.evaluate(() => window.__kam());
      const daz = Math.abs(((k.az * 180 / Math.PI - az) % 360 + 540) % 360 - 180);
      fremme = Math.hypot(k.x - v.cx, k.z + v.cy) < 0.5 && daz < 0.5 && !k.anim;
      const naa = [k.zoom, k.x, k.z, k.az].map(q => q.toFixed(4)).join();
      if (fremme && naa === forrige) break; forrige = naa;
    }
    if (!fremme) { console.log('FEIL kamera kom ikke fram', v.n, az); continue; }
    await page.waitForTimeout(3000);
    const kam = await page.evaluate(() => window.__kam());
    // verden = (x, høyde, -y) (src/05_bygg.js: «modellkoordinater x,y → verden x,-y»)
    const bygg = await page.evaluate(B => B.map(b => ({ id: b.id, tak: window.__skjerm3(b.x, b.h, -b.y), midt: window.__skjerm3(b.x, b.h * 0.5, -b.y), bakke: window.__skjerm3(b.x, 0, -b.y) })), v.bygg);
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(ut, Buffer.from(data, 'base64'));
    fs.writeFileSync(ut.replace(/\.png$/, '.json'), JSON.stringify({ kam, az, zoom: v.zoom, cx: v.cx, cy: v.cy, W, H, bygg }, null, 1));
    console.log('ok', ut, ((Date.now() - t0) / 1000).toFixed(0) + 's', 'feil', errs.length);
  }
}
if (errs.length) console.log('sidefeil:', errs.slice(0, 5));
await browser.close(); server.close();
