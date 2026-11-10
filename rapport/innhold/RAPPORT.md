# RAPPORT — OPPGAVE5: innhold per hus + Hotell Kasernen-versjon

Status: **Del 1 har 29 kildefestede hus, klar til gjennomsyn hos CEO. Del 2 er ikke startet.** Bare Vegar kan si ferdig.
Sist oppdatert: 2026-11-10 (økt 3, Skriver). Økt 1 og 2 var CEO.
Gren `gate/innhold` i worktreet `~/sot-maskin/gate-innhold`, ut fra `76de60e`. `~/sot-maskin/gate` (OPPGAVE4, PAG-1492) er ikke rørt. /prove, forsiden, kirken, Kaserna, fargeoppgaven og introen er ikke rørt.

## Hvor jeg står

Vegar flyttet saken fra CEO til Skriver 10.11 kl. 08:28: innhold per hus er tekst, og det skal gjennom stemmefila og `ki-sensur.py`. Denne økta er den første med tekst i mengde.

**29 av 185 hus har innhold.** Felt med verdi: historie 29, byggeår 27, navn 9, bruk i dag 4. Alt annet står tomt, og det er med vilje: finnes det ikke kilde, står feltet tomt.

- `kilder/bygg-innhold.json` — datakilden. Hvert faktum er `{verdi, kilder[]}` med adresse og lesedato per kilde. 185 hus ligger inne, 156 er tomme.
- `rapport/innhold/sensur-tekst.md` — all tekst i én fil, slik sensuren leste den.
- `rapport/innhold/sensur-stempel.json` — `ki-sensur.py` på teksten: **0 treff, STOPP ingen**. To treff ble rettet først (kolon-avsløring i Kiørboegården, tre-på-rad i Det nye rådhus).
- `rapport/innhold/stikkprover.json` — ti tilfeldige hus, kilden hentet på nytt og byggeårets tall sjekket mot artikkelteksten: **10 av 10 stemmer**.
- `rapport/innhold/navnekonflikter.md` — åtte steder der kartets navn ikke stemmer med kildene. Ikke rettet, og innholdet er holdt tilbake der.
- `rapport/innhold/scope.json` — husutvalget innenfor 200 m (fra økt 1).

## Slik er identiteten bekreftet

Et faktum er verdiløst på feil hus. Hvert hus er derfor koblet på to uavhengige ting:

1. **Adressen.** `adresseid` i `kilder/register/adresser-omraade.json` koblet mot `matrikkel.adresser` i `data/bygg.json`. 101 av de 185 husene har adressetekst; resten er uthus og garasjer uten adresse.
2. **Artikkelkoordinaten.** `{{artikkelkoord}}` i lokalhistoriewiki målt mot bygningspunktet i Matrikkelen (`kilder/innhold-rastoff/koordkobling.json`).

Begge står i `kilder/innhold-rastoff/artikkel-kobling.json`. Der de to peker på samme bygg, er huset fylt. Der de spriker, eller der kartets navn sier noe annet, står huset tomt og konflikten er skrevet ned.

## Kilder brukt

- **Matrikkelen/Kartverket** — bygningsnummer, adresse, SEFRAK- og kulturminnemerke, bygningspunkt (`kilder/matrikkel-bygningspunkt.json`, hentet 26.10.2026).
- **Lokalhistoriewiki** — 61 artikler hentet rått 10.11.2026 og lagret i `kilder/innhold-rastoff/wiki/` med kildelenke og lesedato i hver fil. Dette er kilden til byggeår og historie. Artiklene oppgir selv Verneplan for Fredrikstad festning (2006), Bevaringsplan for festningsbyen Fredrikstad (1969) og Fredrikstad bys historie som sine kilder.
- **Enhetsregisteret (Brønnøysund)** — 412 aktive enheter med forretningsadresse i postnummer 1632, hentet 10.11.2026 (`kilder/innhold-rastoff/brreg-1632.json`, NLOD). Brukt til bruk i dag, og bare der treffet er entydig og institusjonelt.

