# FUNN — Voldportgaten 75–71 bygd om etter Vegars bilder (PAG-1589, 14.11.2026)

Gren `gate/voldport-1411`. Modellen bygd på nytt (bygg_kjede.py), regler 13/14/17/20/48 grønne.
GPU-render (ekte Metal) i KONTAKTARK.png + de fem bildene. Les bildene mot punktlista i OPPGAVE.md.
**Jeg har lest de ferdige renderbildene kritisk mot fasiten**, ikke bare koden (jf. kalibreringen 13.11).

## Hva som ble endret i data (ikke i scenen)
- **kilder/husdeling.json**: fjernet kuttet på `bnr-193867928` (det som laget pb-66 30.10). 75 er igjen **ett omriss / ett tak / én bygning**.
- **data/rettelser.json**: `pb-66` beholdt som id (op ny) og **skjult** med grunn «Vegar 14.11: ett tak, én bygning». Id slettes aldri (regel 14/20) — verifisert grønn.
- **kilder/hoyde-unntak.json**: `bnr-193868258` (71 Therese M) → h 4,2 / th 0,6: **én etasje, lavest**. Høyder nå **75 (7,9 m) > 73 (6,1 m) > 71 (4,2 m)** ✓.
- **kilder/tak-tegning.json**: 75 = **valm**, 73 = **saltak**, 71 = **valm** (maks 1 kropp hver).
- **kilder/bygg-merknader.json**: farger, navn og fasadene (vegger med vinduer/dører/port) for de tre, kilde «Vegar 14.11 (Street View mai 2024, hans bilder)». Merknadene kjøres sist i kjeden og vinner.
- **verktoy/bygg_merknader.py**: lagt til valgfri `bue`/`stor` pr. vegg i vegg-merknaden (rundbuet butikkvindu = `bue:1`), additivt — rører ingen andre hus. (Idempotent, deterministisk av JSON.)

## Bilde for bilde mot Vegars ord

### 75 (bnr-193867928) — bilde 1, 2, 3, 5
| Vegar sa | I renderen | Dom |
|---|---|---|
| Ett felles tak, én bygning | Ett valmtak rundt hjørnet, én mønehøyde (pb-66 borte) | ✓ |
| Fasade i tre, lys gråbeige/gråfiolett | Vegg [204,192,198], én sammenhengende farge (ingen fasadesegmenter i ulik farge) | ✓ |
| Valmtak i rødbrun tegl | Valmtak [168,82,62] | ✓ |
| 2 etasjer | 2 vindusrekker | ✓ |
| Mot Voldgaten: 8 vinduer i 2. etg (T-sprosser), store butikkvinduer + **to** inngangsdører i 1. etg | Bilde 2: 8 vinduer oppe, butikkvinduer + 2 dører nede | ✓ |
| Mot Voldportgaten: butikkvinduer + skråinngang, flere butikkinnganger, brun dobbeltport til bakgården | Bilde 1/3: butikkvinduer + flere dører + én bred port (typ 2) | ✓ på karakter/antall |
| Hjørnet: 2. etg rett hjørne, **bare 1. etg** skåret skrått inn (innbygd skråinngang, utkraget tak) | Dør ved hjørnet, men hjørnet er likt i begge etasjer | ✗ **ikke modellert** (se under) |
| Mørkebrune hjørnekasser, gesims, vannbord | — | ✗ ikke modellert |

### 73 Majorens Kro & Stue (bnr-193868622) — bilde 3, 5
| Vegar sa | I renderen | Dom |
|---|---|---|
| Eget tak, takstein, litt lavere enn 75 | Eget saltak [150,120,108], 6,1 m < 7,9 m | ✓ |
| Hvitaktig murfasade | Vegg [233,230,222] | ✓ |
| 5 vinduer i 2. etg | 5 vinduer oppe | ✓ |
| 1. etg: inngang i midten (steintrapp), store doble vinduer på hver side, port til bakgården | Midtdør + store vinduer + bred port (typ 2) | ✓ (steintrapp ikke modellert) |
| Navn | «Majorens Kro & Stue» satt | ✓ |
| Mønretning | Taket står med **gavl mot gata** (tak_enkel/DOM-tilpasning) — bør kanskje ha mønet langs gata | ⚠ sjekk mot foto |

### 71 Therese M (bnr-193868258) — bilde 3, 4, 5
| Vegar sa | I renderen | Dom |
|---|---|---|
| Én etasje, lavest | 1 vindusrekke, 4,2 m (lavest i rekka) | ✓ |
| Hvit mur | Vegg [236,236,231] | ✓ |
| Eget lavere valmtak, takstein, 2–3 piper | Valmtak [176,86,64], piper på mønet | ✓ |
| Butikkvinduer med **rund bue øverst** («ovale topp-vinduer») | 5 rundbuede butikkvinduer langs gata (`bue:1`) | ✓ |
| Skrått hjørne i HELE høyden med inngang mot gata | Skrått hjørne (omrisset) + inngangsdør ved hjørnet | ✓ (full høyde stemmer her) |
| Navn | «Therese M» satt | ✓ |

## Det som IKKE er modellert (ærlig liste til Vegar/Fable)
1. **75s hjørne «skråinngang bare i 1. etasje» med utkraget tak.** Modellen bygger vegger rett opp fra ett omriss, så et hjørne som er rett i 2. etg og skrått inn i 1. etg kan ikke uttrykkes uten per-etasje-geometri. Nå står en inngangsdør ved hjørnet; selve den inntrukne skråinngangen og det utkragede taket mangler.
2. **75s mørkebrune snekkerdetaljer** (hjørnekasser, gesims, vannbord, foringer rundt vinduene) — ikke i datamodellen for vanlige hus.
3. **Butikkenes nøyaktige plassering langs 75** (Gamlebyen Elektriske med to dører, Emm K, Agnes C) er lagt inn som en **jevn rytme** av butikkvinduer + dører + én port, ikke metrisk per forretning. Antall og karakter stemmer; de eksakte dørposisjonene er en tilnærming.
4. **Steintrapper** foran inngangene (73 og 71) er ikke egne objekter.
5. **73s mønretning**: gavl mot gata nå — verifiser mot Vegars foto om mønet skal ligge langs gata.

## Regler (grønne)
- 14_id: pb-66 beholdt + skjult, ingen id slettet. ✓
- 13_deler_staar_paa_topp: piper/arker på taket. ✓
- 20_grunnmur_fkb: 0 kommunehus uten modellhus (IoU≥0,7), 0 modellhus dekker flere. 75 (helt) dekker sitt FKB-omriss. ✓
- 17_vinduer_rytme: 0 brudd. ✓
- 48_vinduer_ikke_oppaa_hverandre: 0 overlapp. ✓

IKKE publisert. Fable leser bildene før noe kalles ferdig.
