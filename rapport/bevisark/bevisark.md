# Bevisark: kvartaltegning mot 3D-modell

Dato 23.10.2026. Ett ark per tegning i denne mappen: `<Navn>.png` med strektegningen (venstre), modellen forfra (az 40, plakatvinkelen) og modellen bakfra (az 220). Kamerasenteret er snittet av fotavtrykkene til byggene tegningen er koblet til (`kvartal/ut/kobling-<Navn>.json`), zoom etter kvartalets utstrekning. Modellen er `ut/enkel/index.html` versjon 28, bildene tatt med `lag-bilder.mjs` (én nettleserøkt, 34 bilder) og arkene satt sammen med `lag-ark.py`. Råbildene ligger i `kilder/` (tegningene rasterisert fra .ai med pdftoppm 200 dpi, modellbildene, `views.json` med kamera per tegning).

Ingenting er rettet. Dette er observasjoner.

## Tabell

Tallene er summer over byggene tegningen er koblet til i `soc/data/bygg.json`: hvor mange av dem har `fasade_kilde = kvartaltegning`, hvor mange har `tegnet_h`, og antall vinduer (`vind`), piper og arker i data. For kirke finnes ingen koblingsfil; bygg 4 er tatt med direkte.

| Tegning | Bygg koblet | fasade_kilde=kvartaltegning | tegnet_h | vind | piper | arker |
|---|---|---|---|---|---|---|
| Glasshytta | 1 | 0 | 1 | 32 | 2 | 0 |
| Kvartal10 | 17 | 12 | 17 | 410 | 23 | 14 |
| Kvartal11 | 12 | 5 | 12 | 415 | 14 | 16 |
| Kvartal12 | 37 | 16 | 37 | 563 | 45 | 10 |
| Kvartal13 | 4 | 3 | 4 | 198 | 13 | 4 |
| Kvartal14 | 26 | 14 | 26 | 535 | 28 | 8 |
| Kvartal2BITMP | 22 | 11 | 21 | 324 | 28 | 8 |
| Kvartal3 | 14 | 9 | 13 | 293 | 28 | 4 |
| Kvartal4BITMP | 15 | 8 | 15 | 351 | 17 | 9 |
| Kvartal8BITMAP | 24 | 12 | 24 | 585 | 35 | 22 |
| Kvartal9 | 29 | 18 | 29 | 643 | 42 | 20 |
| kvartal5 | 23 | 14 | 23 | 415 | 26 | 11 |
| kvartal6 | 21 | 16 | 21 | 414 | 31 | 14 |
| kvartal7 | 17 | 11 | 17 | 468 | 24 | 11 |
| sistekvartal | 8 | 5 | 8 | 200 | 9 | 3 |
| tell | 1 | 1 | 1 | 22 | 5 | 0 |
| kirke | 1 | 0 | 1 | 0 | 0 | 0 |

To ting i tallene som bør sees på før arkene brukes som fasit:

- 92 av 441 bygg er koblet fra mer enn én tegning, ofte med nøyaktig samme fasadelengde fra begge (Infanterikasernen 3: 226 m fra både Kvartal11 og Kvartal8BITMAP; Ekserserhuset 24: 101 m fra Kvartal10 og Kvartal13; Den gamle spisesal 19: 102 m fra Kvartal3 og kvartal6). Tegningene viser nabokvartal som kontekst, og koblingen tar med seg naboene. Det er derfor «Bygg koblet» er høyere enn antall hus i tegningen for nesten alle ark.
- `tegnet_h` ligger på to ulike skalaer: for de fleste bygg er tegnet_h ≈ 1,7 × h (f.eks. 17,5 mot 10,1), men for en gruppe (10, 11, 162, 173, 188, 229, 248, 336) er tegnet_h 1,8–4,0 m mot h 6,0. Kiørboegården (11) er tegnet med to etasjer og har tegnet_h 3,2. Usikker på hva som er riktig enhet; ser ut som to målemetoder.

