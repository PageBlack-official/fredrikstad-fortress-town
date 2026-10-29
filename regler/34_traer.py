"""Regel: trærne i og rundt Gamlebyen (rammen rundt vollene, der DOM-en dekker) står der Kartverkets DOM−DTM har vegetasjon (over 1,5 m, ikke hus).
  - antallet er 2343 (Vegar: trærne er talt opp), medregnet trærne tatt ut med grunn (kilder/bakke-maalt.json «traer_fjernet»)
  - >= 95 % av trærne står på vegetasjon (innen 1 m)
  - ingen tre står i vannet (data/vann.json) eller inne i et hus
Bevis: rapport/bakke/traer.json (koblingen per tre) og kontrollarkene rapport/bakke/kvartal-NN.png."""
import os, sys, cv2, numpy as np
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import bakke as B, datalag
from shapely.geometry import Point
from shapely.prepared import prep
d = datalag.alle(); dom = B.domene(); R = B.ramme(dom); M = B.MPP
T = d['traer']; veg = B.vegetasjon(R, M, d)
dist = cv2.distanceTransform(1 - veg, cv2.DIST_L2, 5) * M
vann = B.maske([w['p'] for w in d['vann'] if w.get('p')], R, M); hus = B.maske(B.hus_polygoner(d), R, M)
pd = prep(dom); H, W = veg.shape; nan = np.isnan(B.ndsm(R, M))
n = paa = iv = ih = 0; langt = []
for t in T:
    r, c = int((R[3] - t[1]) / M), int((t[0] - R[0]) / M)
    if not (0 <= r < H and 0 <= c < W) or nan[r, c]: continue
    n += 1
    if dist[r, c] <= 1.0: paa += 1
    else: langt.append((dist[r, c], t))
    iv += int(vann[r, c] > 0); ih += int(hus[r, c] > 0)
a = paa / max(1, n)
fjernet = len(B.maalt().get('traer_fjernet', []))
ok = len(T) + fjernet == 2343 and a >= 0.95 and iv == 0 and ih == 0
lin = [f"{paa} av {n} trær i rammen rundt Gamlebyen (DOM-dekningen) står på vegetasjon i DOM−DTM ({a:.1%}, krav 95 %); {iv} i vann, {ih} i hus; {len(T)} trær i alt + {fjernet} tatt ut med grunn (krav 2343)", '',
       f"{len(langt)} trær står mer enn 1 m fra vegetasjon (største avstand først, de 30 første):"]
lin += [f"- ({t[0]:.1f}, {t[1]:.1f}) {dv:.1f} m" for dv, t in sorted(langt, key=lambda q: -q[0])[:30]]
rapport('34_traer', ok, lin)
