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
| finnes | 4 | 20 | 0 | 188 |
| omriss | 65 | 82 | 0 | 41 |
| mone | 45 | 44 | 0 | 96 |
| takform | 9 | 0 | 0 | 179 |
| takfarge | 17 | 2 | 55 | 105 |
| arker | 0 | 37 | 0 | 151 |
| piper | 0 | 30 | 0 | 158 |
| gesims | 45 | 25 | 0 | 64 |
| veggfarge | 4 | 2 | 62 | 32 |
| vinduer | 65 | 14 | 0 | 21 |
| dorer | 0 | 51 | 0 | 49 |
| slaatt_sammen | 20 | 12 | 0 | 0 |
| tegnet_hus_uten_modell | 77 | 0 | 0 | 0 |

## Registrering per tegning

| tegning | hus | dreiing | helning | bakke pt/m | høyde pt/m (kilde) | kanter fra tegningen, median | hus innen 3 pt | blokker flyttet > 3 pt | koblet, men utenfor tegningen |
|---|---|---|---|---|---|---|---|---|---|
| Kvartal2BITMP | 19 | -11.9° | 45.5° | 4.82 | 5.03 (tegnede vegger) | 2.21 pt = 6.6 px | 84 % | 1 av 3 | - |
| Kvartal3 | 7 | -10.0° | 45.5° | 5.19 | 3.37 (tegnede vegger) | 1.89 pt = 5.7 px | 86 % | 6 av 7 | 868088 |
| Kvartal4BITMP | 8 | -12.9° | 45.5° | 5.07 | 3.53 (tegnede vegger) | 1.79 pt = 5.4 px | 88 % | 4 av 4 | 868363, 868428, 868371, 971970, 868398, 971962, 868401 |
| kvartal5 | 18 | -12.3° | 45.5° | 4.86 | 3.60 (tegnede vegger) | 2.13 pt = 6.4 px | 89 % | 1 av 3 | - |
| kvartal6 | 19 | -11.2° | 45.5° | 5.35 | 3.53 (tegnede vegger) | 3.12 pt = 9.4 px | 32 % | 0 av 1 | 868045 |
| kvartal7 | 18 | -14.0° | 45.5° | 4.58 | 3.12 (tegnede vegger) | 2.99 pt = 9.0 px | 50 % | 0 av 1 | 868290, 13394024, 867588 |
| Kvartal8BITMAP | 17 | -13.0° | 45.5° | 4.74 | 2.52 (tegnede vegger) | 1.82 pt = 5.5 px | 88 % | 0 av 1 | - |
| Kvartal9 | 23 | -13.5° | 45.5° | 5.34 | 2.97 (tegnede vegger) | 2.78 pt = 8.3 px | 56 % | 1 av 2 | 868614 |
| Kvartal10 | 15 | -8.7° | 45.5° | 4.74 | 4.19 (tegnede vegger) | 1.62 pt = 4.9 px | 93 % | 1 av 3 | 971873 |
| Kvartal11 | 3 | -15.3° | 45.5° | 5.12 | 4.08 (tegnede vegger) | 1.72 pt = 5.2 px | 67 % | 2 av 3 | - |
| Kvartal12 | 28 | -11.6° | 45.5° | 4.43 | 5.08 (tegnede vegger) | 2.21 pt = 6.6 px | 79 % | 0 av 1 | - |
| Kvartal13 | 4 | -13.5° | 45.5° | 4.90 | 3.17 (tegnede vegger) | 1.84 pt = 5.5 px | 100 % | 3 av 4 | - |
| Kvartal14 | 22 | -12.4° | 45.5° | 5.19 | 4.28 (tegnede vegger) | 3.46 pt = 10.4 px | 41 % | 3 av 5 | 972403, 867847, 972071 |
| sistekvartal | 7 | -13.6° | 45.5° | 5.19 | 5.81 (tegnede vegger) | 2.94 pt = 8.8 px | 71 % | 0 av 1 | 870198 |
| tell | 3 | -12.3° | 45.5° | 5.13 | 4.71 (tegnede vegger) | 3.15 pt = 9.4 px | 33 % | 1 av 3 | - |
| Glasshytta | 2 | -10.5° | 45.5° | 5.09 | 4.27 (tegnede vegger) | 1.4 pt = 4.2 px | 100 % | 1 av 2 | - |
| kirke | 1 | -7.2° | 45.5° | 5.60 | 3.47 (median av de andre tegningene) | 2.56 pt = 7.7 px | 100 % | 1 av 1 | - |
| Toihuset | 1 | -14.6° | 45.5° | 5.05 | 5.25 (tegnede vegger) | 2.74 pt = 8.2 px | 100 % | 0 av 1 | - |

