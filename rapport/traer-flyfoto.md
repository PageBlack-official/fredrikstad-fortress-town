# Treregister fra flyfoto (forslag, 23.10.2026)

Forslag til nytt `data/traer.json`, laget fra `kilder/flyfoto-google-2026-10-23.jpg`. Ikke lagt inn i `data/` – ligger her som
`rapport/traer-flyfoto.json` (ren liste, kan kopieres rett inn), `rapport/traer-flyfoto.meta.json` (metode og tall) og
`rapport/traer-flyfoto-kontrollark.png` (fotoet med funnene).

## Tall

| | |
|---|---|
| Kroner funnet i fotoet | **1 451** |
| … av dem med høy sikkerhet (≥ 0,7) | 597 |
| … delt ut av tette felt med k-means (posisjon omtrentlig) | 830 |
| Gamle punkter utenfor fotoet, beholdt (sikkerhet 0,2) | 365 |
| **Totalt i forslaget** | **1 816** |
| Dagens `traer.json` | 2 385 (2 020 innenfor fotoet) |
| Kroner i 2015-trykket (`dekning.md`) | ca. 338 |
| Forkastet | 216 for små (< 6 m²), 30 i kanten av fotoet, 15 inne i hus |

Dagens modell hadde ca. 7 punkter per tegnet krone i trykket; forslaget har ca. 4 per trykt krone. Trykket tegner de store
rekkene på vollene som få, brede kroner (10–58 pt), fotoet viser at det faktisk står mange trær der – forslaget følger fotoet.

## Metode

1. **Vegetasjon**: HSV-grønt som i regel 01 (H 30–95, S > 45) pluss ExG > 10, svart ramme utenfor fotoet maskert.
2. **Trekroner mot plen**: lokal tekstur (standardavvik i V over 7×7, glattet) > 11 *og* mørkere enn plen (V < 125). Plen er glatt og lys, kroner er mørke og kornete. Åpning/lukking 5 px, felt < 6 m² fjernet.
3. **Enkeltkroner**: avstandstransform av kronemasken, topper med minst 3,5 m avstand, Voronoi-celle rundt hver topp. Celler bredere enn 11 m (tette rekker på vollene) er delt med k-means i kroner på ca. 7,6 m i diameter, dvs. 6–8 m mellom sentrene. Disse er merket `delt` og får sikkerhet ≤ 0,7.
4. **Per krone**: diameter D = 2·√(areal/π). Senter i modellmeter via transformen i `kilder/flyfoto-google-2026-10-23.json` (0,39 m/px). Bakkehøyde fra `landskap.terreng` (samme interpolasjon som `08_festningsterrenget.js`); 479 kroner står på voll (> 1 m).
5. **Filter**: hus (`bygg.json`, +1 m), kjørevei (`landskap.veier`, k = kjore, 0,8 × bredde) og vann. Punkt som ligger inntil 2,5–3 m inne flyttes 1 m utenfor kanten (103 flyttet, sikkerhet −0,1); lenger inne forkastes.
   **Merk:** `vann.json` fra OSM dekker hele vollgravsonen med banker, så 300 ekte kroner langs vollgraven ville forsvunnet. Vann er derfor lest fra fotoet (blått, glatt) i stedet.
6. **Høyde**: solretning og skyggelengde målt fra 222 hus i Gamlebyen med kjent `h`: skyggen faller mot nordøst (bildevinkel 307°), median skyggelengde 0,9 m per m høyde ⇒ sol ca. 48° over horisonten (sommer, ettermiddag). Spredningen hus for hus var stor (0,25–3,0), så tallet er grovt.
   For hvert tre følges skyggeretningen fra kronekanten; der skyggen lander på åpen bakke (ikke annen krone, hus eller vann) regnes høyden ut (H = (L − r/sin e)·tan e + r). Det lyktes for 109 kroner (83 innenfor rimelighet 0,6–2,2 D), og de ga **lavere** høyder enn diameterregelen (median 5,8 m mot 9,0 m) med svak samvariasjon. Skyggemålet er derfor bare blandet 50/50 inn for disse 83; alle andre har **H = 1,2 × D** (løvtrær, antakelsen i oppgaven).
7. **Omregning til `s`**: i `12_trær.js` er kronediameteren ≈ 2,3·s (sideklaser på 0,58·s + radius 0,57·s) og kronetoppen ≈ 2,4·s (toppklase på 1,95·s + radius 0,47·s). Én `s` kan ikke treffe både D og H, så s = (D/2,3 + H/2,4)/2, klemt til 1,6–7,5. Med H = 1,2·D blir s ≈ 0,47·D.

## Fordeling

