# Runde 3: les Street View på nytt, med metoden (Vegar 14.11 17:28)

Vegar om runde 2: «Oi. Den leste ikke noe korrekt. Send agenten ned på gaten og få den til å lese street view igjen, og lær av hvordan den i all verden klarte å ta så feil.»

## Del A: hvorfor det ble så feil (skriv FEILANALYSE.md FØR du bygger)
Fables egen del (allerede kjent, ta den med):
1. OPPGAVE.md pkt 3 sa «legg dem inn for hånd etter beskrivelsen over, ikke fra gatekameraet». Det var feil ordre. Fasadene ble bygd fra Fables tekst, ikke fra Street View. Metoden repoet har (LESMEG «Rettede fasader fra Street View (07.–08.11)») ble aldri brukt.
2. Vegars 9 bilder kom aldri til minien (tilgang til ~/Downloads nektet). Ingen i kjeden så bildene ved siden av renderen.
3. Kontrollen var tekst mot tekst: FUNN og Fables lesing dømte renderen mot punktlista, ikke render mot foto side om side. «✓ på karakter» slapp gjennom en jevn rytme som ikke finnes.
Din del: finn resten selv i dataene (hvilke tall i merknadene kom fra hvor, hva som var gjettet, hva regel 17 og vinduer_regler.py overstyrte). Konklusjon som regel(er) i LESMEG.md samme dag, under en ny overskrift «Voldportgaten 14.11: bygd fra tekst, ikke fra bildet».

## Del B: les gata på nytt med rektifiseringen
Hus: 75 (bnr-193867928, begge gatevegger: Voldportgaten og Voldgaten), 73 Majoren (bnr-193868622), 71 Therese M (bnr-193868258). Andre hus røres ikke.
1. Forkast fasade-merknadene fra runde 1 og 2 for disse tre (vinduer/dører/butikk/veggfelt/spross). Behold: husdelingen tatt ut (pb-66 skjult), høydene 75 > 73 > 71, takformene, Majorens møne langs gata. Dømmes på nytt i del C.
2. `verktoy/sv_rett_plan.py bnr-193867928 bnr-193868622 bnr-193868258` → `node verktoy/sv_hent.mjs` (Street View mai 2024, flere panoramaer per vegg, rett forfra der det går) → `vegg_for_skudd.py` + `anslag_u.py` → hjørner etter HJORNER.md → `rett.py` → hvert vindu, hver dør, port, butikkvindu og bånd lest i METER etter ELEMENTER.md → `overlegg.py` (kontaktark) → øyekontroll → `konverter.py` → `kilder/gate/rett-voldport-1411.json` → `bygg_kjede.py` (fasade_rett.py sist).
3. Farge per vegg fra Street View 2016+ (FARGER.md-ordene), målt i bildet, ikke valgt.
4. Det modellen ikke kan uttrykke (75s skråinngang bare i 1. etg, utkraget tak), står i FUNN som «kan ikke», ikke som erstatning.

## Del C: kontroll mot bildet, ikke mot lista
For hver vegg: montasje Street View | render fra samme standpunkt, samme bildeforhold (1280×720), lagt side om side i rapport/gate/voldport-1411/r3/. Tell element for element: antall vinduer per etasje, dører, port, butikkvinduer, posisjon i meter fra hjørnet (±0,3 m). Avvik = rett, ikke forklar. `verktoy/rett/ferdig_sjekk.py` exit 0.
Ferdig = r3/-montasjer + KONTAKTARK + FUNN-RUNDE3.md (tabell per vegg: SV-tall | modell-tall) + FEILANALYSE.md + LESMEG-regel, regler grønne, commit på gate/voldport-1411. IKKE publiser. Fable leser montasjene før noe meldes til Vegar.
