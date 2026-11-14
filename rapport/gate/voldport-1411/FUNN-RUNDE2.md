# FUNN — RUNDE 2, Voldportgaten 75–71 (Studio, 14.11.2026)

Gren `gate/voldport-1411`, bygd på nytt (bygg_kjede.py, grunnmur urørt). Regler **13/14/17/20/48 grønne**,
last-test ren (`lastet: true feil: []`). GPU-render (ekte Metal/ANGLE) i KONTAKTARK.png + de fem bildene.
**Jeg har lest de ferdige renderbildene kritisk mot RUNDE2-lista**, ikke bare koden (kalibreringen 13.11).
IKKE publisert. Fable leser bildene igjen.

> Merk om oppstart: worktreet hadde ved start en halvferdig, avsporet endring fra en overlappende
> tidligere runde (spekulativ id-flytt 71 → bnr-193867944 «Therese M = Råde Bakeri», som motsier den
> committede OPPGAVE/FUNN og Fables egen RUNDE2 — RUNDE2 pkt 8 behandler 71 som bnr-193868258 uten å
> flagge id-feil). Jeg forkastet den og bygde ren fra 6c6d788. **71 = bnr-193868258** står.

## Verktøy lagt til (additivt, deterministisk, rører ingen andre hus)
- `bygg_merknader.py` + `streetview_fasader.radhoyder`: **«butikk»** {b,h,sill} = store butikkvinduer KUN i
  grunnetasjen, etasjene over normale (der «stor» før gjorde hele veggen lik).
- `bygg_merknader.py` + `src/07`: **«spross»:"T"** = T-postvinduer (én stor nedre rute, to små øvre) på
  etasjene over grunnraden, via vindus-kanalen vInfo.z (var ubrukt; 0/1 = som før, 2 = T-post).
- `bygg_merknader.py` + `src/07` veggfelt: valgfritt **z-spenn [z0,z1]** → smalt horisontalt bånd (vannbord),
  ellers hele veggen som før.

## Dom per punkt (1–9)

| # | Punkt | Gjort | Dom |
|---|---|---|---|
| 1 | 75 store butikkvinduer i 1. etg + rett dobbeltport | butikk {b1.7,h2.4,sill0.4} på NØ+SØ (15 butikkvinduer h2.4); porten endret fra typ 2 (rundbuet) til typ 1 (rett, rektangulær dobbeltdør) | **✓** Grunnetasjen er nå brede butikkvinduer med dører imellom på begge fasader; Voldgaten har 2 dører, Voldportgaten dører + rett dobbeltport. 2. etg er små boligvinduer. |
| 2 | 75 T-sprosser i 2. etg (ikke 4-ruters kryss) | spross:"T" → 17 øvre vinduer merket T-post (e[11]=2); shaderen tegner loddrett post bare i øvre del + losholt | **~** Dataene er riktige og T-posten tegnes. I render står 2.-etg-vinduene små, så T-mønsteret leses svakt på gateavstand (sprossene tones ut når px blir store). Tydeligere enn 4-ruter, men ikke markant. |
| 3 | 75 dempede farger | vegg [204,192,198]→**[202,197,198]** (lys gråbeige, mindre lilla); tak [168,82,62]→**[132,74,60]** (mørk rødbrun) | **✓ vegg / ~ tak** Veggen leser nå lys gråbeige, ikke lavendel. Takets basisfarge er mørknet, men solbelyste takflater reader fortsatt ganske rødt (sol/LOD-fade — jf. «grå granitt ≠ grå basisfarge»). Kan mørknes mer om Vegar vil. |
| 4 | 75 fjern gavlen/ark-formen på mønet | `arker:"ingen"` → arker=0 | **✓** Mønet er rent i kryss- og skråfoto-bildet; ingen ark/gavl midt på. Ett sammenhengende valmtak. |
| 5 | 75 skråinngang i 1. etg på hjørnet | **Valgt vei:** mørk inntrukket flate (veggfelt [70,50,42], hel høyde) som hjørnekasse rundt krysshjørnet + hjørnedøra (NØ u0.02) ved den | **~** Modellen ekstruderer vegger rett fra ett omriss, så en ekte skråskåret 1.-etg-inngang med utkraget tak kan ikke uttrykkes. Jeg la den mørke inntrukne flata med dør på hjørnet (det RUNDE2 ba om som alternativ). Leser som en mørk hjørnebay, ikke en ekte innskåret skråvegg. |
| 6 | 75 mørkebrune bånd (vannbord, hjørnekasser) | veggfelt med z-spenn: vannbord [74,52,44] z 2,85–3,3 over butikkvinduene på begge gatevegger + hjørnekasser | **✓** Tydelig mørkebrunt vannbord mellom butikkvinduene og 2. etg på begge fasader; mørke hjørnekasser ved krysshjørnet. |
| 7 | 73 Majoren: møne LANGS gata | tak-tegning `mone:"kort"` → saltak «tvers» = møne parallelt med gatefasaden | **✓** Gatefasaden (v2) er husets korte side; mone=kort gir takfot mot Voldportgaten, ikke gavl. Gatebildet viser raft/takfot mot gata. (DOM-tilpasning rms 1,25 m; takfot refittet til 5,62 m, fortsatt lavere enn 75.) |
| 8 | 71 Therese M: mørkt tegltak + dør i skrå hjørnet | tak [176,86,64]→**[132,74,60]**; gatedøra flyttet u0.03→u0.97 (fra fjern ende til ~4 m fra apex/skråhjørnet mot gata) | **✓ dør flyttet / ~ tak** Døra står nå mot det skrå hjørnet, ikke lenger i fasaden ved sida (var ved motsatt ende). Rundbuede butikkvinduer står. Takets basisfarge mørknet, men solsiden reader rødt (samme fade som pkt 3). Apex er et skarpt hjørne, ikke en modellert skråvegg, så døra ligger på gatefasaden nær hjørnet; ingen steintrapp som eget objekt. |
| 9 | Gatekamera `kryss` ut i krysset | standpunkt model[182,53] h288 → **[192,52] h248**, fov 84, øye 2,6 | **✓** Kameraet står nå ute i krysset og ser WSW mot 75s hjørne. Ingen svevende dør i forgrunnen; hjørnet med begge butikkfasadene er tydelig. |

## Ærlig restliste (til Vegar/Fable)
1. **T-sprossene (pkt 2)** leses svakt fordi 2.-etg-vinduene er små på gateavstand. Om de skal lese tydelig,
   må vinduene gjøres større eller kameraet nærmere.
2. **Takfargen i sol (pkt 3, 8)** er mørknet i basis men popper rødt i direkte sol (LOD/sol-fade). Si fra om
   den skal mørknes ytterligere, så justerer jeg basisverdien ned.
3. **Ekte innskåret skråinngang med utkraget tak (pkt 5)** og **steintrapp (pkt 8)** krever per-etasje- /
   per-objekt-geometri som modellen ikke har. Løst som mørk hjørnekasse + dør, som RUNDE2 åpnet for.

## Regler (grønne)
- 13_deler_staar_paa_topp ✓ · 14_id (71 beholdt som bnr-193868258, ingen id slettet) ✓ ·
  17_vinduer_rytme 0 brudd ✓ · 20_grunnmur_fkb 0 avvik ✓ · 48_vinduer_ikke_oppaa_hverandre 0 overlapp ✓

IKKE publisert.
