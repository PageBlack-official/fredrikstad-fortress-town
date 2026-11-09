# RAPPORT3 — runde 2: tegn alle 28 husene, Vegar dømmer etter 26

Startet 2026-11-09. Oppgave: `rapport/ferdig/OPPGAVE3.md`. Sluttgate: `python3 verktoy/rett/ferdig_sjekk.py` exit 0
(≥26 «tegnet» med tom avvik + bevis, resten `trenger_vegar` med sporsmal/forsokt/bevis, alle `"runde": 2`).

## Rammer for denne runden (fra Vegars sak PAG-1469, 09.11 — går foran publiser-stegene i OPPGAVE3)
- Ikke send noe eksternt: IKKE `sh publiser.sh`, IKKE Dropbox-kopi. Lokalt arbeid + lokal commit er greit.
- Aldri force-push. Ikke slett noe. Google-bilder aldri i git.
- Ikke rør kirka, Kaserna, forsiden, fargeoppgaven, introen.
- Publisering + Dropbox-kontaktark holdes til Vegar har sett resultatet og sagt fra.

## STATUS akkurat nå (2026-11-09, slutt på økt 1)
`ferdig_sjekk.py` = **exit 1**: 0 tegnet (mål 26), **2 trenger_vegar** (festningsmur, ferdige), 26 hus gjenstår (ikke satt til runde 2).
Dette er ærlig delstatus. Ingen hus er stemplet «tegnet» uten reell dekning («nesten er ikke lov»). Pipeline + kalibrering er verifisert, alle 28 er triagert med bilder, og de 2 festningsmur-husene er avgjort.

## Infrastruktur som er bygget denne økta (kan gjenbrukes rett)
- **`verktoy/rett/montasje.py`** (NY, i repoet): bygger bevis-montasje per hus fra `rapport/ferdig/mapping.json`:
  `python3 verktoy/rett/montasje.py --etter <renderdir> [--for <førdir>] [--ut <utdir>] [id ...]`.
  SV | (før) | etter, én rad per vegg, autocontrast på modell-rendrene. Uten `--ut` skriver den `rapport/ferdig/<id>.jpg` (det ferdig_sjekk ser etter).
- **Render-standpunkter**: `rapport/ferdig/stand-alle.json` (fra runde 1, geometri-sentroide-sikt fra SV-bilens lat/lon). 33 vegger.
- Alle 33 vegger rendret i `rapport/ferdig/renders_r2/` (modell-PNG, IKKE i git, regenereres på ~100 s).

## KALIBRERINGS-FUNN (viktig — løser hovedproblemet fra runde 1)
Runde 1 rendret med **fov 75** → husene ble små og sentrert, men ikke lesbare, og «sto ikke likt». Testet fov-sveip på Vollmesterboligen
(`/tmp/calcmp.jpg`): **fov ~45–50 gjør huset stort nok til å telle vinduer/dører og leser gavel/retning riktig.** Kameraet treffer
allerede huset (sentroiden lander på skjermmidten, f.eks. bnr-6276822 x=772 av 784). Så: **render alltid med fov 50**, ikke 75.
Kommando brukt: lagde `/tmp/stand50.json` (= stand-alle.json med fov=50) og kjørte gatekamera mot `rapport/ferdig/renders_r2`.
Montasjene i `/tmp/judge/<id>.jpg` er fov50 SV|etter og er grunnlaget for triagen under.

Rest-problem for ekte hjørne-overlegg: SV-skjermbildene er zoomet ulikt (ett fast fov matcher ikke alle), og modellen har trær/bokser
(gatemøbler) som av og til dekker huset. For å TELLE og lese farge/tak/form er fov50 godt nok. For presis hjørne-overlegg per vegg
må neste økt finjustere heading/fov/posisjon per vegg (sikt mot husets skjerm-boks fra `window.__gateHus()`, ikke bare sentroiden).

