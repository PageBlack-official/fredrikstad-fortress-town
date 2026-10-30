# Kontroll: Vegars 2015-tegninger mot 3D-modellen (30.10.2026)

Verktøy: `verktoy/kontroll.py` (kamera, render, ark, avvik, md) og `verktoy/kontroll_iso.mjs` (den ekte three.js-scenen fra
`ut/enkel/index.html` tegnet med tegningens projeksjon som projeksjonsmatrise; flate farger, id-bilde, normalbilde; ingen trær,
bakke, murer). Ark: `rapport/kontroll/<tegning>.png` med fire felt: tegningen | modellen med id-etiketter | 50 % oppå | differanse
(rødt = bare tegningen, blått = bare modellen). Tall: `avvik.json`. Denne fila: det jeg så på hvert ark + tallene under.

## Projeksjonen (det som er målt, ikke antatt)

- Tegningene er parallellprojeksjoner med loddrett loddrett, men de er **ikke** én ortografisk projeksjon: høydeskalaen er
  overdrevet ulikt fra tegning til tegning (tegnet vegghøyde / Kartverkets h går fra 2,4 pt/m i Kvartal8 til 6,6 pt/m i
  sistekvartal, mot 4,8–5,3 pt/m på bakken). Derfor er høydeskalaen målt per tegning på veggene som er lest for hånd
  (kilder/fasade-tegning), og høyder er rapportert relativt til tegningens egen median.
- Tegneretningen på bakken er felles (dreiing −8 til −15°, helning 45,5°, fra de seks tegningene der fri tilpasning traff
  best). Målestokk og forskyvning er tilpasset hver tegning (omriss + flatekanter); hver blokk (hus inntil hverandre) får egen
  forskyvning, fordi tegningene er frihånd satt sammen av biter.
- Registrering, målt som avstanden fra modellhusenes synlige kanter til tegningens flatekanter: median 1,5–3,5 pt (5–10 px ved
  3 px/pt) for 15 av 18 tegninger. «Innen noen få piksler» holder for fasadekantene ut mot gata i Kvartal4, 8, 10, 12, 13,
  kvartal5, sistekvartal, Glasshytta, Tøihuset; i gårdsrommene ligger det typisk 3–6 pt unna (frihånd).
- Fri tilpasning (eget kamera per tegning, 7 parametre) ble prøvd først og forkastet: den fant helning 21–50° og knuste
  høydene. Den gamle tilpasningen i fasade_tegning.py (`tilpass_globalt`) ga høydeskala 2,7 på Kvartal12 og treffer ikke.

## Lar seg ikke registrere (si fra)

- **Kvartal11**: koblingen (kilder/kvartal-kobling.json) peker på hus i Kvartal12 (867782, 867839, 867820) og 868568. Tegningen
  viser ett stort U-formet tre-etasjes bygg med ti piper. Det bygget er ikke blant kandidatene, så arket sammenligner feil hus.
  Kvartal11 må kobles på nytt (finne modellhuset/-husene til det store bygget) før avvik kan telles. Tallene for Kvartal11 er ugyldige.
- **Kvartal3**: tegningen er biter spredt over arket (to langhus øverst, et hus med gang, et rødt langhus, en kube). Bare tre
  modellhus (868061, 869572, 868045) fanges; de andre bitene har ikke modellhus innenfor trykkets plassering. Langbygget
  868061/869572 ligger forskjøvet. Bitene må kobles for hånd.
- **Kvartal4BITMP**: alle fem blokkene måtte flyttes (opptil 25 pt) og differansen er stor rødt/blått overalt. Enten er
  tegningen komponert fritt, eller koblingen har feil hus (868339 står også i kvartal7). Ikke til å stole på hus for hus.
- **kvartal6**: venstre del og gårdsrommet treffer, men hele den nederste raden til høyre (oransje fasader langs gata) er rødt
  = modellen har ingen hus der i settet. Trolig mangler husene i koblingen (ligger i nabokvartalets liste), ikke i modellen.
- **kirke**: kirkas `h` i data er 0,01 (formen ligger i `kirke`), så silhuetten til tilpasningen er bare fotavtrykket.
  Kirka ligger forskjøvet og mindre; høydeskalaen er median av de andre tegningene. Det kvalitative under holder likevel.
- **tell** og **Glasshytta**: ett hus hver treffer; resten av arket er biter som ikke har modellhus i settet (huset på
  hvelvet i Glasshytta, det lille gavlhuset og skuret i tell).

## Det jeg så på hvert ark

- **Kvartal2BITMP**: venstre del treffer. Fronten (972292) er grå vegger i modellen, gule/beige hus i tegningen; tegningen har
  mørke tak der modellen har rødt (972292). Høyre fløy: tegningen har en lang fløy med rødt tak bakover (rødt felt, ~3300 pt²)
  der modellen bare har det lille 868673. Gårdsrommet: tegningen har færre, adskilte småhus; modellen har en klynge (300399132,
  971350, 972306, 972373, pb-34). Rødt felt øverst til høyre er nabokvartalet.
- **Kvartal3**: se over. Langbygget er ett hus med jevnt rødt tak og valmet ende i tegningen; modellen deler det i 868061 (rødt)
  og 869572 (mørkt brunt tak) - fargeskifte midt på taket som tegningen ikke har.
- **Kvartal4BITMP**: se over. Synlig uansett plassering: 868371 har mørkt grått tak og mørkerød vegg i modellen, tegningen har
  rødt tak og lys vegg; 868525 har gul vegg og grått tak i modellen, rødt i tegningen.
- **kvartal5**: god registrering. 868231 (bak) er grått tak med valm i modellen, tegningen har to hus med røde saltak og gavler
  (slått sammen). 868215 har nesten svart tak i modellen, grått i tegningen. Midtrekka: tegningen har tre røde hus side om side +
  ett grått; modellen har ett stort rødt tak (987397) - slått sammen. 6251218 har mørkebrunt tak i modellen, rødt i tegningen.
- **kvartal6**: se over. Det grønne huset (971334) og den grå rekka treffer. 867952 (hjørnet) er mørkerød vegg med svart tak i
  modellen; tegningen har oransje vegg med rødt tak og takvinduer.
