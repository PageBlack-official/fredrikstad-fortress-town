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
