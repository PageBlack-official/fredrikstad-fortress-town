# Endringslogg

## Uten versjon (29.10.2026, grenen natt/flyt, ikke publisert) – overganger og flyt
- **Én bevegelsesmodul** (src/15_bevegelse.js, BEV): alle varigheter og kurver på ett sted; stil.css leser dem som CSS-variabler. Kameraet glir fortsatt med glid (v32); knappene +/− får en kort kubisk kurve, kompasset glid.
- **Huskortet:** bunnark fra bunnen på smal skjerm (dra-håndtak: kortet følger fingeren og lukkes med farten den slipper med), sidepanel fra venstre på bred skjerm. Inn 380 ms som bremser, ut 240 ms som akselererer (Material). Bytte av hus i åpent kort toner innholdet i stedet for å bytte tekst på ett bilde.
- **Klikk på hus:** velges med en gang (før 300 ms venting), kameraet glir inn mot huset (minst zoom 2,4, aldri ut) og legger det midt i den delen kortet ikke dekker.
- **Tilbake = samme vei ut:** ×, Esc, trykk utenfor og nettleserens/Androids tilbake lukker kortet og glir kameraet tilbake dit det stod (med mindre du har flyttet kartet selv). Esc lukker kortet først, neste Esc går hjem.
- **Dobbelttrykk på mobil zoomer igjen** (var dødt: MapLibres dobbelttrykk var slått av sammen med dobbeltklikket). Dobbeltklikk og dobbelttrykk gjenkjennes fra klikkene, likt for mus og finger, og zoomer mot punktet.
- **Treghet etter dra, klyp og vri er vår egen:** farten måles i de siste 70 ms av gesten (flytt fra fingrenes midtpunkt, zoom/vri fra kameraet) og dør ut eksponentielt (tau 0,26 s), fra første bilde etter slipp; zoom og vri skjer rundt punktet mellom fingrene. Før tok MapLibre med 0,3 av farten fra klyp og vri, og ett bilde stod stille idet du slapp.
- **Musehjul:** jevn zoom; hvert hakk flytter et mål, og zoomen følger det som en kritisk dempet fjær (før ett utslag per hakk). Punktet under pekeren står. Styreflaten er skilt ut som før (to fingre flytter, klyp zoomer).
- **Speilet i vannet står i fart:** det tonet ut ved hver bevegelse og inn igjen etter stopp. Nå tegnes det på nytt høyst hvert 110 ms i fart, og vannet slår opp i det med kameraet fra da det ble tegnet, så det følger byen imellom.
- **Avbrutt intro:** miniatyr-uskarpheten tones ut på 0,8 s fra der den stod (før forsvant den på ett bilde), og kartet tegnes i full fart til lys og uskarphet er hentet inn (før 10 bilder/s, i trapper). Introen selv er ikke endret.
- **«Reduser bevegelse» gjelder ikke kartet** (Vegars valg, v27): kartet og kortet beveger seg som hos alle andre. Valget het `respectPrefersReducedMotion`, som ikke finnes i MapLibre 6, så det gjaldt ikke; nå `reduceMotion:false`.
- verktoy/flyt-test.mjs måler kamerabanen bilde for bilde med falsk klokke; regel 22. Kilder: rapport/flyt/kilder.md, funn: rapport/flyt/rapport.md.

## Uten versjon (29.10.2026, ikke publisert) – fasadene fra Street View
- 23 antatte hus har fått vinduer per etasje, dører, arker og piper på gatesiden slik Street View viser dem (verktoy/streetview_fasader.py, kilde kilder/streetview/avlesning.json). Andre vegger beholder reglene fra kvartaltegningene. Vegars regel: antall og rekkefølge foran centimeter.
- 23 fasithus fra kvartaltegningene er bare sammenlignet (rapport/streetview-fasader/sammenligning.md); 31 hoppet over (ikke synlig, kirka, portbygg, usikkert om det er riktig hus, for kort vegg til tallene).
- Regel 17 sjekker også Street View-husene. Kontrollark: rapport/streetview-fasader/ark.png.