- **kvartal7**: god registrering. 868320 har grått tak, tegningen rødt; tegningen har to hus (hvitt + lyst) der modellen har ett.
  867626 grått tak i modellen, rødt i tegningen. 971369: tegningen har to grå/røde fasader med saltak, modellen ett hus med
  halvvalm. 868347 er blågrå i modellen, mørk grå i tegningen. Rådhuset 868355 har ingen dører i modellen; tegningen viser 3-4.
- **Kvartal8BITMAP**: god registrering. 13414904: tegningen har lyseblå vegger og et lavt tilbygg foran (rødt felt 2500 pt²);
  modellen har grå vegger. 868282 har grått tak i modellen, rødbrunt i tegningen. 868290 treffer i form (grått valmtak).
- **Kvartal9**: god registrering. 867944 har mørkebrunt tak i modellen, tegningen har lyst rødt tak på hvite vegger.
  Gårdsrommet har røde hull (tegnede flater uten modellhus) og blå klumper (modellhus uten tegning) - modellens gårdsromsbygg
  ligger annerledes enn tegningens.
- **Kvartal10**: god registrering unntatt 867596 (det grå huset til venstre), som ligger 10-15 pt til høyre for tegningen.
  987370 (fronten) er rosabrun i modellen, oransje i tegningen. Tegningen har et lite tårn på 868711 og arkader på 13394024;
  modellen har verken tårn eller arkader. Tegningen har mur langs gata til venstre (ikke bygg).
- **Kvartal11**: se over - ugyldig.
- **Kvartal12**: god registrering (2,5 pt). Det hovedagenten så, stemmer: frontrekka mot hjørnet (972462 + 867715) har store grå
  tak i modellen der tegningen har rødt; 867715 er mørkerød i modellen, lys oransje i tegningen. Inne i gårdsrommet til venstre
  har tegningen et hus med rosa gavl og rødt tak (rødt felt 4000 pt², ved 867820/972772) som modellen mangler; 972772 er et lite
  hvitt hus med grått tak i modellen. Gårdsrommet er åpent i tegningen (ett langt hus 868592 + en liten blokk); modellen fyller
  det med røde tak (868606, 972446, 972608, 972594). 867731 har tre runde arker på hvitt hus i tegningen, blågrå vegg og grått tak i
  modellen. 867758 (høyre ende): tegningen har to hus, modellen ett.
- **Kvartal13**: brukbar registrering. 867499 er ett stort U-formet hus med rødt valmtak i modellen; tegningen har hvite vegger,
  en rød fløy og en grå del - flere hus. 867502: tegningen har tre grå hus (mørkt, grått, lysegrått tak), modellen ett rødt.
  867510: tegningen oransje med halvvalm, modellen gulbrun med valm. Tegningen har en mur (gårdsmur) til høyre og et plankegjerde.
- **Kvartal14**: registrering 3,5 pt. Gamle rådhus (972012) mangler tårnet i modellen (rødt felt øverst til venstre) og har
  ikke arkadevinduene. 16308102 er et stort grått tak i modellen; tegningen har lyse gårdsbygg med pyramidetakvindu. 867693 er
  grønn i modellen, grå/hvit i tegningen.
- **sistekvartal**: god registrering. 870201 er grå i modellen, lyseblå i tegningen. Høyre ende (870252): tegningen har et grått
  hus med takarker + et hvitt hus; modellen ett hus med rødt tak. Det frittstående røde huset nede til venstre har ikke modellhus
  i settet (bit).
- **tell**: 867677 treffer (L-form, hvite vegger, rødt tak). Det lille gavlhuset med to takvinduer og det oransje skuret har
  ikke modellhus; modellen har et langt lavt hus (…634) der tegningen har det lille gavlhuset.
- **Glasshytta**: 869580 har rødbrune vegger (som taket) og et ekstra tverrtak i modellen; tegningen har oransje vegger og
  enkelt valmtak med buet dør.
- **kirke**: tegningen har saltak med gavler på korsarmene; modellen har valmede korsarmer som møtes i midten. Tårnet er
  høyere og slankere i tegningen (lanterne + spir); modellens tårn er lavere. (Tallene for kirka er usikre, se over.)
- **Tøihuset**: god registrering. Veggene er rødbrune som taket i modellen; tegningen har oker/oransje vegger. Tegningen har
  rundbuevinduer og hvite portaler med grønne porter; modellen har små firkantvinduer og grå dører. Modellen har ~14 piper langs
  mønet, tegningen 2-3 takhatter. Den indre fløyen er dypere i tegningen (rødt felt, 6400 pt²).

## De 30 alvorligste avvikene (sett på arkene, tallene i parentes fra avvik.json)

