# Byggene 29.–30.10 (natt/bygg): form, tak, fasader – rapport

Nærbilder per husrekke (modellen ved største zoom, pikseltetthet 2, ved siden av tegningen, med fasadetabell): `rapport/bygg/naer/<tegning>-<k>.jpg`
(`python3 verktoy/bygg_naer.py`). Kvartalsark med hele kvartalet: `rapport/bygg/kvartal-<tegning>.png` (K2–K6, kirka) og kvartal-QA-arkene
`rapport/kvartal-qa/<tegning>.jpg`. Ortofoto-/DOM-utsnitt som bevis: `rapport/bygg/se/` (bare lokalt, ortofotoet er kommunens).
Verktøyene står i LESMEG («Byggene: kjeden, merknadene og det som står på taket»).

## Tall
- Alle 17 tegninger er lest som vektor (Kvartal2–14, kvartal5–7, sistekvartal, tell, Glasshytta, kirka, Tøihuset): 113 hus har
  vinduer og dører fra tegningen (889 elementer), koblet flate for flate i `kilder/fasade-kobling.json`.
- Vegger tegningen ikke viser: Street View der kameraet så veggen (35 vegger), ellers reglene.
- Veggfarge: alle 188 hus som stod med standardveggen har farge (2017-tegningen som vektor der huset er tegnet, ellers nabohuset;
  Street View står foran der det finnes). Tabell: `rapport/bygg/vegg-nye.json`.
- Tegningshusene som avviker fra Street View (100 med vegger kameraet så som tegningen ikke viser) er avgjort hus for hus i `rapport/bygg/sv-avvik.md`: feil vegg (Street View lagt på) 35, feil vindu 23, feil vegg 21, endret siden 2015 19, feil vindu (rettet) 2.
- Regler 01 02 04 06 13 14 17 20 21 grønne (se under).

## Rettet i systemet
- **Døra som egen flate**: hull i veggflaten er ett element; dører/porter/butikkvinduer tegnet som egne flater oppå veggen (også i et
  hakk i bunnkanten) telles; biter av samme dør (fløyer, glass, trapp) slås sammen; brede bånd og mørke skillestriper er ikke vinduer.
- **Etasjerader**: radene samles etter underkanten med enkel kobling (en håndtegnet rad som siger deles ikke); et hus med én etasje får én rad.
- **Street View på vegger tegningen ikke viser** (fasithusene): før fikk de reglene.
- **Sprosser etter zoom** (src/07): kors (post og losholt) minst ~1 px bredt ved største zoom, borte over 0,32 m/px; sprossen i nedre
  ramme (seks ruter) når det er under ~0,1 m/px (største zoom på mobil). Kanten på streken ligger midt på streken, så korset ikke fyller
  vinduet. Målt: nærbilde ved zoom 6 (`rapport/bygg/_arbeid/spr/`, pikseltetthet 1 og 2) og avstandsbilde zoom 3.
- **Takfarge fra ortofoto** ble slettet når veggfargen var satt (tak_fra_ortofoto leste farge_kilde etter vegg_nye): rettet.

## Vegars merknader (kvartalskontrollen 29.10)
Kvartal3
- [x] 67324 port med buet topp, 8 vinduer mot SV, tre takvinduer, ingen arker
- [x] 67324 tilbygg på høyre ende: SØ-enden er valmet i tegningen og i ortofotoet 2024 (`se/artillerismien-se.jpg`); DOM−DTM utenfor
      enden er 0 m, så det står ikke et lavere hus der. Lagt inn som valm (takflate ned mot enden), ikke som eget hus.
- [x] pipene på mønet (alle hus)
- [x] 67308 rødt og lavere (h 3,5 m); døra på langveggen mot SV (flate 168, tegnet utenpå veggen) lagt inn som merknad
- [x] hvitt tilbygg øverst til venstre = bnr-193867316 «Tennishuset» (SEFRAK, i Matrikkelen og kommunekartet). **Beholdt.** Bevis:
      ortofoto 2024 viser en flat grå takflate med rett kant langs kommunekartets omriss i den sørøstre halvdelen av omrisset (resten under
      trekrona); DOM−DTM i omrisset er p50 10,3 m med spredning 5,3 m (trekrone, laserskanningen er eldre enn ortofotoet). Street View ser
      det ikke (bak trærne). Det står derfor med kommunekartets omriss; «hvitt» var standardveggen, som nå har farge.
