# Fargeregister fra 2019-brosjyren — FORSLAG (ikke lagt inn)

Kilde: kilder2019/brosjyre2019-3.jpg (2480×1754, norsk kartside; -1 og -5 er samme kart på andre språk, -2/-4/-6 er tekstsider). Vegar: «alle hus er farget korrekt» der. Takene har ingen regel; de er lest som de er.

Filer: soc/rapport/farger2019.json (register), soc/rapport/farger2019-kontrollark.png (samplepunkter), soc/rapport/farger2019-ark/ (per kvartal), kode i soc/rapport/_farger2019/ (registrer.py, kvartaldel.py, hoved.py, rapport.py, ark.py).

## Metode

1. **Registrering.** 2019-JPG-en er den samme tegningen som 2015-trykket (pdf/side300-1.png) i halv oppløsning. ORB + RANSAC (similaritet) gir 2015-px → 2019-px: skala 0,49976, rotasjon 0,01°, forskyvning (0,60, 0,14) px, residual median 0,7 px. Lagret i _farger2019/reg2015til2019.npy. Dermed virker affin2 (modell → 2015-px) og kvartaltegningenes plassering (kvartal/vek/plassering.json) rett inn i 2019-bildet.
2. **Del A, hus med kvartaltegning (106 hus).** Kvartaltegningene er utsnitt av samme vektortegning, plassert i trykket med skala/forskyvning som stemmer på ±1 px. For hver fasade som kvartal/ut/kobling-*.json kobler til et modellbygg, legges veggpolygonet (tegning-pt → trykk → 2019-px) på 2019-bildet og den dominerende fargen leses (grov kvantisering, største klynge, median; svart strek, grønt (trær/plen) og vann hoppes over). Takflater = de flatene av typen «tak» i kvartaltegningen som grenser til veggens overkant (buffer 1,6 pt, sentrum over veggen). Kantstykker som stikker ut av arket (avkuttede nabohus) hoppes over. Vegger grupperes etter retning (basekant faller mot venstre/høyre): lysest = vegg, mørkest = veggs hvis samme kulør. Tak = tyngste klynge (piksler × kontaktlengde); er den mørk og en lysere flate har ≥25 % av vekten, er den mørke skyggesiden (taks). Kvartaltegningens egen fyllfarge brukes som kryssjekk per flate (se Kryssjekk).
3. **Del B, resten innenfor arket (104 hus).** Som forrige forsøk (soc/rapport/_farger/kjor.py): 2015-trykkets vektorflater rastrert til etikettbilde, fotavtrykket projisert med affin2 + lokal korreksjon og flyttet (±48 px, pluss 4·h i høyden) til flest punkter lander på husflater. Nytt: fargen leses ikke fra 2015-vektoren, men fra 2019-bildet innenfor den samme flaten. Takflate = flaten med flest fotavtrykkspunkter; vegg = første husflate under synlige kanter. Sikkerhet maks «middels» her, fordi husene er tegnet fritt og ren forskyvning kan treffe nabohuset.
4. **Skyggetoner.** Der tak eller vegg er funnet uten skyggeflate, er taks/veggs hentet fra det vanligste paret i registeret for samme lysfarge (merket «utledet fra palettpar» i merknaden).

## Kryssjekk 2019 ↔ kvartaltegning

Kvartaltegningene har fyllfarger som RGB (3 verdier) eller CMYK (4 verdier). RGB-verdiene treffer 2019-bildet direkte (f.eks. (206,129,63) i tegningen = (205,130,63) i 2019). CMYK-verdiene er oversatt med et oppslag bygd av de sikre prøvene (andel > 0,5, > 150 px): (0, .648, .551, 0) → (240,120,103), (.205, .64, .608, .167) → (180,103,85), (0,0,0,.3) → (198,198,198) osv. (_farger2019/cmyk-oppslag.json). Per flate: enig (±15) → flaten teller fullt; uenig og 2019 tydelig (andel ≥ 0,45, ≥ 120 px) → 2019 velges med vekt 0,6; uenig og 2019 utydelig (trær, symboler, tekst over) → kvartaltegningens farge med vekt 0,3. **2019 vinner der den er lesbar**, fordi det er Vegars fasit; kvartaltegningen brukes der 2019 er dekket. Uenighet skyldes nesten alltid at noe ligger over huset i 2019 (trær, tegnforklaringssirkler, symboler), eller at koblingen fasade→bygg har tatt nabohuset.

## Kalibrering mot dagens bygg.vegg/tak (hus med veggs/taks i dag)

