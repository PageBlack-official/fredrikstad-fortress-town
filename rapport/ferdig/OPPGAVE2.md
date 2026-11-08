# Oppgave: gjør ferdig de 22 åpne husene av de 28 (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet `~/sot-maskin/gate` (gren `gate/kamera`). Skriv alt på norsk. Hovedregel: «nesten er ikke lov».
Vegar 08.11: «Jobben var 28 hus». Forrige runde (PAG-1467) kontrollerte alle 28, lukket 6, rettet ingenting og satte oppgaven til done. Det var feil. Denne gangen er oppgaven å rette husene.

Les først: `rapport/ferdig/OPPGAVE.md` (miljø, kommandoer), `rapport/ferdig/RAPPORT.md` (kalibreringen av kameraet), de tre siste delene av `LESMEG.md`, og avviket per hus i `kilder/ferdig.json`. Se på `rapport/ferdig/<id>.jpg` for hvert hus.

## Når er du ferdig
`python3 verktoy/rett/ferdig_sjekk.py` gir exit 0. Ikke sett oppgaven til done før det. «Usikker» er ikke en sluttstatus: er noe usikkert, skaff bedre bilde eller les det i meter.
`trenger_vegar` er bare for det kilden ikke kan svare på. Da skal feltene `sporsmal` og `forsokt` fylles ut, og du skal ha prøvd veiene under først.
Har det gått 20 minutter uten at et nytt hus er lukket, skriv hvor du står i `rapport/ferdig/RAPPORT2.md` og fortsett med neste hus.

## Klargjør
`git merge --no-edit farger` (gir `verktoy/rett/FARGER.md`; selve fargeoppgaven i `rapport/farger/` skal IKKE kjøres her).
`python3 bygg.py enkel && mkdir -p /tmp/f22 && cp ut/enkel/index.html /tmp/f22/for.html` (før-bildet).
Street View-henting er lov nå. Bare synlig Chromium. Google-bilder skal ikke i git: ny mappe under `rapport/gate/` får egen `.gitignore` med `*`. Stopper Google deg med robotsjekk: skriv det, ikke prøv å komme forbi.

## Hus for hus
**Vinduer og dører usikre, eller port feil tegnet** (bnr-13416362, bnr-193868088, bnr-193867855, bnr-193867901, bnr-193867952, bnr-193867626, bnr-193868576, bnr-193972292, bnr-193867804):
les fasaden i meter. Det er ikke gjetting, det er metoden: hjørner etter `verktoy/rett/HJORNER.md` → `rett.py` → elementer etter `verktoy/rett/ELEMENTER.md` → `overlegg.py` → se på overlegget → `konverter.py` → ny `kilder/gate/rett-runde6.json`. Du kan lese bilder selv. Port med flat overkant = uten `bue`. Vinduer og dører fra bilder fra 2010 er gyldige.
Ser ikke bildet hele veggen: `sv_rett_plan.py` med UNNTA for en annen vinkel, hent, les. Gjelder også vegg 3 på bnr-193867626.

**Farge på vegg** (bnr-194006187, bnr-193971288, bnr-193972306, bnr-6276504, bnr-13416419):
se først om målet er riktig hus (firkant i bildet, `verktoy/vegg_for_skudd.py`). Les fargen etter `verktoy/rett/FARGER.md`, bare fra bilder fra 2016 eller senere. Legg siden til i `kilder/gate/farger-rett.json` uten å fjerne noe, og kjør `verktoy/rett/farger_inn.py kilder/gate/farger-rett.json` (hele fila). Sjekk etter kjeden at huset har fått fargen. Vinner fortsatt feil farge: finn hvorfor i `verktoy/streetview_farger.py` og `verktoy/sv_kobling.py`. bnr-13416419 og bnr-193972306 trenger også nytt render (under).

**Dør- og portfarge** (bnr-193867898 blå port, bnr-193867952 hvit dør, bnr-6251331 grønn port): feltene `dor_farge` og `karm_farge` finnes på huset, se `src/07` og hvordan de settes i kjeden. Sett dem i kjeden, ikke for hånd i data. Skal det inn en ny type element (butikkfront på bnr-6251331): bygg det som regel i verktøyet, ikke som unntak for ett hus.

**Tak og arker** (bnr-13415889): les takform og arker fra bildene, bruk `kilder/tak-tegning.json` med `kropper` per bygningskropp (LESMEG, feilen 07.11). Vegg 3 har annen farge og annet tak enn vegg 0: sjekk om det er to hus i én polygon (`kilder/husdeling.json`). Kontroller at takhøyden er rimelig mot h etterpå.

**Render klipper eller bommer** (bnr-193867820, bnr-193971954, bnr-193867480, bnr-13416419, bnr-193972306): lag nytt standpunkt. Kameraet fra en lest vegg, trekk bakover langs heading, eller sikt mot sentroiden som i RAPPORT.md. bnr-193867480 ligger utenfor senterfeltet: sikt på huset, ikke på veggen.

**Festningsmuren** (bnr-24218023, bnr-193972276): finn ut om husene finnes. `verktoy/se_her.py`, ortofoto 2024, kommunekartet, register (`verktoy/register.py`), og en annen panoramavinkel. Finnes huset: les det. Finnes det ikke, eller kilden ikke kan si det: `trenger_vegar` med spørsmål og bilde. Ikke fjern hus selv.

## Etter rettingene
1. `python3 verktoy/bygg_kjede.py` (nohup, ca. 90 s) og `python3 bygg.py enkel`.
2. For hvert hus: lag `rapport/ferdig/<id>.jpg` på nytt fra samme kamera (Street View | før fra `/tmp/f22/for.html` | etter). Se på bildene. Sjekk vinduer, dører, port, farge, takfot, tak. Se også at nabohusene ikke har endret seg.
3. Oppdater `kilder/ferdig.json`. Ferdig = alt publikum ser stemmer og `avvik` er tom.
4. `python3 verktoy/rett/ferdig_sjekk.py` til exit 0.
5. Commit (norsk melding, slutter med «Co-Authored-By: Claude <noreply@anthropic.com>»). Ikke `git add` på Google-bilder.
6. `PYTHONPATH=regler python3 regler/kjor.py` (nohup, ~35 min, etter commit). Commit regelrapporten. Regel 03 er kjent rød; alt annet rødt rettes eller forklares.
7. `sh publiser.sh prove1`. Feiler den på nøkkelen: skriv det og la det stå, ingen andre veier, aldri force.
8. `rapport/ferdig/RAPPORT2.md`: hus for hus hva som ble rettet, før/etter-tall (ferdig av 28), spørsmål til Vegar. Kopier til Dropbox som `teknisk-veikart/status/sot-ferdig-22.md` (finn stien med `ls ~/Library/CloudStorage`) og legg én pekerlinje øverst i `status/smart-old-town.md`.

## Ikke rør
Kirka og Kaserna. Forsiden. Ikke slett noe, ikke force-push, ikke send noe eksternt.
