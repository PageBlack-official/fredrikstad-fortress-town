# Hvor dataene kommer fra (per felt)

| Emne / felt | Kilde | Merknad |
|---|---|---|
| bygg.p (fotavtrykk) | OpenStreetMap | Ikke FKB. 9 bygg uten bygning i flyfoto er skjult (`skjul`, med grunn). Resten ikke verifisert enkeltvis. |
| bygg.h (høyde) | Kvartaltegningene via `tegnet_h` (h = tegnet_h/1,72) der de finnes; ellers OSM | 18 hus står med OSM-rundetall 3,0/6,0 m |
| bygg.vegg / tak (farge) | Trykkfila 2015 (kartbrosjyren), 128 rettet manuelt | Godkjente fasadefarger per bygg (Vegar 2015) |
| bygg.vind (vinduer/dører) | Kvartaltegningene (strektegninger/Kvartal*.ai) for 97 hus (`fasade_kilde: kvartaltegning`); generisk rutenett for 170 (`antatt`) | Må kvalitetssikres kvartal for kvartal |
| bygg.navn / nr / tekst | Tegnforklaringen i kartbrosjyren 2015 (1–46), norsk | Engelsk/tysk finnes i PDF-en, ikke lagt inn |
| bygg.tak2 / gavl2 / sk (takform) | Beregnet (rett skjelett) fra fotavtrykket | |
| bygg.deler (rådhustårn) | Trykkfila | |
| veier, vann, gront, hull | OpenStreetMap | |
| traer | Trykkfila (kroneposisjoner) | |
| legende | Kartbrosjyren 2015 | |
| landskap.terreng (voller) | Beregnet fra OSM-voller + brosjyren | |
| porter | Regel: bygg med «port» i navnet + vei gjennom fotavtrykket | |
| broer | Regel: gang-/sykkelnett som krysser vann, land til land, 5–35 m | Vindebroen = nærmest legendepunkt 26 |
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