1. Kvartal11 - hele tegningen: det store U-bygget sammenlignes ikke med noe; koblingen peker på Kvartal12-hus. (ugyldig)
2. Kvartal12 - hus med rosa gavl og rødt tak i gårdsrommet ved 867820/972772 mangler i modellen (tegnet uten modell, 4076 pt²).
3. Kvartal12 - 972462 + 867715: store grå tak over frontrekka og hjørnet, tegningen har røde tak (972462 takfarge ΔE 4x, 867715 ΔE grå mot rød).
4. Kvartal12 - gårdsrommet: modellen har 868606, 972446, 972608, 972594 der tegningen har åpent gårdsrom (868606 IoU 0,38, 972446 IoU 0,40).
5. kvartal5 - 987397: ett stort rødt tak der tegningen har tre-fire hus (gesims 1,41, tegnet høyere).
6. kvartal5 - 868231: grått valmtak, tegningen har to hus med røde saltak (slått sammen, takform sal/halvvalm, takfarge ΔE 54).
7. Kvartal14 - Gamle rådhus 972012 mangler tårnet og arkadene (gesims 1,38).
8. Kvartal13 - 867499: ett U-hus med rødt valmtak, tegningen har flere hus med hvite vegger og grå del (slått sammen).
9. Kvartal13 - 867502: ett rødt hus, tegningen har tre grå hus.
10. kvartal7 - 868320: grått tak og ett hus, tegningen har rødt tak og to hus (slått sammen, takfarge ΔE 56).
11. kvartal7 - 971369: ett hus med halvvalm, tegningen har to fasader med saltak (slått sammen, takform).
12. Tøihuset 870279: vegger i takfarge (rødbrun) der tegningen har oker; firkantvinduer der tegningen har rundbuer; ~14 piper mot 2-3.
13. Kvartal2BITMP - høyre fløy: tegningen har en lang fløy med rødt tak der modellen bare har 868673 (3275 pt²).
14. Kvartal2BITMP - 972292: grå vegger og rødt tak, tegningen har gule/beige vegger og mørkt tak (silhuett 0,55).
15. kirke 867529: korsarmer med valm, tegningen har saltak med gavler; tårnet lavere enn i tegningen.
16. Kvartal8BITMAP - 13414904: grå vegger, tegningen lyseblå; tilbygg foran mangler (2526 pt²).
17. Kvartal12 - 867731: blågrå vegg og grått tak, tegningen hvitt hus, rødt tak, tre runde arker (takform sal/halvvalm).
18. Kvartal12 - 867758: ett hus, tegningen to; tegningen har 19 vinduer i tre rader på frontveggen, modellen 12.
19. Kvartal10 - 868711/13394024: tårnet og arkadene i tegningen finnes ikke i modellen.
20. Kvartal14 - 16308102: stort grått tak, tegningen har lyse gårdsbygg med pyramidetakvindu.
21. sistekvartal - 870252: ett hus med rødt tak, tegningen grått hus med arker + hvitt hus (gesims 0,53, takfarge ΔE 64).
22. Kvartal3 - 868061/869572: ett langhus i tegningen er to i modellen med ulik takfarge; resten av bitene ukoblet.
23. kvartal7 - 868355 Det gamle rådhus: ingen dører i modellen, tegningen viser 3-4 (vinduer 7 mot 8 ellers likt).
24. kvartal7 - 867626: grått tak (ΔE 56) og takform halvvalm; tegningen rødt valmtak.
25. Kvartal9 - 867944: mørkebrunt tak på grått, tegningen lyst rødt tak på hvitt (slått sammen, 2 fasader).
26. kvartal5 - 868215: nesten svart tak, tegningen grått; 4 vinduer i modellen på vegg 4 der tegningen har ingen.
27. Kvartal8BITMAP - 868282: grått tak, tegningen rødbrunt; takform valm/halvvalm.
28. Glasshytta 869580: rødbrune vegger og ekstra tverrtak; tegningen oransje vegger og enkelt valmtak.
29. Kvartal14 - 867693: grønn vegg og grått tak, tegningen grå/hvit vegg og rødt tak; 8 vinduer i tegningen mot 1 i modellen (vegg 3).
30. kvartal6 - 867952: mørkerød vegg og svart tak, tegningen oransje med rødt tak og takvinduer (registreringen er svak her).

Mange av fargeavvikene over har Street View som kilde i modellen (`farge_kilde`); Vegar har sagt at Street View 2024 går foran
for dagens farge, så de er merket «avvik med grunn» i tabellene. Takfarger grått mot rødt er likevel verdt et blikk: flere
står med «Street View (aug. 2010)», som er eldre enn tegningen.

## Forbehold om tallene

- Omriss-IoU er i bildeplanet; frihånd og blokkforskyvning gir IoU 0,5-0,7 også på hus som er riktige. Under 0,45 er verdt å se på.
- Vinduer: der veggen er lest for hånd (kilder/fasade-tegning), er tegningens tall derfra; ellers hull i veggflaten slått
  sammen (sprossene). Det siste overteller av og til (dører, portaler og butikkvinduer blir flere hull).
- «Slått sammen» = to eller flere tegnede fasader (ikke-overlappende veggflater) på én modellvegg. Sokkel/etasjeskille med
  egen farge kan gi falske treff; feil krever ulike farger.
- Arker og piper fra tegningen er grove anslag fra små flater på taket (takvinduer telles med) og gir bare «avvik» ved forskjell ≥ 3.
- Takform fra tegningen: gavl (spiss vegg) og trekantede takflater. Når ingen ende er synlig, står «ukjent» og ingen dom.
- Gesims: tegnet vegghøyde i hjørnene / (tegningens høydeskala × h). Hus foran kan skjule bunnen og gi for lav verdi.
- «Tegnet uten modellhus»: mange små grupper (< 600 pt²) er bare frihåndsforskyvning, ikke manglende hus. De store er nevnt over.
- Tallene for Kvartal11 er ugyldige, Kvartal3, Kvartal4BITMP, kvartal6 (høyre rad) og kirke er usikre.

## Totaltall per kategori (maskinelt, se forbeholdene over)

| kategori | feil | avvik | avvik med grunn | ok |
|---|---|---|---|---|
| finnes | 3 | 18 | 0 | 184 |
| omriss | 69 | 73 | 0 | 42 |
| mone | 40 | 41 | 0 | 102 |
| takform | 28 | 0 | 0 | 156 |
| takfarge | 15 | 3 | 27 | 127 |
| arker | 0 | 40 | 0 | 144 |
| piper | 0 | 30 | 0 | 154 |
| gesims | 47 | 17 | 0 | 68 |
| veggfarge | 4 | 2 | 18 | 81 |
| vinduer | 60 | 22 | 0 | 26 |
| dorer | 0 | 56 | 0 | 52 |
| slaatt_sammen | 16 | 12 | 0 | 0 |
| tegnet_hus_uten_modell | 86 | 0 | 0 | 0 |

## Registrering per tegning

