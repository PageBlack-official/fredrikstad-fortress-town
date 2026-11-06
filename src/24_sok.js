import * as maplibregl from 'maplibre-gl';
import { DATA, Q0, map, tilLngLat } from './00_oppsett.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { BYGG_ID, kort, kort_, velgHus, velgPunkt } from './16_interaksjon.js';
// ---- søk og kategorier (Vegar: «parkering, finne steder å spise, kultur»): finn et sted, fly dit, les kortet ----
// Stedene står i data/steder.json (verktoy/steder.py: OpenStreetMap, kommunens parkering, kartbrosjyren). Et sted i et bygg løfter bygget
// og viser stedet i kortet; et sted ute (parkering, toalett, statue) får en nål og kortet. En kategori viser nåler for alle stedene i den.
const S = DATA.steder || { kategorier: [], steder: [] };
// gjesteversjonen (30_gjest, ?gjest=<id>): partnerens anbefalte steder er en egen kategori øverst
const GJEST = (DATA.partnere || []).find(p => p.id === Q0.get('gjest'));
if (GJEST && GJEST.anbefalt && GJEST.anbefalt.length) {
  S.kategorier = [{ id: 'anbefalt', navn: `Anbefalt av ${GJEST.navn}` }, ...S.kategorier];
  for (const id of GJEST.anbefalt) { const s = S.steder.find(x => x.id === id); if (s) S.steder.push({ ...s, id: 'anbefalt-' + s.id, kategori: 'anbefalt' }); }
}
const KAT = new Map(S.kategorier.map(k => [k.id, k.navn]));
const IKON = {   // én strek per kategori, samme stil som knappene
  spise: '<path d="M7 3v8a2 2 0 0 0 2 2v8M5 3v5M9 3v5M16 3c-2 1.5-2.5 4-2.5 7h2.5v11"/>',
  kultur: '<path d="M3 9l9-5 9 5M5 9v9M9.5 9v9M14.5 9v9M19 9v9M3 20h18"/>',
  se: '<path d="M4 8.5h3.2L8.8 6h6.4l1.6 2.5H20V19H4z"/><circle cx="12" cy="13.4" r="3.1"/>',
  kulturminne: '<path d="M4 21h16M6 21V10M10 21V10M14 21V10M18 21V10M3 10l9-6 9 6z"/>',
  handle: '<path d="M5 8h14l-1 12H6L5 8zM9 8a3 3 0 0 1 6 0"/>',
  sove: '<path d="M3 18V7M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3M7 11.5h.01"/>',
  parkering: '<path d="M7 20V4h6a4.5 4.5 0 0 1 0 9H7"/>',
  anbefalt: '<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.9z"/>',
  toalett: '<circle cx="8" cy="5" r="1.6"/><circle cx="16" cy="5" r="1.6"/><path d="M8 8v12M6 10h4M16 8l-3 7h6l-3-7v12"/>',
};
// fargen per kategori (som Apple Kart: én farge per slags sted, hvitt symbol på farget sirkel)
const FARGE = { spise: '#f0892b', kultur: '#d6457a', se: '#139a8a', kulturminne: '#9c7350', handle: '#e2a312', sove: '#8657cf', parkering: '#2f6fd6', anbefalt: '#e0483e', toalett: '#7a838e' };
// merket: ikonet hvitt på en sirkel i kategoriens farge; rett opp, aldri dreid (Vegar 06.11: «du har lagt dem skrått»)
const merke = (k, d = 24) => `<span class="merke" style="--f:${FARGE[k] || '#5f6670'};--d:${d}px">${svg(k, Math.round(d * 0.6), 2.1)}</span>`;
const svg = (k, s = 18, w = 1.7) => `<svg viewBox="0 0 24 24" width="${s}" height="${s}" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round">${IKON[k] || IKON.se}</svg>`;
const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const enkel = t => String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/æ/g, 'ae').replace(/ø/g, 'o').replace(/å/g, 'a');
const IOS = /iP(hone|ad|od)|Macintosh.*Mobile/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

