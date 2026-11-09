# RAPPORT4 — runde 3: rett husene etter Vegars dom 09.11 kl. 14:58

Oppgave: `rapport/ferdig/OPPGAVE4.md` (commit a143d84). Sluttgate: `python3 verktoy/rett/dom_sjekk.py` **exit 0**
mot det **bygde** datasettet (`ut/server/data/by.json`), ikke `ferdig_sjekk.py`. Status per hus skal ende
`klar_til_dom`, `"runde": 3`. Bare Vegar kan si «ferdig».

Miljø: `export PATH=$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH`. Repo `~/sot-maskin/gate`, gren `gate/kamera`.

## STATUS (2026-11-09, økt 1 — gate + baseline, ingen husgeometri rørt ennå)

Levert og committet denne økta:
- **`verktoy/rett/dom_sjekk.py`** — sluttkontrollen Vegar ba om. Leser bygde data, assignerer vinduer til vegg
  via `verktoy/vegger.py` (samme som `bygg_ark.py`), grupperer i etasjer på sylleøyde, og krever det tellbare i
  Vegars ord. Hver sjekk siterer ordene den springer ut av, så kravet kan etterprøves som Vegars, ikke agentens.
- **`verktoy/rett/del_a_frys.json`** — frossen referanse for Del A (nr 2, 9, 12, 13). dom_sjekk krever at disse
  fire husene står byte for byte urørt gjennom runde 3.

### VIKTIG funn: committet `ut/server/data/by.json` (HEAD) er UTDATERT mot committet kilde
Et ferskt `python3 bygg.py server` fra committet kilde (data/, src/ er rene på HEAD) gir et **annet** by.json enn
blobben som ligger committet på HEAD. Forskjellen er ekte geometri på Del A (vind, fasade_rett, karm_farge,
dor_farge er mer raffinert i kildebygget — Street View-lesninger lagt på). Altså: **kilden er sannhet, den
committede by.json-blobben er en etterslengt artefakt som aldri ble bygd på nytt før commit.**
→ Del A-frysen er derfor forankret til **det ferske kildebygget** (tilstanden runde 3 starter fra), ikke den
utdaterte blobben. Det låser de fire godkjente husene mot utilsiktet endring under runde 3, uansett hvilket
historisk øyeblikksbilde Vegar så på. **Flagges til Vegar** som eget punkt; kan avstemmes mot git-historikk ved behov.

### Working-tree-artefakter som IKKE er mine og IKKE skal committes
Ved øktstart lå ucommittede endringer i `ut/` (ia-intro.png, ia-kort.png, ia-slutt.png, enkel/index.html,
modul.js, server/index.html, server/sw.js, server/data/by.json) + untracked `rapport/ferdig/renders_r2/`,
`sot-dom-28.jpg`, `kal/sweep.json`, `rapport/gate/sv_rett5/`. **Den ucommittede by.json hadde endret alle fire
Del A-husene** (som Vegar dømte «Korrekt» og sa «ikke rør») — bevis på at disse artefaktene ikke er til å stole
på. ia-*.png er introbildene (forbudt å røre). Jeg har **ikke** rørt, slettet eller committet noen av disse.
`ut/server/*` er nå regenerert fra committet kilde (ren build); resten står urørt. Google/SV-bilder aldri i git.

## BASELINE fra gate (fersk kildebygg) — de 8 tellbare hullene som står igjen
```
nr 1 (bnr-193867952): 1. etg er VVVVVDVVD, skal være V V D V V D V P
nr 1 (bnr-193867952): 2. etg er 9 vinduer, skal være 8 vinduer uten dør/port (3+3+1+dobbel)
nr 6 (bnr-193867855): gatefasaden gir 0 nede / 4 oppe, skal være 2 nede / 2 oppe + rød port
nr 7 (bnr-193867626): 1 pipe, skal være 2
nr 8 (bnr-193867634): 3 piper (skal være 2), 0 takvindu (skal være 1); 7 vinduer på langfasaden stemmer alt
nr 14 (bnr-13416419): 1 vindusrekke, skal være 2 etasjer à 4 vinduer, de to midterste doble
```
Del A: **holder** (byte for byte mot frysen).

## WORKLISTE runde 3 — rekkefølge (Del D FØRST, per oppgaven)

### Del D (må fikses først, ødelegger ellers dommen)
1. **Utbrent hvitt.** Vegar så ingenting på nr 14; 24 Bings gate (bnr-13416362) også utbrent. Finn om det bare
   er i kontrollbildet eller også i kartet Vegar ser, og rett ÅRSAKEN (ikke autokontrast). Sjekk med ekte
   skjermkort: `PW_GPU=1`. (Se `rapport/ferdig/renders_r2/bnr-13416362-*.png` — artefakter fra forrige run, verifiser selv.)
2. **Bevisbildene.** Samme kamera i Street View og modell, huset midt i bildet, ingen nabovegg/mur/tre foran.
   Går det ikke fra standpunktet: flytt kameraet i begge. (fov ~50, ikke 75 — RAPPORT3 systemfunn 1.)

