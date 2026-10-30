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
| finnes | 3 | 22 | 0 | 192 |
| omriss | 71 | 83 | 0 | 38 |
| mone | 46 | 45 | 0 | 99 |
| takform | 9 | 0 | 0 | 183 |
| takfarge | 1 | 0 | 112 | 71 |
| arker | 0 | 40 | 0 | 152 |
| piper | 0 | 31 | 0 | 161 |
| gesims | 49 | 24 | 0 | 68 |
| veggfarge | 8 | 1 | 18 | 76 |
| vinduer | 68 | 16 | 0 | 23 |
| dorer | 0 | 58 | 0 | 49 |
| slaatt_sammen | 19 | 12 | 0 | 0 |
| tegnet_hus_uten_modell | 69 | 0 | 0 | 0 |

## Registrering per tegning

| tegning | hus | dreiing | helning | bakke pt/m | høyde pt/m (kilde) | kanter fra tegningen, median | hus innen 3 pt | blokker flyttet > 3 pt | koblet, men utenfor tegningen |
|---|---|---|---|---|---|---|---|---|---|
| Kvartal2BITMP | 20 | -11.9° | 45.5° | 4.76 | 5.03 (tegnede vegger) | 1.98 pt = 5.9 px | 90 % | 1 av 3 | - |
| Kvartal3 | 7 | -10.0° | 45.5° | 5.19 | 3.37 (tegnede vegger) | 1.91 pt = 5.7 px | 86 % | 6 av 7 | 868088 |
| Kvartal4BITMP | 8 | -10.4° | 45.5° | 5.10 | 3.53 (tegnede vegger) | 2.16 pt = 6.5 px | 100 % | 2 av 3 | 868428, 868371, 971970, 868398, 971962, 868401 |
| kvartal5 | 18 | -12.3° | 45.5° | 4.85 | 3.60 (tegnede vegger) | 2.07 pt = 6.2 px | 89 % | 1 av 3 | - |
| kvartal6 | 19 | -11.1° | 45.5° | 5.34 | 3.53 (tegnede vegger) | 3.36 pt = 10.1 px | 37 % | 0 av 1 | 868045 |
| kvartal7 | 19 | -13.8° | 45.5° | 4.62 | 3.12 (tegnede vegger) | 3.24 pt = 9.7 px | 47 % | 0 av 1 | 868290, 13394024, 867588 |
| Kvartal8BITMAP | 17 | -13.0° | 45.5° | 4.74 | 2.52 (tegnede vegger) | 1.82 pt = 5.5 px | 88 % | 0 av 1 | - |
| Kvartal9 | 24 | -13.5° | 45.5° | 5.33 | 2.95 (tegnede vegger) | 3.0 pt = 9.0 px | 50 % | 1 av 2 | 868614 |
| Kvartal10 | 15 | -9.4° | 45.5° | 4.74 | 4.19 (tegnede vegger) | 1.76 pt = 5.3 px | 93 % | 1 av 3 | 971873 |
| Kvartal11 | 3 | -15.5° | 45.5° | 5.07 | 4.08 (tegnede vegger) | 1.67 pt = 5.0 px | 67 % | 2 av 3 | - |
| Kvartal12 | 28 | -11.6° | 45.5° | 4.43 | 5.08 (tegnede vegger) | 2.22 pt = 6.7 px | 79 % | 0 av 1 | - |
| Kvartal13 | 6 | -14.4° | 45.5° | 4.88 | 3.11 (tegnede vegger) | 2.08 pt = 6.2 px | 100 % | 2 av 4 | - |
| Kvartal14 | 22 | -12.6° | 45.5° | 5.19 | 4.28 (tegnede vegger) | 3.63 pt = 10.9 px | 41 % | 4 av 5 | 972403, 867847, 972071 |
| sistekvartal | 7 | -14.5° | 45.5° | 5.22 | 5.81 (tegnede vegger) | 2.74 pt = 8.2 px | 86 % | 0 av 1 | 870198 |
| tell | 3 | -12.3° | 45.5° | 5.13 | 4.71 (tegnede vegger) | 3.15 pt = 9.4 px | 33 % | 1 av 3 | - |
| Glasshytta | 2 | -10.5° | 45.5° | 5.09 | 4.27 (tegnede vegger) | 1.39 pt = 4.2 px | 100 % | 1 av 2 | - |
| kirke | 1 | -13.8° | 45.5° | 5.54 | 3.47 (median av de andre tegningene) | 4.37 pt = 13.1 px | 0 % | 1 av 1 | - |
| Toihuset | 1 | -14.6° | 45.5° | 5.05 | 5.25 (tegnede vegger) | 2.67 pt = 8.0 px | 100 % | 0 av 1 | - |

