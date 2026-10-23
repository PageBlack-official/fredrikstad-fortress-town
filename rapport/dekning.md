# Dekning: trykket (2015) mot 3D-modellen (Smart Old Town)

Dato: 23.10.2026. Kilder: `pdf/brosjyre.pdf` side 1 (vektor, lest med PyMuPDF), `pdf/side300-1.png` (sett med øynene i utsnitt), `soc/data/*.json`, `kvartal/ut/kobling-*.json`, `pdf/affin2.npy`.
Utsnittene jeg har merket ligger i `soc/rapport/dekning-utsnitt/` (7 PNG). Ingenting i `soc/src` eller `soc/data` er rørt.

## Hvordan trykket er bygd (viktig for alt under)

- Side 1 består av **12 030 fylte baner, null strektegninger og 5 rasterbilder**. Alle «streker» (husomriss, trekroner, kanter) er konturer gjort om til fyll. Bildene er akvarellteksturer (to grønne, én blå, to gråstrukturer) som ligger under og klippes av vektormasker. Vann og gress får altså farge fra raster, form fra vektor.
- Bakken i byen er **én mørk grå plate** (festningsplatået). Gatene er ikke egne objekter: gate = plate minus plen minus hus. Det finnes **ingen fortau, kantstein, oppmerking eller parkeringsplasser** i trykket. Jeg har sjekket det både maskinelt (ingen lyse striper langs gatene i gråklassene) og med øynene i alle sju utsnittene. Byfergen-båtene og en bil-lignende form i nord er det eneste «trafikk»-aktige.
- Objekter er kjent igjen på fyllfarge + banestørrelse. Tabell a) viser nøyaktig hva jeg brukte.

## a) Objekttyper i trykket

