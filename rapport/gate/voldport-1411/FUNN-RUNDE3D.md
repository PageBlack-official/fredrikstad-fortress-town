# FUNN runde 3d (Studio, 14.11.2026) — PAG-1597

Fables oppskrift `RUNDE3D.md` utført. **Bare data** (kilder/gate/rett-*.json → data/rettelser.json via
`fasade_rett.py`, hele kjeden kjørt). **Ingen endring i src/** (render-laget: blåstikk, foring-tone,
tospeils-sprosse, valmtak-vask er Vegars beslutning, rørt ikke). **IKKE publisert.**

Kilde: rektifisert Street View mai-2024 (`4f`, rutenett s10–24) for 75 vegg4; aug-2010-frontal (`2maj10`)
for 73 Majoren (geometri — repo-regel: vindu/dør fra 2010 gyldig, farge bare 2016+). Montasjer:
`r3/montasje-75-vegg4-3d.jpg`, `r3/montasje-73-majoren-3d.jpg` (SV | renderet by).

---

## 1. 75 vegg4 kjerne, 2. etg — SV-tall | modell-tall

**Jeg LESTE vinduene selv i rutenettet (4f) og fant noe annet enn den raske 3c-lesningen.** Fables
antydning i oppskriften (5 vinduer ca. s 11,8 / 13,7 / 15,6 / 17,3 / 21,5) stemmer på at rytmen er
**ujevn**, men de eksakte sentrene er feil: det er **ingen vindu på s13,7** — der er det en **blank bay**
(klar lektekledning, ingen karm, verifisert med pikseldetektor + nærutsnitt `/tmp`-kontroll).

| | SV 4f (lest i meter) | Modell FØR (3c) | Modell NÅ (3d) |
|---|---|---|---|
| 2.etg kjerne-vinduer | sentre **12,3 · 15,2 · 16,75 · 18,6 · 20,4** (5 stk, ~1,1 m brede, ~1,9 m høye) | 9 små i **jevn** rytme (sentre 10,6/13,1/15,5/18,0/20,4/22,9 …) | 5 verifiserte vinduer på de leste sentrene + mørkebrun foring |
| blank bay | **s13–14,5 (ingen vindu)** | vindu lå der (feil) | tomt (rettet) |
| s21–24 | **skjult av Googles info-boks** i både 4f og 4f-box | — | ett rytme-utledet vindu s22,4, **FLAGGET** (ikke kilde-verifisert) |

Vinduene er hvite med T-post og **mørkebrun foring** (`#4a342c`, satt som element-farge, samme som
vegg5). T-post/tospeils-modus og foring-tonen i renderen er src/07-sak (flagget til Vegar, 3c-laget).

### Hvorfor slo ikke 3b/3c-kjernen gjennom i 2. etg? (oppskriftens spørsmål)
**Verken `vinduer_regler` eller `fasade_rett`-merknaden overstyrte noe.** Årsaken er enklere: 2.-etasjes
kjerne-vinduer ble **aldri lest vindu-for-vindu** i 3b/3c. Jeg sammenlignet `rett-v4-kjerne.json` mellom
3b (`1244eb6`) og 3c (`d9f8642`): 1. etg ble målt nøye, men 2. etg sto hele tiden som en **jevn
plassholder-rytme** (sentre ~2,5 m fra hverandre). `fasade_rett.py` kjører sist i kjeden og tegnet derfor
akkurat den jevne plassholderen — renderen var tro mot dataene, dataene var bare ikke lest ferdig.
Skrevet i LESMEG under «Byggene: kjeden».

## 2. 75 vegg4 kjerne, 1. etg — SV-tall | modell-tall

SV 4f fra venstre (s10→s24, i rutenettet): butikkvindu (Emm K) · dør · butikkvindu (Emm K) ·
nedløpsrør ~s16 · butikkvindu (Gamlebyen Elektriske AS) · dør · butikkvindu (Gamlebyen Elektriske) · dør.
Alle i **mørkebrune rammer**, store butikkvinduer — **ikke** de små, jevne vinduene/dørene renderen hadde.

| element | SV (s, meter) | kommentar |
|---|---|---|
| butikk Emm K 1 | 10,2–12,4 | z 0,3–2,9 |
| dør | 12,5–13,2 | |
| butikk Emm K 2 | 13,3–15,4 | |
| *(nedløpsrør)* | ~16 | ikke element |
| butikk Gamlebyen Elektriske | 16,5–19,0 | teglrefleks + skilt |
| dør | 19,5–20,5 | |
| butikk Gamlebyen Elektriske 2 | 21,0–23,1 | |
| dør | 23,4–24,2 | hjørne mot Voldgaten-enden |

Modell NÅ: de samme 8 elementene lest i meter (var før: butikk 10,0–11,3 / dør / butikk 12,7–14,3 /
butikk 15,3–17,1 / dør / dør / butikk 20,6–23,3 — for små og for mange småfelt).

## 3. 75 veggfarge — vegg4 vs vegg5 (målt hver for seg, FARGER.md)

| vegg | bilde | RGB-median (rent veggfelt) | lys | ord |
|---|---|---|---|---|
| vegg4 | 4f | **[164, 155, 156]** (n=60) | sol | lys **varm grå / gråbeige** (R høyest) |
| vegg5 | 5f | **[151, 151, 153]** (n=102) | mer skygge | lys grå, nær nøytral |
| *data i dag* | — | [150, 152, 158] (3c, kjølig) | — | B høyest = blåligst |

Pikselutsnitt: `r3/veggfarge-vegg4-4f.png`, `r3/veggfarge-vegg5-5f.png`. **Forskjellen vegg4↔vegg5 er
lys (sol vs skygge), ikke to malingskulører** — samme bygg, samme puss. Derfor **ikke** splittet i
veggfelt/segment. Men: lagret farge `[150,152,158]` er både **kjøligere og mørkere** enn sollyset vegg4
([164,155,156] varmgrå). Dette er samme lyse-vegg-blåstikk-spørsmålet Vegar eier (3c-laget); jeg **flagger
måletallet og rører ikke fargefeltet** her. Anbefaling til fargepasset: varmgrå ~[164,155,156].

## 4. 73 Majoren, 1. etg — SV-tall | modell-tall

2010-frontalen (`2maj10`, oblikt, grov ±0,5 m) fra venstre (s0 venstre hjørne → s12 portrom-enden):
lite vindu ytterst venstre · inngang m/ trapp (MAJORENS KRO & STUE) · **ETT** stort butikkvindu (~3,5 m) ·
**portrom til høyre med RETT, flat overkant** (bekreftet i nærutsnitt — ikke rundbue).

| element | SV (s, meter) | FØR 3c | NÅ 3d |
|---|---|---|---|
| lite vindu | 0,3–1,1 | manglet | lagt inn |
| inngang/dør (trapp) | 2,0–3,0 | dør 5,7–6,8 (feil sted) | rettet |
| stort butikkvindu ~3,5 m | 3,4–6,9 | 2 butikker (2,6–5,0 + 7,3–9,7) | ett bredt |
| **portrom** | 8,5–11,8 | **rundbuet port s0,2–2,2 (feil ende, bue=1)** | **flat port, typ 1, bue=0, i riktig ende** |

Verifisert i data: Majorens eneste store element er nå `b=3,30 h=3,00 typ=1 bue=0` (flat port). Ingen
`bue` igjen på bygget.

## 5. 73 Majoren, 2. etg — SV-tall | modell-tall

2010 viser **4 vinduer + ett bredere til høyre over porten**.

| | SV (sentre, meter) |
|---|---|
| 4 vinduer | 1,0 · 2,55 · 3,95 · 6,85 |
| bredere over port | ~11,1 (s10,3–11,9) |

Modell FØR (3c): 5 jevne (sentre 3,3/4,8/6,8/8,3/10,2). NÅ: 4 + 1 bredt som over.

---

## Regler
Hele `bygg_kjede.py` kjørte grønt (py-env m/ pyproj+shapely). `fasade_rett.py`: 75 hus med rettet fasade;
928 = 42 elementer på 2 vegger, 622 = 9 elementer på vegg2. Regel 02/04/17 berører lest fasade og står.

## Leveranse
Data satt og verifisert i `data/rettelser.json`. Montasjer i `r3/`. **IKKE publisert.** Render-pipeline-laget
(blåstikk/foring/tospeils/valmtak + veggfarge-varme) løftet til Vegar via CEO, ikke en ny selvgenerert runde.
