# Kvartal-QA: strektegningene fra 2015 mot 3D-modellen

Nattskift 28.10.2026 (Claude, alene). Modell v34 (`ut/enkel/index.html`, bygd fra grenen `natt/kvartal-qa`). Ingenting i `src/` eller `data/` er rørt. Alt under «Avvik jeg ser» er observasjoner, ikke rettelser.

## Hva som ligger her

- `<tegning>.jpg` – ett kontrollark per kvartaltegning (17 stk.): strektegningen til venstre, modellen til høyre i samme utsnitt og målestokk. Byggene er merket med de fem siste sifrene i id-en (bnr) eller `pb-n`, og hele id-en, navn, fasadekilde og høyde står under arket. Grønt merke = fasade fra kvartaltegning, oransje = antatt (reglene), grått = ingen fasadekilde. `~` = koblet i runde 2 eller for hånd (se under). «(utenfor)» = punktet ligger utenfor utsnittet og er satt i kanten.
- `oversikt.jpg` – plan over Gamlebyen (nord opp) med hvert bygg farget etter tegningen det er koblet til, og tabellen med tall. Rødt omriss = gml-bygg uten tegning, lilla omriss = koblet til flere tegninger. Trykket og tegningene er ikke brukt i dette bildet.
- `vinkler.json` – målingene bak vinkelvalget per tegning.
- `../../kilder/kvartal-kobling.json` – koblingen (KILDE i git): per tegning fil, transformasjon tegning→trykk, residual, inliers, bygg-id-er, antall med fasade fra tegning/antatt, og byggene som bare treffer nabokvartal i kanten (`kant`).

Kildetegningene (`kilder/kvartal-ai/`), 2019-trykket og arbeidsfilene (`_arbeid/`: masker, modellbilder, visninger) ligger bare lokalt og er i `.gitignore`.

## Metode

1. **Rastrering.** De 17 .ai-filene (PDF inni) lastet ned fra Dropbox og rastrert med PyMuPDF på 150 dpi med alle lag på (`verktoy/kvartal_qa.py rastrer`).
2. **Registrering mot 2019-trykket.** SIFT (ikke ORB: skalaforskjellen er ~3×, og SIFT tåler den) + RANSAC similaritet, prøvd med rasteret nedskalert til 0,2–0,6. Beste forsøk = flest inliers. «Sikker» krever ≥ 12 inliers, median ≤ 3 px og at minst to skalaer gir samme transformasjon. 14 tegninger registrerte sikkert ved første forsøk, alle med median 0,20–0,32 px og skala 0,30–0,34 (tegningene er utsnitt av samme vektortegning, så skalaen skal være lik; median 0,322).
   - **kirke**: SIFT ga bare 9 inliers, men maskert malmatching (TM_CCOEFF_NORMED) i samme skala lander 0,7 px fra SIFT-svaret, med klar topp. Godtatt som kryssjekket.
   - **tell** og **Glasshytta**: SIFT fant dem ikke (små hus, trær over i trykket). Jeg fant dem med øynene i trykket og satte et anker (`ANKER` i `kvartal_qa.py`), deretter malmatching i ±20 px rundt ankeret i fast skala. tell = Ingeniørgården (23) med naboene; sjekket med kantoverlegg, sitter innen et par piksler. Glasshytta er **to hus limt sammen fra hver sin kant av byen**: huset på buen = Voldporten med vaktstuen (25), huset med valmtak og buedør = ved Ravelinporten (27). Hver del har sin egen transformasjon. For huset på buen trekker malmatchingen mot tallet «25» som ligger over huset i trykket, så ankeret står fast (justert for øyet, usikkerhet ~5 px). Begge markert USIKKER i koblingsfila.
