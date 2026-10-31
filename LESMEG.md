# Gamle Fredrikstad – tegnet 3D-kart (Smart Old Town)

Kilden til kartet. Alt som publiseres bygges herfra; ingenting rettes i ferdig HTML.

    python3 bygg.py enkel     én fil (ut/enkel/index.html) – til artefakt, e-post, test
    python3 bygg.py server    ut/server/ – legges på hvilken som helst webserver; installerbar som app (PWA), virker uten nett etter første besøk
    python3 regler/kjor.py    kjører alle regelsjekkene, skriver rapport/rapport.md og bevisbilder

## Mapper
- data/      én JSON per emne (bygg, veier, vann, trær, legende, porter, broer …). Hva hvert felt kommer fra: KILDER.md
- src/       koden, én fil per del, i rekkefølge (00_oppsett … 16_klikk). stil.css, kropp.html, mal.html, manifest, sw.js
- assets/    teksturer (vann, pensel), app-ikoner, logo
- regler/    Vegars regler som kjørbare sjekker; hver skriver rapport/<regel>.md og evt. bevisbilde
- kilder/    referanser som sjekkene måler mot (flyfoto med transform)
- verktoy/   hjelpere (hodeløs lasting, rendring)
- ut/        bygd resultat (ikke kilde)

## Status 23.10.2026 (v30)
Motor: MapLibre GL JS 6.14.0 (kamera, gester, koordinater). Byen: three.js 0.160 som custom layer. Koden er filer i rekkefølge i ett modulskop (ikke ekte ES-moduler ennå).
Geometrien er slått sammen (v29): vanlige hus ligger i ett nett per materiale med byggindeks per punkt; løft og vekst per bygg går gjennom hus-teksturen tHus (05_bygg: settHus). Et hus som skal endres, endres i data (rettelser.json) og bygges på nytt, ikke i scenen. Grupper som flyttes som objekter (kirka, portbygg, bygg med deler, broer) slås sammen med flatGruppe.
Neste: kvalitetssikring kvartal for kvartal (bevisark tegning mot modell), deretter regel 02–04 grønne. v30: husfarger dømt visuelt mot 2019-trykket (rapport/farger-dom, rettelser i data/rettelser.json), trær fra flyfoto på flatene og dagens rekker på vollene. Åpne datakilder til POI-laget: rapport/apne-data.md.

## Sola finner byen (28.10)
Introen: overskyet → solkant vandrer over byen → kastskygger vokser fram → sola lander på 250°/42°. Lyset følger kameraets vei (bearing),
så det er riktig uansett bildefrekvens; avbrutt intro henter resten inn på 0,8 s. Shaderen: `solHer(wq)` i GL_SOL_F (02_lys) gir 0–1 per
punkt, `skyggeMask()` og de lyse tonene blandes med den; `U_SOL` deles av alle materialer gjennom `kobleSol()` (15_loop ved load).
Stillbilder langs veien: `node verktoy/sol-intro-stills.mjs ut/enkel/index.html rapport/_sol` (u 0, 0,25, 0,5, 0,75, 1), fordi
programvare-GPU-en ikke kan vise introen i fart; dommen i fart er Vegars, på /prove/.

## Faste ID-er: bygningsnummeret fra Matrikkelen (26.10)
Hvert bygg har en fast nøkkel i `id`: `bnr-<bygningsnummer>` når bygget finnes i Matrikkelen (Kartverket, CC BY 4.0), ellers `pb-<løpenummer>`. Bygningsnummeret er statens nøkkel, den samme kommunen, Forsvarsbygg, meglere og Riksantikvaren bruker, og det finnes i alle norske byer. `matrikkel` på bygget har bygningsnummer, uuid, bygningstype, kulturminne/SEFRAK og adresse- og matrikkelenhet-id (eierkoblingen).
Rettelser, porter og legende peker på id, aldri på plass i lista. Alle id-er som er delt ut, står i kilder/id-register.txt; en id slettes aldri, bygget skjules med grunn. Regel 14 passer på dette.

    python3 verktoy/matrikkel.py hent     henter bygningspunktene (kilder/matrikkel-bygningspunkt.json)
    python3 verktoy/matrikkel.py koble    gir nye bygg id, oppdaterer matrikkelfeltet, rører aldri en id som finnes

All lesing og retting av data går gjennom datalag.py, som bygg.py, regelsjekkene og verktøyene deler.

## Rettelseslaget (23.10)
Grunndataene i data/ er generert (OSM, trykkfila, kvartaltegningene) og kan lages på nytt. Alt Vegar retter ligger i data/rettelser.json, én linje per rettelse, og legges oppå ved hvert bygg:

    [{"emne":"bygg","id":"bnr-193867537","op":"sett","felt":"vegg","verdi":[214,96,80],"hvem":"Vegar","dato":"2026-10-24","grunn":"trykkfila"},
     {"emne":"bygg","id":"pb-12","op":"skjul","hvem":"Claude","dato":"2026-10-23","grunn":"flyfoto: parkeringsplass"}]

Operasjoner: sett (felt = verdi), skjul og ny. Rettelser slettes aldri, de overstyres av en nyere linje (et skjult bygg vises igjen med `sett skjul null` og grunn).

`ny` (29.10) legger til et objekt grunndataene ikke har: `{"emne":"bygg","id":"pb-25","op":"ny","verdi":{…hele bygget, med id…},"hvem":…,"dato":…,"grunn":…}`.
datalag.legg_paa_rettelser lager alle nye objekter først (bakerst i lista, i rekkefølgen de står), så sett/skjul kan peke på dem uansett hvor
linjen står; samme id i flere ny-linjer: den nyeste vinner; en ny-id kan ikke finnes i grunndataene. Plassene til grunndataene endres aldri
(rapport/hoyder og regel 02 bruker plass i lista). Id-en registreres i kilder/id-register.txt som alle andre, og regel 14 teller nye bygg med.
Redigeringsmodusen skal skrive nye objekter på samme måte. Flytting er `sett p`.

## Vinduer og dører på hus uten tegning (27.10)
Fasit er husene lest fra kvartaltegningene (`fasade_kilde: kvartaltegning` og v33-rettelser). De andre (`antatt`) får vinduer og dører fra reglene målt på fasiten:

    python3 rapport/vinduer/mal_tegningene.py    måler fasit-husene på nytt (rapport/vinduer/maalinger.json)
    python3 verktoy/vinduer_regler.py           lager vind for de antatte husene som rettelser (idempotent; --tørt viser bare)
    python3 rapport/vinduer/kontrollark.py      fasadetegninger før/etter og fasit til sammenligning

Endres h på et antatt hus, kjøres vinduer_regler.py på nytt (rettelser følger ikke høyden av seg selv; regel 17 sier fra).

