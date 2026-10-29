"""Tak fra fotavtrykket: rett skjelett (straight skeleton) over en husrekke, med gavler der Gamlebyens hus har saltak.

Feltene som lages er de samme som src/07 tegner (og som etter/10_tak.py lagde; den fila er ikke i repoet):
  tak2   takflater, hver en liste [x, y, t] der t er avstanden inn fra takfoten (taket står i h + t * th)
  gavl2  gavlvegger og brannmurer: linjestykker [[x, y, t], [x, y, t]] fra veggtoppen opp til taket
Taket beregnes for hele rekka (alle hus som står inntil hverandre) og deles så per hus, så nabotak møtes i samme møne.

Metoden (ingen ekstra bibliotek, bare shapely, numpy, opencv):
  1. Rekka slås sammen til ett omriss U. Vegger som skal være gavl, forlenges utover (taket fortsetter forbi gavlen og
     klippes der), resten får valm.
  2. Bølgefronten: U krympes med skarpe hjørner (mitre) i trinn på oppløsningen; T(p) = tida fronten bruker til punktet p.
     Det er definisjonen av rett skjelett, og GEOS gjør topologien (splitt, hull) riktig.
  3. Hver takflate hører til én vegg k: der avstanden til veggens linje d_k er lik T, i den sammenhengende biten som
     berører veggen. Innenfor flaten er t = d_k eksakt (flaten er plan).
  4. Flatene gjøres til polygoner; hjørner der tre flater møtes regnes eksakt (like langt fra alle tre veggenes linjer),
     så nabo-flater deler hjørnepunkt og ingen sprekker vises.
  5. Takhøyden kappes ved t = 9,146 (7,5 m ved helning 0,82, som i src/07); over det er taket flatt.
  6. Det ingen flate dekker (et knutepunkt rasteret ikke fant), får planet de fleste pikslene under biten har.
Kontroll 29.10: på de gamle OSM-omrissene gir dette taket median 0,07 m avvik fra de gamle takflatene (90 % under 0,8 m);
avvikene er der de gamle rekkene var delt opp annerledes.

    import tak
    per_hus = tak.rekke([shapely-polygoner], gavl=lambda a, b: bool)   # -> [(tak2, gavl2), ...] i samme rekkefølge
"""
import math
import numpy as np
import cv2
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

KAPP = 7.5 / 0.82          # t der taket blir flatt (src/07: CAP 7,5 m ved helning 0,82)
LUKK = 0.15                # glipper mellom hus i samme rekke under dette lukkes


def _ringer(P):
    return [np.array(P.exterior.coords)[:-1]] + [np.array(r.coords)[:-1] for r in P.interiors]


def _rydd(P, tol=0.04):
    P = orient(P.simplify(tol, preserve_topology=True), 1.0)
    return P if P.is_valid else orient(P.buffer(0), 1.0)


def _kanter(P):
    """Alle kanter (a, b, innover-normal) i et orientert polygon (ytre mot klokka, hull med klokka)."""
    ut = []
    for R in _ringer(P):
        n = len(R)
        for k in range(n):
            a, b = R[k], R[(k + 1) % n]; u = b - a; L = float(np.hypot(*u))
            if L < 1e-6:
                continue
            u = u / L
            ut.append((a, b, np.array([-u[1], u[0]]), L))
    return ut


def gavl_regel(P, a, b, kanter):
    """Regel for hus uten gammelt tak å arve fra: veggen er gavl når den er enden av en fløy: begge hjørnene er konvekse
    (60–120°), naboveggene er omtrent parallelle og minst like lange, og veggen er høyst 13 m (saltak; ellers valm)."""
    for k, (a0, b0, n0, L0) in enumerate(kanter):
        if np.allclose(a0, a) and np.allclose(b0, b):
            break
    else:
        return False
    m = len(kanter)
    pa, pn = kanter[(k - 1) % m], kanter[(k + 1) % m]
    if L0 > 13 or min(pa[3], pn[3]) < 0.9 * L0:
        return False
    u0 = (b0 - a0) / L0
    up = (pa[1] - pa[0]) / pa[3]; un = (pn[1] - pn[0]) / pn[3]
    konveks = lambda u1, u2: u1[0] * u2[1] - u1[1] * u2[0] > 0 and abs(u1 @ u2) < 0.5
    return konveks(up, u0) and konveks(u0, un) and (up @ -un) > 0.94


