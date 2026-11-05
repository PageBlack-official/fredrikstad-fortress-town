import { DATA, Q0 } from './00_oppsett.js';
import { TILSTAND } from './tilstand.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { velgHus } from './16_interaksjon.js';
// ---- gjesteversjonen: et hotell (eller en annen partner) får kartet som sitt eget, i én lenke: ?gjest=<id> ----
// data/partnere.json: navn, bygget de holder til i, aksentfarge og anbefalte steder (id-er i data/steder.json). Lenka åpner kartet med
// partnerens navn oppe til venstre, og når introen er ferdig, løftes partnerens bygg og kortet åpnes. Anbefalingene blir en egen kategori
// øverst i Finn (lagt inn i 24_sok, som bygger søket). Uten ?gjest er kartet som før.
const P = (DATA.partnere || []).find(p => p.id === Q0.get('gjest'));
if (P) {
  document.documentElement.style.setProperty('--gjest', P.farge || '#2b2420');
  document.documentElement.classList.add('gjest');
  const merke = document.createElement('div'); merke.id = 'gjestemerke'; merke.textContent = P.navn;
  (document.getElementById('topp') || document.body).prepend(merke);
  const hus = () => buildings.find(g => g.userData.b && g.userData.b.id === P.bygg_id);
  const vent = () => { if (TILSTAND.introDone && hus()) setTimeout(() => velgHus(hus()), 400); else requestAnimationFrame(vent); };
  if (P.bygg_id && !location.hash.includes('hus=')) requestAnimationFrame(vent);
}
window.__gjest = () => P ? { id: P.id, navn: P.navn } : null;
