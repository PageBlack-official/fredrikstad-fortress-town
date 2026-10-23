# Åpne data for Gamlebyen-kartet — vurdering av Heggelund-tipset

Dato: 23.10.2026. Research, ingenting bygget. Alle API-kall under er testet fra kommandolinje med `Origin`-header for å se CORS-svaret; «CORS ok» betyr at serveren svarte med `access-control-allow-origin` som en GitHub Pages-side kan bruke.

## 1. Hva siden er

- Adresse: https://test.offentligdata.com/ (lnkd.in/daBrKnBE peker dit). Tittel «OSINT DASHBOARD». Ingen om-side, ingen kildeliste, ingen robots.txt. Ingen offentlig GitHub-repo funnet (GitHub-søk er sperret fra denne sesjonen, så det er ikke endelig). Heggelunds LinkedIn: https://no.linkedin.com/in/sysfrog
- Teknologi (lest ut av `osint-map.bundle.js` og `layers/config.js`):
  - MapLibre GL JS 5.24 (ikke Cesium lenger; koden har rester av Cesium).
  - Grunnkart: OpenFreeMap (OSM-vektorfliser, gratis, ingen nøkkel) — https://tiles.openfreemap.org/planet
  - Terreng: Mapterhorn (gratis terrengfliser, terrarium-koding, Norge landsdekkende 1 m) — https://tiles.mapterhorn.com/{z}/{x}/{y}.webp
  - 3D-bygg: `fill-extrusion` på OSM-omriss fra OpenFreeMap (`render_height`, ellers 8 m). For Oslo sentrum har han et ekstra, forhåndsberegnet datasett (`/static/data/oslo-buildings.json`, 139 000 bygg): **omriss fra OSM, høyde = median(DOM1 − DTM1) per omriss fra Kartverkets nasjonale høydemodell (CC BY 4.0)**. Dekodes i en Web Worker. Det er den eneste Kartverket-bruken i kartet («Kartverket (Oslo heights)» i attribusjonen).
  - Trær: statiske GeoJSON-filer per by (Oslo, Bergen, Trondheim, ca. 5 MB hver) der hvert tre er stablede polygoner (stamme + 2–3 kronelag) ekstrudert i MapLibre. Trolig avledet fra DOM/DTM-differansen (overflatemodell minus terreng), ikke fra et treregister.
  - **Siden har backend.** Alle levende lag går via egne endepunkter (`/api/datasource/transit`, `/api/stream`, `/api/news`, `/api/webcams`, `/api/map-search` m.fl.) og via søsterprosjektet hans **allemannsdata.com** (75 MCP-servere / 337 verktøy, «ingen nøkkel kreves»), som er en mellomtjener han drifter foran Kystverket, MET, badetemperatur osv. «No paid API keys» stemmer, «no backend» stemmer ikke.
- Kilder nevnt i koden: Entur (JourneyPlanner v3, NSR, sanntidsposisjoner), BarentsWatch AIS + AISStream + VesselFinder (skip), Kystverket (navigasjonsinstallasjoner via Kystverkets ArcGIS WFS), NVE (HydAPI, damdata), Vegvesen (trafikk, kameraer), Geonorge WMS (støykart), MET, allemannsdata-API for tidevann/havvarsel/badetemp/oppdrett/politilogg.

## 2. Datasett som er relevante for Gamlebyen

