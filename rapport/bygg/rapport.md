# Byggene 29.10 (natt/bygg): form, tak, fasader – rapport

Kontrollark per kvartal (laget: Kvartal2BITMP, Kvartal3, Kvartal4BITMP, kvartal5, kvartal6, kirke; de andre rendres fortsatt –
`python3 verktoy/bygg_ark.py ark` når `rapport/bygg/_arbeid/<tegning>-az20.png` finnes): `rapport/bygg/kvartal-<tegning>.png` (tegningen til venstre, modellen fra samme kant, az 20, til høyre,
fasadetabell under: vinduer per vegg og etasje nederst først, D dører, P porter, ark, takvinduer, piper, kilde). Nærbilder av husene
med merknader: `rapport/bygg/_arbeid/naer/` (bare lokalt). Verktøyene står i LESMEG («Byggene: kjeden»).

## Rettet i systemet (gjelder alle hus)
- **Høydene fulgte plassen i lista, ikke huset.** `rapport/hoyder/hoyder.json` var nøklet på plass; et nytt bygg foran de andre nye
  flyttet alle plassene, og målt høyde havnet på nabohuset. Nå har målingene id (hent.py, legg_inn.py, regel 02).
- **Piper og arker står på taket.** Høyden regnes alltid fra takflatene (datalag), pipene flyttes til mønet. Arkene på −2,08 m
  (bnr-193918247) og 0,52 m (bnr-193868134) kom av at en rettelse regnet mot ny høyde ble flyttet en gang til. Regel 13 sjekker nå
  alle 499 piper og arker.
- **Tegningsvinduene ble skjøvet inn i hjørnene.** grunnmur.py holder nå aksens andel av veggen når veggen endrer lengde.
- **Street View alle sider** (296 hus, «sider»): fasade per sett vegg; når kamerapunktet bommer, velges veggen etter retningen i
  avlesningen. 82 hus endret, 95 tegningshus bare sammenlignet.
- **Knekktak** (`takform: knekk`), **sokkel/natursteinsetasje**, **takvinduer** og **veggfelt** (to fasader under ett omriss) i data og src/07.
- **Takfarge fra ortofoto 2024** på 26 av de nye byggene fra kommunekartet (11 hoppet over: trær over taket eller for små). Veggen
  på dem står fortsatt nøytral (ses ikke fra lufta, ikke i Street View).
- **Id etter Matrikkelen:** kommunehuset med punktet 193867995 fikk id bnr-193867995 (var pb-15), nabohuset bnr-193972160.
  Fire dobbeltnumre og tre kontorpunkter uten hus er avgjort med ortofoto/DOM i `kilder/id-etter-matrikkel.json`.

## Fasader fra tegningene som vektor
`verktoy/fasade_tegning.py`: vinduer og dører er hull i veggflatene i .ai-fila. 28 hus i Kvartal2, 3, 4, 5 og 6 har nå vinduer lest
som vektor (223 elementer, antall og rekkefølge i andel av veggen), resten av veggene etter reglene. Koblingen flate→hus er satt for
hånd (`kilder/fasade-kobling.json`): den automatiske kameratilpasningen holder ikke på tegninger satt sammen av biter.
Kjent svakhet: dører/porter overtelles der døra er tegnet som egen flate (72292: 3 i stedet for 2), og noen etasjerader slås sammen
(6247822, 68045 er tatt ut av lesingen av den grunn).
**Ikke gjort:** Kvartal7–14, sistekvartal, tell, Glasshytta har fortsatt tegningsvinduene fra v22/v33 (nå med riktig andel langs veggen).

## Vegars merknader (kvartalskontrollen 29.10)
Kvartal3
- [x] 67324 port med buet topp (2,4 × 2,6 m midt på langveggen mot SV, 8 vinduer, som tegningen og Street View)
- [x] pipene på toppen av taket (alle hus: mønet)
- [x] tre vinduer i taket (tolket som de tre takvinduene i tegningen) – arkene tatt bort, tegningen har ingen
- [x] huset til høyre rødt og lavere (bnr-193867308: farge fra tegningen, h 3,5 m)
- [ ] tilbygg på høyre side av 67324 – ikke rettet. Nærbildet viser at modellen har vanlig gavl i høyre ende; tegningen har en lavere
      endedel med valm (flate 149/150). Trolig det han mener; takformen per ende er ikke lagt inn ennå.
