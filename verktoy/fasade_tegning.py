"""Fasadene lest som vektor fra Vegars kvartaltegninger (strektegninger/*.ai, 2015), på dagens omriss (kommunekartet).

Tegningene er tegnet isometrisk fra sør-sørøst (asimut ≈ 20 i kartets kamera, se kilder/kvartal-kobling.json). Hver farget
flate i tegningen er en egen vektorsti: veggene har vinduene og dørene som hull, takflatene har takvinduene som hull.
Verktøyet:
  1. leser flatene (sti med fyll, ytre ring + hull) og skiller vegger fra tak (loddrette sidekanter, hull, plassering under taket)
  2. legger modellens synlige vegger (dagens omriss og høyde) inn i tegningen med kameraet målt per tegning
  3. kobler hver tegnet vegg til en modellvegg (retning, plass, lengde)
  4. leser elementene på veggen: vinduer (glass med sprosser), dører (mørke, står på bakken), porter (buet topp),
     i akser (andel av veggens lengde) og rader (etasje), og legger dem på modellveggen
Antall og rekkefølge går foran centimeter (Vegar 29.10): aksene står der tegningen har dem, i andel av veggen.

    python3 verktoy/fasade_tegning.py flater <tegning>     flatene og hullene (rapport/bygg/_arbeid/<tegning>-flater.png)
"""
import json, math, os, sys, warnings
warnings.filterwarnings('ignore')
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import fitz
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

AI = os.path.join(ROT, 'kilder', 'kvartal-ai')
ARB = os.path.join(ROT, 'rapport', 'bygg', '_arbeid')


def _bez(P, n=8):
    P = [np.array(q) for q in P]
    return [tuple((1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]) for t in np.linspace(0, 1, n)]


def ringer(sti):
    """Delstiene i en vektorsti som punktlister (kurver flatet ut)."""
    R, cur = [], []
    for it in sti['items']:
        if it[0] == 'l':
            seg = [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            seg = _bez([(q.x, q.y) for q in it[1:5]])
        elif it[0] == 're':
            r = it[1]; seg = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)]
        elif it[0] == 'qu':
            q = it[1]; seg = [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y), (q.ul.x, q.ul.y)]
        else:
            continue
        if cur and math.hypot(cur[-1][0] - seg[0][0], cur[-1][1] - seg[0][1]) > 1e-3:
            R.append(cur); cur = []
        cur += seg if not cur else seg[1:]
    if cur:
        R.append(cur)
    return [r for r in R if len(r) >= 3]


def flater(navn):
    """Alle fargede flater i tegningen: dict(i, farge, ytre (Polygon), hull [Polygon], type)."""
    d = fitz.open(os.path.join(AI, navn + '.ai')); side = d[0]
    ut = []
    for i, s in enumerate(side.get_drawings()):
        f = s.get('fill')
        if not f or s.get('type') not in ('f', 'fs'):
            continue
        f = tuple(round(v, 3) for v in f)
        R = [Polygon(r).buffer(0) for r in ringer(s)]
        R = [g for g in R if g.area > 0.05]
        if not R:
            continue
        R.sort(key=lambda g: -g.area)
        ytre = R[0]
        if ytre.geom_type != 'Polygon':
            ytre = max(ytre.geoms, key=lambda g: g.area)
        hull = [g for g in R[1:] if ytre.buffer(0.5).contains(g.representative_point())]
        ut.append(dict(i=i, farge=f, ytre=Polygon(ytre.exterior), hull=hull, andre=[g for g in R[1:] if g not in hull]))
    return ut, side.rect


def _utstrekning(P, x):
    g = P.intersection(LineString([(x, -1e5), (x, 1e5)]))
    if g.is_empty:
        return 0.0
    b = g.bounds
    return b[3] - b[1]


def er_vegg(P):
    """Vegg: loddrette sidekanter i begge ender (tegningen holder loddlinjene loddrette). Tak har skrå eller spisse ender."""
    x0, y0, x1, y1 = P.bounds
    if x1 - x0 < 2:
        return False
    hm = _utstrekning(P, (x0 + x1) / 2)
    if hm < 1.5:
        return False
    d = min(1.2, (x1 - x0) * 0.08)
    v, h = _utstrekning(P, x0 + d), _utstrekning(P, x1 - d)
    return v >= 0.55 * hm and h >= 0.55 * hm


def kobling(navn):
    k = json.load(open(os.path.join(ROT, 'kilder', 'kvartal-kobling.json')))
    return next(t for t in k['tegninger'] if t['navn'] == navn)


def kamera_start(navn):
    """Første kamera modell -> tegning (PDF-punkt): bakken fra modell_h_til_2019 (trykket) og tegning->trykk fra koblingen.
    Gir (G, k): punkt = G @ [x, y, 1] - [0, k*z]  (loddrett er loddrett i tegningen)."""
    A = np.load(os.path.join(ROT, 'kilder', 'ai', 'ai', 'modell_h_til_2019.npy'))      # [x, y, h, 1] -> trykk
    T = np.array(kobling(navn)['tegning_til_trykk'])                                   # tegning px150 -> trykk
    T3 = np.vstack([T, [0, 0, 1]]); Ti = np.linalg.inv(T3)
    Mg = np.array([[A[0, 0], A[1, 0], A[3, 0]], [A[0, 1], A[1, 1], A[3, 1]], [0, 0, 1]])
    G = (np.diag([72 / 150, 72 / 150, 1]) @ Ti @ Mg)[:2]
    s = np.linalg.svd(G[:, :2], compute_uv=False)
    k = s[0] * math.sqrt(max(0.0, 1 - (s[1] / s[0]) ** 2))       # ortografisk: loddrett skala = s cos(e)
    return G, k


def maske(navn, R=2.0):
    """Alt som er tegnet (ikke hvitt) som maske, R piksler per PDF-punkt."""
    d = fitz.open(os.path.join(AI, navn + '.ai')); pm = d[0].get_pixmap(matrix=fitz.Matrix(R, R))
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3]
    return (im.min(axis=2) < 235).astype(np.uint8), im


def blokker(bygg, buf=0.6):
    """Modellhus som står inntil hverandre, er tegnet som ett stykke: sammenhengende grupper (id-lister)."""
    import networkx as nx
    P = {x['id']: Polygon(x['p']).buffer(buf) for x in bygg}
    g = nx.Graph(); g.add_nodes_from(P)
    ids = list(P)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            if P[ids[a]].intersects(P[ids[b]]):
                g.add_edge(ids[a], ids[b])
    return [sorted(c) for c in nx.connected_components(g)]


def tak_hoyde(x):
    """Takets høyeste punkt over gesims (m), som kartet tegner det."""
    th = x.get('th') or 0.82
    if x.get('tak2'):
        return max((q[2] for f in x['tak2'] for q in f), default=0) * th
    if x.get('sk'):
        return min(max((q[2] for f in x['sk'] for q in f), default=0) * th, 7.5 * th / 0.82)
    return min(min(x['r'][2], x['r'][3]) * 0.48, 7.5) * th / 0.82


def silhuett(x, proj):
    """Husets omriss i tegningen: vegger og tak projisert (proj(x, y, z) -> punkt)."""
    P = x['p']; h = x['h']; deler = []
    g = [proj(q[0], q[1], 0) for q in P]; t = [proj(q[0], q[1], h) for q in P]
    for k in range(len(P)):
        a, b = k, (k + 1) % len(P)
        deler.append(Polygon([g[a], g[b], t[b], t[a]]).buffer(0))
    deler.append(Polygon(t).buffer(0))
    th = x.get('th') or 0.82
    for f in (x.get('tak2') or x.get('sk') or []):
        if len(f) >= 3:
            deler.append(Polygon([proj(q[0], q[1], h + q[2] * th) for q in f]).buffer(0))
    if not x.get('tak2') and not x.get('sk'):
        r = x['r']; cx, cy, w, l, a = r; a = math.radians(a)
        rise = tak_hoyde(x)
        deler.append(Polygon([proj(q[0], q[1], h) for q in P]).convex_hull.union(Point(proj(cx, cy, h + rise))).convex_hull)
    return unary_union([d for d in deler if d.is_valid and d.area > 0])


