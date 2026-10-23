# Endringslogg

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
