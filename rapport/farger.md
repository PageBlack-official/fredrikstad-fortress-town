# Fargeregister fra trykkfila 2015 — FORSLAG (ikke lagt inn)

Kilde: pdf/brosjyre.pdf side 1 (InDesign 2015), lest som vektor med PyMuPDF (metode A). Rasteret (pdftoppm) ble forkastet fordi fargene der avviker fra dagens palett (pdftoppm gjengir CMYK annerledes: taks (174,102,86) blir (171,84,76)); PyMuPDFs fyllfarger treffer dagens verdier innen ±3.

## Metode

1. Alle 12 030 fylte vektorflater på side 1 hentet ut (`page.get_drawings()`), 4 628 flater over 30 px² gjort om til shapely-polygoner i 300 dpi-piksler og rastrert til et etikettbilde (øverste flate per piksel; små mørke flater = vinduer/streker hoppet over).
2. Hvert hus’ fotavtrykk projisert med pdf/affin2.npy pluss lokal korreksjon fra de 28 parene tegnforklaringssirkel ↔ hus med nr (samme som kvartal/kobling.py, bare motsatt vei).
3. Fordi trykket er tegnet for hånd (bitmap-trace, 403 000 kurvesegmenter) ligger husene opptil 40–60 px unna det projiserte fotavtrykket. Hvert hus ble derfor flyttet lokalt (±48 px, pluss opp til 4·h px i høyden) til flest mulig rutenettpunkter i fotavtrykket lander på husflater (ikke plen, gate, vann, strek). Hus der under 35 % av fotavtrykket lander på husflate er merket «ikke i trykket».
4. Tak = vanligste husfarge i det innpassede fotavtrykket (sirklene i tegnforklaringen sitter på takene, så affin2 lander på takplanet). Taks = nest vanligste farge hvis den er samme kulør, mørkere og ≥12 % av punktene.
5. Vegg = for hver synlig kant (utovervendt normal nedover i bildet): gå nedover fra kanten, hopp over takfargene, ta første løp av annen husfarge. To retningsgrupper → lysest = vegg, mørkest = veggs (bare hvis samme kulør).

## Kalibrering mot husene som har veggs/taks i dag

- Tak: 111 av 197 hus treffer dagens tak/taks innen ±12 per kanal = **56 %** (62 % før kravet om samme kulør på skyggetonen).
- Vegg: 55 av 182 = **30 %**.
- **Kravet på 85 % er ikke nådd.** Hvorfor: trykket er ikke en projeksjon av OSM-fotavtrykkene, men en frihåndstegning som er bitmap-tracet; vinkler, lengder og plassering avviker per hus (se kontrollarket: f.eks. Kommandantgården nr 12 er tegnet som en L med annen vinkel). Et fotavtrykk som flyttes rett (translasjon) treffer da ofte nabohuset eller gata, og veggprøvene under kantene ender i nabohusets vegg. I tillegg er mange av dagens 276 «trykkfarger» standardverdier (145 hus har tak (244,120,104)), så kalibreringsmålet er selv delvis avledet. Takfargene for de store, frittliggende husene (Tøihuset, Infanterikasernen, Provianthuset, Hovedvakten, Bakeriet) treffer; feilene sitter i tette kvartaler med små hus.
- Det som trengs for å komme over 85 %: husvis innpassing med rotasjon/skalering (eller manuelle anker per kvartal, som kvartaltegningene allerede gir for 97 hus), ikke bare translasjon. Det er en 1–2 timers jobb, ikke 35 minutter.

## Antall

- Hus i modellen: 441 (9 skjult).
- Hus med farge funnet i trykket: 209 (sikkerhet høy 147, middels 58).
- Ikke i trykket: 232, hvorav 164 utenfor arket (gml=0, Isegran/Kongsten/utenfor vollene) og 59 innenfor vollene uten husflate der fotavtrykket lander (små uthus bak trær, eller feilplassert): 10, 12, 17, 28, 42, 43, 49, 53, 55, 56, 58, 62, 73, 76, 83, 89, 94, 100, 101, 104, 105, 111, 112, 116, 118, 119, 121, 124, 125, 129, 131, 133, 135, 137, 139, 141, 149, 151, 171, 181, 267, 277, 296, 297, 298, 365, 369, 371, 372, 401, 406, 411, 413, 416, 423, 426, 429, 431, 432.

## Palett i trykket (sammenslått innen ±8) — DETTE skal Vegar godkjenne

Takfarger (lys side):

