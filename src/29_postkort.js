import { map } from './00_oppsett.js';
import { VAER } from './23_vaer.js';
import { melding } from './25_her.js';
// ---- postkort: utsikten du står i, med papirkant og dato, til å dele eller lagre (Vegar: «postkort-knapp») ----
// Bildet hentes fra lerretet i samme bilde som det tegnes (MapLibre «render»), så det trengs ingen preserveDrawingBuffer.
const MND = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember'];
const knapp = document.createElement('button'); knapp.id = 'postkort'; knapp.type = 'button'; knapp.setAttribute('aria-label', 'Lag postkort av utsikten'); knapp.title = 'Postkort';
knapp.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><rect x="3" y="6" width="18" height="13" rx="2"/><circle cx="12" cy="12.5" r="3.4"/><path d="M8.5 6l1.4-2h4.2l1.4 2"/></svg>';
(document.getElementById('topp') || document.body).append(knapp);
function hent(){ return new Promise(ok => { map.once('render', () => map.getCanvas().toBlob(ok, 'image/png')); map.triggerRepaint(); }); }
async function lag(){
  knapp.disabled = true;
  try {
    const bilde = await createImageBitmap(await hent()), w = bilde.width, h = bilde.height;
    const kant = Math.round(Math.min(w, h) * 0.045), tekstH = Math.round(Math.min(w, h) * 0.11);
    const c = document.createElement('canvas'); c.width = w + 2 * kant; c.height = h + kant + tekstH; const g = c.getContext('2d');
    g.fillStyle = '#f6f3ea'; g.fillRect(0, 0, c.width, c.height); g.drawImage(bilde, kant, kant);
    g.strokeStyle = 'rgba(43,36,32,.18)'; g.lineWidth = Math.max(1, kant * 0.04); g.strokeRect(kant, kant, w, h);
    const d = new Date(), v = VAER.naa, f = Math.round(tekstH * 0.34);
    g.fillStyle = '#2b2420'; g.font = `600 ${f}px "Helvetica Neue", Helvetica, Arial, sans-serif`; g.textBaseline = 'middle';
    g.fillText('Gamle Fredrikstad', kant, h + kant + tekstH / 2);
    g.font = `400 ${Math.round(f * 0.72)}px "Helvetica Neue", Helvetica, Arial, sans-serif`; g.fillStyle = '#7a7166'; g.textAlign = 'right';
    const vt = v && v.temp != null ? ` · ${Math.round(v.temp)}°` : '';
    g.fillText(`${d.getDate()}. ${MND[d.getMonth()]} ${d.getFullYear()}${vt}`, c.width - kant, h + kant + tekstH / 2);
    const blob = await new Promise(ok => c.toBlob(ok, 'image/jpeg', 0.92)), navn = `gamlebyen-${d.toISOString().slice(0, 10)}.jpg`;
    const fil = new File([blob], navn, { type: 'image/jpeg' });
    if (navigator.canShare && navigator.canShare({ files: [fil] })) { try { await navigator.share({ files: [fil], title: 'Gamle Fredrikstad' }); } catch (_) { /* avbrutt */ } }
    else { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = navn; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000); melding('Postkortet er lagret.'); }
  } catch (e) { melding('Fikk ikke laget postkortet.'); }
  finally { knapp.disabled = false; }
}
knapp.addEventListener('click', lag);
window.__postkort = lag;