## Avvik jeg ser per ark

Modellbildene er tatt på zoom 2,7–3,2 for kvartalene, så enkeltvinduer kan sjelden telles. Der jeg skriver «ser likt ut» mener jeg form, etasjeantall og plassering. Tegningens synsvinkel likner bakfra-bildet (az 220) oftere enn forfra-bildet.

### Glasshytta (bygg 10 Krutthuset)
- Tegningen har to hus: et hvitt hus med utvendig trapp (øverst til venstre) og et lite oransje hus med valmtak og buet dør. Bare det lille huset er koblet (bygg 10).
- Det lille huset har én etasje og én vindusrad i tegningen; modellen (gul vegg, valmtak) har to vindusrader.
- Veggfarge: oransje/rød i tegningen, gul i modellen.
- Det hvite huset med trapp finnes ikke blant de koblede byggene, og jeg ser det ikke i modellbildene. Usikker på om det finnes i modellen.

### Kvartal10
- Tegningen viser ett stort sammenhengende anlegg med gårdsrom og 12–14 arker i rekke på to tak. Ved kamerasenteret (bygg 252/238/240) ser jeg ingen slike arkerekker i modellen. Data: 252 har 1 ark, 238 har 0, 240 har 1.
- Tårn-/kuppelaktig oppbygg bak langhuset øverst i tegningen finner jeg ikke i modellen.
- Langhuset i forkant av tegningen (oransje vegg, to vindusrader, ca. 20 vinduer per rad) likner mest på Infanterikasernen (bygg 3) i modellen, som ligger øst for kirken og er koblet til Kvartal11, ikke Kvartal10. Usikker på om forkantbygget er koblet til riktig modellbygg.
- Det hvite huset med valmtak til venstre i tegningen likner det grå huset med valmtak nord for kirken i modellen. Ser likt ut.
- Koblingen omfatter også Kiørboegården (11) og Ekserserhuset (24), som er hovedbyggene i Kvartal13-tegningen. Samme fasader koblet fra to tegninger.

### Kvartal11 (Infanterikasernen, bygg 3)
- Tegningen: U-formet, to etasjer, ingen arker, 14 piper. Modellen (sett forfra i Kvartal10-arket og bakfra her) har flere arker på taket. Data: 6 arker, 3 piper.
- Gårdsmuren med to porter rundt bakgården i tegningen ser jeg ikke i modellen.
- Modellen har mange flere bygg koblet (12) enn tegningen viser (ett bygg + mur); kamerasenteret havner derfor ved siden av Infanterikasernen forfra.
- Takflatene er enkle saltak i begge. Vindusantall per rad er umulig å telle i modellbildet (zoom 2.7). Usikker.

### Kvartal12
- Tegningen: lukket kvartal med to-etasjes langhus mot gaten og 10–12 mindre hus med saltak rundt et gårdsrom. Modellen viser et tilsvarende tett kvartal. Grov form stemmer.
- Fasadefarger: tegningen beige/oransje/grå/rosa; modellen hvit/gul/rød. Flere bygg ser ut til å ha fått standardfarge.
- Langhuset mot gaten (nederst i tegningen) har to vindusrader med ca. 16 vinduer per rad; i modellen (orange/rød to-etasjes) kan jeg ikke telle. Usikker.
- Modellbildet forfra har brune trær uten krone nederst til venstre. Ser ut som render-/LOD-tilstand, ikke et tegningsavvik.