3. **Kobling.** Bygg med `gml=1`, ikke skjult, med `px2019` (rapport/farger2019.json) innenfor tegningens tegnede omriss i trykket (gårdsrom fylt, utvidet 15 px). Tegnede biter mindre enn 15 % av hovedmotivet regnes som nabokvartal i kanten og føres som `kant`, ikke som tegningens bygg (det var grunnen til de doble koblingene i bevisarkene 23.10).
   - Runde 2: en tegnet bit uten et eneste bygg får nærmeste ukoblede bygg innenfor 65 px (`bygg_naer`): Krutthuset (Kvartal3, 28 px), Vollmesterboligen (tell, 48 px), Voldporten med vaktstuen (Glasshytta, 62 px).
   - Runde 3: bygg med `fasade_kilde=kvartaltegning` er lest fra en tegning og skal ligge i en. To sto ukoblet og er koblet til nærmeste omriss: Artillerigården bnr-193868061 (Kvartal3, 14 px) og Kommisjonsgården bnr-193868428 (Kvartal4BITMP, 27 px).
   - For hånd (`MANUELT`): Voldportravelinet bnr-193869580 til Glasshytta, fordi legendenummer 27 står ved huset i trykket mens px2019 ligger ~150 px unna.
   - Avvik fra briefen: runde 2/3 og «kant» er lagt til fordi px2019 bommer mer enn 25 px i utkanten av byen (opptil ~150 px ved Ravelinporten). Alt som ikke er rent px2019-i-omriss er merket i fila, så det kan sjekkes.
4. **Kamera og vinkel.** Senter = snittet av fotavtrykkenes tyngdepunkt, zoom = 372 / (0,95 × utstrekning) (minst 100 m utstrekning for tegninger med ett–to bygg). `__vis(az, zoom, x, y)` tar modellmeter med y nord (src/15_loop.js → tilLngLat). Vinklene: **az 20**, regnet ut ved å dekomponere `kilder/ai/ai/modell_h_til_2019.npy` (trykket er sett mot kompassretning 340°, ~50° over horisonten, 3,245 trykk-px per meter), og **az 40**, plakatvinkelen i kartet.
   Vinkelen velges ved måling, ikke skjønn: byggenes skjermpunkt (`__skjerm3` midt på veggen) legges over byggenes punkt i tegningen (px2019 ført tilbake) med kjent målestokk (3,245 trykk-px/m ÷ tegningsskala × kameraets meter per piksel) og rotasjonen låst til 0; bare forskyvningen tilpasses (median). Lavest restavvik vinner. **az 20 vinner på alle 14 tegningene som kan måles (≥ 3 bygg)**, typisk 7–13 trykk-px mot 17–37 for az 40. Får rotasjonen gå fri, vil az 20 dreie –6° til +6°, az 40 –8° til –29°. Det er altså az 20 som står samme vei som tegningene; plakatvinkelen (40) gjør ikke det.
   Samme tilpasning legger modellbildet i tegningens utsnitt og målestokk på arket.
5. **Ark.** `verktoy/kvartal_ark.py` (via `kvartal_qa.py ark`). JPG, 1600 px bredt.

Nettleser: hodeløs Chromium med swiftshader, ~70–90 s per bilde (34 bilder + 4 på nytt). Første kjøring ga feil bilder: `__kam()` viser forrige visning til kartet har tegnet et nytt bilde, så ventesløyfa slapp for tidlig. Rettet (venter til senter og asimut står på målet), alt tatt på nytt.

## Tall per tegning

| Tegning | Bygg | Fasade fra tegning | Antatt | Ingen | Residual (px) | Inliers | Restavvik az 20 / az 40 (trykk-px) | Merknad |
|---|---|---|---|---|---|---|---|---|
| Kvartal2BITMP | 16 | 9 | 7 | 0 | 0,25 | 23 | 13,6 / 20,8 | |
| Kvartal3 | 6 | 5 | 1 | 0 | 0,30 | 42 | 9,0 / 36,6 | 2 i runde 2/3; tegningen er satt sammen av biter |
| Kvartal4BITMP | 13 | 8 | 5 | 0 | 0,25 | 18 | 6,1 / 22,9 | 1 i runde 3 |
| kvartal5 | 15 | 10 | 5 | 0 | 0,24 | 66 | 11,7 / 17,5 | |
| kvartal6 | 18 | 8 | 9 | 1 | 0,22 | 75 | 9,7 / 17,1 | |
| kvartal7 | 18 | 10 | 8 | 0 | 0,28 | 29 | 11,3 / 29,8 | |
| Kvartal8BITMAP | 16 | 7 | 9 | 0 | 0,24 | 22 | 8,5 / 19,7 | |
| Kvartal9 | 20 | 8 | 12 | 0 | 0,24 | 41 | 7,4 / 20,0 | 9 bygg i kant |
| Kvartal10 | 14 | 9 | 5 | 0 | 0,20 | 48 | 8,9 / 20,2 | |
| Kvartal11 | 4 | 2 | 2 | 0 | 0,23 | 29 | 12,0 / 26,3 | |
| Kvartal12 | 25 | 13 | 11 | 1 | 0,30 | 65 | 7,4 / 20,9 | 2 i kant |
| Kvartal13 | 4 | 3 | 1 | 0 | 0,30 | 13 | 30,1 / 45,7 | modellutsnittet usikkert (se under) |
| Kvartal14 | 19 | 8 | 11 | 0 | 0,32 | 47 | 12,2 / 25,4 | 3 i kant |
| sistekvartal | 6 | 5 | 1 | 0 | 0,27 | 44 | 7,6 / 25,0 | Labratoriet limt inn nede til venstre |
| tell | 2 | 1 | 1 | 0 | anker | – | for få bygg | USIKKER registrering |
| Glasshytta | 2 | 0 | 2 | 0 | anker | – | for få bygg | USIKKER, to hus fra hver sin kant |
| kirke | 1 | 0 | 0 | 1 | 0,38 | 9 | for få bygg | kryssjekket (0,7 px) |

