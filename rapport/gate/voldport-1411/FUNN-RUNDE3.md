# FUNN — RUNDE 3, Voldportgaten 75–71: lest fra Street View på nytt (Studio, 14.11.2026)

Gren `gate/voldport-1411`. Del A (FEILANALYSE + LESMEG-regel) er committet (5368028) og rørt ikke.
Dette er del B/C-arbeidet: **jeg gikk faktisk ned på gaten** (hentet ny Street View) og leste de tre
husenes gatevegger mot modellen. IKKE publisert.

## 0. Rettelse av forrige status: Street View-hentingen er IKKE blokkert
Forrige heartbeat (commit a0aac82, `RUNDE3-STATUS.md`) meldte del B **blokkert** fordi `sv_hent.mjs`
«krever synlig Chromium og stopper ved robotsjekk — en uassistert heartbeat kan ikke løse det».
**Det stemmer ikke i denne runneren.** Jeg kjørte `node verktoy/sv_hent.mjs` uassistert to ganger:
- 2 helvegg-skudd (planleggerens) → «ferdig 2 bilder 9 s», ingen robotsjekk.
- 5 frontale skudd (ett pano rett foran hver gatevegg) → «ferdig 5 bilder 19 s», ingen robotsjekk.

Synlig Chromium starter og når Google her. **Den egentlige begrensningen er ikke hentingen, men
(a) skuddgeometrien og (b) hus-identiteten (PAG-1591)** — se §3–4. Alle 7 skuddene ligger i
`rapport/gate/sv_rett_r3/` (gitignorert, Google-bilder skal ikke i git); rutenett-avlesningene i
`rapport/gate/voldport-1411/r3/rett-arbeid/`.

## 1. Hva jeg hentet (mai 2024 der det fins, ellers aug 2010 — 2010 gyldig for vindu/dør, ikke farge)
| Skudd | Hva det viser | Kvalitet |
|---|---|---|
| `bnr-193867928-4f` (2024, 4,5 m, skrå 0°) | 75 Voldportgaten-fasaden rett forfra | **utmerket** |
| `bnr-193867928-5f` (2024, 7,9 m, skrå 27°) | 75 Voldgaten-kortsida | god |
| `bnr-193867928-5` (2024, 39 m, skrå 38°) | 75 hele hjørnet fra krysset (planleggerens helvegg) | oblik |
| `bnr-193868622-2f` (2010, 28 m, skrå 35°) | 73-retningen (gult trehus m/markiser) | langt/oblik |
| `bnr-193868258-1f` (2010, 6,2 m, skrå 24°) | 71 forfra: lavt kremhvitt trehus | god |
| `bnr-193868258-2f` (2010, 8,9 m, skrå 45°) | 71 langs, med takopplett | brukbar |
| `bnr-193868258-2` (2024, 20 m, skrå 61°) | planleggerens helvegg — lander på restaurantbygget (Majoren) | oblik + identitetsfelle |

## 2. SV-tall mot modell-tall (det recipe ba om)

### 75 Voldportgaten 75 (bnr-193867928) — identitet IKKE omstridt (hjørnebygget, Gamlebyen Elektriske/Emm K)
| Vegg | Street View (lest nå) | Modellen i dag | Dom |
|---|---|---|---|
| vegg4 Voldportgaten (33,5 m) | Stående trepanel, lys gråbeige. **Mørkebrunt vannbord** mellom etasjene (✓ stemmer). Øvre etg: rad med enkle vinduer i mørkebrune foringer, **loddrett midtpost (tospeil), ikke 4-ruters kryss**. Grunnetg: **store butikkvinduer** (Gamlebyen Elektriske AS × 2, Emm K) vekslende med dører; **steintrapp** ved dørene; **mørk portåpning/passasje i høyre ende** | 9 + 9 vinduer, 5 dører i **jevn rytme** (u 0.02/0.30/0.48/0.70/0.90), butikk-type grunnetg, T-spross, vannbord, port | antall/posisjon **oppdiktet rytme**; karakteren (butikk+vannbord+port) stemmer |
| vegg5 Voldgaten (20,2 m) | 2 etg, samme panel/trim; grunnetg store butikkvinduer + dører (skilt «STORE», «happy ♥…»); øvre vindusrad | 6 + 8 vinduer, 2 dører | øvre «8» var Vegars tall; resten rytme |

Vannbordet, butikkvinduene og porten traff **på karakter**. Det som aldri ble lest: de **faktiske
posisjonene** (hvor Elektriske slutter, hvor Emm K/​Agnes C står, hvor porten står) i meter.

### 73 Majoren (bnr-193868622) — svak lesning
Frontal-pano (2010, 28 m) peker på et **gult trehus med grå markiser** over en butikkinngang; det
oblike 2024-skuddet viser **restaurantbygget** (kniv/gaffel-ikon, uteservering, mørkt valmtak,
hjørneinngang). Hvilket av disse som er Majorens bnr kan jeg **ikke** avgjøre herfra uten å gå inn i
identitetsspørsmålet (PAG-1591). Modellen: saltak, 5 vinduer øvre, midtdør + port. **Ikke bekreftet mot foto.**

### 71 «Therese M» (bnr-193868258) — modellen er grovt feil, OG identiteten er omstridt
| Street View (lest nå, 2010 forfra) | Modellen i dag |
|---|---|
| **Lavt 1-etasjes KREMHVITT TREHUS** (stående/liggende panel), **rødt tegltak som VALM med TAKOPPLETT (arker)**, **grønn tofløyet dør** med overvindu og klassisk dørinnfatning midt på, flankert av vanlige **tospeilsvinduer** (gardiner), flere vinduer langs | Hvit **mur**, **5 rundbuede butikkvinduer** («ovale topp»), valm **uten arker**, h 4,2 m, dør i skrått hjørne |
| **Ingen rundbuede butikkvinduer på dette bygget.** | |