- rgb(244, 123, 106) — 67 hus
- rgb(255, 255, 255) — 27 hus
- rgb(188, 190, 192) — 13 hus
- rgb(246, 147, 128) — 13 hus
- rgb(239, 240, 240) — 12 hus
- rgb(217, 110, 94) — 12 hus
- rgb(173, 100, 86) — 9 hus
- rgb(226, 204, 187) — 7 hus
- rgb(247, 150, 84) — 7 hus
- rgb(250, 188, 142) — 5 hus
- rgb(128, 130, 133) — 4 hus
- rgb(178, 110, 95) — 3 hus
- rgb(249, 224, 204) — 3 hus
- rgb(218, 219, 218) — 3 hus
- rgb(215, 167, 129) — 3 hus
- rgb(209, 211, 211) — 3 hus
- rgb(140, 142, 144) — 2 hus
- rgb(205, 194, 150) — 2 hus
- rgb(105, 109, 110) — 2 hus
- rgb(212, 183, 170) — 1 hus
- rgb(189, 124, 112) — 1 hus
- rgb(199, 200, 202) — 1 hus
- rgb(222, 206, 154) — 1 hus
- rgb(251, 224, 171) — 1 hus
- rgb(237, 213, 196) — 1 hus
- rgb(156, 157, 158) — 1 hus
- rgb(253, 203, 165) — 1 hus
- rgb(254, 243, 206) — 1 hus
- rgb(253, 235, 174) — 1 hus
- rgb(253, 229, 157) — 1 hus
- rgb(201, 107, 94) — 1 hus

Takfarger (skyggeside):

- rgb(173, 100, 86) — 56 hus
- rgb(128, 130, 133) — 14 hus
- rgb(105, 109, 110) — 10 hus
- rgb(217, 110, 94) — 10 hus
- rgb(115, 116, 119) — 5 hus
- rgb(135, 81, 70) — 4 hus
- rgb(218, 165, 125) — 2 hus
- rgb(178, 110, 95) — 2 hus
- rgb(164, 84, 72) — 2 hus
- rgb(197, 99, 86) — 2 hus
- rgb(226, 204, 187) — 2 hus
- rgb(249, 224, 204) — 1 hus
- rgb(239, 240, 240) — 1 hus
- rgb(218, 219, 220) — 1 hus
- rgb(244, 123, 106) — 1 hus
- rgb(193, 121, 107) — 1 hus
- rgb(241, 95, 93) — 1 hus
- rgb(188, 190, 192) — 1 hus
- rgb(141, 143, 143) — 1 hus
- rgb(250, 188, 142) — 1 hus
- rgb(205, 194, 150) — 1 hus
- rgb(253, 203, 165) — 1 hus

Veggfarger (lys side):

- rgb(239, 240, 240) — 31 hus
- rgb(255, 255, 255) — 26 hus
- rgb(188, 190, 192) — 23 hus
- rgb(244, 123, 106) — 17 hus
- rgb(252, 190, 143) — 13 hus
- rgb(246, 148, 129) — 13 hus
- rgb(217, 110, 94) — 7 hus
- rgb(249, 224, 204) — 6 hus
- rgb(173, 100, 86) — 6 hus
- rgb(253, 203, 165) — 6 hus
- rgb(222, 206, 154) — 5 hus
- rgb(226, 205, 190) — 5 hus
- rgb(253, 235, 174) — 3 hus
- rgb(152, 154, 157) — 3 hus
- rgb(247, 171, 157) — 3 hus
- rgb(253, 229, 157) — 3 hus
- rgb(218, 165, 125) — 3 hus
- rgb(218, 219, 220) — 3 hus
- rgb(209, 211, 211) — 3 hus
- rgb(237, 213, 196) — 2 hus
- rgb(222, 242, 246) — 2 hus
- rgb(254, 243, 206) — 2 hus
- rgb(251, 224, 171) — 1 hus
- rgb(247, 150, 82) — 1 hus
- rgb(178, 110, 95) — 1 hus
- rgb(165, 167, 170) — 1 hus
- rgb(197, 99, 86) — 1 hus
- rgb(195, 181, 170) — 1 hus
- rgb(215, 193, 119) — 1 hus
- rgb(205, 194, 150) — 1 hus
- rgb(241, 95, 93) — 1 hus
- rgb(135, 81, 70) — 1 hus
- rgb(150, 79, 67) — 1 hus
- rgb(202, 129, 72) — 1 hus

Veggfarger (skyggeside):