| tegning | hus | dreiing | helning | bakke pt/m | høyde pt/m (kilde) | kanter fra tegningen, median | hus innen 3 pt | blokker flyttet > 3 pt | koblet, men utenfor tegningen |
|---|---|---|---|---|---|---|---|---|---|
| Kvartal2BITMP | 19 | -12.0° | 45.5° | 4.83 | 4.90 (tegnede vegger) | 2.0 pt = 6.0 px | 84 % | 1 av 3 | - |
| Kvartal3 | 3 | -11.1° | 45.5° | 5.26 | 3.33 (tegnede vegger) | 2.83 pt = 8.5 px | 67 % | 2 av 2 | 869556, 868053, 868037, 867324, 868088 |
| Kvartal4BITMP | 9 | -15.5° | 45.5° | 4.88 | 3.49 (tegnede vegger) | 1.54 pt = 4.6 px | 100 % | 5 av 5 | 868363, 868428, 971970, 868398, 971962, 868401 |
| kvartal5 | 16 | -12.4° | 45.5° | 4.91 | 3.45 (tegnede vegger) | 2.1 pt = 6.3 px | 81 % | 2 av 3 | - |
| kvartal6 | 18 | -10.9° | 45.5° | 4.89 | 3.76 (tegnede vegger) | 3.31 pt = 9.9 px | 33 % | 0 av 1 | 868045 |
| kvartal7 | 17 | -13.8° | 45.5° | 4.61 | 3.10 (tegnede vegger) | 2.56 pt = 7.7 px | 53 % | 0 av 1 | 6251765, 868290, 13394024, 867588 |
| Kvartal8BITMAP | 18 | -13.0° | 45.5° | 4.78 | 2.43 (tegnede vegger) | 1.75 pt = 5.2 px | 89 % | 0 av 1 | - |
| Kvartal9 | 23 | -14.5° | 45.5° | 5.26 | 3.00 (tegnede vegger) | 2.61 pt = 7.8 px | 56 % | 1 av 2 | 868614 |
| Kvartal10 | 15 | -8.0° | 45.5° | 4.82 | 3.62 (tegnede vegger) | 1.72 pt = 5.2 px | 87 % | 1 av 3 | 971873 |
| Kvartal11 | 5 | -14.9° | 45.5° | 5.27 | 4.08 (tegnede vegger) | 2.2 pt = 6.6 px | 60 % | 3 av 4 | 867537 |
| Kvartal12 | 26 | -11.8° | 45.5° | 4.51 | 4.75 (tegnede vegger) | 2.5 pt = 7.5 px | 62 % | 0 av 1 | - |
| Kvartal13 | 4 | -12.8° | 45.5° | 4.97 | 2.89 (tegnede vegger) | 2.12 pt = 6.4 px | 100 % | 3 av 4 | - |
| Kvartal14 | 22 | -12.2° | 45.5° | 5.24 | 4.74 (tegnede vegger) | 3.46 pt = 10.4 px | 41 % | 4 av 5 | 972403, 867847, 972071 |
| sistekvartal | 7 | -12.7° | 45.5° | 5.07 | 6.58 (tegnede vegger) | 2.12 pt = 6.4 px | 71 % | 1 av 1 | 870198 |
| tell | 2 | -12.0° | 45.5° | 5.02 | 5.02 (tegnede vegger) | 3.83 pt = 11.5 px | 50 % | 1 av 2 | - |
| Glasshytta | 1 | -10.6° | 45.5° | 5.10 | 4.03 (tegnede vegger) | 1.7 pt = 5.1 px | 100 % | 1 av 1 | 869548 |
| kirke | 1 | -13.8° | 45.5° | 5.54 | 3.47 (median av de andre tegningene) | 4.37 pt = 13.1 px | 0 % | 1 av 1 | - |
| Toihuset | 1 | -14.8° | 45.5° | 4.98 | 5.01 (tegnede vegger) | 2.03 pt = 6.1 px | 100 % | 0 av 1 | - |

## Per hus (maskinelt)

Alvor: **F** feil, A avvik, G avvik med grunn (modellens farge har en kilde nyere enn tegningen 2015: Street View 2016+ for vegg, ortofoto 2024 for tak). Tomt = ok eller ikke målt.

### Kvartal2BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972373 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 868118 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 868126 |  |  | A | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 0.60 (tegningen lavere) |
| 868134 |  |  |  | **F** |  | **F** |  |  | **F** |  | A |  | gesims: tegnet/modell 1.52 (tegningen høyere); takform: tegning valm, modell halvvalm; vinduer: vegg 2 (17.2 m): tegning 0 vinduer i rader [], modell 7 i rader [7] |
| 868150 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 5 (10.0 m): tegning 0 vinduer i rader [], modell 8 i rader [4, 4] |
| 868088 |  |  |  | **F** | A |  | G |  |  | A |  | A | gesims: tegnet/modell 1.45 (tegningen høyere) |
| 972292 |  |  | A | A | **F** |  | G | G | **F** | A | A | A | vinduer: vegg 2 (15.8 m): tegning 7 vinduer i rader [3, 2, 2], modell 5 i rader [3, 2] |
| 972314 |  |  | **F** | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 0.38 (tegningen lavere) |
| 972365 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 868096 |  |  | A |  |  |  |  |  | **F** | A | A | A | vinduer: vegg 8 (15.4 m): tegning 0 vinduer i rader [], modell 9 i rader [7, 2] |
| 868142 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 3 (15.1 m): tegning 5 vinduer i rader [5], modell 10 i rader [5, 5] |
| 972306 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 971350 |  |  | **F** |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (188, 190, 192) (grå/svart), modell (175, 96, 83) (rød), ΔE 47.1; modellens farge: 2019-trykket (dømt) (ortofoto 2024: taket ligger i slagskygge) |
| 972349 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 868681 |  | A | A | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.53 (tegningen lavere); vinduer: vegg 2 (10.4 m): tegning 0 vinduer i rader [], modell 5 i rader [3, 2] |
| 868703 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 300399132 |  |  | A |  |  |  |  |  | **F** |  |  |  | vinduer: vegg 2 (6.2 m): tegning 0 vinduer i rader [], modell 3 i rader [3] |
| 868673 |  |  | A | **F** |  |  |  |  | **F** | A | A |  | gesims: tegnet/modell 0.57 (tegningen lavere); vinduer: vegg 7 (14.1 m): tegning 6 vinduer i rader [2, 2, 2], modell 4 i rader [4] |
| pb-54 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972373 (9312 pt², ~2 hus); ved 972306 (881 pt², ~1 hus); ved 868134 (642 pt², ~1 hus); ved 300399132 (676 pt², ~1 hus); ved 868673 (3275 pt², ~1 hus)

### Kvartal3

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868061 |  |  | **F** |  | **F** |  | G |  | A | A |  | A |  |
| 868045 |  | **F** |  |  |  |  |  |  | **F** | A |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); vinduer: vegg 3 (44.9 m): tegning 4 vinduer i rader [1, 3], modell 7 i rader [7] |
| 869572 |  | **F** | A |  |  |  |  |  |  | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 8; ulike farger: 2) |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868061 (4602 pt², ~2 hus); ved 868061 (6623 pt², ~2 hus); ved 868061 (260 pt², ~1 hus)

