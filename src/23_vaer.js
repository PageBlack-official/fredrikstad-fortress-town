import { TILSTAND } from './tilstand.js';
import { Q0, map } from './00_oppsett.js';
import { U_SOL } from './02_lys.js';
// ---- været: kartet viser været i Gamlebyen nå (Vegar: «Er det overskyet er det det du ser, er det vinter, vår, sol») ----
// Kilde: Meteorologisk institutt, Locationforecast 2.0 (api.met.no, CC BY 4.0, «Data fra MET Norway»). Hentes ved lasting og hvert
// 15. minutt, mellomlagres i økta. Svarer ikke MET, står kartet i sol som før (ingenting brytes).
// Det været gjør med bildet:
//   skydekke  -> U_SOL.sky (02_lys): solHer() ganges med (1 - sky), så overskyet gir introens gråvær uten kastskygger
//   regn/snø  -> eget lerret over kartet med striper eller fnugg; tetthet etter nedbør per time
//   tåke      -> et lyst slør over kartet
//   årstid    -> U_SOL.aarstid: grønt (plener, trær) får vår-, sommer-, høst- eller vinterfarge etter datoen
//   snødekke  -> U_SOL.sno: tak, bakke og trekroner hvitner når det snør eller er kuldegrader om vinteren
// Test og demo: ?vaer=sol|lettskyet|skyet|regn|sno|taake (fast vær), ?vaer=0 (av), ?aarstid=vaar|sommer|hoest|vinter, ?sno=0..1.
const PUNKT = { lat: 59.2055, lon: 10.9545 };
const VAER_AV = Q0.get('vaer') === '0';
const NAVN = { sol: 'Sol', lettskyet: 'Lettskyet', delvis: 'Delvis skyet', skyet: 'Skyet', regn: 'Regn', sludd: 'Sludd', sno: 'Snø', taake: 'Tåke', torden: 'Torden' };

// MET-symbolet (f.eks. «partlycloudy_day», «lightrainshowers_night») til våre fem størrelser
function fraSymbol(sym, skyProsent, mm, temp){
  const s = (sym || '').replace(/_(day|night|polartwilight)$/, '');
  const v = { sky: Math.min(1, (skyProsent ?? 0) / 100), nedbor: null, mengde: mm || 0, taake: 0, temp, navn: 'sol' };
  if (/fog/.test(s)) { v.taake = 0.55; v.navn = 'taake'; }
  else if (/thunder/.test(s)) { v.nedbor = 'regn'; v.navn = 'torden'; }
  else if (/snow/.test(s)) { v.nedbor = 'sno'; v.navn = 'sno'; }
  else if (/sleet/.test(s)) { v.nedbor = 'sludd'; v.navn = 'sludd'; }
  else if (/rain/.test(s)) { v.nedbor = 'regn'; v.navn = 'regn'; }
  else if (s === 'clearsky' || s === 'fair') v.navn = s === 'fair' ? 'lettskyet' : 'sol';
  else if (s === 'partlycloudy') v.navn = 'delvis';
  else if (s === 'cloudy') v.navn = 'skyet';
  if (v.nedbor && !v.mengde) v.mengde = /light/.test(s) ? 0.4 : /heavy/.test(s) ? 4 : 1.2;
  return v;
}
const FAST = {
  sol: () => fraSymbol('clearsky', 5, 0, 8), lettskyet: () => fraSymbol('fair', 30, 0, 8), skyet: () => fraSymbol('cloudy', 100, 0, 6),
  regn: () => fraSymbol('rain', 100, 1.5, 6), sno: () => fraSymbol('snow', 100, 1.2, -3), taake: () => fraSymbol('fog', 100, 0, 3),
};

