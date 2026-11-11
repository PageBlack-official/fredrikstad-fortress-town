import * as maplibregl from 'maplibre-gl';
import { DATA, Q0, map, tilLngLat, zoomFor } from './00_oppsett.js';
import { TILSTAND } from './tilstand.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { velgHus } from './16_interaksjon.js';
import { glidKamera } from './15_bevegelse.js';
import { velgSted } from './24_sok.js';
// ---- gjesteversjonen: et hotell (eller en annen partner) får kartet som sitt eget, i én lenke: ?gjest=<id> ----
// data/partnere.json: navn, bygget de holder til i, aksentfarge og anbefalte steder (id-er i data/steder.json). Lenka åpner kartet med
// partnerens navn oppe til venstre. Når introen er ferdig, sentreres kartet på partnerens bygg, og et eget merke blir stående på det, så det
// er tydelig hvor hotellet er uten at bygget utgir seg for å være åpent (Hotell Kasernen åpner 2027). Anbefalingene blir en egen kategori
// øverst i Finn (lagt inn i 24_sok). Gangtidene fra hotellet regnes i gange.js. Uten ?gjest er kartet som før.
const P = (DATA.partnere || []).find(p => p.id === Q0.get('gjest'));
if (P) {
  document.documentElement.style.setProperty('--gjest', P.farge || '#2b2420');
  document.documentElement.classList.add('gjest');
  const merke = document.createElement('div'); merke.id = 'gjestemerke'; merke.textContent = P.navn;
  (document.getElementById('topp') || document.body).prepend(merke);

  const bygg = (DATA.bygg || []).find(b => b.id === P.bygg_id);
  const hus = () => buildings.find(g => g.userData.b && g.userData.b.id === P.bygg_id);
  const sted = (DATA.steder && DATA.steder.steder || []).find(s => s.bygg_id === P.bygg_id && s.kategori === 'sove');
  // midtpunktet til bygget (samme som gange.js regner gangtidene fra)
  let cx = 0, cy = 0; if (bygg && bygg.p && bygg.p.length) { for (const [x, y] of bygg.p) { cx += x; cy += y; } cx /= bygg.p.length; cy /= bygg.p.length; }

  // det stående merket på hotellet: en nål i aksentfargen med et hus-tegn og navnet, så gjesten alltid ser hvor hotellet er.
  // Ingen logo eller profil (den eies av andre) – bare navnet og at det åpner i 2027.
  function hotellNaal(){
    if (!bygg) return;
    const el = document.createElement('button'); el.type = 'button'; el.className = 'gjest-naal';
    el.setAttribute('aria-label', `${P.navn} – åpner 2027`); el.title = P.navn;
    el.innerHTML = `<span class="hode"><svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18V7M3 13h18v5M21 13a3 3 0 0 0-3-3h-7v3M7 11.5h.01"/></svg></span><span class="flagg"><b>${P.navn}</b><i>åpner 2027</i></span>`;
    el.addEventListener('click', e => { e.stopPropagation(); if (sted) velgSted(sted); else { const g = hus(); if (g) velgHus(g); } });
    new maplibregl.Marker({ element: el, anchor: 'bottom' }).setLngLat(tilLngLat(cx, cy)).addTo(map);
  }

  // åpningen: når introen er ferdig og bygget finnes, sentrer kartet på hotellet og sett merket.
  // Har lenka alt et hus= (delt utsikt), rører vi ikke kameraet – da vant lenka.
  let satt = false;
  const vent = () => {
    if (!(TILSTAND.introDone && hus())) { requestAnimationFrame(vent); return; }
    if (satt) return; satt = true; hotellNaal();
    if (bygg && !location.hash.includes('hus=')) setTimeout(() => glidKamera({ center: tilLngLat(cx, cy), zoom: Math.max(map.getZoom(), zoomFor(2.0)), offset: [0, 0] }, 'hjem'), 400);
  };
  requestAnimationFrame(vent);
}
window.__gjest = () => P ? { id: P.id, navn: P.navn } : null;
