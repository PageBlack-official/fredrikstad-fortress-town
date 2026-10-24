"""Vinduer for nær et hjørne (regel 04) flyttes langs veggen til klaring halv bredde + 0,3 m; får det ikke plass, eller kolliderer det
med naboen på samme vegg, fjernes det. Resultatet er rettelser i data/rettelser.json (felt vind per bygg). Kjøres på nytt ved behov."""
import json, sys, os, numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROT, 'regler')); from _felles import gamleby
b = json.load(open(os.path.join(ROT, 'data/bygg.json')))
ret = json.load(open(os.path.join(ROT, 'data/rettelser.json')))
# egne, tidligere regel 04-rettelser tas ut først, så kjøringen alltid starter fra det samme grunnlaget (idempotent); andre rettelser legges oppå
ret = [r for r in ret if not (r['emne'] == 'bygg' and r['felt'] == 'vind' and r.get('grunn', '').startswith('regel 04'))]
for r in ret:
    if r['emne'] == 'bygg' and r['op'] == 'sett': b[r['i']][r['felt']] = r['verdi']
flyttet = fjernet = 0; nye = []
for i, x in gamleby(b):
    if x.get('skjul') or not x.get('vind'): continue
    P = np.array(x['p'], float); n = len(P); V = [list(v) for v in x['vind']]; endret = False
    def kant(q):
        best = None
        for k in range(n):
            a, c = P[k], P[(k + 1) % n]; u = c - a; L = np.linalg.norm(u); u = u / L
            t = float((q - a) @ u); d = abs(float((q - a)[0] * u[1] - (q - a)[1] * u[0]))
            if 0 <= t <= L and (best is None or d < best[0]): best = (d, t, L, k, a, u)
        return best
    behold = []
    for v in V:
        q = np.array(v[:2]); w = v[7]; kb = kant(q)
        if not kb or kb[0] >= 1.0: behold.append(v); continue
        d, t, L, k, a, u = kb; krav = w / 2 + 0.3; mål = krav + 0.05   # litt margin, så avrunding til cm ikke havner under kravet
        if min(t, L - t) >= krav: behold.append(v); continue
        if L < 2 * mål: fjernet += 1; endret = True; continue
        t2 = min(max(t, mål), L - mål); dq = (t2 - t) * u
        v2 = list(v); v2[0] = round(v[0] + dq[0], 2); v2[1] = round(v[1] + dq[1], 2)
        # kollisjon med et annet vindu i samme høyde på samme vegg
        kolli = any(abs(o[2] - v2[2]) < 0.5 and np.hypot(o[0] - v2[0], o[1] - v2[1]) < (o[7] + w) / 2 + 0.2 for o in behold + [z for z in V if z is not v])
        if kolli: fjernet += 1; endret = True; continue
        behold.append(v2); flyttet += 1; endret = True
    if endret:
        nye.append({"emne": "bygg", "i": i, "op": "sett", "felt": "vind", "verdi": behold, "hvem": "Claude", "dato": "2026-10-24", "grunn": "regel 04: vinduer flyttet inn fra hjørnet (halv bredde + 0,3 m) eller fjernet når de ikke fikk plass"})
json.dump(ret + nye, open(os.path.join(ROT, 'data/rettelser.json'), 'w'), ensure_ascii=False, indent=0)
print(f'{len(nye)} bygg, {flyttet} vinduer flyttet, {fjernet} fjernet')