## Per hus (maskinelt)

Alvor: **F** feil, A avvik, G avvik med grunn (modellens farge har en kilde nyere enn tegningen 2015: Street View 2016+ for vegg, ortofoto 2024 for tak). Tomt = ok eller ikke målt.

### Kvartal2BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972373 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 868118 |  |  | A |  | A |  |  | G | A |  |  |  |  |
| 868126 |  |  | A | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 0.61 (tegningen lavere) |
| 868134 |  |  |  | **F** |  |  |  | G | **F** |  | A |  | gesims: tegnet/modell 1.35 (tegningen høyere); vinduer: vegg 2 (17.2 m): tegning 0 vinduer i rader [], modell 7 i rader [7] |
| 868150 |  |  |  |  |  |  |  |  | **F** | A | A |  | vinduer: vegg 5 (10.0 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 868088 |  |  | A | **F** |  |  | G | G |  | A |  |  | gesims: tegnet/modell 1.47 (tegningen høyere) |
| 972292 |  |  | A | A | **F** |  | G | G | **F** | A | A | A | vinduer: vegg 2 (15.8 m): tegning 7 vinduer i rader [3, 2, 2], modell 5 i rader [3, 2] |
| 972314 |  |  | **F** | A | **F** |  |  | G |  |  |  |  |  |
| 972365 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868096 |  |  | **F** |  |  |  |  | G |  |  | A | A |  |
| 868142 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 3 (15.1 m): tegning 5 vinduer i rader [5], modell 10 i rader [5, 5] |
| 972306 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 971350 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972349 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868681 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 868703 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 300399132 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 868673 |  |  | A | **F** | A |  |  |  | **F** | A | A |  | gesims: tegnet/modell 0.57 (tegningen lavere); vinduer: vegg 7 (14.1 m): tegning 6 vinduer i rader [2, 2, 2], modell 4 i rader [4] |
| pb-54 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-62 |  |  | **F** | **F** | **F** |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.10 (tegningen lavere); vinduer: vegg 3 (8.6 m): tegning 0 vinduer i rader [], modell 3 i rader [1, 2] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972306 (8322 pt², ~2 hus); ved 300399132 (2824 pt², ~1 hus); ved 868673 (3275 pt², ~1 hus)

### Kvartal3

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868061 |  | **F** | A |  | A |  | G |  | **F** |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2); vinduer: vegg 1 (11.7 m): tegning 16 vinduer i rader [6, 10], modell 4 i rader [2, 2] |
| 869556 |  |  |  | **F** |  |  | **F** | G | **F** |  |  |  | gesims: tegnet/modell 1.81 (tegningen høyere); veggfarge: tegning (218, 165, 125) (oransje/brun), modell (168, 164, 156) (grå/svart), ΔE 28.1; modellens farge: Street View 2010 (grå naturstein (bruddstein/granitt), ikke pusset); eldre enn tegningen, men tegningen har ikke huset; vinduer: vegg 1 (10. |
| 868053 |  |  | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 1.40 (tegningen høyere) |
| 867308 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868045 |  | **F** |  |  |  |  |  |  | **F** | A |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); vinduer: vegg 3 (44.9 m): tegning 4 vinduer i rader [1, 3], modell 7 i rader [7] |
| 868037 |  |  | A |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 2 (14.0 m): tegning 2 vinduer i rader [1, 1], modell 4 i rader [4] |
| 867324 |  |  | A | A | **F** |  |  | G |  | A |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868061 (229 pt², ~1 hus); ved 868037 (678 pt², ~1 hus)