Riksantikvarens kulturminnesøk svarte ikke på API-kall denne økta. Kulturminneplanen fra Fredrikstad kommune (`kilder/kulturminner.json`) dekker Sentrum, ikke Gamlebyen, og ga ingenting her.

## Bruk i dag — fire hus, og hvorfor ikke flere

«I dag» krever en fersk kilde. Lokalhistoriewiki skriver «idag (2008)» i artikkel etter artikkel, og det er for gammelt. Feltet er derfor fylt bare der Enhetsregisteret bekrefter noe entydig i dag:

| Hus | Bruk i dag | Grunnlag |
|---|---|---|
| Tøihuset | Fredrikstad Museum | Enhetsregisteret (STI på Tøihusgaten 41) + artikkelen |
| Dunkejongården | Foreningen Gamle Fredrikstad | Enhetsregisteret (FLI på Torvgaten 60) + artikkelen |
| Ekserserhuset | Gamlebyen Kulturhus | Enhetsregisteret (FLI på Kirkegaten 24) |
| Skolebygningen | Plus-skolen | Enhetsregisteret (Organisasjonen Plus på Færgeportgaten 77). Artikkelen sier Akademi for scenekunst, uten årstall. Den ferske kilden vinner. |

De andre står tomme. En adresse i Enhetsregisteret er ikke bevis på at virksomheten bruker bygget; Kirkegaten 28A har 20 enheter registrert. Der artikkelen og registeret spriker, eller der registeret bare viser enkeltpersonforetak, er feltet tomt og grunnen skrevet i `merknad` på huset.

## Husene som er fylt

| Hus | Bygg-ID | Adresse | Byggeår |
|---|---|---|---|
| Infanterikasernen | bnr-193867537 | Kasernegaten 47 | 1783–1787 |
| Kiørboegården | bnr-193867502 | Toldbodgaten 35 | 1767 |
| Kommandantgården | bnr-193867499 | Toldbodgaten 34 | 1768 |
| Ekserserhuset | bnr-193867510 | Kirkegaten 24 | 1808 |
| Dunkejongården | bnr-193867588 | Torvgaten 60 | 1784 |
| Det gamle rådhus | bnr-193868355 | Kirkegaten 27 | 1784 |
| Binggården | bnr-193868363 | Kirkegaten 31 | 1830-årene |
| Muldvadgården | bnr-193868223 | Kirkegaten 30 | 1830-årene |
| Kommisjonsgården | bnr-193868428 | Færgeportgaten 76 | 1834 |
| Salamandergården | bnr-193868150 | Færgeportgaten 79 | (tomt, se merknad) |
| Tøihuset | bnr-193870279 | Tøihusgaten 41 | 1773–1775 |
| Vollmesterboligen | bnr-193867634 | Voldgaten 97 | 1869 |
| Ingeniørgården | bnr-193867677 | Voldgaten 97 | 1868 |
| Voldporten med vaktstuen | bnr-193869548 | Voldgaten 98 | 1695 |
| Det nye rådhus | bnr-193972012 | Tøihusgaten 42 | 1861–1864 |
| Skolebygningen | bnr-193868436 | Færgeportgaten 77 | 1784 |
| Bramergården | bnr-193868029 | Færgeportgaten 85 | ca. 1831–1832 |
| Bøckmanngården | bnr-6242812 | Færgeportgaten 82 | 1986 |
| Enigheden | bnr-193868010 | Færgeportgaten 84 | 1838 |
| Gaaserudgården | bnr-193867618 | Torvgaten 57 og 57A | ca. 1830 |
| Rokkes hotell | bnr-193867979 | Voldportgaten 74 | ca. 1830 |
| Thiisgården | bnr-193868371 | Voldportgaten 70A | 1830-årene |
| Væktergården | bnr-193867952 | Voldgaten 10 og 11 | 1970-årene |
| Salen | bnr-193867707 | Kasernegaten 56 | trolig 1899 |
| (uten navn) | bnr-16308102 | Kasernegaten 53 og 54 | slutten av 1990-tallet |
| (uten navn) | bnr-193868398 | Toldbodgaten 38 | 1830-årene |
| (uten navn) | bnr-6247822 | Voldgaten 12 | (tomt, se merknad) |
| Færgeporten | pb-9 | — | 1727 |
| Mellomporten | pb-11 | — | 1727 |

