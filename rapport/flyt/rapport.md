# Overganger og flyt: brudd funnet og rettet (29.10.2026, grenen natt/flyt)

Målt med verktoy/flyt-test.mjs (falsk klokke, 16 ms per bilde, ?tegn=0) på bygget fra natt/grunnmur-fkb (før: maaling-for.json)
og på denne grenen (etter: maaling.json, regel 22 grønn). Bevegelse per bilde = hvor langt bakken under ni faste skjermpunkter flytter seg.

| # | Brudd funnet | Før | Etter | Status |
|---|---|---|---|---|
| 1 | Avbrutt intro: miniatyr-uskarpheten forsvant på ett bilde | sprang 1,0 i ett bilde | største endring 0,058 per bilde, toner ut på 0,8 s | rettet (15_loop: tiltOppdater) |
| 2 | Etter avbrutt intro tegnet kartet 10 bilder/s mens lys og uskarphet ble hentet inn (trapper) | samme verdi i 8 bilder, så sprang | full fart til ferdig | rettet (puls) |
| 3 | Dobbelttrykk på mobil gjorde ingenting (MapLibres dobbelttrykk var slått av sammen med dobbeltklikket; vår zoom lyttet bare på dblclick) | zoom +0 | zoom +1, punktet glipper 0,3 px | rettet (egen gjenkjenning fra klikkene) |
| 4 | Klikk/trykk på hus ventet 300 ms før noe skjedde | start etter 304 ms (mobil) | start 0 ms | rettet (huset velges med en gang; bare «lukk ved trykk utenfor» venter på et mulig dobbeltklikk) |
| 5 | Dra og slipp: tregheten tok med 0,3 av fingerfarten, og første bilde etter slipp stod stille | første bilde etter slipp 0 (så 0,3) | 0,97 | rettet (egen treghet, 15_bevegelse) |
| 5b | Klyp og vri: tregheten tok med 0,3 av farten (kan ikke stilles i MapLibre), ett bilde stod stille | 0 | klyp 0,97, vri 0,97 | rettet (egen treghet) |
| 5c | Musehjul: ett utslag per hakk | rykk 1,0 | rykk 0,27, punktet står (0 px) | rettet (egen hjulzoom med fjær) |
| 5d | Speilet i vannet tonet ut ved hver bevegelse og inn igjen 0,3 s etter stopp | styrke 0 i fart | full styrke i fart, speilet aldri eldre enn 100 ms | rettet (14, 03, 15_loop) |
| 6 | Kortet på desktop lå nederst på midten over byen; kameraet glir ikke inn til huset | kort 416 px bredt nederst, ingen kamerabevegelse | sidepanel fra venstre, huset glir inn midt i den frie flaten (zoom +0,88 fra hjem) | rettet |
| 7 | Mobil: kortet kunne ikke dras ned | følger ikke fingeren | følger fingeren (126 px), lukkes med farten den slippes med | rettet (bunnark) |
| 8 | Tilbake speilet ikke inngangen: × og trykk utenfor lukket kortet uten å flytte kameraet tilbake, Esc gikk rett hjem | – | ×, Esc og trykk utenfor glir tilbake dit kameraet stod (0 px avvik), Esc lukker kortet først | rettet |
| 9 | Nettleserens/Androids tilbake forlot siden når kortet var åpent | ingen historikk | lukker kortet | rettet (history.pushState) |
| 10 | Kortet: samme tid og kurve inn og ut (450 ms) | 450/450 ms | inn 380 ms bremser, ut 240 ms akselererer (Material) | rettet |
| 11 | Bytte av hus i åpent kort byttet teksten på ett bilde | popp | innholdet toner over (180 ms), kortet står | rettet |
| 12 | «Reduser bevegelse»: kartvalget `respectPrefersReducedMotion:false` finnes ikke i MapLibre 6, så Vegars valg (v27: kartet skal bevege seg selv med «Reduser bevegelse» på Mac) gjaldt ikke | kortet gled, kameraflytt 0 ms (lest i MapLibres easeTo) | `reduceMotion:false`; kort og kamera glir (målt: dobbeltklikk 800 ms med redusert bevegelse) | rettet |
| 13 | Knappene +/− og kompasset brukte MapLibres egne tider og kurve | 500/1000 ms, annen kurve | 420 ms myk / 900 ms glid fra BEV | rettet |
| 14 | Varighet og kurver spredt i koden og CSS | tall i 16_interaksjon og stil.css | én modul (15_bevegelse.js, BEV), CSS-variabler | rettet |

Ikke brudd (målt, i orden før og etter): dobbeltklikk zoomer mot punktet (0,2 px), hjem 1,3 s uten hopp, hjem-glidningen avbrytes av et dra
(MapLibre stopper animasjonen ved hver gest), klyp zoomer rundt fingrene (0 px), musehjul holder punktet under pekeren (0 px), introen selv
(ikke endret).

Ikke rettet:
- Styreflate (to fingre flytter) går utenom MapLibre (panBy uten animasjon) og følger fingrene; tregheten der er macOS sin. Ikke målt her.
- Speilet: når kartet stopper, tegnes det på nytt med riktig parallakse; forskjellen fra det flyttede speilet er høyst 110 ms bevegelse
  gammel og bør ikke synes, men det er ikke sett i ekte Chrome.

Må sjekkes i ekte Chrome og på telefon (programvare-GPU-en her kan ikke vise fart): bildefrekvens under glidning til hus og under dra av
bunnarket (tast d / ?d=1), at bunnarket føles riktig under fingeren på iPhone (Safari) og Android, Android-tilbake, og at sidepanelet ikke
dekker noe viktig på 13-tommers skjerm.

Kontrollbilder: verktoy/kort-bilder.mjs (desktop: sidepanel med kirka midt i den frie flaten, sett 29.10).