| Objekttype | Kjent igjen på | Antall i trykket (ca.) | I modellen | Merknad |
|---|---|---|---|---|
| Hus (fasader, tak, vinduer, piper, arker) | Røde/oransje/gule/grå fyll med 10–400 delbaner + mørkgrå konturbaner (5 000–11 000 delbaner) | ca. 330 tak i kvartaltegningene (sum av `typ: tak` i `kvartal/ut/*.json`); 379 modellbygg ligger innenfor kartutsnittet | `bygg.json`: 441 (9 skjult) | Modellen har flere småbygg (OSM-garasjer) enn trykket tegner. |
| Trekroner | Seks grønntoner (0.386/0.574/0.439 m.fl.), én bane per krone, 100–235 delbaner, bredde 10–58 pt | **338 kroner** (baner > 150 pt²) | `traer.json`: 2 385 punkter (alle innenfor kartet) | Modellen har ca. 7 punkter per tegnet krone. Enten mange stammer per krone eller skogsfelt som enkelt-trær. Ikke feil, men ikke 1:1. |
| Plen / gårdsrom gress | Lys grønn fyll (0.475/0.691/0.528), 17 store baner | 17 store + småfelt | `gront.json` 55 (OSM), `gardsrom.json` 17 (8 gress, 9 belagt) | Trykket skiller bare grønt/grått; modellen har samme to typer. |
| Vann (elv, vollgrav) | Blå raster klippet av vektormaske (0.583/0.843/0.889, 950 005 pt²) | 1 stor + vollgraver | `vann.json` 16 polygoner | Ja. |
| Voller og vollveier | Grå strek-baner (0.387/0.392/0.401, 77 baner) rundt bastionene + mørk grå vei oppå vollen | 15–20 vollkanter, 4 vollveier | `voller.json` 15, `landskap.terreng`, `landskap.veier` 331 (190 gang, 141 kjøre) | Ja, grovt. Ikke sjekket kant for kant. |
| Lyse stier (over plen, på bastion) | Lys grå strimler (0.84–0.93) ca. 3–5 pt brede | 6–8 stykker (ved 30, 25, 33, sør for 18) | OSM `footway` 477 segmenter | Trolig dekket av OSM-gangveier, ikke koblet én og én. |
| Murer | Lys grå tykk kant (parkmur Tøihuset), tegl (ved 3), fortring Isegran | 4–6 synlige | `murer.json` 21 (11 wall, 5 retaining, 4 fence, 1 ruin) | Trykket tegner få murer; modellen har flere (OSM). |
| Plankegjerder | Brun, tannet stripe (Tøihusgaten ved 8) | 1 tydelig, 1–2 usikre (ved 36, ved 12) | `gjerder.json` 46 segmenter | Modellen har langt flere enn trykket viser. |
| Porter | Hus med portåpning (11, 25, 34, 44) | 4 | `porter.json` 4 | Ja. |
| Broer | Vindebroen (26) tegnet som ramme over vann; Isegran-landgang | 1 (+1 usikker) | `broer.json` 3 | Ja for Vindebroen. |
| Statue | Figur på sokkel på torget | 1 | `statue.json` 1 | Ja. |
| Nummer-markører 1–46 | Mørk grå sirkel (0.221/0.216/0.222, areal 208 pt², 64 baner) med lys tall; jeg fant 47 sirkler med tallbredde | 46 (+1 feiltreff) | `legende.json` 46 | Ja. |
| Tjeneste-ikoner | Hvit sirkel 15 pt + svart symbol: spise (ca. 10), museum (4), info (1), hotell (1), WC (1), ferje (1), «T»-symbol (1) | ca. 19–26 (26 hvite sirkler, noen er vinduer) | **mangler** | Verdt å ha: er del av kartets bruksverdi. |
| Gatenavn | Hvit versal-tekst langs gate (8 tekstblokker + 9 gatenavn som kurver) | 9 gatenavn + Isegran + Kongsten fort | OSM `veier.json` har `name` på en del, bl.a. Toldbodgaten | Modellen har ikke utplassert navn langs gater. |
| Båter | Rød ferje med hvitt dekk, 2 stk ved Toldbodgaten; brun båt under bygging på Isegran | 3 | **mangler** | |
| Brygge med pullerter | Rosa flate + 3 stolper ved 14 | 1 | mangler | |
| Flagg | Flaggstang på Tøihus-tårnet (20) | 1 | mangler | |
| Små figurer/lykter | To små gule bokser på Isegran | 2 | mangler | Usikker på hva de er. |
| Fortau | – | **0 (ikke tegnet)** | mangler | Begge mangler. Skal bygges fra annen kilde enn trykket. |
| Parkering | – | **0 (ikke tegnet)** | mangler | Som over. |
| Biler, lyktestolper, benker, skilt | – | **0** | – | Finnes ikke i trykket. Bare «Kongsten fort»-skiltet nederst til høyre. |
| Brostein | – | 0 (torget er lys beige flate) | `brostein.json` 43 punkter | Modellen legger brostein der trykket bare har en lys flate. |
| Skygger | Mørk grå (0.18–0.26) flater sør-vest for hus | ca. 300 | gjengis av lys i modellen | Ikke data. |

Maskinelt talt: hus (tak), trekroner, markører, ikoner, vollkanter. Sett med øynene: murer, gjerder, porter, broer, båter, brygge, flagg, figurer, fortau/parkering (fravær).

## b) Dekningsmatrise

Rader = de 14 kvartaltegningene (fra `kvartal/ut/kobling-*.json`, felt `kvartal` = modellbygg i tegningen) + kirke-tegningen er ikke egen rad fordi den ikke har kobling-fil (kirka er bygg 4, nr 7, i Kvartal 10-regionen), + Glasshytta + Tøihuset + fire områder uten kvartaltegning. Kvartal 1 har ingen tegning i mappa.

Regionen for en rad er bokser rundt kvartalets modellbygg + 10 m, så **naborader overlapper** og summene er høyere enn kartet. For trykket er objektene regnet om til modellmeter via inversen av `affin2.npy`. «Sett»-områdene (de fire siste) er pt-bokser i trykket, og blir store skjeve bokser i modellen; tallene der er grove.

Lesing: «ja» = tallene er like nok til at jeg tror kildene viser det samme. «usikker» = tallene finnes i begge, men jeg kan ikke si at de peker på de samme objektene. «ikke sjekket» = jeg har ikke sett på dette området med øynene.

