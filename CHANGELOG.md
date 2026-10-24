# Endringslogg

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
