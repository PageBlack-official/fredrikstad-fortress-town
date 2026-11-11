// Mobilmåler (10.11, PAG-1503): måler kartet slik Vegar møter det på telefonen — iPhone-profil (390×844, DPR 3, berøring),
// CPU-struping 4× (CDP Emulation.setCPUThrottlingRate) og EKTE fingergester (CDP Input.dispatchTouchEvent): klyp-zoom med to
// fingre og panorering med én. Per bilde leser vi window.__logg (15_loop): r = hele render() i laget, o = oppdater(), sp = speil,
// sk = skyggekart, s/b/f = 3D/blekk/fxaa (01), kall = draw calls (renderer.info.render.calls). I tillegg: tid til første egne bilde
// på en 4G-profil (CDP Network.emulateNetworkConditions), servert som server-bygget (index.html + data/by.json + assets).
//
// Bruk:  PW_MODUL=.../playwright/index.js node verktoy/mobil_maal.mjs <ut.json> <navn>=<dir> [<navn>=<dir> ...]
//   <dir> er en bygget mappe. Har den data/by.json brukes den som server-bygg (4G-last måles). Ellers ventes index.html (gest).
//   Miljø: CPU=4 (strupefaktor), RUNDER=3, SCEN=pan,pinch,ro (gestene), GPU=swiftshader (standard; PW_GPU=1 for maskinens kort).
// SwiftShader gir ikke en telefons ekte bildefrekvens, men forholdet før/etter og fordelingen på delene (oppdater/3D/speil/skygge/
// draw calls) er det som styrer om fingeren henger. Ekte bilder/s leser Vegar på telefonen med ?maal=1.
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';

const [,, utfil, ...varianter] = process.argv;
if (!utfil || !varianter.length) { console.error('bruk: node verktoy/mobil_maal.mjs <ut.json> <navn>=<dir> ...'); process.exit(1); }
const V = varianter.map(a => { const [navn, dir] = a.split('='); const d = path.resolve(dir);
  return { navn, dir: d, server: fs.existsSync(path.join(d, 'data', 'by.json')) }; });
const CPU = +(process.env.CPU || 4), RUNDER = +(process.env.RUNDER || 3), EKSTRA = process.env.EKSTRA || '';
const SCEN = (process.env.SCEN || 'pan,pinch,ro').split(',').filter(Boolean);
// iPhone-profil (iPhone 12/13/14-klasse): CSS 390×844, fysisk DPR 3, berøring
const W = 390, H = 844, DPR = 3;

// én statisk filserver per variant-mappe (fanger /index.html, /data/by.json, /assets/*)
function server(dir) { return http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0]); const p = path.join(dir, rel === '/' ? 'index.html' : rel);
  if (!p.startsWith(dir) || !fs.existsSync(p) || !fs.statSync(p).isFile()) { r.statusCode = 404; r.end(); return; }
  const t = { '.html':'text/html; charset=utf-8', '.json':'application/json', '.js':'text/javascript', '.png':'image/png', '.webmanifest':'application/manifest+json' }[path.extname(p)] || 'application/octet-stream';
  r.setHeader('content-type', t); r.end(fs.readFileSync(p)); }); }

const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const res = { profil: { W, H, DPR, cpu: CPU }, runder: RUNDER, scen: SCEN, varianter: V.map(v => v.navn), maal: {}, last: {}, feil: [] };

const med = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const p95 = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]; };
const snitt = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const maxv = a => a.length ? Math.max(...a) : null;
function oppsummer(d) {
  const L = d.logg || []; const f = k => +((snitt(L.map(x => x[k] || 0)) || 0).toFixed(2));
  return { ms: Math.round(d.ms), bilder: L.length, perSek: +(L.length * 1000 / d.ms).toFixed(1),
    ramme_snitt: +(snitt(L.map(x => x.r)) || 0).toFixed(1), ramme_verst: +(p95(L.map(x => x.r)) || 0).toFixed(1), ramme_maks: +(maxv(L.map(x => x.r)) || 0).toFixed(1),
    oppdater: f('o'), speil: f('sp'), skygge: f('sk'), scene: f('s'), blekk: f('b'), fxaa: f('f'),
    kall_snitt: Math.round(snitt(L.map(x => x.kall || 0)) || 0), kall_maks: maxv(L.map(x => x.kall || 0)) || 0,
    speilBilder: L.filter(x => x.sp > 0).length, skyggeBilder: L.filter(x => x.sk > 0).length };
}

