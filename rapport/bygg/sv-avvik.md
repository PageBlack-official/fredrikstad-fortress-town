# Tegningshus som avviker fra Street View: avgjørelse per hus

Laget av verktoy/sv_avvik.py (30.10) fra rapport/streetview-fasader/kjoring.json og vektoravlesningen av tegningene. Reglene står øverst i verktøyet. Tegningen er fasit for vinduer og dører; «endret siden 2015» betyr at Street View viser en annen fasade i dag, og huset står fortsatt etter tegningen til Vegar sier noe annet.

feil vegg (Street View lagt på): 35 · feil vindu: 23 · feil vegg: 21 · endret siden 2015: 19 · feil vindu (rettet): 2

| id | navn | siden kameraet så | Street View | før (modell) | vurdering | grunn |
|---|---|---|---|---|---|---|
| bnr-13414904 |  | S | [3, 4] | [4] | endret siden 2015 | tegningen [4], Street View [3, 4] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193867626 |  | S | [2, 2] | [2, 1, 1] | endret siden 2015 | tegningen [2, 1, 1], Street View [2, 2] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193867715 |  | S | [2, 2] | [] | endret siden 2015 | tegningen [], Street View [2, 2] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193867723 |  | SØ | [6, 7] | [4, 6] | endret siden 2015 | tegningen [4, 6], Street View [6, 7] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193867839 |  | S | [6, 8] | [4, 4] | endret siden 2015 | tegningen [4, 4], Street View [6, 8] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193867952 |  | SØ | [10, 9] | [7, 7] | endret siden 2015 | tegningen [8, 7], Street View [10, 9] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193868061 | Artillerigården | SV | [11, 12] | [2, 5] | endret siden 2015 | tegningen [3, 5], Street View [11, 12] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193868096 |  | SØ | [3, 3] | [1, 2] | endret siden 2015 | tegningen [1, 2], Street View [3, 3] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193868347 |  | SØ | [5, 5] | [2] | endret siden 2015 | tegningen [2], Street View [5, 5] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193868533 |  | SØ | [1] | [] | endret siden 2015 | tegningen [], Street View [1] (middels sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193868568 | Brannstasjon - uthus til Infanterikasernen | S | [0] | [] | endret siden 2015 | tegningen [], Street View [0] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193869572 |  | SV | [8, 9] | [5, 3] | endret siden 2015 | tegningen [6, 3], Street View [8, 9] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193870228 |  | SØ | [6, 6] | [5, 5, 1] | endret siden 2015 | tegningen [5, 5, 1], Street View [6, 6] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193870260 |  | S | [6, 6] | [4, 4] | endret siden 2015 | tegningen [4, 4], Street View [6, 6] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193972292 |  | S | [4, 5] | [3, 2] | endret siden 2015 | tegningen [4, 2], Street View [4, 5] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-193972489 |  | SØ | [1] | [] | endret siden 2015 | tegningen [], Street View [1] (middels sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-6242812 |  | SØ | [4, 4] | [2, 2] | endret siden 2015 | tegningen [2, 2], Street View [4, 4] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-6251331 |  | SØ | [3, 3] | [1, 1] | endret siden 2015 | tegningen [1, 1], Street View [3, 3] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| pb-33 |  | S | [0] | [] | endret siden 2015 | tegningen [], Street View [0] (høy sikkerhet): flere etasjer eller vinduer i dag enn i tegningen |
| bnr-16290424 |  | SV | [2, 3] | [2] | feil vegg | Street View så SV-siden (9 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-16308102 |  | N | [5, 6] | [] | feil vegg | Street View så N-siden (15 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193867359 |  | NØ | [1] | [5] | feil vegg | Street View så NØ-siden (12 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868053 | Undervisningsbrakke | NV | [0] | [6] | feil vegg | Street View så NV-siden (19 m), som tegningen ikke viser; tegningen viser [6] |
| bnr-193868231 | Balaklava | NØ | [4] | [4] | feil vegg | Street View så NØ-siden (12 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868231 | Balaklava | SV | [1] | [3] | feil vegg | Street View så SV-siden (11 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868274 |  | SØ | [4] | [7] | feil vegg | Street View [4] er radene på en annen tegnet vegg; på veggen sammenligningen valgte, viser tegningen [7] |
| bnr-193868290 |  | NV | [4, 4] | [5, 6, 6] | feil vegg | Street View så NV-siden (17 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868363 | Binggården | SØ/S | [1, 1] | [1, 2] | feil vegg | Street View så SØ/S-siden (12 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868444 |  | SØ | [8] | [5] | feil vegg | Street View så SØ-siden (25 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193868525 |  | SØ/N | [1, 1] | [] | feil vegg | Street View så SØ/N-siden (3 m), som tegningen ikke viser; tegningen viser [] |
| bnr-193870295 | Bakeriet | V | [10] | [13] | feil vegg | Street View så V-siden (37 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193870309 | Offisersvakten | Ø | [2] | [2] | feil vegg | Street View så Ø-siden (7 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193870317 | Det grundmurede provianthus | SØ/Ø | [0] | [6] | feil vegg | Street View så SØ/Ø-siden (71 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193870325 | Hovedvakten – det gamle slaveri | N | [1] | [4] | feil vegg | Street View så N-siden (13 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193971334 |  | NV | [3] | [3] | feil vegg | Street View så NV-siden (12 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193971954 |  | S | [3] | [3, 1] | feil vegg | Street View så S-siden (8 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193972195 |  | S | [2] | [1, 1, 1] | feil vegg | Street View så S-siden (4 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193972403 |  | N | [2, 4] | [2, 3, 2] | feil vegg | Street View så N-siden (17 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-194006187 |  | V/S | [2] | [] | feil vegg | Street View så V/S-siden (10 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| pb-45 |  | S | [0] | [] | feil vegg | Street View så S-siden (2 m), som tegningen ikke viser; tegningen viser ingen lest vegg |
| bnr-193867499 | Kommandantgården | NV | [9] | [9] | feil vegg (Street View lagt på) | Street View så NV-siden (34 m), som tegningen ikke viser: veggen har nå Street View [9] i stedet for reglene |
| bnr-193867502 | Kiørboegården | V/SV | [1, 2] | [1, 2] | feil vegg (Street View lagt på) | Street View så V/SV-siden (16 m), som tegningen ikke viser: veggen har nå Street View [1, 2] i stedet for reglene |
| bnr-193867537 | Infanterikasernen | N | [6, 5] | [6, 5] | feil vegg (Street View lagt på) | Street View så N-siden (44 m), som tegningen ikke viser: veggen har nå Street View [6, 5] i stedet for reglene |
| bnr-193867588 | Dunkejongården | N | [5, 4] | [5, 4] | feil vegg (Street View lagt på) | Street View så N-siden (22 m), som tegningen ikke viser: veggen har nå Street View [5, 4] i stedet for reglene |
| bnr-193867677 | Ingeniørgården | V | [6, 6] | [6, 6] | feil vegg (Street View lagt på) | Street View så V-siden (19 m), som tegningen ikke viser: veggen har nå Street View [6, 6] i stedet for reglene |
| bnr-193867707 |  | N | [6, 6] | [6, 6] | feil vegg (Street View lagt på) | Street View så N-siden (24 m), som tegningen ikke viser: veggen har nå Street View [6, 6] i stedet for reglene |
| bnr-193867758 |  | N | [4, 4] | [4, 4] | feil vegg (Street View lagt på) | Street View så N-siden (15 m), som tegningen ikke viser: veggen har nå Street View [4, 4] i stedet for reglene |
| bnr-193867766 |  | N | [4, 4] | [4, 4] | feil vegg (Street View lagt på) | Street View så N-siden (15 m), som tegningen ikke viser: veggen har nå Street View [4, 4] i stedet for reglene |
| bnr-193867774 |  | N | [4, 5] | [4, 5] | feil vegg (Street View lagt på) | Street View så N-siden (10 m), som tegningen ikke viser: veggen har nå Street View [4, 5] i stedet for reglene |
| bnr-193867782 |  | NV | [6, 6] | [6, 6] | feil vegg (Street View lagt på) | Street View så NV-siden (14 m), som tegningen ikke viser: veggen har nå Street View [6, 6] i stedet for reglene |
| bnr-193867936 |  | NV | [6, 3] | [6, 3] | feil vegg (Street View lagt på) | Street View så NV-siden (29 m), som tegningen ikke viser: veggen har nå Street View [6, 3] i stedet for reglene |
| bnr-193867944 |  | NV | [5] | [5] | feil vegg (Street View lagt på) | Street View så NV-siden (29 m), som tegningen ikke viser: veggen har nå Street View [5] i stedet for reglene |
| bnr-193867987 |  | NV | [2, 2] | [2, 2] | feil vegg (Street View lagt på) | Street View så NV-siden (10 m), som tegningen ikke viser: veggen har nå Street View [2, 2] i stedet for reglene |
| bnr-193868029 |  | NØ | [1, 1] | [1] | feil vegg (Street View lagt på) | Street View så NØ-siden (4 m), som tegningen ikke viser: veggen har nå Street View [1, 1] i stedet for reglene |
| bnr-193868045 | Den gamle spisesal | NV | [1] | [1] | feil vegg (Street View lagt på) | Street View så NV-siden (7 m), som tegningen ikke viser: veggen har nå Street View [1] i stedet for reglene |
| bnr-193868126 |  | NV | [2, 3] | [2, 3] | feil vegg (Street View lagt på) | Street View så NV-siden (11 m), som tegningen ikke viser: veggen har nå Street View [2, 3] i stedet for reglene |
| bnr-193868223 | Muldvadgården | NV | [4, 2] | [4, 2] | feil vegg (Street View lagt på) | Street View så NV-siden (14 m), som tegningen ikke viser: veggen har nå Street View [4, 2] i stedet for reglene |
| bnr-193868258 |  | NV | [2] | [2] | feil vegg (Street View lagt på) | Street View så NV-siden (6 m), som tegningen ikke viser: veggen har nå Street View [2] i stedet for reglene |
| bnr-193868282 |  | NV | [4] | [4] | feil vegg (Street View lagt på) | Street View så NV-siden (13 m), som tegningen ikke viser: veggen har nå Street View [4] i stedet for reglene |
| bnr-193868320 |  | SØ | [11, 11] | [11, 11] | feil vegg (Street View lagt på) | Street View så SØ-siden (25 m), som tegningen ikke viser: veggen har nå Street View [11, 11] i stedet for reglene |
| bnr-193868339 |  | NV | [1, 1] | [1, 1] | feil vegg (Street View lagt på) | Street View så NV-siden (7 m), som tegningen ikke viser: veggen har nå Street View [1, 1] i stedet for reglene |
| bnr-193868371 |  | NV | [7, 3] | [7, 3] | feil vegg (Street View lagt på) | Street View så NV-siden (27 m), som tegningen ikke viser: veggen har nå Street View [7, 3] i stedet for reglene |
| bnr-193868398 |  | NV | [5] | [5] | feil vegg (Street View lagt på) | Street View så NV-siden (14 m), som tegningen ikke viser: veggen har nå Street View [5] i stedet for reglene |
| bnr-193868428 | Kommisjonsgården | NV | [5] | [5] | feil vegg (Street View lagt på) | Street View så NV-siden (18 m), som tegningen ikke viser: veggen har nå Street View [5] i stedet for reglene |
| bnr-193868460 | Kjørbogårdens sidebygning | NV | [2] | [2] | feil vegg (Street View lagt på) | Street View så NV-siden (6 m), som tegningen ikke viser: veggen har nå Street View [2] i stedet for reglene |
| bnr-193868622 |  | NØ | [5, 4] | [5, 4] | feil vegg (Street View lagt på) | Street View så NØ-siden (12 m), som tegningen ikke viser: veggen har nå Street View [5, 4] i stedet for reglene |
| bnr-193868711 |  | NV | [3, 3] | [3, 3] | feil vegg (Street View lagt på) | Street View så NV-siden (19 m), som tegningen ikke viser: veggen har nå Street View [3, 3] i stedet for reglene |
| bnr-193870252 |  | N | [2] | [2] | feil vegg (Street View lagt på) | Street View så N-siden (9 m), som tegningen ikke viser: veggen har nå Street View [2] i stedet for reglene |
| bnr-193918239 | Bullgården | NV | [7, 5] | [7, 5] | feil vegg (Street View lagt på) | Street View så NV-siden (20 m), som tegningen ikke viser: veggen har nå Street View [7, 5] i stedet for reglene |
| bnr-193971288 |  | NØ | [2, 2] | [2, 2] | feil vegg (Street View lagt på) | Street View så NØ-siden (6 m), som tegningen ikke viser: veggen har nå Street View [2, 2] i stedet for reglene |
| bnr-193971946 |  | N | [3] | [3] | feil vegg (Street View lagt på) | Street View så N-siden (15 m), som tegningen ikke viser: veggen har nå Street View [3] i stedet for reglene |
| bnr-193972101 |  | N | [3, 3] | [3, 3] | feil vegg (Street View lagt på) | Street View så N-siden (17 m), som tegningen ikke viser: veggen har nå Street View [3, 3] i stedet for reglene |
| bnr-193972411 | Sindinggården | NV | [0] | [] | feil vegg (Street View lagt på) | Street View så NV-siden (11 m), som tegningen ikke viser: veggen har nå Street View [0] i stedet for reglene |
| bnr-6242812 |  | NØ | [5, 5] | [5, 5, 4] | feil vegg (Street View lagt på) | Street View så NØ-siden (18 m), som tegningen ikke viser: veggen har nå Street View [5, 5] i stedet for reglene |
| pb-7 |  | NØ | [0] | [] | feil vegg (Street View lagt på) | Street View så NØ-siden (9 m), som tegningen ikke viser: veggen har nå Street View [0] i stedet for reglene |
| bnr-193867510 | Ekserserhuset | SØ | [3] | [6] | feil vindu | tegningen [6], Street View [3]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193867537 | Infanterikasernen | SØ/Ø | [2, 2] | [4, 4, 4] | feil vindu | tegningen [4, 4, 4], Street View [2, 2]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193867731 |  | SØ | [3, 3] | [4, 4] | feil vindu | tegningen [4, 4], Street View [3, 3]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193867855 |  | S | [2] | [3] | feil vindu | tegningen [3], Street View [2]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193867863 |  | S | [4, 4] | [9, 10] | feil vindu | tegningen [9, 10], Street View [4, 4]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193867898 | Gamlebyen modelljernbanesenter | SØ | [6, 5] | [5, 5] | feil vindu | tegningen [5, 5], Street View [6, 5]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193867901 |  | SØ | [5, 3] | [3, 3] | feil vindu | tegningen [3, 3], Street View [5, 3]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193867936 |  | SV | [1, 1] | [2, 2, 1] | feil vindu | tegningen [2, 2, 1], Street View [1, 1]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193867979 |  | SV | [5, 6] | [7, 4, 7] | feil vindu | tegningen [7, 4, 7], Street View [5, 6]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193867987 |  | S/SØ | [2] | [4] | feil vindu | tegningen [4], Street View [2]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193868150 | Salamandergården | SV | [4, 5] | [4, 4] | feil vindu | tegningen [4, 4], Street View [4, 5]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193868258 |  | SØ | [5] | [6, 2] | feil vindu | tegningen [6, 2], Street View [5]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193868266 |  | SØ | [3, 3] | [4, 5] | feil vindu | tegningen [4, 5], Street View [3, 3]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193868274 |  | SV-gavl + S-langside mot Torvgaten | [2] | [4] | feil vindu | tegningen [4], Street View [2]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193868401 |  | SØ | [3, 4] | [4, 5] | feil vindu | tegningen [5, 5], Street View [3, 4]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193870201 |  | to hjørnefasader: kortside mot SV/plenen | [4, 4] | [3, 3] | feil vindu | tegningen [3, 3], Street View [4, 4]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193870236 |  | SØ | [2, 2] | [5, 5] | feil vindu | tegningen [5, 5], Street View [2, 2]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193870279 | Tøihuset | S | [5] | [19] | feil vindu | tegningen [19], Street View [5]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193972063 |  | SØ | [3, 3] | [2, 2] | feil vindu | tegningen [2, 2], Street View [3, 3]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193972462 |  | S | [5] | [9] | feil vindu | tegningen [9], Street View [5]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-193987370 |  | S | [7] | [13] | feil vindu | tegningen [13], Street View [7]: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står |
| bnr-6247822 |  | SØ | [5, 4] | [4, 3] | feil vindu | tegningen [4, 3], Street View [5, 4]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-6251218 |  | SØ | [4, 6] | [4, 4] | feil vindu | tegningen [4, 4], Street View [4, 6]: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står |
| bnr-193868037 | Marketenteriet | SV | [1] | [1] | feil vindu (rettet) | vektoravlesningen gir [1], som Street View; den gamle avlesningen hadde [1] |
| bnr-193869580 | Voldportravelinet | NV og SV | [2] | [2] | feil vindu (rettet) | vektoravlesningen gir [2], som Street View; den gamle avlesningen hadde [2] |
