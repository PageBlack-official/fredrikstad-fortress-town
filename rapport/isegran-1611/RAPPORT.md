# Isegran 16.11 — utført (Studio)

Worktree ~/sot-maskin/voldport, gren gate/voldport-1411 (= /rask). Tak 90 min: parts 1–3 levert og sett; part 4 + pilastrene gjenstår (se nederst).

## 1. Gangvei-bånd på brygga — GJORT
- Funn bekreftet: `data/veier.json` er rå OSM og bygges **ikke** av noe verktøy. De tegnede båndene kommer fra `data/landskap.json` «veier» (tegnes i `src/08_festningsterrenget.js`), bygd av `verktoy/bakke.py` (`gater`). Regelen er derfor lagt der veibåndene bygges.
- Regel i kjeden: `verktoy/bakke.py gater()` tar nå ut enhver vei (kjøre/gang) som ligger ≥ 50 % av lengden inne i et brygge-omriss (`data/brygger.json`). Gjelder ALLE brygger. 8 veier tatt ut (br-2 ved Isegran + 7 andre brygger på kartet); listet i `rapport/bakke/veier-fjernet.json` med grunn.
- Rød regel: `regler/50_vei_ikke_paa_brygge.py` — rød hvis et tegnet veibånd ligger ≥ 50 % på en brygge. Nå grønn (0 av 414).
- Bevis: før/etter fra samme kamera over br-2 (det grå, hevede båndet med side ned i vannet er borte).

## 2. Isegranhuset bnr-193867464 — GJORT (unntatt pilastre)
- Vegg `#c58c59` = (197,140,89); tak rød takstein NCS S 4050-Y60R ≈ `#9E4E2C` = (158,78,44). Skyggetoner: `veggs`/`taks` = null → byens regel (×0,72/0,80/0,80) deriverer dem. Kilde «Vegar 16.11».
- **Valmtak**: `tak2` regnet på nytt fra fotavtrykket uten gavl (`verktoy/tak.py`, gavl=av) → 4 takflater, `gavl2` tømt, `takform`=valm. Bekreftet i render (hofter på alle sider, ingen gavltrekant).
- **Vinduer vannfasaden**: de 7 jevnt fordelte erstattet med 2 etasjer × 5 vinduer = 10 (hvite, sprosser), på aksene Fable målte i Vegars foto (frac fra østre/venstre hjørne sett fra hagen: 0,195 · 0,580 · 0,808 · 0,856 · 0,953; z = 1,6 og 4,1). De 16 vinduene på de tre andre veggene beholdt. Geometrien validert: aksene faller sammen med de eksisterende SV-vinduene på samme vegg.

## 3. Småhusene — GJORT (fargen + valmtak)
- Lysthuset bnr-193867456 og pb-16 (det andre lille huset ved hagen): vegg/tak samme som hovedhuset, skyggetoner null, lite valmtak (`tak2` regnet fra fotavtrykket, 4 flater).
- NB: pb-16 er den nærmeste eksisterende lille strukturen i hagen mot vannet; lysthuset ligger i NV-hjørnet. Fant ikke et eget bygg i NØ-hjørnet i bygg.json/ortofoto — Vegar bør bekrefte at lysthus + pb-16 er «de to småhusene».

## 4. Renessansehagen — GJENSTÅR (recipe klar)
Ortofoto 2024 lest (flis_-448_64): rektangulær parterre mellom huset og vannet, grusramme, diagonale X-stier, sentral sirkel, 4 trekantbed med buksbom, pergola-rad mot vannet. Men i modellen er hageflaten i dag dekket av kartets trær.
Recipe (ett neste pass):
- grus-stier + bed → `kilder/flater-maalt.json` «flater» (`{id:fl-70…, typ:grus|bed, p, grunn:"ortofoto 2024 (Renessansehagen)"}`), bygg `python3 verktoy/flater.py parkering`.
- buksbomhekker → `kilder/bakke-maalt.json` «gjerder» (`{typ:"hekk", h:0.5, p, grunn}`), bygg `python3 verktoy/bakke.py gjerder`.
- trærne i hagen fjernes via `traer_fjernet` i `kilder/bakke-maalt.json` («Ingen trær i hagen»).
- lav mur/kaikant mot vannet.

## Pilastre — GJENSTÅR
De 4 tykke loddrette listene/pilastrene på vannfasaden (frac 0,481 · 0,661 · 0,741 · 0,906) er ikke lagt inn — trenger en fasadefelt-/veggfelt-representasjon (`verktoy/bygg_merknader.py`). Ikke rukket innenfor taket.