## Per hus (maskinelt)

Alvor: **F** feil, A avvik, G avvik med grunn (modellens farge er Street View, tegningen er 2015). Tomt = ok eller ikke målt.

### Kvartal2BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972373 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 868118 |  |  | A | **F** | A |  | **F** |  | A |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere); veggfarge: tegning (247, 154, 135) (rød), modell (236, 240, 240) (hvit), ΔE 47.6 |
| 868126 |  |  | A | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 0.61 (tegningen lavere) |
| 868134 |  |  |  | **F** |  |  | G | G | **F** |  | A |  | gesims: tegnet/modell 1.35 (tegningen høyere); vinduer: vegg 2 (17.2 m): tegning 0 vinduer i rader [], modell 7 i rader [7] |
| 868150 |  |  |  |  |  |  | G |  | **F** | A |  |  | vinduer: vegg 5 (10.0 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 868088 |  |  |  | **F** |  |  | G | G |  | A |  | A | gesims: tegnet/modell 1.47 (tegningen høyere) |
| 972292 |  |  | A | A | **F** |  | G | G | **F** | A | A |  | vinduer: vegg 2 (15.8 m): tegning 7 vinduer i rader [3, 2, 2], modell 5 i rader [3, 2] |
| 972314 |  |  | **F** | A | **F** |  | G |  |  |  |  |  |  |
| 972365 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 868096 |  |  | A |  |  |  |  |  | **F** | A | A | A | vinduer: vegg 8 (15.4 m): tegning 0 vinduer i rader [], modell 9 i rader [7, 2] |
| 868142 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 3 (15.1 m): tegning 5 vinduer i rader [5], modell 10 i rader [5, 5] |
| 972306 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 971350 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972349 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 868681 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 868703 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 300399132 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 868673 |  |  | A | **F** | A |  | G | G | **F** | A | A |  | gesims: tegnet/modell 0.57 (tegningen lavere); vinduer: vegg 7 (14.1 m): tegning 6 vinduer i rader [2, 2, 2], modell 4 i rader [4] |
| pb-54 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972306 (8322 pt², ~2 hus); ved 972306 (1321 pt², ~1 hus); ved 868134 (642 pt², ~1 hus); ved 300399132 (489 pt², ~1 hus); ved 868673 (3275 pt², ~1 hus)

### Kvartal3

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868061 |  | **F** | A |  | A |  | G |  | **F** |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2); vinduer: vegg 1 (11.7 m): tegning 16 vinduer i rader [6, 10], modell 4 i rader [2, 2] |
| 869556 |  |  |  | **F** |  |  | G |  | **F** |  |  |  | gesims: tegnet/modell 1.81 (tegningen høyere); vinduer: vegg 1 (10.7 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 868053 |  |  | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 1.40 (tegningen høyere) |
| 867308 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868045 |  | **F** |  |  |  |  | G |  | **F** | A |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); vinduer: vegg 3 (44.9 m): tegning 4 vinduer i rader [1, 3], modell 7 i rader [7] |
| 868037 |  |  | A |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 2 (14.0 m): tegning 2 vinduer i rader [1, 1], modell 4 i rader [4] |
| 867324 |  |  | A | A | **F** |  | G |  |  | A |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868061 (229 pt², ~1 hus); ved 868037 (678 pt², ~1 hus)