### Kvartal4BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868339 |  |  | A |  | A |  |  |  |  |  | A | A |  |
| 971954 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 868371 |  |  |  |  |  |  |  | G |  |  | A |  |  |
| 868525 |  | **F** | **F** | **F** |  | **F** | G | G | A | A | A | A | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 4; ulike farger: 3); gesims: tegnet/modell 0.57 (tegningen lavere); takform: tegning valm, modell halvvalm |
| 971946 |  |  | **F** |  |  |  |  | A |  |  |  |  |  |
| 194006187 |  |  | **F** |  | A |  |  |  | **F** |  | A | A | vinduer: vegg 1 (8.3 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 971989 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 971202 |  |  | A |  | A |  |  |  | A |  | A | A |  |
| pb-48 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868525 (1013 pt², ~1 hus); ved 971946 (1671 pt², ~2 hus); ved 971954 (537 pt², ~1 hus); ved 971989 (321 pt², ~1 hus); ved 971954 (320 pt², ~1 hus)

### kvartal5

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868223 |  | **F** |  |  |  | **F** |  |  |  | A | A |  | slaatt_sammen: tegningen har 4 fasader på én modellvegg (vegg 0, 3; ulike farger: 2); takform: tegning valm, modell halvvalm |
| 6242812 |  |  | A | A | A |  |  |  | **F** | A |  |  | vinduer: vegg 2 (10.4 m): tegning 8 vinduer i rader [2, 2, 2, 1, 1], modell 4 i rader [2, 2] |
| 868231 |  | **F** |  |  | A | **F** |  |  | A |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 7; ulike farger: 2); takform: tegning sal, modell halvvalm |
| 16290424 |  |  | A | **F** | A | **F** |  | **F** | **F** |  | A |  | gesims: tegnet/modell 2.19 (tegningen høyere); takform: tegning sal, modell halvvalm; takfarge: tegning (239, 240, 240) (hvit), modell (175, 96, 83) (rød), ΔE 58.8; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått); vinduer: vegg 4 (8.6 m): te |
| 6251323 |  |  |  |  |  |  |  |  | A | A |  |  |  |
| 987397 |  |  | A | **F** | A |  |  |  | **F** | A |  |  | gesims: tegnet/modell 1.41 (tegningen høyere); vinduer: vegg 1 (28.4 m): tegning 7 vinduer i rader [1, 6], modell 10 i rader [10] |
| 868207 |  | A |  |  |  | **F** |  | **F** | **F** | A | A | A | takform: tegning valm, modell halvvalm; takfarge: tegning (237, 213, 196) (oransje/brun), modell (172, 96, 82) (rød), ΔE 45.6; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått); vinduer: vegg 5 (2.4 m): tegning 2 vinduer i rader [1, 1], modell |
| 6251331 |  |  |  |  |  | **F** |  |  |  |  |  |  | takform: tegning sal, modell halvvalm |
| 6251218 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 868215 |  |  |  | **F** |  | **F** |  |  | **F** |  | A | A | gesims: tegnet/modell 1.38 (tegningen høyere); takform: tegning sal, modell halvvalm; vinduer: vegg 4 (8.8 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972195 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 972187 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 972225 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972209 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 971342 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972217 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972187 (172 pt², ~1 hus); ved 16290424 (301 pt², ~1 hus); ved 6251323 (659 pt², ~1 hus)

### kvartal6

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6247822 |  |  | A |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 6 (14.6 m): tegning 9 vinduer i rader [4, 2, 3], modell 7 i rader [4, 3] |
| 867979 |  | A | **F** | A |  |  |  |  | A | A | A | A |  |
| pb-6 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868029 |  |  | **F** | A | A |  |  |  | **F** | A |  |  | vinduer: vegg 0 (9.5 m): tegning 8 vinduer i rader [1, 1, 3, 2, 1], modell 2 i rader [2] |
| 971334 |  |  | A | **F** |  |  | G |  | **F** |  |  |  | gesims: tegnet/modell 0.31 (tegningen lavere); vinduer: vegg 7 (8.6 m): tegning 4 vinduer i rader [2, 2], modell 3 i rader [1, 1, 1] |
| 868630 |  |  | **F** |  | **F** | **F** |  |  |  |  |  |  | takform: tegning valm, modell halvvalm |
| 868002 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 971318 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972179 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867952 |  | **F** | A |  | **F** |  | G |  | **F** | A |  | A | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 1, 2; ulike farger: 3); vinduer: vegg 2 (3.4 m): tegning 12 vinduer i rader [2, 2, 1, 1, 6], modell 2 i rader [1, 1] |
| 867995 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868010 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971296 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868665 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868657 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867987 |  | A | A | A |  |  |  |  | **F** | A |  |  | vinduer: vegg 7 (14.9 m): tegning 6 vinduer i rader [2, 4], modell 4 i rader [4] |
| 972160 |  |  | **F** |  | **F** |  |  |  |  |  | A |  |  |
| 868649 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868002 (413 pt², ~1 hus); ved 868630 (129 pt², ~1 hus); ved 6247822 (15743 pt², ~4 hus)

### kvartal7

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868355 |  |  |  |  |  |  |  |  | A | A | A |  |  |
| 868339 |  | **F** |  | A |  |  |  |  | **F** | A | A |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 2 (17.2 m): tegning 10 vinduer i rader [2, 4, 4], modell 6 i rader [5, 1] |
| 867626 |  | A |  |  |  | **F** |  |  | **F** | A | A | A | takform: tegning valm, modell halvvalm; vinduer: vegg 2 (19.9 m): tegning 9 vinduer i rader [8, 1], modell 12 i rader [6, 6] |
| 868347 |  |  | **F** |  |  |  | **F** |  | **F** | A |  |  | veggfarge: tegning (239, 240, 240) (hvit), modell (254, 234, 174) (oransje/brun), ΔE 31.9; modellens farge: 2019-trykket (dømt); vinduer: vegg 6 (12.8 m): tegning 4 vinduer i rader [1, 1, 2], modell 2 i rader [2] |
| 971369 |  | **F** |  |  |  | **F** |  |  | A | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 7; ulike farger: 2); takform: tegning sal, modell halvvalm |
| 868320 |  | **F** |  |  |  |  |  |  |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2) |
| 867618 |  | **F** |  |  |  |  |  |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); vinduer: vegg 3 (11.8 m): tegning 8 vinduer i rader [2, 4, 2], modell 5 i rader [1, 2, 2] |
| 918239 |  |  | **F** |  | A | **F** |  |  |  |  | A | A | takform: tegning sal, modell halvvalm |
| 868525 |  |  | **F** | **F** | **F** |  |  |  |  |  | A |  | gesims: tegnet/modell 0.53 (tegningen lavere) |
| 971946 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 6275109 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 991718 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 971202 |  |  | **F** |  | **F** |  |  | A |  |  |  |  |  |
| 868517 |  |  | **F** | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 0.51 (tegningen lavere) |
| pb-28 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-33 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 1.85 (tegningen høyere) |
| pb-47 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved pb-47 (530 pt², ~1 hus); ved 867626 (1362 pt², ~1 hus)