- Tak: 113 av 198 = **57 %** (±15 per kanal; treff hvis forslagets tak/taks treffer dagens tak/taks).
- Vegg: 60 av 180 = **33 %**.
- Per sikkerhet (tak): høy 50/80, middels 48/85, lav 15/33.
- **Målet på 85 % er ikke nådd, og jeg tror ikke det kan nås mot denne fasiten.** Av de 85 bommene har 50 dagens standardverdi rødt tak (244/246,120,104) og 29 dagens grått (188/190/128). Kontrollarket og utsnittene i _farger2019/chk-miss.png viser at 2019-tegningen faktisk har grått tak der dagens verdi sier rødt (f.eks. bygg 194, 206, 226, 313) og rødt der dagens sier grått (168, 208, 218, 355, 380). Dagens verdier er i stor grad standardverdier (145 hus har nøyaktig (244,120,104)), ikke avlest trykk. 2019-bildet er fasiten Vegar ba om; der registeret og dagens verdi er uenige, er det dagens verdi som bør byttes, ikke forslaget. Uavhengig sjekk: for de 28 husene med tegnforklaringsnummer (sirkelen sitter på taket) stemmer forslaget med fargen rundt sirkelen for de store, frittliggende husene (Tøihuset, Provianthuset, Laboratoriet, Bakeriet, Ekserserhuset, Arnesgården, Det gamle rådhus, Rosinggården, Bullgården); bommene der er hus der sirkelen sitter på skyggesiden eller på en nabo.
- Det som fortsatt er usikkert: Del B-husene (ren forskyvning) i de tette kvartalene uten kvartaltegning, og hus der koblingen fasade→bygg i kvartal/ut/kobling-*.json har tatt nabohuset (det gir riktig farge for feil hus).

## Antall

- Hus i modellen: 441. Med farge i registeret: 210 (høy 84, middels 90, lav 36). Kilde: 2019 104, 2019+kvartaltegning 106.
- Ikke i trykket: 231, hvorav 187 utenfor arket (gml=0), 9 skjult, og 35 innenfor arket uten lesbar husflate: 10, 17, 28, 100, 101, 103, 113, 114, 115, 120, 123, 171, 181, 270, 271, 272, 273, 274, 275, 276, 277, 278, 310, 368, 370, 373, 374, 395, 396, 397, 403, 405, 407, 412, 430.

## Palett i 2019 (klynger ±8, antall hus)

**Tak (lys side)**

- rgb(240, 120, 103) — 77 hus
- rgb(179, 102, 84) — 39 hus
- rgb(217, 110, 92) — 14 hus
- rgb(135, 135, 135) — 10 hus
- rgb(198, 198, 198) — 8 hus
- rgb(119, 119, 117) — 7 hus
- rgb(243, 150, 132) — 5 hus
- rgb(186, 113, 96) — 5 hus
- rgb(244, 244, 244) — 5 hus
- rgb(232, 215, 199) — 4 hus
- rgb(115, 151, 115) — 3 hus
- rgb(255, 255, 255) — 3 hus
- rgb(148, 148, 148) — 3 hus
- rgb(171, 82, 66) — 2 hus
- rgb(199, 102, 86) — 2 hus
- rgb(67, 67, 65) — 2 hus
- rgb(214, 202, 154) — 2 hus
- rgb(143, 88, 71) — 2 hus
- rgb(244, 150, 76) — 2 hus
- rgb(248, 194, 147) — 2 hus
- rgb(217, 193, 181) — 1 hus
- rgb(208, 208, 208) — 1 hus
- rgb(234, 86, 86) — 1 hus
- rgb(103, 137, 104) — 1 hus
- rgb(226, 226, 226) — 1 hus
- rgb(220, 174, 133) — 1 hus
- rgb(167, 165, 166) — 1 hus
- rgb(250, 209, 171) — 1 hus
- rgb(254, 238, 180) — 1 hus
- rgb(218, 217, 218) — 1 hus
- rgb(95, 92, 91) — 1 hus
- rgb(89, 119, 91) — 1 hus
- rgb(249, 230, 214) — 1 hus

**Tak (skyggeside)**

- rgb(179, 102, 84) — 24 hus
- rgb(115, 115, 115) — 6 hus
- rgb(217, 110, 92) — 6 hus
- rgb(135, 135, 135) — 5 hus
- rgb(143, 88, 71) — 5 hus
- rgb(186, 113, 96) — 2 hus
- rgb(128, 125, 119) — 2 hus
- rgb(222, 175, 133) — 1 hus
- rgb(67, 67, 65) — 1 hus
- rgb(94, 126, 96) — 1 hus
- rgb(240, 120, 103) — 1 hus
- rgb(234, 86, 86) — 1 hus
- rgb(198, 198, 198) — 1 hus
- rgb(113, 110, 106) — 1 hus
- rgb(249, 194, 147) — 1 hus
- rgb(250, 209, 171) — 1 hus

**Vegg (lys side)**