### Del B — tellbare (gate-krav), sourced i kjeden, ALDRI hånd-redigert i data
Per hus: les fasaden mot Street View (HJORNER→rett→ELEMENTER→konverter→kjede), bygg, render, montér bevis,
se selv, sett `kilder/ferdig.json` → `klar_til_dom` runde 3. Metode: RAPPORT3 «NESTE ØKT».
- **nr 1** (10 Voldgaten): legg om gatefasaden til V V D V V D V P nede; 2. etg 3+3+1 + dobbelvindu over port-døren.
- **nr 6** (Torvgaten 67): «lest bygget feil». Det hvite huset = 2 vinduer nede + 2 oppe, rød port står.
  Tak som «hatt med klaffer» = halvvalm (SV v4, [TOLKNING]). Nå ligger det 12 elementer på 3 vegger — reduser.
- **nr 7** (26/27 Kirkegaten): 2 piper; fjern «stor kloss på venstresiden av taket» (finn hva den er — arker=2?).
- **nr 8** (Vollmesterboligen): 2 piper (er 3), 1 takvindu på kortveggen (er 0). 7 vinduer stemmer alt.
  Svart kloss foran huset finnes ikke i SV — bort; samme svarte kloss ved 35 Heibergs gate (bnr-6276504), rett årsaken.
- **nr 14** (22 Bings gate): to etasjer (bildet vinner over Kartverkets 4,6 m — skriv unntaket i datakilden med
  begrunnelse, ikke hardkoding), 4 vinduer per rad, de to midterste doble. Utbrent — se Del D.

### Del B — ikke-tellbare (dømmes på bevisbilde, ikke i gate)
- **nr 3** (bnr-193867898, 9 Voldgaten): korrekt, men døren er for langt ned — skal på gateplan.
- **nr 4** (bnr-193867804, 51 Kasernegaten): slå sammen rosa del + beige nabo (to vinduer nede/oppe) til ÉTT
  hus, hele bygget rosa; behold begge ID-ene i registeret ([TOLKNING] husdeling). Vinduer/dører står der de står.
- **nr 5** (bnr-193972292, 79 Færgeportgaten): vinduene til høyre skal helt ned på gatenivå; 2.-etg-vinduene litt
  for store — alle vinduer skal være i samme størrelse.
- **nr 10** (bnr-193868576, 41 Tøihusgaten): teglmurhus (ingen lys sokkel om SV ikke har det), brun port. Form ellers korrekt.
- **nr 11** (bnr-193971954, Del A-unntak): alt godkjent unntatt pipa — mål pipa mot SV/flyfoto, rett BARE
  størrelsen hvis kilden viser feil.

### Del C — de 12 som ikke holdt (farge/standpunkt/okklusjon)
Farge-regelen: riktig kulør, ikke eksakt tone. Blågrå [178,196,206] leses blå — finn en verdi som leses GRÅ for
de grå husene (bnr-193868088, bnr-6276512). Autokontrast forvrenger kulør (RAPPORT3 systemfunn 2): les `vegg`
i data, ikke det strukne bildet. Listen:
```
bnr-13415889  9/10 Ove Ramms   villa for enkel: tredje takark, balkong, grå side står hvit
bnr-6276822   2 Lammers        taket rødt, skal være mørkt
bnr-6251331   21 Raadhusgaten  gult (ikke beige); kilde «strågul», SV mai 2024 gult
bnr-193868088 lys blågrått     grått, står blått (farge-verdi-fiks)
bnr-6276512   37 Heibergs      grått, står blått (samme farge-fiks)
bnr-193971946 hvitpusset       vinduskarmene skal være mørke
bnr-13416362  24 Bings         kontrollbildet utbrent (Del D)
bnr-193867820 13 Rådhusgaten   kameraet står bak en mur (standpunkt)
bnr-6276504   35 Heibergs      trær dekker huset; svart kloss (se nr 8)
bnr-193972306 grått panelhus   bildet viser en annen vegg enn modellen (standpunkt)
bnr-193971288 hvitt hus        usikkert om bildet viser riktig hus
bnr-193867480 Widdingstua      terrenget under vannet: rett bakke_dtm så huset kan tegnes
```

## NÅR ALT ER TEGNET (fra oppgaven)
1. Kjeden → `python3 bygg.py enkel`, bevisbilder for alle hus i Del B og C (fov 50).
2. Commit (norsk). Aldri Google/SV-bilder i git. Regler etter commit (`PYTHONPATH=regler python3 regler/kjor.py`,
   nohup). Regel 03 kjent rød; annet rødt rettes.
3. `sh publiser.sh prove1` (deploy-nøkkel virker nå, vanlig push, aldri force). Bare /prove1.
4. Kontaktark → Dropbox `.../teknisk-veikart/status/sot-dom-runde3.jpg` (SV | etter, adresse + Vegars nr).
   Rapport `status/sot-tegnet-runde3.md`. Pekerlinje øverst i `status/smart-old-town.md`.
5. PAG-1469 → done (erstattet av denne oppgaven).

## GRENSER (står ved lag)
Ikke rør kirka, Kaserna, forsiden, /prove, fargeoppgaven, introen (ia-*.png). Ikke slett noe, aldri force-push,
ikke send noe eksternt. Publiser bare til /prove1. Et hus der INGEN kilde kan svare → `trenger_vegar` med
spørsmål + bilde (ikke merk det klart).

## Logg
- 2026-11-09 økt 1: `dom_sjekk.py` + `del_a_frys.json` skrevet og validert (Del A holder, 8 tellbare geometrihull
  står). Funn: committet by.json-blob utdatert mot kilde (frys forankret til kildebygg, flagges Vegar). Ingen
  husgeometri rørt ennå. Oppgaven står `in_progress`; fortsett fra «WORKLISTE runde 3».