Navn er fylt bare der kartet mangler navn. Der kartet har navnet, er feltet tomt, så kortet ikke viser to varianter av samme navn. Kirken er ikke rørt, etter stopp-listen.

## Hus som står tomme med vilje

- **156 hus** uten innhold. De 55 uthusene og garasjene har ingen kilde og skal se tomme og ferdige ut.
- **Åtte hus** er holdt tilbake på grunn av navnekonflikt eller uklar identitet. Alle står i `navnekonflikter.md`: Bullgården, Prestegården og Toldbodgaten 37; Rosinggården; Vennehaabet; Balaklava; Kongeporten (pb-10); Fredrikstad hospital; Kjørbogårdens sidebygning.
- **Brannstasjon – uthus til Infanterikasernen** (bnr-193868568): ingen artikkel, ingen kilde.
- **Gamlebyen modelljernbanesenter** (bnr-193867898): ingen artikkel, og ingen entydig adresse å slå opp i Enhetsregisteret.

## Det som gjenstår

1. **Leseveien.** Ingenting i `verktoy/`, `src/` eller `regler/` leser `kilder/bygg-innhold.json` i dag. Innholdet er derfor ikke synlig i kartet ennå. Oppgaven sier at kartet skal lese dette gjennom kjeden, ikke hardkodet. Dette er kode i byggekjeden, og det ligger hos Studio eller CEO, ikke hos Skriver.
2. **Ny regel 49:** hvert faktum med verdi i `kilder/bygg-innhold.json` må ha kilde og dato; rød stopper publisering. Skrevet som krav her, ikke som kode, av samme grunn.
3. **Navnekonfliktene** må avgjøres av Vegar eller Studio før de åtte husene kan fylles.
4. **Del 2, Hotell Kasernen-versjonen.** Ikke startet. Den er kode og layout i `src/30_gjest`, `data/partnere.json` og et gå-nettverk for gangtid langs gatene. Ett funn fra denne økta hører hjemme der: Enhetsregisteret har **Kasernen Hotelldrift AS** registrert på Kasernegaten 47. Hotellet åpner i 2027, så kartet skal ikke framstille det som åpent, og `data/partnere.json` skriver i dag «Hotel Kasernen» der oppgaven ber om «Hotell Kasernen». Ingen logo, ingen profil.
5. **Kontaktark** til Dropbox (`status/sot-kasernen-innhold.jpg`) venter på at leseveien finnes, siden arket skal vise kort for ti hus.

## Kostnad

Økt 3 tok under to timer fra start til sensurstempel. 29 hus er kildefestet; de resterende navngitte er enten konfliktbefengte eller uten artikkel. Skal flere av de 156 fylles, må kilden være en annen enn lokalhistoriewiki, for den er nå gjennomgått for Gamlebyen. Neste kilde i rekken er Riksantikvarens kulturminnesøk, som ikke svarte i dag, og SEFRAK-registreringene. Det er en egen økt, og den bør vente til leseveien finnes og Vegar har sett de 29 første på et kort.

## Økt 1 og 2 (CEO, 10.11)

Økt 1 la grunnarbeidet: isolert worktree, husutvalget innenfor 200 m fra Infanterikasernen (185 bygg, euklidsk avstand som superset av gangavstand), og skjemaet i `kilder/bygg-innhold.json` med alle 185 hus og alle verdier `null`. Økt 2 kildefestet bevis-huset Det gamle rådhus (bnr-193868355) og lot bruk i dag stå tomt fordi eneste kilde pekte på 2008.