## 34 (28.10.2026, /prove/, ikke godkjent) – sola finner byen, skyggekartet dekker bildet
- **Sola finner byen** (Vegar: «Kjør A»): introen starter overskyet (tegningens to toner, ingen kastskygger, litt kjøligere), en solkant vandrer over byen fra solsiden mens kameraet svinger inn (høye punkter først), kastskyggene vokser fram der kanten har passert, og sola synker fra 58° til de godkjente 42° så skyggene er lange idet kameraet lander. Lyset er bundet til kameraets vei (bearing), ikke til klokka. Avbrutt intro henter solkanten inn på 0,8 s. Alt i lyskoden (02_lys: solHer, U_SOL, kobleSol; 15_loop: solStart/solTil/solOppdater); ingen overlegg. Light leak-overlegget fra 26.10 er tatt ut. ?solintro=0 gir fast sol fra start.
- **Skyggekartet dekket mindre enn bildet** siden v31.1 (trinnet rundet opp): skyggene ble kuttet i kanten av dekningen, kanten fulgte kameraet, og «zoom» tegnet kartet hvert bilde (Vegar: «trærnes skygge tegnes på nytt hver gang jeg flytter meg»). Nå rundes trinnet ned (R minst 1,4·r, opptil 1650 m; sola 2500 m ute, fjernplan 6000). Regel 19 måler dekning og ny tegning i ro og under dra; rød på v33, grønn nå.
- **Trekroner og vinduer lyses fra sola, ikke kameraet:** solRetning() er i kamerarommet; normalen transformeres dit som husene gjør. Før dreide lyssiden med kameraet.
- **Regel 02 måler mot Kartverket** (fasit for høyde, Vegar 28.10); tegningene er fasit for fasade (03). 197 hus grønne, 78 uten sikker måling listes til kvartal-QA.
- **Sperre i publiser.sh:** samlerapporten stemples med siste kilde-commit; ingen publisering uten fersk rapport, uten urettede endringer, eller med røde regler utenom 09 (/prove/ slipper røde gjennom, men listes). regler/kjor.py kan kjøre et utvalg og bygger sammendraget fra regel-filene.
- Grå hus: ikke løst (se LESMEG). Kaserna med veranda og uteservering, bryggene, vann og flater mot ortofoto 2024 (27.10) er med.


## Uten versjon (27.10.2026, ikke publisert) – Kaserna slik den blir som hotell
- Infanterikasernen (bnr-193867537) tegnet etter SG&CO-illustrasjonene for Fredriksborg: to høye etasjer over lys granittsokkel, vinduene i faste akser (3,4 m) rundt hele bygget, kjellervinduer i sokkelen, to grønne fløydører med overlys mot torget (de to nye inngangene Riksantikvaren godkjente i 2025, én på hver side av hjørnet), uteservering mot torget der statuen står (te-1: lavt dekke, plantekasser, parasoller, som i SG&CO-kveldsbildet), oksøye i arkene over hjørneinngangene, takarker over annenhver akse, 12 piper (årets måneder). Rettelser med grunn, laget av verktoy/kaserna.py.
- Gården lukket: teglmur fra fløyene til brannstasjonen (mu-1, mu-2, sporet målt i ortofoto 2024), porten inn fra gata med rundbue midt i muren. Gjerdelinjene i samme spor tegnes ikke lenger.
- Vinterhagen (vh-1): glasshus med grønne sprosser og taklanterne mot hjørnets gårdsfasade, dør fra hotellet ut i glasshuset.
- Nye vindustyper i tegnekoden: oksøye (typ 3) og grønn fløydør med overlys (bue 2). Regel 14 passer på mu- og vh-id-ene.

## Uten versjon (27.10.2026, ikke publisert) – vinduer og dører etter reglene fra kvartaltegningene
- De 142 antatte husene har fått vinduer og dører etter reglene Gamlebyens hus følger i tegningene, målt på 121 fasit-hus: vindu 0,85 × 1,4 m, brystning 0,9 m, etasjehøyde 3,0 m, akser med lik avstand rundt 2,8 m fra 0,85 m inn fra hjørnet, symmetrisk om veggens midtakse, samme akser i alle etasjer, ingen vinduer under 3 m vegg eller mot nabohus, én dør 1,05 × 2,2 m på gatesiden i midtaksen (ikke på uthus). Rapport: rapport/vinduer/regler-fra-tegningene.md, kontrollark i rapport/vinduer/.
- Regel 17 (vinduer i rytme) passer på dette for de antatte husene. På de gamle dataene: 94 brudd (91 vinduer/dører mot nabohus). Nå 0.
- verktoy/vegger.py: felles kode for veggene på et hus (gatesiden, felles vegg, gårdsrom), brukt av verktøyet, målingen og regelen.

