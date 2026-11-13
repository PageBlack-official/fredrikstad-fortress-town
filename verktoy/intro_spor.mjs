// Intro-spor (13.11): Chrome-ytelsesspor av introen (uten ?skip) og en topp-liste over hva hovedtråden brukte tida på,
// samlet per funksjon (selvtid) og per hendelsestype. Bruk: PW_GPU=1 node verktoy/intro_spor.mjs <ut-mappe> <index.html>
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, ut, fil] = process.argv; const W = +(process.env.BREDDE || 1280), H = +(process.env.HOYDE || 720), DPR = +(process.env.DPR || 2);
const server = http.createServer((q, r) => { r.setHeader('content-type', 'text/html; charset=utf-8'); r.end(fs.readFileSync(path.resolve(fil))); });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DPR }); const page = await ctx.newPage();
fs.mkdirSync(ut, { recursive: true }); const spor = path.join(ut, 'spor.json');
await browser.startTracing(page, { path: spor, screenshots: false, categories: ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'v8.execute', 'disabled-by-default-v8.cpu_profiler', 'blink.user_timing', 'gpu'] });
await page.goto(`http://127.0.0.1:${port}/index.html`);
await page.waitForFunction(() => window.__klar && window.__klar(), null, { timeout: 120000, polling: 200 });
await page.waitForTimeout(300);
await browser.stopTracing();
await browser.close(); server.close();
const T = JSON.parse(fs.readFileSync(spor, 'utf8')); const ev = T.traceEvents || T;
// hovedtråden: tråden med flest RunTask i renderprosessen
const tr = {}; for (const e of ev) if (e.name === 'RunTask' && e.dur) { const k = e.pid + ':' + e.tid; tr[k] = (tr[k] || 0) + e.dur; }
const hoved = Object.entries(tr).sort((a, b) => b[1] - a[1])[0][0];
const per = {}; let lange = [];
for (const e of ev) { if (e.pid + ':' + e.tid !== hoved || !e.dur) continue; per[e.name] = (per[e.name] || 0) + e.dur; if (e.name === 'RunTask' && e.dur > 50000) lange.push(Math.round(e.dur / 1000)); }
// CPU-profil: selvtid per funksjon
const prof = {}; const noder = {}; let tidsSum = 0;
for (const e of ev) if (e.name === 'ProfileChunk' && e.args && e.args.data && e.args.data.cpuProfile) {
  const cp = e.args.data.cpuProfile; for (const n of (cp.nodes || [])) noder[n.id] = n;
  const s = cp.samples || [], d = e.args.data.timeDeltas || []; for (let i = 0; i < s.length; i++) { const n = noder[s[i]]; if (!n) continue; const cf = n.callFrame || {}; const k = (cf.functionName || '(anon)') + ' ' + (cf.url || '').split('/').pop() + ':' + cf.lineNumber; prof[k] = (prof[k] || 0) + (d[i] || 0); tidsSum += d[i] || 0; } }
const topp = o => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, 25).map(([k, v]) => `${(v / 1000).toFixed(0).padStart(6)} ms  ${k}`).join('\n');
const rapport = `HOVEDTRÅD hendelser (ms):\n${topp(per)}\n\nLANGE OPPGAVER >50 ms: ${lange.length} (${lange.slice(0, 30).join(', ')})\n\nCPU-PROFIL selvtid (sum ${(tidsSum / 1000).toFixed(0)} ms):\n${topp(prof)}\n`;
fs.writeFileSync(path.join(ut, 'topp.txt'), rapport); console.log(rapport);