// årstiden etter dato (Fredrikstad): fargen grønt ganges med, og styrken. Sommer er tegningens egne farger.
function aarstidFor(d){
  const tving = Q0.get('aarstid'); const m = d.getMonth() + 1, dag = d.getDate();
  const a = tving || (m <= 2 || m === 12 ? 'vinter' : m <= 5 ? 'vaar' : m <= 8 ? 'sommer' : 'hoest');
  const sen = (m === 11 || (m === 10 && dag > 15));   // seint på høsten: brunere, mindre metning
  return a === 'vinter' ? { navn: a, farge: [0.98, 1.04, 0.94], styrke: 0.6 }          // gråere grønt, lite metning
    : a === 'vaar' ? { navn: a, farge: [0.95, 1.42, 0.62], styrke: 0.45 }              // friskt, lyst grønt
      : a === 'hoest' ? { navn: a, farge: sen ? [1.32, 1.02, 0.58] : [1.55, 1.05, 0.42], styrke: sen ? 0.55 : 0.6 }   // oker og rust; seint på høsten brunere
        : { navn: a, farge: [1, 1, 1], styrke: 0 };
}

// skydekke i bildet: litt skyer gir fortsatt sol og skygger; først over ~45 % dempes sola, og helt overskyet er introens gråvær
const skyFor = v => (v.nedbor || v.taake) ? Math.max(0.85, v.sky) : Math.min(1, Math.max(0, (v.sky - 0.45) / 0.5)) * 0.9;
const snoFor = (v, aar) => { const t = +Q0.get('sno'); if (!isNaN(t) && Q0.get('sno') !== null) return t;
  if (v.nedbor === 'sno') return 0.85; if (v.nedbor === 'sludd') return 0.3; if (aar.navn === 'vinter' && v.temp != null && v.temp <= -1) return 0.6; return 0; };

const VAER = { naa: null, kilde: null, mal: { sky: 0, sno: 0 }, tid: 0, feil: null };
async function hent(){
  const fast = Q0.get('vaer');
  if (fast && FAST[fast]) { VAER.kilde = 'fast'; return FAST[fast](); }
  const lagret = (() => { try { const x = JSON.parse(sessionStorage.getItem('vaer') || 'null'); return x && Date.now() - x.t < 15 * 60e3 ? x.v : null; } catch (_) { return null; } })();
  if (lagret) { VAER.kilde = 'met'; return lagret; }
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 6000);
  try {
    const r = await fetch(`https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=${PUNKT.lat}&lon=${PUNKT.lon}`, { signal: ctl.signal });
    if (!r.ok) throw new Error('MET ' + r.status);
    const j = await r.json(); const ts = j.properties.timeseries;
    const naa = Date.now(); const p = ts.reduce((b, x) => Math.abs(new Date(x.time) - naa) < Math.abs(new Date(b.time) - naa) ? x : b, ts[0]);
    const d = p.data.instant.details, n1 = p.data.next_1_hours || p.data.next_6_hours || {};
    const v = fraSymbol(n1.summary && n1.summary.symbol_code, d.cloud_area_fraction, n1.details && n1.details.precipitation_amount, d.air_temperature);
    v.symbol = n1.summary && n1.summary.symbol_code; v.vind = d.wind_speed; v.vindFra = d.wind_from_direction; v.tid = p.time;
    try { sessionStorage.setItem('vaer', JSON.stringify({ t: Date.now(), v })); } catch (_) { /* privat vindu */ }
    VAER.kilde = 'met'; return v;
  } catch (e) { VAER.feil = String(e.message || e); return null; } finally { clearTimeout(t); }
}

// overgangen: verdiene glir mot målet på ~2 s, så været aldri popper inn
let glir = false;
function glid(){
  const m = VAER.mal, k = 0.06; let igjen = false;
  for (const [u, mal] of [[U_SOL.sky, m.sky], [U_SOL.sno, m.sno]]) { const d = mal - u.value; if (Math.abs(d) > 0.003) { u.value += d * k; igjen = true; } else u.value = mal; }
  TILSTAND.skyggeSkitten = true; map.triggerRepaint();
  if (igjen) requestAnimationFrame(glid); else glir = false;
}
function settVaer(v){
  const aar = aarstidFor(new Date()); VAER.aarstid = aar.navn;
  U_SOL.aarstid.value.set(aar.farge[0], aar.farge[1], aar.farge[2], aar.styrke);
  VAER.naa = v;
  VAER.mal = v ? { sky: skyFor(v), sno: snoFor(v, aar) } : { sky: 0, sno: snoFor({}, aar) };
  nedbor.sett(v); taake.style.opacity = v ? String(v.taake) : '0'; merke(v);
  if (!glir) { glir = true; requestAnimationFrame(glid); }
}

