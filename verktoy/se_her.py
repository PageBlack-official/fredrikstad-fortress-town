"""Ett utsnitt for å avgjøre et bygg: ortofoto 2024 (kommunen) med modellhusene (id), kommunens omriss (FKB, gult),
Matrikkelens bygningspunkter (nummer) og Kartverkets høyde over bakken (DOM−DTM, eget panel). Bildene viser ortofoto og
ligger bare lokalt (rapport/bygg/se/, ikke i git).

    python3 verktoy/se_her.py x y [radius=25] [navn]      modellmeter (x øst, y nord)
"""
import json, os, sys, importlib.util
import numpy as np, cv2
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, flater as FL, kommunekart as KK

UT = os.path.join(ROT, 'rapport', 'bygg', 'se')


def ndh_utsnitt(x0, y0, x1, y1, mpp):
    H = os.path.join(ROT, 'rapport', 'hoyder')
    spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    dom, gt = hent.les(os.path.join(H, 'kilder', 'dom1_25832.tif')); dtm, _ = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif'))
    nd = dom - dtm; ex0, ny0, dx, dy = gt
    W, Hh = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    xs, ys = np.meshgrid(x0 + (np.arange(W) + 0.5) * mpp, y1 - (np.arange(Hh) + 0.5) * mpp)
    U = hent.til_utm(np.stack([xs, ys], -1))
    c = ((U[..., 0] - ex0) / dx).astype(int); r = ((ny0 - U[..., 1]) / dy).astype(int)
    ok = (r >= 0) & (r < nd.shape[0]) & (c >= 0) & (c < nd.shape[1])
    out = np.full((Hh, W), np.nan); out[ok] = nd[r[ok], c[ok]]
    return out


def lag(x, y, rad=25.0, navn=None, mpp=0.0625):
    x0, y0, x1, y1 = x - rad, y - rad, x + rad, y + rad
    im, px = FL.ortofoto(x0, y0, x1, y1, mpp)
    nd = ndh_utsnitt(x0, y0, x1, y1, mpp)
    hm = np.clip(np.nan_to_num(nd, nan=0) / 15.0, 0, 1)
    hb = cv2.applyColorMap((hm * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    def P(pts): return np.array([px(*q) for q in pts], np.int32)
    d = datalag.alle(); K = KK.omriss()
    for panel in (im, hb):
        for k in K:
            if k.distance(__import__('shapely').geometry.Point(x, y)) > rad * 1.5: continue
            cv2.polylines(panel, [P(np.array(k.exterior.coords))], True, (0, 230, 255), 1)
        for b in d['bygg']:
            if b.get('skjul'): continue
            c = P(b['p'])
            if (c[:, 0].max() < 0) or (c[:, 1].max() < 0) or c[:, 0].min() > panel.shape[1] or c[:, 1].min() > panel.shape[0]: continue
            cv2.polylines(panel, [c], True, (60, 60, 255), 2)
            cc = c.mean(0).astype(int); cv2.putText(panel, b['id'].replace('bnr-', ''), tuple(cc), 0, 0.45, (40, 40, 255), 1)
        for p in json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json')))['punkter']:
            mx, my = datalag.til_modell(*p['lonlat'])
            if x0 <= mx <= x1 and y0 <= my <= y1:
                q = tuple(int(v) for v in px(mx, my)); cv2.circle(panel, q, 4, (255, 0, 255), -1)
                cv2.putText(panel, str(p['bygningsnummer']), (q[0] + 5, q[1] - 5), 0, 0.42, (255, 0, 255), 1)
    # høydetall i rutenett (hver 4. m)
    for gx in np.arange(x0 + 2, x1, 4.0):
        for gy in np.arange(y0 + 2, y1, 4.0):
            c, r = px(gx, gy); v = nd[int(r), int(c)] if 0 <= int(r) < nd.shape[0] and 0 <= int(c) < nd.shape[1] else np.nan
            if not np.isnan(v): cv2.putText(hb, f"{v:.0f}", (int(c) - 6, int(r) + 4), 0, 0.33, (255, 255, 255), 1)
    os.makedirs(UT, exist_ok=True)
    f = os.path.join(UT, f"{navn or f'{x:.0f}_{y:.0f}'}.jpg")
    cv2.imwrite(f, np.hstack([im, hb]), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return f


if __name__ == '__main__':
    a = sys.argv[1:]
    print(lag(float(a[0]), float(a[1]), float(a[2]) if len(a) > 2 else 25.0, a[3] if len(a) > 3 else None))
