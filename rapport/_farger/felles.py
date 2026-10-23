"""Felles: trykkets vektorflater som shapely-polygoner + modell→trykk-projeksjon."""
import json, pickle, os, math
import numpy as np
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
from PIL import Image

ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad'
PX = 300 / 72.0  # pt -> 300 dpi-piksler
Image.MAX_IMAGE_PIXELS = None


def last_flater(min_areal_px=30.0):
    dr = pickle.load(open(os.path.join(ROT, 'pdf/drawings-side1.pkl'), 'rb'))
    polys, fills, seq = [], [], []
    for d in dr:
        pts = []
        for it in d['items']:
            if it[0] == 'l':
                pts += [it[1], it[2]]
            elif it[0] == 'c':
                # kubisk bezier: start, midt (de Casteljau t=0.5), slutt
                p0, p1, p2, p3 = (np.array(q) for q in it[1:5])
                m = 0.125 * p0 + 0.375 * p1 + 0.375 * p2 + 0.125 * p3
                pts += [tuple(p0), tuple(m), tuple(p3)]
            elif it[0] == 're':
                r = it[1]
                pts += [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
            elif it[0] == 'qu':
                q = it[1]
                pts += [tuple(q[i]) for i in range(4)] if hasattr(q, '__len__') else []
        if len(pts) < 3:
            continue
        arr = np.array(pts, float) * PX
        try:
            pg = Polygon(arr)
            if not pg.is_valid:
                pg = pg.buffer(0)
            if pg.is_empty or pg.area < min_areal_px:
                continue
        except Exception:
            continue
        polys.append(pg)
        fills.append(tuple(int(round(v * 255)) for v in d['fill']))
        seq.append(d['seqno'])
    return polys, fills, seq


class Trykk:
    def __init__(self):
        self.polys, self.fills, self.seq = last_flater()
        self.tree = STRtree(self.polys)
        self.im = np.asarray(Image.open(os.path.join(ROT, 'pdf/side300-1.png')).convert('RGB'))
        self.M = np.load(os.path.join(ROT, 'pdf/affin2.npy'))

    def px(self, xy):
        """modell (x,y) -> trykk-px (300 dpi)."""
        xy = np.asarray(xy, float)
        if xy.ndim == 1:
            return np.array([xy[0], xy[1], 1.0]) @ self.M
        return np.c_[xy, np.ones(len(xy))] @ self.M

    def flate(self, p, hopp_morke=True, hopp_smaa=400.0):
        """Øverste flate i punktet p (px). Hopper over små/mørke flater (vinduer, streker)."""
        pt = Point(p)
        idx = self.tree.query(pt)
        kand = []
        for i in idx:
            if self.polys[i].contains(pt):
                kand.append(i)
        kand.sort(key=lambda i: -self.seq[i])
        for i in kand:
            f = self.fills[i]
            if hopp_morke and max(f) < 110 and self.polys[i].area < 4000:
                continue
            if self.polys[i].area < hopp_smaa:
                continue
            return i
        return None

    def raster(self, p, r=2):
        x, y = int(round(p[0])), int(round(p[1]))
        h, w, _ = self.im.shape
        if not (r <= x < w - r and r <= y < h - r):
            return None
        blk = self.im[y - r:y + r + 1, x - r:x + r + 1].reshape(-1, 3)
        return tuple(int(v) for v in np.median(blk, axis=0))


def last_bygg():
    return json.load(open(os.path.join(ROT, 'soc/data/bygg.json')))


def naer(a, b, tol=12):
    return a is not None and b is not None and all(abs(int(x) - int(y)) <= tol for x, y in zip(a, b))


def lag_korreksjon(T, b):
    """Lokal px-korreksjon fra parene (tegnforklaringssirkel, hus med nr), som i kvartal/kobling.py."""
    circ = np.load(os.path.join(ROT, 'pdf/sirkler300.npy')).astype(float)
    pairs = []
    for x in b:
        if x.get('nr'):
            c = np.mean(x['p'], axis=0); p = T.px(c)
            dd = np.hypot(circ[:, 0] - p[0], circ[:, 1] - p[1]); i = dd.argmin()
            if dd[i] < 110:
                pairs.append((p, circ[i] - p))  # affin-px -> offset
    P = np.array([p for p, _ in pairs]); O = np.array([o for _, o in pairs])

    def korr(px):
        px = np.asarray(px, float)
        d = np.hypot(P[:, 0] - px[0], P[:, 1] - px[1])
        w = 1.0 / (d + 60.0) ** 2
        return px + (w[:, None] * O).sum(axis=0) / w.sum()
    return korr, pairs


def rutenett(pg, steg=8.0, inn=4.0):
    """Punkter i et rutenett inne i polygonet (krympet med `inn` px)."""
    g = pg.buffer(-inn)
    if g.is_empty:
        g = pg
    minx, miny, maxx, maxy = g.bounds
    pts = []
    y = miny
    while y <= maxy:
        x = minx
        while x <= maxx:
            if g.contains(Point(x, y)):
                pts.append((x, y))
            x += steg
        y += steg
    if not pts:
        rp = g.representative_point(); pts = [(rp.x, rp.y)]
    return pts