- rgb(188, 190, 192) — 14 hus
- rgb(173, 102, 88) — 8 hus
- rgb(215, 167, 129) — 6 hus
- rgb(128, 130, 133) — 4 hus
- rgb(226, 204, 187) — 3 hus
- rgb(222, 206, 154) — 2 hus
- rgb(115, 116, 119) — 2 hus
- rgb(135, 81, 70) — 2 hus
- rgb(237, 238, 238) — 2 hus
- rgb(217, 110, 94) — 2 hus
- rgb(189, 124, 112) — 1 hus
- rgb(250, 188, 142) — 1 hus
- rgb(242, 123, 106) — 1 hus
- rgb(195, 181, 170) — 1 hus
- rgb(164, 84, 72) — 1 hus
- rgb(152, 154, 157) — 1 hus
- rgb(237, 213, 196) — 1 hus
- rgb(249, 224, 204) — 1 hus
- rgb(246, 147, 128) — 1 hus

Merk: paletten med 1–3 hus per farge er støy fra feilinnpassing (nabohus, vinduer, skilt). De store klyngene er trykkets reelle palett: rød tak (244,123,106)/(173,100,86), grått tak (188,190,192)/(128,130,133), vegger hvit (239,240,240)/(255,255,255), oransje (252,190,143)/(218,165,125), kremgul (252,230,157), lys rosa (249,224,204), laks (246,148,129), teglrød (202,129,72).

## Hus der forslaget avviker fra dagens bygg.vegg/tak med > 20 per kanal (284)

