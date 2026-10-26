# Hvor dataene kommer fra (per felt)

| Emne / felt | Kilde | Merknad |
|---|---|---|
| bygg.p (fotavtrykk) | OpenStreetMap | Ikke FKB. 9 bygg uten bygning i flyfoto er skjult (`skjul`, med grunn). Resten ikke verifisert enkeltvis. |
| bygg.h (høyde) | Kvartaltegningene via `tegnet_h` (h = tegnet_h/1,72) der de finnes; ellers OSM | 18 hus står med OSM-rundetall 3,0/6,0 m |
| bygg.vegg / tak (farge) | Trykkfila 2015 (kartbrosjyren), 128 rettet manuelt | Godkjente fasadefarger per bygg (Vegar 2015) |
| bygg.vind (vinduer/dører) | Kvartaltegningene (strektegninger/Kvartal*.ai) for 97 hus (`fasade_kilde: kvartaltegning`) + 25 lest på ny i v33 (rettelser); de 142 andre (`antatt`) har vinduer og dører etter reglene målt på tegningene (verktoy/vinduer_regler.py, rapport/vinduer/regler-fra-tegningene.md, rettelser med grunn «regler fra kvartaltegningene (27.10)») | De antatte er regler, ikke tegning: må fortsatt kvalitetssikres kvartal for kvartal |
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

Modellkoordinater: meter, x = øst, y = nord, origo ca. 59,202835 N 10,952745 Ø (utledet 23.10 fra kirka og statuen, ±3 m).
