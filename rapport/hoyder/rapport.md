# Bygghøyder i Gamlebyen fra Kartverkets høydemodeller

Dato 24.10.2026. Alt kjøres på nytt med `python3 rapport/hoyder/hent.py` fra `soc/` (`--ny` laster ned rådata igjen). Ingenting i `src/` eller `data/` er endret.

## Kort

- **Dekning:** 276 bygg i Gamlebyen (`gamleby()`). 266 har forslag, 9 er skjult i kartet, kirka er stikkprøve. Sikkerhet: 134 høy, 63 middels, 69 lav.
- **Hovedfunn:** kartet står gjennomgående for høyt. Median avvik er **−2,3 m** på veggen (193 hus bør ned mer enn 1 m, 26 bør opp mer enn 1 m). Kartets møne ligger i snitt 3,5 m over det målte.
- **Takene er for bratte:** målt takhelning er 0,57 m stigning per meter inn fra takfoten (median av 178 hus, kvartil 0,37–0,73). Kartet bruker 0,82. Det tilsvarer ca. 30° mot kartets ca. 39°.
- **Tegnehøydene holder ikke som fasit:** også husene med «pålitelig» kvartaltegning bommer med −2,7 m i snitt, og samvariasjonen med målingen er svak (r = 0,46).
- Metoden er kontrollert på Infanterikasernen, der kartet og målingen treffer hverandre innen 0,1 m.

## Kilder

| Data | Adresse | Lisens |
|---|---|---|
| DOM 1 m (overflate med tak), Nasjonal høydemodell | `https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25832`, dekning `nhm_dom_topo_25832` | CC BY 4.0, © Kartverket (WCS-et oppgir «fees: free, access constraints: none») |
| DTM 1 m (terreng), Nasjonal høydemodell | `https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25832`, dekning `nhm_dtm_topo_25832` | CC BY 4.0, © Kartverket |
| Byggomriss og kartets høyder | `data/bygg.json` (OSM-omriss, h fra kvartaltegning eller OSM) | som i KILDER.md |

Rådata ligger i `kilder/dom1_25832.tif` og `kilder/dtm1_25832.tif` (EPSG:25832, 1 m, 1012 × 937 piksler, bbox 610991,6563830 – 612003,6564767). Hver fil har en `.json` ved siden av med den eksakte forespørselen. Begge tjenestene svarte direkte på curl. Fredrikstad kommunes DOM 2015 er ikke brukt fordi Kartverkets egen tjeneste var åpen. Skanneåret for DOM i Fredrikstad er ikke sjekket.

Attribusjon i kartet: «Høydedata © Kartverket, CC BY 4.0».

## Metode

1. Modellmeter → lon/lat på samme måte som `src/00_oppsett.js` (Web Mercator-skala ved origo) → UTM 32N (EPSG:25832, WCS-ets egen projeksjon).
2. **Forskyvning:** origo er bare kjent til ±3 m. Alle omriss ble flyttet i et rutenett på 0,5 m, og forskyvningen som traff flest piksler med DOM−DTM > 3 m ble valgt: **0,0 m øst, −1,0 m nord**. Treffandelen gikk fra 95,8 % til 96,5 %. Origo stemmer altså nesten, og forskyvningen er brukt på alle hus.
3. For hvert hus: piksler med senter inne i omrisset, krympet 1 m fra kanten (0,5 m eller 0 m for små hus, merket i `merknad`). p50 og p90 av DOM−DTM.
4. **Kartets overflate** regnes ut piksel for piksel slik `07_vinduer-dører-og-porter.js` bygger taket. For `tak2` (275 av 276 hus) blir det vegg `h` + takflatens `z` · 0,82. Andre varianter: `sk` med tak 7,5, saltak-prisme med `rise = min(kortside · 0,48, 7,5)`, pyramider for `deler`. Kirka følger `06_kirka` (vegg 9,5, møne 17,7, tårnskaft 34). Taket bestemmes av fotavtrykket og ikke av `h`, så kartets takhøyde over vegg er kjent i hver piksel.
5. **Forslag:** `h_forslag = median(DOM−DTM − kartets tak over vegg)`. Det er veggen som får kartets overflate til å treffe målingen best når taket bygges som i dag. Begge sidene er meter over bakken, så det trengs ingen skalering. `h_med_maalt_takhelning` er samme regnestykke med taket senket til den målte helningen 0,57. Den gir 0,3–0,8 m høyere vegg og er riktig tall hvis SLOPE i koden endres.
6. **Sikkerhet:** høy, middels eller lav ut fra antall piksler, rest etter tilpasning (MAD) og om p50 og p90 er enige. I tillegg merkes andel piksler under 2 m (gårdsrom, feil omriss, revet hus) og forslag som traff gulvet på 2 m.