## Festningsmur-husene — AVGJORT (begge trenger_vegar, runde 2, ferdig)
Begge FINNES og er riktig plassert: matrikkel-bygningspunkt + FKB-omriss (kommunekart) + ortofoto 2024 + Kartverket-høyde (DOM−DTM)
bekrefter bygg på stedet (`rapport/bygg/se/fm_24218023.jpg`, `fm_193972276.jpg` fra `se_her.py`). Plassering/omriss/høyde er altså fra
kildene og riktige. Det eneste som ikke kan verifiseres er FASADEN (vinduer/dører/farge): ingen tegning dekker husene, og
Street View-standpunktet ser festningsmuren (husene ligger i indre gårdsrom bak vollen, ikke synlig fra gata). Derfor trenger_vegar
med presist spørsmål (står i `kilder/ferdig.json`): skal fasaden stå regel-simulert, eller finnes tegning/foto?
- bnr-24218023: matrikkel type 144 (anneks), h~8 m. bnr-193972276: type 629, SEFRAK, h~10 m, terrakotta-tak i ortofoto.

## TRIAGE av de 26 gjenstående (lest på fov50-montasjene i /tmp/judge) — hva neste økt skal gjøre per hus

### A. Ser riktige ut — trolig «tegnet» etter bedre hjørne-overlegg + ny bevis (bekreft vinduer tett)
- **bnr-193867634** (Vollmesterboligen): hvit, brunt tak, gavel/vinduer stemmer. MERK reelt avvik: modellen har **3 piper**, SV viser ~1 (nær gavel). Sjekk `piper` i data mot SV før tegnet.
- **bnr-6276016** (rød 2-et.): form/farge/vinduer stemmer godt.
- **bnr-193867723** (sandgul 2-et.): to vindusrekker + dør stemmer.
- **bnr-6276822** (vinrød 2-et.): farge/form ok, men modell-tre dekker deler — trekk kamera/ny vinkel for ren bevis.
- **bnr-6276512** (37 Heibergs): modell leser mettet BLÅ, SV er blågrå/grå — sjekk om «blågrå» er for mettet (fargekilde).
- **bnr-193971946** (hvit puss m/rundbue): buen er riktig; modell virker litt blålig-hvit — sjekk veggfarge.

### B. Konkret fiksbart i kjeden (fasade_rett / dor_farge) — gjør disse først, høyest gevinst
- **bnr-193867898** (9 Voldgaten, duebla): blå vegg stemmer, men PORT er brun i modell, blå i SV → sett `dor_farge` blå (se OPPGAVE2 «Dør- og portfarge», `src/07`, kjeden). SV okt 2019 (dør/port gyldig).
- **bnr-193868576** (41 Tøihusgaten): PORT tegnet med rundbue (typ 2), SV viser flat rektangulær tredør → typ 1 via `fasade_rett`. Vurder også veggfarge: modell er klar rød, SV er umalt tegl (brunrød). SV mai 2024 (gyldig).
- **bnr-193972292** (79 Færgeportgaten): rundbue-port i modell der SV har flat dør/vinduer → typ 2→1. Farge/høyde/rødt tak stemmer. SV mai 2024.
- **bnr-6251331** (21 Rådhusgaten, strågul): SV har GRØNN garasjeport + GRØNN butikkfront; modell har brune dører, ingen butikkfront → `dor_farge` grønn + bygg butikkfront som REGEL (ikke unntak), se OPPGAVE2. Tyngre. SV mai 2024.

### C. Farge-/mål-ID-tvil — krever tegnings-sjekk + bare 2016+-bilder for farge
- **bnr-194006187** (hvit liggende panel): modell beige/grå, SV hvit — men SV er **aug 2010** (UGYLDIG for farge). Tegningen bestemmer; bekreft hva tegningen sier, da trolig tegnet.
- **bnr-193971288** (hvit): modell-forgrunnsvegg er salviegrønn, SV (aug 2010) viser hvitt. mål-ID usikkert (hvilken vegg er huset). Finn skjerm-ID i render-json, sjekk tegning. 2010 kan ikke sette farge.
- **bnr-193972306** (grå/brun panel m/garasjeport): modell okergul, SV (aug 2010) grå/brun. Render klipper også (vegg 4). Trenger nytt standpunkt + tegnings-sjekk. 2010 kan ikke sette farge.
- **bnr-6276504** (35 Heibergs): modell leser gul sentralt, SV (apr **2024**, gyldig) hvit liggende panel. Finn mål-ID (skjermpunkt), les farge fra 2024-bildet hvis det er huset.

