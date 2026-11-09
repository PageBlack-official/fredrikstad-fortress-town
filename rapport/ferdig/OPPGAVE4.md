# Oppgave 4: Vegars dom på husene, og resten av de 28 (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet `~/sot-maskin/gate` (gren `gate/kamera`). Skriv alt på norsk. Hovedregel: «nesten er ikke lov».
Les `rapport/ferdig/OPPGAVE.md` (miljø og kommandoer), `rapport/ferdig/RAPPORT3.md` (metoden og fellene) og de siste delene av `LESMEG.md`.

Vegar dømte 09.11 kl. 14:58. Under står ordene hans uendret, med skrivefeil. **Det han har lest av bildet er fasit for det huset og går foran tegning, Street View-lesing og agentens tidligere avlesning.** Kartverket er fortsatt fasit for høyde, unntatt der det står under. Tolkning (min, Fable) står merket [TOLKNING]; bildet avgjør om den er feil.

## Del A: Vegar har godkjent. Ikke rør disse

| Nr | Hus | Vegar |
|---|---|---|
| 2 | bnr-193867901, 8 Voldgaten | «Korrekt» |
| 9 | bnr-193867723, sandgult | «Korrekt» |
| 12 | bnr-6276016, 30 General Ohmes vei | «korrekt» |
| 13 | bnr-194006187, hvitt panelhus | «Korrekt» |

`bnr-193971954` (nr 11, rød butikkgård): «Korrekt med vanwkelig å se om pipa skal være så stor eller ei». Alt er godkjent unntatt pipa: mål pipa mot Street View og flyfotoet, og rett bare størrelsen hvis kilden viser at den er feil.

## Del B: Rett etter Vegars ord

**Nr 1, bnr-193867952, 10 Voldgaten**
«Fra venstre: 1 etg. På bildet ser jeg to vinduer med sprosser helt til venstre, så dør, to vinduer med sprosser så dør, ett vindue med sprosser, stor port.2 etg. fra venstre. tre vinduer med sprosser + tre vinduer med sprosser, så ett vindu og så et dobbelvindu over port-døren.»

**Nr 3, bnr-193867898, 9 Voldgaten**
«korrekt, men døren er to langt ned. Den må være på gateplan»

**Nr 4, bnr-193867804, 51 Kasernegaten**
«Her har du lest bygget feil. SLå sammen den rosa delen med den beide delen til høyre med to vinduer nede og oppe og fargelegg bygget rosa. Aller er vindusplassering og dørplasseringen er riktig.»
[TOLKNING] Nabobygget til høyre (det beige med to vinduer nede og to oppe) er samme hus. Slå sammen via husdelingen, behold begge ID-ene i registeret, hele bygget rosa. Vinduer og dører står der de står.

**Nr 5, bnr-193972292, 79 Færgeportgaten**
«Nesten korrekt. de vinduene til høyre på tegningen er for høyre helt nede på gatenivå. og de i 2 etg er også litt for store. Det virker som alle vinduene er i samme størrelse.»

**Nr 6, bnr-193867855, Torvgaten 67**
«Det virker som du har lest bygget feil. Det hvite huset har to vinduer nede og to vinduer i 2 etg. Taket er formet som en slag hatt med klaffer. Den røde porten er riktig plassert.»
[TOLKNING] Tak med avvalmede gavler (halvvalm), slik Street View-bildet SV v4 viser. Les formen av bildet.

**Nr 7, bnr-193867626, 26/27 Kirkegaten**
«Riktig, men det er en stor kloss på venstresiden av taket som ikke finnes. Taket skal ha to piper»

**Nr 8, bnr-193867634, Vollmesterboligen, 5 Voldgaten**
«Det manger et vindu helt til høyre. Det skal være 7 vinduer på og to piper på det bygget, og et takvindu på kortveggen. Sort kloss har du allerede notert»
Den svarte klossen foran huset finnes ikke i Street View og skal bort. Finn hva den er, og rett årsaken: samme svarte kloss står ved 35 Heibergs gate.

**Nr 10, bnr-193868576, 41 Tøihusgaten**
«Porten er brun, det er en tegn-mur-hus. Ellers korrekt form»
[TOLKNING] Murhus i tegl: teglfarget vegg som leses som mur, uten lys sokkel hvis Street View ikke har det. Brun port.

**Nr 14, bnr-13416419, 22 Bings gate**
«Tegningen din er så blass at jeg ikke ser noe, men bildet viser fire vinduer med sprosser der vinduene i midten oppe og nede er dobbelvinduer»
Huset skal ha to etasjer slik bildet viser. [TOLKNING] Bildet vinner over Kartverkets 4,6 m her; skriv unntaket med begrunnelse i datakilden, ikke som hardkoding. Finn også hvorfor huset er utbrent (se Del D).