## Bakkeflatene mot ortofoto 2024 (27.10)
Fasit for torg, gater, plener, gårdsrom og parkering er kommunens ortofoto 2024 (bare kontroll, ikke i git, se KILDER.md).

    python3 verktoy/flater.py hent        ortofotofliser + kommunens parkeringslag
    python3 verktoy/flater.py id          faste id-er til grønt (gr-) og gårdsrom (ga-)
    python3 verktoy/flater.py parkering   data/parkering.json og data/flater.json fra kilder/flater-maalt.json (flater målt for hånd)
    python3 verktoy/flater.py maal        gress i gårdsrommene og klipping av grønt over parkering, som rettelser
    python3 verktoy/flater.py ark etter   kontrollark per område i rapport/flater/

Tegnes i src/17_bakkeflater-og-parkering.js (plener, gårdsrom, målte flater, parkering). Regel 15 måler avvikene.

## Vannet mot ortofoto 2024 (27.10)
Fasit for strandlinja (Glomma, vollgravene, kaiene, Isegran) er det samme ortofotoet. data/vann.json er OSM-vannet (kilder/vann-osm.json) rettet mot vannmasken fra fotoet, med fast id (vn-) og kanttype per kant: k = kai/mur/brygge, n = naturlig. Kanttypen og det fotoet ikke ser (smale grøfter i sivet) står for hånd med grunn i kilder/vann-maalt.json. Under trekroner og takutstikk (kartets egne trær og hus) gjelder OSM-kanten.

    python3 verktoy/vann.py hent        ortofotoflisene over hele kartrammen
    python3 verktoy/vann.py maske       vannmasken (kilder/ortofoto-2024/vannfasit.png, ikke i git)
    python3 verktoy/vann.py lag         data/vann.json og data/vannfelt.json (g-kanalen = kai, r = avstand til land)
    python3 verktoy/vann.py kontroll    kontrollark før/etter per strekning i rapport/vann/ (bildene ikke i git) og avvik.json

Tegnes i src/03_bakke-vann-grønt.js: naturlig kant skyller inn med skum, kai og mur står rett og rolig. Regel 16 måler.

## Bryggene mot ortofoto 2024 (27.10)
Fergeleiet (Gamlebyen og Sentrum), gjestebrygga i Toldbodgaten, Isegran og båtplassene langs Glomma. OSM gir strukturen (omriss, flytende eller fast); ortofotoet avgjør om brygga finnes og hvor. Det OSM mangler, er målt for hånd i fotoet (kilder/brygger-maalt.json, med grunn), og «sett» der er lista over bryggene som synes i fotoet, som regel 18 teller mot. Faste id-er (br-) med ankerpunkt (kilder/brygger-anker.json) som vannflatene. Typer: fast (på stolper, ca. 1 m over vannet), flytebrygge (ca. 0,4 m), utrigger (smal bom).

    python3 verktoy/brygger.py hent     OSM over kartrammen (kilder/brygger-osm.json)
    python3 verktoy/brygger.py maal     data/brygger.json (utriggerne i en «rad» flyttes til der fotoet viser bommene)
    python3 verktoy/brygger.py ark      kontrollark før/etter per område i rapport/brygger/ (bildene med ortofoto ligger bare lokalt)

Tegnes i src/18_brygger.js. Regel 18 måler dekning, at ingen brygge står på land (data/vann.json), og at fotoet viser brygge under hver av dem.

## Grå hus: fargene i tegningen som vektor (28.10, forsøk, ikke lagt inn)
132 hus i Gamlebyen står hvite/grå; 48 av dem er dømt riktige mot 2019-trykket (hvite hus), 39 har fått trykkets farge, og 43 mangler dom
(20 var skjult av trær/tekst i trykket, 23 står utenfor det dømte arket). 165 hus utenfor vollene har ingen farge i noen tegning.
Gamlebyen+Isegran2017.ai (Dropbox, Gamlebyen kart tegning) er samme artwork som 2019-trykket og har lagene i behold, så husflatene kan
leses som vektor uten trær (verktoy/farger_tegning.py, kilder/ai bare lokalt). Registreringen tegning→trykk er på 1,4 px, men
modell→trykk (fra px2019 i rapport/farger2019.json) er på 5–25 px, og husene er tegnet fritt, så fotavtrykket treffer ofte nabohus,
gate eller tre. Forslagene i rapport/farger-tegning/forslag.json er derfor ikke lagt inn. Veien videre er den samme som for v30:
kontrollark per hus der Vegar dømmer, eller Street View-runde som i 2015.

## Grunnmuren fra kommunekartet (29.10)
Fasit for husomrissene i Gamlebyen er kommunens oppmålte omriss (FKB), lest som vektor fra kommunekartet Vegar lastet ned fra kartportalen
(kilder/kommunekart/kommunekart.pdf, bare lokalt; transformasjonen til modellmeter i pdf_til_modell.json). Kommunekartet brukes som mål for vår
egen modellering, ikke vist i kartet. Alt legges inn som rettelser med grunn som begynner med «kommunekart FKB 29.10».

    python3 verktoy/grunnmur.py            omriss, tak, nye bygg, matrikkelfelt, piper/arker, tegnede vinduer flyttet (idempotent)
    python3 -I rapport/hoyder/hent.py      høydene måles på nytt på de nye omrissene (forskyvningen står fast fra tall.json)
    python3 -I rapport/hoyder/legg_inn.py
    python3 verktoy/grunnmur.py            andre gang: nye bygg får første høydegjetning, alt annet er likt
    python3 verktoy/vinduer_regler.py      vinduer på antatte hus etter de nye veggene og naboene
    python3 verktoy/grunnmur.py ark        kontrollark rapport/grunnmur/oversikt.png (ikke i git); plan og tall i rapport/grunnmur/plan.json

Per hus i Gamlebyen (verktoy/kommunekart.py: i_gamlebyen; bare hus helt innenfor kartrammen):
- én-til-én: `sett p` (og ph, r, rf, tk); id, farger og vinduer følger huset.
- ett modellhus over flere kommunehus: delen der husets matrikkelpunkt står, beholder id-en; resten blir nye bygg (`ny`). Tegnede vinduer
  som står på en utskilt del, følger med dit (delen får `fasade_kilde: kvartaltegning` og `fasade_fra`).
- flere modellhus i ett kommunehus: kommunens omriss deles mellom dem (nærmeste modellhus), så alle id-er beholdes.
- kommunehus uten modellhus: står et skjult modellhus der, vises det igjen med kommunens omriss (alle 9 skjult 23.10 etter Google-flyfotoet
  står i kommunekartet og i ortofotoet); ellers nytt bygg med `bnr-` fra et matrikkelpunkt som hører til omrisset, eller neste `pb-`.
  Under 6 m² hoppes over og listes. Nye hus får nøytral farge (vegg 226/222/212, tak 150/144/138) til Vegar velger.