// ---- nedbør: eget lerret over kartet (striper for regn, fnugg for snø); tegnes bare når det faller noe ----
const nedbor = (() => {
  const c = document.createElement('canvas'); c.id = 'nedbor'; c.setAttribute('aria-hidden', 'true'); document.body.appendChild(c);
  const g = c.getContext('2d'); let type = null, n = 0, deler = [], kjorer = false, vind = 0;
  const str = () => { const d = Math.min(devicePixelRatio, 2); c.width = innerWidth * d; c.height = innerHeight * d; g.setTransform(d, 0, 0, d, 0, 0); };
  addEventListener('resize', str); str();
  const ny = (tilfeldigY) => ({ x: Math.random() * (innerWidth + 200) - 100, y: tilfeldigY ? Math.random() * innerHeight : -20, v: type === 'sno' ? 0.6 + Math.random() * 0.9 : 9 + Math.random() * 6, r: type === 'sno' ? 1.4 + Math.random() * 2.6 : 0, f: Math.random() * 6.28 });
  function steg(){
    if (!type || document.hidden) { kjorer = false; g.clearRect(0, 0, innerWidth, innerHeight); return; }
    g.clearRect(0, 0, innerWidth, innerHeight);
    if (type === 'sno') { g.fillStyle = 'rgba(255,255,255,.88)'; g.beginPath(); for (const p of deler) { p.f += 0.02; p.y += p.v; p.x += Math.sin(p.f) * 0.5 + vind * 0.3; g.moveTo(p.x + p.r, p.y); g.arc(p.x, p.y, p.r, 0, 6.283); if (p.y > innerHeight + 10) Object.assign(p, ny(false)); } g.fill(); }
    else { g.strokeStyle = type === 'sludd' ? 'rgba(235,240,248,.55)' : 'rgba(60,82,118,.5)'; g.lineWidth = 1.3; g.beginPath(); for (const p of deler) { p.y += p.v; p.x += vind; g.moveTo(p.x, p.y); g.lineTo(p.x - vind * 1.6, p.y - p.v * 2.4); if (p.y > innerHeight + 20) Object.assign(p, ny(false)); } g.stroke(); }
    requestAnimationFrame(steg);
  }
  return {
    sett(v){ type = v && v.nedbor ? v.nedbor : null; if (!type) { deler = []; return; }
      vind = v.vind ? Math.max(-3, Math.min(3, (v.vind / 4) * Math.sin(((v.vindFra || 0) + 180) * Math.PI / 180))) : 0.8;
      const tett = Math.min(1, 0.25 + (v.mengde || 1) / 3); n = Math.round((type === 'sno' ? 260 : 420) * tett * Math.min(1.6, Math.max(0.8, innerWidth * innerHeight / 1.2e6)));
      deler = Array.from({ length: n }, () => ny(true)); if (!kjorer) { kjorer = true; requestAnimationFrame(steg); } },
    info: () => ({ type, n: deler.length }),
  };
})();
const taake = document.createElement('div'); taake.id = 'taake'; taake.setAttribute('aria-hidden', 'true'); document.body.appendChild(taake);

