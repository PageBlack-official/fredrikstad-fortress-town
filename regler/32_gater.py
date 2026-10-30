"""Regel: veibåndene i Gamlebyen (data/landskap.json «veier», tegnes i src/08) har bredden og kanten kildene viser.
Hver vei som verktoy/bakke.py gater kunne måle (kommunekartets gateareal for kjørevei, ortofotoets belagte mark mot gress for
gangvei), måles på nytt: bredden i kartet skal være innen 1,0 m av målingen og midten innen 1,0 m av midten av arealet. Veier med færre enn 5 målinger (hver 2. m) regnes som ikke målbare.
Krav: >= 95 % av de målte veiene. Veier som ikke kan måles (åpen plass, under trær, utenfor kildene), telles og listes."""
import os, sys, json, numpy as np
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import bakke as B, datalag
if not os.path.exists(B.KK.PDF):
    rapport('32_gater', False, ['kommunekartet mangler lokalt']); raise SystemExit
from shapely.geometry import LineString
d = datalag.alle(); dom = B.gate_omraade(); R = B.ramme(dom); M = B.MPP
kl, f, _ = B.bakkekart(d, R, M, utenfor=True)
kkl = f['kk'].copy(); kkl[~f['kk_inn']] = 255
ok_kk = np.zeros(256, bool); ok_kk[[B.K['belagt'], B.K['ukjent']]] = True
ok_or = np.zeros(256, bool); ok_or[list(B.BELAGT)] = True
n = god = umaalt = 0; avvik = []
for v in d['landskap']['veier']:
    if not LineString([q[:2] for q in v['p']]).intersects(dom.buffer(5)): continue
    if v['k'] == 'kjore':
        r = B.maal_vei(v, kkl, ok_kk, R, M, luke=1.2) or B.maal_vei(v, kl, ok_or, R, M, luke=0.75)
    else:
        r = B.maal_vei(v, kl, ok_or, R, M, maks=8, luke=0.5, maks_b=6.0)
    if r is None or r[2] < 5: umaalt += 1; continue   # under 5 målinger: for usikkert (verktøyet endrer ikke slike veier heller)
    n += 1; b, fo, k = r
    if abs(b - v['w']) <= 1.0 and abs(fo) <= 1.0: god += 1
    else: avvik.append(f"- {v['k']} ved ({v['p'][0][0]:.0f}, {v['p'][0][1]:.0f}): kartet {v['w']} m, målt {b:.1f} m, midten {fo:+.1f} m ({k} målinger)")
a = god / max(1, n)
rapport('32_gater', a >= 0.95, [f"{god} av {n} målte veier (Gamlebyen og kommunekartets dekning utenfor vollene) har riktig bredde og kant ({a:.1%}, krav 95 %); {umaalt} kan ikke måles (åpen plass, trær, utenfor kildene)", ''] + (['Avvik:'] + avvik if avvik else []))