- modellhus uten kommunehus slettes aldri; skjules bare når Kartverkets DOM−DTM ikke har noe over 1 m og huset ikke har navn.
- røres ikke: kirka, Kaserna, portbyggene. Flater i PDF-en som ligger inni en større flate er bygningsdeler (tas bort), med mindre
  matrikkelen har et eget bygg i dem.
Taket regnes fra fotavtrykket for hver husrekke med et endret hus (verktoy/tak.py, rett skjelett); gavlene arves fra det gamle taket der
veggen står omtrent samme sted, ellers tak.gavl_regel. Regel 20 måler resultatet (IoU >= 0,7 per kommunehus, ingen modellhus over to).
verktoy/matrikkel.py koble jobber på grunndataene; kjør grunnmur.py etterpå, så matrikkelfeltet på de rettede husene følger omrisset.

## Fasadene fra Street View (29.10)
En agent leste fasadene av i Google Street View i Vegars Chrome: kilder/streetview/avlesning.json (77 hus, bare tall og ord; bildene
ligger aldri i repoet). Fargene legges inn av verktoy/streetview_farger.py, fasadene av:

    python3 verktoy/streetview_fasader.py          vinduer per etasje, dører, arker og piper på gatesiden (idempotent; --tørt viser bare)
    python3 verktoy/streetview_fasader.py ark      kontrollark rapport/streetview-fasader/ark.png (endret) og ark-fasit.png (fasithus)

Gatesiden er veggen som vender mot kamerapunktet (viewpoint i pano_url) innenfor heading ± 35°, uten hus i siktlinja. Vinduene står
etter reglene i vinduer_regler.py (akser, brystning, etasje, hjørneklaring), men med antallet fra bildet; dørene der friteksten sier
(venstre/midt/høyre, sett fra kameraet). Huset får `fasade_kilde: streetview` og `fasade_sv` (veggen som er sett), så vinduer_regler.py
lar det være; regel 17 sjekker det med to lettelser som følger av kilden (dør på den sette veggen, overtallige vinduer i en etasje
med flere vinduer enn etasjen under). Fasithusene fra kvartaltegningene endres ikke, bare sammenlignes
(rapport/streetview-fasader/sammenligning.md). Hus der merknaden sier at det er usikkert om det er riktig hus, står med grunn i
kilder/streetview/hopp.json. Har gateveggen ikke plass til tallene, hoppes huset over og listes (trolig feil vegg eller feil hus).
Rekkefølge: grunnmur.py → vinduer_regler.py → streetview_fasader.py (kjøres på nytt når omriss eller h endres).

## Registeret: fasiten for hva som skal finnes (29.10)
kilder/register/gamlebyen.json har ett element per kommunehus i Gamlebyen (FKB-omriss innenfor avgrensningen til grunnmur.py),
koblet til Matrikkelens bygningsnummer, Kartverkets adresser og modellens id, med areal (fotavtrykk), høyde-, fasade- og fargekilde,
Street View-status og om huset har kort. Nøkkelen er tyngdepunktet (`fkb-x_y`), ikke plassen i PDF-en. Telling og hull med grunn:
kilder/register/avstemming.json. Boligareal/bruksareal finnes ikke i åpne data (krever innlogging i Matrikkelen); byggeår heller ikke.

    python3 verktoy/register.py hent      adresser i hele avgrensningen, alle postnumre (kilder/register/adresser-omraade.json)
    python3 verktoy/register.py           registeret, avstemmingen og Street View-gålista (kilder/register/streetview-mangler.json)
    python3 verktoy/register.py kort      huskort: nye for adresser uten kort (bakerst i data/adresser.json); kort som står i et annet hus
                                          enn adressepunktet, flyttes dit (bare bygg_id; kortet følger adressepunktet etter grunnmuren)
    python3 verktoy/register.py ark       kontrollark rapport/register/oversikt.png (bare lokalt)

Rekkefølge: adresser.py koble skriver data/adresser.json på nytt fra grunndataene, så register.py kort kjøres etter den.
Soner: «gamlebyen» = huset står i et kommunehus i avgrensningen; «randsone» = huset er i modellen, men utenfor kommunekartets ramme
(Heibergs gate, Cicignongata, Bings gate …); «utenfor» = utenfor avgrensningen (Nabbetorpveien, Prestelandet, Gudeberg allé …).
Regel 21 regner registeret på nytt og er rød når en adresse i Gamlebyen mangler hus eller kort, et kort står i et annet hus enn
adressepunktet, eller et kommunehus (eller en adresse i randsonen) mangler hus uten unntak med grunn i kilder/register/unntak.json.

## Byggene: kjeden, merknadene og det som står på taket (29.10, natt/bygg)
Rettelseslaget lar nyeste linje vinne, og hvert verktøy flytter sine linjer bakerst når det kjøres. Derfor er rekkefølgen fast:

    python3 verktoy/grunnmur.py              omriss og tak fra kommunekartet (planlegger uten id_flytt sine linjer)
    python3 verktoy/id_flytt.py              hus over på riktig bnr-id etter Matrikkelen (kilder/id-etter-matrikkel.json)
    python3 -I rapport/hoyder/hent.py        høydene måles (hoyder.json har id per hus; plassen i lista brukes ikke lenger)
    python3 -I rapport/hoyder/legg_inn.py    høyde og takhelning på id
    python3 verktoy/vinduer_regler.py        vinduer etter reglene på antatte hus
    python3 verktoy/streetview_fasader.py    Street View, alle sider («sider» i avlesningen); veggen etter retningen når kamerapunktet bommer
    python3 verktoy/fasade_tegning.py les_fra_kontroll   koblingen tegning↔hus fra forrige kontroll (kilder/fasade-kobling-kontroll.json,
                                             skrevet av `kontroll.py avvik`); håndkoblingen i fasade-kobling.json går foran. To runder
                                             kjede→bygg→kontroll gir samme kobling (sjekket 30.10, «stabil»)
    python3 verktoy/fasade_tegning.py legg_inn   vinduer fra kvartaltegningene som vektor (kilder/fasade-tegning/, se under)
    python3 verktoy/streetview_farger.py     veggfarger fra Street View 2016+ (fargeregelen, se «Fargene» under)
    python3 verktoy/tak_farge.py             takfarger: ortofoto 2024 (mellombåndet pikselvis: falmet tegl eller grått), tegningen bare der fotoet ikke ser
    python3 verktoy/vegg_nye.py              veggfarger: tegningen > Street View før 2015 > nabohuset; farge_kilde
    python3 verktoy/bygg_merknader.py        merknadene på enkelthus (kilder/bygg-merknader.json): Vegars kvartalskontroll og avgjørelser mot kildene
    python3 verktoy/fasade_former.py         former fra tegningen (rundbuevinduer, portaler, piper; kirkas høyder og silhuett)

