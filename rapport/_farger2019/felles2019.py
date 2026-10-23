"""Felles for fargeregisteret fra 2019-brosjyren.

Koordinatrom:
  tegning-pt (kvartal/vek/<Navn>.json)  --s,tx,ty-->  trykk-pt (2015)  --×300/72-->  trykk-px 300 dpi
  trykk-px  --×0.5 (ORB-registrering, residual 0.1 px)-->  2019-px (kilder2019/brosjyre2019-3.jpg, 2480×1754)
  modell (m) --affin2 + lokal korreksjon--> trykk-px
"""
import json, os, pickle, math
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree

ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad'
PX = 300 / 72.0
Image.MAX_IMAGE_PIXELS = None

# 2019-px = A @ [x2015, y2015, 1] (fra ORB/RANSAC, se registrer.py)
REG = np.load(os.path.join(ROT, 'soc/rapport/_farger2019/reg2015til2019.npy')) if os.path.exists(
    os.path.join(ROT, 'soc/rapport/_farger2019/reg2015til2019.npy')) else np.array([[0.5, 0, 0], [0, 0.5, 0]])


def px2019(p2015):
    p = np.asarray(p2015, float)
    if p.ndim == 1:
        return REG @ np.array([p[0], p[1], 1.0])
    return np.c_[p, np.ones(len(p))] @ REG.T


def last_bygg():
    return json.load(open(os.path.join(ROT, 'soc/data/bygg.json')))


def last_2019():
    return np.asarray(Image.open(os.path.join(ROT, 'kilder2019/brosjyre2019-3.jpg')).convert('RGB'))


class Modell2Trykk:
    """modell (m) -> trykk-px (300 dpi) med affin2 og lokal korreksjon fra sirkel↔hus-parene."""
    def __init__(self, b):
        self.M = np.load(os.path.join(ROT, 'pdf/affin2.npy'))
        circ = np.load(os.path.join(ROT, 'pdf/sirkler300.npy')).astype(float)
        pairs = []
        for x in b:
            if x.get('nr') and x.get('p'):
                c = np.mean(x['p'], axis=0); p = self.affin(c)
                dd = np.hypot(circ[:, 0] - p[0], circ[:, 1] - p[1]); i = dd.argmin()
                if dd[i] < 110:
                    pairs.append((p, circ[i] - p))
        self.P = np.array([p for p, _ in pairs]); self.O = np.array([o for _, o in pairs])

    def affin(self, xy):
        xy = np.asarray(xy, float)
        if xy.ndim == 1:
            return np.array([xy[0], xy[1], 1.0]) @ self.M
        return np.c_[xy, np.ones(len(xy))] @ self.M

    def korr(self, px):
        px = np.asarray(px, float)
        d = np.hypot(self.P[:, 0] - px[0], self.P[:, 1] - px[1])
        w = 1.0 / (d + 60.0) ** 2
        return px + (w[:, None] * self.O).sum(axis=0) / w.sum()

    def px(self, xy):
        a = self.affin(xy)
        if a.ndim == 1:
            return self.korr(a)
        return np.array([self.korr(q) for q in a])


def plassering():
    return json.load(open(os.path.join(ROT, 'kvartal/vek/plassering.json')))


def kvartal_poly_2019(navn, pts):
    """tegning-pt -> 2019-px."""
    pl = plassering()[navn]
    s, tx, ty = pl['s'], pl['tx'], pl['ty']
    p = np.asarray(pts, float)
    p2015 = (p * s + (tx, ty)) * PX
    return px2019(p2015)


def median_i_polygon(im, poly_px, inn=1.5, maks=4000):
    """Medianfarge (RGB) av pikslene i polygonet (krympet `inn` px). Returnerer (farge, antall) eller (None, 0)."""
    pg = Polygon(poly_px)
    if not pg.is_valid:
        pg = pg.buffer(0)
    if pg.is_empty:
        return None, 0
    g = pg.buffer(-inn)
    if g.is_empty:
        g = pg
    minx, miny, maxx, maxy = g.bounds
    H, W = im.shape[:2]
    x0, x1 = max(0, int(minx)), min(W - 1, int(math.ceil(maxx)))
    y0, y1 = max(0, int(miny)), min(H - 1, int(math.ceil(maxy)))
    if x1 <= x0 or y1 <= y0:
        return None, 0
    from PIL import ImageDraw
    m = Image.new('L', (x1 - x0 + 1, y1 - y0 + 1), 0)
    dr = ImageDraw.Draw(m)
    geoms = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for gg in geoms:
        dr.polygon([(x - x0, y - y0) for x, y in gg.exterior.coords], fill=255)
        for ring in gg.interiors:
            dr.polygon([(x - x0, y - y0) for x, y in ring.coords], fill=0)
    mask = np.asarray(m) > 0
    pix = im[y0:y1 + 1, x0:x1 + 1][mask]
    if len(pix) == 0:
        return None, 0
    return pix, len(pix)


def dominant(pix, hopp_morke=True):
    """Dominerende farge i et pikselsett: grov kvantisering (8 trinn), største klynge, median innenfor.
    Mørke piksler (strek, vinduer) og hvitt (tekst/symbol) hoppes over hvis det finnes annet."""
    pix = np.asarray(pix, int)
    if len(pix) == 0:
        return None, 0.0
    lys = pix.max(axis=1)
    ok = np.ones(len(pix), bool)
    if hopp_morke:
        ok &= lys >= 90
    r, g, bb = pix[:, 0], pix[:, 1], pix[:, 2]
    ok &= ~((g > r + 10) & (g > bb + 4))      # grønt: trær og plen tegnet over huset
    ok &= ~(bb > r + 30)                       # vann
    if ok.sum() < 0.1 * len(pix):
        ok = np.ones(len(pix), bool)
    p = pix[ok]
    q = (p // 12)
    keys = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
    u, cnt = np.unique(keys, return_counts=True)
    k = u[cnt.argmax()]
    # ta med naboceller (±1 trinn) for robust median
    sel = (np.abs(q[:, 0] - k // 10000) <= 1) & (np.abs(q[:, 1] - (k // 100) % 100) <= 1) & (np.abs(q[:, 2] - k % 100) <= 1)
    col = np.median(p[sel], axis=0)
    return tuple(int(round(v)) for v in col), float(sel.sum() / len(pix))


def cmyk2rgb(c):
    """CMYK (0..1) -> RGB, naiv (1-c)(1-k). Brukes bare som grov sammenligning."""
    if len(c) == 3:
        return tuple(int(round(255 * v)) for v in c)
    if len(c) == 4:
        k = 1 - c[3]
        return tuple(int(round(255 * (1 - min(1, v)) * k)) for v in c[:3])
    return (128, 128, 128)


def naer(a, b, tol=15):
    return a is not None and b is not None and all(abs(int(x) - int(y)) <= tol for x, y in zip(a, b))
