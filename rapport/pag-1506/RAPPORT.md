# PAG-1506 — OPPGAVE5 Del 2 (Studio): Hotell Kasernen-versjon av kartet

Gren: `gate/innhold` · arbeidsmappe `~/sot-maskin/gate-innhold` · ikke publisert (Vegars port).

## Hva som er gjort

Alt styres av `data/partnere.json` (bygg_id, navn, farge). Et annet hotell får sin
egen versjon ved å legge til en partner — ingen kodeendring.

1. **Navnet rettet.** `data/partnere.json`: «Hotel Kasernen» → «Hotell Kasernen».
   (Stedet `pb-hotellkasernen` i `data/steder.json` het allerede riktig.)

2. **Åpner på hotellet, tydelig merket.** `src/30_gjest.js`: når introen er ferdig,
   sentreres kartet på bygget (bnr-193867537), og et eget merke blir stående på det:
   aksentfarget nål med hus-tegn, navnet og «åpner 2027». **Ingen logo eller profil**
   (den eies av andre), og «åpner 2027» + stedstypen «Hotell (under ombygging)» gjør at
   bygget ikke utgir seg for å være åpent nå. Merket står igjen mens du utforsker.

3. **Gangtid langs gatene.** Ny modul `src/gange.js`: bygger et gå-nettverk av
   `data/veier.json` (hvert gatepunkt en node, delte kryss slått sammen), kjører én
   Dijkstra fra hotellet og snapper hvert sted til nærmeste gate. Gir meter → minutter
   ved rolig gange (5 km/t). Regnes langs gatene, ikke i luftlinje — derfor får
   kafeene på andre siden av elva ærlige 37–52 min (du må rundt via brua), mens
   nabostedene får 2–4 min. Bygges først når noen spør (lat), så vanlig kart betaler
   ingenting. Bakgrunn: Skrivers funn «Kasernen Hotelldrift AS, Kasernegaten 47» er
   ikke vist noe sted — kun brukt for å bekrefte bygget.

   Gangtiden vises:
   - **I kortet** for hvert sted: «3 min å gå fra Hotell Kasernen» (`src/24_sok.js`).
   - **I trefflista** i Finn: «Balaklava · Restaurant · 3 min å gå».
   - **På turene**: «Vandringen i Gamlebyen … starten 2 min unna» (`src/26_turer.js`).
   - Ikke på hotellets eget bygg (du er der).

4. **Vanlig kart uendret.** Alt nytt er bak `?gjest=`-porten (`GANGE.aktiv`,
   `.gjest`-klassen). Uten `?gjest=` er kartet bit-for-bit som før — se skjermkortene.

## Skjermkort (PW_GPU=1, ekte skjermkort)

| | Mobil (390×844) | PC (1100×750) |
|---|---|---|
| Uten `?gjest=` (uendret) | `mob-uten.png` | `pc-uten.png` |
| Åpning, hotellet merket | `mob-gjest-aapning.png` | `pc-gjest-aapning.png` |
| Finn: gangtid i liste + turer | `mob-gjest-finn.png` | `pc-gjest-finn.png` |
| Kort: «3 min å gå fra Hotell Kasernen» | `mob-gjest-kort.png` | `pc-gjest-kort.png` |

Ingen konsoll- eller sidefeil i noen av de åtte.

## Rørt ikke

/prove, forsiden, kirken, Kaserna, fargeoppgaven, introen. Ikke publisert.

## Merknad om grenen

Grenen hadde fra før uinnsjekket arbeid fra Del 1 (innhold per hus: `datalag.py`,
`src/16_interaksjon.js`, `src/kropp.html`, `publiser.sh`, `regler/49_*`). Det er ikke
mitt, og jeg har latt det stå urørt. Mine filer: `src/gange.js`, `src/30_gjest.js`,
`src/24_sok.js`, `src/26_turer.js`, `src/main.js`, `src/stil.css`, `data/partnere.json`.
Innsjekk/publisering er CEOs/Vegars kall.