| Område | Kilde | Bygg: trykk / modell | stemmer? | Trær: kroner i trykk / punkter i modell | stemmer? | Markører: trykk / legende | stemmer? | Ikoner: trykk / modell | stemmer? | Murer / gjerder i modell | stemmer? | Fortau: trykk / modell | Parkering: trykk / modell | Porter / broer / statue i modell |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kvartal 2 | kvartaltegning | 32 / 37 | ja | 14 / 94 | usikker (modellen har flere punkter per krone) | 6 / 6 | ja | 1 / 0 | nei (mangler i modellen) | 0 / 10 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 3 | kvartaltegning | 15 / 32 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 19 / 166 | usikker (modellen har flere punkter per krone) | 4 / 5 | usikker | 0 / 0 | – | 0 / 8 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 4 | kvartaltegning | 18 / 20 | ja | 8 / 51 | usikker (modellen har flere punkter per krone) | 4 / 3 | usikker | 2 / 0 | nei (mangler i modellen) | 1 / 10 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 5 | kvartaltegning | 30 / 54 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 2 / 6 | usikker (modellen har flere punkter per krone) | 7 / 6 | usikker | 5 / 0 | nei (mangler i modellen) | 0 / 13 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 6 | kvartaltegning | 28 / 52 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 9 / 21 | usikker (modellen har flere punkter per krone) | 4 / 3 | usikker | 6 / 0 | nei (mangler i modellen) | 0 / 8 | ikke sjekket | nei / nei | nei / nei | 1 / 0 / 0 |
| Kvartal 7 | kvartaltegning | 19 / 36 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 10 / 31 | usikker (modellen har flere punkter per krone) | 9 / 9 | ja | 6 / 0 | nei (mangler i modellen) | 2 / 13 | ikke sjekket | nei / nei | nei / nei | 1 / 0 / 1 |
| Kvartal 8 | kvartaltegning | 34 / 77 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 8 / 30 | usikker (modellen har flere punkter per krone) | 9 / 5 | usikker | 10 / 0 | nei (mangler i modellen) | 0 / 23 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 1 |
| Kvartal 9 | kvartaltegning | 34 / 68 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 17 / 145 | usikker (modellen har flere punkter per krone) | 2 / 1 | usikker | 6 / 0 | nei (mangler i modellen) | 0 / 12 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 10 | kvartaltegning | 21 / 26 | ja | 23 / 93 | usikker (modellen har flere punkter per krone) | 8 / 6 | usikker | 2 / 0 | nei (mangler i modellen) | 2 / 15 | ikke sjekket | nei / nei | nei / nei | 1 / 0 / 0 |
| Kvartal 11 | kvartaltegning | 5 / 33 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 9 / 54 | usikker (modellen har flere punkter per krone) | 5 / 5 | ja | 1 / 0 | nei (mangler i modellen) | 0 / 17 | ja (teglmur ved 3 sett) | nei / nei | nei / nei | 0 / 0 / 1 |
| Kvartal 12 | kvartaltegning | 36 / 58 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 14 / 93 | usikker (modellen har flere punkter per krone) | 1 / 1 | ja | 1 / 0 | nei (mangler i modellen) | 0 / 9 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 13 | kvartaltegning | 14 / 5 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 18 / 62 | usikker (modellen har flere punkter per krone) | 5 / 4 | usikker | 0 / 0 | – | 1 / 9 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Kvartal 14 | kvartaltegning | 34 / 37 | ja | 27 / 233 | usikker (modellen har flere punkter per krone) | 2 / 1 | usikker | 6 / 0 | nei (mangler i modellen) | 0 / 8 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Siste kvartal (21) | kvartaltegning | 15 / 7 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 22 / 171 | usikker (modellen har flere punkter per krone) | 1 / 1 | ja | 6 / 0 | nei (mangler i modellen) | 0 / 2 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Tell (23) | kvartaltegning | 6 / 1 | usikker (regionboks tar med nabobygg eller tegningen deler tak) | 6 / 31 | usikker (modellen har flere punkter per krone) | 0 / 1 | usikker | 0 / 0 | – | 0 / 0 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Glasshytta | kvartaltegning | 3 / 1 | ja | 2 / 18 | usikker (modellen har flere punkter per krone) | 0 / 0 | ja | 0 / 0 | – | 0 / 0 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Tøihuset (19) | bare trykk | – / 4 | ikke sjekket (ingen kvartaltegning) | 29 / 144 | usikker (modellen har flere punkter per krone) | 3 / 2 | usikker | 7 / 0 | nei (mangler i modellen) | 1 / 5 | ja (plankegjerde + parkmur sett) | nei / nei | nei / nei | 0 / 0 / 0 |
| Vest: 11–14 | bare trykk | – / 7 | ikke sjekket (ingen kvartaltegning) | 13 / 50 | usikker (modellen har flere punkter per krone) | 5 / 4 | usikker | 3 / 0 | nei (mangler i modellen) | 3 / 3 | ikke sjekket | nei / nei | nei / nei | 1 / 0 / 0 |
| Isegran | bare trykk | – / 16 | ikke sjekket (ingen kvartaltegning) | 49 / 200 | usikker (modellen har flere punkter per krone) | 5 / 6 | usikker | 5 / 0 | nei (mangler i modellen) | 4 / 3 | usikker (fortringen er mur i trykket; modellen har 4 murer her, ikke sjekket hvilke) | nei / nei | nei / nei | 1 / 0 / 0 |
| Havn/Vindebroen (25–28) | bare trykk | – / 3 | ikke sjekket (ingen kvartaltegning) | 32 / 100 | usikker (modellen har flere punkter per krone) | 3 / 3 | ja | 0 / 0 | – | 0 / 1 | ikke sjekket | nei / nei | nei / nei | 1 / 2 / 0 |
| Sør: voll 17–18,21–22 | bare trykk | – / 52 | ikke sjekket (ingen kvartaltegning) | 57 / 408 | usikker (modellen har flere punkter per krone) | 6 / 4 | usikker | 3 / 0 | nei (mangler i modellen) | 1 / 1 | ikke sjekket | nei / nei | nei / nei | 0 / 0 / 0 |
| Nord/øst-vollen (33–34) | bare trykk | – / 121 | ikke sjekket (ingen kvartaltegning) | 87 / 740 | usikker (modellen har flere punkter per krone) | 23 / 20 | usikker | 12 / 0 | nei (mangler i modellen) | 3 / 27 | ikke sjekket | nei / nei | nei / nei | 2 / 2 / 0 |