## Del C: De 12 som ikke holdt da Fable så på bildene

| Hus | Feilen |
|---|---|
| bnr-13415889, 9/10 Ove Ramms gate | Villaen er for enkel: tredje takark, balkong, grå side står hvit |
| bnr-6276822, 2 Lammers gate | Taket er rødt, skal være mørkt |
| bnr-6251331, 21 Raadhusgaten | Huset er gult, står beige. Kilden gir «strågul»; Street View mai 2024 viser gult |
| bnr-193868088, lys blågrått panelhus | Huset er grått, står blått |
| bnr-6276512, 37 Heibergs gate | Huset er grått, står blått |
| bnr-193971946, hvitpusset | Vinduskarmene skal være mørke |
| bnr-13416362, 24 Bings gate | Kontrollbildet er utbrent, kan ikke vurderes |
| bnr-193867820, 13 Rådhusgaten | Kameraet står bak en mur |
| bnr-6276504, 35 Heibergs gate | Trær dekker huset; svart kloss (se nr 8) |
| bnr-193972306, grått panelhus | Bildet viser en annen vegg enn modellen |
| bnr-193971288, hvitt hus | Usikkert om bildet viser riktig hus |
| bnr-193867480, Widdingstua | Terrenget ligger under vannet: rett årsaken i terrenget (bakke_dtm), så huset kan tegnes |

Farge: Vegars regel er riktig kulør (et grønt hus grønt), ikke eksakt tone. Blågrå-verdien [178,196,206] leses tydelig blå i kartet; finn en verdi som leses grå på husene som er grå.

## Del D: To ting som må fikses først, for de ødelegger dommen

1. **Utbrent hvitt.** Vegar så ingenting på nr 14; 24 Bings gate er også utbrent. Finn om dette bare er i kontrollbildet eller også i kartet han ser, og rett årsaken. Autokontrast er ikke en løsning. Sjekk med det ekte skjermkortet (PW_GPU=1).
2. **Bevisbildene.** Vegar skal se huset. Samme kamera i Street View og modell, huset midt i bildet, ingen nabovegg, mur eller tre foran. Går det ikke fra det standpunktet: flytt kameraet i begge.

## Sluttkontroll

`ferdig_sjekk.py` måler bare at feltene er fylt. Den ga exit 0 på et sett der bare 13 av 26 holdt. Derfor:

1. Lag `verktoy/rett/dom_sjekk.py` som leser det **bygde** datasettet (`ut/`), ikke `kilder/ferdig.json`, og som krever det som kan telles i Vegars ord: nr 1 (rekkefølgen i begge etasjer), nr 6 (2+2 vinduer), nr 7 (2 piper), nr 8 (7 vinduer, 2 piper, 1 takvindu), nr 14 (fire vinduer per rad, de to midterste doble, to rader). Exit 0 er kravet.
2. Del A skal være uendret, byte for byte i dataene for de husene. Sjekk det i samme skript.
3. Status per hus i `kilder/ferdig.json`: `klar_til_dom` med `"runde": 3`. Du kan aldri sette «ferdig».
4. Se på hvert bevisbilde selv. Står du ikke inne for et hus, skriv hvorfor. Ikke merk det klart.

## Når du er klar

1. Kjeden, `python3 bygg.py enkel`, bevisbilder for alle husene i Del B og C.
2. Commit (norsk melding). Aldri Google-bilder i git. Regler etter commit (`PYTHONPATH=regler python3 regler/kjor.py`, nohup). Regel 03 er kjent rød; annet rødt rettes.
3. `sh publiser.sh prove1`. Deploy-nøkkelen virker nå. Vanlig push, aldri force.
4. Kontaktark til Dropbox `.../20 Paperclip/outputs/teknisk-veikart/status/sot-dom-runde3.jpg`, Street View | etter, adresse og Vegars nummer under. Rapport: `status/sot-tegnet-runde3.md`. Én pekerlinje øverst i `status/smart-old-town.md`.
5. Sett PAG-1469 til done: den er erstattet av denne oppgaven.

Ikke stopp for å spørre. Kan en kilde svare, spør kilden. Bare et hus der ingen kilde kan svare får `trenger_vegar`, med spørsmål og bilde. Går du tom for kontekst: skriv hvor du er i `rapport/ferdig/RAPPORT4.md` og fortsett derfra i neste kjøring.

## Ikke rør

Kirka og Kaserna. Forsiden og /prove (Morten ser den). Fargeoppgaven i `rapport/farger/`. Introen. Ikke slett noe, ikke force-push, ikke send noe eksternt.
