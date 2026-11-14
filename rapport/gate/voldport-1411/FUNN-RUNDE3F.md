# FUNN — runde 3f (Studio, 15.11 natt, PAG-1601)

## Pkt 3: GJORT (commit 03930c7)
Karmfarge `#4a342c` satt på 75s dører + port, begge gatevegger (opt-in, som foringen): vegg5 2 dører, vegg4 2 dører + 1 port. `bygg_kjede`/fasade_rett kjørt (75 hus med rettet fasade). Dørene/porten på 75 leser nå mørkebrun mot SV, ikke hvit karm.

## Pkt 1 & 2: lest fra `r3/rett-v4/bnr-193867928-4f-smark.jpg` (grønt meter-rutenett, s SYNKER mot høyre i bildet) — IKKE applisert ennå
Eksakt ±0,3 m-plassering mot de grønne linjene gjenstår; min lesing (element → s-senter, fra bildet):
1. etg kjerne, fra venstre (høy s → lav s):
- **dør (brun, ytterst)** s≈24,5 (delvis utenfor venstre bildekant)
- butikkvindu (Gamlebyen Elektriske) s≈22,5 (s0≈21,5 s1≈23,5)
- **dør m/ steintrapp** s≈20,0 (19,5–20,5)
- butikkvindu (Gamlebyen Elektriske AS, kartnål) s≈17,5 (16,2–19,0)
- **nedløpsrør** s≈16,3 (luke i 2.-etg-rytmen her)
- butikkvindu (Emm K) s≈15,0 (14,0–16,0)
- **dør m/ steintrapp** s≈12,7 (12,0–13,5)
- butikkvindu (Emm K) s≈10,5 (9,5–11,5)
- **port (brun)** lav s (hjørnebygget, utenfor høyre bildekant)
Rekkefølge = dør, butikk, dør, butikk, [nedløp], butikk, dør, butikk, port (stemmer med Fables lesing). Renderen i dag (rett-v4-kjerne.json, økende s): dor(8), butikk(10,2), dor(12,5), butikk(13,3), butikk(16,5), dor(19,5), butikk(21), dor(23,4) — feil rekkefølge/antall.
2. etg: SV viser **7** vinduer i synsfeltet med STØRRE luke mellom 4. og 5. (ved nedløpsrøret s≈16); renderen har 6. Legg inn det 7. vinduet og juster luka.

## Neste steg (presist, innen 60-min-boksen)
Mål hvert element mot de grønne linjene i 4f-smark (±0,3 m), skriv s0/s1 i `rett-v4-kjerne.json` i rekkefølgen over, legg til det 7. 2.-etg-vinduet, `bygg_kjede`, regenerer montasje fra SAMME standpunkt (r3e/), `speil_sjekk.py` grønn. IKKE publiser.
