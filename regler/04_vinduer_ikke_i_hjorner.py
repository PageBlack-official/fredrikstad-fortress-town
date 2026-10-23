"""Regel (Vegar): aldri vinduer i hjørner eller kuttet. Et vindu må ha halv bredde + 0,3 m klaring til nærmeste hjørne langs veggen."""
import numpy as np
from _felles import *
b = data('bygg'); feil = []
for i, x in gamleby(b):
    if x.get('skjul') or not x.get('vind'): continue
    P = np.array(x['p'], float); n = len(P)
    for v in x['vind']:
        q = np.array(v[:2]); w = v[7]
        # nærmeste kant og posisjonen langs den
        best = None
        for k in range(n):
            a, c = P[k], P[(k + 1) % n]; u = c - a; L = np.linalg.norm(u); u /= L
            t = float((q - a) @ u); d = abs(float((q - a)[0] * u[1] - (q - a)[1] * u[0]))
            if 0 <= t <= L and (best is None or d < best[0]): best = (d, t, L)
        if best and best[0] < 1.0 and min(best[1], best[2] - best[1]) < w / 2 + 0.3:
            feil.append(f"- bygg {i}: vindu ved ({v[0]},{v[1]}) {round(min(best[1], best[2]-best[1]),2)} m fra hjørnet (bredde {w})")
rapport('04_vinduer_ikke_i_hjorner', not feil, [f"{len(feil)} vinduer for nær et hjørne"] + feil[:60] + (['- …'] if len(feil) > 60 else []))
