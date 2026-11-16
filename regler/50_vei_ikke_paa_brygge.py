"""Regel (Vegar 16.11, «rare greiene på brygga»): ingen vei eller gangvei tegnes oppå en brygge. Brygga er flaten;
et veibånd som ligger på den, blir et hevet bånd med sider ned i vannet. En vei som ligger minst 50 % av lengden sin inne
i et brygge-omriss (data/brygger.json) skal være tatt ut av de tegnede veibåndene (data/landskap.json «veier», tegnes i
src/08). Fjerningen skjer i verktoy/bakke.py (gater), sammen med gress-regelen; denne regelen er rød hvis noe slapp gjennom.
Gjelder alle brygger."""
from _felles import *
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

KRAV = 0.5
L = data('landskap'); br = data('brygger')
bry = [Polygon(b['p']).buffer(0) for b in br if not b.get('skjul') and len(b.get('p', [])) >= 3]
U = unary_union(bry) if bry else None
feil, linjer = [], []
paa = []
if U is not None:
    for v in L['veier']:
        lin = LineString([q[:2] for q in v['p']])
        if lin.length <= 0:
            continue
        frac = lin.intersection(U).length / lin.length
        if frac >= KRAV:
            paa.append((v, frac))
linjer.append(f"{len(L['veier'])} veibånd tegnet, {len(bry)} brygger; {len(paa)} vei(er) ligger ≥ {KRAV:.0%} på en brygge "
              f"(krav: 0 — brygga er flaten)")
for v, fr in paa:
    x0, y0 = v['p'][0][:2]
    feil.append(f"- en «{v['k']}»-vei ligger {fr:.0%} på en brygge (fra {x0:.0f}, {y0:.0f}); ta den ut i verktoy/bakke.py (gater)")
rapport('50_vei_ikke_paa_brygge', not feil, linjer + feil)
