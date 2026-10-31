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
| finnes | 4 | 20 | 0 | 195 |
| omriss | 65 | 83 | 0 | 47 |
| mone | 43 | 51 | 0 | 99 |
| takform | 7 | 0 | 0 | 188 |
| takfarge | 1 | 0 | 106 | 79 |
| arker | 0 | 39 | 0 | 156 |
| piper | 0 | 32 | 0 | 163 |
| gesims | 17 | 14 | 37 | 70 |
| veggfarge | 3 | 0 | 16 | 81 |
| vinduer | 0 | 8 | 13 | 83 |
| dorer | 0 | 0 | 2 | 102 |
| slaatt_sammen | 11 | 7 | 9 | 0 |
| tegnet_hus_uten_modell | 0 | 0 | 67 | 0 |

## Registrering per tegning

| tegning | hus | dreiing | helning | bakke pt/m | høyde pt/m (kilde) | kanter fra tegningen, median | hus innen 3 pt | blokker flyttet > 3 pt | koblet, men utenfor tegningen |
|---|---|---|---|---|---|---|---|---|---|
| Kvartal2BITMP | 20 | -11.9° | 45.5° | 4.76 | 5.03 (tegnede vegger) | 1.98 pt = 5.9 px | 90 % | 1 av 3 | - |
| Kvartal3 | 7 | -10.0° | 45.5° | 5.19 | 3.37 (tegnede vegger) | 1.91 pt = 5.7 px | 86 % | 6 av 7 | 868088 |
| Kvartal4BITMP | 8 | -11.2° | 45.5° | 5.12 | 3.53 (tegnede vegger) | 2.08 pt = 6.2 px | 88 % | 2 av 3 | 868428, 868371, 971970, 868398, 971962, 868401 |
| kvartal5 | 18 | -12.3° | 45.5° | 4.86 | 3.81 (tegnede vegger) | 2.03 pt = 6.1 px | 94 % | 1 av 3 | - |
| kvartal6 | 19 | -11.1° | 45.5° | 5.88 | 3.53 (tegnede vegger) | 2.13 pt = 6.4 px | 74 % | 3 av 5 | 868045 |
| kvartal7 | 19 | -13.8° | 45.5° | 4.62 | 3.12 (tegnede vegger) | 3.24 pt = 9.7 px | 47 % | 0 av 1 | 868290, 13394024, 867588 |
| Kvartal8BITMAP | 18 | -10.7° | 45.5° | 4.90 | 2.52 (tegnede vegger) | 1.69 pt = 5.1 px | 89 % | 0 av 1 | - |
| Kvartal9 | 24 | -13.6° | 45.5° | 5.35 | 2.94 (tegnede vegger) | 2.92 pt = 8.8 px | 50 % | 1 av 2 | 868614 |
| Kvartal10 | 16 | -10.8° | 45.5° | 4.65 | 4.19 (tegnede vegger) | 1.73 pt = 5.2 px | 94 % | 3 av 5 | - |
| Kvartal11 | 3 | -15.6° | 45.5° | 5.07 | 4.08 (tegnede vegger) | 1.63 pt = 4.9 px | 67 % | 2 av 3 | - |
| Kvartal12 | 28 | -11.6° | 45.5° | 4.43 | 5.08 (tegnede vegger) | 2.22 pt = 6.7 px | 79 % | 0 av 1 | - |
| Kvartal13 | 6 | -14.5° | 45.5° | 4.86 | 3.11 (tegnede vegger) | 2.08 pt = 6.3 px | 100 % | 2 av 4 | - |
| Kvartal14 | 22 | -12.9° | 45.5° | 5.06 | 4.28 (tegnede vegger) | 3.25 pt = 9.7 px | 45 % | 4 av 5 | 972403, 867847, 972071 |
| sistekvartal | 8 | -15.0° | 45.5° | 5.30 | 5.81 (tegnede vegger) | 2.79 pt = 8.4 px | 75 % | 1 av 2 | - |
| tell | 3 | -12.3° | 45.5° | 5.13 | 4.71 (tegnede vegger) | 3.15 pt = 9.4 px | 33 % | 1 av 3 | - |
| Glasshytta | 2 | -10.6° | 45.5° | 5.07 | 5.36 (tegnede vegger) | 0.92 pt = 2.8 px | 100 % | 1 av 2 | - |
| kirke | 1 | -13.8° | 45.5° | 5.54 | 3.47 (median av de andre tegningene) | 4.37 pt = 13.1 px | 0 % | 1 av 1 | - |
| Toihuset | 1 | -14.7° | 45.5° | 5.05 | 5.25 (tegnede vegger) | 2.58 pt = 7.7 px | 100 % | 0 av 1 | - |