### Kvartal13 (Kiørboegården 11, Ekserserhuset 24, bygg 20, 21)
- Bakfra-bildet (az 220) matcher tegningens synsvinkel best: Kiørboegården (hvit L-form, rødt tak) og to grå hus ligger likt i begge.
- Kiørboegården: to vindusrader i tegningen, to i modellen. Ser likt ut. Data sier tegnet_h 3,2 m mot h 6,0 m, som ikke stemmer med to etasjer. Usikker på hva tegnet_h måler her.
- Ekserserhuset: langt oransje bygg med gavl i tegningen; langt oransje bygg vest for kirken i modellen. Form stemmer; antall vinduer kan ikke telles.
- Stakittgjerdet langs gaten i tegningen finnes ikke i modellen (steinmur/vei i stedet).

### Kvartal14
- Hjørnebygget med tårn: tegningen har et høyt tårn med spiss og flagg og buegang (arkader) i første etasje. I modellen (bakfra) ser jeg et lavt firkantet tårn uten spiss og ingen buegang. Usikker på om det er samme bygg.
- Langfløyen (rød, to etasjer, ca. 20 vinduer per rad) finnes i modellen som rød to-etasjes bygning. Form stemmer grovt.
- Hvitt to-etasjes hus til høyre i tegningen (ca. 8 vinduer per rad) har en motpart i modellen bakfra. Ser likt ut.
- Lite gult hus med oppbygg på taket midt i kvartalet: finner det ikke i modellen. Usikker.

### Kvartal2BITMP
- Husrekken langs gaten (mørkerødt hjørnehus, gult, beige, hvitt) stemmer grovt i modellen forfra: rødt to-etasjes hjørnehus og to-etasjes naboer.
- Modellen har et langt rødt to-etasjes bygg (brakkeaktig) sør for rekken som ikke er med i tegningen. Trolig nabokvartal, ikke avvik.
- Grå uthus/bakbygg bak husrekken i tegningen: modellen viser hvite/grå hus bak. Usikker på antall.
- Arker: tegningen har takoppbygg på to av husene; i modellen ser jeg ingen arker på rekken.

### Kvartal3
- Langt to-etasjes rødt bygg med tre arker (Den gamle spisesal, 19) i tegningen; modellen har det lange røde bygget, men jeg ser ingen arker. Data: bygg 19 arker-tall se tabell.
- Tegningen viser fire frittliggende småhus pluss et lite firkantet hus; modellen har småhus på samme sted, men ett langt skråstilt hus nederst til venstre i tegningen finner jeg ikke. Usikker.
- Modellbildene har mange trær uten krone (brune) i dette området. Render-/LOD-tilstand, ikke tegningsavvik.

### Kvartal4BITMP
- Hvitt to-etasjes hjørnehus (nederst til høyre i tegningen, ca. 8 vinduer per rad) finnes i modellen bakfra. Ser likt ut.
- Rødt hus med grått valmtak til venstre i tegningen: i modellen er takene røde. Takfarge avviker; usikker på hvilket bygg.
- Gult lite hus midt i kvartalet (tegning) ser jeg ikke i modellen. Usikker.
- Frittliggende hus øverst i tegningen (beige med rødt tak) har motpart i modellen.

### Kvartal8BITMAP
- Lyseblått to-etasjes hus foran til venstre i tegningen finnes i modellen forfra (lyseblått, to vindusrader). Ser likt ut.
- Det grå langhuset bakerst har et lite takoppbygg/takrytter midt på taket i tegningen; i modellen ser jeg ikke noe oppbygg. Usikker på hvilket bygg det er.
- Hvitt langhus foran til høyre (to vindusrader) har en hvit to-etasjes motpart i modellen. Grov form stemmer.
- Infanterikasernen (bygg 3) er koblet til denne tegningen med 226 m fasade, nøyaktig det samme som i Kvartal11. Tegningen viser ingen U-formet kaserne. Koblingen ser feil ut.
- Gult hus bakerst til venstre i tegningen: usikker på motpart.

