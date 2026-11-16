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

## 4+5 UTFØRT 16.11 (Studio, PAG-1634) — se under for detaljer

## 4. Renessansehagen — GJENSTÅR (recipe klar)
Ortofoto 2024 lest (flis_-448_64): rektangulær parterre mellom huset og vannet, grusramme, diagonale X-stier, sentral sirkel, 4 trekantbed med buksbom, pergola-rad mot vannet. Men i modellen er hageflaten i dag dekket av kartets trær.
Recipe (ett neste pass):
- grus-stier + bed → `kilder/flater-maalt.json` «flater» (`{id:fl-70…, typ:grus|bed, p, grunn:"ortofoto 2024 (Renessansehagen)"}`), bygg `python3 verktoy/flater.py parkering`.
- buksbomhekker → `kilder/bakke-maalt.json` «gjerder» (`{typ:"hekk", h:0.5, p, grunn}`), bygg `python3 verktoy/bakke.py gjerder`.
- trærne i hagen fjernes via `traer_fjernet` i `kilder/bakke-maalt.json` («Ingen trær i hagen»).
- lav mur/kaikant mot vannet.

## Pilastre — GJENSTÅR
De 4 tykke loddrette listene/pilastrene på vannfasaden (frac 0,481 · 0,661 · 0,741 · 0,906) er ikke lagt inn — trenger en fasadefelt-/veggfelt-representasjon (`verktoy/bygg_merknader.py`). Ikke rukket innenfor taket.

---

## DEL 4 — Renessansehagen — UTFØRT 16.11 (Studio)
Parterren målt i ortofoto 2024 (flis_-448_64) via rektifisering mot modellmeter (flis-hjørne -448,64; 0,125 m/px) og forankret på husene bnr-193867464/456 + pb-16. Parallellogram W(-337,3;117,5) N(-314,6;123,1) S(-329,2;100,4), ~23×19 m.
- **Flater** (`kilder/flater-maalt.json`, bygd med `flater.py parkering` → `data/flater.json`): `fl-651` grus-plattform (hele parterren) + `fl-652…662` bed-kompartement: 4 trekantbed i vestre X-kvadrat, 5 strekbed i NØ-«kammen», 2 bed i SØ. Alle klippet mot husomrisset (buffer 0,2 m) så ingenting ligger inne i huset. Id-ene lå over `fl-650` (auto-klassifiseringens maks) og er ført i `kilder/id-register.txt` så klassifiseringen ikke gjenbruker dem. **NB id:** oppgavens «fl-70…» kolliderte med 650 auto-flater — brukte `fl-651+`.
- **Buksbom** (`kilder/bakke-maalt.json` «gjerder», h 0,45): X-kvadratets omriss + 2 diagonaler, kant rundt hver strek-/SØ-bed. 12 linjer → `data/gjerder.json` som `gj-491…502` (kilde «målt for hånd»). `bakke.py gjerder` krever cv2+DOM-DTM (mangler i denne py) og ville re-detektert ALLE gjerder → la hekkene inn kirurgisk i samme postformat som håndmergen gir; en senere full `bakke.py gjerder` reproduserer dem fra bakke-maalt (arver id ved overlapp).
- **Trær:** 0 trær i parterren i `data/traer.json` (nærmeste 20 m unna, sør for huset). «Ingen trær i hagen» er allerede oppfylt — `traer_fjernet` ville vært en no-op (det refererer konkrete tre-posisjoner som fjernes), så ingen ble lagt inn.
- **Render verifisert** mot fasit (orto_hage.png): X-kvadrat m/4 trekanter, kam-strekbed og grønne buksbomkanter leser riktig; parterren ligger ren mellom hus og vann, uten trær. 
- **Åpen vurdering til Vegar:** bed-kompartementene er typ `bed` (brun jord) etter oppgavens «grus|bed». I fasit leser de litt grønnere/lysere. Vil du ha dem som plen (grønn), er det én endring: typ `bed`→`gress` på `fl-652…662`.

## DEL 5 — 4 pilastre på vannfasaden (bnr-193867464) — UTFØRT 16.11 (Studio)
Lagt inn som `veggfelt` via `kilder/bygg-merknader.json` (ny hus-post) → `bygg_merknader.py` → rettelse. Side `NNV` = vannfasaden (wi 0, L 19,9 m). Bekreftet at `veggfelt.fra`=0 er ØSTRE hjørnet = samme «frac fra østre hjørne sett fra hagen» som del-2-vinduene. Fire grunne lister, bredde ~0,6 m, full vegghøyde (z utelatt → 0..h), 3 cm ut fra veggen, lysere varm veggtone [214,170,120] så de leser som relieff.
- **Verifisering:** veggfelt-rettelsen gir 4 segmenter på riktig vegg, monotont øst→vest etter frac 0,481/0,661/0,741/0,906, full høyde. I render (fast PITCH0, skrå ovenfra) ligger vannfasaden under takskjegget og pilastrene er ikke tydelige ovenfra; verifisert på datanivå. Tydeligere i bakkenær visning.
- **Pilaster-farge** er en modelleringsvalg (ingen fasadefoto-farge i briefen) — juster ved behov.