- rgb(244, 244, 244) — 27 hus
- rgb(180, 103, 85) — 20 hus
- rgb(237, 120, 103) — 20 hus
- rgb(198, 198, 198) — 20 hus
- rgb(249, 195, 148) — 12 hus
- rgb(243, 150, 132) — 11 hus
- rgb(232, 215, 199) — 9 hus
- rgb(251, 230, 213) — 8 hus
- rgb(255, 255, 255) — 7 hus
- rgb(226, 226, 226) — 5 hus
- rgb(222, 175, 133) — 5 hus
- rgb(217, 110, 92) — 4 hus
- rgb(240, 222, 208) — 4 hus
- rgb(250, 209, 172) — 4 hus
- rgb(119, 119, 117) — 4 hus
- rgb(244, 150, 76) — 4 hus
- rgb(146, 146, 146) — 3 hus
- rgb(167, 165, 166) — 3 hus
- rgb(255, 232, 162) — 2 hus
- rgb(89, 119, 91) — 2 hus
- rgb(246, 176, 164) — 2 hus
- rgb(255, 244, 212) — 2 hus
- rgb(243, 165, 106) — 1 hus
- rgb(205, 130, 64) — 1 hus
- rgb(99, 100, 97) — 1 hus
- rgb(184, 113, 96) — 1 hus
- rgb(208, 230, 234) — 1 hus
- rgb(115, 112, 108) — 1 hus
- rgb(226, 213, 165) — 1 hus
- rgb(115, 151, 115) — 1 hus
- rgb(244, 177, 184) — 1 hus
- rgb(214, 202, 154) — 1 hus
- rgb(255, 239, 182) — 1 hus
- rgb(131, 129, 124) — 1 hus
- rgb(244, 159, 139) — 1 hus
- rgb(234, 86, 86) — 1 hus
- rgb(218, 217, 218) — 1 hus
- rgb(255, 247, 226) — 1 hus

**Vegg (skyggeside)**

- rgb(180, 103, 85) — 8 hus
- rgb(198, 198, 198) — 6 hus
- rgb(135, 135, 135) — 3 hus
- rgb(230, 214, 200) — 2 hus
- rgb(131, 128, 123) — 2 hus
- rgb(239, 121, 103) — 2 hus
- rgb(144, 87, 72) — 2 hus
- rgb(221, 175, 133) — 1 hus
- rgb(162, 162, 162) — 1 hus
- rgb(227, 212, 165) — 1 hus
- rgb(119, 119, 117) — 1 hus
- rgb(244, 244, 244) — 1 hus
- rgb(243, 150, 132) — 1 hus
- rgb(248, 194, 146) — 1 hus
- rgb(246, 176, 164) — 1 hus
- rgb(95, 93, 92) — 1 hus
- rgb(196, 206, 174) — 1 hus
- rgb(218, 218, 218) — 1 hus
- rgb(214, 202, 154) — 1 hus
- rgb(255, 232, 163) — 1 hus

## Hus der 2019 avviker fra dagens bygg.vegg/tak med mer enn 20 per kanal (182 hus)