def _proj(G, k, s, kz, c0, d):
    def p(x, y, z):
        q = G @ [x, y, 1]
        return (c0[0] + s * (q[0] - c0[0]) + d[0], c0[1] + s * (q[1] - c0[1]) - k * kz * z + d[1])
    return p


def synlig(G, a, b, P):
    """Veggen a->b (fotavtrykk P, mot klokka eller ikke) vender mot tegneren: utoverpekende normal peker ned i bildet."""
    u = np.array(b) - np.array(a); n = np.array([u[1], -u[0]])
    if Polygon(P).exterior.is_ccw is False:
        n = -n
    return (G[:, :2] @ n)[1] > 1e-6


def kanter(x, proj, G):
    """Linjene tegningen har for huset: synlige vegger (bunn, gesims, hjørner), takkanter og møner."""
    P = x['p']; h = x['h']; L = []
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        if math.dist(a, b) < 0.5: continue
        topp = [proj(*a, h), proj(*b, h)]
        L.append(topp)
        if synlig(G, a, b, P):
            L += [[proj(*a, 0), proj(*b, 0)], [proj(*a, 0), proj(*a, h)], [proj(*b, 0), proj(*b, h)]]
    th = x.get('th') or 0.82
    for f in (x.get('tak2') or x.get('sk') or []):
        for q1, q2 in zip(f, f[1:] + f[:1]):
            if q1[2] > 0.05 or q2[2] > 0.05:
                L.append([proj(q1[0], q1[1], h + q1[2] * th), proj(q2[0], q2[1], h + q2[2] * th)])
    return L


def avstandsbilde(navn, R):
    """exp(-d²/2σ²) der d er avstanden til nærmeste svarte strek i tegningen (σ = 2,5 pt)."""
    import cv2
    d = fitz.open(os.path.join(AI, navn + '.ai')); pm = d[0].get_pixmap(matrix=fitz.Matrix(R, R))
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3]
    strek = (im.max(axis=2) < 90).astype(np.uint8)
    dt = cv2.distanceTransform(1 - strek, cv2.DIST_L2, 5) / R
    return np.exp(-dt ** 2 / (2 * 2.5 ** 2)).astype(np.float32), im


def _mal(L, R, pad=2):
    import cv2
    A = np.array([q for l in L for q in l]); x0, y0 = A.min(0); x1, y1 = A.max(0)
    T = np.zeros((int((y1 - y0) * R) + 2 * pad + 1, int((x1 - x0) * R) + 2 * pad + 1), np.float32)
    for a, b in L:
        cv2.line(T, (int((a[0] - x0) * R) + pad, int((a[1] - y0) * R) + pad), (int((b[0] - x0) * R) + pad, int((b[1] - y0) * R) + pad), 1, 1)
    return T, x0 - pad / R, y0 - pad / R


def tilpass(navn, B, R=1.5, vindu=40, skalaer=(0.94, 1.0, 1.06), kz_liste=(0.8, 1.0, 1.25), min_score=0.6, ids_lov=None, kamera=None):
    """Hver blokk (hus inntil hverandre) legges der tegningen har strekene sine: modellens synlige kanter (vegger, gesims,
    hjørner, tak) matches mot de svarte strekene (avstandsbilde), med forskyvning, målestokk og høydeskala. Grådig: beste
    blokk først; strekene den tar, teller ikke for de andre. Gir {blokk-nr: dict(ids, s, kz, c0, d, score)} og info."""
    import cv2
    E, im = avstandsbilde(navn, R); H, W = E.shape
    M = (im.min(axis=2) < 235).astype(np.float32)
    G, k = kamera or kamera_start(navn)
    bl = blokker(B); BY = {x['id']: x for x in B}
    ledig = E.copy()
    res = {}; igjen = list(range(len(bl)))
    lov = set(ids_lov or [])
    andre_runde = False
    while igjen:
        beste = None
        for bi in igjen:
            if andre_runde and not (set(bl[bi]) & lov): continue
            ids = bl[bi]
            c0 = np.mean([G @ [*Polygon(BY[i]['p']).centroid.coords[0], 1] for i in ids], axis=0)
            for s in skalaer:
                for kz in kz_liste:
                    pr = _proj(G, k, s, kz, c0, (0, 0))
                    L = [l for i in ids for l in kanter(BY[i], pr, G)]
                    if not L: continue
                    T, x0, y0 = _mal(L, R)
                    th_, tw = T.shape
                    vv = 2000 if andre_runde else vindu
                    ax, ay = max(0, int((x0 - vv) * R)), max(0, int((y0 - vv) * R))
                    bx, by = min(W, int((x0 + vv) * R) + tw), min(H, int((y0 + vv) * R) + th_)
                    if bx - ax < tw or by - ay < th_: continue
                    r = cv2.matchTemplate(ledig[ay:by, ax:bx], T, cv2.TM_CCORR) / T.sum()
                    sil = unary_union([silhuett(BY[i], pr) for i in ids])
                    Sm = np.zeros_like(T)
                    for g in getattr(sil, 'geoms', [sil]):
                        cv2.fillPoly(Sm, [((np.array(g.exterior.coords) - [x0, y0]) * R).astype(np.int32)], 1)
                    ring = cv2.dilate(Sm, np.ones((9, 9), np.uint8)) - Sm
                    Mr = cv2.matchTemplate(M[ay:by, ax:bx], Sm, cv2.TM_CCORR) / max(Sm.sum(), 1)
                    Rr = cv2.matchTemplate(M[ay:by, ax:bx], ring, cv2.TM_CCORR) / max(ring.sum(), 1)
                    r = r + 0.5 * Mr - 0.25 * Rr
                    _, mx, _, ml = cv2.minMaxLoc(r)
                    sc = mx
                    if beste is None or sc > beste[0]:
                        beste = (sc, bi, s, kz, c0, ((ax + ml[0]) / R - x0, (ay + ml[1]) / R - y0), T, (ax + ml[0], ay + ml[1]))
        if beste is None or beste[0] < min_score:
            if andre_runde or not lov: break
            andre_runde = True      # biter limt inn langt fra plassen sin (Kvartal3, 13, tell, Glasshytta): hele tegningen
            continue
        sc, bi, s, kz, c0, dd, T, (px, py) = beste
        ids = bl[bi]
        par = finjuster(ledig, R, G, k, [BY[i] for i in ids], c0, dict(s=s, kz=kz, d=dd, rot=0.0, sk=0.0))
        res[bi] = dict(ids=ids, c0=[float(c0[0]), float(c0[1])], **par)
        pr = proj_par(G, k, c0, par)
        T, x0, y0 = _mal([l for i in ids for l in kanter(BY[i], pr, G)], R)
        Tb = cv2.dilate((T > 0).astype(np.uint8), np.ones((5, 5), np.uint8))
        px, py = int(round(x0 * R)), int(round(y0 * R))
        ax, ay = max(0, px), max(0, py)
        reg = ledig[ay:py + T.shape[0], ax:px + T.shape[1]]
        reg[Tb[ay - py:ay - py + reg.shape[0], ax - px:ax - px + reg.shape[1]] > 0] *= 0.15
        igjen.remove(bi)
    return res, dict(G=G, k=k, R=R, bilde=im)


def proj_par(G, k, c0, par):
    """Kamera for én blokk: start-kameraet G, så målestokk s, liten dreiing rot (grader) og skjevhet sk om blokkens midte,
    høydeskala kz (tegningen overdriver høyden) og forskyvning d (PDF-punkt)."""
    s, kz, rot, sk = par['s'], par['kz'], math.radians(par.get('rot', 0)), par.get('sk', 0)
    Mx = s * np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]]) @ np.array([[1, sk], [0, 1]])
    c0 = np.array(c0); d = np.array(par['d'])
    def p(x, y, z):
        q = G @ [x, y, 1]
        r = c0 + Mx @ (q - c0) + d
        return (float(r[0]), float(r[1] - k * kz * z))
    return p


def _punkter(L, steg=0.7):
    P = []
    for a, b in L:
        n = max(2, int(math.dist(a, b) / steg))
        P += [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in np.linspace(0, 1, n)]
    return np.array(P)


def _score(E, R, P):
    from scipy.ndimage import map_coordinates
    if len(P) == 0: return 0.0
    return float(map_coordinates(E, [P[:, 1] * R, P[:, 0] * R], order=1, mode='constant', cval=0).mean())


