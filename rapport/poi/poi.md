# POI-datagrunnlag Gamlebyen (hentet 24.10.2026)

Filer: `steder.json` (data), `kontrollark.png` (bevis på flyfoto, utsnittet med bilde), `hent.py` (henter alt på nytt, `python3 hent.py`).

## Koordinater
Modellens origo lon 10.952745, lat 59.202835. Web Mercator (R=6378137): mx = R·lon_rad, my = R·ln(tan(π/4+lat_rad/2)). x = (mx−mx0)·cos(lat0), y = (my−my0)·cos(lat0). cos(lat0) er mercator-skalaen ved origo, så 1 enhet = 1 meter på bakken ved origo (x øst, y nord). Kontrollarket bruker flyfotoets transform fra `kilder/flyfoto-google-2026-10-23.json`.

## Tall per type (steder.json)
| type | antall | merknad |
|---|---|---|
| parkering | 224 | 191 plasser (lag 1) + 33 automater (lag 0), alt innen Gamlebyen-boksen + 500 m. Bare ca. 49 ligger innenfor kartets kjerne (|x|<350, |y|<450 m); filtrer på avstand i kartet |
| ferje | 5 | Gamlebyen fergeleie (stoppested + 2 quayer, linje 803 og 805), pluss Vaterland fergeleie (stoppested + quay, uten linjer i Entur-svaret) |
| buss | 7 | Gamlebyen (63038, quay 108763), Kongsten (stoppested + 2 quayer), Vaterland (stoppested + quay). Gamlebyen-stoppet har ingen linjer knyttet til seg i Entur (tom liste), Kongsten har 101, 113, 123, 186, 8 |
| restaurant | 16 | OSM: restaurant, cafe, pub |
| overnatting | 4 | OSM: hotel, guest_house (to av dem ligger 600–700 m unna, nordvest) |
| museum | 4 | OSM |
| toalett | 8 | OSM, alle uten navn |
| annet | 0 | |

## Kilder og lisens
- Fredrikstad kommune ArcGIS TekniskDrift/Parkering lag 0 og 1: **lisens er ikke oppgitt i tjenesten.** data.norge.no oppgir «ingen vilkår» (publisert 2018), men det er ikke en lisens. Bekreft med kart@fredrikstad.kommune.no før publisering. Felt: ANTALL, PRIS, ELBIL, KOMMENTAR, EASYPARK, TYPE, AUTOMATNR, LENKE. PRIS, ELBIL, TYPE og EASYPARK er koder, ikke kroner/tekst; kodeforklaring ikke hentet (se usikkerhet).
- Entur Journey Planner v3 / NSR: NLOD. Header `ET-Client-Name: pageblack-smartoldtown`.
- OpenStreetMap via Overpass: ODbL 1.0, krever attribusjon «© OpenStreetMap-bidragsytere».

## Hva feilet
- overpass-api.de (tilkobling nullstilt) og overpass.kumi.systems (tidsavbrudd) fra skallet. overpass.private.coffee ga ingen forbindelse. Speilet maps.mail.ru svarte på tredje forsøk; skriptet prøver alle fire i tre runder. Overpass-speil er upålitelige, så kjør hent.py på nytt hvis OSM-tallene blir 0 (feil logges i `hent.logg.json`).
- Ingenting annet feilet.

## Stikkprøver mot flyfotoet
1. Fergeleiet (sp2448, quay 4259/4260) ligger på og ved Gamlebyen brygge, ved vannet, rett ved Google-etiketten «Gamlebyen brygge» og ferjelinja «Gressvik–Gamlebyen». Bussholdeplassen Gamlebyen (63038/108763) ligger ved kaikanten litt sør for den.
2. Parkering: P1-4606/4607 (Laboratoriegaten, 30 plasser) og P1-15942 ligger på parkeringsflatene sør i Gamlebyen ved Laboratoriegaten, og P1-4605/P0-147 ved Kirkegaten/Tøihusgaten. Voldgaten-punktene ligger langs veien ved vollen. Sentrale parkeringspunkter treffer parkeringsareal eller gate, ikke bygg eller vann.
3. OSM: toalettet n2393456192 treffer Google-ikonet «Public toilet» ved Bastion 5; museet n6591537397 (Bastion 5) stemmer med Googles ikoner; Pepo's (restaurant) ligger ved Googles «Pepos Restaurant». Café Magenta, som står i flyfotoet, finnes ikke i OSM-uttrekket (mulig hull); Modelljernbanesenteret (n6591537391) ligger på Google-ikonet.

## Usikkerhet
- Parkeringspunktene er punkter fra kommunen, ikke polygoner; noen ligger i gatesenter og ikke på selve plassen. Meterfeil ca. 5–15 m.
- Flere kommunale punkter ligger tett på hverandre (P1-4599, 4602 osv. er soner/linjer representert som punkt). Dobbel representasjon mellom lag 0 (automat) og lag 1 er ikke slått sammen.
- Kodene PRIS/ELBIL/TYPE er ikke oversatt; hent kodeliste fra lagets domener (`MapServer/1?f=json`, felt-domener) før de vises.
- Ingen sanntid for ledige plasser. Entur oppgir fergen som mode BUS; ferje avgjøres her på stoppested/linje 803/805.
- Flyfotoet er en sammensetning med sømmer; punkter nær sømmen (midt på arket) kan ha opptil noen meter ekstra feil.
- OSM-listen er ikke verifisert mot kommersielt register (kan mangle nyåpnede steder eller ha nedlagte).
