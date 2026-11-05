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

## Kommentarhistorikk 23.10–05.11 (flyttet ut av koden 05.11)
Kommentarene i src/ sier nå hvorfor koden er slik. Datoene og rekkefølgen stod slik i kommentarene før omleggingen (fil:linje i 3b93557 etter steg 1–2):
- 00_oppsett.js:15: // ---- tegnestil (23.10, bestemt med Vegar): streken er stikkets, flatene er flate, lyset er glatt. 2015-teknikkens varme (akvarellvask,
- 00_oppsett.js:18: // kurve: filmkurven over høylysene (lys-og-bevegelse pkt. 1, 24.10), avslått i kartet.
- 00_oppsett.js:19: // av i kartet (ingen synlig forskjell, 24.10); ?kurve=1 for introfilmen
- 00_oppsett.js:30: // hjemmevisningen (26.10, Vegar: «sluttbildet i dette utsnittet»): byen sett fra elva, kirka oppe til høyre, litt brattere enn plakaten.
- 00_oppsett.js:33: // stående telefon har sitt eget sluttbilde (Vegar 02.11 13:23, skjermbilde fra iPhone: «Uansett versjon vil jeg at denne stillingen skal være siste frame på mobilvisningen»):
- 00_oppsett.js:37: // hjemmevisningens høyde over horisonten: 48° på bred skjerm; 40° på smal (stående telefon), der 48° leses som «for mye ovenfra» (Vegar 28.10)
- 00_oppsett.js:43: /* (02.11) lerretet får ingen MSAA: byen tegnes kantutjevnet i eget mål (01: MSAA + FXAA) og legges over hele lerretet, så MSAA på lerretet var dobbeltarbeid */, reduceMotion:false /* «Reduser bevegelse» av: Vegars valg, CHANGELOG v27 (15_bevegelse) */, pixelRatio: Math.min(devicePixelRatio,2), doubleClickZoom:true, dragRotate:true, touchPitch:true, fadeDuration:0, renderWorldCopies:false });
- 00_oppsett.js:54: // Vegar 28.10; ytelsesmåleren trappet først ned etter 75 trege bilder). ?pix=<millioner> overstyrer.
- 01_etterbehandling.js:16: /* (05.11, Vegar: «refresh-raten + oppløsningen») maskin: alltid 4x MSAA */ type:THREE.HalfFloatType});
- 01_etterbehandling.js:18: // (02.11) minimum-dybden til streken: R32F i samme oppløsning som 3D-passet; uten flyttallsmål (svært gamle nettlesere) regnes den i streken som før
- 01_etterbehandling.js:35: // (02.11) minimum av pikselen og naboen til høyre og over er regnet i et eget pass (tMin, rå dybde): én oppslag i stedet for tre, samme tall
- 01_etterbehandling.js:52: // filmkurve (teknikk 15, 24.10): toppen bøyes av over KNE (230/255) mot TAK (241/255), alt under står urørt, så husfargene (fasit) ikke flytter seg.
- 01_etterbehandling.js:58: // punch (02.11 kveld, Vegar: «før» så mer imponerende ut): i skjermrom, etter fargekoden. Metningen løftes mest der den er svak
- 01_etterbehandling.js:144: // metning ned 7 % (Vegar 03.11 21:34: «litt glorete»): etter punchen, i skjermrom, bare på kartet (papiret rundt står). ?metning=1 gir urørt.
- 02_lys.js:32: // 48°: den faste sola (42°) er svakt gyllen, ikke hvit (28.10)
- 02_lys.js:71: // (04.11) og aldri mens en finger er nede: skyggekartet tegnes når du slipper   // i introen tegnes skyggekartet hvert bilde: sola synker og skyggene vokser
- 02_lys.js:73: // Stabilt skyggekart (24.10, Vegar på mobil: «skyggene tegnes hele tiden så det flakker»): på en liten skjerm går et dra ut av
- 02_lys.js:77: // 28.10: trinnet rundes NED, så R alltid er minst 1,4·r. Med Math.ceil (24.10–27.10) ble R ofte mindre enn bildet: skyggene
- 02_lys.js:109: // Sola finner byen (28.10, Vegar: «A»): i introen er byen overskyet (ingen kastskygger, kjølig), og en solkant vandrer over byen.
- 02_lys.js:114: // overskyet: tydelig mørkere og blåere (28.10 kl. 16.40: 0,86/0,90/0,97 var usynlig i Vegars Chrome)
- kvalitet.js:6: // Regelen: kvaliteten trappes aldri ned av seg selv (Vegar, se CHANGELOG 05.11). Oppløsningen settes av pikselbudsjettet (PIX) og skjermen.
- 03_bakke-vann-grønt.js:12: // BAKKELAG (02.11, avvik A8): flater som ligger nesten i samme høyde (brostein 5 cm, veier 7–10 cm, flater 9 cm, parkering 12 cm,
- 03_bakke-vann-grønt.js:18: // I BROSTEINSFLATEN (02.11, avvik A15): brostein er grunnen der (src/04). En brosteinsflate, et brosteinsbånd i en vei eller et
- 03_bakke-vann-grønt.js:75: // 03.11 (Vegar: «savner livet i vannet, hvordan det skummer langs bryggene»): kai og brygge får også skum, smalere og svakere enn
- 03_bakke-vann-grønt.js:86: // solgløtt (lys-og-bevegelse pkt. 3, 24.10; bygd 02.11 kveld): sola speiler seg i små bølger, så glitteret glir når byen dreies.
- 04_brostein-i-hele-gamlebyen.js:18: // (05.11, Vegar: «virker pixlete» på desktop) fugene er 8 cm: blir de smalere enn en skjermpiksel, flimret de i et kornete mønster.
- 05_bygg.js:53: // ---- kontaktskygge (lys-og-bevegelse pkt. 1, 24.10): et mykt mørke på bakken der hus og trær står, i tillegg til kastskyggen.
- 05_bygg.js:56: // 02.11 kveld: lå på 4 cm, under brosteinen (5 cm) og gresset (28 cm) etter bakkelagene (A8), så regel 12 målte 0,1–0,2 %.
- 05_bygg.js:73: // orientering avgjør hvilken side som er ut: (-ey,ex) peker INN i et mot-klokka polygon (rettet 03.11, båndet lå under husene)
- 05_bygg.js:122: // naturstein (sokkel.type, avvik A10 02.11): skift med ujevn høyde, blokker med ujevn lengde, mørke fuger og
- 06_kirka-bygget-etter-2017.js:5: // Korsarmene (30.10, natt/farge): valm i endene, som kvartaltegningen kirke.ai (trekantet takflate over hver endevegg, ingen gavlvegg)
- 06_kirka-bygget-etter-2017.js:7: // noen av kildene. ENDE = 'gavl' gir saltak med gavlvegg og rundvindu i gavlen (slik det stod 29.10).
- 06_kirka-bygget-etter-2017.js:76: // målt i Kartverkets DOM−DTM 25.10: takfot ca. 8,8 m, møne 14,4 m (før 9,5 + 8,2 = 17,7, 3 m for høyt)
- 06_kirka-bygget-etter-2017.js:112: // korsarmenes endevegger mot sør og øst har dør, som i kvartaltegningen (Vegar 29.10: «det mangler en dør plassert inni en
- 06_kirka-bygget-etter-2017.js:126: // i kilder/bygg-merknader.json, ellers regelen under), så kontrolløren teller de samme vinduene som kartet viser (31.10)
- 06_kirka-bygget-etter-2017.js:148: // høydene (30.10): Kartverkets DOM−DTM ved tårnet har murkronen på 18–19 m (kanten av tårnet) og toppen 32 m midt over
- 06_kirka-bygget-etter-2017.js:153: // Landemerke (Vegar 30.10): tårnet skal fungere dramatisk, ikke korrekt, fordi det brukes til å orientere seg. bygg.kirke.visning
- 06_kirka-bygget-etter-2017.js:172: // spiret: foten er ~1/4 av lanternens bredde (foto Commons «Oestre fredrikstad kirke 01», 2008); 0,3 m ble en nål som forsvant på kartzoom (Vegar 30.10: «for kort»)
- 06_kirka-bygget-etter-2017.js:180: // tårnfoten mot øst har ingen vinduer i tegningen (Vegar 29.10: «på tårnet skal det ikke være vindu vendt mot sør øst»)
- 07_vinduer-dører-og-porter.js:23: // kamerarom som husene (28.10)
- 07_vinduer-dører-og-porter.js:27: // buet topp: port (typ 2) og rundbuevindu (typ 0, bue 1; Tøihuset 30.10)
- 07_vinduer-dører-og-porter.js:37: // sprosser etter zoom (30.10): post og losholt (3,5 cm) og sprossene i nedre ramme (2 cm) holdes minst ~1 px brede
- 07_vinduer-dører-og-porter.js:135: // ---- landemerker (30.10, natt/landemerker): gjenbrukbare elementer som styres av data, ikke engangsfikser ----
- 07_vinduer-dører-og-porter.js:145: // landemerke (Vegar 30.10): visningsskala forstørrer tårnet fra bakken; de målte tallene i dataene står
- 07_vinduer-dører-og-porter.js:184: // felt over arkaden (A.felt {z0, z1, bredde, dybde}, natt/atrium 30.10): etasjen over har høye innfelte felt med samme deling som buene,
- 07_vinduer-dører-og-porter.js:194: // ATRIUM (bygg.atrium, 30.10): innglasset gårdsrom i en ring av tak (ringtaket står i tak2/gavl2, regnet av verktoy/landemerker.py).
- 07_vinduer-dører-og-porter.js:246: // sokkel / natursteinsetasje i egen farge (29.10: tegningen og Street View viser «rød tegl over grå natursteinsetasje»); type naturstein
- 07_vinduer-dører-og-porter.js:255: // takhelning per hus (th) fra Kartverkets høydemodell der den er målt (24.10)
- 07_vinduer-dører-og-porter.js:342: // veggfelt: del av en vegg i egen farge (to fasader under ett omriss i kommunekartet, f.eks. teglgård + pussgård; 29.10)
- 07_vinduer-dører-og-porter.js:352: // fasadesegmenter (30.10): én kropp etter DOM/Matrikkelen, men tegningen viser flere fasader på veggen. Hvert segment er en
- 07_vinduer-dører-og-porter.js:381: // takvinduer: flate vinduer i takflaten (x, y, bredde, høyde langs fallet), som i kvartaltegningene (29.10)
- 08_festningsterrenget.js:17: // TERRENGFLIKER (30.10, data/terrengflikker.json): Kartverkets DTM lagt over det beregnede terrenget der det beregnede er feil
- 08_festningsterrenget.js:32: // Flater og veier legges på den (avvik A16, 02.11): med bilineær høyde og hjørner bare i polygonets punkter skar store flater
- 08_festningsterrenget.js:69: // flate (data/landskap.json, verktoy/bakke.py gater 29.10): kjøreveier lagt med brostein tegnes med brosteinen, ikke gategrått
- 08_festningsterrenget.js:70: // heller og grus (kaia, plassene, stiene på vollene) får flatens farge, som flatene i 17 (30.10)
- 08_festningsterrenget.js:74: // båndet legges på terrenget (avvik A8, 02.11): punktene i dataene står med opptil 30 m mellomrom, og en rett bit mellom dem
- 09_murer-plankegjerder-og-voller.js:16: // gjerdelinjer som ligger i sporet til en teglmur (data/teglmurer.json), tegnes ikke: teglmuren erstatter dem (27.10, Kaserna)
- 09_murer-plankegjerder-og-voller.js:18: // gjerder, murer og hekker sett i ortofoto 2024 (data/gjerder.json, verktoy/bakke.py gjerder 29.10): {typ, p, h}; gammel form (bare punkter) = gjerde
- 10_porter.js:23: // VINGEMURER (30.10): skrå murer som holder vollen ved porten. [x0, y0, x1, y1, h0, h1, tykk]: innerflaten fra porthjørnet ut til
- 12_trær.js:16: // dybdeskriving og egen skyggeoppslag fram til 24.10; på iPhone forsvant de ved zoom og dra uten at noen av delene kunne pekes ut
- 12_trær.js:34: // solRetning() er i kamerarommet (three.js); normalen må dit, ellers dreier lyssiden med kameraet (28.10)
- 14_speilinger-i-vannet.js:9: // 29.10: speilet toner ikke lenger ut når kartet beveger seg. Det tegnes på nytt høyst hvert BEV.speilMs ms i fart (og hvert bilde i ro
- 14_speilinger-i-vannet.js:20: // (05.11) speilet i full oppløsning på maskin, halv på telefon
- 14_speilinger-i-vannet.js:25: // (02.11) matrisen sammenlignes direkte, ingen ny tekst per bilde
- 14_speilinger-i-vannet.js:49: // stående telefon: sentrum for sluttbildet (Vegar 02.11, se 00_oppsett STAAENDE)
- 14_speilinger-i-vannet.js:50: // ny hjemmevisning (26.10): midt i byen, torget litt under midten   // ?tx=&ty= setter startpunktet (test)
- 15_bevegelse.js:4: // ---- bevegelse: én modul for varighet og kurver i hele kartet (oppdrag 15, 29.10; kilder: rapport/flyt/kilder.md) ----
- 15_bevegelse.js:22: // s: en avbrutt intro henter inn lyset og uskarpheten på denne tida (28.10)
- 15_bevegelse.js:31: // (CHANGELOG v27, 23.10: «respectPrefersReducedMotion av ("Reduser bevegelse" i macOS slo av alle animasjoner)»; bekreftet av hovedagenten
- 15_bevegelse.js:32: // 29.10). Valget het feil i MapLibre 6 og ble ignorert; riktig navn er reduceMotion:false i kartvalgene (00_oppsett).
- 15_bevegelse.js:42: // ---- treghet etter dra, klyp og vri (29.10) ----
- 15_bevegelse.js:50: // slipplogg (04.11, Vegar: «den flytter seg fremdeles når jeg slipper tommelen»): hvert slipp og hvert kameraflytt de neste 600 ms
- 15_bevegelse.js:61: // Hoppet er ikke bevegelse. Tas det med, leses det som et kast (Vegar 02.11, mobil: «hopper bildet ganske langt mot venstre når jeg
- 15_bevegelse.js:65: // fingerNede: minst én finger er på kartet (leses av 15_loop og 02_lys: ingen tunge pass mens fingeren er nede, 04.11)
- 15_bevegelse.js:96: // På en treg telefon kan behandlingen komme 100–300 ms etter at fingeren løftet; da gikk vi (02.11) til MapLibres treghet, som regner
- 15_bevegelse.js:97: // farten med tommelhoppet inne (sprett). Natt til 04.11 lot jeg i stedet målevinduet vokse med bildetiden, og da fikk en finger som
- 15_bevegelse.js:98: // hadde STOPPET fart fra bevegelsen før stoppet (Vegar 04.11: «kartet glir litt mot høyre» når tommelen slipper). Nå: har fingeren
- 15_bevegelse.js:121: // ---- musehjul (29.10): jevn zoom i stedet for ett utslag per hakk ----
- 15_lenke.js:5: // ---- lenka husker utsikten (02.11): #view=lat,lon,zoom,pitch,bearing&hus=<bygg-id> ----
- 15_loop.js:42: // introen om igjen (Vegar 04.11: «når man klikker på hele byen ønsker jeg at introen starter igjen»): samme løp som ved lasting,
- 15_loop.js:54: // ---- Sola finner byen (28.10, Vegar: «A») ----
- 15_loop.js:57: // godkjente 42° (23.10), så skyggene blir lange idet kameraet lander. Lyset er bundet til kameraets vei (bearing), ikke til klokka
- 15_loop.js:70: // en kurve til oppå gjorde at sola var over byen på 0,6 s (målt i Vegars Chrome 28.10 kl. 16.30)
- 15_loop.js:77: // avstanden fra startvinkelen, målt den korte veien rundt, delt på sveipet. Før 28.10 kl. 16 ble u regnet med fortegn fra plakatvinkelen
- 15_loop.js:87: // (Vegar 28.10: «ytterkantene er blury helt til introen er ferdig, og da blir alt skarpt samtidig»). Uten solintro: ut over de siste 40 %.
- 15_loop.js:91: // avbrutt intro (29.10, oppdrag 15): før ble tiltU satt til 1 i bildet etter avbruddet, så uskarpheten forsvant på ett bilde (målt i
- 15_loop.js:129: // speilet (29.10): toner inn én gang etter introen og blir stående. I fart tegnes det på nytt høyst hvert BEV.speilMs ms; mellom gangene
- 15_loop.js:131: // (02.11) uten vann i bildet tegnes ikke speilet (21_flyt: vannISyne); kommer vannet inn, tegnes det i samme bilde (nøkkelen er ny)
- 15_loop.js:135: // (04.11) aldri et speilpass mens en finger er nede: det var støtene som hakket på telefonen; det forrige speilet følger kameraet imens
- 15_loop.js:136: // (04.11) kvalitetstrinnet byttes bare når kartet står: midt i et dra kjentes det som at kartet «hentet seg inn»
- 15_loop.js:148: // ber kartet tegne på nytt når noe beveger seg; i ro tegnes det 30 ganger i sekundet på maskin (05.11, Vegar: «refresh-raten»), 10 på telefon, når vann er i bildet (vannet lever), ellers ikke (02.11)
- 15_loop.js:149: // (29.10) også mens en avbrutt intro henter inn lys og uskarphet: før gikk det med 10 bilder/s når kartet stod, så uskarpheten
- 15_loop.js:153: // testene venter på dette i stedet for et fast antall sekunder (tomler_test, 03.11)
- 16_interaksjon.js:33: // ---- huskortet (oppdrag 15, 29.10): klikk -> huset løfter seg og kameraet glir inn, kortet glir inn (mobil: bunnark fra bunnen, som
- 16_interaksjon.js:44: // tomt kort fremfor plassholder: det som vises, er ferdig (27.10)
- 16_interaksjon.js:46: // bygg delt i fløyer (husdeling «felles_tak», 31.10 Tøihuset): fløyas egne steder øverst; de andre fløyenes og de uten kjent plass under «Også i …»
- 16_interaksjon.js:116: // «Hele Gamlebyen» spiller introen på nytt (Vegar 04.11), på mobil og bred skjerm; Esc glir bare hjem som før
- 17_bakkeflater-og-parkering.js:8: // ---- bakkeflater og parkering (27.10): plenene (OSM, rettet mot ortofoto 2024), gresset i gårdsrommene slik ortofotoet viser det,
- 17_bakkeflater-og-parkering.js:23: // bed (bar jord) og brostein utenfor brosteinsflaten kommer fra ortofotoet (verktoy/bakke.py overflater, 29.10)
- 17_bakkeflater-og-parkering.js:67: // (brostein i Gamlebyen) og bare oppmerkingen tegnes: den glatte parkeringsflaten oppå brosteinen var «noe rart foran huset» (avvik A3, 02.11)
- 18_brygger.js:5: // ---- brygger (27.10): fergeleiet, gjestebrygga i Toldbodgaten, Isegran og båtplassene langs Glomma, fra data/brygger.json
- 19_gardsmurer-og-vinterhager.js:6: // ---- gårdsmurer i tegl med rundbueport, glasshus (vinterhager) (27.10, Kaserna etter ombyggingen; data fra verktoy/kaserna.py) ----
- 19_gardsmurer-og-vinterhager.js:19: // åpninger der et portbygg står i muren ([fra, til, id] i meter langs muren, verktoy/kaserna.py): muren tegnes ikke gjennom buen (avvik A2, 02.11)
- 19_gardsmurer-og-vinterhager.js:82: // (granittsokkelen som eget bånd 16 cm utenfor veggen er tatt ut 02.11, avvik A9: på Artillerigården (sokkel 3,1 m) dekket den
- 20_statuen-paa-torvet.js:24: // kontrollert mot Wilse 1931 og nb.no 1969. Posituren rettet 30.10 etter Street View mai 2024 (rett forfra, fra vest-nordvest) og
- 20_statuen-paa-torvet.js:30: // jernsko (sabaton): avrundet, ikke kasse (30.10)
- 20_statuen-paa-torvet.js:35: // pluderhoser/lårplater: buklet profil (30.10)
- 20_statuen-paa-torvet.js:38: // brystharnisk: rundet bryst, smalt mot beltet (30.10)
- 21_flyt.js:6: // ---- flyt uten lavere oppløsning (02.11, Vegar: «ikke dårligere oppløsning, heller motsatt») ----
- 22_byferga.js:6: // ---- Byfergene (03.11 og 04.11, Vegar: «se byferga entre kaia i gamlebyen i introswipen», «koble fergetider til fergen») ----
- 22_byferga.js:7: // To like båter (Vegars tegning 03.11 22:04): rødt skrog som dominerer, lang hvit salong med en rekke vinduer, styrhus og åpent dekk
- 22_byferga.js:22: // skroget: boks med avfasede ender. Rampeenden (+x, baugen mot kaia) er flat og bred, den andre enden er spisset (Vegar 03.11 22:46)
- 22_byferga.js:48: // (05.11, regel 19) båtene kaster ikke i skyggekartet: det skal stå stille når kartet står, og en båt i fart ville tegnet det på nytt hele tiden