// åpningstider fra OSM («Mo-Fr 10:00-17:00; Sa 10:00-15:00») vises lesbart på norsk; det vi ikke forstår, vises som det står
const DAG = { Mo: 'man', Tu: 'tir', We: 'ons', Th: 'tor', Fr: 'fre', Sa: 'lør', Su: 'søn', PH: 'helligdager' };
const MND = { Jan: 'jan', Feb: 'feb', Mar: 'mar', Apr: 'apr', May: 'mai', Jun: 'jun', Jul: 'jul', Aug: 'aug', Sep: 'sep', Oct: 'okt', Nov: 'nov', Dec: 'des' };
const aapent = t => !t ? '' : t === '24/7' ? 'Døgnåpent' : t.replace(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/g, m => MND[m]).replace(/\b(Mo|Tu|We|Th|Fr|Sa|Su|PH)\b/g, d => DAG[d]).replace(/\boff\b/g, 'stengt').replace(/;\s*/g, ' · ').replace(/,/g, ', ');

// ---- kortet for et sted ----
// et sted kan ha flere plasser (punkter: samme gate med beboerparkering i tre strekk, fem toaletter); kortet viser plassen du valgte
function fyllSted(s, b, p = s){
  kort.querySelector('h2').textContent = s.navn;
  const bygg = b && (b.navn || b.adr);
  kort.querySelector('.a').textContent = [p.type ?? s.type, s.adresse || (bygg && bygg !== s.navn ? bygg : '')].filter(Boolean).join(' · ');
  kort.querySelector('.b').textContent = p.merknad ?? s.merknad ?? '';
  const linjer = [];
  if (s.aapent) linjer.push(`<li>${esc(aapent(s.aapent))}</li>`);
  if (s.mat) linjer.push(`<li>${esc(s.mat[0].toUpperCase() + s.mat.slice(1))}</li>`);
  if (s.easypark) linjer.push(`<li>EasyPark-sone ${esc(s.easypark)}</li>`);
  if (s.telefon) linjer.push(`<li><a href="tel:${esc(s.telefon.replace(/\s/g, ''))}">${esc(s.telefon)}</a></li>`);
  if (s.nettside) linjer.push(`<li><a href="${esc(/^https?:/.test(s.nettside) ? s.nettside : 'https://' + s.nettside)}" target="_blank" rel="noopener">${s.kategori === 'kulturminne' ? 'Kulturminneplanen (PDF)' : esc(s.nettside.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''))}</a></li>`);
  if (s.punkter) linjer.push(`<li>${s.punkter.length} plasser i kartet</li>`);
  const ll = tilLngLat(p.x, p.y);
  const vei = IOS ? `https://maps.apple.com/?daddr=${ll.lat.toFixed(6)},${ll.lng.toFixed(6)}&dirflg=w` : `https://www.google.com/maps/dir/?api=1&destination=${ll.lat.toFixed(6)},${ll.lng.toFixed(6)}&travelmode=walking`;
  linjer.push(`<li class="vei"><a href="${vei}" target="_blank" rel="noopener">Veibeskrivelse</a></li>`);
  kort.querySelector('.her').innerHTML = linjer.join('');
  kort.querySelector('.ogsa').innerHTML = ''; kort.querySelector('.ogsa-t').textContent = ''; kort.querySelector('.farge').innerHTML = '';
  kort.querySelector('.id').textContent = s.kilde === 'OpenStreetMap' ? '© OpenStreetMap-bidragsytere' : (s.kilde || '');
}
let valgtSted = null;
let valgtNaal = null;   // nøkkelen til nåla som er valgt: id, eller id#n for plass n
function velgSted(s, n = 0){
  const p = s.punkter ? s.punkter[n] || s.punkter[0] : s;
  valgtSted = s; valgtNaal = s.punkter ? `${s.id}#${s.punkter.indexOf(p)}` : s.id; tegnNaaler();
  const bid = p.bygg_id ?? s.bygg_id, g = bid && buildings.find(x => x.userData.b && x.userData.b.id === bid);
  if (g) { velgHus(g); fyllSted(s, BYGG_ID.get(bid), p); }
  else velgPunkt(() => fyllSted(s, null, p), p.x, p.y);
  kort_.sted = s.id;
}
kort_.vedLukk.push(() => { kort_.sted = null; if (valgtSted) { valgtSted = null; valgtNaal = null; tegnNaaler(); } });