### Kvartal8BITMAP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972152 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868258 |  |  | A | A | A |  | G |  | **F** | A | A | A | vinduer: vegg 7 (6.9 m): tegning 0 vinduer i rader [], modell 6 i rader [3, 3] |
| pb-5 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 0.39 (tegningen lavere) |
| 868541 |  |  | **F** | **F** |  |  |  |  | A |  |  |  | gesims: tegnet/modell 2.33 (tegningen høyere) |
| 868266 |  |  |  | **F** |  | **F** |  |  | **F** |  | A |  | gesims: tegnet/modell 1.64 (tegningen høyere); takform: tegning valm, modell halvvalm; vinduer: vegg 2 (15.4 m): tegning 0 vinduer i rader [], modell 9 i rader [4, 5] |
| 868274 |  | A |  | **F** |  | **F** |  |  | A | A | A |  | gesims: tegnet/modell 1.45 (tegningen høyere); takform: tegning sal, modell halvvalm |
| 868312 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868282 |  | A |  |  |  | **F** |  |  | **F** | A |  |  | takform: tegning valm, modell halvvalm; vinduer: vegg 2 (11.3 m): tegning 3 vinduer i rader [3], modell 8 i rader [4, 4] |
| 13414904 |  | A | A |  |  |  |  | G | **F** | A | A | A | vinduer: vegg 3 (6.6 m): tegning 4 vinduer i rader [1, 3], modell 9 i rader [3, 3, 3] |
| 972136 |  |  | A | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 2.54 (tegningen høyere) |
| 300279164 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 868290 |  |  |  | **F** |  | **F** |  |  | **F** |  |  |  | gesims: tegnet/modell 0.55 (tegningen lavere); takform: tegning sal, modell halvvalm; vinduer: vegg 5 (5.4 m): tegning 0 vinduer i rader [], modell 5 i rader [3, 1, 1] |
| 868533 |  |  | A | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 0.26 (tegningen lavere) |
| pb-13 |  |  | A |  |  | **F** |  |  |  |  |  |  | takform: tegning valm, modell halvvalm |
| 972144 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971288 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971261 |  |  | A | **F** |  | **F** |  | G | A |  |  |  | gesims: tegnet/modell 0.55 (tegningen lavere); takform: tegning valm, modell halvvalm |
| 16313173 |  |  | A |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868290 (200 pt², ~1 hus); ved 868290 (716 pt², ~2 hus); ved 13414904 (2526 pt², ~2 hus); ved 868282 (179 pt², ~2 hus); ved 868258 (1042 pt², ~1 hus); ved 972144 (223 pt², ~1 hus)

### Kvartal9

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972489 |  |  | A | **F** | **F** |  |  | **F** |  |  |  |  | gesims: tegnet/modell 2.02 (tegningen høyere); takfarge: tegning (239, 240, 240) (hvit), modell (188, 188, 192) (grå/svart), ΔE 18.5; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 867855 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 867936 |  |  |  |  |  |  | G |  | A | A | A |  |  |
| 867863 |  |  | A |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 7 (30.2 m): tegning 12 vinduer i rader [12], modell 19 i rader [9, 10] |
| 867901 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867944 |  | **F** | A |  |  |  |  |  |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2) |
| 972519 |  |  | A |  | **F** | **F** |  |  |  |  |  |  | takform: tegning valm, modell halvvalm |
| 972624 |  |  | A |  |  | **F** |  |  |  |  | A |  | takform: tegning valm, modell halvvalm |
| 867928 |  |  |  |  |  | **F** |  | G |  |  | A |  | takform: tegning valm, modell halvvalm |
| 867898 |  |  | A |  |  | **F** |  |  | A |  |  | A | takform: tegning valm, modell halvvalm |
| 868622 |  |  |  | A | A |  |  |  |  |  |  |  |  |
| 868592 |  |  | A | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 2.21 (tegningen høyere) |
| pb-14 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 971377 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 971385 |  |  | **F** | **F** | A |  |  |  | A |  |  |  | gesims: tegnet/modell 1.87 (tegningen høyere) |
| 972543 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 0.60 (tegningen lavere) |
| 972535 |  |  | **F** | **F** | **F** |  |  | **F** |  |  |  |  | gesims: tegnet/modell 0.42 (tegningen lavere); takfarge: tegning (226, 204, 187) (oransje/brun), modell (175, 96, 83) (rød), ΔE 43.7; modellens farge: 2019-trykket (dømt) (ortofoto 2024: taket ligger i slagskygge) |
| 972616 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972608 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972632 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972497 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 0.58 (tegningen lavere) |
| pb-26 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-45 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867944 (592 pt², ~1 hus)

