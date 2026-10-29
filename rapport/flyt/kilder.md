# Flyt og overganger: hva kildene sier (29.10.2026, oppdrag 13 og 15)

Kort notat med det som er lagt til grunn for src/15_bevegelse.js, huskortet i src/16_interaksjon.js og verktoy/flyt-test.mjs.

## MapLibre GL JS 6.14 (kartmotoren vår)
Lest i kildekoden til den versjonen kartet laster (cdn.jsdelivr.net/npm/maplibre-gl@6.14.0/dist/maplibre-gl-dev.mjs) og i API-dokumentasjonen.
- Alle animerte flytt (easeTo, flyTo, panBy, zoomIn …) kan avbrytes: hver gest kaller `camera.stop(true)` før den flytter kartet
  (handler_manager `_updateMapTransform`), og en ny easeTo starter fra der kameraet er. Vi trenger altså ingen egen avbrytingskode, bare
  å bruke kartets animasjoner, ikke egne rAF-løkker.
- easeTo `around`: punktet står fast på skjermen under zoom (MapLibres egen dobbeltklikk-zoom gjør det samme, 300 ms). `offset`: målet
  havner så mange piksler fra midten (brukes for å legge huset midt i den delen kortet ikke dekker). `padding` blir værende på kartet etter
  animasjonen og flytter forsvinningspunktet: https://maplibre.org/maplibre-gl-js/docs/examples/offset-vanishing-point-with-padding/ ,
  derfor offset, ikke padding.
- `essential: true` gjør at en animasjon kjøres selv med «redusert bevegelse»; ellers settes varigheten til 0. Kartvalget som slår av
  dette, heter `reduceMotion` i 6.x (https://maplibre.org/maplibre-gl-js/docs/API/type-aliases/AnimationOptions/). Kartet vårt hadde
  `respectPrefersReducedMotion:false`, som ikke finnes i 6.14 og ble ignorert.
- Treghet etter dra (handler_inertia): farten måles over de siste 60 ms, glir ut med bezier(0,0,.3,1), flytt maks 1400 px/s, lineæritet 0,3.
  Klyp zoomer rundt midtpunktet mellom fingrene (`pinchAround`), to fingre vrir og vipper (TwoFingersTouch…).
- Musehjul: `setWheelZoomRate` (standard 1/450; vi har 1/150), styreflate-klyp kommer som ctrl+hjul (1/100).
- `maplibregl.setNow()` og Playwrights `page.clock` gir deterministisk tid: brukt i flyt-test.

## Apple: «Designing Fluid Interfaces» (WWDC 2018, https://developer.apple.com/videos/play/wwdc2018/803/)
- Svar på berøring med en gang; let etter forsinkelser overalt (tap, trykk). Grunnen til at et klikk på et hus nå velger det med en gang
  (før ventet vi 300 ms på et mulig dobbeltklikk).
- Alt skal kunne avbrytes og omdirigeres midt i en bevegelse.
- Ta med farten fra fingeren: bruk historikken, ikke bare siste punkt, og prosjiser endepunktet (posisjon + fart · tid) før du bestemmer
  om noe lukkes eller går tilbake. Fjær uten oversving (100 % demping) som utgangspunkt. Brukt i bunnarket.

## Apple HIG, kart og stedskort (https://developer.apple.com/design/human-interface-guidelines/maps)
- Stedskort som ark fra bunnen på iPhone, som sidepanel/popover på iPad og Mac. Hold det valgte stedet synlig mens kortet vises.
  Marker det valgte tydelig (huset løfter seg hos oss).

## Material 3, varighet og kurver (https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md)
- Varighet vokser med hvor langt noe beveger seg (50–1000 ms i trinn). Inn: «emphasized decelerate» cubic-bezier(.05,.7,.1,1);
  ut: «emphasized accelerate» cubic-bezier(.3,0,.8,.15); flytt innenfor bildet: «standard» cubic-bezier(.2,0,0,1).
  Kortet: inn 380 ms, ut 240 ms. (m3.material.io gir ikke tekst uten JavaScript; tallene er fra Material-bibliotekets egen dokumentasjon.)

## Redusert bevegelse (https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- Brukeren ber om at bevegelse fjernes, dempes eller byttes ut; skalering og panorering av store flater er det som utløser ubehag.
  Eksempelet bytter bevegelse med en toning. Hos oss: kortet toner i stedet for å gli. Kameraet glir fortsatt (Vegars valg, se rapporten).

## UI-overganger: FLIP og View Transitions
- FLIP (First, Last, Invert, Play; https://thomaswilburn.github.io/viz-book/perf-flip.html): mål før og etter, animer bare transform og
  opacity, så nettleseren slipper ny layout per bilde. Kortet animeres bare med transform/opacity; bytte av hus i åpent kort toner innholdet.
- View Transition API (https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API): øyeblikksbilde av før og etter,
  `document.startViewTransition`. Ikke brukt: kortet er ett element som glir, og WebGL-lerretet skal aldri fryses i et øyeblikksbilde.

## 60 bilder/s
- 16,7 ms per bilde; kartet bruker selv det meste (3D, skygger, strek). UI-overganger skal derfor være transform/opacity (komponeres på GPU,
  ingen layout), målinger av layout (offsetTop o.l.) bare én gang ved åpning, og ingen egen rAF ved siden av kartets.

## Sider som ikke kunne leses (tilgang ble ikke gitt i tide)
- https://web.dev/articles/animations-guide , https://aerotwist.com/blog/flip-your-animations/ og m3.material.io (JavaScript-side).
  Innholdet er dekket av kildene over.