Høydene følger id-en (29.10): hoyder.json var nøklet på plassen i bygg-lista. Når et nytt bygg kom inn foran de andre nye byggene
(rettelser med op ny), flyttet alle plassene seg ett hakk, og målt høyde havnet på nabohuset. Nå har hver måling id, legg_inn.py og
regel 02 slår opp på id.

Piper og arker står på taket: datalag.hoyden_styrer regner høyden fra takflatene (h + t·th) hver gang, og pipene flyttes opp til
mønet (datalag.til_monet; `piper_fri: true` på huset slår det av). Før ble høyden lagret og flyttet med høydeendringen, og en rettelse
regnet mot ny høyde ble flyttet en gang til (arker på −2,08 m). Regel 13 sjekker at piper og arker står på takflaten.

Nye felt på bygg (tegnes i src/07): `takform: "knekk"` (knekktak/mansard, takflatene deles ved bruddet i datalaget, datalag.KNEKK),
`sokkel: {h, farge, skygge}` (natursteinsetasje i egen farge), `takvinduer: [[x, y, bredde, høyde]]` (flate vinduer i takflaten),
`veggfelt: [[x1, y1, x2, y2, r, g, b]]` (del av en vegg i egen farge: to fasader under ett omriss i kommunekartet).

Kvartaltegningene som vektor (verktoy/fasade_tegning.py, under arbeid): flatene i .ai-fila er egne stier, vinduer og dører er hull i
veggflatene. Verktøyet legger modellen inn i tegningen (globalt kamera, så per blokk og per hus, kantmatching mot strekene), kobler
flatene til modellvegger og leser elementene i andel av veggen. Koblingen er ikke sikker nok alene der tegningen er satt sammen av
biter eller frihånd avviker mye (Kvartal3, Kvartal4BITMP); kilder/fasade-kobling.json tar flate -> «id/vegg» for hånd.
Kontrollark per kvartal: verktoy/bygg_ark.py (rapport/bygg/kvartal-<tegning>.png). Utsnitt med ortofoto og DOM: verktoy/se_her.py.

Koblingen for hånd (30.10) har disse formene per hus i kilder/fasade-kobling.json: `17` (flaten, siden etter bunnkanten),
`"11/SØ"` (siden gitt), `"19/SV@4"` (veggen gitt, indeks i vegger.vegger slått sammen), `{"f": [27, 46], "side": "SV@6", "fra": 0,
"til": 0.755}` (tegningen viser flere modellhus i én vegg: husets del) og `{"f": [19], "side": "SØ@1", "plass": [0.58, 1]}` (flaten er
bare en del av modellveggen). Hull i flaten er vinduer og dører; dører tegnet som egne flater oppå veggen, også i et hakk i
bunnkanten, telles med; biter av samme dør slås sammen; et hus med én etasje får én rad. Alle 17 tegninger er lest (Tøihuset fra
Dropbox, scanninger). Vegger tegningen ikke viser: Street View der kameraet så veggen (streetview_fasader.py skriver
rapport/streetview-fasader/fasit-sv-vegger.json for fasithusene), ellers reglene.

    python3 verktoy/sv_avvik.py          tegningshus som avviker fra Street View: feil vegg / feil vindu / endret siden 2015 (rapport/bygg/sv-avvik.md)
    python3 verktoy/bygg_naer.py visninger | ark    nærbilder ved største zoom og pikseltetthet 2 ved siden av tegningen (rapport/bygg/naer/)

Sprosser (src/07): post og losholt holdes minst ~1 px brede og tones ut over 0,2–0,32 m per piksel; sprossen i nedre ramme (seks ruter)
vises først under 0,075–0,13 m per piksel (største zoom på mobil). Største zoom i kartet er zoom 6 (src/00, maxZoom).
## Parkering og statuen på Torvet (29.10)
Parkeringen er kommunens: verktoy/parkering.py lager data/parkering.json fra kommunens parkeringslag (kilder/parkering-kommunen.json),
reglene og prisene fra kommunens sider (kilder/parkering-regler.json) og flatene målt i ortofotoet (kilder/flater-maalt.json og
kilder/parkering-maalt.json). Hver plass får kategori (hc, el-lading, beboer, buss, bobil, avgift, tidsbegrenset) etter regler på
kommunens type/navn/kommentar, regler i klartekst og kilde-URL. Antall skrives bare der kommunen oppgir det. verktoy/flater.py parkering
kaller den samme koden.

    python3 verktoy/parkering.py hent       kommunens lag på nytt, med liste over nye/borte/endrede plasser
    python3 verktoy/parkering.py lag        data/parkering.json
    python3 verktoy/parkering.py ark [orto] rapport/torvet/parkering.png (orto: på ortofotoet, bare lokalt)

Statuen er Frederik II (Wilhelm Rasmussen, bronse, 1917); i Tamburparken står «Sittende pike» (Arne Durban, 1957–58). data/statue.json har
plass, retning (kompassgrader), sokkelleddene, figurens form og høyde med kilder (poster med tegnes:false har bare kommunens punkt); src/20_statuen-paa-torvet.js tegner bare det dataene sier (sokkel som stabel av kvadratiske ledd, figuren i
platerustning med kommandostav og hånd i siden). `visningsskala` i dataene er 2,0 (se Landemerker under; 29.10 stod den på 1, før det 1,3 som i tegningen). Sokkel og figur er
virkelige mål; skalaen gjelder bare visningen. Kontrollark: `python3 verktoy/statue_ark.py` (fire vinkler mot referanseprofilen, ett ark per skulptur). Regel 21 og 22 passer på dette.
## Landemerker: dramatisk, ikke korrekt (Vegar 30.10)
«For at det skal funke i et slikt kart må tårnet fungere mer dramatisk – ikke korrekt. Og det samme må statuen. Dette er landemerker
man bruker for å orientere seg.» Regelen: dataene har de målte tallene (DOM, foto, ortofoto), og en egen visningsskala forstørrer
landemerket i kartet. Kontrollene og reglene leser de målte tallene. I dag: kirketårnet (bygg.kirke.visning {skala 1,6, detalj 1,3},
verktoy/fasade_former.py KIRKE_VISNING, src/06), statuen på Torvet (data/statue.json visningsskala 2,0, src/20) og rådhustårnet
(deler[].visningsskala 1,35, verktoy/landemerker.py RAADHUS_TAARN, src/07 bygTaarn). Nye landemerker får samme felt.
## Bakken i Gamlebyen mot ortofoto, kommunekart og DOM (29.10)
Overflater, gater, gjerder/murer/hekker og trær i Gamlebyen (innenfor vollene og vollene selv = landskap.fest + brosteinsflaten)
er lest av kildene med verktoy/bakke.py. Fasit per piksel (0,25 m): ortofoto 2024 der det ser bakken; kommunekartets arealtype
(gateareal, grøntareal, vann) der det ikke ser (trær, skygge, takutstikk), så nærmeste piksel fotoet ser. Hus = modellens omriss,
trær og høyde = Kartverkets DOM−DTM (rapport/hoyder/kilder).

    python3 verktoy/bakke.py overflater   data/flater.json (gress/bed/grus/asfalt/brostein fra fotoet; fl-1…4 og parkering står foran)
    python3 verktoy/bakke.py gater        bredde, midte og flatetype for veibåndene (data/landskap.json)
    python3 verktoy/bakke.py gjerder      data/gjerder.json (gjerde/mur/hekk sett i fotoet langs eiendomsgrensene og gårdsrommene)
    python3 verktoy/bakke.py traer        trærne flyttet til kronene i DOM−DTM (antallet uendret)
    python3 verktoy/bakke.py ark [N …]    kontrollark rapport/bakke/kvartal-NN.png (ortofoto | med kartets linjer | modellens bakke ovenfra)