### Kvartal9
- Tegningen har tre store bygg med mørkegrå/svarte tak bakerst i kvartalet; i modellen er takene i samme område røde. Takfarge avviker.
- Lyseblått hus foran til høyre i tegningen: jeg finner ikke et lyseblått hus på tilsvarende sted i modellen forfra (ett lyseblått hus skimtes bakfra nederst til høyre). Usikker.
- Oransje hjørnehus til venstre (to etasjer) og den lange røde fløyen langs gaten stemmer grovt med modellen.
- Det store grå bakbygget har et lite takoppbygg i tegningen; ikke sett i modellen.
- 29 bygg koblet, men tegningen viser ca. 15 hus. Flere av byggene er også koblet fra Kvartal12 og kvartal6.

### kvartal5
- Gult langhus til venstre i tegningen (to etasjer, ca. 10 vinduer per rad) har en gul to-etasjes motpart i modellen forfra. Ser likt ut.
- Tegningen har ett grått/svart tak (bakerst til høyre) og flere grå uthus midt i kvartalet; i modellen er nesten alle tak røde. Takfarge avviker.
- Rosa/beige hjørnehus nederst i tegningen med to vindusrader: modellen har et hvitt to-etasjes hjørnehus på samme sted. Veggfarge avviker.
- Modellen har tydelig flere og mindre bygg i kvartalet enn tegningen (23 koblet mot ca. 12 hus i tegningen). Usikker på hvilke som er tegnet.
- Vindusantall per rad kan ikke telles i modellbildet. Usikker.

### kvartal6
- Oransje to-etasjes langhus foran i tegningen med fire arker på taket: modellen forfra har et oransje to-etasjes bygg med fire arker midt i bildet. Ser likt ut.
- Grønt hus bakerst til venstre i tegningen: jeg finner ikke et grønt hus i modellen. Veggfarge avviker (modellen hvit/gul?), usikker på hvilket bygg.
- Langhuset bakerst til høyre har mørkegrått tak i tegningen; i modellen er takene i området røde.
- Hvitt/grått hjørnehus til venstre foran i tegningen med buet port: modellen har et hvitt to-etasjes hus på hjørnet. Porten kan jeg ikke se. Usikker.
- 21 bygg koblet; tegningen viser ca. 12 hus. Flere av byggene (218, 220, 225) er også koblet fra Kvartal9.

### kvartal7
- Tegningen viser et lukket kvartal rundt et stort tomt gårdsrom. Kamerasenteret i modellen havner på torget med statuen; gårdsrommet i tegningen er trolig torget, men tegningen har bygg på alle fire sider, mens modellen har gate/åpning. Usikker.
- Grått langhus bakerst med buet port (midt på) i tegningen: modellen bakfra har en lang hvit/grå to-etasjes rekke. Porten ser jeg ikke.
- Rød fløy med eget lite gårdsrom foran til høyre i tegningen: modellen forfra har rødt bygg på hjørnet med gul nabo, men jeg ser ikke det lille gårdsrommet. Usikker.
- Gule to-etasjes hus foran i tegningen (to stykker) finnes i modellen forfra (gule, to vindusrader). Ser likt ut.
- Takfarge: grått tak på bakbygget i tegningen, rødt i modellen.

### sistekvartal
- Tegningen viser en husrekke med fem–seks hus (lyseblått, gult, hvitt, grått) langs én gate pluss et frittliggende rødt langhus. I modellen (bakfra) ser jeg hvitt, gult og grått hus i rekke, men ikke det lyseblå. Veggfarge avviker.
- Det lyseblå hjørnehuset i tegningen har to vindusrader; i modellen forfra er det et hus med grått tak og lyseblå vegg nord for trærne, men ett plan. Usikker.
- Det frittliggende røde langhuset (tegning nederst) med ca. 10 vinduer på langsiden: modellen bakfra har et rødt hus øverst til høyre med færre vinduer. Usikker på om det er samme.
- Svart tak og takoppbygg på et av husene bakerst i tegningen ser jeg ikke i modellen.
- Modellbildene viser mange trær uten krone i dette området (render-/LOD-tilstand, ikke tegningsavvik).

