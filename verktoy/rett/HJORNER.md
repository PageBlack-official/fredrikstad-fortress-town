# Hjørnelesing (07.11): fire hjørner av én fasade i et Street View-bilde

Hvert bilde (1280 × 720) har et rutenett: magenta loddrette linjer hver 0,05 av bredden (tall hver 0,1), blå vannrette linjer
hver 0,05 av høyden (tall hver 0,1). Bruk rutenettet til å lese posisjoner med tre desimaler.

Huset du skal lese er det som står **midt i bildet** (adressen står i lista). Fasaden er veggen som vender mot kameraet.

For hvert bilde: finn de fire hjørnene av denne fasaden:
- `bv` = bunn venstre: der fasadens venstre kant møter bakken/fortauet
- `tv` = topp venstre: der fasadens venstre kant møter takfoten (undersiden av taket / takrenna), IKKE mønet
- `bh` = bunn høyre, `th` = topp høyre: det samme på høyre side

«Kant» er husets hjørne, eller der nabohusets fasade begynner (annen farge, annen kledning, en loddrett fuge/nedløpsrør mellom husene).
Hvert punkt er `[u, v]`: u = vannrett andel (0 venstre, 1 høyre), v = loddrett andel (0 øverst, 1 nederst). Tre desimaler.

Hvis en kant ligger utenfor bildet: gi punktet der fasaden går ut av bildekanten (u = 0.000 eller 1.000, v der takfoten / bakken
krysser kanten), og skriv `"utenfor": ["venstre"]` (eller "hoyre"). Hvis bakken er skjult (bil, busk): anslå der veggen møter bakken
ut fra sokkel og naboer, og skriv det i `merknad`. Ikke les huset hvis det ikke synes (`"synlig": false, "grunn": "..."`).

Levering: ÉN JSON-liste til fila du får oppgitt, med Write-verktøyet, i samme rekkefølge som lista:
`{"bilde": "...", "synlig": true, "bv": [u,v], "tv": [u,v], "bh": [u,v], "th": [u,v], "utenfor": [], "merknad": "..."}`
Svar til slutt med én linje: antall lest, antall ikke synlig.

## Tillegg for de nye bildene (rute2, 07.11 kveld)
Bildene er tatt fra lengre hold så hele fasaden og takfoten skal være med. Hvilket hus: lista har `anslag_u_venstre` og
`anslag_u_hoyre`, der kartet venter at fasadens ender står (kan bomme ±0,05 fordi Googles posisjon kan være feil), og fasadens
lengde og takfothøyde i meter. Les fasaden som står mellom de anslåtte endene; endene skal stå ved husets hjørner eller der nabohuset
begynner. Passer ikke anslaget med noe hus (for eksempel at fasaden står bak en mur eller et annet hus), skriv `"synlig": false`.
