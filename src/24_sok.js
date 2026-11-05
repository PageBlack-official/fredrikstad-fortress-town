import * as maplibregl from 'maplibre-gl';
import { DATA, map, tilLngLat } from './00_oppsett.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { BYGG_ID, kort, kort_, velgHus, velgPunkt } from './16_interaksjon.js';
// ---- søk og kategorier (Vegar: «parkering, finne steder å spise, kultur»): finn et sted, fly dit, les kortet ----
// Stedene står i data/steder.json (verktoy/steder.py: OpenStreetMap, kommunens parkering, kartbrosjyren). Et sted i et bygg løfter bygget
// og viser stedet i kortet; et sted ute (parkering, toalett, statue) får en nål og kortet. En kategori viser nåler for alle stedene i den.
const S = DATA.steder || { kategorier: [], steder: [] };
const KAT = new Map(S.kategorier.map(k => [k.id, k.navn]));
const IKON = {   // én strek per kategori, samme stil som knappene
  spise: '<path d="M7 3v8a2 2 0 0 0 2 2v8M5 3v5M9 3v5M16 3c-2 1.5-2.5 4-2.5 7h2.5v11"/>',
  kultur: '<path d="M3 9l9-5 9 5M5 9v9M9.5 9v9M14.5 9v9M19 9v9M3 20h18"/>',
  se: '<circle cx="12" cy="10" r="3"/><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/>',
  handle: '<path d="M5 8h14l-1 12H6L5 8zM9 8a3 3 0 0 1 6 0"/>',
  sove: '<path d="M3 18V7M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3M7 11.5h.01"/>',
  parkering: '<path d="M7 20V4h6a4.5 4.5 0 0 1 0 9H7"/>',
  toalett: '<circle cx="8" cy="5" r="1.6"/><circle cx="16" cy="5" r="1.6"/><path d="M8 8v12M6 10h4M16 8l-3 7h6l-3-7v12"/>',
};
const svg = (k, s = 18) => `<svg viewBox="0 0 24 24" width="${s}" height="${s}" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${IKON[k] || IKON.se}</svg>`;
const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const enkel = t => String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/æ/g, 'ae').replace(/ø/g, 'o').replace(/å/g, 'a');
const IOS = /iP(hone|ad|od)|Macintosh.*Mobile/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

// åpningstider fra OSM («Mo-Fr 10:00-17:00; Sa 10:00-15:00») vises lesbart på norsk; det vi ikke forstår, vises som det står
const DAG = { Mo: 'man', Tu: 'tir', We: 'ons', Th: 'tor', Fr: 'fre', Sa: 'lør', Su: 'søn', PH: 'helligdager' };
const MND = { Jan: 'jan', Feb: 'feb', Mar: 'mar', Apr: 'apr', May: 'mai', Jun: 'jun', Jul: 'jul', Aug: 'aug', Sep: 'sep', Oct: 'okt', Nov: 'nov', Dec: 'des' };
const aapent = t => !t ? '' : t === '24/7' ? 'Døgnåpent' : t.replace(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/g, m => MND[m]).replace(/\b(Mo|Tu|We|Th|Fr|Sa|Su|PH)\b/g, d => DAG[d]).replace(/\boff\b/g, 'stengt').replace(/;\s*/g, ' · ').replace(/,/g, ', ');