| idx | navn | felt | dagens | forslag | sikkerhet |
|---|---|---|---|---|---|
| 2 | Det grundmurede provianthus | vegg | [248, 224, 204] | [255, 255, 255] | høy |
| 4 | Kirken | vegg | [238, 242, 242] | [194, 196, 198] | middels |
| 5 | Tøihuset | vegg | [252, 188, 144] | [255, 255, 255] | høy |
| 6 | Labratoriet | vegg | [254, 190, 146] | [246, 147, 128] | middels |
| 7 | Brannbatteriet | tak | [244, 120, 104] | [212, 183, 170] | middels |
| 7 | Brannbatteriet | vegg | [252, 188, 144] | [253, 253, 254] | middels |
| 8 | Binggården | tak | [188, 188, 192] | [239, 240, 240] | høy |
| 8 | Binggården | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 9 | Artillerigården | vegg | [246, 150, 130] | [252, 190, 143] | lav |
| 11 | Kiørboegården | tak | [128, 128, 132] | [188, 190, 189] | høy |
| 13 | Brannstasjon - uthus til Infanterikasernen | tak | [246, 122, 106] | [189, 124, 112] | høy |
| 13 | Brannstasjon - uthus til Infanterikasernen | vegg | [246, 150, 130] | [255, 255, 255] | høy |
| 15 | Undervisningsbrakke | tak | [246, 122, 106] | [255, 255, 255] | høy |
| 16 | Artillerismiens uthus | tak | [246, 122, 106] | [255, 255, 255] | middels |
| 16 | Artillerismiens uthus | vegg | [252, 188, 144] | [217, 110, 94] | middels |
| 18 | Voldporten med vaktstuen | tak | [246, 122, 106] | [255, 255, 255] | lav |
| 19 | Den gamle spisesal | tak | [246, 122, 106] | [247, 150, 82] | middels |
| 19 | Den gamle spisesal | vegg | [236, 240, 240] | [188, 190, 192] | middels |
| 20 | Kjørbogårdens sidebygning | tak | [190, 190, 194] | [123, 127, 128] | høy |
| 21 | Kommandantgården | tak | [246, 122, 106] | [204, 204, 204] | høy |
| 22 | Offisersvakten | tak | [246, 122, 106] | [199, 200, 202] | høy |
| 24 | Ekserserhuset | vegg | [244, 148, 80] | [255, 255, 255] | høy |
| 25 | Kommisjonsgården | tak | [188, 188, 192] | [253, 253, 253] | middels |
| 25 | Kommisjonsgården | vegg | [252, 228, 156] | [173, 100, 86] | middels |
| 26 | Voldportravelinet | tak | [244, 120, 104] | [255, 255, 255] | middels |
| 27 | Marketenteriet | tak | [244, 120, 104] | [252, 190, 143] | middels |
| 27 | Marketenteriet | vegg | [252, 188, 144] | [255, 255, 255] | middels |
| 29 | Sprøytehuset / Proviantboden | tak | [244, 120, 104] | [255, 255, 255] | middels |
| 29 | Sprøytehuset / Proviantboden | vegg | [236, 240, 240] | [244, 123, 106] | middels |
| 30 | Artillerismien | tak | [244, 120, 104] | [255, 255, 255] | høy |
| 30 | Artillerismien | vegg | [248, 224, 204] | [218, 165, 125] | høy |
| 99 | Annekset | tak | [244, 120, 104] | [255, 255, 255] | middels |
| 102 |  | tak | [244, 120, 104] | [255, 255, 255] | høy |
| 102 |  | vegg | [252, 188, 144] | [239, 240, 240] | høy |
| 107 | Det gamle raadhus | tak | [246, 122, 106] | [255, 255, 255] | høy |
| 107 | Det gamle raadhus | vegg | [254, 234, 174] | [252, 190, 143] | høy |
| 108 |  | vegg | [250, 226, 206] | [188, 190, 192] | middels |
| 109 |  | tak | [246, 122, 106] | [255, 255, 255] | middels |
| 109 |  | vegg | [254, 190, 146] | [218, 165, 125] | middels |
| 110 |  | vegg | [254, 234, 174] | [239, 240, 240] | middels |
| 152 |  | tak | [238, 242, 242] | [244, 123, 106] | middels |
| 152 |  | vegg | [246, 122, 106] | [239, 240, 240] | middels |
| 154 |  | vegg | [236, 240, 240] | [246, 148, 129] | høy |
| 155 |  | tak | [246, 122, 106] | [255, 255, 255] | høy |
| 155 |  | vegg | [238, 242, 242] | [244, 123, 106] | høy |
| 156 |  | vegg | [236, 240, 240] | [249, 224, 204] | høy |
| 157 |  | tak | [246, 122, 106] | [188, 190, 192] | høy |
| 158 |  | tak | [246, 122, 106] | [246, 147, 128] | middels |
| 158 |  | vegg | [236, 240, 240] | [188, 190, 192] | middels |
| 159 | Skolebygningen | vegg | [252, 228, 156] | [239, 240, 240] | middels |
| 160 |  | tak | [246, 150, 130] | [188, 190, 192] | middels |
| 160 |  | vegg | [244, 148, 80] | [209, 211, 212] | middels |
| 162 |  | tak | [190, 190, 194] | [255, 255, 255] | høy |
| 162 |  | vegg | [248, 224, 204] | [173, 100, 86] | høy |
| 163 |  | tak | [190, 190, 194] | [244, 123, 106] | middels |
| 163 |  | vegg | [252, 228, 156] | [239, 240, 240] | middels |
| 164 | Muldvadgården | tak | [246, 122, 106] | [222, 206, 154] | høy |
| 165 |  | tak | [218, 110, 94] | [239, 240, 240] | høy |
| 165 |  | vegg | [236, 240, 240] | [244, 123, 106] | høy |
| 166 |  | vegg | [236, 240, 240] | [218, 219, 220] | middels |
| 168 |  | tak | [190, 190, 194] | [244, 123, 106] | middels |
| 168 |  | vegg | [246, 150, 130] | [249, 224, 204] | middels |
| 169 |  | tak | [246, 122, 106] | [239, 240, 240] | høy |
| 169 |  | vegg | [238, 242, 242] | [244, 123, 106] | høy |
| 170 |  | tak | [246, 122, 106] | [226, 204, 187] | middels |
| 170 |  | vegg | [250, 226, 206] | [252, 190, 143] | middels |
| 172 | Salamandergården | tak | [246, 122, 106] | [252, 190, 143] | høy |
| 172 | Salamandergården | vegg | [254, 190, 146] | [222, 206, 154] | høy |
| 173 |  | tak | [244, 120, 104] | [217, 110, 94] | middels |
| 174 |  | tak | [246, 122, 106] | [255, 255, 255] | høy |
| 174 |  | vegg | [250, 226, 206] | [217, 110, 94] | høy |
| 176 |  | tak | [246, 122, 106] | [255, 255, 255] | middels |
| 178 |  | tak | [246, 122, 106] | [173, 100, 86] | høy |
| 178 |  | vegg | [254, 230, 158] | [237, 213, 196] | høy |
| 179 |  | vegg | [236, 240, 240] | [252, 190, 143] | høy |
| 182 | Balaklava | vegg | [250, 226, 206] | [188, 190, 192] | høy |
| 183 |  | tak | [188, 188, 192] | [178, 110, 95] | høy |
| 183 |  | vegg | [236, 240, 240] | [218, 219, 218] | høy |
| 184 | Rosinggården | tak | [244, 120, 104] | [188, 190, 192] | høy |
| 184 | Rosinggården | vegg | [188, 220, 216] | [251, 224, 171] | høy |
| 185 |  | vegg | [218, 110, 94] | [251, 202, 163] | høy |
| 186 |  | tak | [246, 150, 130] | [244, 123, 106] | høy |
| 186 |  | vegg | [246, 122, 106] | [246, 147, 128] | høy |
| 187 |  | vegg | [104, 168, 128] | [188, 190, 192] | middels |
| 188 |  | vegg | [236, 240, 240] | [247, 150, 82] | høy |
| 190 |  | tak | [188, 188, 192] | [255, 255, 255] | høy |
| 190 |  | vegg | [236, 240, 240] | [252, 190, 143] | høy |
| 191 |  | tak | [244, 120, 104] | [246, 147, 128] | høy |
| 191 |  | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 192 |  | tak | [244, 120, 104] | [217, 110, 94] | høy |
| 192 |  | vegg | [248, 224, 204] | [239, 240, 240] | høy |
| 193 | Bullgården | tak | [188, 188, 192] | [239, 240, 240] | middels |
| 193 | Bullgården | vegg | [236, 240, 240] | [244, 123, 106] | middels |
| 194 |  | tak | [244, 120, 104] | [251, 224, 171] | middels |
| 194 |  | vegg | [188, 220, 216] | [152, 154, 157] | middels |
| 196 |  | tak | [218, 110, 94] | [255, 255, 255] | høy |
| 196 |  | vegg | [250, 238, 226] | [217, 110, 94] | høy |
| 197 | Feiergården | vegg | [236, 240, 240] | [218, 219, 220] | høy |
| 199 |  | tak | [246, 122, 106] | [226, 204, 187] | middels |
| 200 |  | tak | [244, 120, 104] | [247, 154, 135] | høy |
| 201 |  | tak | [246, 122, 106] | [237, 213, 196] | høy |
| 203 |  | tak | [244, 120, 104] | [247, 150, 82] | høy |
| 203 |  | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 204 | Prestegården | tak | [246, 122, 106] | [218, 165, 125] | høy |
| 205 |  | tak | [244, 120, 104] | [239, 240, 240] | høy |
| 205 |  | vegg | [188, 220, 216] | [246, 147, 128] | høy |
| 206 |  | vegg | [244, 148, 128] | [255, 255, 255] | middels |
| 207 |  | tak | [244, 120, 104] | [217, 110, 94] | høy |
| 207 |  | vegg | [236, 240, 240] | [244, 123, 106] | høy |
| 208 |  | tak | [188, 188, 192] | [255, 255, 255] | middels |
| 208 |  | vegg | [236, 240, 240] | [173, 100, 86] | middels |
| 209 |  | vegg | [238, 242, 242] | [251, 202, 163] | høy |
| 210 |  | vegg | [194, 122, 110] | [239, 240, 240] | høy |
| 211 |  | tak | [188, 188, 192] | [244, 123, 106] | middels |
| 212 |  | tak | [128, 128, 132] | [249, 224, 204] | høy |
| 212 |  | vegg | [236, 240, 240] | [217, 110, 94] | høy |
| 213 |  | vegg | [252, 228, 156] | [255, 255, 255] | høy |
| 214 |  | tak | [246, 150, 82] | [246, 147, 128] | høy |
| 214 |  | vegg | [246, 122, 106] | [188, 190, 192] | høy |
| 215 |  | tak | [244, 120, 104] | [255, 255, 255] | høy |
| 215 |  | vegg | [236, 240, 240] | [178, 110, 95] | høy |
| 216 |  | tak | [246, 122, 106] | [226, 204, 187] | middels |
| 216 |  | vegg | [250, 226, 206] | [188, 190, 192] | middels |
| 217 |  | vegg | [218, 110, 94] | [188, 190, 192] | høy |
| 218 |  | tak | [188, 188, 192] | [217, 110, 94] | høy |
| 218 |  | vegg | [236, 240, 240] | [165, 167, 170] | høy |
| 219 |  | tak | [244, 120, 104] | [218, 219, 218] | høy |
| 219 |  | vegg | [236, 240, 240] | [197, 99, 86] | høy |
| 220 |  | tak | [246, 122, 106] | [247, 150, 82] | middels |
| 220 |  | vegg | [246, 150, 82] | [226, 204, 187] | middels |
| 221 | Gamlebyen modelljernbanesenter | tak | [244, 120, 104] | [255, 255, 255] | høy |
| 222 |  | tak | [218, 110, 94] | [255, 255, 255] | høy |
| 223 |  | vegg | [250, 226, 206] | [239, 240, 240] | middels |
| 224 |  | vegg | [250, 226, 170] | [152, 154, 157] | høy |
| 225 |  | tak | [188, 188, 192] | [128, 130, 133] | høy |
| 228 |  | vegg | [252, 188, 144] | [215, 167, 129] | høy |
| 229 |  | vegg | [246, 150, 82] | [237, 238, 238] | høy |
| 230 | Det nye rådhus | tak | [244, 120, 104] | [215, 167, 129] | høy |
| 230 | Det nye rådhus | vegg | [252, 188, 144] | [255, 255, 255] | høy |
| 231 | Sindinggården | tak | [244, 120, 104] | [215, 167, 129] | høy |
| 231 | Sindinggården | vegg | [236, 240, 240] | [246, 148, 129] | høy |
| 232 |  | tak | [246, 122, 106] | [246, 148, 129] | høy |
| 233 |  | tak | [246, 122, 106] | [250, 188, 142] | høy |
| 235 |  | vegg | [244, 148, 128] | [247, 171, 157] | høy |
| 236 |  | tak | [188, 188, 192] | [242, 123, 106] | middels |
| 236 |  | vegg | [236, 240, 240] | [246, 148, 129] | middels |
| 237 |  | tak | [246, 122, 106] | [156, 157, 158] | høy |
| 237 |  | vegg | [238, 238, 238] | [188, 190, 189] | høy |
| 238 |  | tak | [246, 122, 106] | [173, 102, 88] | høy |
| 239 |  | tak | [246, 122, 106] | [247, 150, 84] | høy |
| 239 |  | vegg | [246, 150, 86] | [250, 188, 142] | høy |
| 240 | Dunkejongården | tak | [246, 122, 106] | [173, 102, 88] | høy |
| 241 |  | vegg | [244, 148, 80] | [237, 238, 238] | høy |
| 242 |  | vegg | [236, 240, 240] | [254, 243, 206] | høy |
| 243 |  | vegg | [236, 240, 240] | [173, 102, 88] | høy |
| 244 |  | vegg | [246, 150, 86] | [255, 255, 255] | høy |
| 245 |  | tak | [244, 120, 104] | [247, 150, 84] | høy |
| 245 |  | vegg | [248, 224, 204] | [253, 203, 165] | høy |
| 246 |  | vegg | [236, 240, 240] | [195, 181, 170] | høy |
| 247 |  | tak | [246, 122, 106] | [246, 148, 129] | høy |
| 247 |  | vegg | [246, 150, 130] | [242, 123, 106] | høy |
| 248 | Vennehaabet | tak | [244, 120, 104] | [237, 238, 238] | høy |
| 248 | Vennehaabet | vegg | [244, 148, 80] | [173, 102, 88] | høy |
| 249 |  | tak | [246, 150, 130] | [253, 203, 165] | høy |
| 249 |  | vegg | [254, 206, 166] | [246, 148, 129] | høy |
| 250 |  | tak | [244, 120, 104] | [254, 243, 206] | høy |
| 250 |  | vegg | [248, 224, 204] | [244, 130, 112] | høy |
| 251 |  | tak | [188, 188, 192] | [173, 100, 86] | høy |
| 251 |  | vegg | [236, 240, 240] | [215, 193, 119] | høy |
| 252 |  | vegg | [236, 240, 240] | [250, 188, 142] | høy |
| 253 |  | tak | [246, 122, 106] | [214, 113, 98] | middels |
| 253 |  | vegg | [254, 206, 166] | [226, 205, 190] | middels |
| 255 |  | tak | [246, 122, 106] | [253, 235, 174] | høy |
| 255 |  | vegg | [254, 234, 174] | [246, 148, 129] | høy |
| 256 |  | tak | [246, 122, 106] | [209, 211, 211] | middels |
| 256 |  | vegg | [236, 240, 240] | [242, 123, 106] | middels |
| 257 |  | tak | [188, 188, 192] | [242, 123, 106] | middels |
| 257 |  | vegg | [236, 240, 240] | [226, 205, 190] | middels |
| 258 |  | tak | [244, 120, 104] | [226, 205, 190] | middels |
| 258 |  | vegg | [252, 188, 144] | [214, 113, 98] | middels |
| 259 |  | tak | [188, 188, 192] | [213, 215, 216] | høy |
| 259 |  | vegg | [236, 240, 240] | [190, 192, 194] | høy |
| 260 |  | tak | [246, 122, 106] | [246, 148, 129] | middels |
| 261 |  | vegg | [252, 232, 172] | [205, 194, 150] | middels |
| 262 | Arnesgården | vegg | [252, 228, 156] | [252, 236, 206] | høy |
| 263 |  | tak | [214, 114, 98] | [237, 238, 238] | middels |
| 263 |  | vegg | [254, 190, 146] | [242, 123, 106] | middels |
| 264 | Færgeporten | tak | [244, 120, 104] | [255, 255, 255] | middels |
| 265 | Kongeporten | tak | [244, 120, 104] | [255, 255, 255] | lav |
| 266 | Mellomporten | tak | [246, 122, 106] | [239, 240, 240] | middels |
| 305 |  | vegg | [238, 242, 242] | [188, 190, 192] | høy |
| 306 |  | vegg | [244, 148, 80] | [188, 190, 192] | høy |
| 307 |  | tak | [244, 120, 104] | [188, 190, 192] | høy |
| 307 |  | vegg | [252, 228, 156] | [239, 240, 240] | høy |
| 311 |  | tak | [244, 120, 104] | [246, 147, 128] | høy |
| 311 |  | vegg | [236, 240, 240] | [173, 100, 86] | høy |
| 313 |  | vegg | [254, 230, 158] | [255, 255, 255] | høy |
| 327 |  | tak | [246, 122, 106] | [205, 194, 150] | middels |
| 328 |  | vegg | [244, 148, 80] | [252, 190, 143] | høy |
| 329 |  | tak | [244, 120, 104] | [250, 188, 142] | høy |
| 329 |  | vegg | [244, 148, 80] | [242, 123, 106] | høy |
| 330 |  | tak | [244, 120, 104] | [239, 240, 240] | høy |
| 332 |  | tak | [188, 188, 192] | [244, 123, 106] | høy |
| 332 |  | vegg | [236, 240, 240] | [249, 224, 204] | høy |
| 334 |  | tak | [244, 120, 104] | [239, 240, 240] | høy |
| 334 |  | vegg | [236, 240, 240] | [152, 154, 157] | høy |
| 335 |  | vegg | [244, 148, 80] | [237, 238, 238] | høy |
| 336 |  | tak | [246, 122, 106] | [246, 148, 129] | høy |
| 337 |  | tak | [244, 120, 104] | [246, 148, 129] | høy |
| 337 |  | vegg | [244, 148, 80] | [221, 207, 158] | høy |
| 338 |  | tak | [244, 120, 104] | [249, 224, 204] | høy |
| 338 |  | vegg | [248, 224, 204] | [244, 123, 106] | høy |
| 339 |  | tak | [188, 188, 192] | [205, 194, 150] | middels |
| 340 |  | tak | [244, 120, 104] | [173, 100, 86] | høy |
| 340 |  | vegg | [250, 226, 206] | [226, 204, 187] | høy |
| 342 |  | tak | [188, 188, 192] | [217, 110, 94] | høy |
| 343 |  | vegg | [236, 240, 240] | [247, 154, 135] | høy |
| 344 |  | tak | [244, 120, 104] | [217, 110, 94] | høy |
| 345 |  | tak | [188, 188, 192] | [217, 110, 94] | høy |
| 346 |  | vegg | [246, 122, 106] | [247, 171, 157] | middels |
| 347 |  | vegg | [248, 224, 204] | [241, 95, 93] | høy |
| 350 |  | tak | [244, 120, 104] | [247, 150, 84] | middels |
| 350 |  | vegg | [244, 148, 80] | [250, 188, 142] | middels |
| 351 |  | tak | [188, 188, 192] | [218, 219, 218] | høy |
| 351 |  | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 352 |  | tak | [188, 188, 192] | [173, 100, 86] | høy |
| 352 |  | vegg | [244, 148, 80] | [188, 190, 192] | høy |
| 353 |  | tak | [128, 128, 132] | [209, 211, 211] | middels |
| 354 |  | tak | [244, 120, 104] | [226, 205, 190] | høy |
| 354 |  | vegg | [236, 240, 240] | [242, 123, 106] | høy |
| 355 |  | tak | [188, 188, 192] | [217, 110, 94] | middels |
| 355 |  | vegg | [236, 240, 240] | [188, 190, 192] | middels |
| 356 |  | tak | [244, 120, 104] | [217, 110, 94] | høy |
| 356 |  | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 357 |  | tak | [188, 188, 192] | [128, 130, 133] | høy |
| 357 |  | vegg | [236, 240, 240] | [135, 81, 70] | høy |
| 358 |  | vegg | [246, 150, 130] | [253, 203, 165] | høy |
| 359 |  | tak | [188, 188, 192] | [226, 204, 187] | høy |
| 360 |  | vegg | [236, 240, 240] | [249, 224, 204] | høy |
| 361 |  | tak | [214, 114, 98] | [247, 150, 84] | høy |
| 361 |  | vegg | [250, 226, 206] | [209, 211, 211] | høy |
| 363 |  | tak | [244, 120, 104] | [188, 190, 189] | høy |
| 363 |  | vegg | [252, 188, 144] | [226, 205, 190] | høy |
| 364 |  | tak | [106, 110, 110] | [239, 240, 240] | høy |
| 364 |  | vegg | [246, 150, 82] | [188, 190, 192] | høy |
| 375 |  | tak | [244, 120, 104] | [178, 110, 95] | høy |
| 375 |  | vegg | [244, 148, 128] | [236, 237, 235] | høy |
| 376 |  | tak | [244, 120, 104] | [239, 240, 240] | høy |
| 377 |  | tak | [244, 120, 104] | [173, 100, 86] | høy |
| 377 |  | vegg | [252, 228, 156] | [222, 206, 154] | høy |
| 378 |  | vegg | [236, 240, 240] | [247, 171, 157] | høy |
| 379 |  | vegg | [252, 228, 156] | [255, 255, 255] | middels |
| 381 |  | tak | [244, 120, 104] | [250, 188, 142] | middels |
| 381 |  | vegg | [244, 148, 80] | [253, 203, 165] | middels |
| 382 |  | tak | [244, 120, 104] | [255, 255, 255] | høy |
| 382 |  | vegg | [236, 240, 240] | [188, 190, 192] | høy |
| 383 |  | vegg | [250, 226, 206] | [255, 255, 255] | middels |
| 384 |  | vegg | [246, 122, 106] | [253, 229, 157] | høy |
| 385 |  | tak | [150, 82, 70] | [253, 229, 157] | høy |
| 385 |  | vegg | [246, 122, 106] | [150, 79, 67] | høy |
| 386 |  | tak | [246, 122, 106] | [128, 130, 133] | høy |
| 386 |  | vegg | [238, 242, 242] | [188, 190, 192] | høy |
| 387 |  | tak | [246, 122, 106] | [178, 110, 95] | høy |
| 387 |  | vegg | [254, 190, 146] | [255, 255, 255] | høy |
| 388 |  | tak | [188, 188, 192] | [173, 100, 86] | høy |
| 388 |  | vegg | [236, 240, 240] | [244, 123, 106] | høy |
| 389 |  | vegg | [246, 150, 86] | [209, 211, 211] | høy |
| 390 |  | tak | [246, 122, 106] | [249, 224, 204] | høy |
| 390 |  | vegg | [250, 226, 206] | [242, 123, 106] | høy |
| 393 |  | tak | [246, 122, 106] | [201, 107, 94] | høy |
| 393 |  | vegg | [246, 122, 106] | [202, 129, 72] | høy |
| 394 |  | tak | [244, 120, 104] | [173, 100, 86] | middels |
| 398 |  | tak | [244, 120, 104] | [188, 190, 192] | høy |
| 398 |  | vegg | [236, 240, 240] | [252, 190, 143] | høy |
| 402 |  | tak | [188, 188, 192] | [226, 205, 190] | høy |
| 402 |  | vegg | [248, 224, 204] | [214, 113, 98] | høy |
| 404 |  | tak | [246, 122, 106] | [140, 142, 144] | høy |
| 404 |  | vegg | [236, 240, 240] | [222, 206, 154] | høy |
| 408 |  | tak | [244, 120, 104] | [253, 253, 253] | høy |
| 408 |  | vegg | [236, 240, 240] | [244, 123, 106] | høy |
| 438 | Kruttmagasinet | tak | [244, 120, 104] | [255, 255, 255] | middels |
| 438 | Kruttmagasinet | vegg | [252, 188, 144] | [239, 240, 240] | middels |
| 439 |  | vegg | [252, 228, 156] | [222, 242, 246] | høy |
| 440 |  | vegg | [188, 220, 216] | [222, 242, 246] | høy |

Filene: soc/rapport/farger.forslag.json (per hus), soc/rapport/farger-kontrollark.png (samplepunkter i forslagets farge). Koden: soc/rapport/_farger/kjor.py og felles.py. Ingenting i soc/src eller soc/data er endret.
Merk om px i forslaget: punktet er tyngdepunktet i det innpassede fotavtrykket; for U-formede hus (Tøihuset) ligger det i gårdsrommet, fargen er likevel lest i husflatene rundt.
