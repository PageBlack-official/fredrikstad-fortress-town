# FUNN — Voldportgaten runde 3e (speilvendt fasade, 6-vs-8, montasjer) — 14.11

Gren `gate/voldport-1411`, etter 6aa46e6. Bare data + verktøy, ingen `src/`. **Ikke publisert.**

## 1. Speilvendt Majoren — årsak funnet i koden, ikke speilet for hånd

**Symptom:** `montasje-73-majoren-3d.jpg` leste port-butikk-dør-vindu fra venstre; Street View leser
vindu-dør-butikk-port. Fasaden var speilvendt om s-aksen.

**Årsak (`verktoy/fasade_rett.py`):** s leses fra bildets venstre (veggen sett forfra fra utsiden). Koden
plasserte elementet på `venstre + u·s` med `u = (hoyre − venstre)`. For at s skal vokse mot bildets høyre må
leseretningen `u` og veggens utovernormal `n` danne en høyrehåndsramme: `(n × u)_z > 0`. Når `venstre`/`hoyre`
i en rett-fil står i motsatt rekkefølge av det kameraet så, blir `(n × u)_z < 0`, s vokser høyre→venstre, og
hele veggen speiles. Majoren hadde `venstre=[137.84,65.36]`, `hoyre=[149.02,60.37]` → `(n × u)_z = −1`.

**Rettelse:** `fasade_rett` normaliserer nå leseretningen — er `(n × u)_z < 0`, måles s fra det hjørnet som
faktisk er utsidens venstre (`a, u = c, −u`). Facing-normalen var alltid riktig (utover fra `vegger.py`);
bare *hvor* langs veggen senteret havnet var speilet. De 88 veggene som alt lå rett (`(n × u)_z = +1`) røres
ikke; de 3 bakvendte rettes.

Verifisert i bygd modell: Majoren-portrommet (b=3,3 m) sto på skjerm-x **−4,0** (venstre) før fiks, **+4,0**
(høyre) etter — samme side som SV. Det brede venstrevinduet står nå til venstre.

## 2. Regel/test — `verktoy/rett/speil_sjekk.py`

Hard sjekk mot **fasit fra Street View**, lest ut av den **bygde** modellen (ikke en gjenbruk av fiksens egen
regnemåte, så den er ikke sirkulær): Majoren-porten er helt til høyre i SV → portrommet (bredeste åpning på
vegg 2) MÅ ligge på utsidens høyre halvdel. I tillegg en opplysende skanning av hvilke godkjente rett-vegger
som er bakvendt-authored i rådata (normaliseres av fasade_rett). **Bevist at den fanger feilen:** uten fiksen
havner porten på skjerm-x −4,0 (test FEILER), med fiksen +4,0 (test PASSER).

## 3. Alle fire vegger (+ hele banken) sjekket

Av 91 godkjente rett-vegger var **3 bakvendt-authored** (`(n × u)_z = −1`), nå normalisert av fiksen:

| vegg | fil | status |
|---|---|---|
| 73 Majoren v2 (bnr-193868622) | rett-majoren | var SPEILVENDT → rettet |
| 75 vegg4 (bnr-193867928) | rett-v4-kjerne | var SPEILVENDT → rettet |
| dom-nr5 v2 (bnr-193972292) | rett-dom-nr5 | var bakvendt (eldre) → rettet |
| 75 vegg5 (bnr-193867928) | rett-voldport-1411 | var riktig (+1) |
| 944 vegg7 (bnr-193867944) | rett-944-therese | var riktig (+1) |

## 4. Montasjer fra samme standpunkt og retning som SV

`rapport/gate/voldport-1411/r3e/montasje-{73-majoren,75-vegg4,75-vegg5,944-vegg7}-3e.jpg`: SV | render, der
renderen er tatt med gatekameraet fra **SV-kameraets lat/lon/heading/fov** (1280×720), ikke hjørneperspektiv,
så de kan legges side om side. **Forbehold:** SV-skuddene har pitch 95–97 (ser opp mot takfoten); gatekameraet
kan ikke tegne pitch > 88,5, så renderen står på pitch 88,4 — samme standpunkt og retning, litt lavere blikk.

## 5. 6-vs-8 (FUNN-RUNDE4)

- **Voldgaten-veggen** på bnr-193867928 er **vegg 5** (SØ-normal, L=20,2 m, fri mot gata) — ikke den lange
  vegg 4 (NØ, 33,5 m, mot Voldportgaten).
- SV viser **8 vinduer i 2. etg som tospeils** på nettopp vegg 5. Spross 3 (tospeils) + foring lå feilaktig på
  **6** vinduer på vegg 4 (som i egen lesing er **T-post**, ikke tospeils).
- Rettet: `fasade_rett` fikk støtte for per-element `spross` (additivt). `rett-voldport-1411` v5 → `spross:3`
  på de 8 tospeils-vinduene (hadde foring alt). `rett-v4-kjerne` v4 → `spross:2` (T-post) på 2.etg. Bygd modell:
  vegg5 = 8 tospeils, vegg4 2.etg = T-post. src/07 hadde alt `spross>2.5` (tospeils) og foring (+1000).

## 6. Veggfarge 75

`kilder/bygg-merknader.json` bnr-193867928 `sett.vegg` = **[164,155,156]** (varm grå fra 3d-målingen vegg4 sol).
Motoren er rettet, så fargen kan stå.

## Endrede filer
- `verktoy/fasade_rett.py` — s-akse normalisert mot utovernormal; per-element `spross`.
- `verktoy/rett/speil_sjekk.py` — ny test.
- `kilder/gate/rett-majoren.json` — bredt venstrevindu (pkt 3), telling.
- `kilder/gate/rett-voldport-1411.json`, `rett-v4-kjerne.json` — spross 3/2.
- `kilder/bygg-merknader.json` — veggfarge 75.
- `rapport/gate/voldport-1411/r3e/` — montasjer + denne FUNN.
