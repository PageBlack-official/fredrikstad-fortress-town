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
