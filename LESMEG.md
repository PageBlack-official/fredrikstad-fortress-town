# Gamle Fredrikstad – tegnet 3D-kart (Smart Old Town)

Kilden til kartet. Alt som publiseres bygges herfra; ingenting rettes i ferdig HTML.

    python3 bygg.py enkel     én fil (ut/enkel/index.html) – til artefakt, e-post, test
    python3 bygg.py server    ut/server/ – legges på hvilken som helst webserver; installerbar som app (PWA), virker uten nett etter første besøk
    python3 regler/kjor.py    kjører alle regelsjekkene, skriver rapport/rapport.md og bevisbilder

## Mapper
- data/      én JSON per emne (bygg, veier, vann, trær, legende, porter, broer …). Hva hvert felt kommer fra: KILDER.md
- src/       koden, én fil per del, i rekkefølge (00_oppsett … 16_klikk). stil.css, kropp.html, mal.html, manifest, sw.js
- assets/    teksturer (vann, pensel), app-ikoner, logo
- regler/    Vegars regler som kjørbare sjekker; hver skriver rapport/<regel>.md og evt. bevisbilde
- kilder/    referanser som sjekkene måler mot (flyfoto med transform)
- verktoy/   hjelpere (hodeløs lasting, rendring)
- ut/        bygd resultat (ikke kilde)

## Status 23.10.2026 (v30)
Motor: MapLibre GL JS 6.14.0 (kamera, gester, koordinater). Byen: three.js 0.160 som custom layer. Koden er filer i rekkefølge i ett modulskop (ikke ekte ES-moduler ennå).
Geometrien er slått sammen (v29): vanlige hus ligger i ett nett per materiale med byggindeks per punkt; løft og vekst per bygg går gjennom hus-teksturen tHus (05_bygg: settHus). Et hus som skal endres, endres i data (rettelser.json) og bygges på nytt, ikke i scenen. Grupper som flyttes som objekter (kirka, portbygg, bygg med deler, broer) slås sammen med flatGruppe.
Neste: kvalitetssikring kvartal for kvartal (bevisark tegning mot modell), deretter regel 02–04 grønne. v30: husfarger dømt visuelt mot 2019-trykket (rapport/farger-dom, rettelser i data/rettelser.json), trær fra flyfoto på flatene og dagens rekker på vollene. Åpne datakilder til POI-laget: rapport/apne-data.md.

## Sola finner byen (28.10)
Introen: overskyet → solkant vandrer over byen → kastskygger vokser fram → sola lander på 250°/42°. Lyset følger kameraets vei (bearing),
så det er riktig uansett bildefrekvens; avbrutt intro henter resten inn på 0,8 s. Shaderen: `solHer(wq)` i GL_SOL_F (02_lys) gir 0–1 per
punkt, `skyggeMask()` og de lyse tonene blandes med den; `U_SOL` deles av alle materialer gjennom `kobleSol()` (15_loop ved load).
Stillbilder langs veien: `node verktoy/sol-intro-stills.mjs ut/enkel/index.html rapport/_sol` (u 0, 0,25, 0,5, 0,75, 1), fordi
programvare-GPU-en ikke kan vise introen i fart; dommen i fart er Vegars, på /prove/.

## Faste ID-er: bygningsnummeret fra Matrikkelen (26.10)
Hvert bygg har en fast nøkkel i `id`: `bnr-<bygningsnummer>` når bygget finnes i Matrikkelen (Kartverket, CC BY 4.0), ellers `pb-<løpenummer>`. Bygningsnummeret er statens nøkkel, den samme kommunen, Forsvarsbygg, meglere og Riksantikvaren bruker, og det finnes i alle norske byer. `matrikkel` på bygget har bygningsnummer, uuid, bygningstype, kulturminne/SEFRAK og adresse- og matrikkelenhet-id (eierkoblingen).
Rettelser, porter og legende peker på id, aldri på plass i lista. Alle id-er som er delt ut, står i kilder/id-register.txt; en id slettes aldri, bygget skjules med grunn. Regel 14 passer på dette.

    python3 verktoy/matrikkel.py hent     henter bygningspunktene (kilder/matrikkel-bygningspunkt.json)
    python3 verktoy/matrikkel.py koble    gir nye bygg id, oppdaterer matrikkelfeltet, rører aldri en id som finnes

All lesing og retting av data går gjennom datalag.py, som bygg.py, regelsjekkene og verktøyene deler.

