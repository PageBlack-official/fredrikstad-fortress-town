# RAPPORT3 — runde 2: tegn alle 28 husene, Vegar dømmer etter 26

Oppgave: `rapport/ferdig/OPPGAVE3.md`. Sluttgate: `python3 verktoy/rett/ferdig_sjekk.py` exit 0
(≥26 «tegnet» med tom avvik + bevis, resten `trenger_vegar` med sporsmal/forsokt/bevis, alle `"runde": 2`).

## Rammer (PAG-1469, 09.11 — går foran publiser-stegene i OPPGAVE3)
- Ikke send noe eksternt: IKKE `sh publiser.sh`, IKKE Dropbox. Lokalt arbeid + lokal commit er greit.
- Aldri force-push. Ikke slett noe. Google-bilder aldri i git. Ikke rør kirka/Kaserna/forsiden/fargeoppgaven/introen.

## STATUS (2026-11-09, slutt på økt 2): `ferdig_sjekk.py` = exit 1 — **12 tegnet, 2 trenger_vegar, 14 gjenstår**
Fra 0 tegnet (runde 1) til 12. De 14 gjenstående har ekte restavvik (ikke bare «usikker») som krever metertlesing av fasade,
nytt standpunkt, nytt element (butikkfront/mansard), eller Vegars skjønn. Ingen hus stemplet tegnet uten reell dekning.

### Tegnet (12): bnr-193867634, 6276016, 193867723, 6276512, 194006187, 6276504, 193971288, 193971946, 193868576, 13416362, 193867626, 193972292
### Trenger_vegar (2): bnr-24218023, bnr-193972276 (festningsmur)

