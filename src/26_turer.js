import { DATA } from './00_oppsett.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { BYGG_ID, kort, kortInnhold, kort_, velgHus, velgPunkt } from './16_interaksjon.js';
// ---- turer: kameraet tar deg fra stopp til stopp, kortet forteller (Vegar: «turer med kamerabaner») ----
// Turene står i data/turer.json som lister med numrene fra kartbrosjyren (data/legende.json). Teksten på hvert stopp er brosjyrens egen
// (Visit Fredrikstad 2015, lagt inn på bygget som «tekst»), ikke skrevet på nytt. Stopp uten tekst viser navnet og plassen.
// Startes fra søket (Finn → Turer). Piltastene og knappene i kortet blar; Lukk avslutter. Velger du et annet hus selv, avsluttes turen.
const TURER = DATA.turer || [];
const LEGENDE = new Map((DATA.legende || []).map(l => [l.nr, l]));
let tur = null, i = 0, egen = false;

function stoppData(nr){
  const l = LEGENDE.get(nr); if (!l) return null;
  const b = l.bygg_id && BYGG_ID.get(l.bygg_id);
  return { nr, navn: l.navn, tekst: (b && b.tekst) || '', bygg_id: l.bygg_id, x: l.xy[0], y: l.xy[1] };
}
function fyll(s){
  kort.querySelector('h2').textContent = s.navn;
  kort.querySelector('.a').textContent = `${tur.navn} · stopp ${i + 1} av ${tur.stopp.length}`;
  kort.querySelector('.b').textContent = s.tekst;
  kort.querySelector('.her').innerHTML = ''; kort.querySelector('.ogsa').innerHTML = ''; kort.querySelector('.ogsa-t').textContent = '';
  kort.querySelector('.farge').innerHTML = ''; kort.querySelector('.id').textContent = s.tekst ? 'Tekst: kartbrosjyren til Visit Fredrikstad (2015)' : '';
  let f = kort.querySelector('.tur');
  if (!f) { f = document.createElement('div'); f.className = 'tur'; f.innerHTML = '<button type="button" class="forrige" aria-label="Forrige stopp">‹</button><span class="teller" aria-live="polite"></span><button type="button" class="neste" aria-label="Neste stopp">›</button>';
    kortInnhold.after(f); f.querySelector('.forrige').onclick = () => gaa(-1); f.querySelector('.neste').onclick = () => gaa(1); }
  f.hidden = false; f.querySelector('.teller').textContent = `${i + 1} / ${tur.stopp.length}`;
  f.querySelector('.forrige').disabled = i === 0; f.querySelector('.neste').disabled = i === tur.stopp.length - 1;
}
function vis(){
  const s = stoppData(tur.stopp[i]); if (!s) return gaa(1);
  const g = s.bygg_id && buildings.find(x => x.userData.b && x.userData.b.id === s.bygg_id);
  egen = true;
  if (g) { velgHus(g); fyll(s); } else velgPunkt(() => fyll(s), s.x, s.y);
  egen = false; kort_.tur = tur.id;
}
function gaa(d){ if (!tur) return; const n = i + d; if (n < 0 || n >= tur.stopp.length) return; i = n; vis(); }
function start(id){ tur = TURER.find(t => t.id === id); if (!tur) return false; i = 0; vis(); return true; }
function slutt(){ if (!tur) return; tur = null; kort_.tur = null; const f = kort.querySelector('.tur'); if (f) f.hidden = true; }
kort_.vedLukk.push(slutt);
kort_.vedVelg.push(() => { if (!egen) slutt(); });
addEventListener('keydown', e => { if (!tur || e.target.closest('input,textarea')) return; if (e.key === 'ArrowRight') { e.preventDefault(); gaa(1); } if (e.key === 'ArrowLeft') { e.preventDefault(); gaa(-1); } });

// i søkepanelet: turene som egne valg over kategoriene
const panel = document.getElementById('sokpanel');
if (panel && TURER.length) {
  const rad = document.createElement('div'); rad.className = 'turer'; rad.setAttribute('role', 'group'); rad.setAttribute('aria-label', 'Turer');
  rad.innerHTML = '<p class="t">Turer</p>' + TURER.map(t => `<button type="button" data-tur="${t.id}"><b>${t.navn}</b><small>${t.om}</small></button>`).join('');
  panel.querySelector('.kat').before(rad);
  rad.addEventListener('click', e => { const b = e.target.closest('[data-tur]'); if (!b) return; panel.hidden = true; start(b.dataset.tur); });
}
window.__tur = { start, gaa, slutt, naa: () => tur && { id: tur.id, i } };
export { start as startTur };
