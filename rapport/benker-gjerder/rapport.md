# Benker og gjerder: datagrunnlag (24.10.2026)

Kjør på nytt: `python3 rapport/benker-gjerder/hent.py` (henter OSM), eller med `--cache`. src/ og data/ er ikke rørt.

## Kort
- **Benker: 78** i modellens område (69 benker, 9 piknikbord). Alle kommer fra OpenStreetMap. **2019-trykket tegner ingen benker** (sjekket i 12 rutenettutsnitt og 5 nærbilder). 51 av dem ligger på land inne i trykkets kart. De 27 andre ligger på Isegran og på elvebredden nord/vest for elva, der modellen har hus men trykket ikke viser noe. Det står i feltet `i_trykket`. 39 benker utenfor modellens område er tatt ut (Fredrikstad stasjon, sentrum), se `tall.json`.
- **Gjerder: 12 linjer lest i trykket.** 7 av dem finnes allerede i data (gjerder.json eller murer.json). Det gir **5 nye fra trykket og 2 nye fra OSM, til sammen 7 forslag** i `gjerder-forslag.json`.
- Det er trykket som er fasiten, og det tegner få gjerder. Gamlebyen har flere plankegjerder i virkeligheten enn trykket viser. Dagens 46 gjerder.json-linjer er flere enn trykket har. Opphavet deres er ukjent: de lå ferdig i den gamle bydata.json.

## Filer
| Fil | Innhold |
|---|---|
| gjerder-forslag.json | 7 nye polylinjer i samme format som data/gjerder.json |
| gjerder-kilde.json | én rad per linje, i samme rekkefølge: kilde, 2019-px, type, farge i trykket, sikkerhet, merknad |
| benker.json | `{x, y, retning_grader, kilde, type, retning_kilde, i_trykket, osm, lon, lat}` |
| tegnet2019.json | det jeg leste i trykket (fot-linjer i 2019-px). Dette er håndarbeidet; resten regnes ut |
| kontrollark.png | 6 områder, med 2019-trykket til venstre og flyfoto til høyre. Grått = dagens gjerder, mørkegrått = murer, rødt = forslag (stiplet = lav/usikker), blått = benk med strek for antatt retning |
| tall.json | alle tall og avstander rapporten bygger på |
| hent.py, proj.py | verktøyet (modell ↔ 2019-px ↔ flyfoto ↔ lat/lon) |

## Gjerdelinjene i trykket (T1–T12)
| id | hva / hvor | sikkerhet | status |
|---|---|---|---|
| T1 | brunt plankegjerde, Tøihusgaten mellom 9 og 8 | høy | finnes (gjerder[3], 2,7 m) |
| T2 | hvit mur/gjerde, Kasernegaten sørside øst for 10 | middels | **ny** |
| T3 | hvit mur, Kasernegaten nord, på tvers av gata inn mot 45-kvartalet | høy | finnes (gjerder[14], 3,6 m etter klipp) |
| T4 | hvit, Kasernegaten nord vest | lav | finnes (gjerder[5]) |
| T5–T7 | Tøihusparken: grønn kant NV og SV, hvit mur SØ | middels/høy | finnes (murer[1], OSM-muren) |
| T8 | hekk rundt hagen nord for 20 | middels | finnes (gjerder[8], 3,6 m) |
| T9 | gul mur rundt gårdsrom sør for 20-kvartalet | lav | **ny** |
| T10 | hvit mur, Raadhusgaten | lav | **ny** (bare 2,7 m igjen etter klipp) |
| T11 | gul mur ved 37 | lav | **ny** |
| T12 | to tynne linjer fra 30 mot 29 | usikker (kan være sti) | **ny** (4,7 m igjen etter klipp) |

I tillegg kommer to nye fra OSM: way 1484177463 og 1484177464, barrier=fence, 6 m og 21 m vest på Isegran. De ligger utenfor alle panelene på kontrollarket og er ikke sett med øynene.

Regelen for «finnes» er at linja i snitt ligger nærmere enn 4 m en eksisterende gjerde- eller murlinje.

**Regel jeg la inn: et gjerde stopper ved husveggen.** Fem av trykklinjene gikk 9–15 m inn i fotavtrykkene. Husene i trykket står på mønehøyde, så et gjerde som er tegnet «inn til huset», havner inne i huset når det regnes om til bakken. hent.py klipper bort det som ligger inne i hus og beholder den lengste biten.

## OSM-supplementet
OSM-API-et ble brukt direkte (api.openstreetmap.org). overpass-api.de kuttet forbindelsen gjennom proxyen, og WebFetch nektet (robots). Et Overpass-speil (mail.ru) ble stoppet av tillatelsessjekken, så det er ikke brukt.

Alle OSM-murer i byen finnes allerede i murer.json (avvik 0,7 m). Den eneste hekken i OSM er utenfor modellen. OSM har 6 gjerder: 4 ligger i murer.json fra før, og de 2 på Isegran er nye.

## Benkenes retning
OSM har ingen `direction`-tagg på noen av benkene, så `retning_grader` er **antatt** (kompasskurs for hvor man ser, 0 = nord):
- Er det vann nærmere enn 15 m, vender benken mot vannet. Det gjelder 26.
- Ellers vender den mot nærmeste vei eller sti. Det gjelder 52.

Begrunnelsen står i `retning_kilde` for hver benk.

## Tre stikkprøver jeg tok selv
1. **T1, plankegjerdet i Tøihusgaten.** I 2019-utsnittet (rutenett 560/500) ser jeg et brunt, tannet gjerde mellom 9 og 8. Omregnet ligger det 2,7 m fra dagens gjerder[3]. På kontrollarket (A) følger den grå linja gata på samme side. Det stemmer.
2. **Benkene på torget (statuen, 1).** OSM har 5 benker rundt statuen, fra (−1, 56) til (26, 64). I 2019-utsnittet (panel D) havner de på torgflaten rundt statuen og 2, og på flyfotoet ligger de på den åpne plassen. Plasseringen er troverdig. Selve benkene ser jeg ikke på flyfotoet: oppløsningen er ca. 0,4 m/px, og en benk blir 4–5 px.
3. **T3 i Kasernegaten.** Jeg trodde først muren fulgte gata. I nærbildet (4x) går den på tvers av gata, inn mot 45-kvartalet, og på flyfotoet (panel B) gikk den røde linja inn i et hus. Det var dette som ga regelen om at gjerdet stopper ved husveggen. Etter klipp ligger den 3,6 m fra gjerder[14], så den finnes allerede.

## Det jeg er usikker på
- **T9–T12 er lest fra få piksler** (±3 px er ca. ±1–2 m) og kan være husvegger eller sokler. Derfor er de stiplet. T12 kan like gjerne være en sti.
- **T5/T6 er grønne i trykket** (hekk eller grønnmalt mur) på samme sted som OSM-muren rundt Tøihusparken. Det er et spørsmål om farge, ikke en ny linje.
- **42 av dagens 46 gjerder har ingen støtte i trykket.** Ingen av dem går inn i hus. Jeg har ikke slettet noe og foreslår ikke å slette noe uten en kilde.
- **Benkene er ikke verifisert én og én** på flyfotoet, på grunn av oppløsningen. Retningen er antatt for alle. 15 har `check_date` fra 2021–2025 i OSM.
- **Flyfotoet dekker bare midten av byen.** Panel F og deler av E faller delvis utenfor.