def finjuster(E, R, G, k, X, c0, par):
    """Kontinuerlig finjustering av blokkens kamera (Powell) på snittet av avstandsbildet langs modellens kanter."""
    from scipy.optimize import minimize
    def f(v):
        q = dict(s=v[0], kz=v[1], d=(v[2], v[3]), rot=v[4], sk=v[5])
        if not (0.85 < v[0] < 1.15 and 0.6 < v[1] < 1.6 and abs(v[4]) < 5 and abs(v[5]) < 0.1 and math.hypot(v[2] - par['d'][0], v[3] - par['d'][1]) < 30): return 1.0
        pr = proj_par(G, k, c0, q)
        return -_score(E, R, _punkter([l for x in X for l in kanter(x, pr, G)]))
    v0 = [par['s'], par['kz'], par['d'][0], par['d'][1], par.get('rot', 0), par.get('sk', 0)]
    r = minimize(f, v0, method='Powell', options=dict(xtol=0.01, ftol=1e-4, maxfev=1500))
    v = r.x
    return dict(s=round(float(v[0]), 4), kz=round(float(v[1]), 3), d=[round(float(v[2]), 2), round(float(v[3]), 2)],
                rot=round(float(v[4]), 2), sk=round(float(v[5]), 4), score=round(-float(r.fun), 3), score_grov=None)


def finjuster_hus(E, M, R, G, k, x, c0, par, maks=15.0):
    """Hvert hus for seg innenfor blokkens kamera: forskyvning og høydeskala, med straff for å gå langt fra blokken
    (tegningen er frihånd, så huset kan stå noen punkt fra der blokken sier)."""
    from scipy.optimize import minimize
    import cv2
    def f(v):
        q = dict(par); q['d'] = (par['d'][0] + v[0], par['d'][1] + v[1]); q['kz'] = v[2]
        if math.hypot(v[0], v[1]) > maks or not 0.6 < v[2] < 1.8: return 1.0
        pr = proj_par(G, k, c0, q)
        P = _punkter(kanter(x, pr, G))
        sil = silhuett(x, pr)
        import shapely
        sb = sil.buffer(-1.5); x0, y0, x1, y1 = sil.bounds
        gx, gy = np.meshgrid(np.arange(x0, x1, 3.0), np.arange(y0, y1, 3.0)); gx, gy = gx.ravel(), gy.ravel()
        ok = shapely.contains_xy(sb, gx, gy) if not sb.is_empty else np.zeros(len(gx), bool)
        inn = np.c_[gx[ok], gy[ok]] if ok.any() else np.array([[0.0, 0.0]])
        mm = _score(M, R, inn)
        return -(_score(E, R, P) + 0.3 * mm) + 0.002 * (v[0] ** 2 + v[1] ** 2) / 10
    best = None
    for dx in (-6, 0, 6):
        for dy in (-4, 0, 4):
            r = minimize(f, [dx, dy, par['kz']], method='Powell', options=dict(xtol=0.05, ftol=1e-4, maxfev=400))
            if best is None or r.fun < best.fun: best = r
    v = best.x; q = dict(par); q['d'] = [round(par['d'][0] + v[0], 2), round(par['d'][1] + v[1], 2)]; q['kz'] = round(float(v[2]), 3)
    q['score_hus'] = round(-float(best.fun), 3)
    return q


# ---------------------------------------------------------------- vegger i tegningen -> modellvegger

def vegger_proj(x, pr, G):
    """Husets synlige vegger i tegningen: dict(k, a, b (modell), L, q (Polygon i tegningen), venstre (modellpunktet som står
    til venstre i tegningen))."""
    P = x['p']; h = x['h']; ut = []
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        L = math.dist(a, b)
        if L < 1.0 or not synlig(G, a, b, P):
            continue
        ga, gb, ta, tb = pr(*a, 0), pr(*b, 0), pr(*a, h), pr(*b, h)
        q = Polygon([ga, gb, tb, ta]).buffer(0)
        if q.area < 1:
            continue
        ut.append(dict(k=k, a=a, b=b, L=L, q=q, venstre=a if ga[0] <= gb[0] else b))
    return ut


def tak_proj(x, pr):
    th = x.get('th') or 0.82; h = x['h']
    deler = [Polygon([pr(q[0], q[1], h + q[2] * th) for q in f]).buffer(0) for f in (x.get('tak2') or x.get('sk') or []) if len(f) >= 3]
    if not deler:
        deler = [Polygon([pr(q[0], q[1], h) for q in x['p']]).buffer(0)]
    return unary_union(deler)


def er_tak_farge(f):
    return False


def koble_flater(F, hus, BY, G, k):
    """Hver farget flate i tegningen kobles til en modellvegg (id, k) eller et tak (id, 'tak'), etter overlapp med husets
    projiserte vegger og tak (husets eget kamera). Gir liste av dict(flate, id, vegg|None, iou)."""
    kand = []
    for i, par in hus.items():
        x = BY[i]; pr = proj_par(G, k, par['c0'], par)
        for v in vegger_proj(x, pr, G):
            kand.append((i, v['k'], v['q']))
        kand.append((i, 'tak', tak_proj(x, pr)))
    ut = []
    for f in F:
        if min(f['farge']) > 0.97 or max(f['farge']) < 0.3 or f['ytre'].area < 15:
            continue
        P = f['ytre']; best = None
        for i, kk, q in kand:
            if not q.intersects(P):
                continue
            inter = q.intersection(P).area
            sc = inter / P.area                      # andel av flaten som ligger i kandidaten
            if kk != 'tak':
                sc *= 1.0 if er_vegg(P) else 0.8
            if best is None or sc > best[3]:
                best = (i, kk, q, sc)
        if best and best[3] >= 0.35:
            ut.append(dict(flate=f, id=best[0], vegg=best[1], andel=round(best[3], 2)))
    return ut


# ---------------------------------------------------------------- elementer på en tegnet vegg

