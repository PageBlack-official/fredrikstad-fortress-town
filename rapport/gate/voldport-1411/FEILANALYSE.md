# FEILANALYSE — hvorfor Voldportgaten 75–71 ble lest så feil (Studio, 14.11.2026)

Vegar 14.11 17:28: «Den leste ikke noe korrekt … lær av hvordan den i all verden klarte å ta så feil.»
Skrevet FØR del B (RUNDE3.md), som bestilt. Fables tre kjente punkter + det jeg selv finner i dataene.

## Fables tre (kjent, tatt med)
1. **Feil ordre i OPPGAVE.md pkt 3:** «Vinduer/dører/butikkvinduer: legg dem inn **for hånd etter beskrivelsen over** (fasade_rett / elementer), **ikke fra gatekameraet**.» Fasadene ble altså bygd fra Fables **tekst**, ikke fra Street View. Metoden repoet har (LESMEG «Rettede fasader fra Street View 07.–08.11»: rektifisering → les hvert element i meter) ble aldri brukt.
2. **Bildene nådde aldri minien.** Vegars 9 skjermbilder lå i ~/Downloads (tilgang nektet). Ingen i kjeden så fotoet ved siden av renderen.
3. **Kontrollen var tekst mot tekst.** FUNN og Fables lesing dømte renderen mot punktlista, ikke render mot foto side om side. «✓ på karakter» slapp gjennom en jevn rytme som ikke finnes.

## Det jeg finner i dataene (resten)

### 4. Antallene kom fra ord, ikke fra telling i bildet
`verktoy/bygg_merknader.py` (docstring l.7–8): tar **«antall per etasje»** og **dørene** som merknad, og **«erstatter veggens vind»**. Antallene i merknadene for de tre husene er Vegars/Fables **ord**, ikke målt i Street View:
- 75: «**8** vinduer i 2. etg» (Vegar, Voldgaten-sida) — et muntlig anslag, ikke en telling per vegg.
- 73 Majoren: «**5** vinduer i 2. etg» (Fables lesing) — samme.
- 71 Therese M: butikkvinduer «med ovale topp-vinduer» — form fra ord, antall og bredde aldri målt.
Ingen av tallene har en kilde i et rektifisert bilde. De er **gjettet fra beskrivelsen**.

### 5. Posisjonene ble maskingenerert i JEVN RYTME — kjernefeilen
`bygg_merknader.py`: «vinduer i **jevn rytme etter reglene**, antall per etasje og dørene der merknaden sier (u = andel fra venstre)». `verktoy/vinduer_regler.py` (l.112): «aksene legges på **hele veggen**, så rytmen holder». Altså: gi et antall, og verktøyet **fordeler vinduene jevnt** over veggen. Ingen ekte posisjon i meter fra fotoet ble noensinne brukt. Dette ER «den jevne rytmen som ikke finnes» — ikke en bieffekt, men selve metoden runde 1–2 brukte.

### 6. Regel 17 KREVER jevn rytme → grønn 17 var et faretegn, ikke en bekreftelse
`regler/17_vinduer_rytme.py`: «innen en vegg og etasje står vinduene med **lik avstand**». Regelen håndhever jevn rytme — også for `fasade_kilde=streetview` (med bare to unntak: dør på den veggen bildet viser, og en etasje kan ha flere vinduer enn den under). Følge: hvis du hadde lagt vinduene på de **ekte, ujevne** posisjonene fra et foto, ville **regel 17 blitt RØD**. Runde 1–2 fikk «17 grønn» nettopp fordi rytmen var **pålagt**. En grønn 17 på et **fotografert** hus betyr at rytmen er diktert av regelen, ikke lest fra bygget — det er et varsel, ikke en kvittering.

### 7. «Merknadene vinner over alt»
OPPGAVE.md pkt 2: «Merknadene vinner over alt (Fargene §).» De tekst-avledede merknadene overstyrte dermed enhver annen kilde. Kombinert med pkt 4–6: et muntlig antall → jevn maskinrytme → låst som fasit, uten at noe foto fikk korrigere.

## Konklusjon (én setning)
Runde 1–2 brukte **antatt-hus-verktøyet** (antall per etasje → jevn rytme, håndhevet av regel 17) på et **fotografert** hus. Det verktøyet er riktig for hus uten foto (kvartaltegning), men for et hus vi faktisk har på Street View gir det en plausibel, feil fasade — og regelgrønt bekreftet rytmen i stedet for å avsløre den. Rettingen (del B): les hvert element i **meter** fra rektifisert Street View (`fasade_rett`/ELEMENTER.md), sett `fasade_kilde=streetview`, og kontroller **render mot foto side om side**, ikke mot regel 17.

→ LESMEG-regel skrevet samme dag under «Voldportgaten 14.11: bygd fra tekst, ikke fra bildet».