## Rettelseslaget (23.10)
Grunndataene i data/ er generert (OSM, trykkfila, kvartaltegningene) og kan lages på nytt. Alt Vegar retter ligger i data/rettelser.json, én linje per rettelse, og legges oppå ved hvert bygg:

    [{"emne":"bygg","id":"bnr-193867537","op":"sett","felt":"vegg","verdi":[214,96,80],"hvem":"Vegar","dato":"2026-10-24","grunn":"trykkfila"},
     {"emne":"bygg","id":"pb-12","op":"skjul","hvem":"Claude","dato":"2026-10-23","grunn":"flyfoto: parkeringsplass"}]

Operasjoner: sett (felt = verdi), skjul og ny. Rettelser slettes aldri, de overstyres av en nyere linje (et skjult bygg vises igjen med `sett skjul null` og grunn).

`ny` (29.10) legger til et objekt grunndataene ikke har: `{"emne":"bygg","id":"pb-25","op":"ny","verdi":{…hele bygget, med id…},"hvem":…,"dato":…,"grunn":…}`.
datalag.legg_paa_rettelser lager alle nye objekter først (bakerst i lista, i rekkefølgen de står), så sett/skjul kan peke på dem uansett hvor
linjen står; samme id i flere ny-linjer: den nyeste vinner; en ny-id kan ikke finnes i grunndataene. Plassene til grunndataene endres aldri
(rapport/hoyder og regel 02 bruker plass i lista). Id-en registreres i kilder/id-register.txt som alle andre, og regel 14 teller nye bygg med.
Redigeringsmodusen skal skrive nye objekter på samme måte. Flytting er `sett p`.

## Vinduer og dører på hus uten tegning (27.10)
Fasit er husene lest fra kvartaltegningene (`fasade_kilde: kvartaltegning` og v33-rettelser). De andre (`antatt`) får vinduer og dører fra reglene målt på fasiten:

    python3 rapport/vinduer/mal_tegningene.py    måler fasit-husene på nytt (rapport/vinduer/maalinger.json)
    python3 verktoy/vinduer_regler.py           lager vind for de antatte husene som rettelser (idempotent; --tørt viser bare)
    python3 rapport/vinduer/kontrollark.py      fasadetegninger før/etter og fasit til sammenligning

Endres h på et antatt hus, kjøres vinduer_regler.py på nytt (rettelser følger ikke høyden av seg selv; regel 17 sier fra).

## Bakkeflatene mot ortofoto 2024 (27.10)
Fasit for torg, gater, plener, gårdsrom og parkering er kommunens ortofoto 2024 (bare kontroll, ikke i git, se KILDER.md).

    python3 verktoy/flater.py hent        ortofotofliser + kommunens parkeringslag
    python3 verktoy/flater.py id          faste id-er til grønt (gr-) og gårdsrom (ga-)
    python3 verktoy/flater.py parkering   data/parkering.json og data/flater.json fra kilder/flater-maalt.json (flater målt for hånd)
    python3 verktoy/flater.py maal        gress i gårdsrommene og klipping av grønt over parkering, som rettelser
    python3 verktoy/flater.py ark etter   kontrollark per område i rapport/flater/

Tegnes i src/17_bakkeflater-og-parkering.js (plener, gårdsrom, målte flater, parkering). Regel 15 måler avvikene.

## Vannet mot ortofoto 2024 (27.10)
Fasit for strandlinja (Glomma, vollgravene, kaiene, Isegran) er det samme ortofotoet. data/vann.json er OSM-vannet (kilder/vann-osm.json) rettet mot vannmasken fra fotoet, med fast id (vn-) og kanttype per kant: k = kai/mur/brygge, n = naturlig. Kanttypen og det fotoet ikke ser (smale grøfter i sivet) står for hånd med grunn i kilder/vann-maalt.json. Under trekroner og takutstikk (kartets egne trær og hus) gjelder OSM-kanten.

    python3 verktoy/vann.py hent        ortofotoflisene over hele kartrammen
    python3 verktoy/vann.py maske       vannmasken (kilder/ortofoto-2024/vannfasit.png, ikke i git)
    python3 verktoy/vann.py lag         data/vann.json og data/vannfelt.json (g-kanalen = kai, r = avstand til land)
    python3 verktoy/vann.py kontroll    kontrollark før/etter per strekning i rapport/vann/ (bildene ikke i git) og avvik.json

Tegnes i src/03_bakke-vann-grønt.js: naturlig kant skyller inn med skum, kai og mur står rett og rolig. Regel 16 måler.