### D. Render bommer / klipper — lag nytt standpunkt (OPPGAVE2 «Render klipper»)
- **bnr-193867480** (v/Isegran): render viser IKKE huset (fugleperspektiv, huset ligger utenfor senterfeltet over vannet). Lag nytt standpunkt som sikter på huset (bruk SV-posisjon, sikt mot husets sentroide). SV apr 2010 (dør/vindu gyldig, ikke farge).
- **bnr-193867820** (13 Rådhusgaten, laksrosa): auto-vegg 3 klipper inn i nabobygg → render fra vegg-4-standpunkt.
- **bnr-193971954** (rød): auto-vegg 3 klipper under tak → nytt standpunkt.
- **bnr-13416419** (22 Bings gate, hvit): render mørk/utydelig → nytt standpunkt + farge-sjekk.

### E. Vindustall usikkert — les fasaden i meter (HJORNER→rett→ELEMENTER→overlegg→konverter), OPPGAVE2 gruppe 1
- **bnr-13416362** (24 Bings, oker): farge/tak stemmer, vindusrekke usikker.
- **bnr-193868088** (lys blågrå): farge/tak/nabo ok, vindustall usikkert.
- **bnr-193867855** (hvit 1,5-et.): dør/vindu usikre (SV aug 2010, gyldig for vindu/dør).
- **bnr-193867901** (8 Voldgaten, oransje): dørplassering usikker.
- **bnr-193867952** (10 Voldgaten, terrakotta): vindustall + dørfarge (brun vs hvit).
- **bnr-193867626** (26/27 Kirkegaten, laksrød): vegg 2 ok, vegg 3 gavl ikke bekreftet (bruk UNNTA + ny vinkel).
- **bnr-193867804** (51 Kasernegaten, laks): bred port vs smal dør — porttype/breddesjekk.

### F. Stort tak-/struktur-avvik — tyngst, kan ende trenger_vegar
- **bnr-13415889** (9/10 Ove Ramms gate): modellen mangler **mansardtak + takarker (dormers)**, og vegg 3 har annen farge (grønn vs grå) + annet tak enn vegg 0. Mulig **to hus i én polygon** (`kilder/husdeling.json`). Bruk `kilder/tak-tegning.json` med `kropper`. SV mai 2024.

## PRESIS NESTE-STEG-REKKEFØLGE for neste økt
1. `export PATH=$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH`. `python3 bygg.py enkel`. `cp ut/enkel/index.html /tmp/f22/for.html` (før-modell).
2. Gjør gruppe B-fiksene i kjeden (dor_farge, fasade_rett typ2→1), så C/E der tegning/2016+-bilde gir svar, så D (nye standpunkt), til slutt F.
3. Etter hver bolk: `python3 verktoy/bygg_kjede.py` (nohup ~90 s) + `python3 bygg.py enkel`, render `/tmp/stand50.json` → `renders_r2`, `montasje.py` → se på bildet.
4. Når et hus stemmer: `montasje.py --for /tmp/f22/for-renders --ut rapport/ferdig <id>` for ekte SV|før|etter-bevis, sett `kilder/ferdig.json` {status tegnet, runde 2, bevis, avvik []}.
5. `ferdig_sjekk.py` til exit 0 (≥26 tegnet). Så lokal commit. IKKE publiser/Dropbox (PAG-1469).

## Hus for hus (runde 2) — logg etter hvert
- 2026-11-09 økt 1: bnr-24218023 + bnr-193972276 → trenger_vegar (finnes i kildene, fasade uverifiserbar bak voll). Resten triagert, se over. Ingen datarettinger kjørt enda.