## 33 (26.10.2026, /prove/) – ny intro og hjemmevisning tilbake i kilden
- Light leak i introen, ny hjemmevisning (byen sett fra elva, kirka oppe til høyre, 48°), kirkeskipet senket til målt høyde, vinduer og dører fra v33. Publisert 26.10 kl. 18.43 fra en økt som aldri pushet kilden; hentet tilbake fra den publiserte fila og lagt i main. Vinduene ligger som rettelser med grunn.
- Regel 12 (kontaktskygge) måler 0,1–0,2 % med v33 i hodeløs Chrome mot 2,5 % med v32. Ikke løst; må sjekkes i ekte nettleser.

## På prøve (26.10.2026, /prove/, ikke godkjent) – huskortet bruker statens nøkler
- Hvert bygg har fast id fra Matrikkelen (bygningsnummer), se LESMEG. Huskortet viser offisiell adresse (Kartverket), virksomhetene som holder til i bygget (Brønnøysund), bygningsnummer og om bygget er registrert kulturminne.
- Virksomheter: bare steder en besøkende går inn i (butikk, servering, overnatting, museum). Enkeltpersonforetak uten ansatte og selskapsnavn som ikke er stedsnavn, vises ikke (rettelser med grunn), før virksomhetene legger seg inn selv.
- verktoy/adresser.py hent/koble er byvertens verktøy: kjøres når registrene endrer seg, kobler alt på byggets id.

## 32 (24.10.2026) – kamera uten bråstopp, kontaktskygger (godkjent av Vegar i hånda, /prove/)
- Alle animerte kameraflytt bruker én kurve (glid: eksponentiell inn og ut). Dobbeltklikk-zoom er vår egen (800 ms, MapLibres 300 ms med bråstopp er av), hjem 1,3 s, glidning til huskortet 0,9 s, introen samme kurve. ?glid=0 gir de gamle. Regel 11.
- Kontaktskygger: bånd 1,3 m rundt hver husfot og skive under hvert tre, geometri på bakken (multipliseres inn), stabilt i fart. ?kontakt=0 slår av. Regel 12.
- Filmkurve (lys-og-bevegelse pkt. 1) bygd og testet uten synlig forskjell; avslått (kurve:0), koden ligger for introfilmen. Vignett droppet.
- Lærdom: bevegelse dømmes i bevegelse. Prøvebygg legges på /prove/ (sh publiser.sh prove) og Vegar dømmer i hånda; stills dømmer bare stills. verktoy/film.mjs (styrt klokke) virker, men programvare-GPU-en her bruker ca. 1 min per bilde; opptak gjøres i Vegars Chrome (canvas.captureStream).

## 31.1 (24.10.2026) – stabilt skyggekart
- Vegar på mobil etter v31: «skyggene tegnes hele tiden så det flakker». På en smal skjerm går et dra ut av skyggekartets margin ofte, og hver ny tegning fikk ny skala (R = r·1,4) og nytt senter, så tekselrutenettet flyttet seg og de myke kantene krøp. Nå er dekningen trinnvis (1100 m / 1,5^k) og senteret låst til tekselrutenettet i lysets plan: to tegninger av samme sted gir samme teksler. (Standard metode for stabile skyggekaskader.)

## 31 (24.10.2026) – trekronene er geometri
- Vegar fra mobilen: kronene forsvant fortsatt (nå ved dra oppover), med perfNivaa 0, ingen GL-feil, og samme feil med ?kroner=enkel, utendybde, utenskygge og nospeil. Samme utsnitt tegnet riktig i hodeløs Chrome. Konklusjon: billboard-kronene (tegnede skiver med egen dybdeskriving) oppførte seg annerledes på iPhone-brikken uten at delen kunne pekes ut. Vegar: «lås størrelsene og la dem zoomes som husene».
- Kronene er nå kuler i klaser (SphereGeometry 14×10, instansert, samme klasedata som før) med samme sol, skyggemaske og blekkstrek som husene. Tre toner som før. Skyggekroppene beholdes (kronene skygger ikke seg selv). Nærbilde og hjemmevisning er nesten like v30 (rapport/d-sammenligning/kuler-for-etter-naer.png).
- Borte: lovMat-billboarden, NOISE_GLSL i kronene, gl_FragDepth, ?kroner-bryterne fra 30.3/30.4. ?d=1 (målerute på mobil) og ?nivaa=N står.