### Kvartal4BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868363 |  |  | A |  |  |  |  | G | A |  | A |  |  |
| 868339 |  | **F** |  | **F** |  |  |  | G | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); gesims: tegnet/modell 1.70 (tegningen høyere); vinduer: vegg 3 (12.1 m): tegning 5 vinduer i rader [2, 3], modell 0 i rader [] |
| 971954 |  |  | A |  | A |  |  |  |  |  |  | A |  |
| 868525 |  | A | A | A | A | **F** | G | G | **F** |  | A | A | takform: tegning valm, modell sal/sammensatt; vinduer: vegg 4 (15.4 m): tegning 2 vinduer i rader [2], modell 0 i rader [] |
| 971946 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 194006187 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 971989 |  |  | **F** | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.54 (tegningen lavere); vinduer: vegg 5 (5.0 m): tegning 0 vinduer i rader [], modell 4 i rader [2, 2] |
| 971202 |  |  | **F** | **F** | **F** |  | **F** | G | A | A |  |  | gesims: tegnet/modell 0.30 (tegningen lavere); veggfarge: tegning (246, 147, 129) (rød), modell (188, 190, 192) (grå/svart), ΔE 45.1; modellens farge: kvartaltegningen Kvartal4BITMP (skygge side, IoU 0.62) |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 971954 (1428 pt², ~1 hus); ved 971946 (905 pt², ~1 hus); ved 971989 (247 pt², ~1 hus)

### kvartal5

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868223 |  | **F** |  |  |  | **F** |  |  |  | A | A |  | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 0, 3; ulike farger: 2); takform: tegning valm, modell sal |
| 6242812 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868231 |  |  | A |  | A |  |  | G |  |  |  | A |  |
| 16290424 |  |  | A | **F** | A |  |  | G | **F** |  | A |  | gesims: tegnet/modell 2.45 (tegningen høyere); vinduer: vegg 4 (8.6 m): tegning 5 vinduer i rader [2, 3], modell 2 i rader [2] |
| 6251323 |  |  |  |  |  |  |  |  | A | A |  |  |  |
| 987397 |  |  | A |  | A |  |  | G | **F** | A |  |  | vinduer: vegg 2 (2.4 m): tegning 4 vinduer i rader [2, 2], modell 0 i rader [] |
| 868207 |  | A |  |  | A |  |  | G | **F** | A | A | A | vinduer: vegg 5 (2.4 m): tegning 2 vinduer i rader [1, 1], modell 0 i rader [] |
| 6251331 |  |  | A | A |  |  |  |  |  |  |  |  |  |
| 6251218 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 868215 |  |  | A | **F** |  |  |  |  | **F** |  | A | A | gesims: tegnet/modell 1.44 (tegningen høyere); vinduer: vegg 4 (8.8 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972195 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972187 |  |  | **F** | **F** |  |  |  |  | **F** | A |  |  | gesims: tegnet/modell 2.69 (tegningen høyere); vinduer: vegg 3 (5.0 m): tegning 2 vinduer i rader [1, 1], modell 2 i rader [2] |
| 972225 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972209 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 971342 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972217 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| pb-60 |  |  |  |  | A |  |  | G | A |  | A |  |  |
| pb-61 |  |  | A |  |  |  |  | G | **F** | A |  |  | vinduer: vegg 2 (10.4 m): tegning 8 vinduer i rader [3, 5], modell 4 i rader [2, 2] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972187 (172 pt², ~1 hus); ved 16290424 (301 pt², ~1 hus)

### kvartal6

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6247822 |  |  | **F** |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 6 (14.6 m): tegning 9 vinduer i rader [4, 2, 3], modell 7 i rader [4, 3] |
| 867979 |  | **F** | A | **F** |  |  |  | G | A | A | A | A | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 2; ulike farger: 2); gesims: tegnet/modell 1.35 (tegningen høyere) |
| pb-6 |  |  | **F** |  | **F** |  |  | G |  |  |  | A |  |
| 868029 |  |  | A | A |  |  |  | G | **F** | A |  |  | vinduer: vegg 0 (9.5 m): tegning 8 vinduer i rader [1, 1, 3, 2, 1], modell 2 i rader [2] |
| 971334 |  |  |  | **F** |  |  | G | G | **F** |  |  |  | gesims: tegnet/modell 0.45 (tegningen lavere); vinduer: vegg 7 (8.6 m): tegning 7 vinduer i rader [2, 2, 3], modell 3 i rader [1, 1, 1] |
| 868630 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868002 |  |  | A | A | A |  | **F** | G | **F** |  |  |  | veggfarge: tegning (247, 150, 82) (oransje/brun), modell (236, 240, 240) (hvit), ΔE 64.5; modellens farge: 2019-trykket (dømt); vinduer: vegg 3 (6.5 m): tegning 0 vinduer i rader [], modell 3 i rader [3] |
| 971318 |  |  |  |  |  |  |  | G |  |  |  |  |  |
| 972179 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867952 |  | A | A |  |  |  |  |  | **F** | A | A |  | vinduer: vegg 6 (28.4 m): tegning 10 vinduer i rader [2, 2, 2, 4], modell 15 i rader [8, 7] |
| 867995 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868010 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971296 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868665 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868657 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867987 |  | A | A |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 7 (14.9 m): tegning 6 vinduer i rader [2, 4], modell 4 i rader [4] |
| 972160 |  |  | A |  | A |  |  |  |  |  | A |  |  |
| 868649 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-59 |  | A | **F** | **F** | A |  | G | G | **F** | A |  | A | gesims: tegnet/modell 0.37 (tegningen lavere); vinduer: vegg 2 (15.8 m): tegning 8 vinduer i rader [1, 2, 3, 2], modell 14 i rader [7, 7] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 6247822 (12207 pt², ~4 hus)