Innenfor brosteinsflaten er brostein grunnen og flatene er avvikene; på vollene er gresset (terrenget) grunnen. Brostein og grus
skilles på farge og tekstur, men lys belegning i sol kan ikke alltid skilles i fotoet: en flate med annen type enn grunnen må være
minst 15 m² og ses i sol på halve arealet. Det som er dømt for hånd, står i kilder/bakke-maalt.json (prøvepunkter, faste flater).
Gjerder, murer og hekker: fotoet (mørk/grønn smal stripe langs eiendomsgrensene), Street View-avlesningen (utsagnene «stakitt
til venstre», «hekk foran» … plassert i åpningen til nabohuset eller ved gatekanten; `SV_AVLESNING=<sti>` peker på avlesningen) og
det som er målt for hånd (kilder/bakke-maalt.json «gjerder»). Tegningen (2017/2019-trykket) er prøvd som kilde for murene i
åpningene langs gata, men registreringen modell -> trykk (2–8 m) er for grov; slås på med TEGNING_GJERDER=1 når tegningene er
registrert per kvartal.
Trær: ett tre per tretopp i DOM−DTM; trær uten topp i et tett felt minst 5 m fra hverandre; dubletter og trær uten vegetasjon
(dømt med øyet i fotoet) tas ut med grunn (kilder/bakke-maalt.json «traer_fjernet», «traer_dommer», «traer_nye»).
Gater: gatene dømt i Street View-bildene (kilder/bakke-maalt.json «gater») går foran fotoets brostein/grus; gangveier som er gress
i fotoet nesten hele veien, tas ut (rapport/bakke/veier-fjernet.json). Innkjørsler og plasser: `bakke.py innkjorsler`.
Gata (`bakke.gatemaske`): kommunekartets gateareal + veibåndene; kommunekartet tegner mange gater i Gamlebyen hvite, så gatearealet
alene mangler dem. Ingen gjerde, mur eller hekk får stå i gata eller i et hus (regel 33 feiler ellers). Gatene måles også utenfor
vollene der kommunekartet dekker (`bakke.gate_omraade`). Oppmerkede parkeringsfelt: `bakke.py parkeringsfelt` (kommunens lag +
radene målt i ortofotoet, også kilder/parkering-maalt.json fra torvet-arbeidet), tegnes som hvite streker i src/17.
Regler: 31 overflater, 32 gater, 33 gjerder, 34 trær (alle måler mot kildene, krav 95 %).
Rekkefølge: grunnmur.py → bakke.py gater (fra grunndataene) → overflater → innkjorsler → parkeringsfelt → gjerder → traer → ark.

## Overganger og flyt (29.10)
Alt som beveger seg, tar tid og kurve fra src/15_bevegelse.js (BEV); stil.css får dem som CSS-variabler (--t-kort-inn, --k-inn …). Nye
animasjoner legges der, ikke som tall i koden (regel 11 sier fra). Kameraflytt går gjennom `glidKamera(mål, type)` (easeTo, alltid avbrytbart
av en ny gest). Huskortet: bunnark under 720 px bredde, sidepanel over; tilbake speiler inngangen.

    node verktoy/flyt-test.mjs ut/enkel/index.html rapport/flyt/maaling.json [klikk dobbel hjul dra avbryt hjem intro mtrykk ark klyp mdobbel redusert]
    PYTHONPATH=regler python3 regler/22_flyt.py

Testen kjører med Playwrights falske klokke (16 ms per bilde) og ?tegn=0 (kameraet og tilstanden oppdateres, byen tegnes ikke), så den måler
hopp, rykk, bråstopp og ankerpunkt, ikke bildefrekvens. Bildefrekvens og følelsen i fingrene ses i ekte Chrome og på telefon (tast d, ?d=1).

## Rene tak og husdeling etter tegningen (30.10, natt/tak)
Kontrollen (verktoy/kontroll.py) viste at husene ikke lignet tegningene: taket var regnet som rett skjelett over hele husrekka
(verktoy/tak.py), så hvert sprang i kommunekartets omriss ble en takflate og rekka fikk ett sammensatt valmtak. Vegar tegnet rene hus:
én kropp med saltak, gavler og møne, vinkelhus som to kropper. Nå:

    python3 verktoy/husdeling.py                ett modellhus per tegnet hus: delinger, sammenslåinger, skjul, nye (kilder/husdeling.json)
    python3 verktoy/husdeling.py linjer <tegn>  fasadelinjene: modellens husgrenser og tegningens veggflater i meter langs gata
    python3 verktoy/husdeling.py sprang <tegn>  sprang i mønet i Kartverkets DOM (husgrenser i taket) og nærmeste fasadegrense i tegningen
    python3 verktoy/husdeling.py forslag <tegn> fasadegrensene i tegningen lagt ned på modellveggene (rapport/tak/deling-*.png, bare lokalt)
    python3 verktoy/tak_enkel.py                rent tak per hus (tak2/gavl2/takform; h og th fra DOM der rapport/hoyder ikke har sikker måling)
    python3 verktoy/tak_enkel.py fra_kontroll   takform og mønretning lest av tegningene (avvik.json) inn i kilder/tak-tegning.json
    python3 verktoy/tak_enkel.py ark x y r navn plan: DOM−DTM ved siden av modellens takflater (rapport/tak/)

