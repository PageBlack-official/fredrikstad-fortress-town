# Regelrapport

Kilde: 3bb3f58+urettet versjon 34 kjørt 2026-10-30 03:37

- OK   01_bygg_finnes  (0 bygg med vegetasjon under seg som ikke er skjult; 1 skjult med grunn)
- OK   02_hoyder_maalt  (212 hus står med Kartverkets målte høyde; 0 avviker; 119 hus uten sikker måling beholder tegning/OSM)
- FEIL 03_fasader_fra_tegning  (135 hus med fasade fra tegning, 196 antatt (må kvalitetssikres kvartal for kvartal))
- OK   04_vinduer_ikke_i_hjorner  (0 vinduer for nær et hjørne)
- OK   05_kvalitet_bare_kamera  (settSkala(skalaStille) uavhengig av bevegelse)
- OK   06_bygger_og_laster  (- bygd enkel -> /home/claude/wt-samlet/ut/enkel/index.html 3201 kB versjon 34)
- OK   07_ingen_feil_i_bruk  (- intro: underveis az -2.79 zoom 1.00 → ferdig az -2.79 zoom 1.00 intro false)
- OK   08_lint  (- ingen feil)
- FEIL 09_publisert  (- Pages: versjon 32 (ønsket 34))
- OK   10_mobiltrinn_tegner_likt  (- kronegrønt trinn 0: 19242 px, trinn 2: 18713 px)
- OK   11_kamera_glir  (- alle animerte flytt bruker glid/glidUt)
- FEIL 12_kontaktskygge  (- 0.2 % av Torvet-bildet er mørkere med kontaktskygge enn uten (krav 0,5–12 %))
- OK   13_deler_staar_paa_topp  (- bygg 230 (Det nye rådhus) del 0: h 21.0, målt topp 20.0, p90 i delen 19.9, kropp p50 10.3 → ok)
- OK   14_id  (485 bygg, 429 med bygningsnummer fra Matrikkelen (269 av 320 i Gamlebyen), 1612 id-er i registeret)
- OK   15_flater  (0 avvik, 5 advarsler; 19 plener innenfor ortofotoet målt)
- OK   16_vann  (99.40% av kartets vann er vann i ortofotoet (krav 98.5%), 99.48% av ortofotoets vann er dekket (krav 98.5%); før retting (OSM): 97.02% og 98.89%)
- OK   17_vinduer_rytme  (145 antatte hus og Street View-hus, 1870 vinduer, 91 dører; 0 brudd)
- OK   18_brygger  (38 av 38 brygger i ortofotoet finnes i kartet (100%, krav 95%); 57 brygger tegnet)
- OK   19_skyggekart_stabilt  (- zoom1.2: R 489 m, bilde 296 m, dekning 1.65; i ro 5 bilder, dra 6 bilder – ingen ny tegning)
- OK   20_grunnmur_fkb  (281 kommunehus i Gamlebyen over 6 m²: 0 uten modellhus med IoU >= 0,7; 0 modellhus dekker flere kommunehus; 5 unntak (fredet))
- OK   21_register  (296 kommunehus i Gamlebyen (281 med modellhus), 245 bygningsnumre, 135 adresser (135 med hus, 135 med kort), 288 modellhus)
- OK   22_flyt  (- ok   klikk på hus, kameraet glir inn: 912 ms, topp 55.2 px/bilde, hopp 0, rykk 0.24 (<= 0.45), bråstopp 0 (<= 0,15))
- OK   23_parkering  (56 plasser fra kommunens lag, 25 med målt flate, 31 med grunn; antall kjent for 19 (411 plasser), ukjent for 37)
- OK   24_statue  (Frederik II (Wilhelm Rasmussen (1879–1965), 1917-09-12 (byens 350-årsjubileum)): 4.60 m høy, ser mot 291°, 0.0 m fra ortofotomålingen, +0.0° fra gatenettet)
- OK   31_overflater  (gruppe 96.0% (krav 95 %), belagt type 98.1% (krav 95 %), prøvepunkter 96% av 24 (krav 95 %), dekning 100.00% (krav 99 %))
- OK   32_gater  (123 av 126 målte veier (Gamlebyen og kommunekartets dekning utenfor vollene) har riktig bredde og kant (97.6%, krav 95 %); 164 kan ikke måles (åpen plass, trær,)
- OK   33_gjerder  (presisjon 95.3% av 163 m funnet i fotoet (krav 95 %), dekning 99.7% av 195 m sett langs kandidatlinjene (krav 95 %); 0 av 95 stykker krysser gateareal eller hus)
- OK   34_traer  (1456 av 1459 trær i rammen rundt Gamlebyen (DOM-dekningen) står på vegetasjon i DOM−DTM (99.8%, krav 95 %); 0 i vann, 0 i hus; 1593 trær i alt = 2343 fra 23.10 )

Detaljer per regel i samme mappe.
