# Veggfarge fra rettede fasader (07.11)

Instruksen agentene leste fargene etter 07.11. Lå bare i skyen til 08.11; lagt i repoet så den kan brukes igjen. `verktoy/rett/farge_kandidater.py` bruker de samme ordene og reglene.

Hvert bilde er én husfasade rettet ut rett forfra (meterrutenett oppå). Si hvilken farge VEGGEN er malt i (ikke vinduer, sokkel,
dører eller tak). Bruk ETT ord eller uttrykk fra denne lista, det som passer best:
umalt tegl, naturstein, hvitkalket, laksoransje, oransje, terrakotta, gråfiolett, laks, rosa, vinrød, brun, mørk brun, rødbrun,
oksiderød, rød, fersken, aprikos, okerbrun, okergul, sennep, gråbeige, beige, lys grå, varm grå, blågrå, kremgul, sandgul, gul,
grågrønn, grønn, blå, antrasitt, mørk grå, grå, krem, hvit.
Tenk på at sol, skygge og motlys endrer fargen i bildet: si fargen veggen faktisk er malt i. Er du usikker mellom to, eller
veggen er mest i skygge/dekket: "sikker": false. Les også en RGB-median av et rent veggfelt (Python/PIL), og si om feltet er i
sol eller skygge ("lys": "sol"/"skygge"/"overskyet").
Levering: én JSON-liste til fila du får oppgitt: {"bilde": "...", "vegg_farge": "...", "vegg_rgb": [r,g,b], "lys": "...", "sikker": true}

Regler som følger med (LESMEG, verktoy/streetview_farger.py): bare bilder fra 2016 eller senere gir veggfarge. Sikre lesninger inn med `verktoy/rett/farger_inn.py`.
