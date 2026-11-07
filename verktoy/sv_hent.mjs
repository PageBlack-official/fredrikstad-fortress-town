// Street View-bilder per gatefasade (07.11) fra kilder/gate/sv_skudd.json (verktoy/sv_velg.py har valgt panorama og retning).
//   node verktoy/sv_hent.mjs [skudd.json] [utmappe]  -> utmappe/<id>-<del>.jpg + utmappe/hent.json (pano, dato, posisjon, retning)
// Synlig Chromium (Google gir ikke Street View i hodeløs nettleser). Gjenopptar; stopper ved robotsjekk og skriver hvor.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const ROT = path.dirname(path.dirname(new URL(import.meta.url).pathname));
const skudd = JSON.parse(fs.readFileSync(process.argv[2] || path.join(ROT, 'kilder/gate/sv_skudd.json'), 'utf8'));
const ut = process.argv[3] || path.join(ROT, 'rapport/gate/sv');
const DEL = process.argv[4] ? process.argv[4].split('/').map(Number) : [0, 1];      // «0/2» og «1/2»: to nettlesere deler lista
fs.mkdirSync(ut, { recursive: true });
const loggF = path.join(ut, `hent-${DEL[0]}.json`);
const logg = fs.existsSync(loggF) ? JSON.parse(fs.readFileSync(loggF, 'utf8')) : {};
const lagre = () => fs.writeFileSync(loggF, JSON.stringify(logg, null, 0));
const retning = (la1, lo1, la2, lo2) => { const r = Math.PI / 180, y = Math.sin((lo2 - lo1) * r) * Math.cos(la2 * r), x = Math.cos(la1 * r) * Math.sin(la2 * r) - Math.sin(la1 * r) * Math.cos(la2 * r) * Math.cos((lo2 - lo1) * r); return (Math.atan2(y, x) / r + 360) % 360; };
const SV = /,\d+a,[\d.]+y,/;
const urlPano = (la, lo, fov, hd, pano) => `https://www.google.com/maps/@${la},${lo},3a,${fov}y,${hd.toFixed(1)}h,93t/data=!3m6!1e1!3m4!1s${pano}!2e0!7i16384!8i8192?hl=no`;
const urlPunkt = (la, lo, fov, hd) => `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${la},${lo}&heading=${hd.toFixed(1)}&pitch=3&fov=${fov}&hl=no`;
const b = await chromium.launch({ headless: false, channel: 'chromium', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const s = await b.newContext({ viewport: { width: 1280, height: 720 }, locale: 'nb-NO' });
const p = await s.newPage();
let samtykke = false, n = 0; const t0 = Date.now();
async function gaa(u) {
  await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (!samtykke) { for (const t of ['Avvis alle', 'Reject all']) { const k = p.getByRole('button', { name: t }); if (await k.count()) { await k.first().click(); break; } } samtykke = true; await p.waitForTimeout(1500); if (!SV.test(p.url())) await p.goto(u, { waitUntil: 'domcontentloaded' }); }
  for (let i = 0; i < 16 && !SV.test(p.url()); i++) await p.waitForTimeout(400);
}
for (let i = DEL[0]; i < skudd.length; i += DEL[1]) {
  const x = skudd[i], navn = `${x.id}-${x.del_}`, fil = path.join(ut, navn + '.jpg');
  if (logg[navn] && (logg[navn].mangler || fs.existsSync(fil))) continue;
  await gaa(x.pano ? urlPano(x.lat, x.lon, x.fov, x.heading, x.pano) : urlPunkt(x.lat, x.lon, x.fov, x.heading));
  if (p.url().includes('/sorry/')) { console.log('ROBOTSJEKK ved', navn, 'etter', n); logg._stopp = navn; lagre(); break; }
  if (!SV.test(p.url())) { logg[navn] = { mangler: true }; lagre(); n++; continue; }
  let la = +(p.url().match(/@(-?[\d.]+),/) || [])[1], lo = +(p.url().match(/@-?[\d.]+,(-?[\d.]+),/) || [])[1];
  const pano = (p.url().match(/!1s([\w-]{10,})!2e/) || [])[1];
  if (!x.pano && pano) { const hd = retning(la, lo, x.mlat, x.mlon); await gaa(urlPano(la, lo, x.fov, hd, pano)); x.heading = hd; }
  await p.waitForTimeout(2600);
  const tekst = await p.evaluate(() => (document.querySelector('#titlecard') || document.body).innerText);
  const dato = (tekst.match(/(jan|feb|mar|apr|mai|jun|jul|aug|sep|okt|nov|des)[a-z]*\.? \d{4}/i) || [])[0] || x.dato || null;
  await p.addStyleTag({ content: '#titlecard,#omnibox-container,#minimap,.scene-footer-container,.app-viewcard-strip,[jsaction*="minimap"],.widget-scene-imagery-render ~ div button{visibility:hidden!important}' }).catch(() => {});
  await p.waitForTimeout(250);
  await p.screenshot({ path: fil, type: 'jpeg', quality: 80 });
  logg[navn] = { pano: pano || x.pano, dato, lat: la, lon: lo, heading: +(+x.heading).toFixed(1), fov: x.fov };
  lagre(); n++;
  if (n % 25 === 0) console.log(n, 'bilder', Math.round((Date.now() - t0) / 1000), 's');
}
lagre(); console.log('ferdig', n, 'bilder', Math.round((Date.now() - t0) / 1000), 's');
await b.close();