## Per hus (maskinelt)

Alvor: **F** feil, A avvik, G avvik med grunn (modellens farge har en kilde nyere enn tegningen 2015: Street View 2016+ for vegg, ortofoto 2024 for tak). Tomt = ok eller ikke målt.

### Kvartal2BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972373 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 868118 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| 868126 |  |  | A | G |  |  |  |  |  |  |  |  |  |
| 868134 |  |  |  | G |  |  |  | G |  |  | A |  |  |
| 868150 |  |  |  |  |  |  |  |  |  |  | A |  |  |
| 868088 |  |  | A | G |  |  | G | G |  |  |  |  |  |
| 972292 |  |  | A | G | **F** |  | G | G | A |  | A | A |  |
| 972314 |  |  | **F** | A | **F** |  |  | G |  |  |  |  |  |
| 972365 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868096 |  |  | **F** | G |  |  |  |  |  |  | A | A |  |
| 868142 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972306 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 971350 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972349 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868681 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 868703 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 300399132 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 868673 |  |  | A |  | A |  |  | G |  |  | A |  |  |
| pb-54 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-62 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 972306 (8322 pt², ~2 hus, avvik med grunn: nabobit); ved 300399132 (2824 pt², ~1 hus, avvik med grunn: frihånd); ved 868673 (3275 pt², ~1 hus, avvik med grunn: mur/frihånd)

### Kvartal3

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868061 |  | **F** | A |  | A |  |  |  |  |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2) |
| 869556 |  |  |  | G |  |  |  |  |  |  |  |  |  |
| 868053 |  |  | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 1.40 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)) |
| 867308 |  |  | **F** | A | **F** |  |  |  |  |  |  |  |  |
| 868045 |  | G |  |  |  |  |  |  |  |  |  | A |  |
| 868037 |  |  | A |  |  |  |  | G | G |  |  |  |  |
| 867324 |  |  | A | A | **F** |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 868061 (229 pt², ~1 hus, avvik med grunn: takdel); ved 868037 (678 pt², ~1 hus, avvik med grunn: mur)

### Kvartal4BITMP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868363 |  |  | A |  |  |  |  | G |  |  | A |  |  |
| 868339 |  | **F** |  | G |  |  |  |  |  |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3, 2; ulike farger: 2) |
| 971954 |  |  | A | G |  |  |  |  |  |  |  | A |  |
| 868525 |  | A | A | A | A | **F** | G | G |  |  | A | A | takform: tegning valm, modell sal/sammensatt |
| 971946 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 194006187 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 971989 |  |  | **F** | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 0.35 (tegningen lavere) (veggflatene i tegningen); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 971202 |  |  | **F** | G | **F** |  | **F** | G | A |  |  |  | veggfarge: tegning (246, 147, 129) (rød), modell (248, 224, 204) (hvit), ΔE 38.3; modellens farge: 2019-trykket (dømt) |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 971954 (699 pt², ~1 hus, avvik med grunn: frihånd); ved 971954 (3429 pt², ~1 hus, avvik med grunn: frihånd); ved 971946 (905 pt², ~1 hus, avvik med grunn: frihånd)