## 30.2 (24.10.2026) – trekronene på mobil
- Vegar fanget det på mobilen (skjermbilde kl. 16.55): ved innzooming forsvant alle kronene, stammene stod igjen, og skyggene var borte. Årsak: ytelsestrinn 2 (mobil som sliter) kastet skyggekartet (dispose + null) for å få det bygd på nytt i 1024; etter det tegnet verken skyggene eller kronene (kronene sampler skyggekartet). Reprodusert i hodeløs Chrome med ?nivaa=2 (rapport/d-sammenligning/mobil-nivaa-0-2fix-2.png). Rettet: skyggekartet beholdes og får setSize(1024,1024).
- Trinnene er nå en funksjon (settNivaa) som kan tvinges med ?nivaa=N, så de kan testes uten å vente på måleren.
- Ny regel 10: trinn 2 skal tegne samme bilde som trinn 0 på mobilflate i nærbilde (kronegrønt og avvik måles).

## 30.1 (24.10.2026) – Torvgata: tre gule hus tilbake
- Vegar fra mobilen: «legg spesielt merke til Torvgata. Her mangler det to gule hus bl.a.» Bygg 238, 240 og 313 (Dunkejongården-rekka) var dømt W/G i v30; fotavtrykket projisert på mønehøyde traff det hvite huset med arker bak, ikke det gule foran. Dagens gule beholdt, rettelsene trukket, linje med Vegar som kilde i rettelser.json. Lærdom (i LESMEG): i tette rekker treffer projeksjonen nabohuset bak; dommen må leses mot huset som står under polygonet, og Vegars øye vinner.

## 30 (23.10.2026) – husfarger dømt mot 2019-trykket, trær fra flyfoto på flatene
- Husfarger: 245 hus som står i 2019-trykket er dømt visuelt, ett og ett, mot kontrollark (rapport/farger-dom/ark-01…21.png: 2019-utsnitt med fotavtrykk, dagens farge og agentforslaget). 105 stemte som de stod, 69 er rettet (53 vegger, 45 tak), 65 var ikke synlige (trær, tekstfelt, vann), 4 er egne bygg (kirka, portene). Rettelsene ligger i data/rettelser.json (265 linjer, hvem/dato/grunn), palettbokstavene i farger-dom/palett.json, dommen i farger-dom/dom.txt. Skyggetonene (veggs/taks) nullstilles der fargen byttes, så de avledes av fargen.
- Agentforslaget farger2019.json ble underkjent i mottakskontrollen (bygg 194: lyseblått i trykket, grått i forslaget med «høy sikkerhet»; koblingen fasade→bygg tar nabohuset). Funn underveis: tegneren la plantegningen på mønehøyde og tegnet veggene nedover, så fotavtrykket projisert med affin2 treffer mønet, ikke grunnmuren (rapport/farger2019-hoydeskala.png).
- Trær: flyfoto-forslaget (rapport/traer-flyfoto.json) brukes på flatene (bakke ≤ 1 m, 1 200 punkter), dagens rekker beholdes på vollene (bakke > 1 m, 1 143 punkter): forslaget alene gjorde vollene for tynne mot både trykket og fotoet (rapport/d-sammenligning/traer-for-etter.png mot traer-c-for-etter.png).
- Regel 09: publisert versjon på Pages og i artefaktbygget skal være lik VERSJON. Regel 07 og 08 kjører nå fra hvilken som helst mappe (de var grønne bare fra prosjektmappa).
- Mottakskontroll for agenter i LESMEG: mot briefen, mot kilden (egne stikkprøver), mot beviset.

