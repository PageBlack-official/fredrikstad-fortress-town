# Oppgave: veggfarger fra Street View for husene i Gamlebyen som mangler farge fra virkeligheten (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet `~/sot-maskin/gate` (gren `gate/kamera`). Skriv alt på norsk. Hovedregel: «nesten er ikke lov». Les først de to siste delene av `LESMEG.md`
(«Arbeidsdeling» og «Rettede fasader») og «Veggfarger fra Street View». Oppgaven er bestilt av Vegar 08.11.2026.

## Hva og hvorfor
197 hus i Gamlebyen har veggfarge fra tegning eller trykk, ikke fra virkeligheten (`rapport/farger/husliste.md`). Regelen: nyeste kilde vinner, Street View fra 2016 eller senere går foran tegningen,
«tilnærmet riktig er nok, feil kulør er ikke lov». `verktoy/rett/farge_kandidater.py` plukker ut lesninger. Den er et filter, ikke en dom: uavhengig kontroll ga 7 avvik på 31 hus. Derfor steg 3 med øyet.

## Miljø
- `export PATH=$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH`
- Maskinen har andre jobber (Plex, Paperclip). Kjør det som tar over 30 sekunder med `nohup … > logg 2>&1 < /dev/null &` og les loggen.

## Steg
0. **Klargjør.** Sjekk at `paperclip get_issue PAG-1467` er `done`, og at ingen annen agent jobber i mappa (`ps aux | grep -E "sv_hent|kjor.py|gatekamera"`).
   `cd ~/sot-maskin/gate && git merge farger`. Filene i `ut/` og `rapport/rapport.md` kan stå endret fra forrige jobb; de rører ikke flettingen. Blir det konflikt i LESMEG.md: behold begge sider.
   Ta vare på kartet slik det er nå: `python3 bygg.py enkel && mkdir -p /tmp/farger && cp ut/enkel/index.html /tmp/farger/for.html`.
1. **Test.** `python3 verktoy/rett/test_farge_kandidater.py rapport/farger/ark/test.jpg`. Exit 1 = stopp og rapporter; ikke juster tersklene for å få den grønn uten å si det i rapporten.
2. **Hent de nye bildene.** Bare det som står i `kilder/gate/sv_farge_skudd.json` (lag lista på nytt med `verktoy/rett/farge_skudd.py` hvis det har kommet nye bilder siden).
   Google-bilder skal ikke i git:
   `mkdir -p rapport/gate/sv_rett_farger && printf '*\n' > rapport/gate/sv_rett_farger/.gitignore`
   `for d in 0 1 2; do nohup node verktoy/sv_hent.mjs kilder/gate/sv_farge_skudd.json rapport/gate/sv_rett_farger $d/3 > /tmp/farger/hent-$d.log 2>&1 < /dev/null & done`
   Synlig Chromium, ikke hodeløs. Får du robotsjekk: stopp, skriv det i rapporten, ikke prøv å komme forbi.
3. **Les og se.**
   `python3 verktoy/rett/farge_liste.py`
   `python3 verktoy/rett/farge_kandidater.py --liste rapport/farger/husliste.json --ut rapport/farger/kandidater.json --status rapport/farger/status.json --avvist rapport/farger/avvist.txt --ark rapport/farger/ark/kandidater.jpg`
   Les kontaktarket `rapport/farger/ark/kandidater.jpg` (åpne bildet, ikke bare tallene). Hver rute: Street View med magenta firkant der veggen er målt, ordets farge og målt farge nederst. Hus som får ny kulør står først.
   Underkjenn en lesning når firkanten står på feil hus, på noe foran huset (tre, skur), når veggen er flerfarget (tegl med hvite bånd), når bildet er for lite til å se, eller når ordet ikke stemmer med det du ser.
   Tre brunt er «brun», ikke terrakotta. Skriv bildenavnet (for eksempel `pb-7-0`) på egen linje i `rapport/farger/avvist.txt` og kjør kommandoen på nytt. Er du i tvil: underkjenn. Et hus som står igjen, er ikke feil; en feil farge er.
4. **Flett inn.**
   `python3 verktoy/rett/farge_kandidater.py --liste rapport/farger/husliste.json --ut rapport/farger/kandidater.json --status rapport/farger/status.json --avvist rapport/farger/avvist.txt --flett kilder/gate/farger-rett.json`
   `python3 verktoy/rett/farger_inn.py kilder/gate/farger-rett.json` (hele fila, se fellen i LESMEG)
   `nohup python3 verktoy/bygg_kjede.py > /tmp/farger/kjede.log 2>&1 < /dev/null &` (ca. 90 s). `python3 bygg.py enkel`.
5. **Kontroller.**
   `python3 verktoy/rett/farge_kontroll.py sjekk` skal gi 0 feil. Står det FEIL, er lesningen ikke kommet gjennom fargeregelen: finn årsaken i `verktoy/sv_kobling.py` før du går videre.
   Før/etter fra samme kamera:
   `python3 verktoy/rett/farge_kontroll.py standpunkter /tmp/farger/st.json`
   `PW_GPU=1 node verktoy/gatekamera.mjs /tmp/farger/for.html /tmp/farger/st.json rapport/farger/ark/for`
   `PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html /tmp/farger/st.json rapport/farger/ark/etter`
   `python3 verktoy/rett/farge_kontroll.py ark rapport/farger/ark/for rapport/farger/ark/etter rapport/farger/ark/for-etter.jpg`
   Se på arket: riktig hus har skiftet, og ingenting annet. Kameraet kan stå inne i et annet hus (LESMEG); da teller bildet ikke, og huset sjekkes fra et annet standpunkt.
6. **Commit.** `git add verktoy kilder/gate kilder/streetview data/rettelser.json rapport/farger` (kontaktarkene holdes ute av `rapport/farger/.gitignore`). Norsk melding som slutter med «Co-Authored-By: Claude <noreply@anthropic.com>».
7. **Regler, så publiser.** `PYTHONPATH=regler nohup python3 regler/kjor.py > /tmp/farger/regler.log 2>&1 < /dev/null &` (~35 min, må kjøres etter commit). Commit regelrapporten. Rød regel 03 er kjent; alt annet rødt skal forklares i rapporten.
   `sh publiser.sh prove1`. Feiler den med «Permission denied (publickey)»: skriv det i rapporten og la publiseringen stå. Ikke prøv andre veier, ikke force-push.
8. **Rapport.** `rapport/farger/RAPPORT.md`: antall hus farget, antall underkjent og hvorfor, hus som fortsatt mangler kilde, hva testen ga. Kopier den til Dropbox: `.../Page Black Business/20 Paperclip/outputs/teknisk-veikart/status/sot-farger.md`
   (finn Dropbox-stien med `ls ~/Library/CloudStorage`) og legg én pekerlinje (maks 250 tegn) øverst i `status/smart-old-town.md`.

## Ikke rør
Kirka (`x['kirke']`) og Kaserna (`datalag.EGNE_FASADER`). Forsiden (`publiser.sh forside`). Tak (farger fra ortofoto). Ikke slett noe, ikke send noe eksternt. Sjekk kilden (logg, bilde, siden ute) før du skriver at noe er feil.
