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

## Rettelseslaget (23.10)
Grunndataene i data/ er generert (OSM, trykkfila, kvartaltegningene) og kan lages på nytt. Alt Vegar retter ligger i data/rettelser.json, én linje per rettelse, og legges oppå ved hvert bygg:

    [{"emne":"bygg","i":184,"op":"sett","felt":"vegg","verdi":[214,96,80],"hvem":"Vegar","dato":"2026-10-24","grunn":"trykkfila"},
     {"emne":"bygg","i":391,"op":"skjul","hvem":"Claude","dato":"2026-10-23","grunn":"flyfoto: parkeringsplass"}]

Operasjoner: sett (felt = verdi) og skjul. Flytting og nye objekter kommer med redigeringsmodusen. Rettelser slettes aldri, de overstyres av en nyere linje.

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
