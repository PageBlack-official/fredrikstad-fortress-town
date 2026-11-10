# RAPPORT — Hurtigsporet /rask (PAG-1504)

Vegar 10.11 08:40: «Hurtigspor først». Han vil dømme et hus, få det rettet og se endringen raskt — ikke vente timer
på full kjede + ~45 regler + publiser.sh. Dette er den raske veien ut, ved siden av /prove og forsiden.

## Flyten (gjelder husrettinger fra nå)

**Vegar dømmer hus → agent retter i kilden → commit → `sh rask.sh` → lenke til huset i saken.**

Agenten jobber i worktreet `~/sot-maskin/gate-rask` (gren `gate/rask`, grenet fra `gate/kamera`). Når huset er rettet
og committet, kjører hen `sh rask.sh` på minien. Under 10 min senere står endringen på
`https://pageblack-official.github.io/fredrikstad-fortress-town/rask/`, og lenka `rask/?hus=<bnr>` flyr kameraet rett til huset.
Den lenka limes inn i saken der huset ble dømt.

## Hva rask.sh gjør (og ikke gjør)

1. **Krever committet kilde.** Hjørnestemplet viser kilde-commit; urettede endringer ville gjort stemplet til en løgn, så scriptet stopper på dem.
2. **Diff mot forrige /rask-bygg** (`rapport/rask-sist.txt`) sier hvilke hus (bnr) som endret seg, fra `data/bygg.json`. Artefaktet
   er ett samlet bygg (enkel), så selve HTML-en kan ikke bygges per hus — diffen brukes til lenka og rapporten. Endres src/datalag/assets
   rammer det alle hus, og da står hus-lista tom (hele byen bygges uansett).
3. **Enkel bygg** (`python3 bygg.py enkel`), ~3–4 s.
4. **Bare de raske vaktreglene** som stopper et ødelagt kart:
   - a) bygger og laster + ingen JS-feil (`verktoy/last-test.mjs`: hodeløs Chromium, `window.__vis` finnes, feil-lista tom)
   - b) regel 48: vinduer ikke oppå hverandre (ren Python; samme regel som sperrer publiser.sh)
   Resten av de ~45 reglene kjøres som før, bare for /prove1 og /prove.
5. **Hjørnestempel + ?hus-sjia** limes inn i rask-kopien (ikke i src/ eller /prove-bygget): `#raskmerke` nederst til høyre med
   kilde-commit + tid, og et inline-skript som gjør `?hus=<bnr>` → `#hus=bnr-<bnr>` før modulen laster.
6. **Publiserer bare mappa rask/** på gh-pages. Vanlig commit oppå `origin/gh-pages`, **aldri force-push** (avvist push → hent gh-pages
   på nytt, legg rask/ oppå igjen, til 5 forsøk). Samme deploy-nøkkel som publiser.sh (remote `pages`, alias `github-sot`).
   **/prove, /prove1, /backup og forsiden røres aldri.**
7. **Venter til /rask/ viser den nye kilden** (meta `kilde` = commit-hash), og måler commit → synlig.

## Målt tid — commit → synlig på /rask (3 forsøk, 10.11.2026)

| Forsøk | Kilde-commit | Hendelse                         | commit → synlig |
|--------|--------------|----------------------------------|-----------------|
| 1      | `2077f37`    | første /rask-bygg (hele byen)    | **67 s**        |
| 2      | `a5c47f8`    | ny commit i kilden               | **174 s**       |
| 3      | `6bc91b8`    | ny commit i kilden               | **61 s**        |

Alle tre godt under målet på 10 min. Flaskehalsen er GitHub Pages' egen bygging/propagering (innholdsuavhengig), ikke vårt bygg
(~3–4 s) eller vaktreglene (~20 s med `PW_GPU=1`, Mac-ens eget skjermkort). De tre målecommittene var loggnotater i `data/logg.json`
(innholdsuavhengig latens); flyten er den samme for en ekte husretting.

## Lenke-eksempel for ett hus

`https://pageblack-official.github.io/fredrikstad-fortress-town/rask/?hus=193870325` → flyr kameraet til **Hovedvakten – det
gamle slaveri** (bnr 193870325) og åpner kortet. Verifisert i hodeløs Chromium (kortet åpnet på Hovedvakten, ingen JS-feil) og
på den live siden. Diff-deteksjonen er verifisert: en endring i ett bygg gir `ENDRET HUS: ['193870325']` og rett lenke.

## Grenser som holdes

- Aldri force-push; aldri /prove, /prove1, /backup eller forsiden. Etter 3 publiseringer har gh-pages fortsatt
  `index.html assets backup data prove prove1 sw.js …` urørt, pluss den nye `rask/`.
- rask.sh genererer ingen mockup/bilde; det bygger bare kartet fra kilden og legger det ut.

## Til CEO

rask.sh ligger på gren `gate/rask`. Flett den inn i `gate/kamera` og si fra til Studio (PAG-1492) at husrettinger fra nå går ut
på /rask først. Oppskriften bør også løftes til `teknisk-veikart`-skillen via den vanlige propose_skills-veien (dagbok → løft).