### tell (bygg 12 Ingeniørgården)
- Tegningen har tre bygg: et lite hus med to arker, et L-formet to-etasjes hus (hvit vegg, rødt tak, to vindusrader med 4–5 vinduer per rad og fløy) og en lang lav bod. Bare L-huset er koblet (bygg 12).
- L-huset har to vindusrader i tegningen; i modellen ser det ut som én etasje (h 3,5 m i data, tegnet_h 6,1). Etasjeantall avviker.
- Det lille huset med to arker og boden ser jeg ikke i modellen. Usikker på om de finnes.
- Piper: 5 i data, 1–2 synlige i modellbildet; tegningen viser ingen piper på L-huset. Usikker.

### kirke (bygg 4 Kirken)
- Korsformet skip med spissbuede vinduer stemmer i form mellom tegning og modell. Ser likt ut.
- Tårnet i tegningen har runde/ovale vinduer i to høyder under klokkerommet; modellens tårn har bare de høye buevinduene så langt bildet viser. Usikker (tårntoppen er utenfor bildet ved zoom 5,5).
- Grønn kobberhjelm med lanterne og spir i tegningen: ikke synlig i bevisarket (kuttet), men synlig i Kvartal10-arket, der formen likner.
- Buet hovedportal i gavlen (tegning) kan jeg ikke se i modellen bakfra. Usikker.
- Trærne rundt kirken er uten krone i forfra-bildet (render-/LOD-tilstand).

## Tegninger uten kobling til modellen

Alle 16 kvartaltegningene har koblingsfil (`kvartal/ut/kobling-<Navn>.json`), også kvartal5, kvartal6, kvartal7, sistekvartal og tell. Den eneste uten er **kirke**.

Hva som mangler for kirke:

1. `kvartal/ut/kirke.json` (fasadefilen fra `fasader.py`) finnes ikke. Jeg kjørte `python3 -I fasader.py vek/kirke.json <ut>` til en prøvefil i `kilder/kirke-forsok.json`: den gir 10 flater, 9 vegger, 28 vinduer, 0 dører. Den kjører altså.
2. `kobling.py` på prøvefilen gir `kilder/kobling-kirke-forsok.json`: 9 fasader, 5 koblet, 3 rekker, bygg [4, 230]. Bygg 230 er en nabo og hører ikke til kirken. Fem av ni fasader koblet er svakt, og tårnet er ikke en egen flate i modellens `p` (kirken ligger i feltet `kirke` med `torn`, `skip` og `skiptak`), så koblingen treffer bare skipets vegger.
3. Skal kirke kobles ordentlig, trengs enten at `kobling.py` får lov til å koble mot `kirke.torn`/`kirke.skip` i tillegg til `p`, eller at kirken får tårn og skip som egne polygoner i `p`. Det er en endring i `soc/data` eller `kobling.py`, og jeg har ikke rørt noen av delene.

I tillegg: Glasshytta-tegningen har to hus (hvitt hus med trapp og det lille Krutthuset), men bare Krutthuset (10) er koblet. tell-tegningen har tre bygg, bare Ingeniørgården (12) er koblet. Det er ikke manglende filer, men manglende treff i koblingen.

## Hva som ikke gikk

- Zoom 2,7 på de store kvartalene er for langt unna til å telle vinduer per rad. Et ark per bygg (zoom 5–7, sentrert på hvert koblet bygg) ville gitt tellbare vinduer, men koster ca. 30 s per bilde × 2 × antall bygg.
- Modellbildene har med UI-knappene («Hele byen», +/−). Kosmetisk.
- Flere modellbilder øst og sør i byen viser trær uten krone (brune stammer). Det er modellens tilstand ved `__vis`-kallet, ikke noe i tegningene.
- Kjøringen tok ca. 55 minutter mot budsjett 35: renderingen med programvare-GPU lå på 25–48 s per bilde.