## Kalibrering mot kartets egen modell

Utvalget er `fasade_kilde == 'kvartaltegning'` og 2,5 < tegnet_h/1,72 < 15, med minst 10 piksler, uten kirka: **82 hus**.

| Sammenligning (samme piksler) | Målt − kart, snitt | Median | Std | Målt/kart (median) | Lineær målt = a · kart + b | r | RMS |
|---|---|---|---|---|---|---|---|
| p50 (mellom gesims og møne) | −2,66 m | −2,66 m | 2,15 m | 0,76 | a = 0,44, b = 3,13 | 0,46 | 1,81 m |
| p90 (≈ møne) | −2,81 m | −2,87 m | 2,25 m | 0,76 | a = 0,46, b = 3,50 | 0,52 | 1,79 m |
| kartets møne (h + full takhøyde) mot p90 | −3,51 m | −3,75 m | 2,43 m | 0,72 | a = 0,41, b = 3,82 | 0,53 | 1,77 m |
| takhelning (stigning per meter inn fra takfot) | kart 0,82 | målt 0,57 | kvartil 0,37–0,73 | | | | |

Slik leser jeg tabellen: om kartets høyder hadde stemt, ville a vært nær 1 og b nær 0. Med a ≈ 0,45 og r ≈ 0,5 forklarer tegnehøydene bare en fjerdedel av variasjonen i de målte høydene. Bare 2 av 82 hus ble kastet som ekstremverdier. Forholdet mellom foreslått og tegnet h går jevnt fra 0,22 til 1,9 uten noen klynge, så feilen er ikke én gal skalafaktor (1,72) som kan rettes med ett tall.

Derfor brukes kalibreringen som kontroll og ikke som omregning. Å dele målingen på a = 0,44 ville doblet støyen. Forslaget bygger direkte på målingen i meter. Den eneste systematiske korreksjonen som er belagt, er takhelningen, og den ligger i et eget felt.

## Tegnet_h under 2,5 m (49 hus i Gamlebyen)

Alle står i dag med OSM-høyde (6,0, 3,0 eller 3,2 m). Målingen avgjør dem:

| Hus | h nå | h_forslag | med målt helning | sikkerhet |
|---|---|---|---|---|
| Kommandantgården (21) | 6,0 | 4,7 | 5,3 | middels |
| Artillerigården (9) | 6,0 | 8,5 | 9,3 | høy |
| Kiørboegården (11) | 6,0 | 6,8 | 7,3 | middels |
| Labratoriet (6) | 6,0 | 3,8 | 4,7 | høy |
| Krutthuset (10) | 6,0 | 4,7 | 5,2 | høy |
| Vollmesterboligen (17) | 6,0 | 3,8 | 4,4 | høy |
| Sprøytehuset / Proviantboden (29) | 6,0 | 3,1 | 3,6 | høy |
| Kruttårnet (28) | 6,0 | 4,8 | 5,5 | lav |
| Isegranhuset (100) | 6,0 | 5,4 | 6,0 | høy |
| Vennehaabet (248) | 6,0 | 7,4 | 8,2 | høy |
| Annekset (99) | 3,0 | 4,7 | 5,4 | høy |
| Kruttmagasinet (438) | 6,0 | 2,0 | 2,0 | lav: DOM−DTM er 0,0 m over hele omrisset. Bygget er typen «bunker»; terrengmodellen regner det trolig som bakke. Målingen kan ikke avgjøre dette huset |

Resten står i `hoyder.json` med merknaden «tegnet_h … (umulig): målingen avgjør». NB: Infanterikasernen (3) er ikke blant disse i dataene. Den har tegnet_h 17,2 (10,0 m), er i kalibreringsutvalget og treffer målingen. I hele datasettet er det 52 slike hus; 49 av dem er i Gamlebyen.

## De 20 største avvikene

Avvik = h_forslag − h_naa (vegg). x og y er modellkoordinater for midten av huset, fordi de fleste husene ikke har navn i dataene.

