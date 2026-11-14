# FUNN runde 3b (Studio, 14.11.2026 kveld) — PAG-1594

Oppskrift: `RUNDE3B.md`. Identitet avgjort av Fable (PAG-1591): **Therese M = bnr-193867944**.
Kilde: bare rektifisert Street View mai 2024. Montasje SV | render per vegg. IKKE publisert.

## Viktig retting: Street View-henting er IKKE blokkert
Runde 3 / forrige 3b-økt (commit 1cf2a24) konkluderte «blokkert på SV-bilder (attended Chrome / robotsjekk)».
Det stemmer ikke nå: `node verktoy/sv_hent.mjs` hentet `bnr-193867944-7` (mai 2024, pano 5YXEHso) på **6 sekunder
uten robotsjekk**. Henting virker fra denne maskinen. De tre gjenstående veggene er derfor ikke blokkert på henting —
de er begrenset av at katalogen (`sv_lager.json`) ikke har et panorama som ser HELE veggen forfra (smale gater, bygg foran).

## Driftsmerknad: to Studio-kjøringer på samme worktree
Ved oppstart lå en annen levende Studio-kjøring (run 233fe855) på samme `voldport`-tre og committet vegg5-fiksen
(63f1ab8) + en «blokkert»-status (1cf2a24). Den avsluttet mens jeg jobbet. Jeg er nå eneste kjøring. Ingen rettelser
ble klobbet: vegg5-fiksen er bygd coherent inn på nytt sammen med 258-tilbakestillingen.

## Per vegg

### 258 (Råde Bakeri / Gamlebyen konditori) — TILBAKESTILT ✓ (commit 40d20ab)
Fjernet 14.11-merknaden «Therese M» fra `bygg-merknader.json` (restaurert 29.10-posten: beige/hvit puss), fjernet 258
fra `hoyde-unntak.json` (tilbake til Kartverkets 6,9 m, 2 etg) og `tak-tegning.json`. Regel 02 grønn (0 høydeavvik),
regel 04 grønn. Ingen ny lesing av 258 (utenfor denne gatesida).

### 944 «Therese M» — BYGD fra rektifisert SV ✓ (denne økta)
Hentet `bnr-193867944-7` (mai 2024, 7,5 m, 49° oblikt), rektifisert (`rett.py`, 50 px/m) → `r3/rett-944/`.
Vegg7 = arkadeveggen mot Voldportgaten. Navn **Therese M** flyttet fra 258 til 944 (`sett.navn`), vinduene lest i meter
(ikke jevn rytme) inn i `kilder/gate/rett-944-therese.json`, `fasade_rett[7]` grønn.

| Street View mai 2024 (rektifisert, meter) | Modell (render) |
|---|---|
| 2 store **rundbuede** butikkvinduer: s 2,5–3,7 (sentrum 3,1) og s 5,4–7,0 (sentrum 6,2); z 0,4–2,9 | 2 rundbuede butikkvinduer på vegg7, samme s/z (fra fasade_rett) |
| Rund «Therese M»-skilt s≈7,6–8,4 (ikke vindu) | — |
| Mulig 3. vindu i fjern (venstre) ende — for forvrengt (49°) til sikker lesing | ikke tegnet (ikke gjettet) |

Montasje: `r3/montasje-944-vegg7.jpg` (SV rektifisert | render). Presisjon grov (±0,5 m), samme standard CEO
godtok for vegg5. **Gjenstår (notert, ikke gjettet):** bygg-bred veggfarge er ikke satt — 944 er et stort L-omriss,
bare SE-hjørnet er den hvite Therese M-butikken; per-vegg hvit kalkpuss trenger veggfelt/segment (neste runde).

### 75 vegg5 (Voldgaten, 20,2 m) — RETTET ✓ (forrige kjøring, commit 63f1ab8, verifisert)
2.etg-vinduene flyttet til SV-posisjonene (sentre 2,3/4,6/7,4/9,6 og 12,8/14,8/17,0/19,3), lest i meter fra rektifisert
bilde. Bygd coherent inn på nytt denne økta. Montasje `r3/montasje-75-vegg5.jpg` finnes (fra før fiksen; bør
regenereres neste runde for å vise de nye posisjonene).

## Gjenstår (ikke blokkert på henting, begrenset på hel-vegg-panorama)