### kvartal5

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868223 |  | G |  |  |  | **F** |  |  |  |  | A |  | takform: tegning valm, modell sal |
| 6242812 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 0.63 (tegningen lavere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 868231 |  |  | A |  | A |  |  | G |  |  |  | A |  |
| 16290424 |  |  | A | **F** | A |  |  | G |  |  | A |  | gesims: tegnet/modell 2.31 (tegningen høyere) (veggflatene i tegningen) |
| 6251323 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 987397 |  |  | A |  | A |  |  | G | G |  |  |  |  |
| 868207 |  | A |  |  |  |  |  | G | A |  | A | A |  |
| 6251331 |  |  | A | G |  |  |  |  |  |  |  |  |  |
| 6251218 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 868215 |  |  | A | G |  |  |  |  |  |  | A | A |  |
| 972195 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972187 |  |  | **F** | G |  |  |  |  | G |  |  |  |  |
| 972225 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972209 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 971342 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972217 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| pb-60 |  |  |  |  | A |  |  | G |  |  | A |  |  |
| pb-61 |  |  | A |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 868223 (172 pt², ~1 hus, avvik med grunn: frihånd); ved 16290424 (301 pt², ~1 hus, avvik med grunn: port/gjerde)

### kvartal6

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6247822 |  |  |  |  |  |  |  | G |  |  | A |  |  |
| 867979 |  |  |  | G |  |  |  | G |  |  |  |  |  |
| pb-6 |  |  | A |  | **F** |  |  |  |  |  |  | A |  |
| 868029 |  |  | A | A | A |  |  | G |  |  |  |  |  |
| 971334 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 868630 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 868002 |  |  |  | G |  |  |  |  |  |  |  |  |  |
| 971318 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 972179 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867952 |  | **F** |  |  |  |  | G |  |  |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2) |
| 867995 |  |  | **F** |  | **F** |  |  | G |  |  | A |  |  |
| 868010 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971296 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 868665 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868657 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 867987 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972160 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 868649 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| pb-59 |  |  |  | A |  |  | G | G | G |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 971318 (1057 pt², ~1 hus, avvik med grunn: frihånd); ved 867987 (536 pt², ~1 hus, avvik med grunn: takdel); ved 867987 (138 pt², ~1 hus, avvik med grunn: detalj); ved 971334 (2472 pt², ~1 hus, avvik med grunn: frihånd); ved 971334 (163 pt², ~1 hus, avvik med grunn: detalj)

### kvartal7

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868355 |  |  |  |  |  |  |  | G |  |  | A |  |  |
| 868339 |  | **F** |  | G | A |  | G | G | G |  | A |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2) |
| 867626 |  | A | A |  |  | **F** | G |  |  |  | A | A | takform: tegning valm, modell sal |
| 868347 |  | **F** | **F** |  | A |  | **F** | G |  |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); veggfarge: tegning (239, 240, 240) (hvit), modell (254, 234, 174) (oransje/brun), ΔE 31.9; modellens farge: 2019-trykket (dømt) |
| 971369 |  |  | A | G |  |  |  |  |  |  | A |  |  |
| 868320 |  | **F** |  |  |  |  |  | G |  |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 1; ulike farger: 2) |
| 867618 |  |  |  |  |  |  |  |  |  |  | A | A |  |
| 918239 |  |  | A |  | A |  |  |  |  |  | A | A |  |
| 868525 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 0.48 (tegningen lavere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 6251765 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971946 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 6275109 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| 991718 |  |  | A | A | A |  |  |  |  |  |  |  |  |
| 971202 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 868517 |  |  | **F** | G | A |  |  | G |  |  |  |  |  |
| pb-28 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-33 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 1.69 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| pb-47 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-65 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved pb-47 (530 pt², ~1 hus, avvik med grunn: frihånd); ved 867626 (1362 pt², ~1 hus, avvik med grunn: frihånd)

### Kvartal8BITMAP

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972152 |  |  | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 2.11 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 868258 |  |  |  | **F** |  |  |  | G |  |  | A | A | gesims: tegnet/modell 0.64 (tegningen lavere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| pb-5 |  |  | **F** | G | A |  |  | G |  |  |  |  |  |
| 868541 |  |  | **F** | **F** | A |  |  |  | A |  |  |  | gesims: tegnet/modell 1.49 (tegningen høyere) (veggflatene i tegningen); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 868266 |  |  |  | G |  |  |  | G |  |  | A | A |  |
| 868274 |  | A | A | **F** | A |  |  | G |  |  |  |  | gesims: tegnet/modell 1.57 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)) |
| 868312 |  |  | **F** | A | A |  |  | G |  |  |  |  |  |
| 868282 |  | G |  |  |  |  |  | G |  |  |  |  |  |
| 13414904 |  |  | A |  | A |  |  | G |  |  |  | A |  |
| 972136 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 300279164 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| 868290 |  | A |  | G |  |  |  |  | G |  |  |  |  |
| 868533 |  |  | A | G |  |  |  | G |  |  |  |  |  |
| pb-13 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 972144 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 971288 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 971261 |  |  | **F** | **F** | **F** |  |  |  | A |  |  |  | gesims: tegnet/modell 0.52 (tegningen lavere) (veggflatene i tegningen); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 16313173 |  |  | A |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 868290 (265 pt², ~1 hus, avvik med grunn: mur); ved 13414904 (2526 pt², ~2 hus, avvik med grunn: gjerde/frihånd)

