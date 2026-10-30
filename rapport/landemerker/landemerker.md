# Landemerkene (natt/landemerker, 30.10)

Verktøy: `verktoy/landemerker.py` (sist i kjeden), elementene `bygTaarn` og `bygArkade` i src/07, `kilder/hoyde-unntak.json`.
Kontrollark: rapport/kontroll/Kvartal14.png, Kvartal10.png, Glasshytta.png, tell.png. Nærbilder fra ekte rendering (zoom 6, DPR 2):
rapport/landemerker/_arbeid/naer/ (bare lokalt).

## Rådhuset (bnr-193972012, Kvartal14)
- Plass og høyde fra DOM−DTM: platå 19,8–20,0 m over 4 × 4 ruter, midt (28,5, −87,8). Ortofoto 2024: åttekantet krans med tinder,
  ca. 4,3 m i diameter, lys grå flate inni. Toppen står 5,5 m vest for DOM-platået i fotoet: høye ting heller bort fra fotopunktet
  (relieffforskyvning). DOM ser loddrett og vinner.
- Avviket fra tegningen: projisert med kontrollkameraet står tårnaksen i tegningen 2,3 pt (under 0,5 m) fra DOM-aksen. Toppen er tegnet
  38 pt høyere; det er 45 % overhøyde (20 m · 4,28 pt/m · 0,45 = 38,5 pt), og tårnet er tegnet ca. 40 % bredere (5,8 mot 4,2 m).
  Tegningen har tårnet på samme sted, forstørret som landemerke.
- Formen etter tegningen: åttekantet skaft i lys sandstein, ett høyt rundbuevindu per side, utkraget brystning på konsoller med 16
  tinder, flatt tak, flaggstang med flagg. Tegningen har ingen hjelm, lanterne eller urskive, så modellen har det ikke.
- Hovedkroppen: h 9,79 m / th 0,35 (DOM: takfot mot gata 9–10 m, møne 12,1 m). Tilpasningen i rapport/hoyder ga 6,5 m fordi tårnet og
  fire fløyer ligger i samme omriss; unntaket står med grunn i kilder/hoyde-unntak.json.
- Gatefasaden mot SSV: hjørnefelt | fem store rundbuer i 0,45 m dyp nisje (arkadeelementet) og fem rundbuevinduer over | smalt felt
  med rundbuet dør og to smale rundbuevinduer. Veggfargen er tegningens lyse oker (221, 173, 132), som Street View aug. 2010 (gul tegl).
  Trykkets laks var feil kulør.
- Gårdsfasaden til rådhuset vises ikke i noen av tegningene (Kvartal14 er tegnet fra SSØ), så den står som før.

## Arkaden på 13394024 (Kvartal10)
Gårdsfasaden mot sør (13,8 m): fem rundbuer, 2,1 m brede, 2,9 m til toppen av buen, gesims på 3,5 m og 0,5 m dybde. Ett vindu bak
arkaden er tatt ut. Gjenstår: tegningen har loddrette felt/høye vinduer i etasjen over (ikke lagt inn), og fasaden er grå i tegningen
mot gul i modellen (merknad: trykkfila 2015). Fargen er fargeagentens.

## Voldporten (bnr-193869548, Glasshytta)
- Kroppen vises ikke i kontrollen: verktoy/kontroll_iso.mjs lot three.js frustumteste mot en håndsatt projeksjonsmatrise, og nett i
  egne grupper (portbygg, bygg med deler) ble kastet. Nå er frustumtesten slått av under kontrollrenderen.
- Høyden: DTM under huset er vollkrona (9,4–10,4 moh), så DOM−DTM (4–8 m) målte fra vollen. Fra veien i porten (7,0 moh) er takfoten
  7,5 m og mønet 10,8 m (DOM 17,8 moh). Portmur 4,4 m (bue 3,8 × 3,5 m, Street View 2010) + vaktstue 3,1 m, valmtak med kort møne og
  én pipe midt på (Street View 2010: «valm (pyramideaktig, kort møne)», én pipe; tegningen: valm mot enden).
- Vinduer: SSV-langsida som tegningen (dør ved vestenden, to vinduer), NV-enden som Street View 2010 (to vinduer), SØ-enden ingen
  (relieff og blindfelt; tegningens tomme ramme er blindfeltet).
- Kvinnen på trestubben: Street View aug. 2010 (SØ) viser en bronsestatue av en kvinne på en trestubbe ca. 15 m SØ for porten.
  Brukerfotoet fra aug. 2019 i /home/claude/streetview/bilder (bnr-193869548.jpg) viser den samme trestubben ved vingemuren uten
  statue. Den står altså ikke der i 2019. Ingen andre bilder i kildene. Ikke modellert.

## 867634 Vollmesterboligen (tell)
Ikke en egen del. DOM−DTM langs mønet: 6,9 ± 0,2 m fra 4 til 22 m, takfoten like jevn, ingen sprang i høyde eller bredde. Ett
omriss i kommunekartet, ett bygningsnummer, ett tak i ortofoto 2024. Grunnen står i kilder/bygg-merknader.json.

## Statuen (Frederik II)
Glattet innenfor det dataene allerede sier (positur i data/statue.json, lest av kommunens foto): avrundede jernsko, buklede
pluderhoser og rundet brystharnisk som omdreiningsflater, rillet pipekrage, fyldig helskjegg i stedet for en kjegle, flere segmenter
på lemmene. Jeg har ikke selv sett fotoene (kommunens foto, DigitaltMuseum, nb.no): de ligger som lenker, ikke filer, og jeg lastet dem
ikke ned. Ingen ny detalj er lagt til ut over posituren som står i dataene.

## Det jeg har sett (kontrollark og nærbilder)
- Kvartal14: tårnet er åttekantet med tinder, lys grå topp, rødt flagg og rundbuevinduer, og står bak gatefløyen der tegningen har
  det. Det er lavere enn i tegningen, og det er riktig etter DOM. Fasaden har fem dype rundbuer nede, fem vinduer oppe, hjørnefelt og
  dørfelt. Nærbildene (az −20 og 200) viser det samme i ekte rendering.
- Kvartal10: arkaden har fem buer med dybde under gesimsen, og den femte delvis bak 867588. I ekte rendering leser buene på
  zoom 6, men bakveggen ser brunlig ut, ikke svart.
- Glasshytta: Voldportens kropp er med (før: bare vinduene), med portmur og bue i enden og valmtak. Modellen er lengre enn tegningen
  (14,8 m etter omrisset og DOM, tegningen er forkortet) og står delvis over arkets ramme. I ekte rendering (az 110) ses ikke buen i
  SØ-enden fra den vinkelen.
- Statuen (rapport/torvet/statue.png): avrundet harnisk, buklede pluderhoser, rillet krage og runde jernsko er synlige fra fire
  vinkler. På kartzoom er figuren ca. 20 px høy, og detaljene ses ikke der.
- Regler (rapport/rapport.md, 30.10 09.37): alle grønne unntatt 03, 09 og 12.