| # | Behov | Kilde | Adresse | Nøkkel | Lisens | Format | CORS fra statisk side | Relevans for oss | Status |
|---|---|---|---|---|---|---|---|---|---|
| a | Bussholdeplasser, avganger | Entur JourneyPlanner v3 | `POST https://api.entur.io/journey-planner/v3/graphql` (header `ET-Client-Name: pageblack-smartoldtown`) | Nei | NLOD | GraphQL/JSON | **Ok** (`*`), 2000 kall/2 min | Holdeplass «Gamlebyen» = `NSR:StopPlace:63038` (quay 108763, 59.2048/10.9531). `nearest`-spørring og `estimatedCalls` testet | Klar til bruk |
| a | Bussposisjoner live | Entur Vehicles | `POST https://api.entur.io/realtime/v1/vehicles/graphql` (`codespaceId:"OST"`, `boundingBox`) | Nei | NLOD | GraphQL/JSON | **Ok** (`*`) | 9 kjøretøy i Fredrikstad-boksen i kveld, oppdatert hvert sekund | Klar til bruk |
| b | Byfergen | Entur (samme to API-er) | Stoppested «Gamlebyen fergeleie» `NSR:StopPlace:2448`; linjer 803 «Gamlebyfergen» og 805 «Ålekilen–Sentrum», autoritet Fredrikstad kommune (`OST:Authority:155`) | Nei | NLOD | GraphQL/JSON | **Ok** | **Fergene sender sanntidsposisjon** (`155_elen2` på 803, `155_asta` på 805, lå ved Gamlebyen 18:49). Merk: `mode` rapporteres feil som BUS — filtrer på linje, ikke mode. Rutetabell på fergeleiet gir ikke sanntid (`realtime:false`), men posisjon gjør | Klar til bruk |
| b | Byfergen rute (strek) | Fredrikstad kommune ArcGIS | `…/Temadata/Kollektivtrafikk/MapServer/1` («Byfergen»), `/0` («Stoppesteder») | Nei | Ikke oppgitt, spør kart@fredrikstad.kommune.no | ArcGIS REST → GeoJSON | Ok (server speiler Origin) | Fergelinjene som strek i vannet | Klar, lisens må bekreftes |
| b | AIS (skip i Glomma) | Kystverket Kystdatahuset | `POST https://kystdatahuset.kystverket.no/ws/api/ais/positions/within-bbox-time` | Nei | NLOD | JSON | Ok (`*`) | Historisk (dagstabeller; dagens dato fantes ikke ennå). Ikke live | Begrenset nytte |
| b | AIS live | BarentsWatch | `https://live.ais.barentswatch.no/v1/latest/combined` | Gratis klient-ID (OAuth client credentials) | NLOD | JSON/stream | 401 uten token; hemmeligheten kan ikke ligge i en statisk side | Trengs ikke når Entur gir fergeposisjon | Mellomtjener |
| c | Parkering, plasser og regler | Fredrikstad kommune ArcGIS | `https://arcgis.fredrikstad.kommune.no/server/rest/services/TekniskDrift/Parkering/MapServer/1/query?…&f=geojson` (lag 0 Automat, 1 PPlasser, 2 Parkeringssoner) | Nei | «Ingen vilkår» (data.norge.no), publisert 2018 | GeoJSON | **Ok** | 78 punkter i Gamlebyen-boksen med `NAVN, ANTALL, PRIS, ELBIL, EASYPARK, KOMMENTAR` (Kongsten 122, Tolboden 42, Voldgaten 33, Laboratoriegaten 30 …). Ingen sanntid for ledige plasser | Klar til bruk |
| c | Parkeringsregisteret | Statens vegvesen | `https://parkreg-open.atlas.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringsomraade` | Nei | NLOD | JSON (hele landet, 22 888 rader; filter ignoreres) | **Nei** («Invalid CORS request») | Samme områder som kommunen, med tilbyder (kommunen, APCOA, Park Nordic) | Engangsnedlasting → statisk fil, eller Worker |
| d | FKB vektor (bygg, veikant, murer, gjerder) | Kartverket/Geovekst | Geonorge nedlasting (GML/SOSI/FGDB) | Norge digitalt-part | **Norge digitalt-lisens, ikke åpen** | GML/SOSI | — | Kan ikke publiseres på GitHub Pages | Dødt løp som åpent lag |
| d | FKB som raster | Kartverket WMS | `https://wms.geonorge.no/skwms1/wms.fkb` (lag `bygning`, `veg`, `vegavgrensning`, `bygnanlegglinje` m.fl.) | Nei (svarer uten innlogging) | GetCapabilities sier «Fees: Norge digitalt» | WMS PNG | Ok (`*`) | Presis tegnereferanse under håndtegning. Ikke som synlig lag | Bruk som kalkerpapir |
| d | FKB via kommunen | Fredrikstad kommune ArcGIS | `…/FKB/Samferdsel/MapServer` (sti/gangvei, senterlinje, gatenavn), `…/FKB/Hoydekurver/MapServer/0`, `…/FKB/BygningsmessigeTiltak/MapServer/3` | Nei | Ikke oppgitt — FKB-lisensen følger med | GeoJSON | Ok | Kommunen eksponerer det åpent, men rettigheten er Geovekst sin. Spør kommunen før publisering | Avklar |
| d | Høydedata DTM1/DOM1 | Kartverket | WCS `https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833` (Fees: free), WMS `wms.hoyde-dom-nhm-25833`, nedlasting hoydedata.no | Nei | CC BY 4.0 | WCS GeoTIFF / WMS | Ok (`*`) | Nøyaktig terreng og **trehøyder = DOM − DTM** (Heggelunds metode). Gjøres én gang offline, ikke i nettleseren | Klar for forhåndsberegning |
| d | Terreng i MapLibre | Mapterhorn | `https://tiles.mapterhorn.com/{z}/{x}/{y}.webp` (terrarium) | Nei | Fri, attribusjon kreves | raster-dem | Ok (`*`) | Norge 1 m (bygd på Kartverkets DTM). Rett inn som `setTerrain` | Klar til bruk |
| d | Ortofoto | Kartverket «Norge i bilder» WMS | `wms.geonorge.no/skwms1/wms.nib` | Krever autentisering | Begrenset | WMS | Nei (401-aktig feil) | — | Dødt løp |
| d | Ortofoto via kommunen | Fredrikstad kommune ArcGIS | `…/Bakgrunnskart/Ortofoto_2024/MapServer/export` (også 2019, 2020), `…/Bakgrunnskart/DOM_2015_…/ImageServer` | Nei | Ikke oppgitt | Bilde-eksport | Trolig ok (samme server); ikke verifisert på dette laget | Trær og takform som tegnereferanse | Bruk som referanse, avklar lisens |
| e | Bedrifter på adresse | Brønnøysundregistrene | `https://data.brreg.no/enhetsregisteret/api/underenheter?beliggenhetsadresse.postnummer=1632` | Nei | NLOD | JSON (HAL) | **Ok** (`*`) | 301 underenheter på 1632 Gamle Fredrikstad, med gateadresse og næringskode. Ingen koordinater — må geokodes mot Kartverkets adresse-API (`ws.geonorge.no/adresser/v1`, åpent) | Klar, trenger geokoding |
| e | Steder/kultur | Fredrikstad kommune ArcGIS | `…/Kulturetaten/Skulptur/FeatureServer` (lag: Skulptur, Kulturhistorisk byvandringsløype, Kunstsafari, Inskripsjoner, Kunstvandringer); `…/Temadata/HistoriskeFotografier/FeatureServer` (kommunen + Østfold museum); `…/Temadata/HistoriskeKart/ImageServer` | Nei | Ikke oppgitt | GeoJSON / bilde | Ok | Skulpturer med kunstner og tekst («Sittende pike», Durban), byvandringsløype og historiske foto stedfestet i Gamlebyen | Avklar lisens, så bruk |
| e | Visit Fredrikstad | — | Ikke funnet som API i denne runden | — | — | — | — | Innhold hentes trolig best fra kunden direkte | Ikke undersøkt |
| f | Vær | MET locationforecast 2.0 | `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.2039&lon=10.9513` (krever `User-Agent` med kontakt) | Nei | NLOD/CC BY 4.0 | JSON | **Ok** (`*`) | Liten detalj (sol/regn/vind) | Klar til bruk |
| f | Vannstand | Kartverket se havnivå | `https://vannstand.kartverket.no/tideapi.php?lat=…&lon=…&tide_request=locationdata&datatype=all&refcode=cd` | Nei | CC BY 4.0 | XML | **Ok** (`*`) | Gir Viker-målingen justert for Gamlebyen (observasjon + prognose) | Klar til bruk |
| — | Politiloggen | Politiet | `https://api.politiet.no/politiloggen/v1/messages?Municipalities=Fredrikstad` | Nei (kjent åpent) | — | JSON | Ikke testet: forbindelsen ble brutt fra denne sesjonen | Passer ikke et turistkart | Uaktuelt |