### kvartal7

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868355 |  |  |  |  |  |  |  | G | A | A | A |  |  |
| 868339 |  | **F** |  | A | A |  |  | G | **F** | A | A |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 2 (17.2 m): tegning 10 vinduer i rader [2, 4, 4], modell 6 i rader [5, 1] |
| 867626 |  | A | A |  |  | **F** |  |  | **F** | A | A | A | takform: tegning valm, modell sal; vinduer: vegg 2 (19.9 m): tegning 9 vinduer i rader [8, 1], modell 12 i rader [6, 6] |
| 868347 |  | **F** | **F** |  | A |  | **F** | G | **F** |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); veggfarge: tegning (239, 240, 240) (hvit), modell (254, 234, 174) (oransje/brun), ΔE 31.9; modellens farge: 2019-trykket (dømt); vinduer: vegg 6 (12.8 m): tegning 4 vinduer i rader [1, 1, 2], modell 2 i rader [2] |
| 971369 |  |  | A | **F** |  |  |  |  | A | A | A |  | gesims: tegnet/modell 1.39 (tegningen høyere) |
| 868320 |  | **F** |  |  |  |  |  | G |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2) |
| 867618 |  |  |  |  |  |  |  |  |  | A | A | A |  |
| 918239 |  |  | A |  | A |  |  |  |  |  | A | A |  |
| 868525 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 0.48 (tegningen lavere) |
| 6251765 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971946 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 6275109 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| 991718 |  |  | A | A | A |  |  |  |  |  |  |  |  |
| 971202 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868517 |  |  | **F** | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 0.48 (tegningen lavere) |
| pb-28 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-33 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 1.69 (tegningen høyere) |
| pb-47 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-65 |  |  | **F** |  | **F** |  | **F** | G |  |  |  |  | veggfarge: tegning (184, 208, 195) (grønn), modell (173, 100, 86) (rød), ΔE 52.3; modellens farge: kvartaltegningen kvartal7 (lys side, IoU 0.67) |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved pb-47 (530 pt², ~1 hus); ved 867626 (1362 pt², ~1 hus)

