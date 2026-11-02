# Flyt uten lavere oppløsning (02.11.2026, natt/flyt3)

Vegar 02.11 kl. 00.18: «ikke dårligere oppløsning, heller motsatt, og vise at vår løsning er råere».
Utgangspunkt: allemannsdata.com/examples/montreal_kart føles glattere. Den bruker MapLibres egne klosser (ingen tak, vinduer eller
skygger), pixelRatio maks 1,5, antialias av, og tegner nesten ingenting når kartet står i ro. Vi har tak, vinduer, kastskygger (PCF),
hjørneskygge (AO), blekkstrek, speil i vannet og pixelRatio opptil 2.

Oppløsning, skygger, AO, strek og speil er urørt. Kamerabevegelsene (15_bevegelse) er urørt. Det som er gjort, er å slutte å gjøre
arbeid som ikke synes.

## Hva som er endret

| Endring | Fil | Hvorfor |
|---|---|---|
| Bakkeflatene slått sammen per materiale og plass: 651 nett blir 17 | src/21_flyt.js | Hvert polygon (plen, flate, parkering, vann, brostein) var et eget tegnekall, i 3D-passet og i speilet. Tegnekall koster CPU i three.js, og CPU er det som henger på Vegars Intel-iMac. |
| Vann i bildet (`vannISyne()`): rutenett på 8 m over vannflatene, 33 x 21 skjermpunkter lagt ned på vannet, regnet bare når kameraet har flyttet seg | src/21_flyt.js, 15_loop.js | I ro tegnet kartet 10 hele bilder i sekundet for at vannet skulle leve, også når det ikke var vann i bildet. Nå: ingen bilder i ro uten vann. Speilpasset (en hel scene til) hoppes over når vannet ikke synes. |
| Minimum-dybden til streken i eget pass (R32F) | src/01_etterbehandling.js | Streken slo opp tre dybder for hvert av 41 kall til `Dm()` per piksel (123 oppslag). Nå ett (41 oppslag) pluss tre i et lite forpass. Samme tall; `?mintex0=1` gir den gamle veien. |
| Lerretet uten MSAA (`antialias:false`) | src/00_oppsett.js | Byen tegnes med MSAA i eget mål og FXAA til slutt over hele lerretet; MSAA på lerretet var dobbeltarbeid. Skjermbildet er piksel for piksel likt (se under). |
| Ingen ny tekst eller nye lister per bilde i speilet; `__pt` gjenbrukes | src/14, 01 | Søppeltømming gir hakk. Før: matrisen ble gjort om til tekst hvert bilde i ro. |
| Måling per bilde: `window.__logg`, oppdater/speil/skyggekart/3D/strek/FXAA, `__maal='les'` venter på GPU-en | src/01, 14, 15_loop; verktoy/flyt_maal.mjs | Så tida kan fordeles på delene, før og etter. |
| Flyt-testen teller speilets alder bare når vann er i bildet | verktoy/flyt-test.mjs, regler/22_flyt.py | Uten vann tegnes ikke speilet med vilje. |

## Tall

Tegnekall per bilde (telt i siden, `__pt.kall`, hjemmevisningen): **762 før, 388 etter (−49 %)**. Bakkenett i scenen: 651 før, 17 etter.

Bilder tegnet i ro, tett på et hus inne i byen (zoom 4, ingen vann): før 10 per sekund i ekte Chrome (puls i 15_loop), **etter 0**.
I hjemmevisningen (vann i bildet) er det 10 per sekund som før: vannet lever.

Målt i hodeløs Chromium med programvare-GPU (swiftshader), 360 x 225 px, to runder på omgang før/etter
(`node verktoy/flyt_maal.mjs`, rådata i flyt-02nov-gpu.json og flyt-02nov-cpu.json). Maskinen var delt med en annen agent hele natta,
så ett bilde tok 3–7 sekunder; tallene er relative, ikke bildefrekvens. ms per bilde med GPU-venting (`GPU=1`, median):