### Kvartal4BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868339 |  |  |  | A |  |  | G |  | **F** |  | A | A | vinduer: vegg 2 (17.2 m): tegning 2 vinduer i rader [2], modell 6 i rader [5, 1] |
| 971954 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 868525 |  | **F** | A | A | A | **F** | G |  | **F** |  | A | A | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 4; ulike farger: 2); takform: tegning valm, modell sal/sammensatt; vinduer: vegg 4 (15.4 m): tegning 2 vinduer i rader [2], modell 0 i rader [] |
| 971946 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 194006187 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 971989 |  |  | **F** | **F** | **F** |  | G |  | A |  |  |  | gesims: tegnet/modell 0.30 (tegningen lavere) |
| 971202 |  |  | A | **F** | A |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.43 (tegningen lavere); vinduer: vegg 3 (8.9 m): tegning 3 vinduer i rader [1, 1, 1], modell 0 i rader [] |
| pb-48 |  |  | **F** |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (247, 156, 138) (rød), modell (96, 84, 76) (grå/svart), ΔE 49.4; modellens farge: tak: ortofoto 2024 (mørk brun); vegg: nabohuset bnr-193868371 (residential, 2.8 m unna) |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868525 (1068 pt², ~1 hus); ved 868525 (189 pt², ~1 hus); ved 868525 (126 pt², ~1 hus); ved 971954 (1186 pt², ~1 hus); ved pb-48 (976 pt², ~1 hus); ved 971946 (281 pt², ~1 hus); ved 194006187 (916 pt², ~1 hus)