def elementer(F_vegg, side, R=8.0, flatefarger=(), andre=()):
    """Vinduer, dører og porter på en tegnet vegg (én eller flere flater, f.eks. sokkel + vegg). Rastrerer bare utsnittet:
    alt inne i flaten som ikke har flatens farge (strek, glass, dør), minus kantstreken. Gir (elementer, geometri), der hvert
    element har u (0-1 langs veggen fra venstre i tegningen), v (0-1 opp fra bunnen til gesims), bredde/høyde i andel,
    hvit (andel glass), mork (andel svart), buet (topp smalere enn midten)."""
    import cv2
    U = unary_union([f['ytre'].buffer(1.3) for f in F_vegg]).buffer(-1.3)   # flater skilt av en strek (rekkehus) blir én vegg
    if U.geom_type != 'Polygon':      # flatene henger ikke sammen (sokkel under vegg med tykk strek): hylle rundt alle
        U = unary_union([f['ytre'] for f in F_vegg]).convex_hull
    x0, y0, x1, y1 = U.bounds
    clip = fitz.Rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
    pm = side.get_pixmap(matrix=fitz.Matrix(R, R), clip=clip)
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3].astype(np.int16)
    def tilpx(c): return ((np.array(c) - [clip.x0, clip.y0]) * R).astype(np.int32)
    mf = np.zeros(im.shape[:2], np.uint8); cv2.fillPoly(mf, [tilpx(U.exterior.coords)], 1)
    inn = cv2.erode(mf, np.ones((int(R * 1.3) | 1,) * 2, np.uint8))
    farger = np.array([[c * 255 for c in f['farge']] for f in F_vegg])
    d = np.min([np.abs(im - c).sum(axis=2) for c in farger], axis=0)
    annet = ((d > 60) & (inn > 0)).astype(np.uint8)
    annet = cv2.morphologyEx(annet, cv2.MORPH_CLOSE, np.ones((int(R * 0.5) | 1,) * 2, np.uint8))
    # flatens geometri: venstre/høyre loddkant, bunn og gesims
    fx0, fx1 = x0, x1
    def bunn_topp(xx):
        g = U.intersection(LineString([(xx, -1e5), (xx, 1e5)]))
        if g.is_empty: return None
        b = g.bounds; return b[3], b[1]
    venstre = bunn_topp(fx0 + min(1.0, (fx1 - fx0) * 0.05)); hoyre = bunn_topp(fx1 - min(1.0, (fx1 - fx0) * 0.05))
    if not venstre or not hoyre:
        return [], None
    def gesims(xx):
        t = (xx - fx0) / max(fx1 - fx0, 1e-6); return venstre[1] + (hoyre[1] - venstre[1]) * t
    def bunn(xx):
        bt = bunn_topp(xx); return bt[0] if bt else venstre[0] + (hoyre[0] - venstre[0]) * (xx - fx0) / max(fx1 - fx0, 1e-6)
    ut = []
    def legg(sel, x, y, w, hh):
        """Ett element: sel er pikselmasken i ruta (x, y, w, hh) i utsnittet."""
        if hh > 4 * w and w < R * 1.2:      # loddrett skillestrek mellom rekkehus, ikke et element
            return
        px = im[y:y + hh, x:x + w][sel]
        if len(px) == 0: return
        hvit = float((px.min(axis=1) > 190).mean()); mork = float((px.max(axis=1) < 80).mean())
        cx, cy = clip.x0 + (x + w / 2) / R, clip.y0 + (y + hh / 2) / R
        bt = bunn_topp(cx)
        yb, yg = (bt if bt else (bunn(cx), gesims(cx)))       # bunn og topp av flaten rett over/under elementet
        H = max(yb - yg, 1e-6)
        u = (cx - fx0) / max(fx1 - fx0, 1e-6)
        top, bot = clip.y0 + y / R, clip.y0 + (y + hh) / R
        rad = lambda f: sel[min(hh - 1, int(hh * f))].sum()
        buet = hh > 4 and rad(0.05) < 0.5 * max(rad(0.6), 1)
        ut.append(dict(u=round(u, 4), v=round((yb - cy) / H, 3), vb=round((yb - bot) / H, 3), vt=round((yb - top) / H, 3),
                       bu=round(w / R / max(fx1 - fx0, 1e-6), 4), hv=round(hh / R / H, 3), hvit=round(hvit, 2), mork=round(mork, 2),
                       buet=bool(buet), pt=[round(cx, 2), round(cy, 2)], wpt=round(w / R, 2), hpt=round(hh / R, 2)))
    # 1) hullene i veggflatene: ett hull er ett vindu/én dør (vektor, så to vinduer som står tett, slås ikke sammen)
    hullmaske = np.zeros(im.shape[:2], np.uint8)
    # dører, porter og butikkvinduer tegnet som egne flater oppå veggen (samme farge som veggen, bare streken skiller dem)
    # telles som hull: flaten ligger helt inne i veggen og er liten (30.10)
    egne = [g['ytre'] for g in andre if all(g is not f for f in F_vegg) and g['ytre'].area < 0.25 * U.area
            and g['ytre'].intersection(U.buffer(3.5).buffer(-3.1)).area > 0.85 * g['ytre'].area]   # dør i et hakk i bunnkanten
    hull_alle = [h for f in F_vegg for h in f['hull']]
    egne = [e for e in egne if not any(h.buffer(0.3).contains(e.representative_point()) for h in hull_alle)]
    for hp in [h for f in F_vegg for h in f['hull']] + egne:
        if True:
            if hp.area < 0.15 or not U.buffer(2.5).buffer(-2.0).contains(hp.representative_point()):
                continue
            if any(hp is not e and e.contains(hp.representative_point()) and e.area > hp.area for e in egne):
                continue                                  # hull i en dørflate (glass i døra): døra teller
            m = np.zeros(im.shape[:2], np.uint8); cv2.fillPoly(m, [tilpx(hp.exterior.coords)], 1)
            ys, xs = np.nonzero(m)
            if len(xs) == 0: continue
            x, y, w, hh = xs.min(), ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
            if w * hh < (R * 0.35) ** 2: continue
            legg(m[y:y + hh, x:x + w] > 0, x, y, w, hh)
            hullmaske |= m
    # 2) det som er tegnet oppå flaten og ikke er et hull (dører og porter tegnet som egne flater, mørke felt)
    rest = (annet > 0) & (cv2.dilate(hullmaske, np.ones((int(R * 0.6) | 1,) * 2, np.uint8)) == 0)
    rest = cv2.morphologyEx(rest.astype(np.uint8), cv2.MORPH_OPEN, np.ones((int(R * 0.3) | 1,) * 2, np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(rest, 8)
    for j in range(1, n):
        x, y, w, hh, a_ = st[j]
        if a_ < (R * 0.5) ** 2:
            continue
        legg(lab[y:y + hh, x:x + w] == j, x, y, w, hh)
    geo = dict(fx0=fx0, fx1=fx1, H_venstre=venstre[0] - venstre[1], H_hoyre=hoyre[0] - hoyre[1])
    return ut, geo


# ---------------------------------------------------------------- hele tegningen

def kandidater(navn, d, utvid=25):
    """Husene tegningen kan vise: koblingen fra kvartal-QA (px2019 i tegningens omriss) og hus hvis midtpunkt med start-
    kameraet havner på noe tegnet (utvidet utvid pt). Hus langt utenfor tegningen trekker kameraet feil (krymper det)."""
    import cv2
    G, k = kamera_start(navn)
    m, _ = maske(navn, 1.0)
    m = cv2.dilate(m, np.ones((2 * utvid + 1, 2 * utvid + 1), np.uint8))
    kob = kobling(navn); lov = set(kob['bygg']) | set(kob.get('kant', []))
    B = []
    for x in d['bygg']:
        if x.get('skjul') or not x.get('gml') or x.get('kirke') or len(x['p']) < 3:
            continue
        q = G @ [*Polygon(x['p']).centroid.coords[0], 1]
        inne = 0 <= int(q[1]) < m.shape[0] and 0 <= int(q[0]) < m.shape[1] and m[int(q[1]), int(q[0])]
        if x['id'] in lov or inne:
            B.append(x)
    return B


def les(navn, d=None, logg=print):
    """Leser tegningen: kamera per blokk og hus, flatene koblet til modellvegger, elementene per vegg."""
    import datalag
    d = d or datalag.alle()
    BY = {x['id']: x for x in d['bygg']}
    B = kandidater(navn, d)
    kob = kobling(navn)
    G2, k2, glob = tilpass_globalt(navn, B)
    logg(f"{navn}: globalt kamera s {glob['s']:.3f} kz {glob['kz']:.2f} rot {glob['rot']:.2f} skjev {glob['sk']:.3f} mål {glob['score']:.3f}")
    res, info = tilpass(navn, B, ids_lov=kob['bygg'], kamera=(G2, k2))
    G, k, R = info['G'], info['k'], info['R']
    E, im = avstandsbilde(navn, R); M = (im.min(axis=2) < 235).astype(np.float32)
    hus = {}
    for bi, r in res.items():
        for i in r['ids']:
            hus[i] = finjuster_hus(E, M, R, G, k, BY[i], r['c0'], r)
            hus[i]['c0'] = r['c0']; hus[i]['blokk'] = bi; hus[i]['score_blokk'] = r['score']
    logg(f"{navn}: {len(B)} kandidater, {len(res)} blokker lagt, {len(hus)} hus")
    F, _ = flater(navn)
    kob_f = koble_flater(F, hus, BY, G, k)
    # koblinger satt for hånd (kilder/fasade-kobling.json): flate -> "id/vegg", "id/tak" eller "ingen"
    man = (json.load(open(KOBLING_FIL, encoding='utf8')).get(navn, {}) if os.path.exists(KOBLING_FIL) else {}).get('flater', {})
    if man:
        FI = {f['i']: f for f in F}
        kob_f = [kf for kf in kob_f if str(kf['flate']['i']) not in man]
        for fi, mal in man.items():
            if mal == 'ingen' or int(fi) not in FI: continue
            i, kk = mal.rsplit('/', 1)
            kob_f.append(dict(flate=FI[int(fi)], id=i, vegg='tak' if kk == 'tak' else int(kk), andel=None, for_haand=True))
            if i not in hus and i in BY:      # huset er ikke lagt av tilpasningen: start-kameraet
                hus[i] = dict(s=1.0, kz=1.0, d=[0.0, 0.0], rot=0.0, sk=0.0, c0=[0.0, 0.0], for_haand=True)
    side = fitz.open(os.path.join(AI, navn + '.ai'))[0]
    vegger = {}
    for kf in kob_f:
        if kf['vegg'] == 'tak':
            continue
        vegger.setdefault((kf['id'], kf['vegg']), []).append(kf['flate'])
    lest = []
    for (i, kk), FF in vegger.items():
        el, geo = elementer(FF, side)
        if geo is None:
            continue
        x = BY[i]; pr = proj_par(G, k, hus[i]['c0'], hus[i])
        v = next((v for v in vegger_proj(x, pr, G) if v['k'] == kk), None)
        if v is None:            # for hånd koblet til en vegg som ikke vender mot tegneren med dette kameraet
            P_ = x['p']; a_, b_ = P_[kk], P_[(kk + 1) % len(P_)]
            v = dict(a=a_, b=b_, L=math.dist(a_, b_), venstre=a_ if pr(*a_, 0)[0] <= pr(*b_, 0)[0] else b_)
        lest.append(dict(id=i, vegg=kk, a=v['a'], b=v['b'], L=round(v['L'], 2), venstre=v['venstre'], flater=[f['i'] for f in FF],
                         farger=[f['farge'] for f in FF], elementer=el, geo=geo))
    tak = {}
    for kf in kob_f:
        if kf['vegg'] == 'tak':
            tak.setdefault(kf['id'], []).append(dict(flate=kf['flate']['i'], farge=kf['flate']['farge'], hull=len(kf['flate']['hull']),
                                                      hullpt=[[round(c, 2) for c in h.centroid.coords[0]] for h in kf['flate']['hull']]))
    return dict(navn=navn, hus={i: {kk: (vv if not isinstance(vv, np.ndarray) else vv.tolist()) for kk, vv in p.items()} for i, p in hus.items()},
                vegger=lest, tak=tak, G=G.tolist(), k=k)


def ark_kobling(L, ut, R=3):
    """Overlegg: tegningen, modellhusene med kameraet sitt, og hvilken vegg hver tegnet flate er koblet til."""
    import cv2, datalag
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg']}
    G = np.array(L['G']); k = L['k']
    side = fitz.open(os.path.join(AI, L['navn'] + '.ai'))[0]
    pm = side.get_pixmap(matrix=fitz.Matrix(R, R)); im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3]
    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR); im = (im * 0.55 + 110).astype(np.uint8)
    rng = np.random.default_rng(3)
    F = {f['i']: f for f in flater(L['navn'])[0]}
    for vg in L['vegger']:
        c = tuple(int(v) for v in rng.integers(40, 220, 3))
        for fi in vg['flater']:
            cv2.polylines(im, [(np.array(F[fi]['ytre'].exterior.coords) * R).astype(np.int32)], True, c, 2)
        for e in vg['elementer']:
            p = (np.array(e['pt']) * R).astype(int)
            typ = 'D' if (e['vb'] < 0.12 and e['hv'] > 0.3) else ('o' if e['hvit'] > 0.08 else '.')
            cv2.putText(im, typ, tuple(p - [4, -4]), 0, 0.45, (0, 0, 0), 1)
        P = F[vg['flater'][0]]['ytre'].representative_point()
        cv2.putText(im, f"{vg['id'][-5:]}/{vg['vegg']}", (int(P.x * R) - 20, int(P.y * R)), 0, 0.42, c, 1)
    for i, par in L['hus'].items():
        x = BY[i]; pr = proj_par(G, k, par['c0'], par)
        gp = (np.array([pr(q[0], q[1], 0) for q in x['p']]) * R).astype(np.int32)
        cv2.polylines(im, [gp], True, (0, 0, 230), 1)
        cv2.putText(im, i[-5:], tuple(gp.mean(0).astype(int)), 0, 0.4, (0, 0, 200), 1)
    cv2.imwrite(ut, im)


