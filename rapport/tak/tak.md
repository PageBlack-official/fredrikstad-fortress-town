# Rene tak og husdeling etter tegningen (natt/tak, 30.10)

Verktøy: verktoy/tak_enkel.py (rene tak), verktoy/husdeling.py (delinger/sammenslåinger, kilder/husdeling.json), kilder/tak-tegning.json
(takform, mønretning og tårn lest av tegningene). Se LESMEG «Rene tak og husdeling etter tegningen».

## Kontrolltall før/etter (verktoy/kontroll.py, alle 18 tegninger)
Før = kontrollørens kjøring på natt/kontroll (30.10 03.50). Etter = denne grenen etter fletting med natt/samlet (fargene).
Tegningshus = modellhus med tildelt tegnet flate. «Takform feil» etter leser takformen tak_enkel.py bygde taket med (før ble den
gjettet fra flatene, og brannmurer ga «halvvalm»); tallet er derfor ikke helt sammenlignbart.

| tegning | tegningshus funnet | IoU ≥ 0,75 | median IoU | takform feil | slått sammen | tegnet uten modellhus (≥ 600 pt²) |
|---|---|---|---|---|---|---|
| Kvartal2BITMP | 18 → 18 | 1 → 1 | 0.49 → 0.48 | 1 → 0 | 1 → 0 | 6 → 4 |
| Kvartal3 | 3 → 7 | 0 → 1 | 0.53 → 0.53 | 0 → 0 | 2 → 2 | 4 → 1 |
| Kvartal4BITMP | 9 → 8 | 0 → 1 | 0.43 → 0.52 | 1 → 1 | 1 → 2 | 3 → 2 |
| kvartal5 | 15 → 16 | 1 → 3 | 0.64 → 0.58 | 6 → 1 | 3 → 2 | 1 → 0 |
| kvartal6 | 12 → 14 | 0 → 1 | 0.35 → 0.49 | 1 → 0 | 3 → 4 | 4 → 4 |
| kvartal7 | 15 → 16 | 0 → 0 | 0.57 → 0.51 | 3 → 1 | 5 → 4 | 1 → 1 |
| Kvartal8BITMAP | 18 → 17 | 2 → 1 | 0.55 → 0.53 | 6 → 1 | 3 → 3 | 5 → 4 |
| Kvartal9 | 21 → 23 | 0 → 1 | 0.47 → 0.43 | 4 → 2 | 1 → 1 | 0 → 0 |
| Kvartal10 | 14 → 14 | 2 → 2 | 0.53 → 0.56 | 0 → 0 | 3 → 3 | 2 → 3 |
| Kvartal11 | 3 → 3 | 0 → 1 | 0.35 → 0.29 | 0 → 0 | 0 → 0 | 4 → 5 |
| Kvartal12 | 22 → 20 | 0 → 0 | 0.51 → 0.50 | 1 → 0 | 2 → 3 | 2 → 1 |
| Kvartal13 | 4 → 6 | 1 → 1 | 0.70 → 0.61 | 1 → 0 | 2 → 1 | 6 → 6 |
| Kvartal14 | 19 → 18 | 0 → 0 | 0.50 → 0.52 | 2 → 1 | 0 → 3 | 1 → 1 |
| sistekvartal | 6 → 6 | 1 → 1 | 0.50 → 0.53 | 0 → 0 | 0 → 0 | 3 → 2 |
| tell | 2 → 3 | 1 → 1 | 0.70 → 0.62 | 0 → 0 | 0 → 1 | 0 → 0 |
| Glasshytta | 1 → 1 | 0 → 1 | 0.75 → 0.80 | 0 → 0 | 0 → 0 | 2 → 2 |
| kirke | 1 → 1 | 0 → 0 | 0.64 → 0.69 | 1 → 1 | 0 → 1 | 1 → 2 |
| Toihuset | 1 → 1 | 1 → 1 | 0.87 → 0.86 | 1 → 1 | 1 → 1 | 1 → 1 |
| sum | 184 → 192 | 10 → 17 | | 28 → 9 | 27 → 31 | 46 → 39 |

## Det som er gjort
- 289 hus i Gamlebyen har rent tak: én til tre rektangulære kropper med sal/valm/halvvalm/pult/flatt, mønretning og form fra
  tegningen der kontrollen ser gavler/valm (20 hus), ellers tilpasset Kartverkets DOM. Vegghøyde og takhelning fra DOM der
  rapport/hoyder ikke har sikker måling (h var 8–9 m på flere uthus på 3–4 m).
- 9 hus delt der tegningen viser flere hus og DOM har sprang i mønet (867758, 972446, 867952, 868231, 6242812, 868096, 867502 i tre,
  971369, 867928); Artillerigården 868061 + 869572 slått sammen (ett langhus i tegningen, sammenhengende møne i DOM).
- Gårdsrommet i Kvartal12 (868606, 972446, 972608, 972594): alle har tak i ortofoto 2024 og 3–7 m i DOM; beholdt med lav høyde og
  enkelt tak.
- Tårn på 868711 (Kvartal10) fra tegningen, høyde fra DOM (16,3 m).
- Koblinger: Kvartal11 = Infanterikasernen (+ brannstasjonen, pb-51); Kvartal3: fem biter med håndsatt forskyvning; tell: skuret
  867685; Glasshytta: Voldporten som bit; 869580 enkelt valmtak.

## Ikke løst
- IoU ≥ 0,75 for alle tegningshus er ikke nådd (17 av 192). Frihånd: husene i en tegning har ulik målestokk og forskyvning, så riktige hus
  gir IoU 0,5–0,7.
- Hus der tegningen viser flere fasader, men DOM har sammenhengende møne og Matrikkelen ett bygningsnummer (987397 i kvartal5,
  867804 i Kvartal12, 13394024 i Kvartal10 m.fl.), er ikke delt.
- kvartal6 registreres ustabilt: med ett kamera havner høyre husrad utenfor, med et annet havner baksiden 34 pt for høyt; målet velger det første.
- Rådhustårnet (972012) står der DOM har det, ikke der tegningen har det. Arkadene og rundbuene er fasadeelementer (ikke geometri).
- 867634 (tell): tegningen har et lite gavlhus, ortofoto 2024 og DOM har ett langt hus; står som langt hus.