### kvartal5

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868223 |  | **F** |  |  |  | **F** |  | G |  | A | A |  | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 0, 3; ulike farger: 2); takform: tegning valm, modell sal |
| 6242812 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868231 |  |  | A |  | A |  |  | G |  |  |  | A |  |
| 16290424 |  |  | A | **F** | A |  |  | G | **F** |  | A |  | gesims: tegnet/modell 2.45 (tegningen høyere); vinduer: vegg 4 (8.6 m): tegning 5 vinduer i rader [2, 3], modell 2 i rader [2] |
| 6251323 |  |  |  |  |  |  | G |  | A | A |  |  |  |
| 987397 |  |  | A |  | A |  |  |  | **F** | A |  |  | vinduer: vegg 2 (2.4 m): tegning 4 vinduer i rader [2, 2], modell 0 i rader [] |
| 868207 |  | A |  |  | A |  | G | G | **F** | A | A | A | vinduer: vegg 5 (2.4 m): tegning 2 vinduer i rader [1, 1], modell 0 i rader [] |
| 6251331 |  |  | A | A |  |  | G |  |  |  |  |  |  |
| 6251218 |  |  |  |  |  |  |  | G |  |  |  |  |  |
| 868215 |  |  | A | **F** |  |  | G |  | **F** |  | A | A | gesims: tegnet/modell 1.44 (tegningen høyere); vinduer: vegg 4 (8.8 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972195 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972187 |  |  | **F** | **F** |  |  | G | G | **F** | A |  |  | gesims: tegnet/modell 2.69 (tegningen høyere); vinduer: vegg 3 (5.0 m): tegning 2 vinduer i rader [1, 1], modell 2 i rader [2] |
| 972225 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972209 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 971342 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972217 |  |  | **F** |  | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (226, 204, 187) (oransje/brun), modell (141, 73, 57) (rød), ΔE 50.8; modellens farge: tak: ortofoto 2024 (rød tegl); vegg: 2017-tegningen som vektor (dekning 0.99) |
| pb-60 |  |  |  |  | A |  |  | G | A |  | A |  |  |
| pb-61 |  |  | A |  |  |  | G |  | **F** | A |  |  | vinduer: vegg 2 (10.4 m): tegning 8 vinduer i rader [3, 5], modell 4 i rader [2, 2] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972187 (172 pt², ~1 hus); ved 16290424 (301 pt², ~1 hus)

### kvartal6

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6247822 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 867979 |  | **F** | A | **F** |  |  |  |  | A | A | A | A | slaatt_sammen: tegningen har 3 fasader på én modellvegg (vegg 2; ulike farger: 2); gesims: tegnet/modell 1.35 (tegningen høyere) |
| pb-6 |  |  | **F** |  | **F** |  |  | G |  |  |  | A |  |
| 868029 |  |  | A | A |  |  | G |  | **F** | A |  |  | vinduer: vegg 0 (9.5 m): tegning 8 vinduer i rader [1, 1, 3, 2, 1], modell 2 i rader [2] |
| 971334 |  |  |  | **F** | A |  | G |  | **F** |  |  |  | gesims: tegnet/modell 0.45 (tegningen lavere); vinduer: vegg 7 (8.6 m): tegning 7 vinduer i rader [2, 2, 3], modell 3 i rader [1, 1, 1] |
| 868630 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 868002 |  |  | A | A | A |  | G |  | **F** |  |  |  | vinduer: vegg 3 (6.5 m): tegning 0 vinduer i rader [], modell 3 i rader [3] |
| 971318 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972179 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867952 |  |  | A |  | A |  | G | G | **F** |  |  |  | vinduer: vegg 6 (28.4 m): tegning 2 vinduer i rader [1, 1], modell 15 i rader [8, 7] |
| 867995 |  |  | **F** |  | **F** |  |  | A |  |  |  |  |  |
| 868010 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971296 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868665 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868657 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867987 |  | A | A |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 7 (14.9 m): tegning 6 vinduer i rader [2, 4], modell 4 i rader [4] |
| 972160 |  |  | A |  | A |  |  |  |  |  | A |  |  |
| 868649 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-59 |  | A | **F** | **F** | A |  | G |  | **F** | A |  | A | gesims: tegnet/modell 0.37 (tegningen lavere); vinduer: vegg 2 (15.8 m): tegning 8 vinduer i rader [1, 2, 3, 2], modell 14 i rader [7, 7] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 6247822 (12084 pt², ~4 hus)

### kvartal7

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868355 |  |  |  |  |  |  | G |  | A | A | A |  |  |
| 868339 |  | **F** |  | A | A |  |  |  | **F** | A | A |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 2 (17.2 m): tegning 10 vinduer i rader [2, 4, 4], modell 6 i rader [5, 1] |
| 867626 |  | A |  |  |  | **F** | G | G | **F** | A | A | A | takform: tegning valm, modell sal; vinduer: vegg 2 (19.9 m): tegning 9 vinduer i rader [8, 1], modell 12 i rader [6, 6] |
| 868347 |  | **F** | **F** |  | A |  | G |  | **F** |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); vinduer: vegg 6 (12.8 m): tegning 4 vinduer i rader [1, 1, 2], modell 2 i rader [2] |
| 971369 |  | **F** |  |  |  | **F** |  | G | A | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 7; ulike farger: 2); takform: tegning sal, modell sammensatt |
| 868320 |  | **F** |  |  |  |  | G | G |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2) |
| 867618 |  | **F** |  |  |  |  | G |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2); vinduer: vegg 3 (11.8 m): tegning 8 vinduer i rader [2, 4, 2], modell 5 i rader [1, 2, 2] |
| 918239 |  |  | **F** |  | A |  |  |  |  |  | A | A |  |
| 868525 |  |  | **F** | **F** |  |  |  | G |  |  | A |  | gesims: tegnet/modell 0.48 (tegningen lavere) |
| 6251765 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971946 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 6275109 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 991718 |  |  | A | A | A |  |  | G |  |  |  | A |  |
| 971202 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 868517 |  |  | **F** | **F** | **F** |  |  | **F** |  |  |  |  | gesims: tegnet/modell 0.48 (tegningen lavere); takfarge: tegning (138, 140, 142) (grå/svart), modell (172, 100, 84) (rød), ΔE 36.8 |
| pb-28 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-33 |  |  | **F** | **F** | **F** |  |  | G |  |  |  |  | gesims: tegnet/modell 1.69 (tegningen høyere) |
| pb-47 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved pb-47 (530 pt², ~1 hus); ved 867626 (1362 pt², ~1 hus)

