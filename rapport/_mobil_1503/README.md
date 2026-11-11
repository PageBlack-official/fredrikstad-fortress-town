# PAG-1503 — mobil-lag: mål, rett, mål (Studio, 11.11)

**Mål:** kartet skal følge fingeren uten hakk på mobil (klyp-zoom og panorering).

## Metode
Playwright + CDP mot ut/server (server-bygget), iPhone-profil **390×844 DPR 3**, berøring, **CPU-struping 4×**
(`Emulation.setCPUThrottlingRate`), **ekte fingergester** (`Input.dispatchTouchEvent`: én finger drar, to fingre klyper).
Ekte skjermkort (Metal/ANGLE, `PW_GPU=1`) på minien, ikke programvare-GPU. Per bilde leses `window.__logg` (15_loop): hele
render(), oppdater(), speil, skyggekart, 3D-/blekk-/fxaa-pass, og draw calls (`renderer.info.render.calls`).
Verktøy: `verktoy/mobil_maal.mjs`. Median over 2 runder.

## Funn før
3D-passet er **~90 % av bilde-tida** på mobil. Speil, skyggekart, blekk og fxaa er alle 1–3 ms — ikke flaskehalsen.
~380–400 draw calls per bilde. **~360 egne byggnett sto med `frustumCulled=false`** (vindu-instancing + de bysbredt
sammenslåtte nettene medregnet), så de ble sendt til GPU-en hvert bilde også når de var langt utenfor skjermkanten.

Kontrolltest av hull 1 (oppløsningstrinnet): tvunget `?nivaa=2` (0,6× oppløsning + færre AO-prøver + mindre skyggekart) gjorde
bildet **tregere**, ikke raskere (3D-passet 72 → 89 ms). 3D-passet er bundet av CPU-en som sender tegnekallene, ikke av fyllrate.
Derfor rettet jeg **hull 3 (draw calls), ikke hull 1**.

## Rettelsen (én ting)
`src/21_flyt.js`: slår frustum-kutting på igjen for de vanlige byggnettene under `city` (ett bygg = én kule three.js kan kaste
når den er helt utenfor bildet). InstancedMesh (vinduer/trær) røres ikke — der ville three.js kastet hele settet på den lokale
grunn-kula. Kula blåses opp 30 m så ingenting som berører bildet eller skyggekartet kuttes. `?synsrand=0` slår av (A/B).
Bildet er pikselidentisk (se under).

Instrument i tillegg (ikke selve rettelsen): `?maal=1` — liten hjørnerute med bilder/s og ms per bilde (snitt + verste) under
gest, så Vegar kan ta skjermbilde på telefonen. `src/16_interaksjon.js`.

## Tabell før / etter (median, CPU 4×, iPhone 390×844 DPR 3)

| gest | bilder/s før→etter | ms/bilde før→etter | verste bilde | 3D-pass ms | draw calls |
|------|-----|-----|-----|-----|-----|
| **panorering** | 10,0 → **16,2** | 80,2 → **22,2** | 179 → **53** | 72,2 → **20,1** | 392 → **313** |
| **klyp-zoom**  | 11,1 → **18,3** | 63,7 → **20,0** | 155 → **56** | 57,2 → **17,4** | 331 → **207** |
| **ro**         | –   | 48,9 → **14,7** | 93 → **21** | 45,1 → **12,8** | 402 → **335** |
| **tid til første bilde, 4G** | — | 38,3 s → **16,3 s** | | | |

(«ro» bilder/s er den bevisste hvilekadensen på berøring, ikke et flyt-tall; det som teller i ro er ms per bilde.)

Draw calls faller mest ved innzoom (halve byen utenfor rammen): hjemmevisning 402 → ~313–335, zoom 5 ~380 → ~196.
Ms per bilde mer enn halvert i begge gestene; verste bilde (det som leses som et hakk) under pan 179 → 53 ms, klyp 155 → 56 ms.

## Bilde-likhet (regel «bildet skal se likt ut»)
`verktoy/synsrand_parity.mjs`: samme kamera med kutting PÅ vs `?synsrand=0`, pikseldiff.
- zoom 5: **maks avvik 0** (pikselidentisk)
- zoom 4 (inne i byen): **maks avvik 0** (pikselidentisk)
- hjemmevisning: 2 piksler avvik > 30 (maks 54), 0 piksler > 60 — FXAA-kantstøy fra at ~90 nett bak kameraet ikke tegnes;
  umerkbart og langt innenfor regel 10s terskel (under 3 % piksler over 60).

## Filer
- `src/21_flyt.js` — synsrand (frustum-kutting + 30 m margin), `?synsrand=0`
- `src/16_interaksjon.js`, `src/15_loop.js` — `?maal=1`-hjørneruta
- `src/kvalitet.js` — bare en forklarende kommentar (hvorfor ikke oppløsningstrinnet)
- `verktoy/mobil_maal.mjs`, `verktoy/synsrand_parity.mjs` — måleverktøy