### Kvartal8BITMAP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972152 |  |  | **F** | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 2.11 (tegningen høyere) |
| 868258 |  |  | A | **F** | A |  | G | G | **F** | A | A | A | gesims: tegnet/modell 0.64 (tegningen lavere); vinduer: vegg 7 (6.9 m): tegning 0 vinduer i rader [], modell 6 i rader [3, 3] |
| pb-5 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 0.36 (tegningen lavere) |
| 868266 |  |  | A | A |  |  |  | G | **F** |  | A |  | vinduer: vegg 2 (15.4 m): tegning 0 vinduer i rader [], modell 9 i rader [4, 5] |
| 868274 |  | A | A | **F** | A |  |  | G | A | A |  |  | gesims: tegnet/modell 1.57 (tegningen høyere) |
| 868312 |  |  | **F** | A | **F** |  |  | G |  |  |  |  |  |
| 868282 |  | A |  |  |  |  |  | G | **F** | A |  |  | vinduer: vegg 2 (11.3 m): tegning 3 vinduer i rader [3], modell 8 i rader [4, 4] |
| 13414904 |  | A | A |  |  |  |  | G | **F** | A |  | A | vinduer: vegg 4 (13.0 m): tegning 5 vinduer i rader [4, 1], modell 4 i rader [4] |
| 972136 |  |  | A | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 2.46 (tegningen høyere) |
| 300279164 |  |  | **F** |  | **F** | **F** |  | G |  |  |  |  | takform: tegning valm, modell sal |
| 868290 |  |  |  | A |  |  |  |  | **F** |  |  |  | vinduer: vegg 5 (5.4 m): tegning 0 vinduer i rader [], modell 5 i rader [3, 1, 1] |
| 868533 |  |  | A | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 0.28 (tegningen lavere) |
| pb-13 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972144 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 971288 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971261 |  |  | **F** |  | A |  |  |  | A |  |  |  |  |
| 16313173 |  |  | A |  | A |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868290 (716 pt², ~2 hus); ved 13414904 (2526 pt², ~2 hus); ved 868282 (280 pt², ~1 hus); ved 868258 (337 pt², ~1 hus)

### Kvartal9

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972489 |  |  | **F** | **F** | **F** |  |  | G |  |  |  |  | gesims: tegnet/modell 2.00 (tegningen høyere) |
| 867855 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 867936 |  |  | A |  |  |  | G | G | A | A | A |  |  |
| 867863 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867901 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 867944 |  | **F** | A |  |  |  |  |  |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2) |
| 972519 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972624 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 867928 |  |  |  |  | A | **F** |  | G |  |  | A |  | takform: tegning valm, modell sal/sammensatt |
| 867898 |  |  | **F** |  | **F** |  |  | G | A | A | A | A |  |
| 868622 |  |  |  | A |  |  |  |  |  |  | A |  |  |
| 868592 |  |  | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 2.41 (tegningen høyere) |
| pb-14 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971377 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 971385 |  |  | A | **F** | A |  |  |  | A |  |  |  | gesims: tegnet/modell 1.76 (tegningen høyere) |
| 972543 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere) |
| 972535 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 972616 |  |  | **F** |  | **F** | **F** |  | **F** |  |  |  |  | takform: tegning valm, modell sal; takfarge: tegning (59, 58, 60) (grå/svart), modell (128, 81, 67) (rød), ΔE 28.6; modellens farge: 2019-trykket (dømt) (ortofoto 2024: taket ligger i slagskygge) |
| 972608 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972632 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 972497 |  |  | **F** | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 1.82 (tegningen høyere) |
| pb-23 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-45 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| pb-66 |  |  | A |  | A |  |  |  | **F** | A |  |  | vinduer: vegg 2 (20.2 m): tegning 10 vinduer i rader [1, 9], modell 8 i rader [8] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867944 (592 pt², ~1 hus); ved 971385 (386 pt², ~1 hus)