### Kvartal8BITMAP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972152 |  |  | **F** | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 2.11 (tegningen høyere) |
| 868258 |  |  | A | **F** | A |  | G |  | **F** | A | A | A | gesims: tegnet/modell 0.64 (tegningen lavere); vinduer: vegg 7 (6.9 m): tegning 0 vinduer i rader [], modell 6 i rader [3, 3] |
| pb-5 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 0.36 (tegningen lavere) |
| 868266 |  |  | A | A |  |  | G |  | **F** |  | A |  | vinduer: vegg 2 (15.4 m): tegning 0 vinduer i rader [], modell 9 i rader [4, 5] |
| 868274 |  | A | A | **F** | A |  | G |  | A | A |  |  | gesims: tegnet/modell 1.57 (tegningen høyere) |
| 868312 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868282 |  | A |  |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 2 (11.3 m): tegning 3 vinduer i rader [3], modell 8 i rader [4, 4] |
| 13414904 |  | A | A |  |  |  | G | G | **F** | A |  | A | vinduer: vegg 4 (13.0 m): tegning 5 vinduer i rader [4, 1], modell 4 i rader [4] |
| 972136 |  |  | A | **F** |  |  | **F** |  |  |  |  |  | gesims: tegnet/modell 2.46 (tegningen høyere); veggfarge: tegning (193, 121, 107) (rød), modell (244, 244, 244) (hvit), ΔE 50.3; modellens farge: 2019-trykket (visuelt) |
| 300279164 |  |  | **F** |  | **F** | **F** |  |  |  |  |  |  | takform: tegning valm, modell sal |
| 868290 |  |  |  | A |  |  | G |  | **F** |  |  |  | vinduer: vegg 5 (5.4 m): tegning 0 vinduer i rader [], modell 5 i rader [3, 1, 1] |
| 868533 |  |  | A | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 0.28 (tegningen lavere) |
| pb-13 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972144 |  |  | A |  | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (152, 154, 157) (grå/svart), modell (172, 100, 84) (rød), ΔE 38.5 |
| 971288 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971261 |  |  | **F** |  | A |  |  |  | A |  |  |  |  |
| 16313173 |  |  | A |  | A |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868290 (716 pt², ~2 hus); ved 13414904 (2526 pt², ~2 hus); ved 868282 (280 pt², ~1 hus); ved 868258 (337 pt², ~1 hus)

### Kvartal9

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972489 |  |  | **F** | **F** | **F** |  |  | G |  |  |  |  | gesims: tegnet/modell 2.00 (tegningen høyere) |
| 867855 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 867936 |  |  | A |  |  |  | G | G | A | A | A |  |  |
| 867863 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867901 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 867944 |  | **F** | A |  |  |  | G | G |  | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2) |
| 972519 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972624 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 867928 |  |  |  |  |  | **F** | G |  |  |  | A |  | takform: tegning valm, modell sal/sammensatt |
| 867898 |  |  | **F** |  | **F** |  |  | G |  |  | A | A |  |
| 868622 |  |  |  | A |  |  |  | G |  |  | A |  |  |
| 868592 |  |  | A | **F** | A |  | A |  |  |  |  |  | gesims: tegnet/modell 2.40 (tegningen høyere) |
| pb-14 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971377 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 971385 |  |  | A | **F** |  |  |  |  | A |  |  |  | gesims: tegnet/modell 1.76 (tegningen høyere) |
| 972543 |  |  | **F** | **F** | A |  |  | **F** |  |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere); takfarge: tegning (135, 81, 70) (rød), modell (128, 128, 132) (grå/svart), ΔE 30.5 |
| 972535 |  |  | **F** |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (59, 58, 60) (grå/svart), modell (172, 100, 84) (rød), ΔE 43.2 |
| 972616 |  |  | **F** |  | **F** | **F** |  | **F** |  |  |  |  | takform: tegning valm, modell sal; takfarge: tegning (59, 58, 60) (grå/svart), modell (128, 81, 67) (rød), ΔE 28.6; modellens farge: 2019-trykket (visuelt) |
| 972608 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972632 |  |  | A |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (217, 110, 94) (rød), modell (128, 128, 132) (grå/svart), ΔE 50.2 |
| 972497 |  |  | **F** | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 1.81 (tegningen høyere) |
| pb-23 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-45 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867944 (592 pt², ~1 hus)