## 3. Hva som går uten backend, hva som trenger mellomtjener, hva som er dødt

**Rett fra GitHub Pages, ingen nøkkel:** Entur (holdeplass, avganger, buss- og fergeposisjon), Fredrikstad kommunes ArcGIS (parkering, fergerute, skulpturer, historiske foto, høydekurver), Brønnøysund (med Kartverkets adresse-API for koordinater), MET, Kartverkets vannstand, Mapterhorn-terreng, Kartverkets høyde-WCS (til forhåndsberegning). Alt dette er testet i kveld og svarte med CORS.

**Liten mellomtjener (Cloudflare Worker, gratis-nivå holder):** Vegvesens parkeringsregister (ingen CORS; men siden det er statiske data, er en engangsnedlasting til en JSON-fil i repoet enklere og mer robust enn en Worker). BarentsWatch AIS (hemmelig klient-ID må skjules) — unødvendig så lenge Entur gir fergeposisjon.

**Dødt løp:** FKB-vektor som publisert lag (Norge digitalt-lisens), Norge i bilder-WMS (autentisering). Unntak: FKB-WMS og kommunens ortofoto fungerer som *tegnereferanse* når Vegar håndtegner — bildet ligger aldri i det publiserte kartet.

**Forhåndsberegnet, én gang, offline (ikke backend):** Heggelunds oppskrift for bygg og trær: last ned DTM1 og DOM1 for Gamlebyen (CC BY 4.0), regn median(DOM − DTM) per bygningsomriss og finn trekroner som DOM-topper over 3 m utenfor bygg. Resultatet er to små GeoJSON-filer som legges i repoet. For ett verna område på under 1 km² er det en kveldsjobb i QGIS/Python, og filene blir noen hundre kB.

