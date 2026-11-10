# RAPPORT — OPPGAVE5: innhold per hus + Hotell Kasernen-versjon

Status: **påbegynt, grunnarbeid lagt. Ikke ferdig.** Bare Vegar kan si ferdig.
Sist oppdatert: 2026-11-10 (økt 1, CEO).

## Hvor jeg står

Vegar overstyrte køporten 10.11 kl. 06:37: start OPPGAVE5 nå, PAG-1492 røres ikke (venter på hans øye), baseline for /prove1 er `76de60e`.

Økt 1 er **grunnarbeid, ingen kildefestet tekst ennå**:

1. **Isolert arbeidstre.** OPPGAVE5 kjører i eget git-worktree `~/sot-maskin/gate-innhold` på gren `gate/innhold`, ut fra `76de60e`. Hovedtreet `~/sot-maskin/gate` (gren `gate/kamera`, HEAD `15dcfa1`) har OPPGAVE4s ucommittede endringer og er **ikke rørt** — samme mønster som `gate-farger` bruker. Rører ikke /prove, forsiden, kirken, Kaserna, fargeoppgaven eller introen.

2. **Husutvalget innenfor 200 m (`rapport/innhold/scope.json`).** Avstand er euklidsk fra Infanterikasernens sentroide (bnr-193867537) — en bevisst **superset** av gangavstand (gangavstand ≥ luftlinje, så ingen hus faller ut feil). Gangavstand langs gatene regnes i Del 2.
   - **185 bygg** innenfor 200 m. Fordelt (grov kategori fra Matrikkel-bygningstype, kun planleggingshjelp):
     - bolig 55 · uthus/garasje 55 · næring 38 · offentlig/kultur 10 · hotell/servering/off 9 · ukjent 10 · annet 8
     - SEFRAK-merket: **164** · i Riksantikvarens kulturminnesøk (Askeladden): **13**
   - **30 navngitte bygg** (de rikeste innholdskandidatene): Infanterikasernen (= hotellbygget/Kaserna), Arnesgården, Dunkejongården, Det gamle rådhus, Det nye rådhus, Kommandantgården, Kiørboegården, Tøihuset, Ekserserhuset, Vollmesterboligen, Prestegården, Kommisjonsgården, Salamandergården, Vennehaabet, Bullgården, Binggården, Muldvadgården, Balaklava, Ingeniørgården, Sindinggården, Rosinggården, Gamlebyen modelljernbanesenter, Skolebygningen, m.fl. (full liste i scope.json).
   - **55 uthus/garasje** får normalt ingenting, eventuelt bare «bruk i dag» — de skal se tomme og ferdige ut, ikke fylles med gjetning.

3. **Datakilden `kilder/bygg-innhold.json` (skjema, tom).** Alle 185 hus-noder lagt inn, keyet på bygg-ID (= bygningsnummer i Matrikkelen). Hvert hus har feltene `navn`, `byggeaar`, `historie`, `bruk_i_dag`, hver som `{verdi, kilder:[]}`. **Alle verdier er `null` — ingen tekst er gjettet.** `_skjema` holder kilderekkefølgen og regelen. Kartet skal lese dette gjennom kjeden (ikke hardkodet) — leserveien bygges i fabrikk-økta.

## Avklaringer og obs

- «Kaserna» i stopp-listen gjelder byggets **geometri/fasademodell** (EGNE_FASADER). Innholdstekst om Infanterikasernen (navn/byggeår/historie/bruk) er innhold, ikke modell, og er lov — men selve bygget tegnes aldri om her.
- Del 2: `data/partnere.json` har i dag `navn: "Hotel Kasernen"`. Oppgaven ber om teksten **«Hotell Kasernen»** (dobbel l). Rettes i partnerdata i Del 2 (badge-teksten leser `P.navn`). Ingen logo/profil brukes; hotellet åpner 2027 og skal ikke se åpent ut.
- Kategori-heuristikken er grov (f.eks. type 519 «Brannstasjon – uthus» havnet i «hotell/servering/off»). Den styrer bare hvor jeg legger innsatsen, aldri innholdet. Den endelige dommen per hus er på det faktiske bygget.
- Adresser som peker på flere bygg / bygg med flere matrikkelenheter er merket `flere_bygg_paa_mk` i scope.json og skal nevnes eksplisitt når de fylles.

## Plan videre (iterativt — hver økt ender med gyldig avslutning)

**Del 1 — innhold:**
- Økt 2: **bevis-hus før fabrikk.** Ett hus kildefestet helt igjennom (foreslått: `bnr-193868355` Det gamle rådhus — godt dokumentert, i Askeladden, klart et «hus», ikke Kaserna/kirka). Hent navn/byggeår/historie/bruk fra kilderekkefølgen, hvert faktum med adresse + lesedato, tekst med egne ord gjennom `vegars-stemme` + `ki-sensur.py`. Bygg leservei så kortet viser det gjennom kjeden. Verifiser på ekte skjermkort.
- Deretter: batch over de navngitte + bolig, kilde for kilde. Uthus/garasje sist, kun «bruk» der det finnes.

**Del 2 — Hotell Kasernen-versjon** (`src/30_gjest.js`, `data/partnere.json`):
- Åpne med hotellet sentrert og tydelig merket (i dag velges bare kortet etter intro).
- Spisesteder, parkering, turer med **gangtid langs gatene** fra hotellet. Hard delkomponent: trenger et gå-nettverk langs gatene (vurder `data/turer.json`/`steder.json`/gatelinjer). Utredes i egen økt.
- Alt styrt av partnerdata (så et annet hotell får sin versjon uten kodeendring). Rett `navn` til «Hotell Kasernen». Vanlig kart uten `?gjest=` skal være uendret.
- Mobil/nettbrett/pc, sjekk på ekte skjermkort (PW_GPU=1), smal og bred.

**Sluttkontroll:**
- Ny regel i `regler/` (49): hvert faktum i `kilder/bygg-innhold.json` med verdi må ha kilde + dato; rød stopper publisering.
- Ti tilfeldige hus: åpne kilden på nytt, sjekk at det stemmer; skriv resultatet her.
- Commit → regler (regel 03 kjent rød) → `sh publiser.sh prove1`. Aldri force-push. Forsiden og /prove røres ikke.

## Kostnad (ærlig, til Vegar)

Dette er en stor, iterativ jobb. Grovestimat for Del 1 full batch: ~30 navngitte + ~55 bolig = ~85 hus som skal kildefestes, hvert over inntil 7 kilder, hvert faktum med primærkilde + lesedato, hver tekst gjennom stemme + sensur. Realistisk mange økter. Vegar har bevisst avgrenset til 200 m som en prøve («vi ser om innholdet holder før vi tar hele byen») — bevis-huset i økt 2 er den første ekte kostnads- og kvalitetsprøven. Jeg melder tall per økt og stopper for Vegars dom før en eventuell utvidelse til hele byen.