Taket (tak_enkel.py): omrisset deles i høyst tre nesten-rektangulære kropper (snitt gjennom de innoverbøyde hjørnene, korte snitt
foretrekkes); hver kropp får det nederste av noen plan (sal, valm, halvvalm, pult bare på smale bygg, flatt), ender som støter mot en
annen kropp forlenges inn i den (kilrenne), og huset får det øverste av kroppenes tak. Takform og mønretning: kilder/tak-tegning.json
(tegningen) går foran; ellers tilpasses alle former og begge mønretninger til DOM−DTM (h og th fritt), og den enkleste som passer
velges (saltak foretrekkes). tak.py brukes ikke lenger i Gamlebyen.
Husdelingen (husdeling.py): kuttlinjene står i modellmeter med grunn; biten med husets matrikkelpunkt beholder id-en, nye biter får
bnr- fra et matrikkelpunkt eller neste pb- (skrives tilbake i fila, så de er faste). Sammenslått: det første huset får hele omrisset,
de andre skjules (regel 20 har dem som unntak med grunn). fasade_tegning.py legg_inn fordeler vinduene fra tegningen etter hvor de står
langs veggen, så de følger med når hus deles eller slås sammen. Nye biter legges i tegningens liste i kilder/kvartal-kobling.json.
Kjeden (bygg_kjede.py): grunnmur → id_flytt → husdeling → tak_enkel → hoyder → … → bygg_merknader → register.py kort (kortene følger
adressepunktet når husene deles).
Kontrollen: kvartal-kobling.json kan ha «biter» ({ids, d: [dx, dy] pt, grunn}) for hus Vegar tegnet som en egen bit et annet sted på
arket; forskyvningen settes for hånd og finjusteres av blokksøket. Hvert kontrollark kjøres for seg (render kan krasje på én tegning).

## Oppsett på en ny maskin
Python 3 med opencv-python-headless, numpy, scipy, shapely, pyproj, tifffile, pymupdf (kommunekartet) og scikit-image (bakke.py); Node 22 og `npm install` (ESLint til regel 08); Playwright med Chromium til nettlesertestene.

## Regler som må være grønne før publisering
01–04 innhold mot kildene (02: Kartverket er fasit for høyde, tegningene for fasade – Vegar 28.10), 05 én tegnekvalitet, 06 bygger og laster, 07 ingen JS-feil i bruk (interaksjonstesten), 08 ESLint på den sammensatte modulen, 09 publisert versjon = VERSJON (Pages og artefaktbygget), 10 ytelsestrinn 2 tegner likt som trinn 0 (mobil, nærbilde), 19 skyggekartet dekker bildet og tegnes ikke på nytt under dra, 22 overganger uten hopp, rykk og bråstopp (flyt-test). `PYTHONPATH=regler python3 regler/kjor.py` (kjører fra hvilken som helst mappe; 07 og 08 gikk bare fra prosjektmappa før 23.10).

## Agenter: brief og mottakskontroll (23.10)
Vegar: «jeg liker ikke at du ikke merker noe agenter glipper.» Derfor:
- Briefen sier hvilken kilde som er fasit, hva som ikke skal røres (src/, data/), og hvilket bevis som skal leveres: kontrollark (bilde), tall (antall, dekning, sikkerhet), og verktøyet som lagde det (så kjøringen kan gjentas).
- Mottakskontroll før noe legges fram eller bygges videre på, gjort av hovedtråden, ikke agenten selv:
  1. Mot briefen: brukte agenten kilden den fikk? (23.10: fargeagenten leste det isometriske trykket der husene er tegnet fritt; Vegar måtte peke på 2019-JPG-en.)
  2. Mot kilden: minst tre stikkprøver hovedtråden gjør selv (åpne bildet, slå opp tallet, kjøre kallet).
  3. Mot beviset: kontrollarket ses på, tallene i rapporten stemmer med fila, `git status` viser at bare rapport/ er rørt.
  4. Avvik agenten selv flagger («usikkert», «ikke verifisert») gjentas til Vegar, de forsvinner ikke i oppsummeringen.
- Det samme for egen publisering: regel 09 henter Pages og sjekker versjonen. (23.10: publiser.sh stoppet stille, Pages stod på v27 hele kvelden.)

## GitHub
Repo: github.com/PageBlack-official/fredrikstad-fortress-town. main = kilden, gh-pages = server-bygget (publiser.sh). Pages: pageblack-official.github.io/fredrikstad-fortress-town

## Fargene: regelen fra 30.10 (Vegar)
Mange husfarger kom fra Street View-bilder fra august 2010, ELDRE enn tegningene. Vegar samlet selv husfargene med Street View i 2015;
tegningene og 2019-trykket er fasit for den tiden. Regelen (koden: verktoy/tak_farge.py, streetview_farger.py, vegg_nye.py):
- TAKFARGE: ortofoto 2024 (kilder/ortofoto-2024) er nyeste kilde og ser rett ned på taket: det avgjør kuløren for alle tak. Hver
  takflate måles for seg (omrisset flyttet dit taket står i fotoet: høye tak heller 1–3 m), flatene i blå skygge tas ut; teglrødt leses
  på rødt (a* i Lab) på flatene i lys, grått på medianen i sol, kobber som blågrønt. Falmet/mosegrodd tegl og brungrå betongstein gir
  samme tall i fotoet: der, og der trær eller slagskygge dekker taket, avgjør tegningen. Samme kulør i foto og tegning: tegningens farge.
- VEGGFARGE: nyeste kilde vinner: Street View 2016 eller senere (bilde_dato i kilder/streetview/avlesning.json) > tegningen
  (kvartaltegningen lest av kontrolløren, ellers trykkfargen dømt mot 2019-trykket, ellers 2017-tegningen som vektor) > Street View
  før 2015 > udømt trykkfarge > nabohuset. Merknadene (kilder/bygg-merknader.json) vinner over alt.
- Tilnærmet riktig er nok, feil kulør er ikke lov (tak_farge.familie / samme_kulor).
- Hvert hus har `vegg_kilde`/`vegg_aar` og `tak_kilde`/`tak_aar`; verktoy/kontroll.py gir «avvik med grunn» bare når kilden for akkurat
  den fargen er nyere enn tegningen (2016+). verktoy/tak_fra_ortofoto.py er erstattet av tak_farge.py (linjene er tatt ut).
- Kontrollark: `python3 verktoy/tak_farge.py ark` -> rapport/farge/tak.png og tak-<kvartal>.png (ortofoto | modellens tak ovenfra; bare
  lokalt, viser ortofotoet). Byttene: rapport/farge/bytter.md (før -> etter, kilde, dato), rapport/farge/tak.json og vegg.json.

