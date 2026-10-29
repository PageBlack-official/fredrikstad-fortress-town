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
| veier, vann, gront, hull | OpenStreetMap | |
| traer | Trykkfila (kroneposisjoner) | |
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
| parkering | Fredrikstad kommune, TekniskDrift/Parkering lag 1 (plasser: navn, type, antall, sonekode/EasyPark, automat, kommentar), kilder/parkering-kommunen.json, hentet 29.10 (uendret siden 28.10; men data/parkering.json var bygd 27.10 og hadde Tolboden med 42 plasser, som laget ikke lenger oppgir). Regler og 2026-priser fra kommunens sider (kilder/parkering-regler.json, URL per regel). Flaten målt i ortofoto 2024: kilder/flater-maalt.json (27.10) og kilder/parkering-maalt.json (29.10). Lages av verktoy/parkering.py, regel 21 | id = parkering-1-<OBJECTID>, kommunens nøkkel. Antall bare der ANTALL står i laget, ellers «antall_kilde: ukjent …». EasyPark-kodene er kommunens (feltet EASYPARK); EasyParks eget register er ikke åpent og er ikke kontrollert. NVDB har ingen parkeringsskilt i Gamlebyen (kommunale skilt). Lisens ikke oppgitt (data.norge.no: «ingen vilkår») |
| statue | Frederik II (innskrift FREDERIK II), Wilhelm Rasmussen, bronse, avduket 12.09.1917: Norsk kunstnerleksikon https://nkl.snl.no/Wilhelm_Rasmussen («Fredrik 2, torget, Gamlebyen, Fredrikstad (bronse 1917)»); Fredrikstad kommunes skulpturregister (Kulturetaten/Skulptur lag 0, OBJECTID 4924, med foto); DigitaltMuseum 021018128815 og 021018128816 (Fredrikstad Museum, postkort 1925/1929, avduket 12.09.1917); nb.no NF.W 37173 (Wilse 1931) og FNR 26062/26063 (1969). Plass og retning: ortofoto 2024 (sokkelen ses ovenfra, kantene parallelle med gatenettet 69°; ryggen mot smuget mellom Torvgaten 61 og Infanterikasernen, som i alle fotoene). Mål: forholdstall lest i kommunens frontfoto, målestokk fra personer ved sokkelen (nb.no 1969), kontrollert mot skyggelengden i ortofotoet (ca. 4,7 m i alt). Ingen av fotoene ligger i repoet | Mål ±10 %, plass ±0,5 m, retning ±3°. Kommunens registerpunkt står 6,6 m nord for sokkelen (omtrentlig), ortofotoet går foran. Christian5.ai (Dropbox) er C5-monogrammet (Christian V), ikke en statue. Regel 22 |
| flater (grus, heller, asfalt) | Målt for hånd i ortofoto 2024 (kilder/flater-maalt.json), id fl-<løpenummer> | ±2 m |

Modellkoordinater: meter, x = øst, y = nord, origo ca. 59,202835 N 10,952745 Ø (utledet 23.10 fra kirka og statuen, ±3 m).