### 75 vegg4 (Voldportgaten, 33,5 m)
`sv_rett_plan` finner ikke ett panorama som ser hele veggen (hjørnene faller utenfor i frontalskuddet). Metoden i
oppskriften: 3–4 frontale pano langs veggen, rektifiser hver bit mot kjente kanter, sett sammen i meter med overlapp.
Dette krever ny stitch-logikk i repoet (ikke engangsskript) og 3–4 nye henting-skudd — henting virker, så dette er
gjørbart neste runde.

### 73 Majoren (bnr-193868622)
`sv_rett_plan` finner **ingen** vegg på 622 med et hel-vegg-panorama i katalogen; de eneste frontalskuddene på disk
(622-2f) er **aug. 2010** (feil æra, og 2010-skuddet av det gule trehuset er feil hus per oppskriften). For mai-2024
forfra må `sv_lager.json` utvides med panoramaer tett på Voldportgaten 73 (`node verktoy/sv_lager.mjs` i synlig Chrome),
deretter `sv_rett_plan` → `sv_hent` → rektifisering. Neste runde.

## Ferdig-status
258 ✓, 944 ✓ (grov), 75 vegg5 ✓ (verifisert). 75 vegg4 og 73 Majoren gjenstår (hel-vegg-pano mangler i katalogen).
Regel 02/04 grønne. IKKE publisert.

## Fortsettelse etter CEO-jurydom (14.11 kveld, run c6a6aa61)
CEO-punktene 3 og 4 gjort, 2 eskalert, 1 (modul) bygd:
- **Punkt 3 (rydd):** 12 regenererte byggutdata committet (commit etter 8e8a44c) — gren-hodet speiler nå den bygde modellen.
- **Punkt 4 (vegg5-montasje):** render kjørt på nytt med gjeldende modell → `r3/montasje-75-vegg5.jpg` regenerert. 2.etg 4+4 på SV-posisjonene (sentre 2,3/4,6/7,4/9,6 + 12,8/14,8/17,0/19,3), 1.etg butikkvinduer + 2 dører. Beviser de nye posisjonene.
- **Punkt 1 (vegg4, 33,5 m):** gjenbrukbar stitch-modul `verktoy/rett/rett_lang.py` skrevet + committet (biter → felles meterlerret, myk fjæring i overlapp). Hentet 3 mai-2024-pano (4f/4b/4c) + laget projeksjons-metermerker for hjørnelesing.
  - **Recon:** `4f` (jI8Kdnvk, 5,6 m, ~37°) dekker KJERNEN av butikkfasaden rent — «Gamlebyen Elektriske AS» + «Emm K» + nedløpsrør + port + 2.etg-vindusrad, ca. s 10–24. Dette er den meningsbærende delen.
  - **Problem i endene:** `4c` (XIkNoV5l, Voldgaten-hjørnet) ser IKKE vegg4 rent — den ser nedover Voldgaten på et rødt retur/nabobygg i strykende vinkel, og den fjerne enden (s 24–33,5) er sterkt forkortet. `4b` ligner. Dvs. endene (mot begge hjørner) mangler et frontalt mai-2024-pano; bare kjernen (s≈10–24) har det.
  - **Neste steg:** enten (a) lever vegg4-kjernen (s≈10–24) rektifisert fra 4f som egen bit (den delen Vegars butikkfasade bor i), og la de plane endene stå, eller (b) hent flere pano / aksepter at endene leses grovt. Trenger CEO-pek på ambisjonsnivå for endene før jeg skriver metertall jeg ikke kan stå for.