| bygg | navn | tak i dag | tak 2019 | vegg i dag | vegg 2019 | sikkerhet | kilde |
|---|---|---|---|---|---|---|---|
| 1 | Hovedvakten – det gamle slaveri | [246, 122, 106] | [240, 120, 103] | [254, 190, 146] | [222, 175, 133] | middels | 2019 |
| 2 | Det grundmurede provianthus | [244, 120, 104] | [240, 120, 103] | [248, 224, 204] | [254, 254, 254] | middels | 2019 |
| 3 | Infanterikasernen | [246, 122, 106] | [243, 151, 132] | [246, 150, 130] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 4 | Kirken | [238, 242, 242] | [255, 255, 255] | [238, 242, 242] | [204, 204, 204] | lav | 2019 |
| 5 | Tøihuset | [246, 122, 106] | [240, 120, 103] | [252, 188, 144] | [221, 175, 133] | middels | 2019 |
| 6 | Labratoriet | [246, 122, 106] | [240, 120, 103] | [254, 190, 146] | [242, 151, 132] | lav | 2019 |
| 7 | Brannbatteriet | [244, 120, 104] | [217, 193, 181] | [252, 188, 144] | [240, 120, 103] | lav | 2019 |
| 8 | Binggården | [188, 188, 192] | [171, 82, 66] | [236, 240, 240] | [252, 252, 252] | høy | 2019+kvartaltegning |
| 9 | Artillerigården | [246, 122, 106] | [179, 102, 84] | [246, 150, 130] | [249, 195, 148] | middels | 2019+kvartaltegning |
| 13 | Brannstasjon - uthus til Infanterikasernen | [246, 122, 106] | [180, 103, 85] | [246, 150, 130] | [180, 103, 85] | høy | 2019+kvartaltegning |
| 15 | Undervisningsbrakke | [246, 122, 106] | [179, 102, 84] | [218, 110, 94] | [179, 102, 84] | middels | 2019+kvartaltegning |
| 16 | Artillerismiens uthus | [246, 122, 106] | [180, 102, 86] | [252, 188, 144] | [89, 119, 91] | lav | 2019 |
| 18 | Voldporten med vaktstuen | [246, 122, 106] | [115, 151, 115] | [236, 240, 240] | None | lav | 2019 |
| 19 | Den gamle spisesal | [246, 122, 106] | [240, 120, 103] | [236, 240, 240] | [243, 165, 106] | høy | 2019+kvartaltegning |
| 20 | Kjørbogårdens sidebygning | [190, 190, 194] | [133, 135, 134] | [238, 238, 238] | [199, 198, 197] | middels | 2019 |
| 21 | Kommandantgården | [246, 122, 106] | [184, 111, 94] | [236, 240, 240] | [243, 242, 244] | høy | 2019+kvartaltegning |
| 22 | Offisersvakten | [246, 122, 106] | [208, 208, 208] | [236, 240, 240] | [249, 195, 148] | middels | 2019 |
| 24 | Ekserserhuset | [246, 122, 106] | [237, 120, 103] | [244, 148, 80] | [205, 130, 64] | høy | 2019+kvartaltegning |
| 25 | Kommisjonsgården | [188, 188, 192] | [178, 102, 85] | [252, 228, 156] | [251, 230, 213] | middels | 2019 |
| 26 | Voldportravelinet | [244, 120, 104] | [115, 151, 115] | [244, 148, 128] | None | lav | 2019 |
| 29 | Sprøytehuset / Proviantboden | [244, 120, 104] | [255, 254, 254] | [236, 240, 240] | [240, 120, 103] | lav | 2019 |
| 30 | Artillerismien | [244, 120, 104] | [179, 102, 84] | [248, 224, 204] | [249, 195, 148] | middels | 2019+kvartaltegning |
| 99 | Annekset | [244, 120, 104] | [198, 198, 198] | [236, 240, 240] | [90, 120, 91] | lav | 2019 |
| 102 |  | [244, 120, 104] | [198, 198, 198] | [252, 188, 144] | [244, 243, 245] | middels | 2019 |
| 107 | Det gamle raadhus | [246, 122, 106] | [243, 150, 132] | [254, 234, 174] | [146, 146, 146] | høy | 2019+kvartaltegning |
| 108 |  | [246, 122, 106] | [179, 102, 84] | [250, 226, 206] | [243, 150, 132] | høy | 2019+kvartaltegning |
| 109 |  | [246, 122, 106] | [198, 198, 198] | [254, 190, 146] | [247, 194, 150] | høy | 2019+kvartaltegning |
| 110 |  | [244, 120, 104] | [234, 86, 86] | [254, 234, 174] | [197, 198, 199] | høy | 2019+kvartaltegning |
| 152 |  | [238, 242, 242] | [245, 243, 243] | [246, 122, 106] | [99, 100, 97] | lav | 2019 |
| 154 |  | [188, 188, 192] | [198, 197, 198] | [236, 240, 240] | [217, 110, 92] | middels | 2019 |
| 156 |  | [246, 122, 106] | [240, 120, 103] | [236, 240, 240] | [251, 230, 213] | høy | 2019+kvartaltegning |
| 157 |  | [246, 122, 106] | [179, 102, 84] | [236, 240, 240] | [196, 198, 197] | høy | 2019+kvartaltegning |
| 158 |  | [246, 122, 106] | [240, 120, 103] | [236, 240, 240] | [251, 230, 213] | høy | 2019+kvartaltegning |
| 159 | Skolebygningen | [246, 122, 106] | [240, 120, 103] | [252, 228, 156] | [245, 244, 245] | lav | 2019 |
| 160 |  | [246, 150, 130] | [186, 113, 96] | [244, 148, 80] | [198, 198, 198] | høy | 2019+kvartaltegning |
| 162 |  | [190, 190, 194] | [218, 111, 93] | [248, 224, 204] | [250, 196, 148] | høy | 2019+kvartaltegning |
| 163 |  | [190, 190, 194] | [240, 120, 103] | [252, 228, 156] | [244, 244, 244] | lav | 2019 |
| 164 | Muldvadgården | [246, 122, 106] | [240, 120, 103] | [254, 230, 158] | [231, 215, 199] | middels | 2019+kvartaltegning |
| 168 |  | [190, 190, 194] | [240, 120, 103] | [246, 150, 130] | [232, 215, 200] | høy | 2019+kvartaltegning |
| 170 |  | [246, 122, 106] | [179, 102, 84] | [250, 226, 206] | [184, 113, 96] | lav | 2019 |
| 172 | Salamandergården | [246, 122, 106] | [179, 102, 84] | [254, 190, 146] | [247, 195, 149] | høy | 2019+kvartaltegning |
| 173 |  | [244, 120, 104] | [217, 110, 92] | [236, 240, 240] | [198, 198, 198] | høy | 2019+kvartaltegning |
| 174 |  | [246, 122, 106] | [240, 120, 103] | [250, 226, 206] | [219, 110, 93] | høy | 2019+kvartaltegning |
| 176 |  | [246, 122, 106] | [103, 137, 104] | [238, 242, 242] | None | lav | 2019 |
| 178 |  | [246, 122, 106] | [179, 102, 84] | [254, 230, 158] | [240, 222, 208] | middels | 2019 |
| 179 |  | [246, 122, 106] | [240, 120, 103] | [236, 240, 240] | [249, 195, 148] | høy | 2019+kvartaltegning |
| 180 |  | [246, 122, 106] | [240, 120, 103] | [236, 240, 240] | [208, 230, 234] | høy | 2019+kvartaltegning |
| 182 | Balaklava | [246, 122, 106] | [240, 120, 103] | [250, 226, 206] | [243, 244, 244] | middels | 2019+kvartaltegning |
| 183 |  | [188, 188, 192] | [186, 113, 96] | [236, 240, 240] | [226, 226, 226] | middels | 2019 |
| 184 | Rosinggården | [244, 120, 104] | [198, 197, 199] | [188, 220, 216] | [199, 198, 199] | middels | 2019 |
| 185 |  | [246, 122, 106] | [240, 120, 103] | [218, 110, 94] | [241, 119, 102] | høy | 2019+kvartaltegning |
| 186 |  | [246, 150, 130] | [240, 120, 103] | [246, 122, 106] | [243, 188, 143] | middels | 2019+kvartaltegning |
| 187 |  | [244, 120, 104] | [240, 120, 103] | [104, 168, 128] | [115, 112, 108] | høy | 2019+kvartaltegning |
| 188 |  | [188, 188, 192] | [217, 110, 92] | [236, 240, 240] | [245, 151, 74] | middels | 2019 |
| 189 |  | [244, 120, 104] | [240, 120, 103] | [236, 240, 240] | [197, 197, 198] | høy | 2019+kvartaltegning |
| 190 |  | [188, 188, 192] | [218, 111, 93] | [236, 240, 240] | [254, 255, 254] | middels | 2019 |
| 191 |  | [244, 120, 104] | [179, 102, 84] | [236, 240, 240] | [198, 199, 198] | middels | 2019 |
| 192 |  | [244, 120, 104] | [217, 110, 92] | [248, 224, 204] | [218, 110, 92] | middels | 2019 |
| 193 | Bullgården | [188, 188, 192] | [244, 244, 244] | [236, 240, 240] | [244, 244, 245] | lav | 2019 |
| 194 |  | [244, 120, 104] | [133, 133, 131] | [188, 220, 216] | [198, 197, 199] | høy | 2019+kvartaltegning |
| 195 |  | [244, 120, 104] | [244, 244, 244] | [236, 240, 240] | [198, 198, 198] | høy | 2019+kvartaltegning |
| 196 |  | [218, 110, 94] | [179, 102, 84] | [250, 238, 226] | [241, 222, 208] | høy | 2019+kvartaltegning |
| 199 |  | [246, 122, 106] | [179, 102, 84] | [252, 188, 144] | None | lav | 2019 |
| 201 |  | [246, 122, 106] | [236, 221, 206] | [238, 214, 198] | [226, 213, 165] | høy | 2019+kvartaltegning |
| 202 |  | [188, 188, 192] | [135, 135, 135] | [236, 240, 240] | [115, 151, 115] | lav | 2019 |
| 203 |  | [244, 120, 104] | [199, 102, 86] | [236, 240, 240] | [240, 120, 103] | middels | 2019 |
| 204 | Prestegården | [246, 122, 106] | [240, 120, 103] | [254, 190, 146] | [197, 199, 198] | høy | 2019+kvartaltegning |
| 205 |  | [244, 120, 104] | [217, 110, 92] | [188, 220, 216] | [243, 244, 245] | høy | 2019+kvartaltegning |
| 206 |  | [244, 120, 104] | [135, 135, 135] | [244, 148, 128] | [243, 149, 132] | høy | 2019+kvartaltegning |
| 207 |  | [244, 120, 104] | [241, 120, 104] | [236, 240, 240] | [250, 230, 213] | høy | 2019+kvartaltegning |
| 208 |  | [188, 188, 192] | [240, 120, 103] | [236, 240, 240] | [244, 244, 244] | høy | 2019+kvartaltegning |
| 209 |  | [246, 150, 130] | [243, 150, 132] | [238, 242, 242] | [217, 110, 92] | middels | 2019 |
| 210 |  | [246, 150, 130] | [179, 102, 84] | [194, 122, 110] | [198, 198, 198] | høy | 2019+kvartaltegning |
| 211 |  | [188, 188, 192] | [143, 88, 71] | [236, 240, 240] | [238, 121, 103] | høy | 2019+kvartaltegning |
| 213 |  | [244, 120, 104] | [240, 120, 103] | [252, 228, 156] | [240, 120, 102] | middels | 2019 |
| 214 |  | [246, 150, 82] | [240, 120, 103] | [246, 122, 106] | [243, 150, 74] | høy | 2019+kvartaltegning |
| 215 |  | [244, 120, 104] | [240, 121, 103] | [236, 240, 240] | [249, 208, 173] | høy | 2019+kvartaltegning |
| 216 |  | [246, 122, 106] | [232, 215, 199] | [250, 226, 206] | [251, 230, 213] | middels | 2019+kvartaltegning |
| 217 |  | [246, 150, 130] | [243, 150, 132] | [218, 110, 94] | [115, 115, 115] | middels | 2019 |
| 218 |  | [188, 188, 192] | [240, 120, 103] | [236, 240, 240] | [250, 229, 214] | høy | 2019+kvartaltegning |
| 219 |  | [244, 120, 104] | [226, 226, 226] | [236, 240, 240] | [226, 226, 226] | middels | 2019 |
| 220 |  | [246, 122, 106] | [179, 102, 84] | [246, 150, 82] | [231, 215, 200] | høy | 2019+kvartaltegning |
| 221 | Gamlebyen modelljernbanesenter | [244, 120, 104] | [243, 150, 132] | [236, 240, 240] | [254, 255, 255] | høy | 2019+kvartaltegning |
| 224 |  | [190, 190, 194] | [240, 120, 103] | [250, 226, 170] | [244, 244, 246] | middels | 2019+kvartaltegning |
| 225 |  | [188, 188, 192] | [135, 135, 135] | [236, 240, 240] | [243, 150, 132] | middels | 2019+kvartaltegning |
| 226 |  | [244, 120, 104] | [119, 119, 117] | [236, 240, 240] | [244, 244, 244] | høy | 2019+kvartaltegning |
| 227 |  | [142, 142, 146] | [148, 148, 148] | [254, 230, 158] | [139, 139, 138] | lav | 2019 |
| 229 |  | [246, 122, 106] | [237, 120, 103] | [246, 150, 82] | [180, 103, 85] | middels | 2019 |
| 230 | Det nye rådhus | [244, 120, 104] | [67, 67, 65] | [252, 188, 144] | [180, 103, 85] | middels | 2019+kvartaltegning |
| 231 | Sindinggården | [244, 120, 104] | [220, 174, 133] | [236, 240, 240] | [237, 120, 103] | middels | 2019 |
| 232 |  | [246, 122, 106] | [237, 120, 103] | [246, 150, 130] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 233 |  | [246, 122, 106] | [180, 103, 85] | [254, 190, 146] | [250, 209, 172] | høy | 2019+kvartaltegning |
| 234 |  | [246, 122, 106] | [179, 102, 84] | [234, 234, 234] | [179, 102, 84] | middels | 2019+kvartaltegning |
| 236 |  | [188, 188, 192] | [237, 120, 103] | [236, 240, 240] | [180, 103, 85] | lav | 2019 |
| 237 |  | [246, 122, 106] | [167, 165, 166] | [238, 238, 238] | [167, 165, 166] | middels | 2019 |
| 238 |  | [246, 122, 106] | [119, 119, 117] | [254, 230, 158] | [119, 119, 117] | høy | 2019+kvartaltegning |
| 240 | Dunkejongården | [246, 122, 106] | [180, 103, 85] | [254, 230, 158] | [255, 232, 162] | middels | 2019 |
| 241 |  | [244, 120, 104] | [180, 103, 85] | [244, 148, 80] | [180, 103, 85] | høy | 2019+kvartaltegning |
| 242 |  | [244, 120, 104] | [237, 120, 103] | [236, 240, 240] | [255, 244, 212] | høy | 2019+kvartaltegning |
| 244 |  | [246, 122, 106] | [237, 120, 103] | [246, 150, 86] | [244, 177, 184] | middels | 2019 |
| 245 |  | [244, 120, 104] | [244, 150, 76] | [248, 224, 204] | [231, 212, 199] | middels | 2019 |
| 246 |  | [244, 120, 104] | [180, 104, 86] | [236, 240, 240] | [214, 202, 154] | middels | 2019 |
| 247 |  | [246, 122, 106] | [237, 120, 103] | [246, 150, 130] | [246, 177, 164] | høy | 2019+kvartaltegning |
| 248 | Vennehaabet | [244, 120, 104] | [150, 150, 150] | [244, 148, 80] | [243, 243, 243] | høy | 2019+kvartaltegning |
| 249 |  | [246, 150, 130] | [250, 209, 171] | [254, 206, 166] | [236, 120, 103] | middels | 2019 |
| 250 |  | [244, 120, 104] | [238, 124, 106] | [248, 224, 204] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 251 |  | [188, 188, 192] | [180, 103, 85] | [236, 240, 240] | [243, 150, 132] | middels | 2019+kvartaltegning |
| 252 |  | [244, 120, 104] | [218, 111, 93] | [236, 240, 240] | [215, 170, 130] | middels | 2019+kvartaltegning |
| 255 |  | [246, 122, 106] | [254, 238, 180] | [254, 234, 174] | None | lav | 2019 |
| 256 |  | [246, 122, 106] | [218, 217, 218] | [236, 240, 240] | [119, 119, 117] | lav | 2019 |
| 257 |  | [188, 188, 192] | [67, 67, 65] | [236, 240, 240] | [180, 103, 85] | middels | 2019+kvartaltegning |
| 258 |  | [244, 120, 104] | [95, 92, 91] | [252, 188, 144] | [180, 103, 85] | høy | 2019+kvartaltegning |
| 259 |  | [188, 188, 192] | [240, 120, 103] | [236, 240, 240] | [222, 222, 221] | høy | 2019+kvartaltegning |
| 260 |  | [246, 122, 106] | [180, 103, 85] | [246, 150, 130] | [243, 150, 132] | middels | 2019+kvartaltegning |
| 261 |  | [244, 120, 104] | [237, 120, 103] | [252, 232, 172] | [237, 120, 103] | middels | 2019+kvartaltegning |
| 262 | Arnesgården | [246, 122, 106] | [237, 120, 103] | [252, 228, 156] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 263 |  | [214, 114, 98] | [216, 110, 94] | [254, 190, 146] | [220, 174, 133] | høy | 2019+kvartaltegning |
| 264 | Færgeporten | [244, 120, 104] | [255, 255, 255] | [244, 148, 128] | None | lav | 2019 |
| 265 | Kongeporten | [244, 120, 104] | [115, 151, 115] | [236, 240, 240] | None | lav | 2019 |
| 266 | Mellomporten | [246, 122, 106] | [89, 119, 91] | [246, 122, 106] | None | lav | 2019 |
| 305 |  | [246, 122, 106] | [179, 102, 84] | [238, 242, 242] | [197, 199, 198] | høy | 2019+kvartaltegning |
| 306 |  | [244, 120, 104] | [240, 120, 103] | [244, 148, 80] | [240, 120, 103] | middels | 2019 |
| 307 |  | [244, 120, 104] | [179, 102, 84] | [252, 228, 156] | None | lav | 2019 |
| 311 |  | [244, 120, 104] | [171, 82, 66] | [236, 240, 240] | [244, 150, 132] | høy | 2019+kvartaltegning |
| 313 |  | [190, 190, 194] | [119, 119, 117] | [254, 230, 158] | [180, 103, 85] | høy | 2019+kvartaltegning |
| 327 |  | [246, 122, 106] | [214, 202, 154] | [246, 122, 106] | None | lav | 2019 |
| 328 |  | [244, 120, 104] | [240, 120, 103] | [244, 148, 80] | [246, 244, 246] | middels | 2019 |
| 329 |  | [244, 120, 104] | [248, 194, 147] | [244, 148, 80] | [238, 120, 104] | middels | 2019 |
| 330 |  | [244, 120, 104] | [240, 120, 103] | [236, 240, 240] | [238, 120, 103] | middels | 2019+kvartaltegning |
| 331 |  | [244, 120, 104] | [179, 102, 84] | [236, 240, 240] | [255, 239, 182] | høy | 2019+kvartaltegning |
| 332 |  | [188, 188, 192] | [179, 102, 84] | [236, 240, 240] | [234, 120, 106] | middels | 2019 |
| 334 |  | [244, 120, 104] | [244, 244, 244] | [236, 240, 240] | [162, 162, 162] | middels | 2019 |
| 335 |  | [244, 120, 104] | [237, 120, 103] | [244, 148, 80] | [243, 243, 243] | middels | 2019 |
| 336 |  | [246, 122, 106] | [180, 103, 85] | [222, 210, 158] | [221, 174, 132] | middels | 2019 |
| 337 |  | [244, 120, 104] | [180, 103, 85] | [244, 148, 80] | [180, 103, 85] | middels | 2019+kvartaltegning |
| 338 |  | [244, 120, 104] | [249, 230, 214] | [248, 224, 204] | [131, 129, 124] | middels | 2019 |
| 339 |  | [188, 188, 192] | [214, 202, 154] | [252, 228, 156] | None | lav | 2019 |
| 340 |  | [244, 120, 104] | [179, 102, 84] | [250, 226, 206] | [232, 215, 199] | høy | 2019+kvartaltegning |
| 342 |  | [188, 188, 192] | [217, 110, 92] | [236, 240, 240] | [243, 244, 246] | middels | 2019 |
| 343 |  | [244, 120, 104] | [240, 120, 103] | [236, 240, 240] | [244, 159, 139] | middels | 2019 |
| 345 |  | [188, 188, 192] | [144, 86, 72] | [236, 240, 240] | [232, 215, 199] | middels | 2019+kvartaltegning |
| 346 |  | [244, 120, 104] | [237, 120, 103] | [246, 122, 106] | [180, 103, 85] | lav | 2019 |
| 347 |  | [244, 120, 104] | [240, 120, 103] | [248, 224, 204] | [234, 86, 86] | middels | 2019 |
| 348 |  | [244, 120, 104] | [240, 120, 103] | [236, 240, 240] | [163, 162, 163] | middels | 2019 |
| 350 |  | [244, 120, 104] | [237, 120, 103] | [244, 148, 80] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 351 |  | [188, 188, 192] | [186, 113, 96] | [236, 240, 240] | [198, 198, 198] | middels | 2019 |
| 352 |  | [188, 188, 192] | [179, 102, 84] | [244, 148, 80] | [179, 102, 84] | middels | 2019 |
| 353 |  | [128, 128, 132] | [119, 119, 117] | [236, 240, 240] | [218, 218, 218] | høy | 2019+kvartaltegning |
| 354 |  | [244, 120, 104] | [132, 134, 134] | [236, 240, 240] | [233, 212, 201] | høy | 2019+kvartaltegning |
| 355 |  | [188, 188, 192] | [240, 120, 103] | [236, 240, 240] | [248, 208, 173] | høy | 2019+kvartaltegning |
| 356 |  | [244, 120, 104] | [217, 110, 92] | [236, 240, 240] | [198, 197, 198] | middels | 2019 |
| 357 |  | [188, 188, 192] | [135, 135, 135] | [236, 240, 240] | [113, 114, 114] | middels | 2019 |
| 358 |  | [246, 122, 106] | [237, 120, 103] | [246, 150, 130] | [180, 104, 84] | middels | 2019 |
| 359 |  | [188, 188, 192] | [232, 215, 199] | [236, 240, 240] | [244, 244, 244] | middels | 2019 |
| 360 |  | [244, 120, 104] | [237, 120, 104] | [236, 240, 240] | [179, 102, 84] | høy | 2019+kvartaltegning |
| 361 |  | [214, 114, 98] | [244, 150, 77] | [250, 226, 206] | [232, 212, 199] | middels | 2019 |
| 363 |  | [244, 120, 104] | [133, 135, 134] | [252, 188, 144] | [232, 213, 200] | høy | 2019+kvartaltegning |
| 364 |  | [106, 110, 110] | [244, 244, 244] | [246, 150, 82] | [198, 198, 198] | middels | 2019 |
| 375 |  | [244, 120, 104] | [186, 113, 96] | [244, 148, 128] | [242, 243, 241] | middels | 2019 |
| 376 |  | [244, 120, 104] | [240, 120, 103] | [248, 224, 204] | [179, 102, 84] | høy | 2019+kvartaltegning |
| 377 |  | [244, 120, 104] | [179, 102, 84] | [252, 228, 156] | [243, 244, 244] | høy | 2019+kvartaltegning |
| 378 |  | [244, 120, 104] | [238, 124, 108] | [236, 240, 240] | [254, 245, 212] | høy | 2019+kvartaltegning |
| 379 |  | [244, 120, 104] | [240, 120, 103] | [252, 228, 156] | [146, 146, 146] | lav | 2019 |
| 380 |  | [188, 188, 192] | [199, 102, 86] | [236, 240, 240] | [198, 198, 198] | høy | 2019+kvartaltegning |
| 381 |  | [244, 120, 104] | [180, 103, 85] | [244, 148, 80] | [244, 150, 76] | høy | 2019+kvartaltegning |
| 382 |  | [244, 120, 104] | [217, 110, 92] | [236, 240, 240] | [198, 197, 198] | middels | 2019 |
| 384 |  | [246, 122, 106] | [237, 120, 103] | [246, 122, 106] | [196, 196, 194] | middels | 2019 |
| 385 |  | [150, 82, 70] | [180, 103, 85] | [246, 122, 106] | [255, 232, 162] | høy | 2019+kvartaltegning |
| 386 |  | [246, 122, 106] | [135, 135, 135] | [238, 242, 242] | [178, 102, 86] | middels | 2019 |
| 387 |  | [246, 122, 106] | [249, 195, 148] | [254, 190, 146] | None | lav | 2019 |
| 388 |  | [188, 188, 192] | [179, 102, 84] | [236, 240, 240] | [179, 102, 84] | middels | 2019 |
| 389 |  | [110, 114, 114] | [119, 119, 117] | [246, 150, 86] | [218, 217, 218] | middels | 2019 |
| 390 |  | [246, 122, 106] | [180, 103, 85] | [250, 226, 206] | [237, 120, 103] | høy | 2019+kvartaltegning |
| 393 |  | [246, 122, 106] | [237, 120, 103] | [246, 122, 106] | [243, 243, 243] | høy | 2019+kvartaltegning |
| 394 |  | [244, 120, 104] | [178, 102, 84] | [236, 240, 240] | [179, 102, 85] | lav | 2019 |
| 398 |  | [244, 120, 104] | [197, 198, 200] | [236, 240, 240] | [249, 195, 148] | middels | 2019 |
| 402 |  | [188, 188, 192] | [231, 213, 200] | [248, 224, 204] | [232, 212, 199] | middels | 2019 |
| 404 |  | [246, 122, 106] | [148, 148, 148] | [236, 240, 240] | None | lav | 2019 |
| 408 |  | [244, 120, 104] | [198, 198, 199] | [236, 240, 240] | [240, 121, 103] | høy | 2019+kvartaltegning |
| 438 | Kruttmagasinet | [244, 120, 104] | [198, 198, 198] | [252, 188, 144] | None | lav | 2019 |
| 439 |  | [244, 120, 104] | [179, 102, 84] | [252, 228, 156] | [255, 247, 226] | høy | 2019+kvartaltegning |
| 440 |  | [244, 120, 104] | [240, 120, 103] | [188, 220, 216] | [179, 102, 84] | middels | 2019 |

## Hva Vegar bør se på

1. Kontrollarket: stor sirkel = tak, liten = vegg, magenta ring = ikke funnet, oransje ring = lav sikkerhet. Nummer = byggindeks.
2. Paletten over: er dette fargene han vil ha i modellen? Klyngene ±8 kan slås sammen til faste palettverdier før registeret blir data/farger.json.
3. Avvikslista: der dagens verdi er en standardverdi og 2019 sier noe annet, bør 2019 vinne.