### Kvartal10

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 971938 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972411 |  |  |  |  |  |  | G |  | A |  |  |  |  |
| 13394024 |  | A | **F** | **F** |  |  | **F** | G | A |  |  |  | gesims: tegnet/modell 0.33 (tegningen lavere); veggfarge: tegning (198, 198, 197) (grå/svart), modell (254, 230, 158) (gul/beige), ΔE 39.4; modellens farge: merknad: trykkfila 2015 (Street View-bildet viste nabohuset) |
| 867588 |  | A | A | **F** |  |  |  | G | **F** | A |  |  | gesims: tegnet/modell 0.55 (tegningen lavere); vinduer: vegg 2 (21.6 m): tegning 2 vinduer i rader [2], modell 2 i rader [1, 1] |
| 987370 |  |  |  | **F** |  |  | G |  |  |  | A |  | gesims: tegnet/modell 1.51 (tegningen høyere) |
| 867596 |  | **F** | **F** | A | **F** |  |  | G | **F** | A |  |  | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 3 (8.4 m): tegning 0 vinduer i rader [], modell 4 i rader [2, 2] |
| 868711 |  |  |  |  |  |  | G | G | **F** |  |  |  | vinduer: vegg 4 (10.1 m): tegning 3 vinduer i rader [1, 2], modell 3 i rader [1, 1, 1] |
| 867545 |  |  | **F** | A |  |  |  | G | **F** | A |  |  | vinduer: vegg 2 (17.8 m): tegning 9 vinduer i rader [2, 2, 5], modell 10 i rader [5, 5] |
| 971911 |  |  | A |  |  |  |  | G | **F** |  |  |  | vinduer: vegg 2 (4.2 m): tegning 5 vinduer i rader [1, 2, 1, 1], modell 0 i rader [] |
| 971903 |  |  | **F** | **F** | **F** |  |  | G |  |  |  |  | gesims: tegnet/modell 0.50 (tegningen lavere) |
| 868479 |  |  | A | **F** |  |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.34 (tegningen lavere); vinduer: vegg 0 (12.7 m): tegning 0 vinduer i rader [], modell 4 i rader [1, 3] |
| 868495 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 867553 |  |  |  | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 1.37 (tegningen høyere) |
| 300002508 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| pb-56 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867596 (4992 pt², ~1 hus); ved 867596 (461 pt², ~1 hus); ved 867588 (1790 pt², ~1 hus); ved 867553 (1263 pt², ~1 hus)

### Kvartal11

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867537 |  |  |  |  |  |  |  |  | **F** | A | A | A | vinduer: vegg 6 (16.4 m): tegning 13 vinduer i rader [4, 4, 1, 4], modell 12 i rader [8, 4] |
| 868568 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 1.80 (tegningen høyere) |
| pb-51 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867537 (2081 pt², ~4 hus); ved 868568 (8566 pt², ~1 hus); ved 867537 (306 pt², ~2 hus)

