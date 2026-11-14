# Voldportgaten 75–71: én gateside bygd om etter Vegars bilder (14.11.2026)

Bestilt av Vegar 14.11 13:05 (Fable koordinerer). Worktree: ~/sot-maskin/voldport, gren gate/voldport-1411 (fra gate/vandring-1411 7711058).
Vegars dom: «Du har tegnet hele denne gaten feil.» Bare sida av Voldportgaten fra hjørnet mot Voldgaten til og med Therese M. Ingen andre hus røres.

## Husene (id fra Matrikkelen, kilder/register/gamlebyen.json)
| Adresse | id | Hva det er |
|---|---|---|
| Voldportgaten 75 | bnr-193867928 (+ pb-66, se under) | hjørnebygget mot Voldgaten, gnr/bnr 302/80 |
| Voldportgaten 73 | bnr-193868622 | Majorens Kro & Stue (skiltet «73» står ved porten i Vegars bilde) |
| Voldportgaten 71 | bnr-193868258 | Therese M (Vegar 13:23: «Therese M er nok 71, ja») |

## Det Vegar sa, ordrett (14.11 13:05)
«alle byggene i Voldportgaten 75. Har ett felles tak og er konstruert som én bygning. Fasaden er i tre. Hjørnet har en "innbygd skråinngang".»
«den første butikkens ende stoppen ved den første brune døren […] elektrikkerens adresse stopper ved takrenna. Så kommer det et butikklokale - og bygget stopper ved Majoren.»
«Majoren har eget tak med takstein, og taket er litt lavere enn voldportgaten 75. Majoren har en hvitaktig - murfasade, med egen inngang med trapp i stein, med store dobbelvinduer på begge sider av døren og egen port til bakgården der de også serverer om sommeren. Majorens adresse stopper ved takrennen.»
«Therese m […] med eget og lavere tak med takstein […] huset har en egen skrå-inngang mot gaten og […] bygger er langt og sammenhengende. Therese Ms lokale stopper ved takrennen og har butikkvinduer med store ovale topp-vinduer. Helt til høyre ser du at bygget stopper der du ser begynnelsen på en nytt tak som er mye høyere.»
«Voldportgaten 75 […] fra voldgaten, 8 vinduer i 2 etg med t-sprosser, store butikkvinduer i 1 etg med to inngangsdører.»

## Lest av Fable fra Vegars 9 bilder (Street View mai 2024 + matrikkelkart)
75 (bnr-193867928):
- ETT hus, ETT tak. Husdelingen 30.10 (kilder/husdeling.json: kutt [[166.97,29.42],[176.05,49.69]] → pb-66, «to tegnede fasader i ulike farger … DOM sprang 1,6 m») er feil: ta kuttet ut, skjul pb-66 med grunn (id slettes aldri, regel 14/20).
- Valmtak i rødbrun tegl rundt hjørnet (bildet fra krysset viser valm på hjørnet), én mønehøyde, piper på mønet.
- 2 etasjer. Vegg: stående trepanel lys gråbeige/gråfiolett (dagens vegg [204,192,198] er riktig retning). Mørkebrune hjørnekasser, gesims, vannbord mellom etasjene og over butikkvinduene. Hvite vinduer i mørkebrune foringer.
- Hjørnet: 2. etasje har rett hjørne; BARE 1. etasje er skåret skrått inn (innbygd skråinngang, dør i den skrå veggen, utkraget tak over).
- Mot Voldportgaten (fra hjørnet): butikkvinduer + skråinngang; butikk 1 til første brune dør; elektrikeren (Gamlebyen Elektriske, to dører med steintrapp) til nedløpsrøret; så et butikklokale (Emm K) og den brune dobbeltporten til bakgården; deretter Agnes C-butikk, og huset slutter mot Majoren. Hele veggen er én fasade i samme farge (ingen fasadesegmenter i ulike farger).
- Mot Voldgaten: 8 vinduer i 2. etg med T-sprosser, store butikkvinduer og to inngangsdører i 1. etg.
73 Majoren (bnr-193868622):
- Eget tak, takstein (brun/grå tegl), litt LAVERE enn 75. 2 etasjer, hvitaktig puss/mur. 5 vinduer i 2. etg (hvite karmer, mørkebrun foring).
- 1. etg: inngang i midten med steintrapp, store doble vinduer på begge sider, deretter portrom til bakgården (åpent, med treport innerst). Huset slutter ved nedløpsrøret til høyre for porten.
71 Therese M (bnr-193868258):
- Én etasje, hvit mur, eget lavere tegltak (valm), 2–3 piper.
- Skrått hjørne i HELE høyden med inngangsdør og steintrapp.
- Butikkvinduer med rund bue øverst («ovale topp-vinduer») langs gata.
- Langt og sammenhengende; slutter der neste, mye høyere tak begynner.

## Slik (LESMEG: «Et hus som skal endres, endres i data (rettelser.json) og bygges på nytt, ikke i scenen»)
1. kilder/husdeling.json: fjern kuttet på bnr-193867928 (pb-66 skjules med grunn «Vegar 14.11: ett tak, én bygning»).
2. kilder/tak-tegning.json / kilder/bygg-merknader.json: Vegars avgjørelser for de tre husene (takform, høyder 75 > 73 > 71, farger, skrå hjørner, rundbuer, port), grunn «Vegar 14.11 (Street View mai 2024, hans bilder)». Merknadene vinner over alt (Fargene §).
3. Vinduer/dører/butikkvinduer: legg dem inn for hånd etter beskrivelsen over (fasade_rett / elementer), ikke fra gatekameraet.
4. Kjeden (bygg_kjede.py) → regler 13, 14, 17, 20, 48 grønne.
5. Bilder på minien med ekte GPU: gatekameraet fra krysset Voldportgaten/Voldgaten, fra Voldgaten mot 75s kortside, langs Voldportgaten mot Majoren og mot Therese M, og ett skråfoto ovenfra som Vegars skjermbilde. Legg dem i rapport/gate/voldport-1411/ med et KONTAKTARK.
6. Sammenlign selv bilde for bilde med punktlista over, skriv FUNN.md (hva stemmer, hva ikke), commit på gate/voldport-1411. IKKE publiser. Fable leser bildene før noe kalles ferdig.
