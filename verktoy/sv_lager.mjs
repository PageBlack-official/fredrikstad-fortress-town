// Panoramalager (07.11): hvilke Street View-panoramaer finnes langs gatene, med dato og posisjon. Ingen bilder.
//   node verktoy/sv_lager.mjs  -> kilder/gate/sv_lager.json  {pano: {lat, lon, dato, aar, mnd}}, gjenopptar
// Synlig Chromium (Google gir ikke Street View hodeløst). Stopper ved robotsjekk.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const ROT = path.dirname(path.dirname(new URL(import.meta.url).pathname));
const pkt = JSON.parse(fs.readFileSync(path.join(ROT, 'kilder/gate/sv_punkter.json'), 'utf8'));
const BAK = process.argv[2] === 'bak';   // nr. 2 går baklengs fra slutten og stopper der nr. 1 har vært
const F = path.join(ROT, BAK ? 'kilder/gate/sv_lager-b.json' : 'kilder/gate/sv_lager.json');
const F1 = path.join(ROT, 'kilder/gate/sv_lager.json');
let andre = {}; const lesAndre = () => { if (BAK && fs.existsSync(F1)) try { andre = JSON.parse(fs.readFileSync(F1, 'utf8')).gjort || {}; } catch (e) {} };
const L = fs.existsSync(F) ? JSON.parse(fs.readFileSync(F, 'utf8')) : { panoramaer: {}, gjort: {} };
const lagre = () => fs.writeFileSync(F, JSON.stringify(L));
const MND = { jan: 1, feb: 2, mar: 3, apr: 4, mai: 5, jun: 6, jul: 7, aug: 8, sep: 9, okt: 10, nov: 11, des: 12 };
const b = await chromium.launch({ headless: false, channel: 'chromium', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const s = await b.newContext({ viewport: { width: 1000, height: 640 }, locale: 'nb-NO' });
const p = await s.newPage();
let samtykke = false, n = 0; const t0 = Date.now();
lesAndre();
for (const q of (BAK ? [...pkt].reverse() : pkt)) {
  const k = `${q.x},${q.y}`; if (L.gjort[k]) continue;
  if (BAK && andre[k]) { console.log('møtt nr. 1'); break; }
  await p.goto(`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${q.lat},${q.lon}&heading=0&pitch=0&fov=90&hl=no`, { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (p.url().includes('/sorry/')) { console.log('ROBOTSJEKK etter', n); L._stopp = k; lagre(); break; }
  if (!samtykke) { for (const t of ['Avvis alle', 'Reject all']) { const kn = p.getByRole('button', { name: t }); if (await kn.count()) { await kn.first().click(); break; } } samtykke = true; await p.waitForTimeout(1500);
    if (!/,\d+a,[\d.]+y,/.test(p.url())) await p.goto(`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${q.lat},${q.lon}&heading=0&pitch=0&fov=90&hl=no`, { waitUntil: 'domcontentloaded' }); }
  for (let i = 0; i < 14 && !/,\d+a,[\d.]+y,/.test(p.url()); i++) await p.waitForTimeout(400);
  await p.waitForTimeout(900);
  const u = p.url(), m = u.match(/@(-?[\d.]+),(-?[\d.]+),\d+a/), pano = (u.match(/!1s([\w-]{10,})!2e/) || [])[1];
  if (m && pano) {
    const tekst = await p.evaluate(() => (document.querySelector('#titlecard') || document.body).innerText);
    const d = tekst.match(/(jan|feb|mar|apr|mai|jun|jul|aug|sep|okt|nov|des)[a-z]*\.? (\d{4})/i);
    L.panoramaer[pano] = { lat: +m[1], lon: +m[2], dato: d ? d[0] : null, aar: d ? +d[2] : 0, mnd: d ? MND[d[1].toLowerCase().slice(0, 3)] : 0 };
    L.gjort[k] = pano;
  } else L.gjort[k] = '-';
  n++; if (n % 20 === 0) { lagre(); lesAndre(); console.log(n, Object.keys(L.panoramaer).length, 'pano', Math.round((Date.now() - t0) / 1000), 's'); }
}
lagre(); console.log('ferdig', n, 'punkter,', Object.keys(L.panoramaer).length, 'panoramaer', Math.round((Date.now() - t0) / 1000), 's');
await b.close();