// ---- kortet for et sted ----
function fyllSted(s, b){
  kort.querySelector('h2').textContent = s.navn;
  const bygg = b && (b.navn || b.adr);
  kort.querySelector('.a').textContent = [s.type, s.adresse || (bygg && bygg !== s.navn ? bygg : '')].filter(Boolean).join(' · ');
  kort.querySelector('.b').textContent = s.merknad || '';
  const linjer = [];
  if (s.aapent) linjer.push(`<li>${esc(aapent(s.aapent))}</li>`);
  if (s.mat) linjer.push(`<li>${esc(s.mat[0].toUpperCase() + s.mat.slice(1))}</li>`);
  if (s.easypark) linjer.push(`<li>EasyPark-sone ${esc(s.easypark)}</li>`);
  if (s.telefon) linjer.push(`<li><a href="tel:${esc(s.telefon.replace(/\s/g, ''))}">${esc(s.telefon)}</a></li>`);
  if (s.nettside) linjer.push(`<li><a href="${esc(/^https?:/.test(s.nettside) ? s.nettside : 'https://' + s.nettside)}" target="_blank" rel="noopener">${esc(s.nettside.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''))}</a></li>`);
  const ll = tilLngLat(s.x, s.y);
  const vei = IOS ? `https://maps.apple.com/?daddr=${ll.lat.toFixed(6)},${ll.lng.toFixed(6)}&dirflg=w` : `https://www.google.com/maps/dir/?api=1&destination=${ll.lat.toFixed(6)},${ll.lng.toFixed(6)}&travelmode=walking`;
  linjer.push(`<li class="vei"><a href="${vei}" target="_blank" rel="noopener">Veibeskrivelse</a></li>`);
  kort.querySelector('.her').innerHTML = linjer.join('');
  kort.querySelector('.ogsa').innerHTML = ''; kort.querySelector('.ogsa-t').textContent = ''; kort.querySelector('.farge').innerHTML = '';
  kort.querySelector('.id').textContent = s.kilde === 'OpenStreetMap' ? '© OpenStreetMap-bidragsytere' : (s.kilde || '');
}
let valgtSted = null;
function velgSted(s){
  valgtSted = s; tegnNaaler();
  const g = s.bygg_id && buildings.find(x => x.userData.b && x.userData.b.id === s.bygg_id);
  if (g) { velgHus(g); fyllSted(s, BYGG_ID.get(s.bygg_id)); }
  else velgPunkt(() => fyllSted(s), s.x, s.y);
  kort_.sted = s.id;
}
kort_.vedLukk.push(() => { kort_.sted = null; if (valgtSted) { valgtSted = null; tegnNaaler(); } });

// ---- nålene: alle stedene i valgt kategori, og stedet som er valgt ----
const naaler = new Map(); let aktivKat = null;
function naal(s){
  const el = document.createElement('button'); el.type = 'button'; el.className = 'naal'; el.dataset.kat = s.kategori;
  el.innerHTML = svg(s.kategori, 15); el.setAttribute('aria-label', `${s.navn}, ${s.type || KAT.get(s.kategori) || ''}`); el.title = s.navn;
  el.addEventListener('click', e => { e.stopPropagation(); velgSted(s); });
  return new maplibregl.Marker({ element: el, anchor: 'bottom' }).setLngLat(tilLngLat(s.x, s.y));
}
function tegnNaaler(){
  const vis = new Set(S.steder.filter(s => s.kategori === aktivKat).map(s => s.id)); if (valgtSted) vis.add(valgtSted.id);
  for (const [id, m] of naaler) if (!vis.has(id)) { m.remove(); naaler.delete(id); }
  for (const s of S.steder) if (vis.has(s.id) && !naaler.has(s.id)) { const m = naal(s); m.addTo(map); naaler.set(s.id, m); }
  for (const [id, m] of naaler) m.getElement().classList.toggle('valgt', !!valgtSted && id === valgtSted.id);
}

