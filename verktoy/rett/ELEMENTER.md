# Vinduer og dører fra en rettet fasade (07.11)

Hvert bilde er én husfasade rettet ut som sett rett forfra. Rutenettet er i meter: magenta loddrette linjer hver meter fra venstre
hjørne (tall nederst, `s`), blå vannrette linjer hver meter over bakken (tall til venstre, `z`). Bildet er 50 piksler per meter.
Bunnen av bildet er bakken, toppen er takfoten. Lengde og høyde står i lista.

1. **Sjekk først om rettingen er god:** fasaden skal fylle bildet fra kant til kant, med husets hjørner ved venstre og høyre kant og
   takfoten øverst. Er den skjev, kuttet, viser et annet hus eller mest himmel/bakke: `"ok": false` og en `"grunn"`, og ingen elementer.
2. **Les ALLE vinduer, dører, porter og butikkvinduer** på fasaden, etasje for etasje (også øverste etasje og kjellervinduer):
   `{"type": "vindu|dor|port|butikk|oksoye", "s0": 1.20, "s1": 2.05, "z0": 0.95, "z1": 2.30}` = ytterkanten av karmen i meter
   (s fra venstre hjørne, z over bakken), to desimaler. `port` = bred kjøre-/portåpning, `butikk` = stort utstillingsvindu i 1. etg.
   Rundbuet topp: `"bue": 1`. Farge bare når den er tydelig (hex), f.eks. `"farge": "#2f5d3a"` på en grønn dør.
3. Ser du ikke et element sikkert (tre, bil, skilt foran): ta det ikke med, skriv det i `merknad`.
4. Tell til slutt: antall vinduer per etasje og antall dører, og skriv det i `telling` («1. etg: 4 vinduer + 1 dør; 2. etg: 5 vinduer»).

Levering: ÉN JSON-liste med Write-verktøyet til fila du får oppgitt, i samme rekkefølge som lista:
`{"bilde": "...", "ok": true, "elementer": [...], "telling": "...", "merknad": "..."}`
Svar til slutt med én linje: antall fasader lest, antall ikke ok.
