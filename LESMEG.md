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

Operasjoner: sett (felt = verdi) og skjul. Flytting og nye objekter kommer med redigeringsmodusen. Rettelser slettes aldri, de overstyres av en nyere linje.

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

## Oppsett på en ny maskin
Python 3 med opencv-python-headless, numpy, shapely og pyproj; Node 22 og `npm install` (ESLint til regel 08); Playwright med Chromium til nettlesertestene.

## Regler som må være grønne før publisering
01–04 innhold mot kildene, 05 én tegnekvalitet, 06 bygger og laster, 07 ingen JS-feil i bruk (interaksjonstesten), 08 ESLint på den sammensatte modulen, 09 publisert versjon = VERSJON (Pages og artefaktbygget), 10 ytelsestrinn 2 tegner likt som trinn 0 (mobil, nærbilde). `PYTHONPATH=regler python3 regler/kjor.py` (kjører fra hvilken som helst mappe; 07 og 08 gikk bare fra prosjektmappa før 23.10).

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