## 4. Hva Vegar bør ta med seg, og hva som ikke passer

Det viktigste fra Heggelunds kart er ikke datamengden, men to grep. Det ene er høydemetoden: OSM-omriss pluss Kartverkets DOM/DTM gir målte bygghøyder og faktiske trær, forhåndsberegnet og lagt som statiske filer — ingen server, ingen nøkkel, CC BY-attribusjon. Det er rett vei for Gamlebyen, der vi i dag gjetter høyder. Det andre er at Entur allerede holder Gamlebyfergen og bussene i sanntid på vår holdeplass, gratis og med CORS; et lite punkt som faktisk beveger seg over Glomma gir kartet liv uten at det blir et dashbord. Parkering og skulpturer fra kommunen er samme sort: fakta som står stille og kan tegnes inn én gang.

Det som ikke passer: alt det levende som gjør hans kart til et overvåkingsbord (AIS, fly, GPS-jamming, politilogg, 50 lag med brytere). Gamlebyen er ett lite, verna område, og kartet er håndtegnet — det skal være ett bilde med noen få ting som puster, ikke en datavisning. Hans kart står også på en backend og på allemannsdata.com, som han drifter selv; vi bør ikke lene oss på en privatpersons mellomtjener. Holder vi oss til de kildene som svarte direkte i kveld, trenger vi fortsatt verken server eller nøkkel.

## Kilder

- https://test.offentligdata.com/ (og `/static/js/layers/config.js`, `/static/js/osint-map.bundle.js`, `/static/js/map/oslo-buildings.js`, `/static/data/oslo-buildings.json`)
- https://allemannsdata.com/ · https://allemannsdata.com/wiki/kilder/kystverket/
- https://no.linkedin.com/in/sysfrog
- https://openfreemap.org/ · https://mapterhorn.com/ · https://tiles.mapterhorn.com/tilejson.json
- https://developer.entur.org/pages-journeyplanner-journeyplanner/ · https://developer.entur.org/pages-real-time-vehicle/ · https://developer.entur.org/pages-nsr-nsr/
- https://data.norge.no/en/datasets/2bad10d7-18d2-3b90-94fb-166874e26ed3 (Parkeringsplasser i Fredrikstad) · https://hub-frstadkomm.opendata.arcgis.com/ · https://arcgis.fredrikstad.kommune.no/server/rest/services
- https://data.norge.no/en/datasets/a43ebac8-7b1c-4feb-9832-f77d2fa38b6e/fkb-bygning · https://dokument.geonorge.no/produktark/fkb-bygning/2025-01-07/fkb-bygning.pdf
- https://wms.geonorge.no/skwms1/wms.fkb?service=wms&request=getcapabilities · https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25833?service=wcs&request=getcapabilities
- https://data.brreg.no/enhetsregisteret/api/underenheter?beliggenhetsadresse.postnummer=1632
- https://parkreg-open.atlas.vegvesen.no/ws/no/vegvesen/veg/parkeringsomraade/parkeringsregisteret/v1/parkeringsomraade
- https://api.met.no/weatherapi/locationforecast/2.0/documentation · https://vannstand.kartverket.no/tideapi.php
- https://kystdatahuset.kystverket.no/ws/swagger/index.html · https://www.barentswatch.no/
