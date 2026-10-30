"""Regel: trærne i og rundt Gamlebyen (rammen rundt vollene, der DOM-en dekker) står der Kartverkets DOM−DTM har vegetasjon (over 1,5 m, ikke hus).
  - regnskapet går opp: 2343 trær fra 23.10 − tatt ut + nye fra DOM-toppene = trærne i kartet (kilder/bakke-maalt.json «traer_fjernet», «traer_nye»)
  - >= 95 % av trærne står på vegetasjon (innen 1 m)
  - ingen tre står i vannet (data/vann.json) eller inne i et hus; et tre som står under en krone i DOM−DTM (over 2,5 m) der kartet har vann,
    listes (feilen er da vannflaten)
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
nd = np.nan_to_num(B.ndsm(R, M), nan=0.0)
topp_naer = lambda t: nd[int((R[3] - t[1]) / M), int((t[0] - R[0]) / M)] >= 2.5   # krone over 2,5 m i DOM−DTM der treet står
vt = []
n = paa = iv = ih = 0; langt = []
for t in T:
    r, c = int((R[3] - t[1]) / M), int((t[0] - R[0]) / M)
    if not (0 <= r < H and 0 <= c < W) or nan[r, c]: continue
    n += 1
    if dist[r, c] <= 1.0: paa += 1
    else: langt.append((dist[r, c], t))
    if vann[r, c] > 0:
        if topp_naer(t): vt.append(t)   # et ekte tre (topp i DOM−DTM) der kartet har vann: vannflaten, ikke treet
        else: iv += 1
    ih += int(hus[r, c] > 0)
a = paa / max(1, n)
fjernet = len(B.maalt().get('traer_fjernet', [])); nye = len(B.maalt().get('traer_nye', []))
ok = len(T) + fjernet - nye == 2343 and a >= 0.95 and iv == 0 and ih == 0
lin = [f"{paa} av {n} trær i rammen rundt Gamlebyen (DOM-dekningen) står på vegetasjon i DOM−DTM ({a:.1%}, krav 95 %); {iv} i vann, {ih} i hus; {len(T)} trær i alt = 2343 fra 23.10 − {fjernet} tatt ut + {nye} nye fra DOM-toppene, alle med grunn (regnskapet skal gå opp)", '',
       f"{len(langt)} trær står mer enn 1 m fra vegetasjon (største avstand først, de 30 første):"]
lin += [f"- ({t[0]:.1f}, {t[1]:.1f}) {dv:.1f} m" for dv, t in sorted(langt, key=lambda q: -q[0])[:30]]
if vt: lin += ['', f"{len(vt)} ekte trær (krone i DOM−DTM) står der data/vann.json har vann (vannflaten bør sjekkes, regel 16):"] + [f"- ({t[0]:.1f}, {t[1]:.1f})" for t in vt]
rapport('34_traer', ok, lin)