| # | Hus | h nå | h_forslag | avvik | med målt helning | målt p50 / p90 | kart p50 / p90 | sikkerhet |
|---|---|---|---|---|---|---|---|---|
| 235 | uten navn (x 88, y -99) | 9.7 | 2 | -7.7 | 2.3 | 3.2 / 4.5 | 11.1 / 11.4 | lav |
| 332 | uten navn (x 175, y 91) | 9.2 | 2.1 | -7.1 | 3.1 | 5.4 / 6.5 | 11.9 / 13.5 | lav |
| 330 | uten navn (x 111, y 98) | 9 | 2 | -7.0 | 2.1 | 3.2 / 3.4 | 10.4 / 11.2 | lav |
| 345 | uten navn (x 143, y 15) | 10.1 | 3.3 | -6.8 | 3.8 | 5.1 / 6.9 | 11.6 / 12.8 | middels |
| 354 | uten navn (x 129, y -17) | 8.6 | 2 | -6.6 | 2 | 2.5 / 4.3 | 9.4 / 9.7 | lav |
| 216 | uten navn (x 47, y 146) | 10.3 | 3.8 | -6.5 | 4.4 | 5.9 / 6.5 | 12.1 / 12.9 | middels |
| 380 | uten navn (x 168, y 106) | 8.6 | 2.1 | -6.5 | 2.4 | 3.5 / 3.9 | 10.0 / 10.4 | lav |
| 195 | uten navn (x 112, y 114) | 10.3 | 3.9 | -6.4 | 4.4 | 5.9 / 6.7 | 12.1 / 13.3 | høy |
| 199 | uten navn (x 166, y 85) | 10 | 3.6 | -6.4 | 4 | 5.2 / 6.0 | 11.4 / 11.9 | høy |
| 364 | uten navn (x 144, y 9) | 8.4 | 2 | -6.4 | 2.2 | 2.8 / 2.9 | 9.2 / 9.3 | lav |
| 219 | uten navn (x 178, y 106) | 10 | 3.8 | -6.2 | 4.2 | 5.5 / 6.2 | 11.5 / 12.2 | høy |
| 308 | uten navn (x 142, y 38) | 8.6 | 2.4 | -6.2 | 3 | 4.2 / 6.0 | 10.1 / 10.6 | lav |
| 329 | uten navn (x 100, y -7) | 8.8 | 2.6 | -6.2 | 2.9 | 3.8 / 4.0 | 9.9 / 10.2 | lav |
| 331 | uten navn (x 97, y 101) | 9.5 | 3.3 | -6.2 | 3.9 | 5.5 / 6.3 | 11.6 / 12.8 | middels |
| 333 | uten navn (x 102, y 110) | 8.6 | 2.4 | -6.2 | 3 | 4.9 / 5.9 | 11.0 / 12.6 | høy |
| 360 | uten navn (x 155, y 157) | 9.6 | 3.4 | -6.2 | 3.7 | 4.8 / 5.7 | 11.2 / 12.0 | middels |
| 381 | uten navn (x 98, y -18) | 10.1 | 3.9 | -6.2 | 4.4 | 6.1 / 7.1 | 11.9 / 13.1 | høy |
| 357 | uten navn (x 143, y 35) | 8.6 | 2.5 | -6.1 | 2.8 | 3.9 / 4.5 | 10.1 / 10.5 | lav |
| 189 | uten navn (x 102, y 96) | 10.1 | 4.1 | -6.0 | 4.6 | 6.3 / 7.2 | 12.2 / 13.5 | høy |
| 212 | uten navn (x 149, y 47) | 10.1 | 4.1 | -6.0 | 4.8 | 6.0 / 7.3 | 11.9 / 13.1 | høy |

Alle de 20 største avvikene gjelder hus som står for høyt. De ligger i rekkene i kvartalene midt i byen (blå klynger på kartet i kontrollarket). Typisk har kartet 9–10 m vegg og 12–13 m møne, mens målingen viser 6–7 m møne. Det er en etasje og et loft for mye. Der forslaget treffer gulvet på 2,0 m, er det målte huset lavere enn kartets tak alene. Da er det taket som må ned (smalere tak, lavere helning), ikke bare veggen.

Hus som bør **opp** (avvik ≥ 1,5 m):

