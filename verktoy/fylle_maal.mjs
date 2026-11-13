// Fyllmåler (13.11): hvor mye koster hvert pass på GPU-en? Hjemmevisningen, kartet tvinges til å tegne hvert rAF i 4 s,
// og vi teller kartets bilder (map 'render') og tida mellom dem. Varianter = spørrestreng + taster i feilsøkingsruta (?d=1).
// Bruk: PW_GPU=1 node verktoy/fylle_maal.mjs <ut.json> <index.html>   (miljø: BREDDE, HOYDE, DPR, RUNDER, VAR=json-liste)
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, utfil, fil] = process.argv; const W = +(process.env.BREDDE || 1280), H = +(process.env.HOYDE || 720), DPR = +(process.env.DPR || 2), RUNDER = +(process.env.RUNDER || 2);
const VAR = process.env.VAR ? JSON.parse(process.env.VAR) : [
  { navn: 'grunn', q: '' }, { navn: 'utenSpeil', q: '&nospeil=1' }, { navn: 'ao0', q: '&d=1', taster: ['a', 'a'] }, { navn: 'ss1', q: '&d=1', taster: ['s', 's'] },
  { navn: 'msaa0', q: '&d=1', taster: ['n'] }, { navn: 'pix3', q: '&pix=3' }, { navn: 'tegn0', q: '&tegn=0' } ];
const server = http.createServer((q, r) => { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(path.resolve(fil))); });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const med = a => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const res = { vindu: { W, H, DPR }, maal: {} };
async function en(v) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR }); const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${v.q}`);
  await page.waitForFunction(() => window.__klar && window.__klar() && window.__vaareBilder > 5, null, { timeout: 120000, polling: 200 });
  await page.waitForTimeout(1500);
  for (const t of (v.taster || [])) { await page.keyboard.press(t); await page.waitForTimeout(200); }
  if (v.js) { await page.evaluate(v.js); }
  await page.waitForTimeout(800);
  const d = await page.evaluate(() => new Promise(ok => { const kl = []; const h = () => kl.push(performance.now()); map.on('render', h);
    let paa = true; const loop = () => { if (!paa) return; map.triggerRepaint(); requestAnimationFrame(loop); }; loop();
    setTimeout(() => { paa = false; map.off('render', h); ok({ kl, info: { w: map.getCanvas().width, h: map.getCanvas().height, kval: window.__kval && window.__kval(), kall: (window.__pt || {}).kall } }); }, 4000); }));
  await ctx.close();
  const iv = []; for (let i = 1; i < d.kl.length; i++) iv.push(d.kl[i] - d.kl[i - 1]);
  return { bilder_s: +(d.kl.length / 4).toFixed(1), ms_med: +med(iv).toFixed(1), info: d.info };
}
for (let r = 0; r < RUNDER; r++) for (const v of VAR) { const u = await en(v); (res.maal[v.navn] ||= []).push(u); console.log(`r${r + 1} ${v.navn.padEnd(10)} ${String(u.bilder_s).padStart(5)} bilder/s  ${u.ms_med} ms/bilde  lerret ${u.info.w}x${u.info.h} kval ${JSON.stringify(u.info.kval)}`); }
fs.mkdirSync(path.dirname(utfil), { recursive: true }); fs.writeFileSync(utfil, JSON.stringify(res, null, 1));
await browser.close(); server.close();