def _forleng(U, gavler):
    """U med gavlveggene forlenget utover langs naboveggene (taket går forbi og klippes ved gavlen)."""
    biter = [U]
    for a, b, n, L, ua, ub in gavler:
        D = 0.75 * L + 2.0
        q = Polygon([a, b, b + ub * D, a + ua * D])
        if not q.is_valid:
            continue
        if q.buffer(-0.05).intersects(U):
            continue
        biter.append(q.buffer(0.01))
    E = unary_union(biter)
    if isinstance(E, MultiPolygon):
        E = max(E.geoms, key=lambda g: g.area)
    return _rydd(E, 0.01)


UTSETT = 0.3      # meter: omrisset blåses opp og forenkles før skjelettet, så små sprang i fasaden ikke gir smale flater
FORENKLE = 0.25   # meter: toleranse for forenklingen (taket over en rekke følger ikke hvert lite sprang i veggen)


def skjelett(U, gavl_kant=None, res=None):
    """Takflatene over omrisset U: liste av (polygon, (nx, ny, c)) med t = nx*x + ny*y + c innenfor flaten (kappet ved KAPP).
    gavl_kant(a, b) -> True for vegger som skal ha gavl.
    Skjelettet regnes på U blåst opp UTSETT m og forenklet FORENKLE m (rekkas tak følger ikke hvert lite sprang), og planene
    flyttes ned UTSETT igjen, så t = 0 langs de virkelige veggene; flatene klippes til U."""
    U = _rydd(U)
    Us = _rydd(U.buffer(UTSETT, join_style='mitre', mitre_limit=5.0).simplify(FORENKLE, preserve_topology=True), 0.01)
    if isinstance(Us, MultiPolygon):
        Us = max(Us.geoms, key=lambda g: g.area)
    kU = _kanter(Us)
    gavler = []
    if gavl_kant:
        m = len(kU)
        for k, (a, b, n, L) in enumerate(kU):
            if not gavl_kant(a, b):
                continue
            pa, pn = kU[(k - 1) % m], kU[(k + 1) % m]
            ua = (pa[1] - pa[0]) / pa[3]; ub = (pn[0] - pn[1]) / pn[3]
            gavler.append((a, b, n, L, ua, ub))
    E = _forleng(Us, gavler) if gavler else Us
    kE = _kanter(E)
    if res is None:
        res = float(np.clip(math.sqrt(E.area) / 600, 0.05, 0.12))
    x0, y0, x1, y1 = E.bounds; x0 -= 3 * res; y0 -= 3 * res
    W = int((x1 - x0) / res) + 4; H = int((y1 - y0) / res) + 4
    Ytop = y1 + 3 * res
    px = lambda xy: np.round(np.c_[(xy[:, 0] - x0) / res - 0.5, (Ytop - xy[:, 1]) / res - 0.5] * 8).astype(np.int32)
    def fyll(G):
        m = np.zeros((H, W), np.uint8)
        for g in getattr(G, 'geoms', [G]):
            if g.is_empty or g.geom_type != 'Polygon':
                continue
            cv2.fillPoly(m, [px(np.array(g.exterior.coords))], 1, cv2.LINE_8, 3)
            for r in g.interiors:
                cv2.fillPoly(m, [px(np.array(r.coords))], 0, cv2.LINE_8, 3)
        return m
    inne = fyll(E).astype(bool)
    T = np.zeros((H, W), np.float32); t = 0.0
    while True:
        t += res
        O = E.buffer(-t, join_style='mitre', mitre_limit=50.0)
        if O.is_empty:
            break
        T += fyll(O)
    T = T * res + res / 2
    T[~inne] = 0
    XX = x0 + (np.arange(W) + 0.5) * res; YY = Ytop - (np.arange(H) + 0.5) * res
    gx, gy = np.meshgrid(XX, YY)
    tol = 1.6 * res
    # vegger på samme linje (innen 1,5° og 0,1 m) er samme takplan
    plan, gruppe = [], []
    for a, b, n, L in kE:
        c = -float(n @ a)
        for gi, (nx, ny, cc) in enumerate(plan):
            if nx * n[0] + ny * n[1] > math.cos(math.radians(1.5)) and abs(cc - c) < 0.1:
                gruppe.append(gi); break
        else:
            plan.append((float(n[0]), float(n[1]), c)); gruppe.append(len(plan) - 1)
    # 3. flate per takplan: der avstanden til linja er lik T, i biter som berører en av veggene på linja
    lab = np.full((H, W), -1, np.int32); best = np.full((H, W), np.inf, np.float32)
    for gi, (nx, ny, c) in enumerate(plan):
        d = nx * gx + ny * gy + c
        kand = inne & (np.abs(d - T) <= tol) & (d >= -tol)
        if not kand.any():
            continue
        frø = np.zeros((H, W), np.uint8)
        for k, (a, b, n, L) in enumerate(kE):
            if gruppe[k] == gi:
                cv2.line(frø, tuple(px(a[None])[0]), tuple(px(b[None])[0]), 1, 2, cv2.LINE_8, 3)
        nk, cc = cv2.connectedComponents(kand.astype(np.uint8), connectivity=8)
        berort = np.unique(cc[(frø > 0) & kand]); berort = berort[berort > 0]
        if len(berort):
            m = np.isin(cc, berort)
            e = np.abs(d - T); bedre = m & (e < best)
            lab[bedre] = gi; best[bedre] = e[bedre]
    if (inne & (lab < 0)).any() and (lab >= 0).any():
        from scipy import ndimage
        _, (iy, ix) = ndimage.distance_transform_edt(lab < 0, return_indices=True)
        fyllinn = inne & (lab < 0); lab[fyllinn] = lab[iy[fyllinn], ix[fyllinn]]
    lab[~inne] = -1
    # små øyer av en flate inne i en annen (støy) tas bort: hver flate beholder bare biter over 0,3 m²
    for gi in set(np.unique(lab).tolist()) - {-1}:
        m = (lab == gi).astype(np.uint8)
        nk, cc, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        for q in range(1, nk):
            if st[q, cv2.CC_STAT_AREA] * res * res < 0.3:
                lab[cc == q] = -2
    if (lab == -2).any():
        from scipy import ndimage
        _, (iy, ix) = ndimage.distance_transform_edt(lab < 0, return_indices=True)
        fyllinn = lab == -2; lab[fyllinn] = lab[iy[fyllinn], ix[fyllinn]]
    # 4. knutepunkt der tre eller flere flater møtes: eksakt (like langt fra alle linjene)
    pad = np.pad(lab, 1, constant_values=-1)
    nab = np.stack([pad[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)], -1)
    srt = np.sort(nab, -1); antall = 1 + (np.diff(srt, axis=-1) != 0).sum(-1) - (srt[..., 0] < 0)
    node_m = (antall >= 3) & inne
    noder = []
    if node_m.any():
        nn, cc = cv2.connectedComponents(cv2.dilate(node_m.astype(np.uint8), np.ones((3, 3), np.uint8)), connectivity=8)
        for q in range(1, nn):
            ys, xs = np.nonzero(cc == q)
            S = sorted({int(v) for v in np.unique(nab[ys, xs]) if v >= 0})
            c0 = np.array([XX[xs].mean(), YY[ys].mean()])
            if len(S) >= 3:
                A = np.array([[plan[s][0] - plan[S[0]][0], plan[s][1] - plan[S[0]][1]] for s in S[1:]])
                bb = np.array([plan[S[0]][2] - plan[s][2] for s in S[1:]])
                xy = np.linalg.lstsq(A, bb, rcond=None)[0]
                if np.hypot(*(xy - c0)) < 4 * res:
                    c0 = xy
            noder.append((c0, set(S)))
    # flatens hjørner er endepunktene til veggene på linja og knutepunktene der flaten møter to andre; rekkefølgen tas
    # fra flatens omriss i rasteret (alle kanter i et rett skjelett er rette mellom disse punktene)
    flater = []
    for gi in sorted(set(np.unique(lab).tolist()) - {-1}):
        m = (lab == gi).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        ende = [q for k, (a, b, n, L) in enumerate(kE) if gruppe[k] == gi for q in (a, b)]
        kand = ende + [c0 for c0, S in noder if gi in S]
        pl = (plan[gi][0], plan[gi][1], plan[gi][2] - UTSETT)
        for cnt in cs:
            if cv2.contourArea(cnt) * res * res < 0.2:
                continue
            cnt = cnt[:, 0, :].astype(float)
            C = np.c_[x0 + (cnt[:, 0] + 0.5) * res, Ytop - (cnt[:, 1] + 0.5) * res]
            plass = []
            for v in kand:
                dd = np.hypot(*(C - v).T); i = int(dd.argmin())
                if dd[i] < 5 * res:
                    plass.append((i, v))
            plass.sort(key=lambda q: q[0])
            ren = []
            for _, v in plass:
                if not any(np.hypot(*(v - w)) < 1e-6 for w in ren):
                    ren.append(np.asarray(v, float))
            if len(ren) < 3:
                continue
            F = Polygon(ren)
            if not F.is_valid:
                F = F.buffer(0)
            if F.is_empty or F.area < 1e-3:
                continue
            F = F.intersection(_halvplan(pl, KAPP, E.bounds))
            if not F.is_empty:
                flater.append((F, pl))
    # 5. flatt tak over kappet
    topp = E.buffer(-(KAPP + UTSETT), join_style='mitre', mitre_limit=50.0)
    if not topp.is_empty:
        flater.append((topp, (0.0, 0.0, KAPP)))
    # 6. det ingen flate dekker (et knutepunkt rasteret ikke fant): biten får planet flest piksler under den har
    dekket = unary_union([F.buffer(1e-6) for F, _ in flater]) if flater else Polygon()
    rest = U.difference(dekket)
    for g in getattr(rest, 'geoms', [rest]):
        if g.geom_type != 'Polygon' or g.area < 0.05:
            continue
        m = fyll(g).astype(bool) & (lab >= 0)
        if not m.any():
            c = g.representative_point(); i = int((Ytop - c.y) / res); j = int((c.x - x0) / res)
            v = lab[min(max(i, 0), H - 1), min(max(j, 0), W - 1)]
            if v < 0:
                continue
        else:
            v = np.bincount(lab[m]).argmax()
        pl = (plan[v][0], plan[v][1], plan[v][2] - UTSETT)
        G = g.intersection(_halvplan(pl, KAPP, E.bounds))
        if not G.is_empty:
            flater.append((G, pl))
    # klipp til U (gavlforlengelsene og oppblåsingen bort)
    ut = []
    for F, pl in flater:
        G = F.intersection(U)
        for g in getattr(G, 'geoms', [G]):
            if g.geom_type == 'Polygon' and g.area > 1e-3:
                ut.append((g, pl))
    return ut, U


