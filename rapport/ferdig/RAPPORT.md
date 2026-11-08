# Rapport: lukk 28 hus i Gamlebyen som ferdige — kontroll mot Street View

Kjørt på Mac minien (Vegars-Plex) 2026-11-08, repo `~/sot-maskin/gate`, gren `gate/kamera`.
Bestilt av Vegar 08.11.2026 11:46. Regel: «nesten er ikke lov» — et hus er ferdig bare når alt publikum ser stemmer.

## Resultat
- **6 ferdig**, **22 åpen**. Register: `kilder/ferdig.json`. Sammenligningsbilde per hus: `rapport/ferdig/<id>.jpg` (Street View venstre, modell høyre, én rad per gatevegg).
- Ingenting publisert herfra (publiser.sh / push gjøres av skyøkta).

### Ferdig (6)
| id | adresse | hvorfor ferdig |
|----|---------|----------------|
| bnr-193867634 | Vollmesterboligen, 5 Voldgaten | hvit 1-et., vindusrekke, pipe, tegltak stemmer |
| bnr-6276822 | 2 Lammers gate | mørk vinrød 2-et., vinduer + dør stemmer |
| bnr-6276016 | General Ohmes vei / Hultfeldts gate | rød 2-et., mørkt tak, begge gatevegger stemmer |
| bnr-193867723 | Gamlebyen, sandgul | sandgul 2-et., to vindusrekker + dør stemmer |
| bnr-6276512 | 37 Heibergs gate | blågrå, rødt valmtak, pipe, vinduer stemmer |
| bnr-193971946 | Gamlebyen, hvit puss | hvit puss 1-et., vindusrekke + rundbue-inngang stemmer (buen RIKTIG her) |

### Åpne (22) — kort
Full avviksliste i `kilder/ferdig.json`. Grupper:
- **Porttype (rundbue der SV har flat port) — fixbar (typ 2 → typ 1 via fasade_rett):** bnr-193868576, bnr-193972292. (Se også naboer utenfor de 28 med samme feil ved bnr-193867804.)
- **Element-/fargeavvik på dør/port:** bnr-6251331 (grønn garasjeport + butikkfront mangler), bnr-193867898 (port blå i SV vs brun dør), bnr-193867804 (bred port vs smal dør).
- **Tak/arker:** bnr-13415889 (mangler takarker + feil mansardtak på to vegger).
- **Farge usikker/mulig feil:** bnr-194006187 (hvit vs beige), bnr-193971288 (hvit vs grønn), bnr-193972306 (grå vs oker), bnr-6276504 (hvit vs gul).
- **Vindustall usikkert i tett rekke:** bnr-13416362, bnr-193868088, bnr-193867855, bnr-193867901, bnr-193867952, bnr-193867626.
- **Render klipper / mål ikke synlig (må rendres på nytt fra bedre standpunkt):** bnr-193867820, bnr-193971954, bnr-193867480.
- **SV viser festningsmuren, ikke fasade — kan ikke verifiseres:** bnr-24218023, bnr-193972276 (begge «tegningen har ikke huset»).

## Steg 1 — kalibrering (hva som måtte til)
Rendret Vollmesterboligen fra det lagrede Street View-kameraet (heading 70,6). Huset havnet langt til høyre i modellen, ikke der det står i SV. Et sveip viste at ~heading 80 sentrerer huset — altså **~10° avvik** mellom lagret SV-heading og modellens `__gate`-konvensjon.

**Løsning (deterministisk, ingen gjetting):** sikt kameraet mot byggets tyngdepunkt regnet fra geometrien (`heading = atan2(dØst, dNord)` fra kamera til polygon-sentroide i `datalag.til_modell`-koordinater). Da lander **32 av 33 gatevegger innen ±23 px fra midten** (mål hentet fra `window.__gateHus()`-skjermpunktene). Ett mål (bnr-193867480, Isegran, h=2,5) kom ikke med — huset ligger utenfor senterfeltet.

**To render-artefakter, begge håndtert uten å endre modellen:**
1. *Overlys fra solretningen.* Enkelte fasader rendret nesten hvite (f.eks. bnr-13416362). Dataene var korrekte (oker vegg `[232,184,92]`, rødt tak, 17 vinduselementer) — det var eksponering. Løst med autokontrast-strekk (`ImageOps.autocontrast`, cutoff 1 %, preserve_tone) på modellbildet før montasje. Detalj kom tilbake.
2. *Kamera klipper i trang gate.* Et frontalt kamera 12–14 m ut havnet inne i bygget på motsatt side. Byttet til Street View-bilens faktiske standpunkt (lagret lat/lon, geometri-sikt) som aldri klipper. 32/33 bruker dette; 1 bruker frontal-fallback.

## Metode steg 2–4
- Standpunkter: `rapport/ferdig/stand-alle.json`. Render: `verktoy/gatekamera.mjs` (PW_GPU=1), ut i `rapport/ferdig/renders_sv/`. Montasje + autokontrast → `rapport/ferdig/<id>.jpg`.
- SV-bilde per vegg: lest-vegger fra `bilder[].sv_bilde`; auto-vegger og øvrige fra `rapport/gate/sv_rett*/` eller `rapport/gate/sv/<id>-<vegg>.jpg` (kart i `rapport/ferdig/mapping.json`).
- Jury: lest hvert bilde med øyet (ikke bare tall) — vinduer, dører, port/rundbue, farge, takfot/høyde, takform/-farge. Ferdig bare når farge, høyde, takform og vindus-/dørmønster alle stemmer uten synlig feil element.

## Rettinger gjort
Ingen datarettinger kjørt i denne runden. De sikre, fixbare avvikene (rundbue-porter → flat, et par dørfarger) krever at fasaden leses med hjørner i `rett-*.json` før `fasade_rett.py`; det kan ikke gjøres sikkert uten å lese hjørnene presist, og «aldri gjett» veier tyngst. De er beskrevet presist per hus i `ferdig.json` for en målrettet retterunde.

## Viktige funn til Vegar
1. **Rundbue-porter er en systematisk felle** (OPPGAVE-felle #1): minst bnr-193868576 og bnr-193972292 (+ naboer) har port tegnet som typ 2 (rundbue) der virkeligheten er en flat port. Kandidat for én batch-retting med `fasade_rett` (typ 1).
2. **To «ikke i tegningen»-hus (bnr-24218023, bnr-193972276) har Street View-standpunkt som peker på festningsmuren**, ikke på en fasade. De kan ikke verifiseres, og det bør sjekkes om husene er riktig plassert / om SV-referansen er feil.
3. **Auto/geo-vegger uten eget lest-kamera** gir av og til render som klipper eller bommer på målet (bnr-193867820, bnr-193971954, bnr-193867480). Trenger et bedre standpunkt (f.eks. lest-veggens kamera) for å avgjøres.
4. Kirka og Kaserna ble ikke rørt.
