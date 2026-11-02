"""Regel (02.11, avvik A2): ingen løse småbygg oppå porter og murer, og ingen mur tvers gjennom et portbygg.
Vegar 02.11 16:44: «Det har også kommet et rart lite hus foran en port der, men er plassert feil.»
Årsaken: Kasernens port mot gata (teglmurer mu-1, verktoy/kaserna.py 27.10) stod midt i muren, og FKB-skuret pb-46 (grunnmur.py 29.10)
kom inn akkurat der: et lite beige hus med dør stod i porten. Porten mot kirka (pb-51, portbygg i data/porter.json 30.10) hadde muren
mu-2 tvers gjennom buen. Regelen er rød når
  - en port i en mur (teglmurer[].port) overlapper et hus som vises,
  - en mur går gjennom et portbygg (porter typ mur) eller under 1 m foran det, uten åpning der (teglmurer[].aapninger),
  - et hus under 15 m² står med mer enn 0,5 m² i en gårdsmur, eller med mer enn 15 % i en OSM-mur eller et annet hus (løst småbygg plassert feil).
"""
import sys, math
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402
from shapely.geometry import Polygon, LineString  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

d = datalag.alle()
B = [b for b in d['bygg'] if not b.get('skjul') and b.get('p') and len(b['p']) >= 3]
P = {b['id']: Polygon(b['p']).buffer(0) for b in B}
porter = {pt['bygg_id']: pt for pt in d.get('porter', [])}
linjer, feil = [], []
murflater = []
for mu in d.get('teglmurer', []):
    if mu.get('skjul'): continue
    a, c = mu['p']; L = math.hypot(c[0] - a[0], c[1] - a[1]); linje = LineString(mu['p'])
    murflater.append((mu['id'], linje.buffer(mu['tykk'] / 2, cap_style=2)))
    pt = mu.get('port')
    if pt:
        s = pt['s'] * L; tx, ty = (c[0] - a[0]) / L, (c[1] - a[1]) / L
        q0 = (a[0] + tx * (s - pt['pilar'] / 2), a[1] + ty * (s - pt['pilar'] / 2)); q1 = (a[0] + tx * (s + pt['pilar'] / 2), a[1] + ty * (s + pt['pilar'] / 2))
        port = LineString([q0, q1]).buffer(1.5, cap_style=2)   # porten og passasjen 1,5 m på hver side
        for i, Pb in P.items():
            if Pb.intersection(port).area > 0.3:
                feil.append(f"FEIL porten i {mu['id']} ({mu['port'].get('navn')}) står i huset {i} ({Pb.intersection(port).area:.1f} m²)")
    aap = mu.get('aapninger') or []
    for i, pt_ in porter.items():
        if pt_.get('typ') != 'mur' or i not in P: continue
        g = linje.intersection(P[i].buffer(1.0))   # gjennom portbygget, eller tett langs det foran buen
        if g.length > 0.5 and not any(q[2] == i for q in aap):
            feil.append(f"FEIL muren {mu['id']} går {g.length:.1f} m gjennom eller foran portbygget {i} uten åpning (teglmurer[].aapninger)")
    for q in aap:
        linjer.append(f"ok   {mu['id']}: åpning {q[0]:.1f}–{q[1]:.1f} m for portbygget {q[2]}")
for mu in d.get('murer', []):
    if len(mu.get('p') or []) >= 2: murflater.append((f"murer:{mu.get('t')}", LineString(mu['p']).buffer(0.3, cap_style=2)))
T = STRtree(list(P.values())); ids = list(P.keys())
for b in B:
    Pb = P[b['id']]
    if Pb.area >= 15 or b['id'] in porter: continue
    # gårdsmurene (teglmurer) er tegnet etter FKB og ortofoto: 0,5 m² er feil. OSM-murene (data/murer.json) og nabohus med omriss
    # utenfor kommunekartet er grovere: feil først når mer enn 15 % av småbygget står i dem (pb-37 og pb-43: 5 og 10 %, 02.11)
    for navn, M in murflater:
        a_ = Pb.intersection(M).area
        if a_ > (0.5 if not navn.startswith('murer:') else 0.15 * Pb.area): feil.append(f"FEIL småbygget {b['id']} ({Pb.area:.0f} m²) står {a_:.1f} m² i muren {navn}")
    for j in T.query(Pb):
        o = ids[j]
        a_ = Pb.intersection(P[o]).area if o != b['id'] else 0
        if a_ > 0.15 * Pb.area:
            feil.append(f"FEIL småbygget {b['id']} ({Pb.area:.0f} m²) står {a_:.1f} m² i huset {o}")
        elif a_ > 0.5:
            linjer.append(f"merk {b['id']} ({Pb.area:.0f} m²) overlapper {o} med {a_:.1f} m² ({a_ / Pb.area:.0%}, omrisset til naboen er grovt)")
# portalene har farge fra en dømt kilde (A14, 02.11: Mellomporten stod rød etter en udømt trykkfarge)
BYm = {b['id']: b for b in d['bygg']}
for i, pt_ in porter.items():
    if pt_.get('typ') == 'mur' and i in BYm and 'ikke dømt' in str(BYm[i].get('vegg_kilde') or ''):
        feil.append(f"FEIL portalen {i} ({BYm[i].get('navn') or ''}) har farge fra en udømt trykkfarge")
rapport('38_porter_og_murer_fri', not feil, [f"{len(feil)} feil; {len(murflater)} murer, {len(porter)} portbygg, {sum(1 for b in B if P[b['id']].area < 15)} småbygg under 15 m²"] + feil + linjer)