- [ ] 67308 (huset til høyre): døra på langveggen (flate 168 i tegningen) er ikke lest inn – lesingen fant ingen elementer, veggen står blank
- [ ] hvitt tilbygg øverst til venstre – står i kommunekartet (FKB) og under trærne i ortofotoet: ikke fjernet (konflikt tegning 2015 mot kommunekart)
- [x] 68037: arken mot SØ, ingen pipe, 2 + 2 vinduer og dør i midten; arken på gavlen tatt bort
- [ ] 68037/68088 grønt gjerde og veien til venstre for det – gjerder og veier er ikke byggemnet (videresendt)
- [ ] 68061 «stor grusdekket parkeringsplass» – bakkeflater, ikke byggemnet (videresendt)
- [x] 68053 to inngangsdører i front; én av to piper tatt bort (usikkert hvilken han mente med «største»)
- [x] 68061 steinstrukturen (sokkel 3,1 m i natursteinsfarge, også på 69572) og takvinduene (6 + 7)
- [ ] 68061 vindu som mangler på sørsiden, tre «utstikkere» mot to – ikke rettet (utstikkerne kommer fra kommunekartets omriss)
- [ ] alle vinduer med sprosser – kartet tegner sprosser på alle vinduer, men de ses ikke på avstand; ikke endret
Kvartal4BITMP
- [x] 06187 (merknaden sier 09187): lite hus mot veien, 2 + 2 vinduer
- [ ] 71989 like høyt som nabohuset, venstre del som boks – ikke rettet (uklart hvilket nabohus)
- [ ] 68428 oppmurt gjerde – murer er ikke byggemnet (videresendt)
- [ ] 71962/71970/68401 henger sammen – omrisset er kommunekartets; ikke endret
- [x] 68401 stor inngangsdør (port med buet topp, fra tegningen)
- [ ] bygget til venstre for 68401 finnes ikke – står i kommunekartet: ikke fjernet (konflikt)
- [x] 68363 ingen takvindu, 9 vinduer over to etasjer mot veien, dør til venstre med vindu over og vinduer til høyre mot SØ
Kvartal2BITMP
- [x] fasadene på forrekka lest fra tegningen (Prestegården 5/5, 68088 4/4, 68096, 72292, Salamandergården)
- [ ] hus som mangler nederst til høyre, sammenslåtte hus øverst til høyre, hjørnehuset som skal henge sammen med sidehuset,
      hvitt og lavere hus nederst til høyre, husene i midten – ikke avgjort: krever sammenligning av kommunekartets omriss mot tegningen hus for hus
- [ ] gjerdet – ikke byggemnet (videresendt)
kirke
- [x] dør i rundbuet omramming på sørenden, dør helt til høyre (østenden), ingen vinduer på tårnfoten mot øst (src/06)

## Hovedagentens funn
- [x] (1) Toldbodgaten 37 bnr-193868320 står med 9,1 m i denne grenen og 9,2 m i main; «3,8 m» finnes ikke i dataene. Årsaken til
      feil høyder generelt (plass i stedet for id) er rettet.
- [x] (2) Knekktak på Toldbodgaten 39B
- [x] (3) Balaklava 78B: Kartverket p50 6,6 m, p90 8,5 m gir takfot 4,5 m (høy sokkel + én etasje); beholdt
- [~] (4) Færgeportgaten 84: Matrikkelens punkt (og adressepunktet) står på delelinja mellom gatehuset og bakhuset; kommunekartet legger
      det i bakhuset, så registeret (regel 21) vil ha kortet der. Ikke byttet; trenger at registeret godtar punkt på felles vegg.
      Smedjegaten 91 og Kasernegaten 50: adressepunktene står i bnr-193868118 og bnr-193867804 – Street View-avlesningen må knyttes dit.
- [x] (5) Raadhusgaten 16 og Kirkegaten 32A: ett omriss og ett nummer, ett tak i ortofotoet: ett hus med to fasadefarger (veggfelt)
- [x] (6) Voldportgaten 71 beige (bildet fra 2024 gjelder), Torvgaten 58: fargen fra brukerpanoramaet gjaldt nabohuset, 2015-fargen står
- [x] Kruttmagasinet pb-22: overdekket i vollen (gress, DOM 0 m): vises som lav gressflate med navnet
