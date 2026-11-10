# Navnekonflikter mellom kartdatasettet og kildene (OPPGAVE5, 10.11.2026)

Identiteten til hvert hus er bekreftet på to ting: adressen i datasettet (`kilder/register/adresser-omraade.json`, `adresseid` koblet mot `matrikkel.adresser` i `data/bygg.json`) og artikkelkoordinaten i lokalhistoriewiki (`{{artikkelkoord}}`) målt mot bygningspunktet i Matrikkelen. Tabellen i `kilder/innhold-rastoff/artikkel-kobling.json` viser begge for hver artikkel.

Åtte steder stemmer ikke kartets navn med kildene. Ingen av dem er rettet her. Innhold er holdt tilbake på husene det gjelder, fordi et kort som viser ett navn og en annen gårds historie er verre enn et tomt kort. Navn i `data/bygg.json` er Studios og Vegars, ikke mine.

## 1. Bullgården og Prestegården står på feil bygg

| Bygg | Navn i kartet | Adresse i datasettet | Hva kildene sier |
|---|---|---|---|
| bnr-193918239 | Bullgården | Voldportgaten 69 | Lokalhistoriewiki: **Prestegården**, Voldportgaten 69. Artikkelkoordinat 5,8 m fra bygningspunktet. |
| bnr-193868320 | (uten navn) | Toldbodgaten 37 | Lokalhistoriewiki: **Bullgården**, Toldbodgaten 37, bygd 1767 for kjøpmann Aanen Paus. Artikkelkoordinat 5,2 m. |
| bnr-193868142 | Prestegården | Kirkegaten 32 | Ingen artikkel treffer. Nærmeste artikkelkoordinat er Feiergården (Smedjegaten 86), 43 m unna. |

Støtte for at Toldbodgaten 37 er Bullgården: Enhetsregisteret har «Postgården Fredrikstad Sameie» på adressen, og artikkelen forteller at «Gamle Fredrikstad» postkontor holdt til i første etasje til 1988.

Konsekvens: tre hus står uten innhold til navnene er avgjort.

## 2. Rosinggården

Kartet har navnet på **bnr-193868312**, som ikke har adresse i datasettet. Lokalhistoriewiki oppgir Kirkegaten 29a, og det er **bnr-193868282**. Artikkelkoordinaten ligger 5,9 m fra bnr-193868282 og over 17 m fra bnr-193868312.

## 3. Vennehaabet

Kartet har navnet på **bnr-193867596**. Lokalhistoriewiki oppgir Kasernegaten 46, og det er **bnr-193987370** (artikkelkoordinat 7,5 m). Enhetsregisteret har St. Johanneslogen St. Magnus på Kasernegaten 46, og artikkelen sier at logen kjøpte huset i 1912 og fremdeles eier det.

## 4. Balaklava

Kartet har navnet på **bnr-193868231**, som deler adresse (Kirkegaten 30) med Muldvadgården. Artikkelen oppgir «Færgeportgaten 39b», en adresse som ikke finnes i utvalget, og artikkelkoordinaten ligger 1,4 m fra **bnr-193868452** (Toldbodgaten 39B). Her er både kartet og artikkelen uklare, og huset står tomt.

## 5. Kirkegaten 27 peker på to bygg

bnr-193868355 (Det gamle rådhus, artikkelkoordinat 6,7 m) og bnr-193868517 (16,2 m). Innholdet er lagt på det navngitte bygget. Dette er tilfellet oppgaven ber om å nevne eksplisitt.

## 6. Kongeporten (pb-10)

Kartet kaller porten Kongeporten. Lokalhistoriewiki har ingen artikkel med det navnet; den har «Kommandantporten i Fredrikstad». Porten er tegnet for hånd og har ikke bygningspunkt, så koordinatsjekk finnes ikke. Står tomt til navnet er avklart.

## 7. Fredrikstad hospital

Adressetreffet peker på bnr-193870260 (Voldgaten 4), koordinattreffet på bnr-193972063 (1,3 m, uten adresse). Motstridende, og huset står tomt.

## 8. Kjørbogårdens sidebygning (bnr-193868460)

Ingen egen artikkel. Kjørboegården-artikkelen beskriver gården som to bygninger, en toetasjes langs Kasernegaten og en enetasjes sidefløy mot Toldbodgaten, men sier ikke hvilket bygningsnummer som er hvilket. Står tomt.
