#!/usr/bin/env python3
"""Bakken etter Kartverket (07.11, Vegar: «terreng/høyder fra vann til by»): data/bakke.json = DTM 1 m (rapport/hoyder/kilder/
dtm1_25832.tif, CC BY 4.0 © Kartverket) minus kartets bakkeplan REF (7,0 moh: veien innenfor Voldporten, samme som
verktoy/landemerker.py), samplet i et rutenett på G m over hele DTM-rammen. Byen ligger da 4,3–8,2 moh (−2,7…+1,2 i kartet),
vollene opp til +5,4 og vannet −7. Kartet (src/08) bruker dette som én bakke for alt: terreng, veier, hus, trær, vann.

Vannflaten: medianen av DTM i vannflatene (data/vann.json) + 0,15 m (vannet over elvebunnen i DTM). Inne i vannflatene trykkes
bakken 0,3 m under vannflaten.
Format: h = uint8 base64, rad for rad fra sør, verdi = (høyde + OFF) / S; utenfor rammen gjelder kantverdien.
    python3 verktoy/bakke_dtm.py [--tørt]
"""
import os, sys, json, base64, importlib.util
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
REF, G, S, OFF = 7.0, 2.0, 0.05, 7.25

def main(tørt):
    H = os.path.join(ROT, 'rapport', 'hoyder')
    spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    dtm, gt = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif'))
    tall = json.load(open(os.path.join(H, 'tall.json'))); SH = np.array(tall['forskyvning']); bx = tall['bbox']
    ex0, ny0, dx, dy = gt
    # rammen i modellen: innenfor DTM-ruta (litt inn fra kanten)
    xs, ys = hent.til_modell(np.array([bx[0], bx[2], bx[0], bx[2]]) + 2, np.array([bx[1], bx[1], bx[3], bx[3]]) + 2)
    x0, x1 = float(np.ceil(max(xs[0], xs[2]))), float(np.floor(min(xs[1], xs[3]))) - 4
    y0, y1 = float(np.ceil(max(ys[0], ys[1]))), float(np.floor(min(ys[2], ys[3]))) - 4
    nx, ny = int((x1 - x0) // G) + 1, int((y1 - y0) // G) + 1
    X, Y = np.meshgrid(x0 + np.arange(nx) * G, y0 + np.arange(ny) * G)
    U = hent.til_utm(np.c_[X.ravel(), Y.ravel()]) + SH
    fc = (U[:, 0] - ex0) / dx; fr = (ny0 - U[:, 1]) / dy
    c = np.clip(np.floor(fc).astype(int), 0, dtm.shape[1] - 2); r = np.clip(np.floor(fr).astype(int), 0, dtm.shape[0] - 2)
    tx, ty = np.clip(fc - c, 0, 1), np.clip(fr - r, 0, 1)
    v = (dtm[r, c] * (1 - tx) + dtm[r, c + 1] * tx) * (1 - ty) + (dtm[r + 1, c] * (1 - tx) + dtm[r + 1, c + 1] * tx) * ty
    h = (v - REF).reshape(ny, nx)
    # mild utjevning (3 × 3 binomial, 2 m-rutene): DTM-støyen i skråningene ga blekkstreker som riper; kaikanter og voller står
    k = np.array([1, 2, 1], float) / 4
    hp = np.pad(h, 1, mode='edge')
    h = sum(k[a] * k[b] * hp[a:a + ny, b:b + nx] for a in range(3) for b in range(3))
    # vannflaten
    import shapely
    from shapely.geometry import Polygon
    V = json.load(open(os.path.join(ROT, 'data', 'vann.json')))
    vp = [Polygon(w['p'], [hh for hh in (w.get('h') or []) if len(hh) > 2]) for w in V if len(w.get('p', [])) > 2 and (
        w['t'].get('natural') == 'water' or w['t'].get('water') or w['t'].get('waterway') in ('riverbank', 'dock', 'canal'))]
    vann = shapely.union_all([p.buffer(0) for p in vp]).buffer(-6)        # 6 m inn fra strandkanten: bunnen, ikke bredden
    iv = shapely.contains_xy(vann, X.ravel(), Y.ravel())
    w = float(np.median(h.ravel()[iv])) + 0.15
    # i vannflatene ligger DTM-overflaten opptil en meter over vannet (støy, bredden): bakken trykkes 0,3 m under vannflaten der,
    # så vannet aldri dekkes av bakken; strandkanten går da ned til vannet ved vannflatens kant
    vann0 = shapely.union_all([p.buffer(0) for p in vp])
    i0 = shapely.contains_xy(vann0, X.ravel(), Y.ravel()).reshape(h.shape)
    h = np.where(i0, np.minimum(h, w - 0.3), h)
    q = np.clip(np.round((h + OFF) / S), 0, 255).astype(np.uint8)
    print(f'bakke {nx} × {ny} punkter à {G} m, x {x0:.0f}…{x1:.0f} y {y0:.0f}…{y1:.0f}; høyde {h.min():.2f}…{h.max():.2f} m '
          f'(moh {h.min() + REF:.1f}…{h.max() + REF:.1f}); vannflaten {w:.2f} m ({w + REF:.2f} moh, {int(iv.sum())} punkter i vannet); '
          f'kappet {int((q == 0).sum())} under, {int((q == 255).sum())} over')
    ut = dict(x0=x0, y0=y0, g=G, nx=nx, ny=ny, s=S, off=OFF, ref=REF, vann=round(w, 2),
              h=base64.b64encode(q.tobytes()).decode(),
              kilde=f'Kartverket DTM 1 m (CC BY 4.0) − {REF} moh (kartets bakkeplan), verktoy/bakke_dtm.py')
    if not tørt:
        with open(os.path.join(ROT, 'data', 'bakke.json'), 'w', encoding='utf8') as f: json.dump(ut, f, separators=(',', ':'))

if __name__ == '__main__':
    main('--tørt' in sys.argv)