## TRE SYSTEMFUNN denne runden (gjelder alle framtidige byer)
1. **fov 50, ikke 75.** Render husene med fov ~50 (zoom), ellers blir de for små til å telle vinduer. `/tmp/stand50.json` = stand-alle.json med fov 50. Kameraet treffer huset (sentroide på skjermmidt); kalibreringen i RAPPORT.md gjelder.
2. **Autocontrast forvrenger kulør.** `montasje.py` strekte modell-rendrene (runde 1-arv) → bleke kulører ble mettet (lys blågrå → blå). Mange av runde 1s «fargeavvik» var DETTE + mål-ID-forveksling (nabo lest som mål). Nå: `montasje.py` strekker bare med `--strekk` (av som standard). Bruk `--strekk` BARE når fasaden er utbrent av sol (f.eks. 13416362). For kulør: les `vegg`-verdien i data (sourced), ikke det strukne bildet.
3. **Fargepalett-grense (RETTET i src/07).** Dør/karm/element-fargene lå i `vec3 uPal[64]`; 229 distinkte farger → 165 falt stille til brun standard (6251331 grønne dører #141, 193867952 hvit dør #157, 193972292 grå port #94). Byttet til DataTexture (FloatType, NearestFilter): samme verdier/indekser (hus ≤64 byte-identisk), ingen uniform-grense, trygt på alle GPU-er. Verifisert: 6251331 dører grønne, 6276016 uendret, ingen JS-feil. Regler kjøres for full verifisering (se nederst).

## Verktøy/filer
- `verktoy/rett/montasje.py` — bevis SV|(før)|etter. `--for /tmp/f22/for-renders --etter <dir> --ut <dir> [--strekk] [id…]`.
- `verktoy/gate_avlesning.py` — NY regel: maalt-`port` med `"flat": true` blir typ 1 (flat); ellers rundbue (60 eksisterende porter uendret).
- Render alle: `PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html /tmp/stand50.json rapport/ferdig/renders_r2`. Før-modell: `/tmp/f22/for.html` + `/tmp/f22/for-renders`.
- `verktoy/se_her.py x y rad navn` — festnings-eksistens (ortofoto 2024 + FKB + DOM−DTM), bilder i `rapport/bygg/se/` (ikke i git).

## Festningsmur (2 trenger_vegar) — begge FINNES (matrikkel+FKB+ortofoto 2024+Kartverket-høyde); fasaden uverifiserbar bak vollen uten tegning. Spørsmål i `kilder/ferdig.json`.

## DE 14 GJENSTÅENDE — presist hva som trengs

### Dørfarge rendrer nå riktig (palett-fiks), men ANDRE restavvik:
- **bnr-6251331** (strågul): dører grønne nå, men **butikkfront mangler** (maalt-lesningens `butikk`-elementer avvises, kvartaltegning vinner). Bygg butikkfront som REGEL (OPPGAVE2) + finn hvorfor maalt avvises (gate_avlesning `maalt_avvist`/kantsjekk).
- **bnr-193867952** (10 Voldgaten, terrakotta): garasjeport beige nå, men mangler **hvit inngangsdør** (SV mai 2024, m/trapp, sentralt) — har vindu der. Metertles vegg 6, legg inn dør.
- **bnr-193867898** (9 Voldgaten, duebla): vegg+vinduer stemmer. Dør brun; Vegar leste «1 rød dør, midt-venstre» (uten hex). Trenger hex → sett `dorfarge` i avlesning.
- **bnr-193867901** (8 Voldgaten, oransje): vegg stemmer. Avklar om SVs blå garasjeport hører til dette huset eller nabo; hvis huset: legg inn blå port.

### Metertlesing av fasade (HJORNER→rett→ELEMENTER→overlegg→konverter):
- **bnr-193867804** (51 Kasernegaten): egen fasade = kvartaltegning, 1 smal dør; SV har BRED ornamentert rektangulær port (arken i rund1-bildet var NABO). Metertles bredere port.
- **bnr-193868088** (lys blågrå): vegg [178,196,206] sourced/riktig (ikke «for blå» — det var strekk). Modell mangler trolig ~1 nedre vindu + egen dør. Metertles.
- **bnr-193867855** (hvit 1,5-et.): hvit + form stemmer. Dør-/vindusramme-detaljer (SV aug 2010: grønne rammer, mørk rød port) må leses.
- **bnr-13416419** (22 Bings gate): modell kremfarget m/færre, større vinduer; SV mai 2024 hvit m/mange ornamenterte vinduer + mørkt mansardtak. Sjekk vegg-kilde + metertles vinduer.

### Nytt standpunkt (render bommer — pullback 12 m i `/tmp/standpb.json` hjelper delvis, må også re-sikte heading mot sentroide):
- **bnr-193971954** (rød butikkgård): pullback viser rødt hus til venstre, nabo-gavl dekker midten. Sikt heading på sentroide. SV v3: rødt hus m/butikkfront, rød gavl, hvite vinduer.
- **bnr-193867820** (13 Rådhusgaten, laksrosa): pullback viser rosa hus bak forgrunnsvegg. Re-sikt / vegg-4-standpunkt.
- **bnr-193867480** (v/Isegran): render viser fugleperspektiv (huset over vannet, utenfor senterfeltet). Lag nytt standpunkt som sikter på huset. SV apr 2010: lite låverødt 1-et.

### Tungt (kan ende trenger_vegar):
- **bnr-13415889** (9/10 Ove Ramms gate): modell flatt rødt tak + 2 arker; SV har mansardtak m/mange takarker (v0), vegg 3 grå m/svart mansard. Ikke i husdeling. Bygg mansard+arker via `kilder/tak-tegning.json` (`kropper`), sjekk om to hus i én polygon. Kan tegningen ikke uttrykke mansard → trenger_vegar.

### Okklusjon/balkong:
- **bnr-6276822** (2 Lammers gate, vinrød): vegg/dør/vinduer stemmer, men modell-tre dekker fasaden i bevis (trenger tre-fritt standpunkt) OG SV ser ut til å ha balkong/altan i 2. etg som modellen mangler. Bekreft balkong, legg inn, render fritt.

## NESTE ØKT — rekkefølge
1. `export PATH=$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH`. Sjekk `/tmp/regler.log` (shader-verifisering) — bare regel 03 (kjent rød) skal være rød.
2. `python3 bygg.py enkel`; `cp ut/enkel/index.html /tmp/f22/for.html`; render `/tmp/stand50.json` → `/tmp/f22/for-renders`.
3. Ta de 14: først metertlesing (193867952, 193868088, 193867804, 193867855, 13416419), så standpunkt (193971954, 193867820, 193867480), så butikkfront (6251331), så dør-hex (193867898, 193867901), så tak (13415889), så 6276822.
4. Per hus: rett i kjeden → `bygg_kjede` (nohup ~1m46) + `bygg enkel` → render → `montasje.py --for … --ut rapport/ferdig <id>` → `kilder/ferdig.json` {tegnet, runde 2, bevis, avvik []}.
5. `ferdig_sjekk.py` til exit 0. Commit. IKKE publiser/Dropbox (PAG-1469).

## Logg
- 2026-11-09 økt 1: montasje-verktøy, fov50-kalibrering, festningsmur → trenger_vegar. (commit 7929e79)
- 2026-11-09 økt 2: autocontrast-funn + palett-tekstur-fiks (src/07) + flat-port-regel. 12 hus tegnet totalt. (commits d27f3f3, f932ea6, 9ea4bef m.fl.)