Sum 199 koblinger, 188 ulike bygg av 267 synlige gml-bygg. 11 bygg står i to tegninger (naboer der tegningene overlapper; lista står i koblingsfila). 79 gml-bygg uten tegning er alle `antatt`; de ligger stort sett der det ikke finnes kvartaltegning (kvartalet nord ved Færgeporten/37, Tøihuset/Kruttårnet-området i vest, Isegran, og husene sør og øst som i trykket står under tegnforklaringen eller utenfor arket). Alle 97 bygg med `fasade_kilde=kvartaltegning` er nå koblet til en tegning.

## Hva som er usikkert

- **px2019 bommer.** Punktene er satt fritt; i sentrum 5–25 px, i utkanten mye mer (Ravelinporten ~150 px, Voldporten ~60 px). Et bygg kan derfor være koblet til nabotegningen eller mangle. Bygg med punkt rett utenfor omrisset er ikke tatt med (unntak: runde 2/3 over). Bygg som i arket står med punkt på gata eller i et tomt gårdsrom i tegningen (f.eks. 67820/67839 i Kvartal11, 68525/71946/68339/68290/67588 i kvartal7) er trolig naboer.
- **Tegninger satt sammen av biter** (Kvartal3, Kvartal13, sistekvartal, Glasshytta, tell): bitene står ikke nødvendigvis med riktig avstand til hverandre, så én forskyvning kan ikke treffe alle. Kvartal13 har høyest restavvik (30 px) av den grunn; der skal arket leses hus for hus. Glasshytta har eget utsnitt per hus.
- **tell og Glasshytta** er registrert med anker jeg satte for øyet. Huset på buen (25) står fast uten malmatching.
- **kirke**: tårntoppen kommer ikke med i modellbildet (utsnittet stopper over kuppelen). Tårnhøyden er derfor ikke sammenlignet.
- Modellbildet er tatt med kartets egen helning (pitch 42° på liggende skjerm), trykket er ~50° over horisonten. Høyder ser derfor litt lavere ut i modellen enn i tegningen; vurder etasjer og vinduer, ikke absolutt høyde, på arkene.

## Avvik jeg ser (observasjoner, ikke rettelser)

Generelt: modellen har nesten alle tak i samme lyse teglrøde; tegningene har mørkere brunrøde, grå og nesten svarte tak i mange kvartal. Gårdsrom som er tomme og hvite i tegningene har ofte plen og trær i modellen.

