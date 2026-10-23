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

## Status 23.10.2026 (v26)
Motor: MapLibre GL JS 6.14.0 (kamera, gester, koordinater). Byen: three.js 0.160 som custom layer. Koden er filer i rekkefølge i ett modulskop (ikke ekte ES-moduler ennå).
Neste: kvalitetssikring kvartal for kvartal (bevisark tegning mot modell), deretter regel 02–04 grønne.