### Kvartal10

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 971938 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972411 |  |  |  |  |  |  | G |  | A |  |  |  |  |
| 13394024 |  | A | **F** | **F** |  |  | **F** |  | A |  |  |  | gesims: tegnet/modell 0.36 (tegningen lavere); veggfarge: tegning (198, 198, 197) (grå/svart), modell (254, 230, 158) (gul/beige), ΔE 39.4; modellens farge: merknad: trykkfila 2015 (Street View-bildet viste nabohuset) |
| 867588 |  | A | A | **F** | A |  |  |  | **F** | A |  |  | gesims: tegnet/modell 0.64 (tegningen lavere); vinduer: vegg 2 (21.6 m): tegning 2 vinduer i rader [2], modell 2 i rader [1, 1] |
| 987370 |  |  |  | **F** |  |  | G |  |  |  | A |  | gesims: tegnet/modell 1.45 (tegningen høyere) |
| 867596 |  | A | **F** | **F** | A |  |  | G | **F** | A |  |  | gesims: tegnet/modell 1.52 (tegningen høyere); vinduer: vegg 3 (8.4 m): tegning 0 vinduer i rader [], modell 4 i rader [2, 2] |
| 868711 |  |  |  |  |  |  | G |  | **F** |  |  |  | vinduer: vegg 4 (10.1 m): tegning 3 vinduer i rader [1, 2], modell 3 i rader [1, 1, 1] |
| 867545 |  |  | A | A |  |  |  |  | **F** | A |  |  | vinduer: vegg 2 (17.8 m): tegning 9 vinduer i rader [2, 2, 5], modell 10 i rader [5, 5] |
| 971911 |  |  | A |  |  |  |  | G | **F** |  |  |  | vinduer: vegg 2 (4.2 m): tegning 5 vinduer i rader [1, 2, 1, 1], modell 0 i rader [] |
| 971903 |  |  | **F** | **F** | **F** |  | **F** |  | A |  |  |  | gesims: tegnet/modell 0.62 (tegningen lavere); veggfarge: tegning (255, 232, 161) (gul/beige), modell (244, 244, 244) (hvit), ΔE 37.7; modellens farge: 2019-trykket (dømt) |
| 868479 |  |  | A | **F** |  |  |  |  | **F** |  | A |  | gesims: tegnet/modell 0.39 (tegningen lavere); vinduer: vegg 0 (12.7 m): tegning 0 vinduer i rader [], modell 4 i rader [1, 3] |
| 868495 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 867553 |  |  |  | **F** |  |  |  | G | A |  |  |  | gesims: tegnet/modell 0.64 (tegningen lavere) |
| 300002508 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| pb-56 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867596 (4992 pt², ~1 hus); ved 867596 (461 pt², ~1 hus); ved 868711 (175 pt², ~1 hus); ved 867588 (1790 pt², ~1 hus); ved 867553 (220 pt², ~1 hus)

### Kvartal11

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868568 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 1.60 (tegningen høyere) |
| 867820 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867782 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 867839 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| pb-51 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868568 (15065 pt², ~4 hus); ved 867782 (306 pt², ~2 hus); ved 867782 (391 pt², ~1 hus)

### Kvartal12

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868592 |  |  | **F** | **F** | **F** |  |  | **F** |  |  |  |  | gesims: tegnet/modell 0.06 (tegningen lavere); takfarge: tegning (232, 213, 198) (oransje/brun), modell (175, 98, 84) (rød), ΔE 45.9; modellens farge: kvartaltegningen Kvartal9 (IoU 0.58) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 867820 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 867782 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972594 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 867790 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972101 |  |  | A | A |  |  |  |  | **F** |  |  |  | vinduer: vegg 4 (5.9 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 867804 |  | **F** | **F** | A |  |  | **F** |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); veggfarge: tegning (243, 149, 74) (oransje/brun), modell (236, 240, 240) (hvit), ΔE 66.4; modellens farge: 2019-trykket (dømt); vinduer: vegg 4 (11.3 m): tegning 23 vinduer i rader [4, 15, 4], modell 8 i rader [4, 4] |
| 867723 |  |  | A |  |  |  |  |  | **F** |  |  | A | vinduer: vegg 1 (15.3 m): tegning 11 vinduer i rader [4, 1, 6], modell 10 i rader [4, 6] |
| 972446 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 867758 |  |  | A | A |  |  |  |  | **F** |  |  |  | vinduer: vegg 3 (17.9 m): tegning 19 vinduer i rader [6, 7, 6], modell 12 i rader [6, 6] |
| 867731 |  |  | A |  | A | **F** |  | G | **F** | A |  |  | takform: tegning sal, modell halvvalm; vinduer: vegg 7 (6.2 m): tegning 0 vinduer i rader [], modell 9 i rader [3, 3, 3] |
| 867839 |  |  | A |  |  |  |  |  | A | A |  |  |  |
| 867766 |  |  | A | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.61 (tegningen lavere); vinduer: vegg 7 (5.5 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 972462 |  |  | A |  |  |  |  |  |  |  | A |  |  |
| 867715 |  | **F** | A |  |  |  | G |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); vinduer: vegg 4 (15.2 m): tegning 9 vinduer i rader [4, 1, 4], modell 8 i rader [4, 4] |
| 972128 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971253 |  |  | **F** | A | **F** |  | A |  | A |  |  |  |  |
| 972772 |  |  | **F** | A | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (242, 149, 130) (rød), modell (128, 128, 132) (grå/svart), ΔE 45.4; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 972578 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972608 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972438 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972454 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 868606 |  |  | **F** | A |  |  |  | **F** |  |  |  |  | takfarge: tegning (250, 229, 212) (hvit), modell (175, 96, 83) (rød), ΔE 51.1; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 867812 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867774 |  |  | A | A | A |  |  |  |  |  |  |  |  |
| 6246753 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867820 (4076 pt², ~1 hus); ved 867782 (170 pt², ~1 hus); ved 867758 (956 pt², ~1 hus)

### Kvartal13

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867502 |  |  |  | **F** |  | **F** |  |  | **F** | A |  | A | gesims: tegnet/modell 1.49 (tegningen høyere); takform: tegning sal, modell halvvalm; vinduer: vegg 2 (24.8 m): tegning 8 vinduer i rader [1, 4, 3], modell 9 i rader [6, 3] |
| 868460 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 867499 |  | **F** |  |  |  |  |  |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 22; ulike farger: 2); vinduer: vegg 12 (33.0 m): tegning 7 vinduer i rader [1, 6], modell 8 i rader [8] |
| 867510 |  | A |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 0 (37.2 m): tegning 3 vinduer i rader [3], modell 6 i rader [6] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867499 (172 pt², ~1 hus); ved 867499 (309 pt², ~1 hus); ved 867499 (1814 pt², ~2 hus); ved 868460 (134 pt², ~1 hus); ved 867502 (1158 pt², ~2 hus); ved 867502 (2812 pt², ~2 hus); ved 867510 (160 pt², ~1 hus); ved 867510 (160 pt², ~1 hus)