async function ctxSide(s) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR, isMobile: true, hasTouch: true });
  const page = await ctx.newPage(); page.on('pageerror', e => res.feil.push(e.message));
  const client = await ctx.newCDPSession(page);
  if (CPU > 1) await client.send('Emulation.setCPUThrottlingRate', { rate: CPU });
  return { ctx, page, client };
}
// CDP-fingre: punkter i CSS-piksler
async function fingre(client, type, pts) { await client.send('Input.dispatchTouchEvent', { type, touchPoints: pts.map(p => ({ x: p.x, y: p.y })) }); }
async function sov(ms) { await new Promise(r => setTimeout(r, ms)); }
async function still(page, ms = 1200) { const t0 = Date.now(); while (Date.now() - t0 < 60000) { await sov(200); if (!(await page.evaluate(() => map.isMoving()).catch(() => false))) break; } await sov(ms); }
async function start(page) { await page.evaluate(() => { window.__logg = []; window.__t0 = performance.now(); }); }
async function slutt(page) { return page.evaluate(() => { const d = { logg: window.__logg, ms: performance.now() - window.__t0 }; window.__logg = null; return d; }); }

// panorering: én finger drar 420 px opp-venstre over ~1,3 s, med jevne touchMove (slik en tommel drar)
async function panorer(page, client) { const cx = W / 2, cy = H / 2; await fingre(client, 'touchStart', [{ x: cx, y: cy }]);
  for (let i = 1; i <= 26; i++) { await fingre(client, 'touchMove', [{ x: cx - i * 9, y: cy - i * 6 }]); await sov(40); }
  await fingre(client, 'touchEnd', []); }
// klyp-zoom: to fingre fra 120 px fra hverandre ut til 520 px (zoom inn), rundt sentrum
async function klyp(page, client) { const cx = W / 2, cy = H / 2;
  await fingre(client, 'touchStart', [{ x: cx - 60, y: cy }, { x: cx + 60, y: cy }]);
  for (let i = 1; i <= 26; i++) { const d = 60 + i * 9; await fingre(client, 'touchMove', [{ x: cx - d, y: cy }, { x: cx + d, y: cy }]); await sov(40); }
  await fingre(client, 'touchEnd', [{ x: cx + (60 + 26 * 9), y: cy }]); await fingre(client, 'touchEnd', []); }

async function gester(v) {
  const { ctx, page, client } = await ctxSide();
  await page.goto(`http://127.0.0.1:${v.port}/index.html?skip=1${EKSTRA}`);
  await page.waitForFunction(() => window.__kam && window.__vaareBilder > 2, null, { timeout: 600000 });
  const bering = await page.evaluate(() => ({ coarse: matchMedia('(pointer: coarse)').matches, dpr: devicePixelRatio, nivaa: (window.__kval ? window.__kval().perfNivaa : null), kall: (window.__pt || {}).kall }));
  const ut = { _berøring: bering };
  await still(page, 1500);
  // oppvarming (VARM=n): n runder pan+klyp før målingen, så ytelsesmåleren rekker å telle nok bevegelsesbilder til å be om et trinn ned
  // (representerer en telefon som har dratt rundt noen sekunder). Uten adapt (foer) endrer dette ingenting; med adapt (etter) trapper det ned.
  for (let i = 0; i < +(process.env.VARM || 0); i++) { await panorer(page, client); await still(page, 700); await klyp(page, client); await still(page, 700); }
  ut._nivaaEtterVarm = await page.evaluate(() => (window.__kval ? window.__kval().perfNivaa : null));
  if (SCEN.includes('ro'))   { await start(page); await sov(3000); ut.ro = oppsummer(await slutt(page)); }
  if (SCEN.includes('pan'))  { await start(page); await panorer(page, client); await still(page, 300); ut.pan = oppsummer(await slutt(page)); await still(page, 800); }
  if (SCEN.includes('pinch')){ await start(page); await klyp(page, client);  await still(page, 300); ut.pinch = oppsummer(await slutt(page)); await still(page, 800); }
  await ctx.close(); return ut;
}