### Kvartal9

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972489 |  |  | **F** | **F** | **F** |  |  | G |  |  |  |  | gesims: tegnet/modell 2.01 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)) |
| 867855 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 867936 |  |  | A |  |  |  | G | G | G |  | A |  |  |
| 867863 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867901 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 867944 |  | G | A |  |  |  |  |  |  |  | A | A |  |
| 972519 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 972624 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 867928 |  |  |  |  | A | **F** |  | G |  |  | A |  | takform: tegning valm, modell sal/sammensatt |
| 867898 |  |  | **F** |  | **F** |  |  | G |  |  | A | A |  |
| 868622 |  |  |  | A |  |  |  |  |  |  |  |  |  |
| 868592 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| pb-14 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 971377 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 971385 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972543 |  |  | **F** | G | A |  |  |  |  |  |  |  |  |
| 972535 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 972616 |  |  | **F** |  | **F** | **F** |  | **F** |  |  |  |  | takform: tegning valm, modell sal; takfarge: tegning (59, 58, 60) (grå/svart), modell (128, 81, 67) (rød), ΔE 28.6; modellens farge: 2019-trykket (dømt) (ortofoto 2024: taket ligger i slagskygge) |
| 972608 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972632 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 972497 |  |  | **F** | **F** |  |  |  |  |  |  |  |  | gesims: tegnet/modell 1.82 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| pb-23 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-45 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| pb-66 |  |  | A | A | A |  | G | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 867944 (592 pt², ~1 hus, avvik med grunn: takdel); ved 868592 (174 pt², ~1 hus, avvik med grunn: detalj); ved 971385 (386 pt², ~1 hus, avvik med grunn: frihånd)

### Kvartal10

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 971938 |  |  | A |  | A |  |  |  |  |  |  |  |  |
| 972411 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 13394024 |  | A | A | G |  |  | G | G | G |  |  | A |  |
| 867588 |  | A |  | G |  |  | G | G | G | G |  |  |  |
| 987370 |  |  |  | **F** |  |  |  |  |  |  | A |  | gesims: tegnet/modell 1.51 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 867596 |  |  | **F** | A | A |  |  | G |  |  |  |  |  |
| 868711 |  |  |  |  |  |  |  | G |  |  |  |  |  |
| 867545 |  |  | A | G |  |  |  | G |  |  |  |  |  |
| 971911 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 971903 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971873 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 868479 |  |  |  |  | A |  |  | G |  |  |  |  |  |
| 868495 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 867553 |  |  | A | **F** |  |  |  | G |  |  |  |  | gesims: tegnet/modell 1.37 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 300002508 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| pb-56 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 971903 (3750 pt², ~1 hus, avvik med grunn: frihånd); ved 867596 (680 pt², ~3 hus, avvik med grunn: mur); ved 971903 (135 pt², ~1 hus, avvik med grunn: detalj); ved 867588 (1790 pt², ~1 hus, avvik med grunn: frihånd); ved 867553 (1067 pt², ~1 hus, avvik med grunn: frihånd)

