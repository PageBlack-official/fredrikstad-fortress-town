# Runde 3e — diagnose av speilvendt Majoren (Studio, 14.11 kveld, PAG-1600)

## Hva som er sikkert (målt, ikke gjettet)
Montasje `r3/montasje-73-majoren-3d.jpg`: SV har dør/inngang til VENSTRE, portrom til HØYRE. Renderen har porten til VENSTRE. Speilvendt.

Datalaget (`kilder/gate/rett-majoren.json`, vegg 2): dør s≈2,5, port s≈10,2 (av lengde 12,2). Rekkefølgen i dataene stemmer med SV (dør venstre, port høyre). Så **s-rekkefølgen er riktig lest**; feilen er hvilken MODELL-ende s måles fra.

**Kjernefunn:** `rett-majoren.json` har `venstre=[137.84,65.36]`, `hoyre=[149.02,60.37]`. `vegg_for_skudd.py` (den geometriske regelen, `hoyre_retn=[-n[1],n[0]]`, n utover) gir det MOTSATTE: `venstre=[149.02,60.37]`, `hoyre=[137.84,65.36]`. Altså er venstre/høyre i rett-fila **byttet om** i forhold til verktøyets egen regel. Majoren ble lest via en manuell `frontal_skudd.json`-sti (ikke `sv_rett_skudd`→`vegg_for_skudd`), og venstre/høyre ble satt for hånd/feil der.

## Rotårsak (i koden, som bestilt)
`venstre`/`hoyre` i rett-fila MÅ være den modell-enden som står til venstre/høyre I DET REKTIFISERTE BILDET (der leseren målte s fra venstre). I dag finnes to veier som setter dem ulikt:
- standard: `vegg_for_skudd.py` — geometrisk, fra veggnormalen.
- manuell (Majoren/944): standpunkt-filer i `r3/rett-arbeid/` — satt for hånd, kan bomme.
Ingen av dem binder `venstre` til bildets venstre via KAMERAET. Riktig invariant: projiser veggens to ender til skuddets kamera (som `anslag_u.py` gjør for hint) og sett `venstre` = minst bilde-u, `hoyre` = størst.

## Fix (anbefalt, verifiseres med korrekt montasje)
1. **Kode:** la `vegg_for_skudd.py` (og den manuelle stien) sette `venstre`/`hoyre` ved kameraprojeksjon (minst u = venstre), ikke ved normalen. Lagre skuddets `heading/lat/lon` (eller cx,cy+heading) I rett-oppføringen.
2. **Test/regel (RUNDE3E):** `sjekk_speilvendt` — for hver rett-oppføring med kamera: `venstre` skal projisere til lavere bilde-u enn `hoyre`; ellers rød. Fanger Majoren i dag.
3. **Eksisterende rett-filer:** normaliser i kode (ikke for hånd): der `venstre` projiserer til høyre, bytt `venstre↔hoyre` og speil s → `lengde − s`. Gjelder sjekk av alle fire vegger (75 v4/v5, 944 v7, 622 v2).
4. **MERK (RUNDE3E pkt 4):** montasjene må tas fra SAMME standpunkt+retning som SV-panoet (ikke hjørne). `montasje-73-majoren-3d.jpg` og `-75-vegg4-3d.jpg` må regenereres fra SV-standpunktet før en fix verifiseres — ellers kan et «speilvendt» inntrykk være en montasje-vinkel-artefakt, ikke en datafeil. Disambiguer FØRST med korrekt montasje.

Ikke publisert. Ingen datafiler endret denne økta (venstre/høyre-flip gjøres i koden sammen med montasje-verifisering, ikke gjettet for hånd).