- **Kvartal2BITMP**: Fasaderekken mot gata (68142 Prestegården, 68150 Salamandergården, 72292, 68096) stemmer i farger og to etasjer. Inne i gårdsrommet viser tegningen en lang grå mur/fløy og ett lite frittstående uthus; modellen har tre–fire små hvite hus (99132, 68703, 71350, antatt). Hjørnebygget til høyre er rødt med lav mur langs gata i tegningen, hvitt i modellen.
- **Kvartal3**: Artillerigården (68061) er lang med mange vinduer og tre små arker/gavler bak i tegningen; modellen har to tverrgavler. Krutthuset (69556, 28) står utenfor modellutsnittet fordi biten er limt inn langt fra resten i tegningen.
- **Kvartal4BITMP**: Godt samsvar i form. Binggården (68363) er i tegningen lys med valmtak og symmetrisk vindusrekke; modellen viser hvitt hus med saltak.
- **kvartal5**: Muldvadgården (68223) gul i begge. Midtbyggene har mørkt grått tak (72209) og mørk rødbrun fasade (rundt 51323) i tegningen, rødt tak og hvit vegg i modellen.
- **kvartal6**: Den gamle spisesal (68045) har mørkt grått tak i tegningen, rødt i modellen. Grønt hus (71334) grønt i begge. Innerbyggene har grå vegger i tegningen, hvite i modellen. Hjørnebygget foran (67952) oransje med arker i begge.
- **kvartal7**: Gårdsrommet er stort og tomt i tegningen; modellen har lave bygg der (51765 h 2,9, 91718, 71369). Kan være bygg som kom etter 2015, eller bygg tegningen utelot.
- **Kvartal8BITMAP**: Langbygget øverst (68282) har grå vegger og mørkt tak i tegningen, hvitt og rødt i modellen. Det blå huset (14904) og det oransje (68266) stemmer. Gårdsrommet til venstre har plankegjerde og er tomt i tegningen, plen og trær i modellen.
- **Kvartal9**: Gamlebyen modelljernbanesenter (67898) har lyseblå fasade i tegningen, hvit i modellen. Det lange bygget til venstre foran (67863) har grå vegg i tegningen og oransje i modellen. Hjørnebygget til høyre har butikkvinduer i tegningen.
- **Kvartal10**: Tegningen har et lite tårn/takrytter bak (ved 68711) og en rekke mørke arker på gårdsfløyen (ved 71911/94024); jeg finner ikke tårnet i modellen, og arkene er færre. Vennehaabet (67596), langbygget foran (87370) og Dunkejongården (67588) stemmer i farge og form.
- **Kvartal11**: Infanterikasernen stemmer godt (U-form, to etasjer, piperekken, gårdsmur med to porter). Modellen har et mørkt glassbygg midt i gårdsrommet som ikke finnes i tegningen (2015). 67820 og 67839 er trolig naboer, ikke en del av tegningen.
- **Kvartal12**: Godt samsvar i rekkene. 46753 (h 2,8) ligger under det grå taket på den lange to-etasjes rekka foran i tegningen; sjekk om høyden er for lav.
- **Kvartal13**: Kommandantgården (67499) er U-formet med rødt tak i begge; Kiørboegården (67502) grå med mørkt tak i begge. Tegningen viser et plankegjerde fra Kommandantgården ned mot Ekserserhuset og en mur rundt Kiørboegårdens gårdsrom.
- **Kvartal14**: Det nye rådhus (72012) har et høyt tårn med flagg og mørk brun fasade med buede vinduer i tegningen; i modellen ser jeg bare en lav, mørk pyramidetopp og rød/rosa vegg. Tårnet ser mye lavere ut enn i tegningen (målt bare med øyet).
- **sistekvartal**: Rekka (70201 blå, 70228 gul, 70236 lys, 70252 grå) stemmer i farger. Tegningen har flere bygg bak rekka (gule hus og et hus med mørk gavl) enn modellen viser.
- **tell**: Ingeniørgården (67677) har i tegningen en to-etasjes grå del og lavere hvite deler; i modellen er hele L-en like høy (h 5,9). Den lave oransje bygningen i tegningen finner jeg ikke i modellen. Vollmesterboligen (67634) står lenger fra Ingeniørgården i modellen enn i tegningen.
- **Glasshytta**: Voldporten med vaktstuen (69548) står på en portbue i tegningen; modellen viser et vanlig hus uten bue. Huset ved Ravelinporten er lite og kvadratisk med valmtak og buedør i tegningen; Voldportravelinet (69580, h 2,6) i modellen er langt og smalt med tverrgavl. Enten er det et annet bygg, eller fotavtrykket/taket er feil.
- **kirke**: Korsformet skip med grå tak og tårn med grønn kobberkuppel i begge. Tårnhøyden er ikke sammenlignet (se usikkert).

## Kjøre på nytt

    python3 -I verktoy/kvartal_qa.py rastrer      # krever .ai-filene i kilder/kvartal-ai/ (Dropbox)
    python3 -I verktoy/kvartal_qa.py registrer    # 14 sikre med SIFT, kirke kryssjekket, tell og Glasshytta med anker
    python3 -I verktoy/kvartal_qa.py kobling      # skriver: gml-bygg 267 koblet 188 i flere 11
    python3 bygg.py enkel
    node verktoy/kvartal_bilder.mjs ut/enkel/index.html rapport/kvartal-qa/_arbeid/visninger.json rapport/kvartal-qa/_arbeid   # ~50 min
    python3 -I verktoy/kvartal_qa.py ark          # arkene, oversikt.jpg og vinkler.json