def tilpass_globalt(navn, B, R=1.5):
    """Ett kamera for hele tegningen (alle kandidathusene samtidig): rett opp skjevheten i start-kameraet før blokkene
    finjusteres. Grovsøk på forskyvning (malmatching), så Powell på alle seks parametrene."""
    import cv2
    from scipy.optimize import minimize
    E, im = avstandsbilde(navn, R); M = (im.min(axis=2) < 235).astype(np.float32)
    G, k = kamera_start(navn)
    c0 = np.mean([G @ [*Polygon(x['p']).centroid.coords[0], 1] for x in B], axis=0)
    def kant_alle(pr): return [l for x in B for l in kanter(x, pr, G)]
    best = None
    for s in (0.9, 1.0, 1.1):
        for kz in (1.2, 1.7, 2.2):
            pr = proj_par(G, k, c0, dict(s=s, kz=kz, d=(0, 0)))
            T, x0, y0 = _mal(kant_alle(pr), R)
            sr = int(150 * R); pad = sr + max(T.shape)
            Ep = cv2.copyMakeBorder(E, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
            ox, oy = int(x0 * R) + pad, int(y0 * R) + pad
            ax, ay = ox - sr, oy - sr
            sub = Ep[ay:oy + T.shape[0] + sr, ax:ox + T.shape[1] + sr]
            r = cv2.matchTemplate(sub, T, cv2.TM_CCORR) / T.sum()
            _, mx, _, ml = cv2.minMaxLoc(r)
            if best is None or mx > best[0]:
                best = (mx, s, kz, ((ax + ml[0] - ox) / R, (ay + ml[1] - oy) / R))
    _, s, kz, dd = best
    Pt = flatekanter(navn)
    def f(v):
        q = dict(s=v[0], kz=v[1], d=(v[2], v[3]), rot=v[4], sk=v[5])
        if not (0.7 < v[0] < 1.4 and 0.8 < v[1] < 3.0 and abs(v[4]) < 10 and abs(v[5]) < 0.2): return 2.0
        return -tosidig(E, R, Pt, kant_alle(proj_par(G, k, c0, q)), E.shape)
    r = minimize(f, [s, kz, dd[0], dd[1], 0, 0], method='Powell', options=dict(xtol=0.01, ftol=1e-4, maxfev=3000))
    v = r.x
    par = dict(s=float(v[0]), kz=float(v[1]), d=[float(v[2]), float(v[3])], rot=float(v[4]), sk=float(v[5]), score=-float(r.fun))
    # nytt start-kamera: G' slik at proj_par(G', k, ...) med s=1 osv. er det globale (bakken), og høydeskala kz globalt
    s_, rot, sk = par['s'], math.radians(par['rot']), par['sk']
    Mx = s_ * np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]]) @ np.array([[1, sk], [0, 1]])
    G2 = np.zeros((2, 3)); G2[:, :2] = Mx @ G[:, :2]; G2[:, 2] = Mx @ (G[:, 2] - c0) + c0 + np.array(par['d'])
    return G2, k * par['kz'], par


def flatekanter(navn, steg=1.0):
    """Punkter langs kantene til de fargede flatene (vegger og tak) i tegningen: det modellens kanter skal forklare."""
    F, _ = flater(navn)
    L = []
    for f in F:
        if min(f['farge']) > 0.97 or max(f['farge']) < 0.3 or f['ytre'].area < 6: continue
        c = np.array(f['ytre'].simplify(0.5).exterior.coords)
        L += [[tuple(a), tuple(b)] for a, b in zip(c[:-1], c[1:])]
    return _punkter(L, steg)


def tosidig(E, R, Pt, Lm, shape):
    """Tosidig kantmål: modellkantene mot tegningens streker (E) og tegningens flatekanter (Pt) mot modellkantene."""
    import cv2
    from scipy.ndimage import map_coordinates
    Pm = _punkter(Lm, 1.0)
    if len(Pm) == 0: return 0.0
    a = float(map_coordinates(E, [Pm[:, 1] * R, Pm[:, 0] * R], order=1, mode='constant', cval=0).mean())
    T = np.ones(shape, np.uint8)
    for p, q in Lm:
        cv2.line(T, (int(p[0] * R), int(p[1] * R)), (int(q[0] * R), int(q[1] * R)), 0, 1)
    dt = cv2.distanceTransform(T, cv2.DIST_L2, 3) / R
    b = float(np.exp(-map_coordinates(dt, [Pt[:, 1] * R, Pt[:, 0] * R], order=1, mode='nearest') ** 2 / (2 * 2.5 ** 2)).mean())
    return a + b


# ---------------------------------------------------------------- fra avlesning til vind

AVL = os.path.join(ROT, 'kilder', 'fasade-tegning')
KOBLING_FIL = os.path.join(ROT, 'kilder', 'fasade-kobling.json')