## Bryggene mot ortofoto 2024 (27.10)
Fergeleiet (Gamlebyen og Sentrum), gjestebrygga i Toldbodgaten, Isegran og båtplassene langs Glomma. OSM gir strukturen (omriss, flytende eller fast); ortofotoet avgjør om brygga finnes og hvor. Det OSM mangler, er målt for hånd i fotoet (kilder/brygger-maalt.json, med grunn), og «sett» der er lista over bryggene som synes i fotoet, som regel 18 teller mot. Faste id-er (br-) med ankerpunkt (kilder/brygger-anker.json) som vannflatene. Typer: fast (på stolper, ca. 1 m over vannet), flytebrygge (ca. 0,4 m), utrigger (smal bom).

    python3 verktoy/brygger.py hent     OSM over kartrammen (kilder/brygger-osm.json)
    python3 verktoy/brygger.py maal     data/brygger.json (utriggerne i en «rad» flyttes til der fotoet viser bommene)
    python3 verktoy/brygger.py ark      kontrollark før/etter per område i rapport/brygger/ (bildene med ortofoto ligger bare lokalt)

Tegnes i src/18_brygger.js. Regel 18 måler dekning, at ingen brygge står på land (data/vann.json), og at fotoet viser brygge under hver av dem.

## Grå hus: fargene i tegningen som vektor (28.10, forsøk, ikke lagt inn)
132 hus i Gamlebyen står hvite/grå; 48 av dem er dømt riktige mot 2019-trykket (hvite hus), 39 har fått trykkets farge, og 43 mangler dom
(20 var skjult av trær/tekst i trykket, 23 står utenfor det dømte arket). 165 hus utenfor vollene har ingen farge i noen tegning.
Gamlebyen+Isegran2017.ai (Dropbox, Gamlebyen kart tegning) er samme artwork som 2019-trykket og har lagene i behold, så husflatene kan
leses som vektor uten trær (verktoy/farger_tegning.py, kilder/ai bare lokalt). Registreringen tegning→trykk er på 1,4 px, men
modell→trykk (fra px2019 i rapport/farger2019.json) er på 5–25 px, og husene er tegnet fritt, så fotavtrykket treffer ofte nabohus,
gate eller tre. Forslagene i rapport/farger-tegning/forslag.json er derfor ikke lagt inn. Veien videre er den samme som for v30:
kontrollark per hus der Vegar dømmer, eller Street View-runde som i 2015.

## Grunnmuren fra kommunekartet (29.10)
Fasit for husomrissene i Gamlebyen er kommunens oppmålte omriss (FKB), lest som vektor fra kommunekartet Vegar lastet ned fra kartportalen
(kilder/kommunekart/kommunekart.pdf, bare lokalt; transformasjonen til modellmeter i pdf_til_modell.json). Kommunekartet brukes som mål for vår
egen modellering, ikke vist i kartet. Alt legges inn som rettelser med grunn som begynner med «kommunekart FKB 29.10».

    python3 verktoy/grunnmur.py            omriss, tak, nye bygg, matrikkelfelt, piper/arker, tegnede vinduer flyttet (idempotent)
    python3 -I rapport/hoyder/hent.py      høydene måles på nytt på de nye omrissene (forskyvningen står fast fra tall.json)
    python3 -I rapport/hoyder/legg_inn.py
    python3 verktoy/grunnmur.py            andre gang: nye bygg får første høydegjetning, alt annet er likt
    python3 verktoy/vinduer_regler.py      vinduer på antatte hus etter de nye veggene og naboene
    python3 verktoy/grunnmur.py ark        kontrollark rapport/grunnmur/oversikt.png (ikke i git); plan og tall i rapport/grunnmur/plan.json

Per hus i Gamlebyen (verktoy/kommunekart.py: i_gamlebyen; bare hus helt innenfor kartrammen):
- én-til-én: `sett p` (og ph, r, rf, tk); id, farger og vinduer følger huset.
- ett modellhus over flere kommunehus: delen der husets matrikkelpunkt står, beholder id-en; resten blir nye bygg (`ny`). Tegnede vinduer
  som står på en utskilt del, følger med dit (delen får `fasade_kilde: kvartaltegning` og `fasade_fra`).
- flere modellhus i ett kommunehus: kommunens omriss deles mellom dem (nærmeste modellhus), så alle id-er beholdes.
- kommunehus uten modellhus: står et skjult modellhus der, vises det igjen med kommunens omriss (alle 9 skjult 23.10 etter Google-flyfotoet
  står i kommunekartet og i ortofotoet); ellers nytt bygg med `bnr-` fra et matrikkelpunkt som hører til omrisset, eller neste `pb-`.
  Under 6 m² hoppes over og listes. Nye hus får nøytral farge (vegg 226/222/212, tak 150/144/138) til Vegar velger.
- modellhus uten kommunehus slettes aldri; skjules bare når Kartverkets DOM−DTM ikke har noe over 1 m og huset ikke har navn.
- røres ikke: kirka, Kaserna, portbyggene. Flater i PDF-en som ligger inni en større flate er bygningsdeler (tas bort), med mindre
  matrikkelen har et eget bygg i dem.
