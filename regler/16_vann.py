"""Regel: vannet i kartet stemmer med ortofoto 2024 (Fredrikstad kommune; hent med verktoy/vann.py hent og maske).
Fasiten er vannmasken verktoy/vann.py maske lager av ortofotoet (kilder/ortofoto-2024/vannfasit.png, ikke i git), med det
fotoet ikke ser lagt til: vann under trekroner og takutstikk (kartets egne trær og hus), smale grøfter målt for hånd
(kilder/vann-maalt.json). Innen kartrammen (±860 m):
- minst 98,5 % av vannflaten i kartet er vann i ortofotoet
- minst 98,5 % av vannet i ortofotoet er vann i kartet
- strandlinja: 90 % av kanten ligger innen 1,5 m fra fotoets, per strekning (Glomma vest, fergeleiet, vollgravene, Isegran)
- hver vannflate har fast id (vn-) og kanttype for hver kant (k = kai/mur/brygge, n = naturlig) som data
Merk: data/vann.json er laget av verktoy/vann.py lag mot den samme fasiten, så tallene viser at dataene følger fasiten;
at fasiten følger virkeligheten, vises av kontrollarkene (rapport/vann/<strekning>-etter.jpg).
Bevis: rapport/16_vann.jpg (ortofoto, ikke i git: gult = vann i fotoet, magenta = kai, grønt = naturlig kant i kartet)."""
import os, sys, json
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import vann as V

KRAV_PRESISJON, KRAV_DEKNING, KRAV_P90 = 0.985, 0.985, 1.5
T = V.les_fasit() if os.path.exists(V.FASIT) else None
if T is None or not any(f.endswith('.jpg') for f in os.listdir(V.flater.ORTO)):
    rapport('16_vann', False, ['ortofotoet eller vannfasiten mangler: kjør python3 verktoy/vann.py hent og maske (ligger ikke i git, lisensen er ikke avklart)'])
    raise SystemExit
import datalag, cv2
vv = datalag.alle()['vann']
feil, linjer = [], []
# id og kanttype
ids = [v.get('id') for v in vv]
if None in ids: feil.append(f"- {ids.count(None)} vannflater uten id (kjør verktoy/vann.py lag)")
for v in vv:
    if v.get('skjul'): continue
    for r, kt in [(v['p'], v.get('kant'))] + list(zip(v['h'], v.get('hkant') or [None] * len(v['h']))):
        if kt is None or len(kt) != len(r) or set(kt) - {'k', 'n'}:
            feil.append(f"- {v.get('id')}: kanttypen mangler eller har feil lengde"); break
K = V.tegn(vv); R = V.ramme()
pres, dekn = V.dekning(K, T, R)
O = V.tegn(V.osm()); pres0, dekn0 = V.dekning(O, T, R)
linjer.append(f"{pres:.2%} av kartets vann er vann i ortofotoet (krav {KRAV_PRESISJON:.1%}), {dekn:.2%} av ortofotoets vann er dekket "
              f"(krav {KRAV_DEKNING:.1%}); før retting (OSM): {pres0:.2%} og {dekn0:.2%}")
if pres < KRAV_PRESISJON: feil.append(f"- for mye vann i kartet der fotoet viser land: {pres:.2%}")
if dekn < KRAV_DEKNING: feil.append(f"- vann i fotoet som kartet tegner som land: {dekn:.2%} dekket")
linjer.append('')
linjer.append('| strekning | før: median / p90 / p99 (m) | etter: median / p90 / p99 (m) |')
linjer.append('|---|---|---|')
for navn, bx in V.STREKNINGER.items():
    a0, a1 = V.kantavvik(O, T, bx), V.kantavvik(K, T, bx)
    linjer.append(f"| {navn} | {' / '.join(map(str, a0))} | {' / '.join(map(str, a1))} |")
    if a1[1] > KRAV_P90: feil.append(f"- {navn}: 90 % av strandlinja innen {a1[1]} m (krav {KRAV_P90} m)")
kai = sum(v.get('kant', '').count('k') + sum(x.count('k') for x in v.get('hkant', [])) for v in vv)
alle = sum(len(v.get('kant', '')) + sum(len(x) for x in v.get('hkant', [])) for v in vv)
linjer.append('')
linjer.append(f"{len([v for v in vv if not v.get('skjul')])} vannflater, {alle} kanter, {kai} kai/mur/brygge (kilder/vann-maalt.json), resten naturlig")
# bevis
M = V.mosaikk(); s = 0.18
im = cv2.resize(M, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
cs, _ = cv2.findContours(cv2.resize(T, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_NEAREST), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(im, cs, -1, (0, 230, 255), 1)
for v in vv:
    if v.get('skjul'): continue
    for r, kt in [(v['p'], v.get('kant', ''))] + list(zip(v['h'], v.get('hkant', []))):
        for i in range(len(r)):
            a = V.til_px(*r[i]); b = V.til_px(*r[(i + 1) % len(r)])
            cv2.line(im, (int(a[0] * s), int(a[1] * s)), (int(b[0] * s), int(b[1] * s)), (255, 0, 255) if kt[i:i + 1] == 'k' else (60, 220, 60), 1)
cv2.imwrite(os.path.join(ROT, 'rapport', '16_vann.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 82])
rapport('16_vann', not feil, linjer + feil, 'rapport/16_vann.jpg (ikke i git) og rapport/vann/*-etter.jpg (verktoy/vann.py kontroll)')