### Kvartal12

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868592 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867820 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 867782 |  |  |  |  |  |  |  | G |  |  |  |  |  |
| 972594 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 867790 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972101 |  |  | A | **F** |  |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.60 (tegningen lavere); vinduer: vegg 4 (5.9 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 867804 |  | **F** | **F** | A |  |  | **F** |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); veggfarge: tegning (243, 149, 74) (oransje/brun), modell (236, 240, 240) (hvit), ΔE 66.4; modellens farge: 2019-trykket (dømt); vinduer: vegg 4 (11.3 m): tegning 23 vinduer i rader [4, 15, 4], modell 8 i rader [4, 4] |
| 867723 |  |  | A |  |  |  |  | G | **F** |  |  | A | vinduer: vegg 1 (15.3 m): tegning 11 vinduer i rader [4, 1, 6], modell 10 i rader [4, 6] |
| 972446 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 867758 |  |  | A | A |  |  |  |  | **F** |  | A |  | vinduer: vegg 8 (17.5 m): tegning 6 vinduer i rader [6], modell 12 i rader [6, 6] |
| 867731 |  |  | A |  | **F** |  |  | G | **F** | A |  |  | vinduer: vegg 7 (6.2 m): tegning 0 vinduer i rader [], modell 9 i rader [3, 3, 3] |
| 867839 |  | **F** | A |  |  |  |  |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 7; ulike farger: 2); vinduer: vegg 7 (21.0 m): tegning 14 vinduer i rader [1, 13], modell 8 i rader [4, 4] |
| 867766 |  |  | A | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.61 (tegningen lavere); vinduer: vegg 7 (5.5 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 972462 |  |  | A |  |  |  |  |  |  |  | A |  |  |
| 867715 |  | **F** | A |  |  |  | G | G | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); vinduer: vegg 4 (15.2 m): tegning 9 vinduer i rader [4, 1, 4], modell 8 i rader [4, 4] |
| 972128 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971253 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972772 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972578 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972608 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972438 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972454 |  |  | A | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 1.47 (tegningen høyere) |
| 868606 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 867812 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867774 |  |  |  | A |  |  |  | G |  |  |  |  |  |
| 6246753 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-57 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-58 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867820 (430 pt², ~1 hus); ved 867820 (1327 pt², ~1 hus); ved 867782 (170 pt², ~1 hus)

### Kvartal13

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867502 |  |  |  | A |  |  |  |  |  | A |  | A |  |
| 868460 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 867499 |  |  |  | A |  |  |  | G | **F** | A | A | A | vinduer: vegg 12 (33.0 m): tegning 7 vinduer i rader [1, 6], modell 8 i rader [8] |
| 867510 |  | A |  |  |  |  |  | G | **F** | A |  |  | vinduer: vegg 0 (37.2 m): tegning 3 vinduer i rader [3], modell 6 i rader [6] |
| pb-63 |  |  | **F** | **F** | **F** |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.18 (tegningen lavere); vinduer: vegg 3 (11.0 m): tegning 0 vinduer i rader [], modell 4 i rader [3, 1] |
| pb-64 |  |  | **F** | **F** |  |  |  | G | **F** | A |  |  | gesims: tegnet/modell 1.40 (tegningen høyere); vinduer: vegg 2 (8.5 m): tegning 3 vinduer i rader [3], modell 3 i rader [1, 2] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868460 (172 pt², ~1 hus); ved 867499 (1485 pt², ~2 hus); ved 868460 (134 pt², ~1 hus); ved 867502 (1158 pt², ~2 hus); ved pb-63 (2812 pt², ~2 hus); ved 867510 (160 pt², ~1 hus); ved 867510 (160 pt², ~1 hus)

