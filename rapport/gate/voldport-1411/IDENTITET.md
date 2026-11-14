# IDENTITET — Voldportgaten 71/73 (bnr 258 / 944 / 622)

**Sak:** PAG-1591. Rotårsak funnet i CEO-jury på PAG-1590: «71 Therese M» i modellen
er bygget på **bnr-193868258**, men registrene sier det er feil hus.
**Status:** Verifisering ferdig. Ingen bygging/omkasting gjort. **IKKE publisert.**
Worktree `~/sot-maskin/voldport`, gren `gate/voldport-1411`, commit 8d35ee2.

---

## Dom per bygg

| bnr | Matrikkel-adr | Modellen i dag | **Riktig identitet (dom)** | Sikkerhet |
|-----|---------------|----------------|----------------------------|-----------|
| **193868258** | Voldportgaten 71 | «Therese M» (appearance + merknad 14.11) | **Råde Bakeri Utsalg / Gamlebyen konditori** | Høy |
| **193867944** | Voldportgaten 73 | navnløs, `fasade_kilde=antatt` (placeholder) | **Therese M** (+ Du og jeg pappa) | Høy |
| **193868622** | Voldportgaten 73 | «Majorens Kro & Stue» | **Majorens Kro og Stue** | Høy — ingen endring |

Kort sagt: modellen har byttet om på **258** og **944**. Majoren (**622**) er riktig.

---

## Hvor kildene er enige / spriker

Fire uavhengige signaler på **bnr-193868258** — alle sier *bakeri/butikk*, ingen sier Therese M:

| Signal | bnr-193868258 | bnr-193867944 | bnr-193868622 |
|--------|---------------|---------------|---------------|
| **Enhetsregisteret** (Brreg, org→bygg) | Råde Bakeri Utsalg, 23 ansatte | — | Major-Stuen AS, 27 ansatte |
| **OSM** (navngitt node) | «Gamlebyen konditori» (n372716527) | **«Therese M» (n10101040656), therese-m.no** | — |
| **SEFRAK bygningstype** | butikkbygning | restaurantbygning/kafé | restaurantbygning/kafé |
| **Matrikkel-adresse** (upålitelig) | Voldportgaten 71 | Voldportgaten 73 | Voldportgaten 73 |

### Geometri — det avgjørende signalet (punkt-i-polygon mot `data/bygg.json`)

OSM-nodene er plassert på selve butikkfasaden. Testet mot modellhusenes omriss:

| POI-node | koord (x,y) | Faller inne i | Avstand til nest nærmeste |
|----------|-------------|---------------|---------------------------|
| **Therese M** (therese-m.no, OSM) | 128.0, 66.3 | **bnr-193867944** (8.8 m til senter) | 19.2 m (622), 24.3 m (258) |
| Gamlebyen konditori (OSM) | 115.8, 71.5 | **bnr-193868258** | — |
| Du og jeg pappa (OSM) | 120.6, 58.4 | **bnr-193867944** | — |
| Råde Bakeri (Vegar/Brreg) | 107.9, 69.0 | **bnr-193868258** | — |
| Majorens Kro (Vegar/Brreg) | 138.2, 45.1 | **bnr-193868622** | — |

Therese M-noden ligger **24 m fra bnr-258** og landet rett inne i **bnr-944**.
Geometrien alene flytter Therese M fra 258 til 944.

Rekkefølge oppover gata (senter-x): **258 (#71)** → **944 (#73)** → **622 (#73, Majoren)** → 928 (#75).

### Hvor det spriker
- **Vegars merknad 14.11.2026** (Street View mai 2024, hans 9 bilder; Fable koordinerte):
  *«Therese M (Voldportgaten 71): én etasje, hvit mur, eget lavere valmtak takstein.
  Butikkvinduer med rundbuet topp…»* — denne knytter navnet **Therese M til #71 = bnr-258**.
  Dette er **eneste** kilde som plasserer Therese M på 258, og er rotårsaken til feilen.
- **Brreg** adresse-registrerer også en «Therse M» (org-996364380, **0 ansatte**) på
  **bnr-193868622** (Majoren). Dette er en ren adresse-registrering uten fysisk butikk
  (0 ansatte) og overstyres av OSM-noden med koordinat + nettside på 944.

### Viktig — det interne selvmotsigelsen
`data/steder.json` (POI/navnelaget) har **allerede riktig kobling**:
`pb-980959775 Råde Bakeri → bnr-193868258` og `osm-...656 Therese M → bnr-193867944`.
Feilen sitter altså **ikke** i POI-laget, men i **appearance-arbeidet**: den hvite
1-etasjes fasaden med rundbuede butikkvinduer og valmtak (`vegg [236,236,231]`,
`h/th`, `vind`, `navn:"Therese M"`) ble lagt på **bnr-193868258** via merknaden,
mens ekte Therese M (**bnr-193867944**) står igjen med `fasade_kilde=antatt` (placeholder).
Dette er «riktig fasit, feil hus»: fasaden er en trofast gjengivelse av det Vegar så,
men festet til feil bnr.

---

## Punkt 3 — huset vises i renderne det påstås å være i
Bnr-193868258 (modellens «71 Therese M») ligger i `synlige_hus` i alle fire
publiserings-kandidatene (`mot-therese-m`, `langs-voldportgaten-mot-majoren`,
`kryss-voldportgaten-voldgaten`, `voldgaten-mot-75-kortside`), med `navn:"Therese M"`
frosset inn. bnr-193867944 er med i samme liste, men `navn:null`.
Feilidentiteten er altså synlig i selve renderne → **må ikke publiseres**.

---

## Hva gjenstår usikkert
- **Hvilken fysisk fasade Vegars 9 bilder faktisk viser.** Registrene + geometri er
  entydige på *navn↔bnr*. Men hvis Therese M nylig har flyttet inn i #71-bygget
  (butikker flytter; OSM/Brreg kan være etterslep), kan Vegars øyne ha rett og
  registrene være utdaterte. Derfor må **Vegar bekrefte bnr, ikke bare navn**,
  før noen omkasting bygges.

## Anbefalt retting (bygges IKKE nå — venter på Vegars bnr-bekreftelse)
1. Flytt Therese M-appearancen (hvit mur, valmtak, rundbuede butikkvinduer, `h≈4,2`,
   `navn`) fra **bnr-193868258** → **bnr-193867944**.
2. Gi **bnr-193868258** sin egen identitet: **Råde Bakeri / Gamlebyen konditori**
   (bakeri-/konditorifasade, Voldportgaten 71).
3. `data/steder.json` er allerede riktig — ingen endring der.
4. Regenerer de fire gate-renderne etter omkastingen.
- **Ingen id-er slettes** (regel 14/20) — rettingen er `op:sett`-reassignment av
  appearance-felt, ikke id-retirering. Både 258 og 944 beholder id.
- **Kostnad:** én render-runde.
- **«La det stå» som reelt alternativ:** modellen viser da Therese M der bakeriet
  faktisk er, og ekte Therese M-bygget (944) blir stående som udetaljert placeholder
  med feil høyde. Det er en synlig faktafeil i en publisert gate — frarådes.
