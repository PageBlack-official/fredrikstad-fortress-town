"""Regel: gjerdene, murene og hekkene i Gamlebyen (data/gjerder.json) ses i ortofoto 2024, og det fotoet viser, finnes i kartet.
  - presisjon: hvert stykke i kartet ses i fotoet der det står (mørk smal stripe for gjerde/mur, grønn stripe for hekk, linja
    forskjøvet høyst 0,5 m): krav >= 95 % av lengden
  - dekning: av kandidatlinjene (eiendomsgrensene i kommunekartet, gårdsrommenes kanter) der fotoet viser gjerde, mur eller hekk,
    har kartet et stykke innen 1 m på >= 95 % av lengden
Bevis: kontrollarkene rapport/bakke/kvartal-NN.png (midten: kartets gjerder rødt, murer oransje, hekker grønt over fotoet)."""
import os, sys, math, numpy as np
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import bakke as B, datalag
from shapely.geometry import LineString
from shapely.ops import unary_union
d = datalag.alle(); dom = B.domene(); R = B.ramme(dom); M = B.MPP
f = B.fasit(R, M, d); L = f['trekk']['L']; gr = B.F.gront_maske(f['orto']).astype(np.float32); nd = f['ndsm']
G = [g for g in d.get('gjerder', []) if isinstance(g, dict) and not g.get('skjul')]
tot = sett = 0.0; ikke = []
for g in G:
    l = math.dist(*g['p'][:2]); tot += l
    r = B.vurder_linje(g['p'][0], g['p'][-1], L, gr, nd, R, M, sok=0.5, sett=f['sett'])
    if r and (r['typ'] == g['typ'] or {r['typ'], g['typ']} <= {'gjerde', 'mur'}): sett += l
    else: ikke.append(f"- {g['id']} {g['typ']} ({g['p'][0][0]:.0f}, {g['p'][0][1]:.0f}) {l:.1f} m")
pres = sett / max(tot, 1e-9)
kart = unary_union([LineString(g['p']).buffer(1.0) for g in G]) if G else None
ktot = kdek = 0.0
for kilde, a, b in B._kandidater(d, R, M, f, dom):
    r = B.vurder_linje(a, b, L, gr, nd, R, M, sett=f['sett'])
    if not r: continue
    l = LineString([a, b]); ktot += l.length
    if kart is not None: kdek += l.intersection(kart).length
dek = kdek / max(ktot, 1e-9)
typer = {t: (sum(1 for g in G if g['typ'] == t), sum(math.dist(*g['p'][:2]) for g in G if g['typ'] == t)) for t in ('gjerde', 'mur', 'hekk')}
lin = [f"presisjon {pres:.1%} av {tot:.0f} m (krav 95 %), dekning {dek:.1%} av {ktot:.0f} m sett langs kandidatlinjene (krav 95 %)",
       'i kartet: ' + ', '.join(f"{t} {n} stk / {l:.0f} m" for t, (n, l) in typer.items())]
if ikke: lin += ['', 'Stykker som ikke ses i fotoet der de står:'] + ikke[:40]
rapport('33_gjerder', pres >= 0.95 and dek >= 0.95, lin)
