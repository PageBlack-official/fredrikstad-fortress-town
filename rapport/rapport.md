# Regelrapport

Kilde: af8bad8+urettet versjon 34 kjørt 2026-11-02 03:21

- FEIL 01_bygg_finnes  (krasjet: :)
- OK   02_hoyder_maalt  (202 hus står med Kartverkets målte høyde; 0 avviker; 142 hus uten sikker måling beholder tegning/OSM)
- FEIL 03_fasader_fra_tegning  (158 hus med fasade fra tegning, 185 antatt (må kvalitetssikres kvartal for kvartal))
- OK   04_vinduer_ikke_i_hjorner  (0 vinduer for nær et hjørne)
- OK   05_kvalitet_bare_kamera  (settSkala(skalaStille) uavhengig av bevegelse)
- OK   06_bygger_og_laster  (- bygd enkel -> /home/claude/wt-flyt3/ut/enkel/index.html 3189 kB versjon 34)
- OK   07_ingen_feil_i_bruk  (- intro: underveis az -2.77 zoom 0.99 → ferdig az -2.79 zoom 1.00 intro false)
- OK   08_lint  (- ingen feil)
- FEIL 09_publisert  (- Pages: versjon 32 (ønsket 34))
- OK   10_mobiltrinn_tegner_likt  (- kronegrønt trinn 0: 19087 px, trinn 2: 18593 px)
- OK   11_kamera_glir  (- alle animerte flytt bruker glid/glidUt)
- FEIL 12_kontaktskygge  (- 0.2 % av Torvet-bildet er mørkere med kontaktskygge enn uten (krav 0,5–12 %))
- OK   13_deler_staar_paa_topp  (- bygg 230 (Det nye rådhus) del 0: h 20.0, målt topp 20.0, p90 i delen 20.0, kropp p50 10.6 → ok)
- OK   14_id  (498 bygg, 429 med bygningsnummer fra Matrikkelen (269 av 333 i Gamlebyen), 1627 id-er i registeret)
- FEIL 15_flater  (ortofotoet mangler: kjør python3 verktoy/flater.py hent (flisene ligger ikke i git, lisensen er ikke avklart))
- FEIL 16_vann  (ortofotoet eller vannfasiten mangler: kjør python3 verktoy/vann.py hent og maske (ligger ikke i git, lisensen er ikke avklart))
- OK   17_vinduer_rytme  (127 antatte hus og Street View-hus, 1633 vinduer, 82 dører; 0 brudd)
- FEIL 18_brygger  (38 av 38 brygger i ortofotoet finnes i kartet (100%, krav 95%); 57 brygger tegnet)
- OK   19_skyggekart_stabilt  (- zoom1.2: R 489 m, bilde 296 m, dekning 1.65; i ro 5 bilder, dra 6 bilder – ingen ny tegning)
- FEIL 20_grunnmur_fkb  (kommunekartet mangler: mangler /home/claude/wt-flyt3/kilder/kommunekart/kommunekart.pdf (Vegars nedlasting fra kommunens kartportal; ligger bare lokalt))
- FEIL 21_register  (krasjet: mangler /home/claude/wt-flyt3/kilder/kommunekart/kommunekart.pdf (Vegars nedlasting fra kommunens kartportal; ligger bare lokalt))
- OK   22_flyt  (- ok   klikk på hus, kameraet glir inn: 912 ms, topp 57 px/bilde, hopp 0, rykk 0.2 (<= 0.45), bråstopp 0 (<= 0,15))
- OK   23_parkering  (56 plasser fra kommunens lag, 25 med målt flate, 31 med grunn; antall kjent for 19 (411 plasser), ukjent for 37)
- OK   24_statue  (Frederik II (Wilhelm Rasmussen (1879–1965), 1917-09-12 (byens 350-årsjubileum)): 4.60 m høy, ser mot 291°, 0.0 m fra ortofotomålingen, +0.0° fra gatenettet)
- FEIL 31_overflater  (ortofotoet eller kommunekartet mangler lokalt (verktoy/flater.py hent; kommunekart.pdf fra Vegar))
- FEIL 32_gater  (kommunekartet mangler lokalt)
- FEIL 33_gjerder  (krasjet: _DPI, alpha=False))
- OK   34_traer  (1455 av 1458 trær i rammen rundt Gamlebyen (DOM-dekningen) står på vegetasjon i DOM−DTM (99.8%, krav 95 %); 0 i vann, 0 i hus; 1592 trær i alt = 2343 fra 23.10 )

Detaljer per regel i samme mappe.