### Kvartal10

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 971938 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972411 |  |  |  |  |  |  | G |  | A |  |  |  |  |
| 13394024 |  | A | A | **F** |  |  | G |  | A |  |  | A | gesims: tegnet/modell 0.33 (tegningen lavere) |
| 867588 |  | A | A | **F** |  |  | G |  | **F** | A |  |  | gesims: tegnet/modell 0.55 (tegningen lavere); vinduer: vegg 2 (21.6 m): tegning 2 vinduer i rader [2], modell 2 i rader [1, 1] |
| 987370 |  |  |  | **F** |  |  | G |  |  |  | A |  | gesims: tegnet/modell 1.51 (tegningen høyere) |
| 867596 |  | A | **F** | A | **F** |  |  | G | **F** | A |  |  | vinduer: vegg 3 (8.4 m): tegning 0 vinduer i rader [], modell 4 i rader [2, 2] |
| 868711 |  |  |  |  |  |  | G |  | **F** |  |  |  | vinduer: vegg 4 (10.1 m): tegning 3 vinduer i rader [1, 2], modell 3 i rader [1, 1, 1] |
| 867545 |  |  | A | A |  |  | G |  | **F** | A |  |  | vinduer: vegg 2 (17.8 m): tegning 9 vinduer i rader [2, 2, 5], modell 10 i rader [5, 5] |
| 971911 |  |  |  |  |  |  |  | **F** | **F** |  |  |  | takfarge: tegning (227, 227, 226) (hvit), modell (172, 100, 84) (rød), ΔE 53.0; modellens farge: 2019-trykket (visuelt); vinduer: vegg 2 (4.2 m): tegning 5 vinduer i rader [1, 2, 1, 1], modell 0 i rader [] |
| 971903 |  |  | **F** | **F** | **F** |  |  | **F** |  |  |  |  | gesims: tegnet/modell 0.50 (tegningen lavere); takfarge: tegning (180, 102, 84) (rød), modell (135, 135, 135) (grå/svart), ΔE 38.2; modellens farge: 2019-trykket (visuelt) |
| 868479 |  |  | A | **F** | A |  | **F** |  | **F** |  |  |  | gesims: tegnet/modell 0.34 (tegningen lavere); veggfarge: tegning (255, 232, 161) (gul/beige), modell (174, 102, 86) (rød), ΔE 53.2; vinduer: vegg 0 (12.7 m): tegning 0 vinduer i rader [], modell 4 i rader [1, 3] |
| 868495 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 867553 |  |  | A | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 1.37 (tegningen høyere) |
| 300002508 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| pb-56 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867596 (4992 pt², ~1 hus); ved 867596 (461 pt², ~1 hus); ved 867588 (1790 pt², ~1 hus); ved 987370 (1263 pt², ~1 hus)

### Kvartal11

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867537 |  |  |  |  |  |  |  |  | **F** | A | A |  | vinduer: vegg 6 (16.4 m): tegning 13 vinduer i rader [4, 4, 1, 4], modell 12 i rader [8, 4] |
| 868568 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 1.80 (tegningen høyere) |
| pb-51 |  |  | **F** |  | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (180, 102, 84) (rød), modell (150, 144, 138) (grå/svart), ΔE 35.6; modellens farge: tak: standard: nytt hus fra kommunekartet, farge ikke valgt; vegg: nabohuset bnr-193868568 (Brannstasjon - uthus til Infanterikasernen, 1.4 m unna) |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867537 (1898 pt², ~5 hus); ved 868568 (8566 pt², ~1 hus); ved 867537 (306 pt², ~2 hus)