### Kvartal11

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867537 |  |  |  |  |  |  |  |  |  |  | A | A |  |
| 868568 |  |  | **F** | **F** | **F** |  |  |  |  |  |  |  | gesims: tegnet/modell 1.80 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| pb-51 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 867537 (2081 pt², ~4 hus, avvik med grunn: frihånd); ved pb-51 (243 pt², ~1 hus, avvik med grunn: mur); ved 867537 (306 pt², ~2 hus, avvik med grunn: detalj); ved 868568 (8484 pt², ~1 hus, avvik med grunn: mur/frihånd)

### Kvartal12

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 868592 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867820 |  |  | **F** |  | A |  |  |  |  |  |  |  |  |
| 867782 |  |  |  |  |  |  |  | G |  |  |  |  |  |
| 972594 |  |  | **F** |  |  |  |  |  |  |  |  |  |  |
| 867790 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972101 |  |  | A | G |  |  |  | G |  |  |  |  |  |
| 867804 |  | G | **F** | G |  |  | **F** |  |  |  |  |  | veggfarge: tegning (243, 149, 74) (oransje/brun), modell (236, 240, 240) (hvit), ΔE 66.4; modellens farge: 2019-trykket (dømt) |
| 867723 |  |  | A |  |  |  |  | G |  |  |  | A |  |
| 972446 |  |  | A |  | **F** |  |  |  |  |  |  |  |  |
| 867758 |  |  | A | G |  |  |  |  |  |  | A |  |  |
| 867731 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 867839 |  | G | A |  |  |  |  |  |  |  |  |  |  |
| 867766 |  |  | A | G |  |  |  |  | G |  |  |  |  |
| 972462 |  |  | A |  |  |  |  |  |  |  | A |  |  |
| 867715 |  | G | A |  |  |  | G | G |  |  |  |  |  |
| 972128 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971253 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972772 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972578 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 972608 |  |  | **F** |  | **F** |  |  |  |  |  |  |  |  |
| 972438 |  |  | **F** |  | **F** |  |  | G |  |  |  |  |  |
| 972454 |  |  | A | **F** | A |  |  |  |  |  |  |  | gesims: tegnet/modell 1.47 (tegningen høyere) (fasadeavlesningen (vegger lest for hånd)); høyden har lav sikkerhet i Kartverket-målingen (rapport/hoyder): må sjekkes mot DOM |
| 868606 |  |  | **F** |  |  |  |  | G |  |  |  |  |  |
| 867812 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 867774 |  |  |  | G |  |  |  | G |  |  |  |  |  |
| 6246753 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-57 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-58 |  |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 867820 (430 pt², ~1 hus, avvik med grunn: frihånd); ved 867820 (1327 pt², ~1 hus, avvik med grunn: frihånd); ved 867782 (170 pt², ~1 hus, avvik med grunn: mur)

### Kvartal13

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867502 |  |  |  | G |  |  |  |  |  |  |  | A |  |
| 868460 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| 867499 |  |  |  |  |  |  |  |  | G |  | A | A |  |
| 867510 |  | G |  |  |  |  |  | G |  |  |  |  |  |
| pb-63 |  |  | **F** | G | **F** |  |  | G |  |  |  |  |  |
| pb-64 |  |  | **F** | A |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 868460 (172 pt², ~1 hus, avvik med grunn: takdel); ved 867499 (1485 pt², ~2 hus, avvik med grunn: gjerde); ved 868460 (134 pt², ~1 hus, avvik med grunn: detalj); ved 867502 (1158 pt², ~2 hus, avvik med grunn: mur); ved pb-63 (2812 pt², ~2 hus, avvik med grunn: mur); ved 867510 (160 pt², ~1 hus, avvik med grunn: detalj); ved 867510 (160 pt², ~1 hus, avvik med grunn: detalj)

