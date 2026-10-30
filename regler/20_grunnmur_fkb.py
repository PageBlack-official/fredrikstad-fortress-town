"""Regel (29.10): grunnmuren i Gamlebyen følger kommunens oppmålte omriss (kommunekartet, FKB; verktoy/kommunekart.py).
- hvert kommunehus i Gamlebyen på minst 6 m² har modellhus over seg: husene som ligger i det (minst halve arealet inni)
  dekker det med IoU >= 0,7 (flere modellhus i samme kommunehus er lov: rekkehus med egne bygningsnummer)
- ingen modellhus dekker to eller flere kommunehus (overlapp over 1 m² og 10 % av kommunehuset)
Husdelingen etter tegningen (kilder/husdeling.json, verktoy/husdeling.py, 30.10): hus som er slått sammen fordi tegningen
viser ett hus der kommunekartet har to, kan dekke flere kommunehus; de står som unntak med grunnen, og kommunehusene de dekker,
måles mot det sammenslåtte huset.
Unntak som står i rapporten: kirka (06_kirka), Kaserna (verktoy/kaserna.py) og portbyggene (data/porter.json) bygges for seg
og røres ikke av verktoy/grunnmur.py. Hus utenfor kartrammen har ingen kommunedata og sjekkes ikke.
Uten kommunekartet (kilder/kommunekart/kommunekart.pdf ligger bare lokalt) kan regelen ikke kjøres og er rød."""
import sys
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
try:
    import kommunekart
    K = kommunekart.omriss(); DEK = kommunekart.dekning(); Kin = kommunekart.i_gamlebyen(K, DEK)
except SystemExit as e:
    rapport('20_grunnmur_fkb', False, [f'kommunekartet mangler: {e}']); raise SystemExit(0)
b = data('bygg'); d_porter = data('porter')
fredet = {x['id'] for x in b if x.get('kirke')} | {p['bygg_id'] for p in d_porter if p.get('bygg_id')} | {'bnr-193867537'}
def poly(x):
    P = Polygon(x['p'], [r for r in (x.get('ph') or []) if len(r) > 2]); return P if P.is_valid else P.buffer(0)
vis = [x for x in b if len(x['p']) >= 3 and not x.get('skjul')]
P = {x['id']: poly(x) for x in vis}
gml = {x['id'] for x in vis if x.get('gml')}
ids = list(P); tre = shapely.STRtree([P[i] for i in ids])
import json as _json
_hd = os.path.join(ROT, 'kilder', 'husdeling.json')
SAMMEN = {}
if os.path.exists(_hd):
    for S_ in _json.load(open(_hd, encoding='utf8')).get('sammen', []):
        SAMMEN[S_['ids'][0]] = S_.get('grunn', '')
feil_dekning, feil_flere, unntak = [], [], []
dekker = {}; n = 0
for j in Kin:
    k = K[j]
    if k.area < 6:
        continue
    treff = [ids[int(t)] for t in tre.query(k)]
    if any(i not in gml and P[i].intersection(k).area > 0.5 * k.area for i in treff):
        continue      # huset hører til et bygg utenfor Gamlebyen (gml 0), samme utvalg som verktoy/grunnmur.py
    n += 1
    inni = [i for i in treff if P[i].intersection(k).area >= 0.5 * P[i].area or (i in SAMMEN and P[i].intersection(k).area >= 0.5 * k.area)]
    for i in treff:
        a = P[i].intersection(k).area
        if a > 1.0 and a > 0.1 * k.area:
            dekker.setdefault(i, []).append(j)
    # et hus slått sammen etter tegningen måles bare på sin del i dette kommunehuset
    U = unary_union([P[i].intersection(k.buffer(1.0)) if i in SAMMEN else P[i] for i in inni]) if inni else Polygon()
    iou = U.intersection(k).area / U.union(k).area if inni else 0.0
    if any(i in fredet for i in treff if P[i].intersection(k).area > 0.5 * k.area):
        unntak.append(f"- kommunehus {j} ({k.area:.0f} m²) under fredet bygg {', '.join(i for i in treff if i in fredet)}: IoU {iou:.2f}")
        continue
    if iou < 0.7:
        c = k.representative_point()
        feil_dekning.append(f"- kommunehus {j} ({k.area:.0f} m², ved {c.x:.0f}, {c.y:.0f}): IoU {iou:.2f} med {', '.join(inni) or 'ingen modellhus'}")
for i, js in dekker.items():
    if len(js) >= 2 and i in gml:
        if i in fredet:
            unntak.append(f"- {i} (fredet) dekker kommunehus {', '.join(map(str, js))}")
        elif i in SAMMEN:
            unntak.append(f"- {i} dekker kommunehus {', '.join(map(str, js))}: slått sammen etter tegningen ({SAMMEN[i]})")
        else:
            feil_flere.append(f"- {i} dekker {len(js)} kommunehus: {', '.join(map(str, js))}")
ok = not feil_dekning and not feil_flere
linjer = [f"{n} kommunehus i Gamlebyen over 6 m²: {len(feil_dekning)} uten modellhus med IoU >= 0,7; {len(feil_flere)} modellhus dekker flere kommunehus; {len(unntak)} unntak (fredet)"]
if feil_dekning: linjer += ['', '## Kommunehus uten modellhus som dekker dem (IoU < 0,7)'] + feil_dekning[:80] + (['- …'] if len(feil_dekning) > 80 else [])
if feil_flere: linjer += ['', '## Modellhus over flere kommunehus'] + feil_flere
if unntak: linjer += ['', '## Unntak'] + unntak
linjer.append('\nOmrissene legges inn av verktoy/grunnmur.py (LESMEG: «Grunnmuren fra kommunekartet»).')
rapport('20_grunnmur_fkb', ok, linjer)
