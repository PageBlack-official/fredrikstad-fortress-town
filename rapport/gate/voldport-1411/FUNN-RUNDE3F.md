# FUNN — Voldportgaten runde 3f (siste rettrunde) — 15.11, PAG-1601

Gren `gate/voldport-1411`. Oppskrift: `RUNDE3F.md` (Fable 15.11 00:50). **Ikke publisert.**

Denne runden ble kjørt av to Studio-heartbeats. Første heartbeat la data-delen av pkt 3 (dør-/port-farge) og
committa 03930c7 + FUNN-stubb 09c774f, men uten motor-fiksen karmen faktisk krevde, og avsluttet. Denne
heartbeaten (eier etterpå) fullførte pkt 1, 2 og motor-delen av pkt 3, bygde og **verifiserte mot render**.
Lest på nytt fra `r3e/montasje-75-vegg4-3e.jpg`, ikke fra rutenett-skuddet alene.

## 1. 75 vegg4, 1. etg — rekkefølge og bredde rettet mot montasjen

Montasjen (SV mai 2024, standpunkt 928-4f) leser fra venstre: **dør (brun, ytterst) · butikkvindu (Gamlebyen)
· dør m/steintrapp · butikkvindu (Gamlebyen Elektriske AS) · nedløpsrør · butikkvindu (Emm K) · dør m/steintrapp
· butikkvindu (Emm K) · port (brun, høyre kant)**.

Renderen hadde `butikk–dør–butikk–butikk–dør–butikk–dør` (7 kjerneelementer). Målt mot montasjen (piksel→s via
den bygde modellen, `x_render ≈ 46·s − 395`, verifisert på dør G: SV x530 → s20,1 = modellens dør s19,5–20,5)
stemte B–H allerede. To feil stod igjen, nå rettet i `kilder/gate/rett-v4-kjerne.json`:

- **Dør A (brun, ytterst) manglet i synsfeltet.** Den lå på s8,0–9,0 og falt utenfor venstre bildekant
  (x≈−4). Flyttet til **s8,6–9,8** (SV-senter x30 → s9,2) så den leses ytterst til venstre, som i SV.
- **Siste element skal være port, ikke dør.** `dor s23,4–24,2` → **`port` s23,3–24,8** (brun, z1 2,7).
  Den flaggede Voldgaten-butikken s24,49 nudget til s24,9 for å klarere porten.

Render 3f leser nå `dør–butikk–dør–butikk–butikk–dør–butikk–port` — samme rekkefølge som SV.

## 2. 75 vegg4, 2. etg — 6 → 7 vinduer med ujevn avstand

SV viser **7 vinduer** i synsfeltet med stor luke mellom 4. og 5. fra venstre (ved nedløpsrøret). Renderen
hadde 6 (jevnere rytme). Pane-deteksjon på SV (blå−rød) ga 7 vindussentre; omregnet til s og lagt inn:

| vindu | W0 | W1 | W2 | W3 | W4 | — luke — | W5 | W6 |
|---|---|---|---|---|---|---|---|---|
| s-senter | 8,9 | 13,0 | 14,7 | 16,6 | 18,2 | | 21,1 | 24,35 |

Luka W4→W5 (≈2,9 m) er større enn de andre (≈1,6–2,1 m). Render 3f: pane-deteksjon finner **14 paner = 7
vinduer** (T-post, to paner hver), stor luke mellom nr. 4 og 5. Hvite T-post (spross 2) med mørkebrun foring.

## 3. Brune dørkarmer på 75 (begge vegger) — opt-in som foringen

SV har mørkebrune dører **og karmer**; renderen tegnet hvite karmer. Første heartbeat satte `farge:#4a342c`
på dørene (det farger **dørbladet** brunt), men karmen forble hvit — fordi `src/07` gatet karm-/foring-
omfargingen (linje 48–49) til `typ<0.5 || typ>2.5` (vindu/oksøye). Dører (typ 1) og porter (typ 2, flat =
typ 1 i motoren) falt utenfor og beholdt den hvite standardkarmen. Motor-fiks var nødvendig.

**Rettelse (`src/07_vinduer-dører-og-porter.js`, dørgreina):**
```
if(foring>0.5 && bue<1.5) hvit=mix(pf*0.52, pf*0.82*sf, lit);   // brun dørkarm (opt-in som foringen)
```
Karmen fargelegges i elementets egen farge når foring-flagget (+1000) er satt — nøyaktig samme opt-in som
vindusforingen. `bue<1.5` holder Kaserna-fløydøra (bue 2) utenfor. Dørene på 75 har `farge:#4a342c`
(vegg4-kjernen + begge vegg5-dørene fra 03930c7, resten av vegg4 lagt til her), så de får nå brun karm.

Verifisert i render 3f: alle dører/porter på vegg4 (928-4f) **og** vegg5 (928-5f) har brun karm.

## 4. Verifikasjon
- `verktoy/last-test.mjs` → `lastet: true feil: []` (shader kompilerer).
- `verktoy/rett/speil_sjekk.py` → **grønn** (exit 0): Majoren-porten på utsidens høyre halvdel, 3 vegger normalisert.
- `eslint` på `src/07` → ren.
- Montasje: `rapport/gate/voldport-1411/r3f/montasje-75-vegg4-3f.jpg` (SV | render, hele veggen).

## Endrede filer
- `kilder/gate/rett-v4-kjerne.json` — 1.etg rekkefølge (dør A + port I), 2.etg 7 vinduer, brune karmer, ny telling.
- `src/07_vinduer-dører-og-porter.js` — brun dørkarm opt-in (foring-flagg), 1 linje.
- `rapport/gate/voldport-1411/r3f/` — render 928-4f/928-5f + montasje + denne FUNN.
- (fra 03930c7, 1. heartbeat) `kilder/gate/rett-voldport-1411.json` + rett-v4-kjerne dør-farger.

## Forbehold
- SV-skuddene har pitch 95–97 (ser opp mot takfoten); gatekameraet står på pitch 88,4 — samme standpunkt/retning,
  litt lavere blikk (uendret fra 3e).
- Voldgaten-enden s24–33,5 er fortsatt flagget (rødt nabobygg okkluderer frontalt), dagens data.
