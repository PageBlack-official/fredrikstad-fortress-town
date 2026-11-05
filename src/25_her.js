import * as maplibregl from 'maplibre-gl';
import { map, tilModell, zoomFor } from './00_oppsett.js';
import { BEV, glidKamera } from './15_bevegelse.js';
// ---- «Du er her»: en prikk der du står, når du står i Gamlebyen. Knappen ligger med pluss og minus nede til høyre. ----
// Posisjonen brukes bare i nettleseren (geolocation), sendes ingen steder og lagres ikke. Er du mer enn RADIUS fra midten av byen,
// sier kartet hvor langt unna du er i stedet for å fly ut av kartet.
const RADIUS = 1400;   // meter fra modellens midte (Torvet): Gamlebyen, Isegran, Cicignon og ferjekaiene
let vakt = null, prikk = null, forste = true;
const melding = (() => { const el = document.createElement('div'); el.id = 'melding'; el.setAttribute('role', 'status'); document.body.appendChild(el); let t = null;
  return tekst => { el.textContent = tekst; el.classList.add('vis'); clearTimeout(t); t = setTimeout(() => el.classList.remove('vis'), 4200); }; })();

class HerKnapp {
  onAdd(){
    const c = this.c = document.createElement('div'); c.className = 'maplibregl-ctrl maplibregl-ctrl-group';
    const b = this.b = document.createElement('button'); b.type = 'button'; b.className = 'her-knapp'; b.setAttribute('aria-label', 'Vis hvor jeg er'); b.title = 'Vis hvor jeg er';
    b.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3"/><circle cx="12" cy="12" r="7"/></svg>';
    b.addEventListener('click', () => vakt === null ? start() : stopp());
    c.appendChild(b); return c;
  }
  onRemove(){ this.c.remove(); }
}
const knapp = new HerKnapp(); map.addControl(knapp, 'bottom-right');

function start(){
  if (!('geolocation' in navigator)) { melding('Nettleseren kan ikke vise hvor du er.'); return; }
  knapp.b.classList.add('leter'); forste = true;
  vakt = navigator.geolocation.watchPosition(pos => {
    knapp.b.classList.remove('leter'); knapp.b.classList.add('paa'); knapp.b.setAttribute('aria-pressed', 'true');
    const ll = [pos.coords.longitude, pos.coords.latitude], [x, y] = tilModell(ll), avstand = Math.hypot(x - 20, y - 50);
    if (avstand > RADIUS) {
      if (forste) melding(avstand > 20000 ? `Du er ${Math.round(avstand / 1000)} km fra Gamlebyen.` : `Du er ${(avstand / 1000).toFixed(1).replace('.', ',')} km fra Gamlebyen.`);
      if (prikk) { prikk.remove(); prikk = null; } forste = false; return;
    }
    if (!prikk) { const el = document.createElement('div'); el.className = 'her-prikk'; el.setAttribute('aria-label', 'Du er her'); prikk = new maplibregl.Marker({ element: el }).setLngLat(ll).addTo(map); }
    else prikk.setLngLat(ll);
    if (forste) { glidKamera({ center: ll, zoom: Math.max(map.getZoom(), zoomFor(BEV.husZoom)), offset: [0, 0] }, 'hus'); forste = false; }
  }, err => { stopp(); melding(err.code === 1 ? 'Du har ikke gitt kartet lov til å se hvor du er.' : 'Fant ikke hvor du er akkurat nå.'); },
  { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 });
}
function stopp(){ if (vakt !== null) navigator.geolocation.clearWatch(vakt); vakt = null; if (prikk) { prikk.remove(); prikk = null; }
  knapp.b.classList.remove('paa', 'leter'); knapp.b.setAttribute('aria-pressed', 'false'); }

export { melding };