| Scenario | Hele laget før | etter | Speil før | etter | Strek+AO før | etter | 3D før | etter |
|---|---|---|---|---|---|---|---|---|
| Ro, hjemmevisning | 6421 | 5370 | 1601 | 0 | 92 | 76 | 4882 | 5288 |
| Ro, tett på (zoom 4) | 4334, 0,25 bilder/s | **ingen bilder** | 1290 | – | 100 | – | 2923 | – |
| Panorering (dra 240 px) | 5670 | 5615 | 1467 | 1476 | 87 | **64** | 4143 | 4203 |
| Zoom (tre hjulhakk) | 6027 | 5577 | 1018 | 936 | 91 | **68** | 4978 | 4736 |
| Klikk på hus, kortet inn | 5238 | 5014 | 1503 | **708** | 87 | **64** | 3465 | 3691 |

- Streken (blekk + AO) er 22–26 % billigere i alle scenarioene der den tegnes.
- Speilet: halvparten av tida i klikk-scenarioet, fordi kameraet glir inn til der vannet går ut av bildet.
- 3D-passet er GPU-bundet i programvare (MSAA kjøres per prøve i swiftshader) og står likt innenfor støyen. Gevinsten av halvparten så
  mange tegnekall er CPU-tid, som ikke kan skilles fra GPU-tida på en maskin der «GPU-en» er de samme to CPU-kjernene. CPU-målingen
  uten GPU-venting (flyt-02nov-cpu.json) er for støyete til å bruke (få bilder, delt maskin); det sikre tallet er tegnekallene.

## Bildet er det samme

Skjermbilder 1100 x 750, samme kamera (verktoy/bilde.mjs, UI=0), i bilder-02nov/:
- for-hjem.jpg / etter-hjem.jpg: hjemmevisningen. 0,22 % av pikslene avviker mer enn 2/255, alle i vannet (vannets klokke går mellom
  bildene) og i de ytterste 1–3 pikslene langs venstre og nedre kant.
- for-naer.jpg / etter-naer.jpg: tett på Torvet, vannets klokke låst (`&t=5`). 0,28 % avviker mer enn 2/255, enkeltpiksler i streken
  langs vinduskanter og brosteinsfuger; naer-utsnitt-for-etter-avvik.jpg viser utsnittet før | etter | avvik forstørret. Det kan ikke
  ses med øyet.

Hva avvikene kommer av, er prøvd ut én ting om gangen (samme kamera, samme klokke):
- Før mot før (to kjøringer): 0 avvik. Tegningen er stabil.
- Lerretet med og uten MSAA: 0 avvik (piksel for piksel likt).
- Minimum-dybden i eget pass mot den gamle veien: 0,035 %, bare kantpiksler (oppslag utenfor bildet klemmes litt annerledes).
- Resten (ca. 0,25 %) er sammenslåingen av bakkeflatene: flater av samme materiale som ligger oppå hverandre i samme høyde, tegnes i en
  annen rekkefølge, så noen få piksler i streken langs kantene vinner den ene eller den andre. Begge rekkefølgene er like riktige.

## Prøvd, ikke tatt med

- Senke pixelRatio, skru av skygger, AO, strek eller speil: ikke prøvd. Vegars dom.
- Fordeling av 3D-tida per objektgruppe (skjule grupper og måle): for mye støy på delt maskin (±500 ms per bilde) til å bygge på.
- `document.hidden`: nettleseren stopper requestAnimationFrame i en skjult fane, så puls() står alt stille der. Ingen kode trengs.
- Pekeren over et hus (16_interaksjon: `treffHus` på mousemove, høyst hvert 45. ms) sender en stråle mot alle trekantene i byen.
  Ikke endret: fila er en annen agents område i natt. Verdt å måle i ekte Chrome (tast d) og gi byen en grov rute per hus om det koster.

## Oppløsningen opp?

Pikselbudsjettet (00_oppsett, `PIX`) er 11 millioner på maskin. Vegars iMac (5K, 5120 x 2880 = 14,7 M) tegnes i dag på
skala 0,86. Full oppløsning der er +35 % piksler. Det er ikke hevet i natt: gevinsten over er sikker på CPU-siden og i streken, men
3D-passet på en ekte GPU kan ikke måles her. Prøv i Chrome på iMacen: `?pix=15&d=1`, dra og zoom, og les «siste bevegelse … bilder/s»
mot vanlig lenke. Holder den følge, heves `PIX` til 15e6 for maskin.