## Fasadesegmenter: flere fasader på ett hus (30.10, natt/fasade2)
Når Kartverkets DOM har sammenhengende møne og Matrikkelen ett bygningsnummer, men tegningen viser flere fasader på samme vegg
(egen farge, egen vindusrytme), forblir kroppen og taket ett hus (Kartverket/DOM vinner for geometri). Veggen deles i segmenter:

    python3 verktoy/fasadesegmenter.py finn [tegning ...]    forslag fra tegningene (kontrollørens kamera) i kilder/fasadesegmenter.json
    python3 verktoy/fasadesegmenter.py kobling               segmentvegger uten fasadeavlesning inn i kilder/fasade-kobling.json
    python3 verktoy/fasade_tegning.py les_for_haand <tegning>  vinduene på dem (så legg_inn i kjeden)
    python3 verktoy/fasadesegmenter.py                       rettelsen «fasadesegmenter» (i kjeden etter vegg_nye.py)

kilder/fasadesegmenter.json: «hus» per hus og vegg {a, b, segmenter: [{fra_m, til_m, tegning_rgb, flater}]}, «dom» (forslagene
sett på kontaktarket: godkjent/ikke med grunn) og «for_haand» (satt for hånd, finn rører det ikke). Bare godkjente og håndsatte hus
legges inn: finn gir mange falske (takflater, smale biter, gavler fra nabohuset). Veggen slås opp på nytt i dagens omriss (samme
retning, nærmeste), så den tåler ny grunnmur. Grensene står i andel av den tegnede fasaden (frihånd: lengre eller kortere enn modellen).
Fargen per segment: Street View 2016+ der siktlinja treffer segmentet (eller sidens «fasader» fra venstre) > tegningen > Street View før 2015.
src/07 tegner hvert segment som en veggflate i egen farge og brannmurlinjen som en 14 cm mørk loddrett kant. kontroll.py dømmer
fargen per segment (veggfarge_segmenter i avvik.json); «slått sammen» blir «avvik med grunn» når veggen har segmenter.

Vinduer ved ny brannmur (30.10): bredden på et tegnet element står i andel av veggen avlesningen ble gjort på; når huset er delt,
regnes den om til husets vegg (fasade_tegning.legg_inn), og korte vegger (2–3 m) godtar ett vindu (klassifiser). De delte husene har
igjen alle elementene fra før delingen (889).

Registrering blokkvis (kontroll.py, 30.10): hver «bit» i kilder/kvartal-kobling.json er sin egen blokk med egen forskyvning (søk ±«sok»
pt, standard 8). «kamera_fast» {w: [målestokk, dreiing, tx, ty], grunn} setter det felles kameraet for hånd når fri tilpasning har to
minima (kvartal6); resten tas av bitene, ikke av én global skala.

## Landemerkene (30.10, natt/landemerker)
`python3 verktoy/landemerker.py` (sist i kjeden, etter fasade_former.py; begge stod ikke i bygg_kjede.py før, så linjene deres ble
overstyrt når kjeden gikk på nytt). Form fra 2015-tegningene, plass og høyde fra DOM−DTM, farge fra Street View/ortofoto. To nye
gjenbrukbare elementer i src/07, styrt av data (et nytt tårn eller en ny arkade = en ny post i verktøyet, ingen ny kode):
- `deler: [{form: 'taarn', c, r, sider, skaft, krage, h, ut, tinde_h, tinder, vegg, veggs, topp, vinduer {z, b, h}, stang, flagg}]`
  (bygTaarn): mangekantet skaft, utkraget brystning med tinder, flatt tak, flaggstang, ett rundbuevindu per side. Rådhustårnet.
- `arkader: [{a, b, z0, h, topp, n, bredde, dybde, mork}]` (bygArkade): rundbuer med dybde langs veggen a→b, ramme i veggfargen og
  mørk bakvegg. Rådhusets gatefasade og gårdsarkaden på 13394024 (Kvartal10).
Høyder som tilpasningen per hus måler feil (tårn i omrisset, DTM på vollkrona ved Voldporten) står for hånd med grunn i
kilder/hoyde-unntak.json; rapport/hoyder/legg_inn.py legger dem inn og regel 02 måler mot dem. Voldportens portmur står i data/porter.json
(med kilde). verktoy/kontroll_iso.mjs slår av frustumtesten under kontrollrenderen (portbygg og bygg med deler ble kastet før).
Rapport: rapport/landemerker/landemerker.md.

## Atrium, vingemurer, terrengflikker og statuen mot fotoene (30.10, natt/atrium)
Tre nye gjenbrukbare elementer, alle styrt av data og lagt inn av `verktoy/landemerker.py` (sist i kjeden):
- `bygg.atrium {gaard, kant, z, topp, glass, ramme}` (bygAtrium, src/07): innglasset gårdsrom med karm og glasspyramide (kvadrat) eller
  glassvalm (rektangel), sprosser i karmfargen. Ringtaket rundt står i tak2/gavl2 og regnes av `atrium_tak()`: rett skjelett med
  gårdsrommet som hull der bare veggene i `takfot` har takfot (resten er brannmurer); med konvekst gårdsrom er det eksakt,
  t = min(min_s d_s, max_k w_k·g_k), og helningen per gårdsromskant (w_k) og h/th tilpasses Kartverkets DOM−DTM (`atrium_hoyde()`).
  Postene står i `kilder/atrier.json` (et nytt atrium = en ny post); `tak_farge.py` tar gårdsrommet ut når takfargen måles.
  Første bruk: 16308102 (Kvartal14). h/th står i kilder/hoyde-unntak.json; landemerker.py sier fra hvis DOM-tilpasningen flytter seg.
- `porter[].vingemurer [[x0,y0,x1,y1,h0,h1,tykk]]` og `porter[].bunn` (src/10): skrå murer ved porten, toppen fra h0 ved porten til h1
  ved foten, over veien i porten. Voldporten: SØ fra Street View 2010/2019 og ortofoto 2024 (foten), NV fra Street View 2010.
- `data/terrengflikker.json` (src/08): Kartverkets DTM lagt over det beregnede festningsterrenget der det er feil, med myk kant.
  Voldporten: vollen i terrenget stod 12 m for langt øst og 3 m for høy, så buen og murene stod i en eng. Hele festningsterrenget
  bør på sikt lages fra DTM på samme måte (det beregnede terrenget er OSM-voller + brosjyren).