// 4G: tid fra navigasjon til første egne bilde. Fast 4G (Chrome DevTools-profil): 9 Mbit ned, 1,5 opp, 170 ms rtt.
async function last4g(v) {
  const { ctx, page, client } = await ctxSide();
  await client.send('Network.enable');
  await client.send('Network.emulateNetworkConditions', { offline: false, latency: 170, downloadThroughput: 9 * 1024 * 1024 / 8, uploadThroughput: 1.5 * 1024 * 1024 / 8 });
  const t0 = Date.now();
  await page.goto(`http://127.0.0.1:${v.port}/index.html?skip=1${EKSTRA}`, { waitUntil: 'commit' });
  await page.waitForFunction(() => window.__vaareBilder > 0, null, { timeout: 600000 });
  const ttf = Date.now() - t0;
  const dom = await page.evaluate(() => Math.round(performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart)).catch(() => null);
  await ctx.close(); return { tidForsteBilde: ttf, domKlar: dom };
}

for (const v of V) { const s = server(v.dir); await new Promise(r => s.listen(0, '127.0.0.1', r)); v.port = s.address().port; v._srv = s; }
for (let r = 0; r < RUNDER; r++) for (const v of (r % 2 ? [...V].reverse() : V)) {
  const ut = await gester(v); (res.maal[v.navn] ||= []).push(ut);
  console.log(`runde ${r + 1} ${v.navn} (coarse=${ut._berøring.coarse} nivaa=${ut._berøring.nivaa}): ` + SCEN.map(k => ut[k] ? `${k} ${ut[k].perSek}/s ${ut[k].ramme_snitt}ms kall ${ut[k].kall_snitt}` : '').filter(Boolean).join(' | '));
}
// 4G-last én gang per server-bygg
for (const v of V) if (v.server) { try { res.last[v.navn] = await last4g(v); console.log(`4G ${v.navn}: første bilde ${res.last[v.navn].tidForsteBilde} ms`); } catch (e) { res.feil.push(`4G ${v.navn}: ${e.message}`); } }

// median over rundene
res.median = {};
for (const v of V) { const rs = res.maal[v.navn]; const o = {}; for (const sc of SCEN) { if (!rs[0][sc]) continue; o[sc] = {}; for (const k of Object.keys(rs[0][sc])) { const xs = rs.map(x => x[sc] && x[sc][k]).filter(x => typeof x === 'number'); o[sc][k] = xs.length ? med(xs) : rs[0][sc][k]; } } res.median[v.navn] = o; }
fs.mkdirSync(path.dirname(utfil), { recursive: true }); fs.writeFileSync(utfil, JSON.stringify(res, null, 1));
console.log('\n=== median (CPU ' + CPU + '×, iPhone ' + W + '×' + H + ' DPR ' + DPR + ') ===');
for (const sc of SCEN) for (const v of V) { const m = res.median[v.navn] && res.median[v.navn][sc]; if (m) console.log(`${sc.padEnd(6)} ${v.navn.padEnd(8)} ${String(m.perSek).padStart(5)}/s  bilde ${String(m.ramme_snitt).padStart(5)} ms (verst ${m.ramme_verst})  oppd ${m.oppdater} 3D ${m.scene} blekk ${m.blekk} fxaa ${m.fxaa} speil ${m.speil} skygge ${m.skygge}  draw ${m.kall_snitt} (maks ${m.kall_maks})`); }
for (const v of V) if (res.last[v.navn]) console.log(`4G     ${v.navn.padEnd(8)} første bilde ${res.last[v.navn].tidForsteBilde} ms (DOM ${res.last[v.navn].domKlar} ms)`);
if (res.feil.length) console.log('FEIL:', [...new Set(res.feil)].slice(0, 8));
await browser.close(); for (const v of V) v._srv.close();
