# Gatevandring 14.11 — funn, forbehold og vei videre (PAG-1585)

Studio-run, gren `gate/vandring-1411` fra `gate/ytelse` b649900. Egen worktree
`~/sot-maskin/gate-vandring` (rørte ikke `gate-ytelse` der Claude maler introen).

## Hva som ble gjort
- Verifisert at kjeden virker i worktreet: `bygg.py enkel` (1,5 s), `gatekamera.mjs`
  med PW_GPU=1/Metal (~3 s/bilde), par-montasje SV|modell.
- Inventert rå Street View-skudd fra rundene 1–5: **354 unike hus-vegg-skudd** i
  `rapport/gate/sv_rett2/3/4` med `hent-*.json` (pano, lat/lon, heading, fov, pitch 97).
  Dette er bildene vi sammenligner mot — ingen ny Google-henting trengs for disse.
- Gått 2 klynger (gater) hus for hus: gate01 (Raadhusgaten/Kasernegaten-magasinene, 21),
  gate02 (Kirkegaten/Kirkeparken, 16). Se `LISTE.md` og kontaktarkene.

## Forbehold som styrer resten av vandringen (les før neste runde)
1. **Rå gatekamera-utsikt er for grov til vindus-/dørnivå.** Skuddene fra rundene 1–5 er
   «hele veggen»-skudd med **pitch 97** (ser oppover for å få med takfoten). Gatekameraet kan
   ikke tegne pitch > 88,5 (MapLibre), så modellen rammer et annet utsnitt enn SV. I tillegg
   spriker heading/posisjon fordi Googles pano-posisjon ligger 3–5 m feil. Resultat: modell og
   SV står side om side, men ikke så presist at man trygt kan si «dette vinduet mangler».
   **Å påstå en rettelse herfra er akkurat fella fra PAG-1557.** Derfor er 0 rettet denne runden.
   - Delforbedring brukt: render i **1280×720** (samme bildeforhold som SV), ikke 1568×765.
     Da matcher vfov og sidene, og sammenligningen blir langt lesligere. Gjort for de lesbare.
2. **Den pålitelige rettemetoden er rektifiseringen, ikke rå gatekamera.** Slik rundene 1–5
   faktisk rettet: les 4 hjørner på rutenett-skuddet (HJORNER.md) → `rett.py` (homografi, 50 px/m)
   → les vinduer/dører i meter (ELEMENTER.md) → `fasade_rett.py`. Da faller kamera­feilen bort.
   En ekte ny runde bør gå denne veien på de **lesbare front­fasadene**, ikke rå side-om-side.
3. **Mange standpunkt er ikke lesbare fra dagens kilde.** Av 37 standpunkt var 24 ikke lest:
   17 er **2010-bilder** (regelen: 2010 skal ikke leses), 7 er **okkludert** av tre/gjerde/plass.
   Dette bekrefter LÆRDOM fra runde 5 i `status/smart-old-town.md`: de ~125 simulerte husene
   ligger «bak trær/voll/mur», og **neste kilde må være en annen vinkel (vinter-SV / eget foto),
   ikke flere skudd fra samme pano**.
4. **De lesbare frontfasadene i disse to gatene så allerede riktige ut** (farge, etasjer,
   grovt vindusmønster). Eksempel: 51 Kasernegaten — render kan se buet port, men dataene
   (`rett-runde2.json`, vegg 4) har alt flat dør `#6b4a35`. Rundene 1–5 tok disse.

## Lav-sikkerhets-kandidater (IKKE rettet — trenger rektifisert lesing for å bekreftes)
- bnr-193867936 (15 Raadhusgaten): modell mer mettet gul enn SVs bleke kremgul.
- bnr-193867839 (49 Kasernegaten): SV-vinduer ser hvite ut, modell har grønne karmer.
- bnr-193972446 / pb-46 (13 Raadhusgaten-naboer): et hus SV leser gult, modell oransje.
- bnr-193868290 (28 Kirkegaten): sort rektangel-artefakt på nærvegg ved bratt vinkel (render).

## Anbefaling til Vegar/CEO (scope)
Mekanisk å gå alle 343 hus rå side-om-side gir lav gevinst: de lesbare frontfasadene er
alt rettet i rundene 1–5, og resten er 2010/okkludert fra dagens kilde. To bedre veier:
- **(A)** Kjør en ekte rektifiseringsrunde (hjørner→rett→elementer→fasade_rett) på de
  gjenværende **lesbare** frontfasadene vi ennå ikke har tatt — parallelle agenter, som
  rundene 1–5. Høy presisjon, ekte rettelser.
- **(B)** For de ~125 bak tre/voll/mur: skaff ny kilde (vinter-Street View uten løv, eller
  Vegars egne foto). Uten det kan de ikke leses, uansett hvor mange ganger vi går forbi.

Jeg venter på styringen før jeg bruker en natt på enten (A) i full skala eller fortsetter
den rå vandringen. Grunndataene er urørt; alt dette ligger som rapport-artefakter på grenen.
