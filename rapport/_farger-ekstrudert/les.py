"""Husfarger lest rett av 2019-trykket med geometri, ikke kobling: fotavtrykket projiseres (affin2 + registrering 2015→2019),
tegneren la plantegningen som TAKFLATE og tegnet veggene nedover (sett på bygg 194/377/107: gesimsen ligger på
fotavtrykket, grunnmuren h·k under, k = 2,5 px per meter i 2019-bildet; farger-ekstrudert-debug.png).
Vegg = dominerende farge i båndet 0,25–0,75·h UNDER forkantene (kanter som vender mot betrakteren), tak = dominerende farge i
fotavtrykket løftet 2 m (takflaten over gesimsen), trukket 2 px inn. Blekk (mørkt), hvitt tekstfelt og grønt (trær) telles ikke."""
import json, numpy as np, sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_farger2019'))
import felles2019 as F
from PIL import Image, ImageDraw
K = 2.5
M = np.load(os.path.join(F.ROT, 'pdf/affin2.npy'))
b = F.last_bygg(); IM = F.last_2019(); H, W = IM.shape[:2]
def proj(p): return F.px2019(np.c_[np.asarray(p, float), np.ones(len(p))] @ M)
def maske(poly):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([tuple(q) for q in poly], fill=255); return np.asarray(m) > 0
def dominant(px):
    """dominerende farge blant piksler som ikke er blekk, grønt eller nesten-hvitt; kvantisert til 8"""
    if len(px) < 15: return None, 0
    p = px.astype(int)
    v = p.max(axis=1); s = (p.max(axis=1) - p.min(axis=1))
    g = (p[:, 1] > p[:, 0] + 12) & (p[:, 1] > p[:, 2] + 12)           # grønt (trær, plen)
    ok = (v > 90) & ~g & ~((p[:, 1] > p[:, 2] + 25) & (p[:, 1] > p[:, 0]))  # blekk/vinduer vekk
    p = p[ok]
    if len(p) < 15: return None, 0
    q = (p // 8) * 8 + 4
    c = collections.Counter(map(tuple, q)); (col, n), = c.most_common(1)
    # slå sammen nabobokser (±8) for en roligere verdi
    naer = [np.array(k) for k, m in c.items() if np.abs(np.array(k) - col).max() <= 16]
    vekt = [c[tuple(k)] for k in naer]
    col = tuple(int(round(v)) for v in np.average(naer, axis=0, weights=vekt))
    return col, sum(vekt) / len(px)
ut = {}
for i, x in enumerate(b):
    if not x.get('p') or x.get('skjul'): continue
    P = proj(x['p']); h = x['h']
    if P[:, 0].min() < 5 or P[:, 1].min() < 5 or P[:, 0].max() > W - 5 or P[:, 1].max() > H - 5: ut[i] = {'merknad': 'utenfor arket'}; continue
    # forkanter: kanter der utover-normalen peker nedover i bildet (mot betrakteren). Fotavtrykket ligger på MØNEHØYDE i tegningen:
    # takflaten henger 0–3 m under forkanten, veggen under der igjen (bygg 194, 107, 377 i farger-ekstrudert-debug.png).
    n = len(P); cx, cy = P.mean(axis=0); vegg_px = []; tak_px = []
    R = 3.0
    for k in range(n):
        a, c = P[k], P[(k + 1) % n]; e = c - a; L = np.hypot(*e)
        if L < 4: continue
        nrm = np.array([e[1], -e[0]]) / L
        if np.dot(nrm, [a[0] + e[0] / 2 - cx, a[1] + e[1] / 2 - cy]) < 0: nrm = -nrm   # utover
        if nrm[1] <= 0.15: continue   # vender ikke mot betrakteren
        def band(y0, y1): return [q - nrm * 1.5 for q in [a + (0, y0 * K), c + (0, y0 * K), c + (0, y1 * K), a + (0, y1 * K)]]
        tak_px.append(IM[maske(band(0.8, 2.4))])
        vegg_px.append(IM[maske(band(R + 0.25 * h, R + 0.75 * h))])
    vegg = dominant(np.concatenate(vegg_px)) if vegg_px else (None, 0)
    tak = dominant(np.concatenate(tak_px)) if tak_px else (None, 0)
    ut[i] = {'vegg': vegg[0], 'vegg_andel': round(vegg[1], 2), 'tak': tak[0], 'tak_andel': round(tak[1], 2)}
json.dump(ut, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'farger-ekstrudert.json'), 'w'), ensure_ascii=False)
for i in (194, 377, 353, 107, 3): print(i, ut.get(i), 'i dag', b[i].get('vegg'), b[i].get('tak'))