### Kvartal14

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972039 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972012 |  |  | A | **F** |  |  |  | **F** |  |  | A | A | gesims: tegnet/modell 1.38 (tegningen høyere); takfarge: tegning (221, 174, 132) (oransje/brun), modell (175, 96, 83) (rød), ΔE 31.9; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 870260 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 870236 |  |  |  | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 1.45 (tegningen høyere); vinduer: vegg 1 (15.5 m): tegning 0 vinduer i rader [], modell 10 i rader [5, 5] |
| pb-7 |  |  | **F** |  | A |  |  | **F** |  |  |  |  | takfarge: tegning (167, 166, 166) (grå/svart), modell (175, 96, 83) (rød), ΔE 41.5; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 867693 |  |  | A |  |  |  | G |  | **F** | A |  |  | vinduer: vegg 3 (10.3 m): tegning 8 vinduer i rader [8], modell 1 i rader [1] |
| 867707 |  |  | **F** |  | A |  | G | G | **F** | A |  |  | vinduer: vegg 2 (7.9 m): tegning 12 vinduer i rader [10, 2], modell 5 i rader [2, 1, 2] |
| 867804 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| pb-8 |  |  |  |  |  |  |  |  | A | A |  |  |  |
| 16308102 |  |  | A |  |  |  |  | G |  |  | A |  |  |
| 972063 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 4 (9.8 m): tegning 5 vinduer i rader [2, 1, 2], modell 4 i rader [2, 2] |
| 867715 |  |  | **F** | **F** |  |  | G | **F** | **F** | A |  |  | gesims: tegnet/modell 0.51 (tegningen lavere); takfarge: tegning (134, 134, 134) (grå/svart), modell (174, 119, 104) (rød), ΔE 26.0; modellens farge: kvartaltegningen Kvartal12 (IoU 0.54) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått); vinduer: vegg 4 (15.2 m): tegning 2 vindu |
| 972098 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972004 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972055 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 971229 |  |  | **F** | **F** | **F** | **F** | A | G | **F** | A |  |  | gesims: tegnet/modell 0.40 (tegningen lavere); takform: tegning valm, modell halvvalm; vinduer: vegg 4 (10.1 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972381 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868584 |  |  | **F** |  |  |  |  | A |  |  |  |  |  |
| 870244 |  |  | A |  | **F** | **F** |  |  |  |  |  |  | takform: tegning valm, modell halvvalm |
| 870228 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 972047 |  |  | A | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.40 (tegningen lavere); vinduer: vegg 4 (16.6 m): tegning 0 vinduer i rader [], modell 6 i rader [6] |
| pb-53 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972012 (587 pt², ~1 hus); ved 972012 (529 pt², ~1 hus); ved 870228 (4814 pt², ~1 hus); ved 972063 (162 pt², ~1 hus)

### sistekvartal

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870236 |  |  | A | **F** |  |  |  | **F** | **F** |  |  |  | gesims: tegnet/modell 0.54 (tegningen lavere); takfarge: tegning (244, 123, 106) (rød), modell (66, 66, 65) (grå/svart), ΔE 65.9; modellens farge: kvartaltegningen Kvartal14 (IoU 0.68) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått); vinduer: vegg 1 (15.5 m): tegning 10 vinduer |
| 972403 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 870252 |  |  | A | **F** |  |  |  |  | **F** | A | A | A | gesims: tegnet/modell 0.53 (tegningen lavere); vinduer: vegg 3 (25.3 m): tegning 13 vinduer i rader [4, 9], modell 7 i rader [4, 3] |
| 972381 |  |  | **F** | **F** | **F** |  | G |  |  |  |  |  | gesims: tegnet/modell 0.45 (tegningen lavere) |
| 870244 |  |  | **F** |  | A |  |  | **F** |  |  |  |  | takfarge: tegning (173, 100, 86) (rød), modell (142, 158, 157) (grå/svart), ΔE 42.6; modellens farge: kvartaltegningen Kvartal14 (IoU 0.54) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått) |
| 870228 |  |  | A |  |  |  |  | **F** | **F** | A |  |  | takfarge: tegning (252, 230, 158) (gul/beige), modell (175, 96, 83) (rød), ΔE 55.8; modellens farge: 2019-trykket (dømt) (ortofoto 2024: falmet/mosegrodd: fotoet skiller ikke tegl fra grått); vinduer: vegg 6 (13.5 m): tegning 0 vinduer i rader [], modell 11 i rader [5, 6] |
| 870201 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 4 (12.5 m): tegning 14 vinduer i rader [2, 8, 4], modell 9 i rader [4, 5] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870201 (9153 pt², ~1 hus); ved 972381 (512 pt², ~1 hus); ved 870228 (2333 pt², ~1 hus); ved 870236 (354 pt², ~1 hus); ved 870252 (4543 pt², ~1 hus); ved 870252 (153 pt², ~1 hus)

### tell

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867677 |  |  |  |  |  |  |  |  |  |  |  | A |  |
| 867634 |  |  | A |  | A |  |  |  | **F** |  |  |  | vinduer: vegg 0 (24.1 m): tegning 4 vinduer i rader [4], modell 9 i rader [9] |

### Glasshytta

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 869580 |  |  |  |  |  |  |  |  | A | A |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 869580 (2659 pt², ~2 hus)

### kirke

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867529 |  | **F** |  |  | **F** | **F** | G |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); takform: tegning sal, modell valm; vinduer: vegg 6 (14.2 m): tegning 4 vinduer i rader [1, 3], modell 0 i rader [] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867529 (5033 pt², ~2 hus); ved 867529 (162 pt², ~1 hus); ved 867529 (256 pt², ~1 hus)

### Toihuset

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870279 |  | **F** |  |  |  | **F** | G | **F** | **F** | A | A | A | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 2, 1, 6; ulike farger: 3); takform: tegning sal, modell valm; takfarge: tegning (82, 83, 85) (grå/svart), modell (124, 80, 68) (rød), ΔE 23.5; modellens farge: kvartaltegningen Toihuset (lest for hånd) (ortofoto 2024: falmet/mosegrodd: fo |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870279 (235 pt², ~1 hus); ved 870279 (6413 pt², ~1 hus); ved 870279 (209 pt², ~1 hus); ved 870279 (311 pt², ~1 hus); ved 870279 (253 pt², ~2 hus)