## 29 (23.10.2026) – sammenslått geometri: 3 077 tegnekall ble 174
- Alle vanlige hus (vegger, tak, gavler, arker, piper) ligger nå i ett nett per materiale i stedet for sju–tolv nett per hus. Hvert punkt bærer byggindeks (aBygg) og høyde for tegnede vinduer (aTopp). Løft (klikk/peker) og vekst (introen) styres per bygg gjennom en 512×1-tekstur (tHus, 05_bygg: settHus), også i skyggekartet (husDybde). Vinduene er ett instansert nett for hele byen.
- Kirka, portbygg og bygg med deler er fortsatt egne grupper (de flyttes som objekter), men hver gruppe er slått sammen til ett nett per materiale (flatGruppe). Det samme for broene, statuen og alle murer og gjerder (09). De usynlige strek-objektene (EdgesGeometry, slått av siden blekkpasset tok over) er borte.
- Peking: treff i et sammenslått nett oversettes fra trekantnummer til bygg (husDeler); treff i vinduer fra instansnummer. Kortet, løftet og kameraglidningen virker som før (d-test.mjs: samme hus valgt, samme skjermpunkt).
- Målt i hodeløs Chrome: tegnekall 3 077 → 174, trekanter 519 k → 525 k (flate normaler på kirka). Bildene er pikselidentiske med v28 i hjemmevisningen, ved klikk og i nærbilde (for-etter-*.png i rapport/d-sammenligning; største avvik 66 av 255 i 1 piksel).
- Igjen: 87 flater i 03 (gress/vann-lapper) og 79 materialnett kan slås videre sammen når det trengs.
- Nye verktøy: verktoy/d-test.mjs (tegnekall, klikk, peker, nærbilde før/etter), verktoy/tell.mjs (teller tegnbare objekter per type og forelder).

## 28 (23.10.2026) – tegnestil bestemt med Vegar: stikkstrek, flate farger, fast sol
- Sola står fast i byen (asimut 250°, høyde 42°), satt så hjemmevisningen har samme lysside som plakaten. Skyggene snur seg med byen når den dreies; skyggekartet trenger ikke tegnes på nytt ved rotasjon. ?sol=plakat gir den gamle.
- Stilbryter STIL (00_oppsett): a = stikkstrek uten skjelving og penselbrudd, flate fasadefarger uten akvarellvask, ingen papirkorn, vignett eller skyskygger, trær i tre toner uten flekker. b = a + skravur i skyggene (vegger og bakke, forankret i byen, 5 skjermpunkter mellom strekene, tynnes ut når de blir for tette). c = 2015-varmen som før, som nullpunkt. Standard er a.
- Stilprøve: ut/stil-{a,b,c}.png og -mobil.png, kontaktark levert til Vegar (stilprove-kirka-ABC.png). Avgjørelse ventes.
- Bakgrunn: Vegar har aldri likt akvarellgreiene og trærne fra 2015-teknikken. Det gamle skal sitte i streken (kobberstikket, jf. Fredrikstad 1776 i kildemappa), det nye i flatene, lyset og UX.

## 27.1 (23.10.2026) – to regresjoner fra 27 rettet
- Trekronene forsvant (mobil, og alle utsnitt tettere enn zoom 1): en kommentar i 13_kart.js svelget resten av linja, så kameraets matriser aldri ble oppdatert. Kronene (billboards fra viewMatrix) og solretningen gikk på gamle matriser. Rettet; øyet ligger nå minst 0,5 m bak nærpunktet, så lookAt aldri degenererer.
- Hvitt blink ved hver bevegelse: «const grunn» ble tilordnet på nytt i oppdaterSol → TypeError i hvert bilde i fart → laget vårt tegnet ikke, kartet viste papirfargen. Rettet (let). Ny regel 07: interaksjonstesten kjøres som regel, og én JS-feil i bruk er rødt.
- Målt i Vegars Chrome etterpå: kartet tegnet 10 bilder, laget vårt 10 (ingen tapte bilder); shift+dobbeltklikk zoomer ut; + zoomer inn; − er grå ved minste zoom (riktig).
- Lærdom: begge feilene kom av tekstpatching (sed/replace) uten å lese linja etterpå, og ingen test beveget kartet. Begge vaktene finnes nå (regel 07; og moduler med lint står i ørneblikk-planen).

