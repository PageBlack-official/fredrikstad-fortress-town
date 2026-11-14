# Runde 4 — motoren (src/), billig (Vegar 14.11 20:32: «Kjør, men gjør det billig»)

Fire feil i tegnemotoren, funnet på Voldportgaten (FUNN-RUNDE3C.md «render-pipeline-hull»):
1. Lyse vegger tegnes blåaktige (ambient/himmel toner lyse flater).
2. Valmtak (tak2-flater) vaskes lyse/grå; samme takfarge ser rød ut på saltak.
3. Foringsfargen (mørkebrun) forsvinner nesten mot glasset.
4. Ingen sprosse-modus for tospeils vindu (én loddrett midtpost, ingen tverrpost).

## Slik holdes det billig og trygt
- Én runde, én agent, ingen nye Street View-hentinger, ingen ny datalesing.
- Pkt 3 og 4 er OPT-IN: ny verdi i data (spross 3 = tospeils; foring tegnes bredere/mørkere bare når `farge` er satt på elementet). Hus uten feltet tegnes som før. Ingen regresjon mulig utenfor husene som har feltet.
- Pkt 1 og 2 er globale: finn årsaken i src/05–07 (lys/materiale), rett den med minst mulig endring. Bevis med FØR/ETTER fra samme kamera på 6 faste standpunkt: Voldportgaten 75 krysset, Therese M, Torvet, Kirkegaten, Raadhusgaten, Tøihuset. Piksel-diff utenfor målflatene skal være < 1 %; større avvik = stopp og skriv hvorfor, ikke prøv videre.
- Regler som må være grønne før commit: 13, 17, 22, 42, 45, 48 + maskin-sjekk. Kjør dem én gang, ikke i løkke.
- Tidstak: 90 min. Passerer du det uten grønne regler: commit det som er grønt, skriv resten i FUNN-RUNDE4.md, stopp.

## Etterpå
- Sett spross 3 på 75s 2. etg-vinduer der Street View viser tospeils (vegg5), foring #4a342c står allerede.
- Montasjer på nytt for 75 v4, 75 v5, 73, 944 (SV | render).
- Lærdom i LESMEG under «Motoren: lyse flater og valmtak (14.11)».
- Gren gate/voldport-1411. IKKE publiser.