### Kvartal12

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868592 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867820 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 867782 |  |  |  |  |  |  | G |  |  |  |  |  |  |
| 972594 |  |  | **F** |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (66, 66, 65) (grå/svart), modell (172, 100, 84) (rød), ΔE 41.1; modellens farge: 2019-trykket (visuelt) |
| 867790 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972101 |  |  | A | **F** |  |  | G |  | **F** |  |  |  | gesims: tegnet/modell 0.60 (tegningen lavere); vinduer: vegg 4 (5.9 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 867804 |  | **F** | **F** | A |  |  | G |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); vinduer: vegg 4 (11.3 m): tegning 23 vinduer i rader [4, 15, 4], modell 8 i rader [4, 4] |
| 867723 |  |  | A |  |  |  | G |  | **F** |  |  | A | vinduer: vegg 1 (15.3 m): tegning 11 vinduer i rader [4, 1, 6], modell 10 i rader [4, 6] |
| 972446 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 867758 |  |  | A | A |  |  |  |  | **F** |  | A |  | vinduer: vegg 8 (17.5 m): tegning 6 vinduer i rader [6], modell 12 i rader [6, 6] |
| 867731 |  |  | A |  | **F** |  |  | G | **F** | A |  |  | vinduer: vegg 7 (6.2 m): tegning 0 vinduer i rader [], modell 9 i rader [3, 3, 3] |
| 867839 |  | **F** | A |  |  |  |  |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 7; ulike farger: 2); vinduer: vegg 7 (21.0 m): tegning 14 vinduer i rader [1, 13], modell 8 i rader [4, 4] |
| 867766 |  |  | A | **F** |  |  |  |  | **F** |  |  |  | gesims: tegnet/modell 0.61 (tegningen lavere); vinduer: vegg 7 (5.5 m): tegning 2 vinduer i rader [2], modell 4 i rader [2, 2] |
| 972462 |  |  | A |  |  |  |  | G |  |  | A |  |  |
| 867715 |  | **F** | A |  |  |  | G | G | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 4; ulike farger: 2); vinduer: vegg 4 (15.2 m): tegning 9 vinduer i rader [4, 1, 4], modell 8 i rader [4, 4] |
| 972128 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971253 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972772 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972578 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972608 |  |  | **F** |  | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (155, 154, 154) (grå/svart), modell (174, 102, 86) (rød), ΔE 36.6 |
| 972438 |  |  | **F** |  | **F** |  |  | **F** |  |  |  |  | takfarge: tegning (250, 229, 212) (hvit), modell (135, 135, 135) (grå/svart), ΔE 37.7; modellens farge: 2019-trykket (visuelt) |
| 972454 |  |  | **F** | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 1.47 (tegningen høyere) |
| 868606 |  |  | **F** |  |  |  |  | **F** |  |  |  |  | takfarge: tegning (250, 229, 212) (hvit), modell (172, 100, 84) (rød), ΔE 49.1 |
| 867812 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867774 |  |  |  | A |  |  |  | G |  |  |  |  |  |
| 6246753 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-57 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-58 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867820 (430 pt², ~1 hus); ved 867820 (1327 pt², ~1 hus); ved 867782 (170 pt², ~1 hus)

### Kvartal13

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867502 |  | A |  | A |  |  | G | G | **F** | A |  | A | vinduer: vegg 2 (24.8 m): tegning 8 vinduer i rader [1, 4, 3], modell 9 i rader [6, 3] |
| 868460 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 867499 |  | **F** |  | A |  |  |  |  | **F** | A | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 22; ulike farger: 2); vinduer: vegg 12 (33.0 m): tegning 7 vinduer i rader [1, 6], modell 8 i rader [8] |
| 867510 |  | A |  |  |  |  | G |  | **F** | A |  |  | vinduer: vegg 0 (37.2 m): tegning 3 vinduer i rader [3], modell 6 i rader [6] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 868460 (172 pt², ~1 hus); ved 867499 (1442 pt², ~2 hus); ved 868460 (134 pt², ~1 hus); ved 867502 (1158 pt², ~2 hus); ved 867502 (2812 pt², ~2 hus); ved 867510 (160 pt², ~1 hus); ved 867510 (160 pt², ~1 hus)