// ---- nålene: alle stedene i valgt kategori, og stedet som er valgt ----
const naaler = new Map(); let aktivKat = null;
function naal(s, n){
  const p = n === undefined ? s : s.punkter[n];
  const el = document.createElement('button'); el.type = 'button'; el.className = 'naal'; el.dataset.kat = s.kategori;
  el.innerHTML = merke(s.kategori, 28); el.setAttribute('aria-label', `${s.navn}, ${s.type || KAT.get(s.kategori) || ''}`); el.title = s.navn;
  el.addEventListener('click', e => { e.stopPropagation(); velgSted(s, n); });
  return new maplibregl.Marker({ element: el, anchor: 'bottom' }).setLngLat(tilLngLat(p.x, p.y));
}
function tegnNaaler(){
  // én nål per plass: nøkkel id for et sted med én plass, id#n for plass n
  const vis = new Map();
  for (const s of S.steder) if (s.kategori === aktivKat || s === valgtSted) {
    if (s.punkter) s.punkter.forEach((_, n) => vis.set(`${s.id}#${n}`, [s, n])); else vis.set(s.id, [s, undefined]); }
  for (const [k, m] of naaler) if (!vis.has(k)) { m.remove(); naaler.delete(k); }
  for (const [k, [s, n]] of vis) if (!naaler.has(k)) { const m = naal(s, n); m.addTo(map); naaler.set(k, m); }
  for (const [k, m] of naaler) m.getElement().classList.toggle('valgt', k === valgtNaal);
}

// ---- panelet: søkefelt, kategorier, treff ----
const knapp = document.createElement('button'); knapp.id = 'sok'; knapp.type = 'button'; knapp.setAttribute('aria-haspopup', 'dialog');
knapp.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/></svg><span>Finn</span>`;
knapp.setAttribute('aria-label', 'Finn steder i Gamlebyen');
const panel = document.createElement('div'); panel.id = 'sokpanel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Finn steder'); panel.hidden = true;
panel.innerHTML = `<div class="felt">${'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/></svg>'}<input type="search" placeholder="Spisested, museum, parkering …" aria-label="Søk etter sted" autocomplete="off" enterkeyhint="search"><button type="button" class="lukk" aria-label="Lukk">×</button></div>
<div class="kat" role="group" aria-label="Kategorier">${S.kategorier.filter(k => S.steder.some(s => s.kategori === k.id)).map(k => `<button type="button" data-k="${k.id}" aria-pressed="false">${merke(k.id, 22)}<span>${esc(k.navn)}</span></button>`).join('')}</div>
<ul class="treff" role="listbox" aria-label="Treff"></ul><p class="kilde">Steder: © OpenStreetMap-bidragsytere, Fredrikstad kommune (parkering, kulturminneplanen)</p>`;
(document.getElementById('topp') || document.body).prepend(knapp); document.body.append(panel);
const inn = panel.querySelector('input'), liste = panel.querySelector('.treff');
const INDEKS = S.steder.map(s => ({ s, t: enkel([s.navn, s.type, s.mat, s.adresse, KAT.get(s.kategori)].join(' ')) }));
function treff(){
  const q = enkel(inn.value.trim()), ord = q.split(/\s+/).filter(Boolean);
  let r = INDEKS.filter(({ s, t }) => (!aktivKat || s.kategori === aktivKat) && ord.every(o => t.includes(o)));
  if (q) r.sort((a, b) => (enkel(b.s.navn).startsWith(q) ? 1 : 0) - (enkel(a.s.navn).startsWith(q) ? 1 : 0));
  const vis = (q || aktivKat) ? r.slice(0, 60) : [];
  liste.innerHTML = vis.map(({ s }, i) => `<li role="option" tabindex="-1" data-i="${S.steder.indexOf(s)}" ${i === 0 ? 'aria-selected="true"' : ''}>${merke(s.kategori, 28)}<span><b>${esc(s.navn)}</b><small>${esc([s.type, s.punkter ? `${s.punkter.length} plasser` : '', s.aapent ? aapent(s.aapent).split(' · ')[0] : ''].filter(Boolean).join(' · '))}</small></span></li>`).join('')
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
