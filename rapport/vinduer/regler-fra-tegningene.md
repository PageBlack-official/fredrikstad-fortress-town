# Vinduer og dører: reglene Gamlebyens hus følger i kvartaltegningene (27.10.2026)

Målt på 121 fasit-hus (`fasade_kilde: kvartaltegning` og hus med v33-rettelse på vind; kirka og skjulte bygg holdt utenfor), 2518 vinduer og 121 dører.
Tallene: `maalinger.json`, laget av `mal_tegningene.py`. Veggene, gatesiden og felles vegg er beregnet av `verktoy/vegger.py`
(samme kode som lager vinduene og som regel 17 sjekker med). Bare tall er hentet ut, ingen geometri fra tegningene.

## Tallene

| Hva | Fasit | Regelen som brukes |
|---|---|---|
| Vindu | 0,85 × 1,4 m (68 % av bredder, 76 % av høyder); ellers 0,95, 1,5 og 0,69 × 0,81 | 0,85 × 1,4 m |
| Brystning | 0,9 m (1. etg), 3,9 m (2. etg), 6,9 m (3. etg) | 0,9 + 3,0 per etasje |
| Etasjehøyde | 3,0 m | 3,0 m |
| Antall etasjer | Alle rader der overkanten står minst 0,3 m under gesims: stemmer for 82 % av husene (7 % har flere) | Høyden styrer: samme formel |
| Avstand mellom vinduer (senter) | median 2,82 m, kvartiler 2,71–3,01, 10–90 %: 2,54–4,43 | Mål 2,8 m, lov 2,4–3,4 (2,2–3,6 på dørveggen) |
| Lik avstand innen en vegg | 69 % av veggene har helt lik avstand (avvik under 5 %) | Alltid lik |
| Første vindu fra hjørnet (senter) | 0,85 m på 56 % av veggene (median 0,85, kvartil 3: 1,87) | 0,85 m |
| Symmetri om veggens midtakse | 52 % innen 0,3 m | Alltid symmetrisk |
| Vinduer over hverandre | 72 % av vinduene i 2. og 3. etasje står rett over et vindu eller en dør | Alltid |
| Vegglengde → vinduer | under 2 m: 1 % har vindu, 2–3 m: 23 %, 3–4 m: 79 % (én akse), 4–6 m: 82 % (to), 6–9 m: 88 % (to), 9–13 m: 82 % (tre), 13–20 m: 87 % (fire) | Under 3 m: ingen. 3–4,5 m: ett vindu midt på. Ellers akser etter avstanden over |
| Felles vegg (nabohus inntil, 0,6 m) | 4 % har vinduer (173 hus-vegger og 44 uthus-vegger over 3 m) | Ingen |
| Dør | 1,05 × 2,2 m (51 %), 1,1 × 2,1 (19 %), fra bakken; 16 % med bue | 1,05 × 2,2 m, uten bue |
| Hvor døra står | 84 % på vegger mot gate (64 på gatesiden, 38 på en annen gatevegg), 9 % på baksiden, 4 % på siden | Bare på gatesiden |
| Døra langs veggen | median midt på (kvartiler 0,43–0,59 av lengden), 68 % i aksen nærmest midten, 53 % i vindusrytmen | Midtaksen (oddetall akser), eller midt mellom de to midterste når det er partall |
| Dører per hus | 0: 57 hus, 1: 32, 2: 18, 3+: 14 | Én dør per hus (ikke uthus) |
| Gatesiden | 107 av 121 hus har en vegg rett mot gate (OSM), 14 bare mot gårdsrom/åpent | Nærmeste gate rett ut; ellers sti; ellers mest åpne vegg |

## Uthus og garasjer (18 fasit-hus)
Hypotesen «uthus uten vinduer på baksiden» holder ikke i tegningene: 10 av 10 baksider og 18 av 20 sidevegger over 3 m har vinduer,
som på bolighusene. Det som skiller er døra: 2 av 15 uthus har dør på gatesiden. Regelen: uthus får vinduer etter samme regler, ingen dør.
De lave antatte garasjene (h under 2,6 m) får ingen vinduer fordi høyden ikke rommer et vindu under gesims.

## Usikkert
- 0,85 m fra hjørnet og helt lik avstand på over halvparten av veggene ser ut som måten fasadene ble hentet ut på (vinduene fordelt
  jevnt mellom to marger), ikke nødvendigvis tegningen. Antall vinduer per vegg (én akse per ca. 2,8–3 m) er det sikreste tallet.
- 57 av 121 fasit-hus har ingen dør i dataene. Det kan være at tegningen ikke viser døra (gårdsrom, bakside). Alle antatte bolighus
  får én dør på gatesiden.
- Gatesiden er regnet fra OSM-gater rett ut fra veggen. 41 av de antatte husene har ingen vegg rett mot gate (bakgårdshus); døra står
  da på den mest åpne veggen, som oftest er gårdsrommet.
- Gavlvinduer (over gesims, i gavltrekanten) finnes i fasit, men lages ikke: vinduer skal ikke sitte i taket.

## Resultat
`verktoy/vinduer_regler.py`: 142 antatte hus fikk nye vinduer og dører (2344 vinduer, 78 dører), som rettelser med grunn
«regler fra kvartaltegningene (27.10)». Før: 2198 vinduer og 59 dører slik kartet viste dem.
- 91 vinduer/dører mot nabohus (felles vegg) er borte, 11 vinduer på vegger under 3 m er borte.
- Dørene: før 59 i 44 hus, 17 av dem på en annen vegg enn gatesiden; nå én i hver av 78 bolighus, alle på gatesiden i aksen.
- 6 hus fikk 2. etasje med vinduer der høyden har plass til den; 25 hus er uendret.
- Regel 17 på de gamle dataene: 94 brudd (91 mot nabohus, 3 uten vindu under). Nå: 0.

Kontrollark: `kontrollark.png` (15 antatte hus før og etter), `kontrollark-fasit.png` (6 fasit-hus til sammenligning). Lages på nytt med
`python3 rapport/vinduer/kontrollark.py`.