→ Modellens 71 (hvit mur + rundbuevinduer) ligner **ikke** bygget på bnr-193868258. De rundbuede
butikkvinduene Vegar beskrev hører trolig til **et annet bygg** (den ekte Therese M) — nøyaktig det
`IDENTITET.md`/PAG-1591 sier. Å rette 71s geometri nå ville **bake identitetsfeilen inn i modellen.**

## 3. Hvorfor full rektifisering ikke ble kjørt ferdig denne runden (ærlig)
- `sv_rett_plan.py` fant bare **2 av 11** vegger med et pano som ser hele veggen (75 vegg5, 71 vegg2),
  begge oblike (38°/61°). 75s hovedfasade (vegg4, 33,5 m) får ikke plass i ett pano; 73 har ingen.
- De frontale skuddene jeg hentet er **utmerkede for å LESE** fasadene (det recipe egentlig ba om:
  «lese street view igjen»), men pitch 95 / < hele veggen gjør dem uegnet til `rett.py`-homografi uten
  flere pano per vegg. Å lese meter rett av et uretted, oppovervinklet skudd ville være **å gjette
  meter på nytt** — selve synden i FEILANALYSE.md. Derfor stoppet jeg før jeg skrev falske metertall.
- `rett.py`/`konverter.py`-arbeidsmappa står klar i `r3/rett-arbeid/` (vegger-u.json + rutenett-skudd)
  for den som fortsetter med flere pano per vegg.

## 4. To porter før modellen kan bygges om
1. **75 (undisputed):** kan rektifiseres og bygges om når vegg4+vegg5 leses fra **flere frontale
   pano stitchet** (eller aksepter frontal-lesning som kilde). Studio-arbeid, ikke blokkert av henting.
2. **71 + 73:** geometri-ombygging er **gated på Vegars identitetsavgjørelse (PAG-1591)** — bærer
   bnr-193868258 Therese M eller bakeriet, og hvilket bygg er Majoren? Uten det risikerer vi å
   rette feil fasade på feil fotavtrykk.

## 5. GJORT etter CEOs klarsignal (komm. 1b9e1b26): 75 rektifisert + montasje
CEO dømte lesningen og ga **75 → GÅ NÅ** (71/73 holdes til PAG-1591). Kjørte rett-kjeden på 75:

- **vegg5 (Voldgaten, 20,2 m) rektifisert** fra det oblike krysskuddet `bnr-193867928-5` (mai 2024):
  hjørner → `rett.py` (50 px/m, meterrutenett) → lest i meter (ELEMENTER.md) → `konverter.py` →
  `kilder/gate/rett-voldport-1411.json` (godkjent) → `bygg_kjede.py` (fasade_rett sist).
- Lesning: **2. etg = 8 vinduer** (4 + blank hjørnepilar s8–11 + 4 — stemmer med Vegars «8 vinduer
  i 2. etg mot Voldgaten»); **1. etg = 7 store butikkvinduer + 2 dører** (sammenhengende glassfasade,
  ikke 6 små boligvinduer). `bnr-193867928.fasade_rett = [5]` → regel 17 dømmer nå veggen mot
  virkeligheten, ikke mot rytmen.
- **Montasje SV | render:** `rapport/gate/voldport-1411/r3/montasje-75-vegg5.jpg` (2×1280×720).
  Render fra samme pano-standpunkt (krysset). 75s Voldgaten-face viser nå **butikkvinduer + mørkebrunt
  vannbord** der modellen før hadde en jevn rad småvinduer. Bygningsrekka (blå → oker → grått
  hjørnebygg → rosa → rød) matcher fotoet.
- Presisjon: skuddet er oblikt (38°, 39 m, lav opplosning) → posisjoner ±0,5 m, grovere enn
  ELEMENTER-målet ±0,3 m. CEO godtok frontal-/grovlesning som nok til å erstatte den oppdiktede
  rytmen; helvegg-pano er en senere forbedring.

### Ærlige gjenstående avvik på 75 (ikke løst denne runden)
1. **vegg4 (Voldportgaten, 33,5 m)** — hovedbutikkfasaden (Gamlebyen Elektriske/Emm K) — kan **ikke**
   rektifiseres: 33,5 m får ikke plass i ett pano (hjørnene faller på u −0,57 og 1,52 i frontalskuddet,
   `rett.py` hopper over vegger som går ut av bildet). Den har fortsatt den oppdiktede rytmen. Krever
   stitchet multi-pano eller eget foto. Beskrevet i §2.
2. **Veggfarge:** gata viser et **medium, kjølig grått** (ikke modellens lyse [202,197,198]). Målte
   ikke RGB inn — mine stikkprøver på det oblike skuddet var støyete (skygge/karmer); å gjette en tone
   ville være samme synd. Venter på et rent, solbelyst 2016+-skudd rektifisert for FARGER.md-måling.
3. **71 + 73:** urørt, gated på PAG-1591 (CEOs ordre).

## Status-oppsummering
- Del A: gjort (sibling, 5368028). Rørt ikke.
- Del B: **lest på nytt fra ekte Street View** (7 skudd, korrigerer «blokkert»); SV-mot-modell-tabell i §2.
- Del C: **75 vegg5 rektifisert + fasade_rett + montasje levert** (§5). 75 vegg4 (for lang) og veggfarge
  gjenstår; 71/73 holdt på PAG-1591.
- `fasade_rett`-kilde: `kilder/gate/rett-voldport-1411.json`. Montasje:
  `rapport/gate/voldport-1411/r3/montasje-75-vegg5.jpg` (ligger lokalt; Google-bilder holdes utenfor git).

IKKE publisert.