- [x] 68037 ark mot SØ, ingen pipe, dør i midten; 68053 to dører, én pipe
- [x] 68061 sokkel i naturstein, 6 + 7 takvinduer; vinduet mot sør (SØ-enden av 69572 har 2 + 2 fra tegningen)
- [x] 68061 to (ikke tre) utstikkere: **tre beholdt**. Ortofoto 2024 viser tre framspring med oransje tak mot NØ, DOM ~10 m på alle tre
      (`se/artillerigarden.jpg`). Tegningen 2015 viser to; i dag står det tre.
- [x] alle vinduer med sprosser (se over)
- [ ] gjerde, vei, grusplass: bakke/murer, ikke byggemnet (videresendt tidligere)
Kvartal4BITMP
- [x] 06187 lite hus mot veien, 2 + 2 vinduer
- [x] 71989: boks som 06187. DOM−DTM i omrisset p50 5,8 m / p90 8,0 m (06187: 6,9 / 7,8); modellen stod med gesims 8,7 m. Nå 6,0 m og
      lavt tak som 06187. Tunet mellom 71989 og 68363/06187 er åpent i dag (DOM 0 m, bil i ortofotoet, `se/71989-68363.jpg`), så husene
      står hver for seg som i kommunekartet.
- [x] bygget til venstre for 68401 (71970, og 71962 bak): **beholdt.** DOM−DTM p50 5,6 m (71970) og 6,0 m (71962), spredning 0,9–1,1 m,
      ingen vegetasjon i ortofotoet: tak i dag.
- [x] 68401 stor inngangsdør; 68363 ingen takvindu, 9 vinduer over to etasjer, dør til venstre
Kvartal2BITMP
- [x] hvitt hus + lavere hus nederst til høyre: står nå (68088 og 68673, fra kommunekartet)
- [x] sammenslåtte hus øverst til høyre ved det hvite huset: delt etter kommunekartet (68126, Feiergården 72314, pb-50)
- [x] hjørnehuset nederst til venstre henger sammen med sidehuset: 68142 står inntil 68150 og 68134 (avstand 0)
- [x] husene i midten: omrisset er kommunekartets, høydene Kartverkets; nærbildet `naer/Kvartal2BITMP-*.jpg` viser dem ved siden av tegningen
kirke
- [x] dør i rundbuet omramming, dør helt til høyre, ingen vinduer på tårnfoten mot øst; nytt nærbilde `naer/kirke-1.jpg`

## Funnet i nærbildene og rettet (30.10)
Alle 41 nærbilder er sett (`rapport/bygg/naer/`). Rettet etter dem:
- 12 kommunehus i Gamlebyen stod med gml 0 (Tennishuset, Widdingstua m.fl.) og ble tegnet bleket nesten hvitt uten vinduer: gml 1,
  farge og vinduer; grunnmuren kjørt på nytt, regel 20 grønn (281 kommunehus).
- Krutthuset 69556: pyramidetak som tegningen (var saltak).
- Artillerigården 68061/69572: vinduene er tegnet som svarte felt oppå veggen, ikke hull; talt for hånd: 7 + dør / 8 og 6 + dør / 8 mot SV.
- 68320 (kvartal7): 2 vinduer, dør og rundbuet port nede, 7 vinduer oppe mot gården (lesingen fant 4 av 7).
- Brannstasjonen 68568 og 67308: døra tegnet utenpå veggflaten, lagt inn som merknad.

## Kjent og ikke løst
- Det nye rådhus (bnr-193972012) er bygd med deler (tårn) og tar ikke imot vinduer fra lesingen; tegningen er lest (47 elementer).
- 16308102 (Kvartal14, gul med glasstak) og 68290 (Kvartal8): modellen har veggen som tegningen viser inntil et nabohus (felles vegg),
  så tegningen er ikke lagt på; omrisset er kommunekartets.
- Tøihuset: tegningen er sterkt forkortet (fritegnet), vinduene står i andel av veggen.