### Kvartal14

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 972039 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 972012 |  |  |  | A |  |  |  | G | G | G | A | A |  |
| 870260 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870236 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| pb-7 |  |  | **F** | A |  |  |  |  |  |  |  |  |  |
| 867693 |  | G | A |  | A |  | G |  |  |  |  |  |  |
| 867707 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 867804 |  |  | A |  |  |  |  |  |  |  |  |  |  |
| pb-8 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 16308102 |  |  | A |  | **F** |  |  | G |  |  | A |  |  |
| 972063 |  | **F** | A |  |  |  |  | G |  |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 5; ulike farger: 2) |
| 867715 |  |  | A | G | A |  | G |  |  |  |  |  |  |
| 972098 | **F** |  |  |  |  |  |  |  |  |  |  |  |  |
| 972004 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 972055 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 971229 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 868584 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870228 |  |  | A |  | **F** |  |  | G |  |  |  |  |  |
| 972047 |  |  | A | G |  |  |  | G |  |  |  |  |  |
| pb-53 | A |  |  |  |  |  |  |  |  |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 870228 (3222 pt², ~1 hus, avvik med grunn: nabobit); ved 972063 (162 pt², ~1 hus, avvik med grunn: detalj)

### sistekvartal

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870198 |  |  |  | G |  |  |  | G |  |  |  | A |  |
| 870236 |  |  | A | G |  |  |  | G |  |  |  |  |  |
| 972403 |  |  | **F** |  | A |  |  | G |  |  |  |  |  |
| 870252 |  | **F** | A | G |  |  |  | G |  |  |  | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 3; ulike farger: 2) |
| 972381 | A |  |  |  |  |  |  |  |  |  |  |  |  |
| 870244 |  |  | A |  |  |  |  | G |  |  |  |  |  |
| 870228 |  |  | A |  |  |  | G | G |  |  |  |  |  |
| 870201 |  |  |  |  |  |  |  | G | A |  |  |  |  |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 870244 (4546 pt², ~1 hus, avvik med grunn: frihånd); ved 870201 (232 pt², ~1 hus, avvik med grunn: frihånd); ved 870198 (262 pt², ~1 hus, avvik med grunn: frihånd)

### tell

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867677 |  |  |  |  |  |  |  | G |  |  |  | A |  |
| 867634 |  |  | A |  | A |  |  | G |  |  |  |  |  |
| 867685 |  | **F** | A |  |  |  |  | G |  |  |  |  | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 2; ulike farger: 2) |

### Glasshytta

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 869548 |  |  | **F** |  | **F** |  |  |  | A |  |  |  |  |
| 869580 |  |  |  |  |  |  |  |  |  |  |  |  |  |

### kirke

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 867529 |  | **F** |  |  |  | **F** | G |  | A |  | A | A | slaatt_sammen: tegningen har 2 fasader på én modellvegg (vegg 6; ulike farger: 2); takform: tegning sal, modell valm |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 867529 (3600 pt², ~2 hus, avvik med grunn: landemerke); ved 867529 (162 pt², ~1 hus, avvik med grunn: detalj); ved 867529 (256 pt², ~1 hus, avvik med grunn: detalj)

### Toihuset

| hus | finnes | slaatt_sammen | omriss | gesims | mone | takform | veggfarge | takfarge | vinduer | dorer | arker | piper | merknad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 870279 |  | **F** |  |  |  | **F** |  |  | G |  | A | A | slaatt_sammen: tegningen har 5 fasader på én modellvegg (vegg 2, 1, 6; ulike farger: 3); takform: tegning sal, modell sammensatt |

Tegnet uten modellhus under (flategrupper; dom og grunn fra kilder/bygg-merknader.json, kontaktark rapport/manglende/): ved 870279 (235 pt², ~1 hus, avvik med grunn: detalj); ved 870279 (6413 pt², ~1 hus, avvik med grunn: frihånd); ved 870279 (209 pt², ~1 hus, avvik med grunn: detalj); ved 870279 (311 pt², ~1 hus, avvik med grunn: detalj); ved 870279 (253 pt², ~2 hus, avvik med grunn: detalj)

