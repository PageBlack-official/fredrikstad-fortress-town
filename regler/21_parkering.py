"""Regel: parkeringen i kartet er kommunens parkering, med kilde for alt og ingen gjettede tall.
- data/parkering.json har nøyaktig plassene i kommunens lag 1 (kilder/parkering-kommunen.json) innenfor området (verktoy/parkering.py)
- hver plass har kategori, regler, kilde-URL; antall bare når ANTALL står i laget, ellers «antall_kilde» som sier ukjent
- hver plass har målt flate (p) eller en grunn (uten_flate); en målt flate ligger innen 30 m fra kommunens punkt og står ikke på et hus
  (feil over 25 % av flaten inne i husomriss, advarsel over 10 %: håndmålt ±2 m mot FKB-omrisset)
- kilder/parkering-regler.json har 2026-prisene og kilde-URL for hver regel
Bevis: rapport/torvet/parkering.png (python3 verktoy/parkering.py ark; ortofotoversjonen ark orto ligger bare lokalt)."""
import os, sys, json
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import datalag
import parkering as PK
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

MAKS_AVSTAND, MAKS_HUS, VARSEL_HUS = 30, 0.25, 0.10
feil, linjer, adv = [], [], []
d = datalag.alle(); P = d['parkering']
k = json.load(open(os.path.join(ROT, 'kilder', 'parkering-kommunen.json'), encoding='utf8'))
x0, y0, x1, y1 = PK.OMRAADE
i_laget = set()
for f in k['lag']['plasser']:
    x, y = datalag.til_modell(*f['geometry']['coordinates'])
    if x0 <= x <= x1 and y0 <= y <= y1: i_laget.add(f"parkering-1-{f['properties']['OBJECTID']}")
ids = {p['id'] for p in P}
if ids != i_laget:
    feil.append(f"- dataene og kommunens lag er ulike: mangler {sorted(i_laget - ids)}, ekstra {sorted(ids - i_laget)} (kjør verktoy/parkering.py lag)")
hus = unary_union([Polygon(b['p']).buffer(0) for b in d['bygg'] if not b.get('skjul') and len(b['p']) >= 3])
for p in P:
    n = f"{p['id']} ({p.get('navn')})"
    for felt in ('kategori', 'regler', 'kilde_url', 'antall_kilde'):
        if not p.get(felt): feil.append(f"- {n}: mangler {felt}")
    if 'antall' in p and not (isinstance(p['antall'], int) and 'ANTALL' in p.get('antall_kilde', '') and 'ukjent' not in p['antall_kilde']):
        feil.append(f"- {n}: antall {p['antall']!r} uten kilde i kommunens lag")
    if 'antall' not in p and 'ukjent' not in p.get('antall_kilde', ''):
        feil.append(f"- {n}: antall mangler, men antall_kilde sier ikke ukjent")
    if not p.get('p') and not p.get('uten_flate'): feil.append(f"- {n}: verken målt flate eller grunn")
    if p.get('p'):
        pol = Polygon(p['p']).buffer(0); a = pol.distance(Point(p['x'], p['y']))
        if a > MAKS_AVSTAND: feil.append(f"- {n}: flaten ligger {a:.0f} m fra kommunens punkt")
        andel = pol.intersection(hus).area / max(pol.area, 1e-6)
        if andel > MAKS_HUS: feil.append(f"- {n}: {andel:.0%} av flaten står på hus")
        elif andel > VARSEL_HUS: adv.append(f"- advarsel {n}: {andel:.0%} av flaten står på hus ({p.get('maalt', '')})")
R = json.load(open(os.path.join(ROT, 'kilder', 'parkering-regler.json'), encoding='utf8'))
for s in ('grønn', 'rød'):
    if '2026' not in R['soner'].get(s, {}).get('pris', ''): feil.append(f"- parkering-regler.json: {s} sone mangler 2026-pris")
for nokkel, v in R.items():
    if isinstance(v, dict) and 'kilde' in v and v['kilde'] not in R['kilder']: feil.append(f"- parkering-regler.json: {nokkel} peker på ukjent kilde {v['kilde']}")
kat = {}
for p in P:
    for c in p.get('kategori', []): kat[c] = kat.get(c, 0) + 1
linjer.append(f"{len(P)} plasser fra kommunens lag, {sum(1 for p in P if p.get('p'))} med målt flate, {sum(1 for p in P if p.get('uten_flate'))} med grunn; "
              f"antall kjent for {sum(1 for p in P if 'antall' in p)} ({sum(p.get('antall', 0) for p in P)} plasser), ukjent for {sum(1 for p in P if 'antall' not in p)}")
linjer.append('kategorier: ' + ', '.join(f"{c} {n}" for c, n in sorted(kat.items(), key=lambda t: -t[1])))
linjer += feil + adv
rapport('21_parkering', not feil, linjer, 'rapport/torvet/parkering.png')
