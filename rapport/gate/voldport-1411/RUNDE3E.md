# Runde 3e — speilvendt fasade (Fable 14.11 21:10, etter motor-runden)

montasje-73-majoren-3d.jpg: renderen er SPEILVENDT mot Street View. SV fra venstre: bredt vindu, inngang med trapp, stort butikkvindu, flatt portrom helt til høyre. Render fra venstre: port, butikkvindu, dør, lite vindu. Altså s-aksen i lesingen går motsatt vei av veggens s i modellen.
1. Finn årsaken i kjeden (rett.py/konverter.py/fasade_rett: retning på s vs veggens punktrekkefølge, eller kamera sett innenfra). Rett i koden, ikke ved å speile tallene for hånd. Legg en regel/test som fanger det: et kjent element (porten på Majoren, nedløpsrøret på 75 vegg4) skal stå på samme side i SV og render.
2. Sjekk alle rett-filer fra i dag (75 v4, 75 v5, 944 v7, 622 v2) mot samme feil.
3. Majoren: venstre element er et bredt vindu (ikke lite), 2. etg 4 vinduer + bredt over porten.
4. Montasjene skal tas med gatekameraet FRA SAMME STANDPUNKT OG RETNING som SV-bildet (ikke hjørneperspektiv), så de kan legges side om side. montasje-75-vegg4-3d.jpg er tatt fra en annen vinkel og kan ikke brukes som bevis.
Ferdig = montasjer fra samme standpunkt for alle fire vegger, FUNN-RUNDE3E.md, regel/test, commit. IKKE publiser.

5. 6-vs-8 (FUNN-RUNDE4): finn hvilken vegg av bnr-193867928 som vender mot Voldgaten (normal mot gata, lengde ca. 20,2 m) og hvilken som har 8 vinduer i 2. etg i Street View. Spross 3 + foring skal ligge på de vinduene SV viser som tospeils, på riktig vegg. Avgjør selv fra geometri + SV, ikke spør.
6. 75 veggfarge: sett varm graa [164,155,156] fra 3d-maalingen (vegg4 sol) paa hele huset; motoren er rettet, saa fargen kan settes naa.