// ---- merket oppe til venstre: temperatur og vær nå, med kilden. Trykk åpner valget (vær nå eller et fast vær, til visning) ----
const IKON = {
  sol: '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
  sky: '<path d="M7 18h10.5a4 4 0 0 0 .4-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 7 18z"/>',
  regn: '<path d="M7 14h10.5a4 4 0 0 0 .4-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 7 14z"/><path d="M8.5 17l-1 3M12.5 17l-1 3M16.5 17l-1 3"/>',
  sno: '<path d="M7 14h10.5a4 4 0 0 0 .4-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 7 14z"/><path d="M8.5 18.5h.01M12 20h.01M15.5 18.5h.01"/>',
  taake: '<path d="M4 9h16M3 13h18M5 17h14"/>',
};
const ikonFor = n => n === 'sol' || n === 'lettskyet' ? 'sol' : n === 'regn' || n === 'sludd' || n === 'torden' ? 'regn' : n === 'sno' ? 'sno' : n === 'taake' ? 'taake' : 'sky';
const merkeEl = document.createElement('button'); merkeEl.id = 'vaer'; merkeEl.type = 'button'; merkeEl.setAttribute('aria-haspopup', 'true'); merkeEl.hidden = true;
const valgEl = document.createElement('div'); valgEl.id = 'vaervalg'; valgEl.setAttribute('role', 'menu'); valgEl.hidden = true;
valgEl.innerHTML = `<p class="t">Vis kartet med</p>` + [['naa', 'Været nå'], ['sol', 'Sol'], ['skyet', 'Skyet'], ['regn', 'Regn'], ['sno', 'Snø'], ['taake', 'Tåke']]
  .map(([k, t]) => `<button type="button" role="menuitemradio" data-v="${k}">${t}</button>`).join('') + `<p class="kilde">Værdata: <a href="https://www.met.no/" target="_blank" rel="noopener">MET Norway</a></p>`;
document.body.append(merkeEl, valgEl);
let valgt = Q0.get('vaer') && FAST[Q0.get('vaer')] ? Q0.get('vaer') : 'naa', metNaa = null;
function merke(v){
  if (!v) { merkeEl.hidden = true; return; }
  merkeEl.hidden = false;
  const t = v.temp != null && valgt === 'naa' ? `${Math.round(v.temp)}°` : '';
  merkeEl.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${IKON[ikonFor(v.navn)]}</svg><span>${t ? `<b>${t}</b> ` : ''}${NAVN[v.navn] || ''}</span>`;
  merkeEl.setAttribute('aria-label', `Været i Gamlebyen: ${t} ${NAVN[v.navn] || ''}${valgt === 'naa' ? '' : ' (valgt visning)'}. Velg vær.`);
  valgEl.querySelectorAll('[data-v]').forEach(b => b.setAttribute('aria-checked', String(b.dataset.v === valgt)));
}
merkeEl.addEventListener('click', e => { e.stopPropagation(); valgEl.hidden = !valgEl.hidden; merkeEl.setAttribute('aria-expanded', String(!valgEl.hidden)); });
addEventListener('pointerdown', e => { if (!valgEl.hidden && !valgEl.contains(e.target) && e.target !== merkeEl && !merkeEl.contains(e.target)) valgEl.hidden = true; });
valgEl.addEventListener('click', e => { const b = e.target.closest('[data-v]'); if (!b) return; valgt = b.dataset.v; valgEl.hidden = true;
  if (valgt === 'naa') settVaer(metNaa); else { const v = FAST[valgt](); if (metNaa && metNaa.temp != null) v.temp = metNaa.temp; settVaer(v); } });

async function oppdater(){ const v = await hent(); if (VAER.kilde === 'met') metNaa = v; if (valgt === 'naa' || !metNaa) settVaer(valgt === 'naa' ? v : FAST[valgt]()); VAER.tid = Date.now(); }
if (!VAER_AV) { oppdater(); setInterval(() => { if (!document.hidden && Q0.get('vaer') === null) { try { sessionStorage.removeItem('vaer'); } catch (_) { /* */ } oppdater(); } }, 15 * 60e3); }
else settVaer(null);
document.addEventListener('visibilitychange', () => { if (!document.hidden && VAER.naa && VAER.naa.nedbor) nedbor.sett(VAER.naa); });

window.__vaer = () => ({ naa: VAER.naa, kilde: VAER.kilde, feil: VAER.feil, aarstid: VAER.aarstid, sky: U_SOL.sky.value, sno: U_SOL.sno.value, mal: VAER.mal, nedbor: nedbor.info(), valgt });
export { VAER, settVaer, aarstidFor, fraSymbol };
