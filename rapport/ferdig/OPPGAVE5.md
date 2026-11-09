# Oppgave 5: innhold per hus og Hotell Kasernen-versjon (Smart Old Town, /prove1)

Du kjører på Mac minien, i repoet `~/sot-maskin/gate`. Skriv alt på norsk. Hovedregel: «nesten er ikke lov». Start først når PAG-1496 og PAG-1492 er ferdige. Les de siste delene av `LESMEG.md`. Skillene `page-black-design`, `page-black-vegars-stemme` og `page-black-ki-sensur` gjelder.

Vegar 09.11 kl. 17:59: «Ok, legg 1 og 2 i køen». Det er disse:
1. Innhold per hus: navn, byggeår, historie, hva som er der nå.
2. Hotell Kasernen-versjon: kartet som hotellets forside, med spisesteder, parkering og turer sett fra hotellet.

Avgrensning: bare husene innenfor 200 m gangavstand fra Kasernegaten 47. Vi ser om innholdet holder før vi tar hele byen.

## Del 1: innhold per hus

Hus-ID er bygningsnummeret i Matrikkelen (`matrikkel` i datasettet).

- Bygg en datakilde `kilder/bygg-innhold.json`: per hus-ID felt for navn, byggeår, historie, bruk i dag. Hvert faktum har kilde med adresse og dato for når det er lest. Kartet leser dette gjennom kjeden, ikke hardkodet.
- Kilder, i denne rekkefølgen: Matrikkelen og Kartverket, Riksantikvarens kulturminnesøk (Askeladden), SEFRAK-merket i matrikkelen, Fredrikstad kommunes kulturminneplan, Brønnøysundregistrene for virksomheter, virksomhetenes egne sider, lokalhistoriewiki. Tall og datoer skal ha en primærkilde.
- Finnes det ikke kilde: feltet står tomt. Aldri gjett, aldri fyll ut med generell Gamlebyen-historie. Kortet skal se ferdig ut med bare det som finnes.
- Tekst skrives med egne ord, kort, uten avskrift fra kildene. Hver tekst går gjennom stemmen og `ki-sensur.py`. Ingen private opplysninger om beboere; privatboliger får bare det som gjelder bygningen.
- Hus som er tatt ut, eller der adressen peker på flere bygg: si fra i rapporten.

## Del 2: Hotell Kasernen-versjon

Bygg videre på `?gjest=kasernen` (`src/30_gjest`, `data/partnere.json`). Alt styres av partnerdata, så et annet hotell kan få sin egen versjon uten kodeendring.

- Kartet åpner med hotellet i midten, tydelig merket. Spisesteder, parkering og turer vises med gangtid fra hotellet, regnet langs gatene.
- Bruk navnet «Hotell Kasernen» som tekst. Ikke bruk hotellets logo eller profil: den er laget av andre og vi har ikke lov. Hotellet åpner 2027, og det skal ikke se ut som det er åpent nå.
- Vanlig kart uten `?gjest=` skal være uendret.
- Må fungere på mobil, nettbrett og pc. Se på bildene på ekte skjermkort (PW_GPU=1), smal og bred, før du sier at noe er bra.

## Sluttkontroll

- Ny regel i `regler/`: hvert faktum i `kilder/bygg-innhold.json` har kilde og dato; rød stopper publisering.
- Ti tilfeldige hus: åpne kilden på nytt og sjekk at det som står, stemmer. Skriv resultatet i rapporten.
- Regler etter commit (regel 03 er kjent rød). `sh publiser.sh prove1`. Aldri force-push. Forsiden og /prove røres ikke.

## Lever

- `rapport/innhold/RAPPORT.md`: hvor mange hus som er med, hvor mange felt som er fylt, hva som manglet kilde, stikkprøvene, lenke til `/prove1/?gjest=kasernen`.
- Kontaktark til Dropbox `.../20 Paperclip/outputs/teknisk-veikart/status/sot-kasernen-innhold.jpg`: kort for ti hus og hotellvisningen på mobil og pc. Én pekerlinje øverst i `status/smart-old-town.md`.
- Vegar dømmer. Bare han kan si ferdig. Send ingenting eksternt, ikke kontakt noen, ikke slett noe.

Avslutt hver kjøring med gyldig avslutning på saken. Gjenstår det arbeid: skriv hvor du er i `rapport/innhold/RAPPORT.md` og be om ny kjøring.