def _halvplan(pl, kapp, bounds):
    """Området der flatens t <= kapp (resten er flatt tak)."""
    nx, ny, c = pl
    x0, y0, x1, y1 = bounds; B = box(x0 - 50, y0 - 50, x1 + 50, y1 + 50)
    if abs(nx) + abs(ny) < 1e-9:
        return B
    # linja nx*x + ny*y + c = kapp; halvplanet på siden der t mindre
    n = np.array([nx, ny]); p0 = n * (kapp - c)
    u = np.array([-ny, nx]); R = 1e4
    q = Polygon([p0 + u * R, p0 - u * R, p0 - u * R - n * R, p0 + u * R - n * R])
    return q.intersection(B)


def _t(pl, x, y):
    return float(min(max(pl[0] * x + pl[1] * y + pl[2], 0.0), KAPP))


def _enkle(g):
    """Polygon med hull deles i biter uten hull (src/07 trianglerer hver flate uten hull)."""
    if not g.interiors:
        return [g]
    c = g.interiors[0].centroid
    x0, y0, x1, y1 = g.bounds
    v = box(x0 - 1, y0 - 1, c.x, y1 + 1); h = box(c.x, y0 - 1, x1 + 1, y1 + 1)
    ut = []
    for half in (v, h):
        G = g.intersection(half)
        for gg in getattr(G, 'geoms', [G]):
            if gg.geom_type == 'Polygon' and gg.area > 1e-3:
                ut += _enkle(gg)
    return ut


