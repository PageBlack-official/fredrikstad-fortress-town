# Hvor dataene kommer fra (per felt)

| Emne / felt | Kilde | Merknad |
|---|---|---|
| bygg.p (fotavtrykk) | Gamlebyen: kommunens oppmålte omriss (FKB) fra kommunekartet (kilder/kommunekart/kommunekart.pdf, Vegars nedlasting 29.10, bare lokalt), lagt inn som rettelser av verktoy/grunnmur.py; ellers OpenStreetMap | Kirka, Kaserna, portbyggene og hus utenfor/kuttet av kartrammen står med OSM-omriss. De 9 som var skjult etter flyfotoet 23.10, står i kommunekartet og vises igjen |
| bygg (nye, op ny) | Kommunekartet (FKB-omriss), id fra Matrikkelens bygningspunkt der det finnes | Høyde fra Kartverket der målingen er sikker, ellers første gjetning (DOM−DTM p50 − 1 m); nøytral farge til Vegar velger |
| bygg.h / th (vegghøyde, takhelning) | Kartverket DOM−DTM 1 m (rapport/hoyder), lagt inn som rettelser 24.10 for 197 hus med sikker måling; fasit for høyde fra 28.10 (Vegar). De 78 uten sikker måling står med tegning (`tegnet_h`/1,72) eller OSM til kvartal-QA | Tegningene viser høyde fra tegnevinkelen, ikke målt vegg; de er fasit for fasade, ikke høyde |
| bygg.vegg / tak (farge) | Trykkfila 2015 (kartbrosjyren), 128 rettet manuelt | Godkjente fasadefarger per bygg (Vegar 2015) |
| bygg.vind (vinduer/dører) | Kvartaltegningene (strektegninger/Kvartal*.ai) for 97 hus (`fasade_kilde: kvartaltegning`) + 25 lest på ny i v33 (rettelser); de 142 andre (`antatt`) har vinduer og dører etter reglene målt på tegningene (verktoy/vinduer_regler.py, rapport/vinduer/regler-fra-tegningene.md, rettelser med grunn «regler fra kvartaltegningene (27.10)») | De antatte er regler, ikke tegning: må fortsatt kvalitetssikres kvartal for kvartal |
| bygg.navn / nr / tekst | Tegnforklaringen i kartbrosjyren 2015 (1–46), norsk | Engelsk/tysk finnes i PDF-en, ikke lagt inn |
| bygg.tak2 / gavl2 / sk (takform) | Beregnet (rett skjelett) fra fotavtrykket | Gamlebyen fra 29.10: verktoy/tak.py på kommunens omriss, gavler arvet fra det gamle taket |
| bygg.deler (rådhustårn) | Trykkfila | |
| veier, vann, gront, hull | OpenStreetMap | Plenene i Gamlebyen (3 OSM-flater) er skjult fra 29.10: plenene der tegnes fra ortofotoet (flater) |
| landskap.veier[].w / p / flate (veibåndene) | Gamlebyen: bredde og midte målt mot kommunekartets gateareal (kjørevei) og ortofotoets belagte mark (gangvei), verktoy/bakke.py gater; «maalt» sier hva som gjelder per vei | Flate = flertallstypen under båndet; brostein tegnes med brosteinen (src/08) |
| flater (typ gress/bed/grus/asfalt/brostein, kilde «ortofoto 2024 klassifisert …») | Ortofoto 2024 klassifisert per piksel (grønt, bar jord, belagt; belagt delt i brostein/asfalt/grus på farge og tekstur), kommunekartets arealtype der fotoet ikke ser (trær, skygge), verktoy/bakke.py overflater | Brostein er grunnen innenfor brosteinsflaten, gress på vollene; flatene er avvikene. Prøvepunkter dømt med øyet i kilder/bakke-maalt.json. Lys belegning kan ikke alltid skilles (brostein/grus) |
| gjerder (typ gjerde/mur/hekk, h) | Ortofoto 2024 (mørk smal stripe / grønn stripe) langs kommunekartets eiendomsgrenser og gårdsrommenes kanter, DOM−DTM for mur mot gjerde og høyde, verktoy/bakke.py gjerder | id gj-<n>. Gjerdene som ikke ses i fotoet, er tatt ut (rapport/bakke/gjerder-forkastet.json) |
| traer (posisjon, s) | Lest fra Google-flyfotoet 23.10 (forskjøvet), rettet 29.10 mot Kartverkets DOM−DTM: koblet til tretopp innen 3 m, ellers flyttet inn i nærmeste vegetasjon innen 12 m, verktoy/bakke.py traer | Antallet (2343) uendret; kronen bare gjort større der DOM-en viser større krone |
| traer (opprinnelig) | Trykkfila (kroneposisjoner), så Google-flyfotoet (23.10) | Se raden over for rettingen 29.10 |
| legende | Kartbrosjyren 2015 | |
| landskap.terreng (voller) | Beregnet fra OSM-voller + brosjyren | |
| porter | Regel: bygg med «port» i navnet + vei gjennom fotavtrykket | |
| broer | Regel: gang-/sykkelnett som krysser vann, land til land, 5–35 m | Vindebroen = nærmest legendepunkt 26 |
| brygger | OpenStreetMap (man_made=pier, ODbL; kilder/brygger-osm.json) sjekket mot ortofoto 2024, og målt for hånd i ortofotoet der OSM mangler (kilder/brygger-maalt.json, verktoy/brygger.py) | Utriggerne nord for Gamlebyen er plassert der fotoet viser bommene; ortofotoet er fra april, så sommerbrygger kan mangle |
| assets/pensel.png | The Intergalactic Liquid & Irregular Brushes (Vegars kjøpte pakke) | |
| assets/ikon-*.png, logo | FortressTown_Gamlebyen_Fredrikstad.ai (Page Black 2016) | Ikonet er C5-monogrammet fra O-en i TOWN |
| kilder/flyfoto-google-2026-10-23 | Google Maps flyfoto, skjermbilder | Bare til kontroll, ikke til visning |
| kilder/ortofoto-2024 | Fredrikstad kommune, Bakgrunnskart/Ortofoto_2024 (ArcGIS export, EPSG:3857, 0,125 m/piksel) | Fasit for bakkeflatene. Lisens ikke avklart: bare til kontroll, aldri vist i kartet, flisene ligger ikke i git (`python3 verktoy/flater.py hent`). Transformen står i ortofoto-2024.json |
| gront.id, gardsrom.id | Faste id-er (gr-/ga-<løpenummer>, verktoy/flater.py id), i kilder/id-register.txt | Rettelser peker på dem |
| gardsrom.gress, gardsrom.typ | Målt i ortofoto 2024 (grønt i det åpne gårdsrommet, verktoy/flater.py maal), som rettelser | Trekroner over belagt mark kan telle som gress |
| gront.p (klippet) | Rettelse: grøntflate minus parkering/belagt målt i ortofotoet | gr-3 ved Kongstenhallen |
| parkering | Fredrikstad kommune, TekniskDrift/Parkering lag 1 (plasser: navn, antall, pris, elbil, automat), kilder/parkering-kommunen.json; flaten målt i ortofoto 2024 (kilder/flater-maalt.json) | id = parkering-1-<OBJECTID>, kommunens nøkkel. Lisens ikke oppgitt (data.norge.no: «ingen vilkår») |
| flater (grus, heller, asfalt) | Målt for hånd i ortofoto 2024 (kilder/flater-maalt.json), id fl-<løpenummer> | ±2 m |

Modellkoordinater: meter, x = øst, y = nord, origo ca. 59,202835 N 10,952745 Ø (utledet 23.10 fra kirka og statuen, ±3 m).