- `arkader[].felt {z0, z1, bredde, dybde}` (bygArkade): høye innfelte felt over hver bue i etasjen over (13394024, Kvartal10).
Statuen (src/20, data/statue.json): posituren rettet etter Google Street View mai 2024 (rett forfra) og aug. 2010 (figurens venstre
side), sett i Vegars Chrome (bare som arbeidsreferanse, ikke i repoet; URL-ene står i kildene).

## Tegnede hus uten modellhus (30.10, natt/manglende)
Kontrollen finner flategrupper i 2015-tegningene uten modellhus under («tegnet_uten_modell»). `verktoy/manglende.py` legger hver gruppe
ned på bakken (tegningens kamera baklengs: bunnkanten på z = 0, hele gruppen på z = 0 og 7 m) og lager kontaktark med kildene som avgjør
om huset finnes: tegning | modell | ortofoto 2024 og 2019 | kommunekartet | DOM−DTM i dag (Kartverket) og 2015 (kommunens laserskanning
fra tegningsåret, skiller «revet etter 2015» fra «tegnet fritt»).

    python3 verktoy/manglende.py liste       gruppene fra rapport/kontroll/avvik.json med plass på bakken (rapport/manglende/grupper.json)
    python3 verktoy/manglende.py signaler    kommunehus uten modellhus, skjulte hus, matrikkelpunkter og høyde > 2,5 m utenfor modellhusene
    python3 verktoy/manglende.py ark [T …]   kontaktark rapport/manglende/<tegning>-<nr>.jpg (bare lokalt)
    python3 verktoy/manglende.py se x y [r]  de samme kildepanelene for et punkt

Dommen per gruppe står i kilder/bygg-merknader.json «tegnet_uten_modell» (tegning, senter_pt, utfall, kategori, grunn) og leses av
kontroll.py avvik: med dom blir gruppen «avvik med grunn» (eller «lagt inn»), uten dom «feil». Et hus som finnes og mangler, legges inn
med kilder/husdeling.json («nye»/«deling») eller rettelseslaget; et hus Vegar tegnet som egen bit, kobles med «biter» i kvartal-kobling.json.
Kommunens DOM/DTM 2015 hentes av `hent_2015()` til rapport/hoyder/kilder/*2015_25832.tif (bare lokalt, lisens ikke avklart).

## Vinduene mot 2015-tegningene, runde 2 (31.10, natt/vinduer2)
Kontrollen (`kontroll.py avvik`) gikk fra 10 til 0 «feil» for vinduer; dørene har ingen «avvik» uten grunn. Det som ble bygd:
- Merknadene (kilder/bygg-merknader.json, `bygg_merknader.py`) har fått: `ved` [x, y] (velger veggen nærmest punktet når flere
  vender samme vei), `plass` [fra, til] (gjelder bare den delen av veggen, andel fra venstre sett utenfra), `rader_u` (vinduene der
  tegningen har dem, per etasje nederst først; en tom rad er en etasje uten synlige vinduer) og `bare_telling` (Vegars/Claudes
  håndtelling til kontrollen; vinduene fra fasadeavlesningen står). Kontrollen leser de samme feltene (rader uten vinduer telles ikke).
- Slått sammen hus (husdeling «sammen»): en vegg-merknad på det skjulte huset gjelder delen av vertens vegg som det gamle omrisset
  dekker, og vertens egen merknad resten (Artillerigården 868061 + 869572: 7/8 og 6/8 vinduer på hver halvdel).
- Kirka: buevinduene og dørene i skipet er data (`bygg.kirke.vinduer`, laget av `fasade_former.py` fra merknadene på kirka, ellers
  regelen src/06 hadde: 3 på lange vegger, 2 på korte, ingen ved tårnet). src/06 tegner dem; glass og dørblad har materialet
  `userData.vindu`, som `kontroll_iso.mjs` tegner som vindu (flatetype 3). Før så kontrollen null vinduer på kirka.
- Kontrollen gir «avvik med grunn» når modellen har nøyaktig det tegningen viser på veggen, men noen elementer står bak et nabohus i
  kontrollbildet (frihånd i tegningen), og når veggen er en arkade fra landemerker.py (buene er strek i tegningen, ikke hull).
  Rådhusets dør følger rådhusets grunn (sett i utsnittet: én rundbuet dør i endefeltet).
- `kontroll_iso.mjs`: id-passet leser det opprinnelige materialet (før så det kontrollmaterialet fra forrige pass), og en side som
  laster seg på nytt etter tapt WebGL-kontekst (programvare-GPU etter mange store bilder) gir én ny runde for jobben, så alle 18
  tegninger kan rendres i ett kall.
- `fasade_tegning.py les_for_haand <tegning> --bare id1,id2` leser bare husene med endret håndkobling på nytt; en full omlesing kan
  flytte gamle avlesninger til andre vegger når omrissene er endret siden (Kvartal2BITMP: 868096/pb-62).

## Tøihuset i fløyer (31.10, Vegar: «id-dele opp det bygget slik det faktisk er i dag»)
Tøihuset (bnr-193870279) er delt i tre fløyer med egne id-er: nordfløya mot Tøihusgaten (pb-68), østfløya mot Laboratoriegaten
(bnr-193870279, der matrikkelpunktet står) og sørfløya (pb-69). Kuttene står i kilder/husdeling.json og følger innerveggene fra
innerhjørnene; hjørnene går til nordfløya og sørfløya. «felles_tak» gjør at fløyene står som ett bygg:
- tak_enkel.py regner taket for hele omrisset (unionen av fløyene, originalens tegningsspek) og klipper flater og gavler per fløy;
- rapport/hoyder/legg_inn.py gir alle fløyene samme vegghøyde og takhelning (snitt veid med grunnflaten);
- husdeling.py gir fløyene navn («navn» i delingen), brosjyreteksten og feltet «floyer» (alle id-ene i bygget).
Leietakerne: kilder/virksomheter-plassert.json, lagt oppå data/virksomheter.json og data/adresser.json av
verktoy/virksomheter_plassert.py (siste steg i kjeden). «plassert» flytter en virksomhet fra Enhetsregisteret til riktig fløy,
«steder» legger til steder som ikke står der, og «hele_bygget» betyr at plassen i bygget ikke er kjent. Huskortet viser fløyas egne
steder øverst og de andre under «Også i Tøihuset»; adressen og bygningsnummeret står på alle fløyene.
Plassert med kilde: Fredrikstad Museum i nordfløya, Atelier & Galleri Tøihuset i østfløya. Uten kjent plass: Tøihussalen,
Bombardersalen, Kostymeloftet, Månefestivalen. Ikke lagt inn: husflidslaget, kunstforeningen, militærhistorisk museum, Østfold
Teater og Studium Actoris (bare i en udatert artikkel på lokalhistoriewiki). Vegar kan rette plassene i kilder/virksomheter-plassert.json.