def per_hus(flater, U, hus, gavl_kant=None):
    """Del rekkas tak på husene: (tak2, gavl2) for huset (polygon). gavl2 = husets vegger som ikke er yttervegg på U
    (brannmur mot nabo) eller som er gavl."""
    H = orient(hus.buffer(0), 1.0)
    tak2 = []
    for F, pl in flater:
        G = F.intersection(H)
        for g in getattr(G, 'geoms', [G]):
            if g.geom_type != 'Polygon' or g.area < 0.02:
                continue
            for e in _enkle(orient(g, 1.0)):
                cs = np.array(e.exterior.coords)[:-1]
                tak2.append([[round(float(x), 2), round(float(y), 2), round(_t(pl, x, y), 3)] for x, y in cs])
    gavl2 = []
    Ub = U.boundary
    for a, b, n, L in _kanter(H):
        seg = LineString([a, b])
        paa_U = seg.buffer(0.05).intersection(Ub).length >= 0.9 * L
        er_gavl = paa_U and gavl_kant is not None and gavl_kant(np.asarray(a), np.asarray(b))
        if paa_U and not er_gavl:
            continue
        for F, pl in flater:
            S = seg.intersection(F.buffer(1e-4))
            for s in getattr(S, 'geoms', [S]):
                if s.geom_type != 'LineString' or s.length < 0.05:
                    continue
                (xa, ya), (xb, yb) = s.coords[0], s.coords[-1]
                ta, tb = _t(pl, xa, ya), _t(pl, xb, yb)
                if ta < 0.02 and tb < 0.02:
                    continue
                gavl2.append([[round(xa, 2), round(ya, 2), round(ta, 3)], [round(xb, 2), round(yb, 2), round(tb, 3)]])
    return tak2, gavl2


def rekker(polys, lukk=LUKK):
    """Grupper hus som står inntil hverandre: liste av lister med indekser."""
    P = [p.buffer(lukk / 2) for p in polys]
    tre = shapely.STRtree(P); n = len(P); far = list(range(n))
    def rot(i):
        while far[i] != i:
            far[i] = far[far[i]]; i = far[i]
        return i
    for i in range(n):
        for j in tre.query(P[i]):
            j = int(j)
            if j > i and P[i].intersection(P[j]).area > 0.05:
                far[rot(i)] = rot(j)
    g = {}
    for i in range(n):
        g.setdefault(rot(i), []).append(i)
    return list(g.values())


def omriss_rekke(polys, lukk=LUKK):
    U = unary_union([p.buffer(lukk, join_style='mitre') for p in polys]).buffer(-lukk, join_style='mitre')
    if isinstance(U, MultiPolygon):
        U = max(U.geoms, key=lambda g: g.area)
    # små hull (glipper mellom hus) fylles
    U = Polygon(U.exterior, [r for r in U.interiors if Polygon(r).area > 4.0])
    return _rydd(U)