| | 5 % | 25 % | median | 75 % | 95 % |
|---|---|---|---|---|---|
| Kronediameter D (m) | 3,8 | 6,5 | 7,7 | 8,1 | 9,9 |
| Anslått høyde H (m) | 4,6 | 7,7 | 9,2 | 9,8 | 11,8 |
| s | 1,8 | 3,1 | 3,6 | 3,8 | 4,6 |

Høyde i klasser: 3–6 m: 178 · 6–9 m: 469 · 9–12 m: 740 · over 12 m: 64. Dagens `s` ligger på 3,1–4,4 (snitt 3,75), så forslaget gir
samme skala i modellen, med flere små trær (hager, unge trær) og noen større.
Fordelingen er smal fordi k-means deler tette felt i like store biter; de ekte kjempene på vollene (15–20 m kroner) er antakelig delt i to–tre.

## Sammenligning med dagens traer.json (50 m-ruter, innenfor fotoet)

143 ruter har trær i én av kildene. I 46 ruter har dagens data ≥ 10 flere punkter enn fotoet viser kroner, i 19 ruter ≥ 10 færre.

For mange i dag (rute x/y i meter, dagens → forslag):
- 150–200 / −50–0 (østvollen sør for Vindebroen): 83 → 19
- 100–150 / 250–300 (nordvollen): 84 → 21
- 250–300 / 150–200 (nordøst-bastionen): 72 → 25
- 50–100 / −200–−150 (sør for Tøihuset): 57 → 12
- 50–100 / 200–250: 42 → 6, 0–50 / −200–−150: 43 → 8, −200–−150 / −200–−150 (Toldbodgaten sør): 51 → 16

For få i dag (0 eller nesten 0 punkter der fotoet har trær):
- 200–250 / −200–−150, 100–150 / −250–−200, 150–200 / −200–−150: 19–25 kroner hver – trerekkene langs General Ohmes vei / sørøst for vollgraven
- 300–450 / 0–200 (utsiden av østvollen, jordene og gravlunden mot Torsnesveien): 18–26 kroner per rute
- −100–−50 / 50–100 (Kommandantgården-kvartalet): 13 → 0

De tre første punktene er «randomplasseringen» Vegar så: punkter spredt ut på plen der det ikke står trær (gresset øst for Vindebroen,
glaciset) og tette klumper der trykket har én bred krone.

## Hva som ikke er dekket

- Fotoet dekker modell-x −256…439, y −262…319. **Isegran er ikke med**, og heller ikke sørvollene sør for y ≈ −250 og vestbredden.
  Der er dagens 365 punkter beholdt uendret, med sikkerhet 0,2, så fila kan brukes som den er. Nytt flyfoto over Isegran og sør gir resten.
- Trær utenfor vollene (øst, mot Torsnesveien og boligfeltet) er tatt med fordi fotoet dekker dem; om modellen skal stoppe ved vollgraven, filtrer på x > ~330 og y < −120.

## Usikkert

- **Posisjon i tette rekker** (830 kroner): k-means gir jevn avstand, ikke de ekte stammene. Feil på 2–4 m må påregnes. Grønn/gul i kontrollarket skiller disse.
- **Høyde**: diameterregelen 1,2·D er en antakelse; skyggemålet ga lavere tall (medianen 5,8 m) men er støyete (skygge på gress er ikke mørk nok til terskelen, og solhøyden er grovt målt). Ingen tre er satt under 3 m.
- **Store felt som ikke er trær**: kornete eng på glaciset og skyggekanter på plen kan gi falske kroner (sikkerhet ≤ 0,6 når feltet er lyst eller lite kompakt). Mest utsatt: bankene rundt vollgraven og jordene øst.
- **Små busker/hekker** (< 6 m²) er tatt ut; hekker på 2–3 m bredde kan likevel ha sluppet inn som «trær» med D 3–4 m.
- **Transformen** er oppgitt med ca. 3 m feil fra origo; alle posisjoner arver den.
- Google-overlegget (etiketter, nåler, hvit søm) ligger i fotoet; grønne nåler er flate og uten tekstur og falt derfor ut av kronemasken, men to–tre kan ha overlevd som små kroner nær etikettene.

## Neste steg hvis forslaget skal inn

1. Se kontrollarket; stryk eller flytt det som er galt i de gule områdene.
2. `cp rapport/traer-flyfoto.json data/traer.json` – femte felt (sikkerhet) ignoreres av `12_trær.js`.
3. Vurder å lage en regel `09_traer_i_foto.py` i `regler/` som sjekker hvert tre mot kronemasken fra fotoet, slik regel 01 gjør for hus.