Taket regnes fra fotavtrykket for hver husrekke med et endret hus (verktoy/tak.py, rett skjelett); gavlene arves fra det gamle taket der
veggen står omtrent samme sted, ellers tak.gavl_regel. Regel 20 måler resultatet (IoU >= 0,7 per kommunehus, ingen modellhus over to).
verktoy/matrikkel.py koble jobber på grunndataene; kjør grunnmur.py etterpå, så matrikkelfeltet på de rettede husene følger omrisset.

## Fasadene fra Street View (29.10)
En agent leste fasadene av i Google Street View i Vegars Chrome: kilder/streetview/avlesning.json (77 hus, bare tall og ord; bildene
ligger aldri i repoet). Fargene legges inn av verktoy/streetview_farger.py, fasadene av:

    python3 verktoy/streetview_fasader.py          vinduer per etasje, dører, arker og piper på gatesiden (idempotent; --tørt viser bare)
    python3 verktoy/streetview_fasader.py ark      kontrollark rapport/streetview-fasader/ark.png (endret) og ark-fasit.png (fasithus)

Gatesiden er veggen som vender mot kamerapunktet (viewpoint i pano_url) innenfor heading ± 35°, uten hus i siktlinja. Vinduene står
etter reglene i vinduer_regler.py (akser, brystning, etasje, hjørneklaring), men med antallet fra bildet; dørene der friteksten sier
(venstre/midt/høyre, sett fra kameraet). Huset får `fasade_kilde: streetview` og `fasade_sv` (veggen som er sett), så vinduer_regler.py
lar det være; regel 17 sjekker det med to lettelser som følger av kilden (dør på den sette veggen, overtallige vinduer i en etasje
med flere vinduer enn etasjen under). Fasithusene fra kvartaltegningene endres ikke, bare sammenlignes
(rapport/streetview-fasader/sammenligning.md). Hus der merknaden sier at det er usikkert om det er riktig hus, står med grunn i
kilder/streetview/hopp.json. Har gateveggen ikke plass til tallene, hoppes huset over og listes (trolig feil vegg eller feil hus).
Rekkefølge: grunnmur.py → vinduer_regler.py → streetview_fasader.py (kjøres på nytt når omriss eller h endres).

## Oppsett på en ny maskin
Python 3 med opencv-python-headless, numpy, scipy, shapely, pyproj, tifffile og pymupdf (kommunekartet); Node 22 og `npm install` (ESLint til regel 08); Playwright med Chromium til nettlesertestene.

## Regler som må være grønne før publisering
01–04 innhold mot kildene (02: Kartverket er fasit for høyde, tegningene for fasade – Vegar 28.10), 05 én tegnekvalitet, 06 bygger og laster, 07 ingen JS-feil i bruk (interaksjonstesten), 08 ESLint på den sammensatte modulen, 09 publisert versjon = VERSJON (Pages og artefaktbygget), 10 ytelsestrinn 2 tegner likt som trinn 0 (mobil, nærbilde), 19 skyggekartet dekker bildet og tegnes ikke på nytt under dra. `PYTHONPATH=regler python3 regler/kjor.py` (kjører fra hvilken som helst mappe; 07 og 08 gikk bare fra prosjektmappa før 23.10).

## Agenter: brief og mottakskontroll (23.10)
Vegar: «jeg liker ikke at du ikke merker noe agenter glipper.» Derfor:
- Briefen sier hvilken kilde som er fasit, hva som ikke skal røres (src/, data/), og hvilket bevis som skal leveres: kontrollark (bilde), tall (antall, dekning, sikkerhet), og verktøyet som lagde det (så kjøringen kan gjentas).
- Mottakskontroll før noe legges fram eller bygges videre på, gjort av hovedtråden, ikke agenten selv:
  1. Mot briefen: brukte agenten kilden den fikk? (23.10: fargeagenten leste det isometriske trykket der husene er tegnet fritt; Vegar måtte peke på 2019-JPG-en.)
  2. Mot kilden: minst tre stikkprøver hovedtråden gjør selv (åpne bildet, slå opp tallet, kjøre kallet).
  3. Mot beviset: kontrollarket ses på, tallene i rapporten stemmer med fila, `git status` viser at bare rapport/ er rørt.
  4. Avvik agenten selv flagger («usikkert», «ikke verifisert») gjentas til Vegar, de forsvinner ikke i oppsummeringen.
- Det samme for egen publisering: regel 09 henter Pages og sjekker versjonen. (23.10: publiser.sh stoppet stille, Pages stod på v27 hele kvelden.)

## GitHub
Repo: github.com/PageBlack-official/fredrikstad-fortress-town. main = kilden, gh-pages = server-bygget (publiser.sh). Pages: pageblack-official.github.io/fredrikstad-fortress-town