### Kvartal14

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972039 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 972012 |  |  | A | **F** |  |  |  | G |  |  | A | A | gesims: tegnet/modell 1.83 (tegningen høyere) |
| 870260 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 870236 |  |  |  | **F** |  |  | G |  | **F** |  |  |  | gesims: tegnet/modell 1.63 (tegningen høyere); vinduer: vegg 1 (15.5 m): tegning 0 vinduer i rader [], modell 10 i rader [5, 5] |
| pb-7 |  |  | **F** | A |  |  | G | G |  |  |  |  |  |
| 867693 |  | **F** | A |  | A |  | G | G | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2); vinduer: vegg 3 (10.3 m): tegning 8 vinduer i rader [8], modell 1 i rader [1] |
| 867707 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 867804 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| pb-8 |  | **F** |  |  |  |  |  |  | **F** |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 19; ulike farger: 2); vinduer: vegg 19 (10.1 m): tegning 17 vinduer i rader [5, 7, 5], modell 10 i rader [5, 5] |
| 16308102 |  |  | A |  |  |  |  | G |  |  | A |  |  |
| 972063 |  | **F** | A |  |  |  |  |  | **F** | A |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 5; ulike farger: 2); vinduer: vegg 4 (9.8 m): tegning 5 vinduer i rader [2, 1, 2], modell 4 i rader [2, 2] |
| 867715 |  |  | A | A |  |  | G |  | **F** | A |  |  | vinduer: vegg 4 (15.2 m): tegning 2 vinduer i rader [2], modell 8 i rader [4, 4] |
| 972098 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972004 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972055 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 971229 |  |  | **F** | **F** | A |  | A |  | **F** | A |  |  | gesims: tegnet/modell 0.48 (tegningen lavere); vinduer: vegg 4 (10.1 m): tegning 0 vinduer i rader [], modell 4 i rader [4] |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868584 |  |  | A |  |  |  |  | A |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 870228 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 972047 |  |  | A | **F** |  |  | **F** | **F** | **F** |  |  |  | gesims: tegnet/modell 0.43 (tegningen lavere); veggfarge: tegning (242, 149, 130) (rød), modell (194, 191, 182) (grå/svart), ΔE 39.5; modellens farge: tak: ortofoto 2024 (grå); vegg: 2017-tegningen som vektor (dekning 0.95); takfarge: tegning (237, 119, 102) (rød), modell (150, 150, 148) (grå/svart) |
| pb-53 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 972012 (587 pt², ~1 hus); ved 972012 (529 pt², ~1 hus); ved 870228 (2744 pt², ~1 hus); ved 972063 (162 pt², ~1 hus)

### sistekvartal

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870236 |  |  | A | **F** |  |  | G | G | **F** |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere); vinduer: vegg 1 (15.5 m): tegning 10 vinduer i rader [5, 1, 4], modell 10 i rader [5, 5] |
| 972403 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 870252 |  |  | A | **F** |  |  |  | G | **F** | A |  | A | gesims: tegnet/modell 0.60 (tegningen lavere); vinduer: vegg 3 (25.3 m): tegning 13 vinduer i rader [4, 9], modell 7 i rader [4, 3] |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 870228 |  |  | A |  |  |  | G | G | **F** | A |  |  | vinduer: vegg 6 (13.5 m): tegning 0 vinduer i rader [], modell 11 i rader [5, 6] |
| 870201 |  |  |  |  |  |  |  |  | **F** | A |  |  | vinduer: vegg 4 (12.5 m): tegning 14 vinduer i rader [2, 8, 4], modell 9 i rader [4, 5] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870201 (9456 pt², ~1 hus); ved 870244 (4546 pt², ~1 hus); ved 870236 (194 pt², ~1 hus); ved 870201 (124 pt², ~1 hus); ved 870252 (576 pt², ~1 hus)

### tell

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867677 |  |  |  |  |  |  |  | G |  |  |  | A |  |
| 867634 |  |  | A |  | A |  |  | G | **F** |  |  |  | vinduer: vegg 0 (24.1 m): tegning 4 vinduer i rader [4], modell 9 i rader [9] |
| 867685 |  | **F** | A |  |  |  | G |  |  |  |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2) |

### Glasshytta

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 869548 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 869580 |  |  |  |  |  |  | G |  | A | A |  |  |  |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 869548 (2659 pt², ~2 hus)

### kirke

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867529 |  |  | A |  |  | **F** |  | **F** |  |  | A |  | takform: tegning sal, modell flatt; takfarge: tegning (53, 52, 53) (grå/svart), modell (194, 198, 198) (hvit), ΔE 57.8 |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 867529 (2305 pt², ~1 hus); ved 867529 (162 pt², ~1 hus); ved 867529 (409 pt², ~1 hus); ved 867529 (236 pt², ~1 hus); ved 867529 (162 pt², ~1 hus)

### Toihuset

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870279 |  | **F** |  |  |  | **F** | G | G | **F** | A | A | A | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 2, 1, 6; ulike farger: 3); takform: tegning sal, modell sammensatt; vinduer: vegg 6 (123.2 m): tegning 95 vinduer i rader [93, 2], modell 19 i rader [19] |

Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ved 870279 (235 pt², ~1 hus); ved 870279 (209 pt², ~1 hus); ved 870279 (6413 pt², ~1 hus); ved 870279 (311 pt², ~1 hus); ved 870279 (253 pt², ~2 hus)

