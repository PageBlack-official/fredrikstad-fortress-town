"""Regel (25.10, Vegar: «tårnet bak kirka er ikke frittstående»): en bygningsdel som rager over kroppen (tårn) skal stå der Kartverkets
høydemodell (DOM−DTM) faktisk har en topp. Rådhustårnet stod 17 m for langt nord, utenfor kroppen, i alle versjoner til v32.
Sjekk: innenfor delens omriss skal p90 av DOM−DTM ligge minst 3 m over hovedkroppens målte p50, og delens topp (h) skal ligge
innen 4 m av målt maks (spir klippes i 1 m-modell, så målt kan være lavere)."""
import json, os, sys, numpy as np, importlib.util
from _felles import *
H = os.path.join(ROT, 'rapport', 'hoyder')
spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
dom, gt = hent.les(os.path.join(H, 'kilder', 'dom1_25832.tif')); dtm, _ = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif')); ndh = dom - dtm; x0, y0, dx, dy = gt
import matplotlib.path as mp
ys, xs = np.mgrid[0:ndh.shape[0], 0:ndh.shape[1]]; PTS = np.c_[xs.ravel() + 0.5, ys.ravel() + 0.5]
def inne(p):
    P = hent.til_utm(np.array(p, float)); path = mp.Path([((e - x0) / dx, (y0 - n) / dy) for e, n in P])
    v = ndh[path.contains_points(PTS).reshape(xs.shape)]; return v[~np.isnan(v)]
b = data('bygg'); linjer = []; ok = True
for i, x in enumerate(b):
    if x.get('kirke') or x.get('skjul'): continue
    for k, d in enumerate(x.get('deler') or []):
        if d.get('h', 0) <= x.get('h', 0) + 2: continue
        vd, vk = inne(d['p']), inne(x['p'])
        if len(vd) < 4 or len(vk) < 10: linjer.append(f'- bygg {i} del {k}: for få piksler'); continue
        p90, mk, kropp = np.percentile(vd, 90), vd.max(), np.percentile(vk, 50)
        god = p90 >= kropp + 3 and abs(d['h'] - mk) <= 4
        ok = ok and god
        linjer.append(f"- bygg {i} ({x.get('navn')}) del {k}: h {d['h']}, målt topp {mk:.1f}, p90 i delen {p90:.1f}, kropp p50 {kropp:.1f} → {'ok' if god else 'FEIL'}")
rapport('13_deler_staar_paa_topp', ok, linjer or ['- ingen deler å sjekke'])
