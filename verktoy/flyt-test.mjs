// Flyt-test (29.10, oppdrag 13/15): måler kameraets bane bilde for bilde under typiske gester og overganger, på desktop og mobil.
// Klokka i siden er Playwrights falske klokke: hvert bilde er nøyaktig 16 ms virtuell tid uansett hvor treg programvare-GPU-en er,
// så målingene er kontinuitet (hopp, rykk, bråstopp, ankerpunkt som glipper), ikke bildefrekvens. Bildefrekvens må måles i ekte Chrome
// (tast d i kartet, «siste bevegelse … bilder/s»).
// Bruk: node verktoy/flyt-test.mjs <index.html> <ut.json> [scenario ...]   (FLYT_TEGN=1: tegn byen også; standard er ?tegn=0, bare kameraet)
// Måles på skjermen: fem faste bakkepunkter i byen projiseres med kartets egen projeksjon (map.project) hvert bilde;
// forflytningen per bilde er den største av dem (dekker flytt, zoom og rotasjon).
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, utfil, ...valgte] = process.argv; const dir = path.dirname(file);
const server = http.createServer((q, r) => { const p = path.join(dir, q.url.split('?')[0] === '/' ? 'index.html' : q.url.split('?')[0]); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const BILDE = 16;   // ms virtuell tid per bilde (60/s)
const res = { scenarier: {}, feil: [] };

async function aapne({ mobil = false, skip = true, ekstra = '', redusert = false } = {}) {
  const vp = mobil ? { width: 390, height: 700 } : { width: 900, height: 560 };
  const ctx = await browser.newContext({ viewport: vp, ...(mobil ? { isMobile: true, hasTouch: true, deviceScaleFactor: 1 } : {}), reducedMotion: redusert ? 'reduce' : 'no-preference' });
  const page = await ctx.newPage(); page.on('pageerror', e => res.feil.push(e.message));
  await page.clock.install();
  await page.goto(`http://127.0.0.1:${port}/index.html?pix=0.2${process.env.FLYT_TEGN ? '' : '&tegn=0'}${skip ? '&skip=1' : ''}${ekstra}`);
  await page.waitForFunction(() => window.__kam && window.__vaareBilder > 2, null, { timeout: 600000 });
  await page.clock.pauseAt(Date.now() + 1e7);
  await page.evaluate(() => {
    // fem bakkepunkter i modellmeter (x øst, y nord): midt i byen og fire hjørner ±120 m
    const MP = [[25, 25], [-95, -95], [145, -95], [-95, 145], [145, 145]];
    const o = maplibregl0(); window.__ref = MP.map(([x, y]) => o.ll(x, y));
    function maplibregl0() { const c = map.getCenter(); const m = window.__kam(); return { ll: (x, y) => { // lengde/bredde fra modellmeter via skjermen: bruk tilLngLat om den finnes
      if (window.__tilLngLat) return window.__tilLngLat(x, y);
      const R = 6378137, lat0 = 59.202835 * Math.PI / 180; return { lng: 10.952745 + x / (R * Math.cos(lat0)) * 180 / Math.PI, lat: 59.202835 + y / R * 180 / Math.PI }; } }; }
    window.__prove = () => { const k = document.getElementById('kort'); const r = k.getBoundingClientRect(); const cs = getComputedStyle(k);
      return { t: performance.now(), p: window.__ref.map(ll => { const s = map.project(ll); return [s.x, s.y]; }), z: map.getZoom(), b: map.getBearing(), pi: map.getPitch(),
        mv: map.isMoving(), kort: { vis: k.classList.contains('vis'), top: r.top, left: r.left, bunn: r.bottom, h: r.height, w: r.width, op: +cs.opacity },
        sol: window.__solvei ? window.__solvei() : null, intro: window.__kam().intro }; };
    // kortets overganger: hver gang klassen endres, leses animasjonene (getAnimations tvinger stilen, så overgangen finnes alt)
    window.__kortLogg = []; new MutationObserver(() => { const k = document.getElementById('kort');
      window.__kortLogg.push({ t: performance.now(), vis: k.classList.contains('vis'), anim: k.getAnimations({ subtree: false }).map(a => ({ navn: a.transitionProperty || a.animationName || 'waapi', ms: a.effect.getComputedTiming().duration, easing: a.effect.getComputedTiming().easing || '' })) }); })
      .observe(document.getElementById('kort'), { attributes: true, attributeFilter: ['class'] });
  });
  return { ctx, page, vp };
}
async function kjor(page, ms, logg) { const n = Math.round(ms / BILDE); for (let i = 0; i < n; i++) { await page.clock.runFor(BILDE); if (logg) logg.push(await page.evaluate(() => window.__prove())); } }
const flytt = (a, b) => Math.max(...a.p.map((p, i) => Math.hypot(p[0] - b.p[i][0], p[1] - b.p[i][1])));
// én bevegelse: forflytning per bilde, topp, hopp (enkeltbilde langt over naboene), rykk (endring i fart mellom bilder / topp), bråstopp (siste fart / topp)
function maal(logg, fra = 0, til = logg.length) {
  const d = []; for (let i = fra + 1; i < til; i++) d.push(flytt(logg[i], logg[i - 1]));
  const topp = Math.max(0, ...d); let hopp = 0, rykk = 0; const hoppAt = [];
  for (let i = 0; i < d.length; i++) { const nb = Math.max(d[i - 1] ?? 0, d[i + 1] ?? 0); if (d[i] > 3 && d[i] > 2.5 * nb) { hopp++; hoppAt.push(i); } if (i) rykk = Math.max(rykk, Math.abs(d[i] - d[i - 1])); }
  const sisteI = d.reduce((s, v, i) => v > 0.05 ? i : s, -1); const forsteI = d.findIndex(v => v > 0.05);
  return { bilder: d.length, topp: +topp.toFixed(1), hopp, hoppAt, rykk: topp > 2 ? +(rykk / topp).toFixed(2) : 0, braastopp: topp > 2 && sisteI >= 0 ? +(d[sisteI] / topp).toFixed(2) : 0,
    ms: sisteI >= 0 ? (sisteI - Math.max(0, forsteI) + 1) * BILDE : 0, start_ms: forsteI >= 0 ? forsteI * BILDE : null, d: d.map(v => +v.toFixed(1)) };
}
const ankerFeil = async (page, ll, px) => page.evaluate(([ll, px]) => { const s = map.project(ll); return +Math.hypot(s.x - px[0], s.y - px[1]).toFixed(1); }, [ll, px]);
const kortLogg = page => page.evaluate(() => window.__kortLogg.splice(0));
const skjerm = (page, x, h, y) => page.evaluate(([x, h, y]) => window.__skjerm3(x, h, -y), [x, h, y]);
const KIRKE = [-14.8, 8, -58.9];
const ok = n => !valgte.length || valgte.includes(n);

// ---------------- desktop ----------------
if (['klikk', 'dobbel', 'hjul', 'dra', 'avbryt', 'hjem'].some(ok)) {
  const { ctx, page, vp } = await aapne();
  await kjor(page, 400);
  if (ok('klikk')) {   // klikk på kirka: kamera + kort inn; så lukk (×): speiler kameraet inngangen?
    const k0 = await page.evaluate(() => window.__prove()); const kp = await skjerm(page, ...KIRKE);
    const logg = [k0]; await page.mouse.click(kp[0], kp[1]); await kjor(page, 2400, logg);
    const inn = maal(logg); const kl1 = await kortLogg(page); const k1 = logg.at(-1);
    const husEtter = await skjerm(page, ...KIRKE);
    const fri = k1.kort.vis ? (k1.kort.left > vp.width * 0.5 || k1.kort.w > vp.width * 0.6 ? { x0: 0, x1: vp.width, y0: 0, y1: k1.kort.top } : { x0: k1.kort.left + k1.kort.w, x1: vp.width, y0: 0, y1: vp.height }) : null;
    const husSynlig = fri ? husEtter[0] > fri.x0 && husEtter[0] < fri.x1 && husEtter[1] > fri.y0 && husEtter[1] < fri.y1 : false;
    const logg2 = [k1]; const lukk = await page.$('#kort .lukk'); await lukk.click(); await kjor(page, 2400, logg2);
    const ut = maal(logg2); const kl2 = await kortLogg(page); const k2 = logg2.at(-1);
    res.scenarier.klikk = { inn, ut, kortInn: kl1, kortUt: kl2, kortSynlig: k1.kort.vis, kortRamme: k1.kort, husSynligVedSidenAvKortet: husSynlig, husPx: husEtter,
      tilbakeAvvikPx: +flytt(k2, k0).toFixed(1), zoomInn: +(k1.z - k0.z).toFixed(2) };
  }
  if (ok('klikk')) {   // Esc med kortet åpent: lukker kortet først (og speiler), ikke rett hjem
    const k0 = await page.evaluate(() => window.__prove()); const kp = await skjerm(page, ...KIRKE);
    await page.mouse.click(kp[0], kp[1]); await kjor(page, 2400); await kortLogg(page);
    const logg = [await page.evaluate(() => window.__prove())]; await page.keyboard.press('Escape'); await kjor(page, 2400, logg);
    const k2 = logg.at(-1); res.scenarier.esc = { kortLukket: !k2.kort.vis, tilbakeAvvikPx: +flytt(k2, k0).toFixed(1), bevegelse: maal(logg) };
  }
  if (ok('dobbel')) {   // dobbeltklikk: zoomer inn mot punktet; bakkepunktet under pekeren skal bli under pekeren
    const P = [vp.width * 0.68, vp.height * 0.62]; const ll = await page.evaluate(P => map.unproject(P), P);
    const logg = [await page.evaluate(() => window.__prove())]; await page.mouse.dblclick(P[0], P[1]); await kjor(page, 1600, logg);
    const z = logg.at(-1).z - logg[0].z; res.scenarier.dobbel = { bevegelse: maal(logg), zoom: +z.toFixed(2), ankerPx: await ankerFeil(page, ll, P), kortVis: logg.at(-1).kort.vis };
    await page.keyboard.press('Escape'); await kjor(page, 1600);
  }
  if (ok('hjul')) {   // musehjul tre hakk: punktet under pekeren står
    const P = [vp.width * 0.3, vp.height * 0.4]; const ll = await page.evaluate(P => map.unproject(P), P); await page.mouse.move(P[0], P[1]);
    const logg = [await page.evaluate(() => window.__prove())];
    for (let i = 0; i < 3; i++) { await page.mouse.wheel(0, -100); await kjor(page, 80, logg); }
    await kjor(page, 900, logg);
    res.scenarier.hjul = { bevegelse: maal(logg), zoom: +(logg.at(-1).z - logg[0].z).toFixed(2), ankerPx: await ankerFeil(page, ll, P) };
    await page.keyboard.press('Escape'); await kjor(page, 1600);
  }
  if (ok('dra')) {   // dra og slipp: treghet tar over farten uten hopp
    const logg = [await page.evaluate(() => window.__prove())]; await page.mouse.move(450, 300); await page.mouse.down(); await kjor(page, BILDE, logg);
    const n0 = logg.length; for (let i = 1; i <= 12; i++) { await page.mouse.move(450 + i * 14, 300 + i * 4); await kjor(page, BILDE, logg); }
    const n1 = logg.length; await page.mouse.up(); await kjor(page, 1600, logg);
    const m = maal(logg); const draFart = m.d.slice(n0, n1 - 1).slice(-3); const etter = m.d.slice(n1 - 1, n1 + 2);
    res.scenarier.dra = { bevegelse: m, draFart, etterSlipp: etter, overlevering: draFart.length && etter.length ? +(Math.max(...etter) / (draFart.reduce((a, b) => a + b, 0) / draFart.length)).toFixed(2) : null };
    await page.keyboard.press('Escape'); await kjor(page, 1800);
  }
  if (ok('avbryt')) {   // hjem-glidningen avbrytes av et dra midtveis: kameraet følger handa, glidningen slutter
    await page.evaluate(() => map.jumpTo({ zoom: map.getZoom() + 1.2, bearing: map.getBearing() + 40 })); await kjor(page, 200);
    const logg = [await page.evaluate(() => window.__prove())]; await page.keyboard.press('Escape'); await kjor(page, 450, logg);
    const nA = logg.length; await page.mouse.move(400, 300); await page.mouse.down(); for (let i = 1; i <= 6; i++) { await page.mouse.move(400 - i * 10, 300); await kjor(page, BILDE, logg); }
    await page.mouse.up(); const nB = logg.length; await kjor(page, 1600, logg);
    const m = maal(logg); const etter = maal(logg, nB + 25);   // et halvt sekund etter slipp: står kameraet, eller glir det videre hjem?
    res.scenarier.avbryt = { bevegelse: m, iAvbruddet: m.d.slice(nA - 2, nA + 3), glirVidereEtterSlipp: etter.topp, zoomIgjen: +(logg.at(-1).z - logg[0].z).toFixed(2) };
    await page.keyboard.press('Escape'); await kjor(page, 1800);
  }
  if (ok('hjem')) {   // hjem fra et annet sted: én rolig bevegelse
    await page.evaluate(() => map.jumpTo({ zoom: map.getZoom() + 1, bearing: map.getBearing() - 60, center: map.unproject([700, 150]) })); await kjor(page, 200);
    const logg = [await page.evaluate(() => window.__prove())]; await page.keyboard.press('Escape'); await kjor(page, 2000, logg);
    res.scenarier.hjem = { bevegelse: maal(logg) };
  }
  await ctx.close();
}
// ---------------- introen: kontinuitet, og overgangen når den avbrytes ----------------
if (ok('intro')) {
  const { ctx, page } = await aapne({ skip: false });
  const logg = [await page.evaluate(() => window.__prove())]; await kjor(page, 1500, logg);
  const nA = logg.length; await page.mouse.move(450, 300); await page.mouse.down(); for (let i = 1; i <= 4; i++) { await page.mouse.move(450 + i * 8, 300); await kjor(page, BILDE, logg); }
  await page.mouse.up(); await kjor(page, 1500, logg);
  const tilt = logg.map(l => l.sol ? l.sol.tilt : 0); const dt = tilt.slice(1).map((v, i) => Math.abs(v - tilt[i]));
  res.scenarier.intro = { kameraFoerAvbrudd: maal(logg, 0, nA), tiltHoppStorst: +Math.max(...dt).toFixed(3), tiltVedAvbrudd: tilt.slice(nA - 2, nA + 4).map(v => +v.toFixed(3)), tiltSlutt: +tilt.at(-1).toFixed(3) };
  await ctx.close();
}
// ---------------- mobil ----------------
if (['mtrykk', 'klyp', 'mdobbel', 'ark'].some(ok)) {
  const { ctx, page, vp } = await aapne({ mobil: true });
  const cdp = await ctx.newCDPSession(page);
  const touch = (type, pts) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: pts.map((p, i) => ({ x: p[0], y: p[1], id: i + 1 })) });
  await kjor(page, 400);
  if (ok('mtrykk')) {
    const k0 = await page.evaluate(() => window.__prove()); const kp = await skjerm(page, ...KIRKE);
    const logg = [k0]; await page.touchscreen.tap(kp[0], kp[1]); await kjor(page, 2400, logg);
    const k1 = logg.at(-1); const hus = await skjerm(page, ...KIRKE);
    res.scenarier.mtrykk = { inn: maal(logg), kortVis: k1.kort.vis, kortRamme: k1.kort, bunnark: k1.kort.vis && k1.kort.bunn > vp.height - 40 && k1.kort.w > vp.width * 0.8, husOverKortet: k1.kort.vis && hus[1] < k1.kort.top && hus[1] > 0, kortInn: await kortLogg(page),
      historikk: await page.evaluate(() => !!(history.state && history.state.kort)) };
    if (ok('ark') && k1.kort.vis) {   // dra kortet ned med fingeren: det følger fingeren og lukkes
      const x = vp.width / 2, y0 = k1.kort.top + 14; const spor = [];
      await touch('touchStart', [[x, y0]]); await kjor(page, BILDE);
      for (let i = 1; i <= 8; i++) { await touch('touchMove', [[x, y0 + i * 18]]); await kjor(page, BILDE); spor.push(await page.evaluate(() => document.getElementById('kort').getBoundingClientRect().top)); }
      await touch('touchEnd', []); await kjor(page, 900);
      const k2 = await page.evaluate(() => window.__prove());
      res.scenarier.ark = { folgerFingeren: +(spor.at(-1) - k1.kort.top).toFixed(0), lukket: !k2.kort.vis, kortUt: await kortLogg(page) };
    }
    // tilbake (Android-tilbake / nettleserens tilbake) lukker kortet i stedet for å forlate siden
    const kp2 = await skjerm(page, ...KIRKE); await page.touchscreen.tap(kp2[0], kp2[1]); await kjor(page, 2400);
    const harState = await page.evaluate(() => !!(history.state && history.state.kort));
    if (harState) { await page.evaluate(() => history.back()); await kjor(page, 1200); }
    res.scenarier.tilbake = { harHistorikk: harState, kortLukket: harState ? !(await page.evaluate(() => window.__prove())).kort.vis : false };
    await page.evaluate(() => { const k = document.querySelector('#kort .lukk'); if (document.getElementById('kort').classList.contains('vis')) k.click(); }); await kjor(page, 1600);
  }
  if (ok('klyp')) {   // klyp rundt midtpunktet mellom fingrene: bakkepunktet der står under fingrene
    const M = [vp.width * 0.4, vp.height * 0.45]; const ll = await page.evaluate(M => map.unproject(M), M);
    const logg = [await page.evaluate(() => window.__prove())];
    await touch('touchStart', [[M[0] - 30, M[1]], [M[0] + 30, M[1]]]); await kjor(page, BILDE, logg);
    for (let i = 1; i <= 10; i++) { await touch('touchMove', [[M[0] - 30 - i * 8, M[1] - i * 2], [M[0] + 30 + i * 8, M[1] + i * 2]]); await kjor(page, BILDE, logg); }
    await touch('touchEnd', []); await kjor(page, 1000, logg);
    res.scenarier.klyp = { bevegelse: maal(logg), zoom: +(logg.at(-1).z - logg[0].z).toFixed(2), ankerPx: await ankerFeil(page, ll, M) };
  }
  if (ok('mdobbel')) {   // dobbelttrykk: zoomer inn mot punktet
    await page.evaluate(() => window.__hjem && window.__hjem()); await kjor(page, 1800);
    const P = [vp.width * 0.6, vp.height * 0.35]; const ll = await page.evaluate(P => map.unproject(P), P);
    const logg = [await page.evaluate(() => window.__prove())];
    await page.touchscreen.tap(P[0], P[1]); await kjor(page, 100, logg); await page.touchscreen.tap(P[0], P[1]); await kjor(page, 1500, logg);
    res.scenarier.mdobbel = { bevegelse: maal(logg), zoom: +(logg.at(-1).z - logg[0].z).toFixed(2), ankerPx: await ankerFeil(page, ll, P) };
  }
  await ctx.close();
}
// ---------------- redusert bevegelse ----------------
if (ok('redusert')) {
  const { ctx, page } = await aapne({ redusert: true });
  await kjor(page, 400); const kp = await skjerm(page, ...KIRKE); await page.mouse.click(kp[0], kp[1]); await kjor(page, 1200);
  const kl = await kortLogg(page); const s = await page.evaluate(() => window.__prove());
  res.scenarier.redusert = { kortVis: s.kort.vis, kortInn: kl, kortGlir: kl.some(x => x.anim.some(a => /transform/.test(a.navn))) };
  await ctx.close();
}
res.ferdig = new Date().toISOString();
fs.writeFileSync(utfil, JSON.stringify(res, null, 1));
for (const [n, v] of Object.entries(res.scenarier)) console.log(n, JSON.stringify(v, (k, x) => k === 'd' ? undefined : x));
console.log('feil', JSON.stringify(res.feil));
await browser.close(); server.close();
