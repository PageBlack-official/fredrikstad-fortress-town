# FUNN runde 3c (Studio, 14.11.2026 kveld) — PAG-1594

Fables dom `RUNDE3C.md` + CEOs tilslutning (komm. 9d884e88) utført. Kilde: rektifisert Street View
(mai 2024 der frontal finnes; aug 2010 for geometri der 2024 mangler — repo-regel: vindu/dør fra 2010
gyldig, farge bare 2016+). Montasje SV | render per vegg. IKKE publisert.

## Datarettinger gjort (verifisert i bygd modell)

### 75 (bnr-193867928) — farger målt
- **Veggfarge:** `[202,197,198]` (lys) → **`[150,152,158]` middels kjølig grå** (målt 4f per FARGER.md).
- **Takfarge:** `[132,74,60]` → **`[116,74,60]`** (brunere/mindre rød). Render viser rødbrunt tak nå.
- **Vannbord:** mørkebrunt bånd (fra 14.11) står.
- **2.etg foring:** `farge:#4a342c` (mørkebrun) satt på de 8 vegg5-vinduene i data.

### 944 Therese M — farger
- **Veggfarge:** → **varm hvit kalkpuss `[230,226,218]`** (944 er den hvite Therese M-bygningen).
- **Takfarge:** grå `[176,176,172]`/None → **rødbrun tegl `[150,84,60]`**.

### 75 vegg4 (33,5 m) — ender lest fra 2010 (CEO overstyrte valg-a)
- **Kjerne s10–24:** mai-2024 `4f` (butikker + dører). Uendret fra 3b.
- **Majoren-ende s0–10:** lest fra **aug-2010-frontal `4e0`** (52° oblikt, grov): **brun dobbeltport** s3,3–5,3
  + butikk + dør + 2 2.etg-vindu. Erstatter placeholder-rytmen.
- **Voldgaten-ende s24–33,5:** **INGEN frontal** (2010 heller ikke) — et rødt nabobygg okkluderer 928 fra
  Voldgaten-sida (`4c`/`4b` ser ikke veggen). **Flagget, ikke diktet** (CEO-disiplin). Står på dagens data.

### 73 Majoren — uendret fra 3b, nå rammet som regelkonform (ikke «avvik»)
Geometri fra aug-2010-frontal (repo-regel), farge hvit fra 2024. IDENTITET.md: 622 = Majoren, sikkerhet høy.

### 75 vegg5 1.etg — talt på nytt
Sammenhengende glassfasade: 7 store butikkvinduer + 2 dører (s≈5,7 og 11,8). Dørene står på de smale mørke
feltene i SV; posisjonene fra 3b holder. Ingen endring nødvendig.

## RENDER-PIPELINE-hull (data er riktig, renderen reflekterer det ikke) — 3d-laget
Flere av Fables montasje-anmerkninger er **render-kode**, ikke data. Jeg har satt dataene riktig; renderen
gjør dette:
1. **Lys vegg → blå sky-skjær.** 944 (hvit `[230,226,218]`) og 75 (kjølig grå) renderes blålige fordi
   `mat()`/ambient toner lyse flater mot himmelen. Ikke en fargefeil i data.
2. **Hip-tak vaskes lyst.** 944s valmtak (`tak2`, `roof=b.tak=[150,84,60]`) renderes grått fordi de
   himmelvendte flatene fanger lyst lys; brattere saltak (75) viser samme farge rødt. Verifisert: nærbilde
   viser rødbrune nabotak, hip-flata vaskes. (Se [[verifiser-render-ikke-kode]].)
3. **Tospeils 2.etg-vindu finnes ikke som sprosse-modus.** `src/07` har bare 6-ruter (spross<1,5) og
   T-post (spross 2). «Tospeils, loddrett midtpost, ingen tverrpost» krever ny modus (spross 3 → drop
   losholt, full loddrett post) + `fasade_rett`-støtte for spross per element. **Delt shader-endring** —
   jeg kjører den ikke forhastet på slutten av en lang runde (regresjonsrisiko på alle byens vinduer).
4. **Foring-fargen renderes dempet** mot glasset.

Disse fire er ett sammenhengende lag (lys/materiale/sprosse i `src/05`–`07` + LOD), ikke SV-lesing.
Per CEOs grense (komm. 9d884e88: «finner 3c et nytt lag (3d), er det min eskalering til Vegar») løftes de
til CEO, ikke en ny selvgenerert runde.

## Montasjer (SV-tall | modell-tall)
`r3/montasje-{944-vegg7, 75-vegg5, 75-vegg4, 73-majoren}.jpg` (lokale, Google-bilder utenfor git).
Regel 02/04/17 grønne. Sendes CEO som in_review; render-pipeline-laget flagget over for Vegar-porten.
IKKE publisert.