// ---- panelet: søkefelt, kategorier, treff ----
const knapp = document.createElement('button'); knapp.id = 'sok'; knapp.type = 'button'; knapp.setAttribute('aria-haspopup', 'dialog');
knapp.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/></svg><span>Finn</span>`;
knapp.setAttribute('aria-label', 'Finn steder i Gamlebyen');
const panel = document.createElement('div'); panel.id = 'sokpanel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Finn steder'); panel.hidden = true;
panel.innerHTML = `<div class="felt">${'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/></svg>'}<input type="search" placeholder="Spisested, museum, parkering …" aria-label="Søk etter sted" autocomplete="off" enterkeyhint="search"><button type="button" class="lukk" aria-label="Lukk">×</button></div>
<div class="kat" role="group" aria-label="Kategorier">${S.kategorier.filter(k => S.steder.some(s => s.kategori === k.id)).map(k => `<button type="button" data-k="${k.id}" aria-pressed="false">${svg(k.id, 16)}<span>${esc(k.navn)}</span></button>`).join('')}</div>
<ul class="treff" role="listbox" aria-label="Treff"></ul><p class="kilde">Steder: © OpenStreetMap-bidragsytere, Fredrikstad kommune</p>`;
(document.getElementById('topp') || document.body).prepend(knapp); document.body.append(panel);
const inn = panel.querySelector('input'), liste = panel.querySelector('.treff');
const INDEKS = S.steder.map(s => ({ s, t: enkel([s.navn, s.type, s.mat, s.adresse, KAT.get(s.kategori)].join(' ')) }));
function treff(){
  const q = enkel(inn.value.trim()), ord = q.split(/\s+/).filter(Boolean);
  let r = INDEKS.filter(({ s, t }) => (!aktivKat || s.kategori === aktivKat) && ord.every(o => t.includes(o)));
  if (q) r.sort((a, b) => (enkel(b.s.navn).startsWith(q) ? 1 : 0) - (enkel(a.s.navn).startsWith(q) ? 1 : 0));
  const vis = (q || aktivKat) ? r.slice(0, 60) : [];
  liste.innerHTML = vis.map(({ s }, i) => `<li role="option" tabindex="-1" data-i="${S.steder.indexOf(s)}" ${i === 0 ? 'aria-selected="true"' : ''}>${svg(s.kategori, 16)}<span><b>${esc(s.navn)}</b><small>${esc([s.type, s.aapent ? aapent(s.aapent).split(' · ')[0] : ''].filter(Boolean).join(' · '))}</small></span></li>`).join('')
    || (q ? `<li class="tom">Ingen treff på «${esc(inn.value.trim())}»</li>` : '');
}
function apne(){ panel.hidden = false; knapp.setAttribute('aria-expanded', 'true'); treff(); setTimeout(() => inn.focus({ preventScroll: true }), 30); }
function lukk(){ panel.hidden = true; knapp.setAttribute('aria-expanded', 'false'); }
knapp.addEventListener('click', e => { e.stopPropagation(); panel.hidden ? apne() : lukk(); });
panel.querySelector('.lukk').addEventListener('click', lukk);
inn.addEventListener('input', treff);
inn.addEventListener('keydown', e => {
  const alle = [...liste.querySelectorAll('[data-i]')], i = alle.findIndex(x => x.getAttribute('aria-selected') === 'true');
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); const n = Math.max(0, Math.min(alle.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1))); alle.forEach((x, j) => x.setAttribute('aria-selected', String(j === n))); alle[n] && alle[n].scrollIntoView({ block: 'nearest' }); }
  if (e.key === 'Enter' && alle[Math.max(0, i)]) { velgSted(S.steder[+alle[Math.max(0, i)].dataset.i]); lukk(); }
  if (e.key === 'Escape') { e.stopPropagation(); lukk(); knapp.focus(); }
});
liste.addEventListener('click', e => { const li = e.target.closest('[data-i]'); if (!li) return; velgSted(S.steder[+li.dataset.i]); lukk(); });
panel.querySelector('.kat').addEventListener('click', e => { const b = e.target.closest('[data-k]'); if (!b) return;
  aktivKat = aktivKat === b.dataset.k ? null : b.dataset.k;
  panel.querySelectorAll('[data-k]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.k === aktivKat)));
  tegnNaaler(); treff(); });
addEventListener('pointerdown', e => { if (!panel.hidden && !panel.contains(e.target) && !knapp.contains(e.target)) lukk(); });
addEventListener('keydown', e => { if ((e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) && document.activeElement !== inn) { e.preventDefault(); apne(); } });

window.__sok = { velgSted: id => { const s = S.steder.find(x => x.id === id || x.navn === id); if (s) velgSted(s); return !!s; }, kategori: k => { aktivKat = k; tegnNaaler(); return naaler.size; }, antall: () => S.steder.length };
export { velgSted };