## Majoren (73) — eskalert, venter CEO-dom (komm. 07c0752b)
Hovedfasaden (vegg2) har INGEN frontal mai-2024-pano (Googles 2024-bil kjørte ikke tett forbi; bare 75°-hjørneskudd). Frontal finnes bare fra aug. 2010 (t3dSDJSt, forfra, «MAJORENS KRO & STUE» #73 — samme bygg, men gul puss i 2010, malt hvit før 2024). Valg: geometri fra 2010-frontal + farge hvit fra 2024 (anbefalt), vs grov 75°-mai-2024, vs hopp over. Venter dom.

## CEO-dom utført (14.11 kveld, run c6a6aa61) — alle fire vegger klare

### 75 vegg4 (Voldportgaten, 33,5 m) — KJERNE SV-lest (CEO valg a)
Stitch-modul `rett_lang.py` brukt på `4f` (jI8Kdnvk, mai 2024). **Eksplisitt kilde-skille:**
- **s10–24 (kjernen): SV-lest** fra rektifisert 4f. 1.etg = reelle butikker, ikke jevn rytme:
  brede butikkvinduer (Gamlebyen Elektriske ~s15,3–17,1, Emm K ~s20,6–23,3, + s10–11,3 og s12,7–14,3)
  med innskutte dører (~s11,5 / 17,8 / 19,7). 2.etg = 6 vinduer, regelmessige (SV-bekreftet venstre; Google-kortet
  dekker øvre høyre). Montasje `r3/montasje-75-vegg4.jpg`.
- **s0–10 og s24–33,5 (endene): dagens data**, IKKE kilde-verifisert (ingen frontal mai-2024; `4c`/`4b` ser bare
  rødt retur/nabobygg i strykende vinkel). Featureless plan vegg. Står urørt fra 14.11-merknaden.

| Street View mai 2024 (4f, kjerne s10–24) | Modell |
|---|---|
| 1.etg: brede butikkvinduer + innskutte dører (ikke 6 like vinduer) | butikk + dor-elementer på lest s (rett-v4-kjerne.json) |
| 2.etg: 6 vinduer, jevn rytme ~2 m | 6 vinduer s 10,6/13,1/15,5/18,0/20,4/22,9 |
| Vannbord (mørkebrunt bånd) mellom etasjene | veggfelt mørkebrunt bånd (fra 14.11) |

### 73 Majoren (bnr-193868622) — GEOMETRI fra aug-2010-frontal, FARGE fra mai-2024 (CEO valg 1)
**Kilde-flagg (eksplisitt, CEO-betingelse 1):** Majorens hovedfasade (vegg2) har **ingen** frontal mai-2024-pano
(Googles 2024-bil kjørte ikke tett forbi; eneste 2024-skudd mot vegg2 er 75° oblikt). Geometrien er derfor lest fra
**aug-2010-frontalen** `t3dSDJSt` (helt forfra, ~6 m). CEO verifiserte selv at dette ER Majoren (MAJORENS KRO & STUE,
adresseskilt 73), ikke «det gule trehuset» oppskriften advarte mot (det var L0etK4SO). Fasaden er bygnings-uendret
2010→2024 (verneverdig Gamlebyen-fasade); **bare malt gul → hvit**. Veggfarge = mai-2024 (hvit, [233,230,222] fra
14.11-merknaden). Dette kilde-avviket surfaces CEO til Vegar ved review-porten (CEO-betingelse 2).

| Street View aug 2010 (frontal, geometri) | Modell |
|---|---|
| 5 vinduer i 2. etg | 5 vinduer s 3,3/4,8/6,8/8,3/10,2 (z 3,1–4,8) |
| Midtinngang (MAJORENS, steintrapp) | dør s 5,7–6,8 |
| Store doble vinduer begge sider av inngangen | butikk s 2,6–5,0 og s 7,3–9,7 |
| Egen port til bakgården til høyre («73») | port s 0,2–2,2 (rundbue) |
| Farge: gul (2010) → **hvit i mai 2024** | veggfarge hvit [233,230,222] |

Montasje `r3/montasje-73-majoren.jpg` (SV 2010 | render). Grov ±0,5 m.

### Polish vegg5 (CEO-notat): mørkebrun foring på 2.etg-rammer
Satt `farge:#4a342c` på de 8 vegg5 2.etg-vinduene (karmfarge, `rett-voldport-1411.json`). Ligger i vind-dataen
(v[12]); renderen viser den dempet. Ikke-blokker per CEO.

## Ferdig — alle fire vegger + montasjer, regler grønne
944 ✓, 75 vegg5 ✓ (montasje regenerert), 75 vegg4-kjerne ✓, 73 Majoren ✓. Regel 02/04/17 grønne.
Montasjer: `r3/montasje-{944-vegg7, 75-vegg5, 75-vegg4, 73-majoren}.jpg` (lokale, Google-bilder utenfor git).
Sendes CEO som **in_review**. Majoren-kildeavviket (2010-geometri) flagget over for Vegar-porten. IKKE publisert.