| # | Hus | h nå | h_forslag | avvik | målt p50 / p90 | sikkerhet |
|---|---|---|---|---|---|---|
| 190 | uten navn (x -42, y 80) | 4.1 | 8.9 | +4.8 | 11.7 / 12.8 | høy |
| 177 | uten navn (x -29, y 100) | 3.8 | 8.5 | +4.7 | 11.3 / 12.4 | høy |
| 256 | uten navn (x 60, y -41) | 3.3 | 6.4 | +3.1 | 8.4 / 9.5 | høy |
| 121 | uten navn (x 320, y -205) | 3.2 | 6.1 | +2.9 | 7.9 / 9.3 | høy |
| 432 | uten navn (x -416, y 68) | 3 | 5.8 | +2.8 | 7.0 / 10.7 | lav |
| 187 | uten navn (x 159, y 102) | 3.6 | 6.2 | +2.6 | 8.4 / 9.5 | høy |
| 9 | Artillerigården (x 201, y 179) | 6 | 8.5 | +2.5 | 11.0 / 12.9 | høy |
| 8 | Binggården (x 50, y 118) | 5.6 | 8 | +2.4 | 10.4 / 11.6 | høy |
| 12 | Ingeniørgården (x 171, y -75) | 3.5 | 5.8 | +2.3 | 7.5 / 8.4 | høy |
| 265 | Kongeporten (x -157, y -43) | 3.2 | 5.4 | +2.2 | 6.3 / 7.9 | lav |
| 431 | uten navn (x -415, y 77) | 3 | 5.2 | +2.2 | 6.4 / 8.6 | lav |
| 56 | uten navn (x -417, y 399) | 3 | 4.8 | +1.8 | 7.3 / 8.0 | middels |
| 241 | uten navn (x -38, y 8) | 3.4 | 5.2 | +1.8 | 7.7 / 10.0 | middels |
| 99 | Annekset (x -345, y 52) | 3 | 4.7 | +1.7 | 7.0 / 8.0 | høy |
| 193 | Bullgården (x -13, y 115) | 4.2 | 5.8 | +1.6 | 8.6 / 9.5 | høy |
| 181 | uten navn (x 93, y 240) | 3.2 | 4.7 | +1.5 | 6.6 / 7.8 | høy |
| 239 | uten navn (x 81, y -9) | 5 | 6.5 | +1.5 | 8.9 / 10.2 | høy |

## Tre stikkprøver (snitt i `stikkprover.png`)

1. **Infanterikasernen (3), metodekontroll.** Kartet: vegg 10,0, møne 16,6. Målt: p50 13,4, p90 16,5, høyeste punkt 18,0. Snittet over huset viser at kartets saltak ligger oppå DOM-profilen innen noen desimeter fra takfot til møne. Forslaget er 10,1 m, altså uendret. Bakken 2–6 m utenfor veggen måler 0,01 m (p25), så DOM og DTM står likt på bakken, og forskyvningen er riktig.
2. **Kirken (4).** Skipet: målt p50 11,7, p90 14,2, maks 15,1. Kartet har møne på 17,7 m, altså **ca. 3 m for høyt**. Tårnet: høyeste DOM-punkt er 32,0 m, mens kartet har tårnskaftet på 34 m og spiret helt opp til 60 m. Et tynt spir fanges dårlig i en 1 m-overflatemodell, så den målte toppen er en nedre grense for spiret. Skaftet (34 m) ligger over hele DOM-profilen. Ingen forslag til h, siden kirka bygges i `06_kirka`. Tallene er grunnlag for å justere WH, RISE og SH der.
3. **Brannstasjon, uthus til Infanterikasernen (13).** Lite hus, 108 m². Kartet: vegg 7,4, møne ca. 9. Målt: p50 4,5, p90 4,9. Snittet viser et lavt hus med møne på ca. 5 m og trær på opptil 13 m like ved. Trærne ligger utenfor omrisset og påvirker ikke tallene. Forslaget er 3,2 m vegg (3,6 m med målt helning). Kartet står her ca. 4 m for høyt.

## Usikkerhet

- **Trær over tak** gir for høye p90 og stor rest. Hus med rest over 1,5 m er merket som lav sikkerhet.
- **Små hus** under ca. 40 m² gir få piksler etter krymping. Under 15 piksler er merket lav sikkerhet.
- **Omriss fra OSM** som dekker gårdsrom eller tilbygg i flere høyder trekker medianen ned. Merket når over 25 % av pikslene er under 2 m.
- **Takform:** forslaget forutsetter kartets tak. Når p50 og p90 sier ulikt (over 2 m), har huset et annet tak enn kartet (valm, mansard, flatt), og da er veggtallet alene ikke nok.
- **Tidspunkt:** DOM viser byen slik den var da den ble skannet. Skanneåret for Fredrikstad er ikke sjekket.
- Vertikal nøyaktighet i DOM og DTM er ikke slått opp. Kasernen og bakken utenfor (±0,01 m) tyder på at feilen er langt mindre enn avvikene i denne rapporten.

## Filer

- `hoyder.json`: per byggindeks `p50, p90, h_naa, h_forslag, sikkerhet, merknad`, pluss `avvik, h_med_maalt_takhelning, kart_p50, kart_p90, n_piksler, rest_m`.
- `kontrollark.png`: h nå mot h_forslag per hus (indeks merket der avviket er ≥ 1,5 m), og kart over Gamlebyen farget etter avvik.
- `stikkprover.png` og `stikkprover.json`: de tre snittene.
- `tall.json`: alle mellomtall (forskyvning, kalibrering, per-hus-statistikk).
- `hent.py`: hele kjøringen.
