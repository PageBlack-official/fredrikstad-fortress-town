// Felles inngang til Playwright for testene i verktoy/. Finner Playwright der den er installert:
//   PW_MODUL (sti til playwright/index.js), ellers skyens /opt/npm-tools, ellers prosjektets egen node_modules (npm install).
// GL: i skyen tegner Chromium med SwiftShader (programvare). Med PW_GPU=1 (Mac-en med skjermkort) byttes SwiftShader-flaggene
// ut med maskinens eget skjermkort (ANGLE/Metal på macOS), så testene går mange ganger fortere. Resten av oppsettet er likt.
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const kandidater = [process.env.PW_MODUL, '/opt/npm-tools/node_modules/playwright/index.js', 'playwright'].filter(Boolean);
let pw = null;
for (const k of kandidater) { try { pw = require(k); break; } catch { /* prøv neste */ } }
if (!pw) throw new Error('fant ikke Playwright (sett PW_MODUL eller kjør npm install)');
const GPU = process.env.PW_GPU === '1';
const SW = /swiftshader|^--use-gl=|^--use-angle=/;
function args(a = []){
  if (!GPU) return a;
  const ut = a.filter(x => !SW.test(x));
  ut.push(process.platform === 'darwin' ? '--use-angle=metal' : '--use-angle=default', '--ignore-gpu-blocklist', '--enable-gpu-rasterization');
  return [...new Set(ut)];
}
const ekte = pw.chromium;
export const chromium = new Proxy(ekte, { get(t, k){
  if (k === 'launch') return (o = {}) => t.launch({ ...o, args: args(o.args) });
  if (k === 'launchPersistentContext') return (d, o = {}) => t.launchPersistentContext(d, { ...o, args: args(o.args) });
  const v = t[k]; return typeof v === 'function' ? v.bind(t) : v; } });
export default { ...pw, chromium };
// pngjs (verktoy/pixel.mjs): samme leting
export function finn(navn){ for (const k of [`/opt/npm-tools/node_modules/${navn}`, navn]) { try { return require.resolve(k); } catch { /* neste */ } } return null; }
