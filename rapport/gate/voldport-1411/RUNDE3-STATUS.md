# Runde 3 — status (Studio, 14.11.2026 kveld)

## Del A: GJORT
`FEILANALYSE.md` + LESMEG-regel «Voldportgaten 14.11: bygd fra tekst, ikke fra bildet» skrevet og committet (5368028). Kjernen: runde 1–2 brukte antatt-hus-verktøyet (`bygg_merknader.py`: antall per etasje → **jevn rytme**, håndhevet av **regel 17**) på et **fotografert** hus. Grønn regel 17 bekreftet den pålagte rytmen i stedet for å avsløre den. Rett vei = les hvert element i meter fra rektifisert Street View.

## Del B: BLOKKERT på Street View-bilder (attended Chrome)
Rett-pipelinen krever Street View-foto som ser hele hver gatevegg. Status målt i dag:
- `sv_rett_plan.py bnr-193867928 bnr-193868622 bnr-193868258` → **bare 2 av 11 vegger** har et panorama som ser hele veggen. 9 vegger uten dekning (bl.a. 75 vegg 4/7/8, 73 Majoren vegg 2/8/9, 71 vegg 1/6/7).
- Eksisterende rektifiserte skudd på disk dekker bare delvis: `bnr-193867928-5`, `bnr-193868258-2`. **73 Majoren har ingen.**
- `sv_lager.json` har 584 panoramaer (373 fra 2024), men de ser ikke hele disse smale gateveggene forfra (bygg foran, Googles bil kom ikke tett nok).

**Hvorfor jeg ikke kan hente mer herfra:** `verktoy/sv_hent.mjs` og `sv_lager.mjs` krever **synlig Chromium** («Google gir ikke Street View i hodeløs nettleser») og **stopper ved robotsjekk**. En uassistert heartbeat kan ikke løse robotsjekken. Dette er samme rot som Fables punkt 2 (Vegars 9 bilder nådde aldri minien).

**Å bygge fasadene fra tekst igjen for å «bli ferdig» ville gjenta nøyaktig feilen FEILANALYSE.md beskriver.** Derfor stopper jeg her framfor å levere en ny tekst-fasade.

### Unblock (eier: Vegar / en menneske-styrt Chrome-økt på minien)
1. Kjør `node verktoy/sv_lager.mjs` i synlig Chrome og løs robotsjekken, så katalogen får mai-2024-panoramaer tett på Voldportgaten 75/73/71 — ELLER legg Vegars 9 skjermbilder et sted minien når (ikke ~/Downloads).
2. Så: `sv_rett_plan` → `sv_hent.mjs` (attended) → rektifiserte vegg-bilder i `rapport/gate/sv_rett*/`.
3. Da kan Studio kjøre resten uassistert: les hvert element i meter (ELEMENTER.md) → `rett.py`/`konverter.py` → `kilder/gate/rett-voldport-1411.json` → `bygg_kjede.py` (fasade_rett sist) → montasjer SV|render i `r3/` → `ferdig_sjekk.py`.

Ingen fasadedata rørt denne økta (forkastingen av runde-1/2-merknadene gjøres sammen med rett-innlesingen, ikke før bildene finnes). IKKE publisert.
