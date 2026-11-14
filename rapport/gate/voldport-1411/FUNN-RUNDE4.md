# FUNN runde 4 (Studio, 14.11.2026 kveld) — motoren, billig

Vegar 14.11 20:32: «Kjør, men gjør det billig.» Oppskrift: `RUNDE4-MOTOR.md`. Én runde, ingen SV-henting,
ingen ny datalesing. Gren `gate/voldport-1411`. **IKKE publisert.**

De fire feilene fra FUNN-RUNDE3C «render-pipeline-hull» er rettet i tegnemotoren (`src/05`, `src/07`).
Bevis med FØR/ETTER på 6 faste standpunkt i `rapport/gate/voldport-1411/r4/{for,etter}/` (1280×720, samme kamera).

## Pkt 1+2 — lyse vegger blå / fargede valmtak grå (globalt, `src/05_bygg.js`, `mat()`)
Samme årsak: skyggetonen på fasader og tak ble kjølt for hardt. `KALD`-tonen (b=1,07) + at skyggetonen
kuttes kjøligere i rødt (0,72) enn i blått/grønt (0,80) gjorde at **lyse vegger tippet blå** i skyggen og
**fargede valmtak (halvbelyste himmelvendte flater) vasket mot grå**.

Rettelse (minst mulig, bare hus-materialet — bakkens kastskygge i `medSkygge` er urørt):
- `KALD2 = mix(1, KALD, 0.40)` på vegger, `0.16` på himmelvendte tak-flater (mildere kjøling der valmen fanger lys).
- Lite rødløft (opptil +6 %) på de **lyse** skyggetonene, som motvirker rødkuttet; mørke flater beholder den kjølige skyggen.

**Bevis (for→etter, >6/255):**

| standpunkt | endret px | dR | dB |
|---|---|---|---|
| 1 Voldportgaten 75 krysset | 6,6 % | +9,6 | −4,1 |
| 2 Therese M | 13,7 % | +9,9 | −4,3 |
| 3 Torvet | 6,2 % | +9,4 | −3,5 |
| 4 Kirkegaten | 2,2 % | +9,0 | −3,6 |
| 5 Raadhusgaten | 8,0 % | +9,5 | −4,0 |
| 6 Tøihuset | 1,7 % | +7,3 | −3,2 |

Retning riktig overalt: rødt opp, blått ned i skyggen. **Rendringen er deterministisk** (samme bygg rendret to
ganger = 0,00 % diff), så hver endrede piksel er ekte. Endringen ligger per konstruksjon bare i `mat()`
(vegg/tak); bakke (`medSkygge`), trær (matcap), himmel (bakgrunn) og vinduer (`vindMat`, se under) rører jeg
ikke. Diff-heatmap (`r4/diff-*.png`) bekrefter: gate/bakke/himmel er svarte (uendret), bare vegg/tak-flater lyser.
Kravet «< 1 % diff utenfor målflatene» er oppfylt — ingen lekkasje til ikke-bygg-flater.
(De grå takene som står igjen er grå i dataene — ekte gråtak. Rettingen varmer **skyggesiden** av fargede tak,
som er alt den globale motoren kan/bør gjøre. Jf. [[verifiser-render-ikke-kode]].)

## Pkt 3 — foring druknet mot glasset (OPT-IN, `src/07`)
Når et vindu-element har egen farge (`v[12]`, f.eks. `#4a342c` på 75s vegg5 2.etg) tegnes smyget nå **bredere
(0,16 mot 0,08) og mørkere/mettet** (`pf*0.42 → pf*0.80`) så den mørke brune foringen står mot det mørke glasset.
Flagget bæres i aInfo.w (+1000) så **vinduer uten egen farge tegnes nøyaktig som før** — ingen regresjon.

## Pkt 4 — tospeils fantes ikke som sprosse-modus (OPT-IN, `src/07`)
Ny `spross 3`: full loddrett midtpost, **ingen tverrpost (losholt)** → to høye ruter. Seks-rute (`spross<1,5`) og
T-post (`spross 2`) er uendret. Verifisert i render: `r4/test-tospeils-75b.png` + `r4/crop-tospeils.png` viser
75s vegg5 2.etg med én loddrett post, ingen losholt, og den brune foringen rundt.

## «Etterpå» gjort
- **Spross 3 satt** på 75s 6 vegg5 2.etg-vinduer (z≈5,25, normal 0,9163/−0,4005, idx 31–36 i begge
  rettelser-containere for bnr-193867928) — samme vegg som 1.etg-glassfasaden. Foring `#4a342c` stod der alt.
  **NB identitet:** FUNN-RUNDE3C skrev «8 vegg5-vinduer», men vegg5-fasaden (den med glassbutikken i 1.etg) har
  6 vinduer i 2.etg i dataene; 8-gruppa (idx 43–50, z≈5,30) er en **annen vegg** (normal 0,907/−0,422). Jeg satte
  de 6 på vegg5. Hvis SV egentlig viser tospeils på den andre veggen også, er det en ettretting — flagget til CEO.

## Regler (kjørt én gang, ikke i løkke)
`13 OK · 17 OK · 42 OK · 45 OK · 48 OK`. **22_flyt FEIL**, men de to røde linjene er introen (kamera-
flythrough + uskarphet-uttoning) — **identisk rød på ren HEAD** (verifisert med stash + rebuild), i kode jeg
ikke rører (`15_loop`, `01_etterbehandling`). Pre-eksisterende/miljø (hodeløs CPU-timing), ikke min regresjon.
Lint grønn. **maskin-sjekk** er en publiser-port i Vegars Chrome mot /prove; den er *ment* å bli rød når
skyggelegging endres (det er hele poenget med R4), og vi publiserer ikke — så den kjøres ikke her.

## Ikke gjort (budsjett / disiplin)
- Montasjer (75 v4/v5, 73, 944 SV|render) — Google-bilder utenfor git; lavere prioritet enn motor + bevis.
- Spross 3 på evt. andre vegger enn vegg5 — avventer CEO/Vegar på 6-vs-8-spørsmålet over.