### Kvartal14

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972039 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972012 |  |  | A | **F** |  |  |  | G |  |  | A | A | gesims: tegnet/modell 1.83 (tegningen høyere) |
| 870260 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870236 |  |  |  | **F** |  | **F** |  |  | **F** |  |  |  | gesims: tegnet/modell 1.63 (tegningen høyere); takform: tegning valm, modell sal; vinduer: vegg 1 (15.5 m): tegning 0 vinduer i rader [], modell 10 i rader [5, 5] |
| pb-7 |  |  | **F** | A |  |  |  |  |  |  |  |  |  |
| 867693 |  | **F** | A |  | A |  | G |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 3 (10.3 m): tegning 8 vinduer i rader [8], modell 1 i rader [1] |
| 867707 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 867804 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| pb-8 |  | **F** |  |  |  |  |  |  | **F** |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 19; ulike farger: 2); vinduer: vegg 19 (10.1 m): tegning 17 vinduer i rader [5, 7, 5], modell 10 i rader [5, 5] |
| 16308102 |  |  | A |  |  |  |  | G |  |  | A |  |  |
| 972063 |  | **F** | A |  |  |  |  | G | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 5; ulike farger: 2); vinduer: vegg 4 (9.8 m): tegning 5 vinduer i rader [2, 1, 2], modell 4 i rader [2, 2] |
| 867715 |  |  | A | A |  |  | G |  | **F** | A |  |  | vinduer: vegg 4 (15.2 m): tegning 2 vinduer i rader [2], modell 8 i rader [4, 4] |
| 972098 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972004 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972055 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 971229 |  |  | **F** | **F** |  |  | A | G | **F** | A |  |  | gesims: tegnet/modell 0.48 (tegningen lavere); vinduer: vegg 4 (10.1 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868584 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870228 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 972047 |  |  | **F** | **F** |  |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.43 (tegningen lavere); vinduer: vegg 4 (16.6 m): tegning 0 vinduer i rader [], modell 6 i rader [6] |
| pb-53 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972012 (587 pt², ~1 hus); ved 972012 (529 pt², ~1 hus); ved 870228 (2744 pt², ~1 hus); ved 972063 (162 pt², ~1 hus)

### sistekvartal

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870236 |  |  | A | **F** |  |  |  | G | **F** |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere); vinduer: vegg 1 (15.5 m): tegning 10 vinduer i rader [5, 1, 4], modell 10 i rader [5, 5] |
| 972403 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 870252 |  |  | A | **F** |  |  |  |  | **F** | A |  | A | gesims: tegnet/modell 0.60 (tegningen lavere); vinduer: vegg 3 (25.3 m): tegning 13 vinduer i rader [4, 9], modell 7 i rader [4, 3] |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870228 |  |  | A |  |  |  |  | G | **F** | A |  |  | vinduer: vegg 6 (13.5 m): tegning 0 vinduer i rader [], modell 11 i rader [5, 6] |
| 870201 |  |  |  |  |  |  |  | G | **F** | A |  |  | vinduer: vegg 4 (12.5 m): tegning 14 vinduer i rader [2, 8, 4], modell 9 i rader [4, 5] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870201 (9456 pt², ~1 hus); ved 870244 (4546 pt², ~1 hus); ved 870201 (232 pt², ~1 hus); ved 870252 (576 pt², ~1 hus)

### tell

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867677 |  |  |  |  |  |  |  | G |  |  |  | A |  |
| 867634 |  |  | A |  | A |  |  | G | **F** |  |  |  | vinduer: vegg 0 (24.1 m): tegning 4 vinduer i rader [4], modell 9 i rader [9] |
| 867685 |  | **F** | A |  |  |  | **F** | G |  |  |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); veggfarge: tegning (218, 165, 125) (oransje/brun), modell (242, 240, 232) (hvit), ΔE 36.7; modellens farge: Street View 2010 (lys kalket tegl (offwhite, svakt kjølig)); eldre enn tegningen, men tegningen har ikke huse |

### Glasshytta

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 869548 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 869580 |  |  |  |  |  |  |  |  | A | A |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 869548 (2659 pt², ~2 hus)

### kirke

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867529 |  | **F** |  |  | **F** | **F** | G |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); takform: tegning sal, modell valm; vinduer: vegg 6 (14.2 m): tegning 4 vinduer i rader [1, 3], modell 0 i rader [] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867529 (5033 pt², ~2 hus); ved 867529 (162 pt², ~1 hus); ved 867529 (256 pt², ~1 hus)

### Toihuset

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870279 |  | **F** |  |  |  | **F** | G |  | **F** | A | A | A | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 2, 1, 6; ulike farger: 3); takform: tegning sal, modell sammensatt; vinduer: vegg 6 (123.2 m): tegning 95 vinduer i rader [93, 2], modell 19 i rader [19] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870279 (235 pt², ~1 hus); ved 870279 (6413 pt², ~1 hus); ved 870279 (209 pt², ~1 hus); ved 870279 (311 pt², ~1 hus); ved 870279 (253 pt², ~2 hus)

