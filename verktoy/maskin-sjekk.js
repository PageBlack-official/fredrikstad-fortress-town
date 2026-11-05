// Maskinsjekken (regel «kvaliteten holder i fart», 05.11): kjøres i Vegars egen Chrome på /prove/ (Claude in Chrome: javascript_tool med
// innholdet i denne fila). Svaret lagres som rapport/maskin.json; publiser.sh forside nekter uten grønn sjekk mot samme kilde.
// Hvorfor i hans Chrome: testene i containeren tegner med programvare, og feilen 05.11 (kvaliteten falt ved første bevegelse) var
// usynlig der. Bare et ekte skjermkort viser den.
(async () => {
  const feil = [];
  const vent = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 60 && !(window.__klar && window.__klar()); i++) await vent(500);
  if (!window.__klar || !window.__klar()) feil.push('kartet ble ikke klart på 30 s');
  const kilde = (document.querySelector('meta[name=kilde]') || {}).content || 'ukjent';
  const gpu = (() => { try { const g = document.createElement('canvas').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info'); return g.getParameter(e.UNMASKED_RENDERER_WEBGL); } catch (_) { return 'ukjent'; } })();
  const c = document.querySelector('.maplibregl-canvas') || document.querySelector('canvas');
  const for_ = window.__kval();
  // to rotasjoner à 4 s, med bildetid målt mellom bildene
  const tider = []; let sist = performance.now(), maal = true;
  const f = () => { const n = performance.now(); tider.push(n - sist); sist = n; if (maal) requestAnimationFrame(f); }; requestAnimationFrame(f);
  for (const d of [60, -60]) { window.map.easeTo({ bearing: window.map.getBearing() + d, duration: 4000 }); await vent(4600); }
  maal = false; await vent(1500);
  const etter = window.__kval();
  tider.sort((a, b) => a - b); const median = tider[Math.floor(tider.length / 2)] || 0;
  for (const k of ['skala', 'ss', 'ao']) if (etter[k] !== for_[k]) feil.push(`${k} endret seg fra ${for_[k]} til ${etter[k]} etter bevegelse`);
  if (etter.perfNivaa !== 0) feil.push(`kvalitetstrinn ${etter.perfNivaa}, skal være 0`);
  if (etter.ss < 4) feil.push(`streken tegnes med ${etter.ss} prøver, skal være 4`);
  const pix = c.width * c.height, skalaForventet = Math.min(1, Math.sqrt(11e6 / pix));
  if (etter.skala < Math.max(0.5, skalaForventet) - 0.02) feil.push(`oppløsning ${etter.skala}, skjermen gir ${skalaForventet.toFixed(2)}`);
  const svar = { kilde, ok: feil.length === 0, feil, gpu, lerret: `${c.width}x${c.height}`, dpr: devicePixelRatio, for: for_, etter, ms_per_bilde: +median.toFixed(1), bilder: tider.length, tid: new Date().toISOString(), adresse: location.href.split('#')[0] };
  window.__maskinsjekk = svar; return JSON.stringify(svar);
})();
