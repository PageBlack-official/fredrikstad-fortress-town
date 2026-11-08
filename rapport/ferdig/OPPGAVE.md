# Oppgave: lukk 28 hus i Gamlebyen som FERDIG (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet ~/sot-maskin/gate (git, gren gate/kamera). Vegar har bedt om dette 08.11.2026 kl. 11:46.
Skriv alt på norsk. Hovedregel: «nesten er ikke lov». Et hus er ferdig bare når det stemmer med virkeligheten på alt publikum ser.

## Hvorfor
De 28 husene i `kilder/gate/ferdig-kandidater.json` har form fra kommunekartet, høyde målt av Kartverket, veggfarge fra
virkeligheten og vinduer/dører lest fra Street View på alle frie vegger mot gate. Vegar: «la oss få lukket en del hus som ferdige».
Vegger publikum ikke ser (mot bakgård, inn mot nabo) skal simuleres etter reglene; de er IKKE en grunn til å holde et hus åpent.

## Miljø
- `export PATH=$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH`; ekte GPU: `PW_GPU=1`.
- Bygg: `python3 bygg.py enkel` → ut/enkel/index.html. Kjede: `python3 verktoy/bygg_kjede.py`.
- Gatekamera: `PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html <standpunkter.json> <utmappe>`;
  standpunkt = {navn, pano:"", dato, lat, lon, heading, pitch, fov, oye}. Se verktoy/rett/front_stand.py for et eksempel.
- Kamera for hver lest vegg står i ferdig-kandidater.json (bilder[].kamera), bildet i bilder[].sv_bilde.
  For `sv_auto_vegg` (lest uten retting) står standpunktet i `fasade_sv`.
- Verktøy for rettede fasader: verktoy/rett/ (HJORNER.md, ELEMENTER.md, rett.py, overlegg.py, konverter.py, fasade_rett.py).
- Regler: `PYTHONPATH=regler python3 regler/kjor.py` (alle, ~35 min) eller `... kjor.py 03 17 39 44` (utvalgte).

## Steg
1. Kalibrer kameraet på ETT hus først: render modellen fra nøyaktig samme kamera som Street View-bildet og legg bildene side om
   side. Sjekk at huset står på samme sted i begge (pitch-konvensjon: SV 90 = horisont; oye = øyehøyde). Ikke gå videre før
   et kjent hus står likt i begge bilder. Skriv hva som måtte til i rapporten.
2. For hvert av de 28: lag `rapport/ferdig/<id>.jpg` med Street View til venstre og modellen fra samme kamera til høyre, én rad
   per lest vegg. Se på hvert bilde (les bildet, ikke bare tall) og sjekk:
   antall vinduer og dører, plassering (etasje, avstand fra hjørner), størrelse, rundbue/port, veggfarge, takfot/høyde,
   takform og -farge, sokkel. Vegger mot bakgård: bare sjekk at de ikke er blanke og ikke ser feil ut fra gata.
3. Avvik du kan rette sikkert med verktøyene som finnes (feil element, farge, porttype): rett, kjør kjeden, render på nytt og
   se igjen. Avvik du ikke kan rette sikkert: la huset stå åpent med en setning om hva som er feil. Aldri gjett.
4. Register: `kilder/ferdig.json` = {id: {"status": "ferdig"|"åpen", "dato": "2026-11-08", "bevis": "rapport/ferdig/<id>.jpg",
   "avvik": [..]}}. Ferdig bare når alt publikum ser stemmer.
5. Kjør reglene 03 17 39 44 (og alle hvis du har endret data). Commit med en norsk melding som slutter med
   «Co-Authored-By: Claude <noreply@anthropic.com>». IKKE publiser (push fra minien har ikke GitHub-passord; skyøkta publiserer).
6. Rapport: `rapport/ferdig/RAPPORT.md` (antall ferdig/åpne, avvik per åpent hus, hva som ble rettet, kalibreringen) og kopier
   den til `~/Library/CloudStorage/Dropbox-PageBlack/Page Black Business/20 Paperclip/outputs/teknisk-veikart/status/sot-ferdig-28.md`
   (finn Dropbox-stien med ls hvis den er annerledes). Legg én pekerlinje (maks 250 tegn) øverst i status/smart-old-town.md.

## Ikke rør
- Kirka (bnr-193867529, egen modell i fasade_former) og Kaserna (datalag.EGNE_FASADER).
- Kildekode i src/ (kartet) uten at et avvik krever det; da: beskriv det i rapporten i stedet.
- Ikke slett filer. Ikke force-push. Ikke send noe eksternt.

## Feller som allerede er kjent
- Typ 2 (port) tegnes alltid med rundbue; rett port = typ 1 (fasade_rett gjør dette).
- Vinduer over takfot − 0,1 m fjernes av datalag; fasade_rett kapper 0,15 m under takfot.
- h = 6,0 er standardhøyde på småbygg uten måling — mistenkelig.
- verktoy/gatekamera.mjs: kameraet kan havne inne i et annet hus når standpunktet står for nær; flytt bakover langs heading.


## Tillegg 08.11 12:15 (Vegar: «lær agenten alt du selv lærer»)
- Les den nye delen nederst i LESMEG.md (commit e341caf): arbeidsdeling, veien for rettede fasader og fellene fra natta. De gjelder her.
- Steg 5 er endret: publiser fra minien med `sh publiser.sh prove1` når regelrapporten er kjørt mot din siste commit. publiser.sh pusher med
  egen deploy-nøkkel (remote `pages`), vanlig push uten force. Feiler den med «Permission denied (publickey)», er nøkkelen ikke lagt inn
  på GitHub ennå: skriv det i rapporten og la publiseringen stå. Ikke prøv andre veier.
- Før du skriver at noe er feil: sjekk kilden (logg, bilde, siden ute). Et merke eller notat er ikke en feil.
