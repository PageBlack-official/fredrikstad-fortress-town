# Regelrapport

Kilde: 7d1fb4d versjon 34 kjørt 2026-10-30 02:18

- OK   01_bygg_finnes  (0 bygg med vegetasjon under seg som ikke er skjult; 1 skjult med grunn)
- OK   02_hoyder_maalt  (212 hus står med Kartverkets målte høyde; 0 avviker; 119 hus uten sikker måling beholder tegning/OSM)
- FEIL 03_fasader_fra_tegning  (97 hus med fasade fra tegning, 170 antatt (må kvalitetssikres kvartal for kvartal))
- OK   04_vinduer_ikke_i_hjorner  (0 vinduer for nær et hjørne)
- OK   05_kvalitet_bare_kamera  (settSkala(skalaStille) uavhengig av bevegelse)
- OK   06_bygger_og_laster  (- bygd enkel -> /home/claude/wt-bygg/ut/enkel/index.html 2585 kB versjon 34)
- OK   07_ingen_feil_i_bruk  (- intro: underveis az -1.20 zoom 0.70 → ferdig az -2.79 zoom 1.00 intro false)
- OK   08_lint  (- ingen feil)
- FEIL 09_publisert  (- Pages: versjon 32 (ønsket 33))
- OK   10_mobiltrinn_tegner_likt  (- kronegrønt trinn 0: 17662 px, trinn 2: 17199 px)
- OK   11_kamera_glir  (- alle animerte flytt bruker glid/glidUt)
- FEIL 12_kontaktskygge  (- 0.1 % av Torvet-bildet er mørkere med kontaktskygge enn uten (krav 0,5–12 %))
- OK   13_deler_staar_paa_topp  (- bygg 230 (Det nye rådhus) del 0: h 21.0, målt topp 20.0, p90 i delen 19.9, kropp p50 10.3 → ok)
- OK   14_id  (485 bygg, 429 med bygningsnummer fra Matrikkelen (269 av 320 i Gamlebyen), 637 id-er i registeret)
- OK   15_flater  (0 avvik, 7 advarsler; 22 plener innenfor ortofotoet målt)
- OK   16_vann  (99.40% av kartets vann er vann i ortofotoet (krav 98.5%), 99.48% av ortofotoets vann er dekket (krav 98.5%); før retting (OSM): 97.02% og 98.89%)
- OK   17_vinduer_rytme  (145 antatte hus og Street View-hus, 1870 vinduer, 91 dører; 0 brudd)
- OK   18_brygger  (38 av 38 brygger i ortofotoet finnes i kartet (100%, krav 95%); 57 brygger tegnet)
- OK   19_skyggekart_stabilt  (- zoom1.2: R 489 m, bilde 296 m, dekning 1.65; i ro 5 bilder, dra 6 bilder – ingen ny tegning)
- OK   20_grunnmur_fkb  (281 kommunehus i Gamlebyen over 6 m²: 0 uten modellhus med IoU >= 0,7; 0 modellhus dekker flere kommunehus; 5 unntak (fredet))
- OK   21_parkering  (56 plasser fra kommunens lag, 25 med målt flate, 31 med grunn; antall kjent for 19 (411 plasser), ukjent for 37)
- OK   21_register  (296 kommunehus i Gamlebyen (281 med modellhus), 245 bygningsnumre, 135 adresser (135 med hus, 135 med kort), 288 modellhus)
- OK   22_statue  (Frederik II (Wilhelm Rasmussen (1879–1965), 1917-09-12 (byens 350-årsjubileum)): 4.60 m høy, ser mot 291°, 0.0 m fra ortofotomålingen, +0.0° fra gatenettet)

Detaljer per regel i samme mappe.
