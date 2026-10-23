# Endringslogg

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