## 27 (23.10.2026) – én kvalitet, skyggekart forankret i byen, Mac-knapper
- Én tegnekvalitet i fart og i ro. Før tegnet kartet 3D-bildet i lavere oppløsning og med færre skyggeprøver mens det beveget seg, og skarpt når det stod stille; Vegar så det som pikslete skygger under dra (Mac og mobil). Nå er oppløsning, hjørneskygge og strek like hele tiden (regel 05 skjerpet, kvalitet-test.mjs).
- Skyggekartet er forankret i byen med 40 % margin rundt bildet og tegnes på nytt bare når bildet går ut av dekningen, zoomer, snur over 1,5°, eller husene flytter seg merkbart; myke grunner ventes 150 ms i fart. Før ble det tegnet hvert bilde i fart, og det var det som kostet (målt i Vegars Chrome: 3D-passet 129 ms med skyggekart, 37 ms uten). Store skjermer får 3072²-kart.
- Kameraet sikter mot fjernplanet, ikke nærplanet (når MapLibres nearZ er nær null falt øyet sammen med nærpunktet og retningen ble tilfeldig ett bilde).
- Ytelsesmåleren dømmer etter vår egen tegnetid (render(), CPU), ikke avstanden mellom bildene, og ikke under introen. Trinnene gjelder både i fart og i ro.
- Mac: respectPrefersReducedMotion av («Reduser bevegelse» i macOS slo av alle animasjoner), +/−/kompass-knapper nederst til høyre, ⌘ og rull zoomer på Magic Mouse, shift og dobbeltklikk zoomer ut. Hint-teksten oppdatert.
- Feilsøkingsruta (d): bildefrekvens og tid per pass i siste bevegelse, grunner til skyggetegning, taster m (GPU-måling), n (MSAA av/på).
- Åpent: i Vegars Chrome (claude.ai-verten) går det 50–60 ms mellom bildene som ikke er vår tegning (19 ms) og ikke pikselavhengig (likt ved 1 Mpx og 60 % oppløsning). Skal måles utenfor verten (GitHub Pages) før det jaktes videre.

## 26 (23.10.2026) – MapLibre GL JS som motor
- Kamera, gester, zoom, treghet, grenser og koordinater fra MapLibre 6.14.0 (ESM, pinnet). Byen (three.js 0.160) tegnes som custom layer: three-kameraet settes fra kartets matrise hvert bilde (13_kart.js), øyet utledes av nær- og fjernplanet.
- Perspektiv i stedet for isometri. Plakatvinkelen bevart: pitch 57°, bearing −40° (−130° stående), samme utsnitt som v25 ved zoom 1.
- Blekkpasset lineariserer nå perspektivdybde (nær/fjern fra kartet, i pikselrom); bakgrunnstesten går på rå dybde.
- Styring: dra = flytt, høyreklikk/ctrl-dra = snu og vipp, hjul = zoom, klyp = zoom, to fingre på styreflate = flytt (egen lytter, gest-kontinuitet 120 ms), dobbeltklikk = nærmere, Esc / «Hele byen» = hjem. Mobil: én finger flytter, to fingre klyp/vri/vipp (MapLibre).
- Intro: samme sveip (110°) og zoom, nå som map.easeTo; stoppes av første berøring.
- Kartet tegnes på nytt når noe beveger seg; i ro 10 ganger i sekundet (vannet). Kvalitet følger kameraet som i v24.
- Fjernet: OrbitControls og all egen kamera-/gestkode (13, 15, 16 fra v25).
- MapLibre-CSS ligger i assets (6.14.0) og settes inn i fila ved bygging, så artefaktet ikke trenger eksterne stilark.
- Kjent: skyggene er like v25 (målt med samme testboks: 35 m skygge av 30 m boks i begge). En time gikk til å bevise det.

## 25 (23.10.2026) – kilde som prosjekt
- HTML-en fra artefaktet (versjon 24) delt i data/, src/, assets/. Byggeskript i to modus (enkel, server). PWA: manifest, tjenestearbeider, ikoner fra Fortress Town-logoen.
- Regelsjekker: bygg finnes (flyfoto), høyder fra tegning, fasader fra tegning, vinduer ikke i hjørner, kvalitet bare etter kamera, bygger og laster.
- Innhold likt v24 (porter, broer, 9 spøkelsesbygg skjult, rolig mellom tilstander, gest-kontinuitet, feilsøkingsrute på tasten d).

## 24 (23.10.2026)
- Tegnekvalitet styres bare av kameraet; hus som løfter seg tegnes i full kvalitet. Stillhet 300 ms, speil inn på 0,35 s.
- Styreflate: én gest er flytting eller zoom hele veien.
- 9 OSM-bygg uten bygning i flyfoto skjult.

## 23 (23.10.2026)
- Porter med passasje (Voldporten, Færgeporten; Kongeporten og Mellomporten som portal i mur). Vindebroen med gitterrekkverk og heiseverk; bro fra ravelinet; gangbro nord.
