# Runde 2 (Fable leste GPU-bildene 14.11 14:20) — én rettrunde, så ferdig

Bra: 75 er ett hus med ett tak, høydene 75 > 73 > 71 stemmer, 71 har én etasje med rundbuer, 73 har 5 vinduer oppe og port. Behold alt det.
Feil, i rekkefølge (alle i data/merknader, ikke i scenen):

1. **75 har ingen butikkvinduer.** 1. etasje er tegnet med samme små boligvinduer som 2. etasje, både mot Voldportgaten og mot Voldgaten. Fasit (Vegars bilder): 1. etasje er nesten bare store butikkvinduer (brede, høye, nesten fra sokkel til vannbordet) med dører imellom. Bruk `stor`/butikkvindu-typen du la inn for 71. Mot Voldgaten: store butikkvinduer + 2 dører. Mot Voldportgaten: butikkvinduer + dører + den brune dobbeltporten (ikke rundbuet: porten på 75 er rett, rektangulær; rundbuen i «langs»-bildet til venstre er feil).
2. **75 vinduer i 2. etg: T-sprosser**, ikke 4-ruters kryss. Vegar: «8 vinduer i 2 etg med t-sprosser». Hvite rammer i mørkebrun foring.
3. **75 farger for mettede.** Vegg skal være lys gråbeige med et svakt fiolett skjær (Street View mai 2024), ikke lavendel; dagens [204,192,198] rendres lilla. Tak: mørk rødbrun/brun tegl (se 73-taket for nivå), ikke knallrødt.
4. **75: den lille gavlen/ark-formen midt på mønet** (synlig i voldgaten-mot-75-kortside.png) finnes ikke i virkeligheten. Fjern.
5. **75 skråinngang i 1. etg på hjørnet.** Hvis per-etasje-geometri ikke finnes: skjær hjørnet skrått i omrisset BARE i sokkel/1. etasje som et eget lite hull/inntrukket felt med dør, eller legg en mørk inntrukket flate (veggfelt) med dør på hjørnet. Skriv i FUNN hvilken vei du valgte. Ikke la hjørnet stå rett med en dør ved siden av.
6. **75 mørkebrune bånd:** vannbord mellom etasjene og over butikkvinduene, hjørnekasser. Hvis `veggfelt` [x1,y1,x2,y2,r,g,b] kan gi en smal horisontal stripe: bruk det (mørkebrun ca. [74,52,44]).
7. **73 Majoren: mønet skal ligge LANGS gata** (raft/takfot mot Voldportgaten, ikke gavl). Vegars foto viser takfoten mot gata. Sett mønretning i kilder/tak-tegning.json.
8. **71 Therese M: tegltaket for knallrødt** — mørk rødbrun tegl som på fotoet. Inngangsdøra skal stå i det skrå hjørnet (med steintrapp om mulig), ikke i fasaden ved siden av.
9. Gatekameraet `kryss-voldportgaten-voldgaten` sto inne i et hus (dør svevde i forgrunnen). Flytt standpunktet ut i krysset så 75s hjørne synes.

Ferdig = samme bilder på nytt + KONTAKTARK + FUNN-RUNDE2.md med dom per punkt 1–9, regler grønne, commit. IKKE publiser. Fable leser bildene igjen.