Tre ting matrisen viser:
1. **Bygg stemmer i 5 av 16 tegninger** (2, 4, 10, 14, Glasshytta). I de fleste andre har modellen flere bygg enn tegningen har tak, fordi regionboksen drar inn nabokvartal og OSM har småbygg (garasjer, uthus) som trykket ikke tegner. Tre steder er det motsatt: Kvartal 13 (14 tak mot 4 koblede modellbygg), siste kvartal (15 mot 7) og tell (6 mot 1). Der er koblingen i `kvartal/ut/kobling-*.json` for tynn og bør ses på.
2. **Trær er det største tallavviket**, men trolig ikke feil: 338 kroner i trykket mot 2 385 punkter i modellen. Vegar må si om modellen skal ha én stamme per tegnet krone (da er 2 000 punkter å kaste) eller om tettheten er ønsket.
3. **Alt som mangler i modellen er småting:** ikoner, båter, brygge, flagg, gatenavn på bakken. Fortau og parkering mangler i begge, så de kan ikke hentes fra trykket.

## c) Forslag til datamodell for manglende lag

Alle i modellmeter (x = øst, y = nord, origo som i `soc/KILDER.md`). Kilde-feltet er obligatorisk, slik de andre filene har det.

### fortau.json (finnes ikke i trykket; kilde må bli OSM `sidewalk`-tagger, FKB-vegkant eller flyfoto)
```json
[
  {
    "p": [[-12.4, 18.0], [3.1, 24.6], [20.8, 31.9]],
    "w": 1.8,
    "side": "v",
    "vei": "Kirkegaten",
    "kant": "kantstein",
    "h": 0.12,
    "dekke": "heller",
    "kilde": "flyfoto-google-2026-10-23"
  }
]
```
- `p`: polylinje langs fortauets senterlinje, meter.
- `w`: bredde i meter.
- `side`: `v`/`h` i forhold til veiens retning i `veier.json` (så fortauet kan regenereres hvis veien flyttes).
- `vei`: navn eller indeks i `veier.json` det hører til.
- `kant`: `kantstein`, `ingen`, `rennestein`: styrer om det tegnes en kant mot gata.
- `h`: kanthøyde i meter (0 = i plan med gata).
- `dekke`: `heller`, `asfalt`, `grus`, `brostein`: velger materiale.
- `kilde`: hvor linja kommer fra.