def lagre_avlesning(L):
    """Avlesningen (bare tall: kamera per hus, vegger og elementer i andel av veggen) i kilder/fasade-tegning/<tegning>.json,
    så vind kan lages på nytt uten tegningene (de er åndsverk og ligger bare lokalt)."""
    os.makedirs(AVL, exist_ok=True)
    ut = dict(tegning=L['navn'], laget=__import__('datetime').date.today().isoformat(), verktoy='verktoy/fasade_tegning.py les',
              kamera=dict(G=L['G'], k=L['k']), hus=L['hus'],
              vegger=[{k: v for k, v in vg.items() if k != 'farger'} | dict(farger=[[round(c * 255) for c in f] for f in vg['farger']]) for vg in L['vegger']],
              tak=L['tak'])
    json.dump(ut, open(os.path.join(AVL, L['navn'] + '.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0, default=float)


def klassifiser(el, L, hv_med=None):
    """Element -> (typ, b, h): 0 vindu, 1 dør, 2 port med buet topp; None = ikke et element (strek, flekk)."""
    bu_m, hv = el['bu'] * L, el['hv']
    if el['bu'] > 0.6 and el['hvit'] < 0.05:      # strek langs hele veggen (skillet mellom sokkel og vegg, bunnstreken)
        return None
    if bu_m < 0.3 and hv > 0.45:                  # loddrett skillestrek mellom rekkehus (i meter, ikke andel: lange vegger)
        return None
    if hv > 0.93:                                 # mørk spalte i hele vegghøyden: skillet mellom to tegnede hus (30.10)
        return None
    if bu_m < 0.35:                               # flekk eller sprosse, ikke et vindu
        return None
    # høyere enn vinduene og nede ved bakken (døra/porten kan stå i et hakk i flaten, så bunnen leses litt opp): dør eller port
    # dør/port: tydelig høyere enn vinduene og nede ved bakken (bunnen kan leses litt opp når døra står i et hakk i flaten),
    # eller et helt mørkt felt helt nede som er minst like høyt som vinduene
    hoy = hv_med is not None and el['vb'] < 0.4 and hv > 1.3 * hv_med and el['bu'] < 0.35
    mork = hv_med is not None and el['mork'] > 0.85 and el['hvit'] < 0.05 and el['vb'] < 0.1 and hv > 1.1 * hv_med and el['bu'] < 0.35
    if hoy or mork:
        if bu_m > 1.7 or el['buet']:
            return 2, round(min(max(bu_m, 1.8), 3.2), 2), 2.6      # port/stor inngangsdør med buet topp
        return 1, round(min(max(bu_m, 0.95), 1.6), 2), 2.2
    # bredt felt som ikke er en dør: gesimsbånd, skilt eller sokkellist (30.10); andelen alene gjelder ikke på korte vegger
    # (en bit av en delt vegg ved den nye brannmuren, 2–3 m: ett vindu er over 30 % av den)
    if (bu_m > 2.6 and el['bu'] > 0.06) or (el['bu'] > 0.3 and bu_m > 1.6):
        return None
    if hv > 0.08 and el['bu'] > 0.01:
        return 0, round(min(max(bu_m, 0.6), 1.3), 2), None
    return None


def tegnede_elementer(vg, L):
    """Det tegningen viser på én avlest vegg, slik legg_inn og kontrollen (verktoy/kontroll.py) begge leser det: én definisjon
    av hva som er vindu, dør/port og strek (30.10). Gir (el, vin, rader, gavl): el = [(element, klassifisering)] etter at
    biter av samme dør/vindu er slått sammen, vin = vinduene under gesims (v <= 1,05) sortert etter underkant, rader = vinduene
    samlet i tegnede rader (ny rad når underkanten står mer enn en halv vindushøyde over forrige), gavl = vinduer over gesims."""
    hv_alle = [e['hv'] for e in vg['elementer'] if klassifiser(e, L) is not None]
    hv_med = float(np.median(hv_alle)) if hv_alle else None
    el = [(e, klassifiser(e, L, hv_med)) for e in vg['elementer']]
    el = [(e, k) for e, k in el if k is not None and not (k[0] == 0 and e['vb'] < -0.05)]   # trapp og fortau under bunnkanten
    # to biter av samme dør/port/vindu (fløyer, glass i døra, trapp): den største står igjen (30.10)
    el.sort(key=lambda t: -(t[0]['bu'] * t[0]['hv']))
    beholdt = []
    for e, k in el:
        if any(abs(e['u'] - q['u']) * L < (k[1] + kq[1]) / 2 * 0.9 and min(e['vt'], q['vt']) > max(e['vb'], q['vb']) for q, kq in beholdt):
            continue
        beholdt.append((e, k))
    el = beholdt
    vin = sorted([e for e, k in el if k[0] == 0 and e['v'] <= 1.05], key=lambda e: e['vb'])
    rader = []
    for e in vin:
        # enkel kobling (30.10): avstanden til forrige vindu i rekkefølgen, så en håndtegnet rad som siger, ikke deles
        if rader and e['vb'] - rader[-1][-1]['vb'] < 0.5 * (float(np.percentile([q['hv'] for q in vin], 30)) if vin else 0.3):
            rader[-1].append(e)
        else:
            rader.append([e])
    gavl = [e for e, k in el if k[0] == 0 and e['v'] > 1.05]
    return el, vin, rader, gavl


def etasjer(h, n_et):
    """Brystningshøydene for etasjene et hus med gesims h (Kartverket) har plass til når tegningen viser n_et etasjer:
    standard (brystning 0,9, etasje 3,0, vinduer_regler.rader); viser tegningen flere, presses etasjene ned til 1,9 m
    (lavere vinduer under 2,4 m). Flere tegnede etasjer enn det: tegningen overdriver høyden, Kartverket går foran
    (Vegar 28.10). Gir (brystninger, presset vindushøyde eller None). Brukes av legg_inn og kontrollen (30.10)."""
    import vinduer_regler as VR
    brystn = VR.rader(h)
    if n_et > len(brystn) and n_et > 1:
        vh_ = VR.R['vh'] if (h - 0.3 - VR.R['vh'] - VR.R['bryst']) / (n_et - 1) >= 2.4 else 1.15
        br0 = 0.8 if vh_ < VR.R['vh'] else VR.R['bryst']
        et = (h - 0.3 - vh_ - br0) / (n_et - 1)
        if et >= 1.9:
            return [br0 + et * k for k in range(n_et)], vh_
    return brystn, None


VH_PRESS = [None]
LANDEMERKER = {'bnr-193870279', 'bnr-193972012', 'bnr-193869548', 'bnr-193867529'}   # egne agenter/egen kode (Tøihuset, rådhuset, Voldporten, kirka)


def vegg_vind(vg, x, P):
    """En tegnet vegg til vind-elementer på modellveggen: aksene i andel av veggen fra venstre i tegningen, radene til
    etasjene huset har plass til (brystning 0,9 m, etasje 3,0 m, som reglene); rader over gesims (gavl) står i gavlen."""
    import vinduer_regler as VR
    a, b = np.array(vg['a'], float), np.array(vg['b'], float)
    v0 = np.array(vg['venstre'], float); v1 = b if np.allclose(v0, a) else a
    L = float(np.linalg.norm(v1 - v0)); u = (v1 - v0) / L
    n = np.array([u[1], -u[0]])
    if Polygon(x['p']).contains(Point(*(v0 + u * L / 2 + n * 0.3))):
        n = -n
    h = x['h']
    el, vin, rader, _ = tegnede_elementer(vg, L)
    n_et = sum(1 for r in rader if not (np.mean([e['v'] for e in r]) < 0.22 and len(rader) > 1 and np.mean([e['hv'] for e in r]) < 0.7 * (np.median([e['hv'] for e in vin]) if vin else 0)))
    brystn, VH_PRESS[0] = etasjer(h, n_et)
    spenn = (max(e['vb'] for e in vin) - min(e['vb'] for e in vin)) * h if vin else 0
    if len(rader) > 1 and ((len(brystn) == 1 and VH_PRESS[0] is None) or spenn < 1.4):
        rader = [[e for r in rader for e in r]]   # én etasje: radene i tegningen er samme rad tegnet skjevt (30.10)
    # kjeller: nederste rad med små vinduer helt nede (høyde under 60 % av de andre radene)
    hv_med = np.median([e['hv'] for e in vin]) if vin else 0
    ut = []; notat = []
    rad_z = []
    k = 0
    for r in rader:
        vm = np.mean([e['v'] for e in r]); hm = np.mean([e['hv'] for e in r])
        if vm < 0.22 and hm < 0.7 * hv_med and len(rader) > 1:
            rad_z.append(('kjeller', 0.55, 0.6, 0.5)); continue
        if k < len(brystn):
            vh_ = VH_PRESS[0] or VR.R['vh']; rad_z.append(('etg', brystn[k] + vh_ / 2, vh_, None)); k += 1
        else:
            notat.append(f"rad {len(rad_z) + 1} fikk ikke plass under gesims (h {h} m)"); rad_z.append(None)
    for r, rz in zip(rader, rad_z):
        if rz is None: continue
        slag, zc, hh, bb = rz
        for e in r:
            t = min(max(e['u'] * L, 0), L)
            bw = bb or klassifiser(e, L, hv_med)[1]
            t = min(max(t, bw / 2 + 0.32), L - bw / 2 - 0.32) if L > bw + 0.64 else L / 2
            ut.append(VR.element(P, v0 + u * t, bw, n, zc, bw, hh, 0))
    for e, kk in el:
        if kk[0] in (1, 2):
            t = min(max(e['u'] * L, kk[1] / 2 + 0.32), L - kk[1] / 2 - 0.32) if L > kk[1] + 0.64 else L / 2
            ut.append(VR.element(P, v0 + u * t, kk[1], n, kk[2] / 2, kk[1], kk[2], kk[0]))
    # dør tar plassen til vinduet i 1. etasje der de står oppå hverandre
    dorer = [q for q in ut if q[9] in (1, 2)]
    ut = [q for q in ut if not (q[9] == 0 and q[2] < 3 and any(math.dist(q[:2], d[:2]) < (q[7] + d[7]) / 2 for d in dorer))]
    # to tegnede rader presset til én etasje (lavt hus): vinduer som da står oppå hverandre, blir ett (det bredeste) (30.10)
    beh = []
    for q in sorted(ut, key=lambda q: -q[7]):
        if x['id'] not in LANDEMERKER and q[9] == 0 and any(d[9] == 0 and abs(d[2] - q[2]) < 0.3 and math.dist(q[:2], d[:2]) < (q[7] + d[7]) / 2 for d in beh):
            continue
        beh.append(q)
    ut = [q for q in ut if any(q is d for d in beh)]
    gavl = [e for e, k in el if k[0] == 0 and e['v'] > 1.05]
    if gavl:
        notat.append(f"{len(gavl)} vindu(er) over gesims i tegningen (gavl/ark)")
    for q in ut:
        q[11] = 0          # fra tegning, ikke antatt
    return ut, dict(rader=[len(r) for r in rader], dorer=sum(1 for q in ut if q[9] in (1, 2)), notat=notat)


def legg_inn(tørt=False, bare=None):
    """Vind fra avlesningene (kilder/fasade-tegning/*.json) som rettelser. Tegnede vegger får tegningens elementer; veggene
    tegningen ikke viser, får reglene (vinduer_regler). Idempotent: egne linjer (GRUNN) tas ut først."""
    import datalag, vegger as VG, vinduer_regler as VR, glob as _g
    GRUNN = 'kvartaltegning som vektor (verktoy/fasade_tegning.py, 29.10)'
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    svf = os.path.join(ROT, 'rapport', 'streetview-fasader', 'fasit-sv-vegger.json')
    FASIT_SV = json.load(open(svf, encoding='utf8')) if os.path.exists(svf) else {}
    per_hus = {}
    # husdelingen (verktoy/husdeling.py, 30.10): en vegg lest på et hus som siden er delt eller slått sammen, fordeles på
    # husene etter hvor hvert element står langs veggen (punktet på bakken), ikke etter id-en avlesningen ble gjort med
    hd_f = os.path.join(ROT, 'kilder', 'husdeling.json')
    slekt = {}
    if os.path.exists(hd_f):
        HD = json.load(open(hd_f, encoding='utf8'))
        for D_ in HD.get('deling', []):
            slekt.setdefault(D_['id'], set()).update([D_['id']] + list(D_.get('nye_id') or []))
        for S_ in HD.get('sammen', []):
            for i_ in S_['ids']:
                slekt.setdefault(i_, set()).update(S_['ids'])
        for i_ in list(slekt):
            for j_ in list(slekt[i_]):
                slekt[i_] |= slekt.get(j_, set())
    for f in sorted(_g.glob(os.path.join(AVL, '*.json'))):
        A = json.load(open(f, encoding='utf8'))
        if bare and A['tegning'] not in bare: continue
        for vg in A['vegger']:
            v0 = np.array(vg['venstre'], float); v1 = np.array(vg['b'] if np.allclose(vg['venstre'], vg['a']) else vg['a'], float)
            els = []
            for e in vg['elementer']:
                e = dict(e); e['_g'] = (v0 + e['u'] * (v1 - v0)).tolist(); els.append(e)
            kand = [i_ for i_ in (slekt.get(vg['id']) or {vg['id']}) if i_ in BY and not BY[i_].get('skjul')]
            if len(kand) <= 1 and vg['id'] in BY and not BY[vg['id']].get('skjul'):
                per_hus.setdefault(vg['id'], []).append((A['tegning'], dict(vg, elementer=els))); continue
            if not kand: continue
            grp = {}
            for e in els:
                q = Point(*e['_g'])
                best = min(kand, key=lambda i_: Polygon(BY[i_]['p']).exterior.distance(q) + (0 if Polygon(BY[i_]['p']).buffer(0.5).contains(q) else 5))
                grp.setdefault(best, []).append(e)
            mid = 0.5 * (v0 + v1)
            for i_ in kand:
                Pk = Polygon(BY[i_]['p'])
                seg = LineString([v0 - (v1 - v0) * 0.05, v1 + (v1 - v0) * 0.05]).intersection(Pk.buffer(0.6))
                if seg.is_empty or seg.length < 1.0: continue
                c = np.array(seg.interpolate(0.5, normalized=True).coords[0])
                vg_i = dict(vg, id=i_, elementer=grp.get(i_, []), a=list(c - (v1 - v0) * 0.01), b=list(c + (v1 - v0) * 0.01), venstre=list(c - (v1 - v0) * 0.01), _mid=c.tolist(), _L0=float(np.linalg.norm(v1 - v0)))
                per_hus.setdefault(i_, []).append((A['tegning'], vg_i))
    nye, logg = [], []
    for i, lst in per_hus.items():
        x = BY.get(i)
        if not x or x.get('skjul') or x.get('kirke') or any(d_.get('kilde') != 'tak-tegning' for d_ in (x.get('deler') or [])):
            continue
        P = np.array(x['p'], float); V = VG.vegger(x, omg, slaa_sammen=False)
        # samme vegg i to tegninger: den med flest elementer
        beste = {}
        for tg, vg in lst:
            mid = np.array(vg['_mid']) if vg.get('_mid') else (np.array(vg['a']) + np.array(vg['b'])) / 2
            kk, _ = VG.naermeste_vegg(V, mid)
            if kk is None: continue
            if kk not in beste or len(vg['elementer']) > len(beste[kk][1]['elementer']):
                beste[kk] = (tg, vg)
        tegnet, info = [], {}
        for kk, (tg, vg) in beste.items():
            w = V[kk]
            vg2 = dict(vg, a=list(w['a']), b=list(w['c']),
                       venstre=list(w['a']) if np.linalg.norm(np.array(vg['venstre']) - w['a']) <= np.linalg.norm(np.array(vg['venstre']) - w['c']) else list(w['c']))
            if vg.get('_mid'):
                # delt/sammenslått: elementets plass langs modellveggen fra punktet på bakken (venstre ende som i avlesningen)
                ov0 = np.array(vg['venstre']); d_ = np.array(vg['b']) - np.array(vg['a'])
                wa, wc = np.array(w['a'], float), np.array(w['c'], float)
                if (wc - wa) @ d_ < 0: wa, wc = wc, wa
                Lw = float(np.linalg.norm(wc - wa)) or 1.0
                vg2['venstre'] = list(wa)
                # bredden står i andel av veggen avlesningen ble gjort på: regnes om til andel av husets vegg, ellers blir
                # vinduer ved den nye brannmuren for smale for klassifiser og forsvinner (885 mot 889 elementer 30.10)
                L0 = vg.get('_L0') or Lw
                vg2['elementer'] = [dict(e, u=float(((np.array(e['_g']) - wa) @ (wc - wa)) / Lw ** 2), bu=e['bu'] * L0 / Lw) for e in vg['elementer']]
            el, inf = vegg_vind(vg2, x, P)
            tegnet += el; info[kk] = dict(tegning=tg, **inf)
        # vegger tegningen ikke viser: Street View der kameraet så veggen (streetview_fasader.py, fasithusene), ellers reglene (30.10)
        sv_vegger = {}
        for sv in FASIT_SV.get(i, []):
            kk, _ = VG.naermeste_vegg(V, np.array(sv['mid']))
            if kk is not None and kk not in beste:
                sv_vegger[kk] = sv
                info[kk] = dict(tegning='Street View', rader=sv['rader'], dorer=sum(1 for q in sv['vind'] if q[9] in (1, 2)), notat=[sv['kilde']])
        sv_vind = [v for sv in sv_vegger.values() for v in sv['vind']]
        regler = [v for v in VR.lag_vind(x, omg)[0] if VG.naermeste_vegg(V, np.array(v[:2]))[0] not in beste and VG.naermeste_vegg(V, np.array(v[:2]))[0] not in sv_vegger]
        vind = regler + sv_vind + tegnet
        nye.append({"emne": "bygg", "id": i, "op": "sett", "felt": "vind", "verdi": vind, "hvem": "Claude", "dato": '2026-10-29', "grunn": GRUNN})
        nye.append({"emne": "bygg", "id": i, "op": "sett", "felt": "fasade_kilde", "verdi": "kvartaltegning", "hvem": "Claude", "dato": '2026-10-29', "grunn": GRUNN})
        nye.append({"emne": "bygg", "id": i, "op": "sett", "felt": "fasade_tegning", "verdi": {str(k): v for k, v in info.items()}, "hvem": "Claude", "dato": '2026-10-29', "grunn": GRUNN})
        logg.append(dict(id=i, navn=x.get('navn'), vegger=info, tegnet=len(tegnet), regler=len(regler), streetview=len(sv_vind)))
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
    json.dump(logg, open(os.path.join(ROT, 'rapport', 'bygg', 'fasade-tegning.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f"{len(logg)} hus fikk vind fra tegningene ({sum(l['tegnet'] for l in logg)} elementer fra tegning, {sum(l['regler'] for l in logg)} etter reglene)")
    return logg


# ---------------------------------------------------------------- kobling for hånd (uten kamera)

def familie(P):
    """Venstre (veggen vender mot SV i tegningen) eller høyre (mot SØ): bunnkanten heller ned mot høyre / venstre."""
    x0, y0, x1, y1 = P.bounds
    xs = np.linspace(x0 + (x1 - x0) * 0.15, x1 - (x1 - x0) * 0.15, 7)
    ys = []
    for xx in xs:
        g = P.intersection(LineString([(xx, -1e5), (xx, 1e5)]))
        ys.append(g.bounds[3] if not g.is_empty else np.nan)
    ok = ~np.isnan(ys)
    k = np.polyfit(xs[ok], np.array(ys)[ok], 1)[0] if ok.sum() >= 2 else 0
    return 'SV' if k > 0 else 'SØ'


def les_for_haand(navn, d=None):
    """Kobling fra kilder/fasade-kobling.json: {tegning: {hus: {id: [flate, …]}}}. Hver flate går til husets vegg i samme
    familie (SV: utovernormal 180–270°, SØ: 90–180°), den lengste frie; flere flater på samme vegg slås sammen (rekkehus,
    sokkel). Ingen kameratilpasning: tegningen bestemmer hvilken side, modellen hvilken vegg."""
    import datalag, vegger as VG
    d = d or datalag.alle(); BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    K = json.load(open(KOBLING_FIL, encoding='utf8'))[navn]['hus']
    F = {f['i']: f for f in flater(navn)[0]}
    side = fitz.open(os.path.join(AI, navn + '.ai'))[0]
    lest = []
    for i, fl in K.items():
        x = BY[i]; V = VG.vegger(x, omg, slaa_sammen=True)
        grp = {}; del_ = {}; plass_ = {}
        for nr, fi in enumerate(fl):
            if isinstance(fi, dict) and 'plass' in fi:     # {"f": [..], "side": "SØ@1", "plass": [0.6, 1]}: flaten er bare en del av veggen
                kl = f"{fi['side']}#{nr}"; grp[kl] = list(fi['f']); plass_[kl] = tuple(fi['plass']); continue
            if isinstance(fi, dict):                       # {"f": [..], "side": "SV", "fra": 0, "til": 0.5}: del av en tegnet vegg
                grp.setdefault(fi['side'], []).extend(fi['f']); del_[fi['side']] = (fi['fra'], fi['til']); continue
            if isinstance(fi, str) and '/' in fi:          # "flate/SV" eller "flate/SØ": siden gitt for hånd
                fi, fam = fi.split('/'); fi = int(fi)
            else:
                fam = familie(F[fi]['ytre'])
            grp.setdefault(fam, []).append(fi)
        for nkl, fis in grp.items():
            fam, _, tvang = nkl.split('#')[0].partition('@')   # "flate/SV@2": veggen gitt for hånd (vegger.vegger, slått sammen)
            c = 225 if fam == 'SV' else 135
            kand = [(w['L'] * (w['felles'] < 0.5), k) for k, w in enumerate(V)
                    if abs(((math.degrees(math.atan2(w['n'][0], w['n'][1])) - c) + 180) % 360 - 180) <= 55]
            if tvang: kand = [(1, int(tvang))]
            if not kand: continue
            k = max(kand)[1]; w = V[k]
            el, geo = elementer([F[f] for f in fis], side, andre=list(F.values()))
            if geo is None: continue
            if nkl in del_:                                 # tegningen viser flere modellhus i én vegg: bare husets del, i husets andel
                a0, a1 = del_[nkl]
                el = [dict(e, u=round((e['u'] - a0) / (a1 - a0), 4), bu=round(e['bu'] / (a1 - a0), 4)) for e in el if a0 <= e['u'] < a1]
            if nkl in plass_:
                p0, p1 = plass_[nkl]
                el = [dict(e, u=round(p0 + e['u'] * (p1 - p0), 4), bu=round(e['bu'] * (p1 - p0), 4)) for e in el]
            # venstre i tegningen = seerens venstre utenfra
            ltr = bool(w['u'] @ np.array([-w['n'][1], w['n'][0]]) > 0)
            venstre = w['a'] if ltr else w['c']
            lest.append(dict(id=i, vegg=k, side=fam, a=[float(v) for v in w['a']], b=[float(v) for v in w['c']], L=round(float(w['L']), 2),
                             venstre=[float(v) for v in venstre], flater=fis, farger=[F[f]['farge'] for f in fis], elementer=el, geo=geo))
    samlet = {}
    for v in lest:                                         # flere flater lest hver for seg på samme vegg: én vegg
        kk = (v['id'], v['vegg'])
        if kk in samlet:
            samlet[kk]['elementer'] += v['elementer']; samlet[kk]['flater'] += v['flater']; samlet[kk]['farger'] += v['farger']
        else:
            samlet[kk] = v
    return dict(navn=navn, hus={}, vegger=list(samlet.values()), tak={}, G=[[0, 0, 0], [0, 0, 0]], k=0)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'les_for_haand':
        for n in a[1:]:
            L = les_for_haand(n); lagre_avlesning(L)
            for v in L['vegger']: print(n, v['id'], v['side'], f"vegg {v['vegg']}", len(v['elementer']), 'elementer')
    elif a and a[0] == 'les':
        for n in a[1:]:
            L = les(n); lagre_avlesning(L)
            os.makedirs(ARB, exist_ok=True); ark_kobling(L, os.path.join(ARB, n + '-kobling.png'))
    elif a and a[0] == 'legg_inn':
        legg_inn('--tørt' in a, [n for n in a[1:] if not n.startswith('--')] or None)
    else:
        print(__doc__)

