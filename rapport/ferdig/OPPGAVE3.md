# Oppgave: tegn alle 28 husene ferdig, Vegar dømmer etter 26 (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet `~/sot-maskin/gate` (gren `gate/kamera`). Skriv alt på norsk. Hovedregel: «nesten er ikke lov».
Vegar 09.11: «Be agenten gjøre ferdig alle byggene den har fått oversendt, og la meg ta dommen når den er klar - etter 26 tegnede bygg.»

Lista er de 28 i `kilder/gate/ferdig-kandidater.json`. De 26 er alle unntatt de to ved festningsmuren (bnr-24218023, bnr-193972276). De to skal også prøves, se under.
Les `rapport/ferdig/OPPGAVE.md` (miljø, kommandoer), `rapport/ferdig/OPPGAVE2.md` (hva du gjør med hver gruppe hus), de tre siste delene av `LESMEG.md`, og avvikene i `kilder/ferdig.json`.

## Ikke stopp
Du stopper ikke før `python3 verktoy/rett/ferdig_sjekk.py` gir exit 0. Du spør ikke om lov, ikke om retterunde og ikke om pris. Vegar har bestilt jobben. «Usikker» er ikke en sluttstatus.
Går du tom for kontekst: skriv hvor du er i `rapport/ferdig/RAPPORT3.md`, la oppgaven stå i `in_progress`, og fortsett fra den fila i neste kjøring. Sett aldri oppgaven til done før sjekken er grønn.
Bare Vegar kan si «ferdig». Din sluttstatus per hus er `tegnet` eller `trenger_vegar`, med `"runde": 2`.

## Dette er annerledes enn runde 1 (PAG-1467)
1. **Alle 28 gjøres, også de 6 som ble satt «ferdig».** Kontrollbildene deres holdt ikke: modell og Street View var ikke tatt fra samme sted. Det er sett på bildene.
2. **Kontrollbildet først.** Før du dømmer noe skal huset stå på samme sted i Street View og i modellen, med samme kamera. Kalibrer standpunkt og retning per bilde: finn avviket (Googles posisjon kan ligge 3–5 m feil, runde 1 fant ~10° i retning) ved å legge husets hjørner oppå hverandre. Å sikte mot sentroiden er ikke nok: da viser de to bildene ikke det samme.
3. **Kildene i denne rekkefølgen.** Plassering og omriss: kommunekartet. Høyde: Kartverket. Tak: flyfotoet 2024. Vinduer, dører og farge: Vegars tegninger (`kilder/kvartal-ai`, `kilder/fasade-kobling.json`, `verktoy/fasade_tegning.py`) der tegningen har huset. Street View kontrollerer, og teller bare for det som er endret etter 2015, eller der tegningen ikke har huset. Da leses fasaden i meter etter metoden i LESMEG. Ikke la en lesing av et bilde overstyre tegningen uten at bildet viser en endring.
4. **Du retter.** Runde 1 rettet ingen hus. Rett i kjeden (verktøyene i `verktoy/`), ikke for hånd i data, og bygg regler, ikke unntak for ett hus.

Festningsmuren: se OPPGAVE2. Finnes huset, tegn det. Kan ikke kildene si det: `trenger_vegar` med spørsmål, hva du har prøvd, og bilde. Slett aldri hus.

## Når alt er tegnet
1. Kjeden, `python3 bygg.py enkel`, og nytt `rapport/ferdig/<id>.jpg` for hvert hus: Street View | før | etter, samme kamera. Se på hvert bilde. Nabohusene skal ikke ha endret seg.
2. `kilder/ferdig.json` oppdatert. `ferdig_sjekk.py` gir exit 0.
3. Commit (norsk melding, slutter med «Co-Authored-By: Claude <noreply@anthropic.com>»), aldri Google-bilder i git. Regler etter commit: `PYTHONPATH=regler python3 regler/kjor.py` (nohup, ~35 min). Regel 03 er kjent rød; annet rødt rettes. Commit regelrapporten.
4. `sh publiser.sh prove1`. Vanlig push, aldri force.
5. Kontaktark med alle 28 (samme tre bilder per hus, adresse under) til Dropbox: `.../20 Paperclip/outputs/teknisk-veikart/status/sot-dom-28.jpg`, og `rapport/ferdig/RAPPORT3.md` som `status/sot-tegnet-28.md`: hus for hus hva som er endret og fra hvilken kilde. Finn Dropbox-stien med `ls ~/Library/CloudStorage`. Én pekerlinje øverst i `status/smart-old-town.md`. Vegar dømmer.

## Ikke rør
Kirka og Kaserna. Forsiden. Fargeoppgaven i `rapport/farger/`. Introen. Ikke slett noe, ikke force-push, ikke send noe eksternt.