### parkering.json (finnes ikke i trykket)
```json
[
  {
    "p": [[150.2, -60.1], [171.5, -55.0], [168.9, -43.2], [147.6, -48.3]],
    "type": "oppmerket",
    "plasser": 14,
    "retning": [0.97, 0.23],
    "dekke": "asfalt",
    "navn": "Voldgaten",
    "kilde": "osm amenity=parking"
  }
]
```
- `p`: polygon i meter.
- `type`: `oppmerket` (tegn striper), `grus` (ingen striper), `gate` (langsparkering langs fortau).
- `plasser`: antall plasser hvis tegnet/kjent, ellers `null`.
- `retning`: enhetsvektor for stripene; `null` når `type` ikke er oppmerket.
- `dekke`: materiale.
- `navn`: valgfritt.
- `kilde`: OSM/flyfoto/befaring.

### ikoner.json (finnes i trykket: 19–26 stk)
```json
[
  { "xy": [12.0, 48.5], "typ": "info", "navn": "Turistinformasjonen", "bygg": 107, "kilde": "brosjyre 2015" }
]
```
- `xy`: posisjon i meter. `typ`: `spise`, `museum`, `info`, `hotell`, `wc`, `ferje`, `butikk`. `navn`: valgfritt. `bygg`: indeks i `bygg.json` hvis ikonet hører til et hus, ellers `null`. `kilde`.

### baater.json (finnes i trykket: 3 stk)
```json
[
  { "xy": [60.0, 190.0], "ret": [0.9, 0.4], "l": 12.0, "b": 4.0, "typ": "ferje", "navn": "Byfergen", "kilde": "brosjyre 2015" }
]
```
- `xy`: senter i meter. `ret`: enhetsvektor for baugen. `l`/`b`: lengde og bredde i meter. `typ`: `ferje`, `trebaat`, `fritid`. `navn`, `kilde`.

### smaating.json (brygge, pullerter, flagg, lykter, benker: alt som er punkt + retning)
```json
[
  { "xy": [-130.0, -20.0], "typ": "pullert", "ret": null, "h": 0.8, "kilde": "brosjyre 2015" },
  { "xy": [-128.0, -22.0], "typ": "flaggstang", "ret": null, "h": 9.0, "bygg": 230, "kilde": "brosjyre 2015" }
]
```
- `xy`: meter. `typ`: `pullert`, `flaggstang`, `lykt`, `benk`, `skilt`, `figur`. `ret`: enhetsvektor der det betyr noe (benk, skilt), ellers `null`. `h`: høyde i meter. `bygg`: hvis festet til et hus. `kilde`.
- Brygga ved 14 passer bedre som polygon i `gardsrom.json` med `typ: "brygge"` enn som ny fil.

### gatenavn.json (finnes i trykket: 9 + 2 stedsnavn)
```json
[
  { "navn": "KIRKEGATEN", "p": [[-20.0, 40.0], [30.0, 62.0]], "kilde": "brosjyre 2015" }
]
```
- `navn`: tekst slik den står i trykket. `p`: linja teksten følger, meter. `kilde`.

## Usikkert

- Trekrone-tellingen (338) teller baner, ikke trær. Tette rekker på vollen kan være tegnet som én bane med flere kroner, så det reelle tallet kan ligge på 350–450.
- Ikon-tellingen (26 hvite sirkler på 15 pt) kan inneholde et par runde vinduer; med øynene teller jeg 19–21 ikoner.
- Markør-tellingen fant 47 sirkler mot 46 numre; én er trolig ferje-ikonets bakgrunn eller lignende.
- «Parkmur» rundt Tøihus-parken og «mur/gjerde ved 36» er lest fra tegnemåten (lys grå kant / brun stripe), ikke fra et feltnavn. Vegar bør bekrefte i utsnitt 4 og 7.
- Kvartalregionene er bokser, ikke polygoner, så bygg- og tretall per rad overlapper nabokvartaler.
