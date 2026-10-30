"""Rene tak (30.10): hvert hus er én eller noen få rektangulære kropper med et enkelt tak, slik Vegar tegnet dem i 2015.

Før dette regnet verktoy/tak.py taket som rett skjelett over hele husrekka (kommunekartets omriss). Det ga sammensatte valmtak
som ikke finnes: hvert lite sprang i fasaden ble en egen takflate, og rekka fikk ett tak på tvers av husene. Tegningene viser
noe annet: hvert hus har sin egen kropp med saltak (gavler mot naboene og i endene), noen ganger valm eller halvvalm, og
vinkelhus er to kropper. Dette verktøyet lager det taket.

Modellen per hus (kilder/tak-tegning.json kan overstyre alt, se under):
  1. Kroppene: omrisset legges i sin hovedretning (lengdeveid retning på kantene, modulo 90°). Er omrisset nesten et rektangel
     (minst 80 % av det omskrevne rektangelet i den retningen), er huset én kropp. Ellers deles det i største rektangler i et
     rutenett av hjørnenes koordinater (høyst tre kropper; små rester går til nabokroppen).
  2. Taket på én kropp er det nederste av noen plan (t = avstand inn fra takfoten, høyden h + t·th som src/07 tegner):
       sal       t = v − v0 og t = v1 − v (mønet midt på, gavl i endene)
       valm      + t = u − u0 og t = u1 − u (endene)
       halvvalm  endeplanene løftet: gavl opp til ca. 55 % av mønehøyden, valm over
       pult      ett plan over hele bredden
       flatt     ingen helning
     Ender som støter mot en annen kropp i samme hus, forlenges en halv bredde inn i den, så mønet går inn i nabotaket (kil-
     renne) i stedet for å slutte med en vegg.
  3. Husets tak er det øverste av kroppenes tak (vinkelhus får kilrenne der fløyene møtes), klippet til omrisset.
  4. Gavler (gavl2): alle vegger der taket står over gesims (gavlender, brannmurer mot naboen, pultens høye vegg).
  5. Takform og mønretning: kilder/tak-tegning.json (lest av tegningen, se verktoy/husdeling.py og rapport/tak/) går foran.
     Ellers avgjøres de av Kartverkets DOM−DTM (1 m): alle kombinasjoner av mønretning og takform tilpasses høydene inne i
     kroppen (h og th fritt, minste kvadrater), og den enkleste formen som passer (saltak foretrekkes) velges.
     Vegghøyde og takhelning: fra samme tilpasning; rapport/hoyder (hent.py + legg_inn.py) overstyrer der Kartverket-målingen er sikker.

    python3 verktoy/tak_enkel.py [--tørt]          rettelser for alle hus i Gamlebyen med tak fra kommunekartet
    python3 verktoy/tak_enkel.py ark [x y r navn]   plan med DOM−DTM og mønene (rapport/tak/, bildene ikke i git)
    python3 verktoy/tak_enkel.py fra_kontroll       takform og mønretning lest av tegningene (rapport/kontroll/avvik.json: gavler og
                                                    trekantede takflater på huset) inn i kilder/tak-tegning.json; linjer satt for
                                                    hånd (uten «kilde: kontroll») røres ikke

Kirka, Kaserna og portbyggene røres ikke. Hus med deler (tårn) får rent tak på kroppen; delene står oppå (kilder/tak-tegning.json kan legge
til deler: tårn som tegningen viser og DOM har høyden til). tak.py brukes ikke lenger i Gamlebyen.
"""
import json, math, os, sys
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import shapely

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag

GRUNN = 'rent tak etter tegningen og DOM (verktoy/tak_enkel.py, 30.10)'
HVEM, DATO = 'Claude', '2026-10-30'
TEGNING_FIL = os.path.join(ROT, 'kilder', 'tak-tegning.json')
FORMER = ('sal', 'valm', 'halvvalm', 'pult', 'flatt')
HALV = 0.55          # halvvalm: gavlen går opp til denne andelen av mønehøyden
RYDDE = 0.7          # m: hjørnekoordinater nærmere enn dette slås sammen i rutenettet
EPS = 1e-6


# ------------------------------------------------------------------ geometri

def hovedretning(P):
    """Hovedretningen (radianer, 0–90°) som lengdeveid gjennomsnitt av kantretningene modulo 90°."""
    c = np.array(P.exterior.coords)
    e = np.diff(c, axis=0); L = np.hypot(e[:, 0], e[:, 1]); a = np.arctan2(e[:, 1], e[:, 0]) % (math.pi / 2)
    # vektet sirkelmiddel på 4·vinkel
    z = (L * np.exp(4j * a)).sum()
    return (np.angle(z) / 4) % (math.pi / 2)


def til_lokal(xy, th):
    c, s = math.cos(th), math.sin(th)
    xy = np.asarray(xy, float)
    return np.c_[xy[:, 0] * c + xy[:, 1] * s, -xy[:, 0] * s + xy[:, 1] * c]


def fra_lokal(uv, th):
    c, s = math.cos(th), math.sin(th)
    uv = np.asarray(uv, float)
    return np.c_[uv[:, 0] * c - uv[:, 1] * s, uv[:, 0] * s + uv[:, 1] * c]


def _klynge(v, tol):
    v = sorted(v); ut = [[v[0]]]
    for x in v[1:]:
        if x - ut[-1][-1] < tol: ut[-1].append(x)
        else: ut.append([x])
    return [float(np.mean(g)) for g in ut]


def _rektgrad(G):
    x0, y0, x1, y1 = G.bounds
    return G.area / max((x1 - x0) * (y1 - y0), 1e-9)


def _del_opp(L, nivaa):
    """Beste oppdeling av L (lokal ramme) i nesten-rektangler: snitt langs u eller v gjennom de innoverbøyde hjørnene,
    rekursivt. Poeng = spill (omskrevet rektangel minus areal) + 10 m² per ekstra kropp. Gir (poeng, [biter])."""
    x0, y0, x1, y1 = L.bounds
    spill = (x1 - x0) * (y1 - y0) - L.area
    best = (spill, [L])
    if nivaa == 0 or _rektgrad(L) >= 0.9:
        return best
    S = orient(L.simplify(0.3, preserve_topology=True), 1.0)
    c = np.array(S.exterior.coords)[:-1]; n = len(c)
    kutt = set()
    for k in range(n):
        a, b, d = c[k - 1], c[k], c[(k + 1) % n]
        if (b[0] - a[0]) * (d[1] - b[1]) - (b[1] - a[1]) * (d[0] - b[0]) < -1e-6:      # innoverbøyd (CCW-polygon)
            kutt.add(('u', round(float(b[0]), 2))); kutt.add(('v', round(float(b[1]), 2)))
    from shapely.ops import split as _split
    for akse, verdi in kutt:
        ln = LineString([(verdi, y0 - 1), (verdi, y1 + 1)]) if akse == 'u' else LineString([(x0 - 1, verdi), (x1 + 1, verdi)])
        try:
            deler = [g for g in _split(L, ln).geoms if g.area > 0.5]
        except Exception:
            continue
        if len(deler) < 2: continue
        smaa = [g for g in deler if min(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]) < 2.5]
        if smaa: continue
        # snittet koster etter lengden (et langt snitt på langs av en fløy gir to smale kropper der det er én)
        snitt = ln.intersection(L).length
        tot = 10.0 * (len(deler) - 1) + 2.0 * snitt; biter = []
        for g in deler:
            p_, bb = _del_opp(g, nivaa - 1); tot += p_; biter += bb
        if tot < best[0] - 1e-6:
            best = (tot, biter)
    return best


def kropper(P, th=None, maks=3):
    """Del omrisset i rektangulære kropper. Gir (th, [dict(u0, u1, v0, v1, del_=Polygon)]) i lokal ramme (u langs th)."""
    P = orient(P.buffer(0), 1.0)
    if th is None:
        th = hovedretning(P)
    L = Polygon(til_lokal(np.array(P.exterior.coords), th), [til_lokal(np.array(r.coords), th) for r in P.interiors]).buffer(0)
    if L.geom_type != 'Polygon':
        L = max(L.geoms, key=lambda g: g.area)
    if L.area < 30:
        biter = [L]
    else:
        _, biter = _del_opp(L, 2)
    # høyst maks kropper: de minste slås sammen med naboen de deler lengst kant med
    biter = sorted(biter, key=lambda g: -g.area)
    while len(biter) > maks:
        g = biter.pop()
        k = max(range(len(biter)), key=lambda q: g.buffer(0.05).intersection(biter[q].buffer(0.05)).area)
        biter[k] = unary_union([biter[k], g]).buffer(0)
    ut = []
    for D in biter:
        a, b, c, d = D.bounds
        ut.append(dict(u0=a, u1=c, v0=b, v1=d, del_=D))
    return th, ut


def plan_kropp(k, form, langs, ender=('fri', 'fri')):
    """Planene til én kropp i lokal ramme: liste av (a, b, c) med t = a*u + b*v + c, og domenet (rektangel, lokal).
    langs: mønet går langs u (True) eller langs v. ender: per ende ('fri' eller 'inne'), i mønets retning (lav, høy)."""
    u0, u1, v0, v1 = k['u0'], k['u1'], k['v0'], k['v1']
    # i mønets ramme: s langs mønet, q på tvers
    if langs:
        s0, s1, q0, q1 = u0, u1, v0, v1
        S = lambda a, c: (a, 0.0, c); Q = lambda b, c: (0.0, b, c)
    else:
        s0, s1, q0, q1 = v0, v1, u0, u1
        S = lambda a, c: (0.0, a, c); Q = lambda b, c: (b, 0.0, c)
    w = q1 - q0; hm = w / 2
    ext = [hm if e == 'inne' else 0.0 for e in ender]
    s0e, s1e = s0 - ext[0], s1 + ext[1]
    pl = []
    if form == 'flatt':
        pl = [(0.0, 0.0, 0.0)]
    elif form == 'pult':
        pl = [Q(1.0, -q0)]
    elif form == 'pult-':
        pl = [Q(-1.0, q1)]
    else:
        pl = [Q(1.0, -q0), Q(-1.0, q1)]
        if form in ('valm', 'halvvalm'):
            løft = HALV * hm if form == 'halvvalm' else 0.0
            if ender[0] != 'inne': pl.append(S(1.0, -s0 + løft))
            if ender[1] != 'inne': pl.append(S(-1.0, s1 + løft))
    dom = (s0e, s1e, q0, q1) if langs else (q0, q1, s0e, s1e)
    return pl, box(dom[0], dom[2], dom[1], dom[3])


def _halvplan(a, b, c, B, streng=False):
    """Delen av B der a*u + b*v + c >= 0 (lokal)."""
    if abs(a) + abs(b) < 1e-12:
        return B if c >= (EPS if streng else -EPS) else Polygon()
    x0, y0, x1, y1 = B.bounds; R = 4 * (x1 - x0 + y1 - y0) + 10
    n = np.array([a, b]) / math.hypot(a, b); cc = c / math.hypot(a, b)
    p0 = -n * cc; u = np.array([-n[1], n[0]])
    q = Polygon([p0 + u * R, p0 - u * R, p0 - u * R + n * R, p0 + u * R + n * R])
    return q.intersection(B)


def tak_hus(P, spek):
    """Taket til ett hus. spek = dict(th=retning, kropper=[dict(u0,u1,v0,v1, form, langs, ender)]).
    Gir (tak2, gavl2) i modellmeter (t = avstand inn fra takfoten)."""
    th = spek['th']; K = spek['kropper']
    Lp = Polygon(til_lokal(np.array(P.exterior.coords), th), [til_lokal(np.array(r.coords), th) for r in P.interiors]).buffer(0)
    B = Lp.envelope.buffer(30)
    celler = []          # (kropp, plan, celle)
    for kk, k in enumerate(K):
        pl, dom = plan_kropp(k, k['form'], k['langs'], k.get('ender', ('fri', 'fri')))
        for j, (a, b, c) in enumerate(pl):
            C = dom
            for jj, (a2, b2, c2) in enumerate(pl):
                if jj == j: continue
                # planet j er lavest: t_jj - t_j >= 0 ; ved likhet vinner lavest indeks
                C = C.intersection(_halvplan(a2 - a, b2 - b, c2 - c, B, streng=(jj < j)))
                if C.is_empty: break
            if not C.is_empty and C.area > 1e-4:
                celler.append((kk, (a, b, c), C))
    biter = []
    for n, (kk, (a, b, c), C) in enumerate(celler):
        G = C
        for m, (kk2, (a2, b2, c2), C2) in enumerate(celler):
            if kk2 == kk or G.is_empty: continue
            ov = C2.intersection(G)
            if ov.is_empty or ov.area < 1e-5: continue
            # den andre kroppen er høyere her: t2 - t > 0 (likhet: lavest kroppsindeks vinner)
            hoy = _halvplan(a2 - a, b2 - b, c2 - c, B, streng=(kk2 > kk))
            G = G.difference(ov.intersection(hoy))
        G = G.intersection(Lp)
        for g in getattr(G, 'geoms', [G]):
            if g.geom_type == 'Polygon' and g.area > 0.02:
                biter.append((g, (a, b, c)))
    # deler av omrisset ingen kropp dekker (skal ikke skje; da flatt)
    dekket = unary_union([g for g, _ in biter]) if biter else Polygon()
    rest = Lp.difference(dekket.buffer(1e-6))
    for g in getattr(rest, 'geoms', [rest]):
        if g.geom_type == 'Polygon' and g.area > 0.05:
            biter.append((g, (0.0, 0.0, 0.0)))
    tk = lambda pl, uv: max(0.0, pl[0] * uv[0] + pl[1] * uv[1] + pl[2])
    tak2 = []
    for g, pl in biter:
        for e in _enkle(orient(g, 1.0)):
            cs = np.array(e.exterior.coords)[:-1]
            xy = fra_lokal(cs, th)
            tak2.append([[round(float(x), 2), round(float(y), 2), round(tk(pl, uv), 3)] for (x, y), uv in zip(xy, cs)])
    # gavler: hver vegg der taket står over gesims (fra bitene som berører veggen)
    gavl2 = []
    for R in [Lp.exterior] + list(Lp.interiors):
        c = np.array(R.coords)
        for k in range(len(c) - 1):
            seg = LineString([c[k], c[k + 1]])
            if seg.length < 0.05: continue
            for g, pl in biter:
                S = seg.intersection(g.buffer(1e-4))
                for s in getattr(S, 'geoms', [S]):
                    if s.geom_type != 'LineString' or s.length < 0.05: continue
                    pa, pb = np.array(s.coords[0]), np.array(s.coords[-1])
                    ta, tb = tk(pl, pa), tk(pl, pb)
                    if ta < 0.02 and tb < 0.02: continue
                    (xa, ya), (xb, yb) = fra_lokal(np.array([pa, pb]), th)
                    gavl2.append([[round(float(xa), 2), round(float(ya), 2), round(ta, 3)], [round(float(xb), 2), round(float(yb), 2), round(tb, 3)]])
    # sprang inne i taket (en kropp slutter høyere enn taket ved siden av): loddrett vegg opp til den høye kanten
    for g, pl in biter:
        for k_, (a, b) in enumerate(zip(list(g.exterior.coords)[:-1], list(g.exterior.coords)[1:])):
            seg = LineString([a, b])
            if seg.length < 0.2 or Lp.exterior.distance(seg.interpolate(0.5, normalized=True)) < 0.05: continue
            m = np.array(seg.interpolate(0.5, normalized=True).coords[0])
            n = np.array([b[1] - a[1], -(b[0] - a[0])]); n = n / (np.linalg.norm(n) + 1e-12)
            ut_ = m + n * 0.08
            if g.contains(Point(*ut_)): ut_ = m - n * 0.08
            t_inn = tk(pl, m)
            t_ut = None
            for g2, pl2 in biter:
                if g2.contains(Point(*ut_)):
                    t_ut = tk(pl2, ut_); break
            if t_ut is not None and t_inn > t_ut + 0.1:
                pa, pb = np.array(a), np.array(b)
                (xa, ya), (xb, yb) = fra_lokal(np.array([pa, pb]), th)
                gavl2.append([[round(float(xa), 2), round(float(ya), 2), round(tk(pl, pa), 3)], [round(float(xb), 2), round(float(yb), 2), round(tk(pl, pb), 3)]])
    return tak2, gavl2


def _enkle(g):
    if not g.interiors:
        return [g]
    c = g.interiors[0].centroid
    x0, y0, x1, y1 = g.bounds
    ut = []
    for half in (box(x0 - 1, y0 - 1, c.x, y1 + 1), box(c.x, y0 - 1, x1 + 1, y1 + 1)):
        G = g.intersection(half)
        for gg in getattr(G, 'geoms', [G]):
            if gg.geom_type == 'Polygon' and gg.area > 1e-3:
                ut += _enkle(orient(gg, 1.0))
    return ut


def ender_for(K, kk, langs):
    """Hvilke ender av kropp kk (i mønets retning) støter mot en annen kropp i samme hus."""
    k = K[kk]
    if langs:
        e0 = box(k['u0'] - 0.3, k['v0'] + 0.3, k['u0'] + 0.3, k['v1'] - 0.3); e1 = box(k['u1'] - 0.3, k['v0'] + 0.3, k['u1'] + 0.3, k['v1'] - 0.3)
    else:
        e0 = box(k['u0'] + 0.3, k['v0'] - 0.3, k['u1'] - 0.3, k['v0'] + 0.3); e1 = box(k['u0'] + 0.3, k['v1'] - 0.3, k['u1'] - 0.3, k['v1'] + 0.3)
    ut = []
    for e in (e0, e1):
        inne = any(e.intersection(K[j]['del_']).area > 0.3 * e.area for j in range(len(K)) if j != kk)
        ut.append('inne' if inne else 'fri')
    return tuple(ut)


# ------------------------------------------------------------------ DOM

_DOM = None
def dom():
    """(ndh, gt, SH, hent): Kartverkets DOM−DTM 1 m med forskyvningen fra rapport/hoyder/tall.json."""
    global _DOM
    if _DOM is None:
        import importlib.util
        H = os.path.join(ROT, 'rapport', 'hoyder')
        spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
        d_, gt = hent.les(os.path.join(H, 'kilder', 'dom1_25832.tif')); t_, _ = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif'))
        SH = tuple(json.load(open(os.path.join(H, 'tall.json')))['forskyvning'])
        _DOM = (d_ - t_, gt, SH, hent)
    return _DOM


def dom_punkter(G, krymp=0.5):
    """Pikselsentre (modellmeter) og DOM−DTM inne i polygonet G (modellmeter), krympet krymp m."""
    ndh, gt, SH, hent = dom()
    x0, y1, dx, dy = gt; Hh, W = ndh.shape
    I = G.buffer(-krymp) if G.buffer(-krymp).area > 3 else G
    if I.is_empty: return np.zeros((0, 2)), np.zeros(0)
    a, b, c, d = I.bounds
    xs, ys = np.meshgrid(np.arange(a, c, 0.5), np.arange(b, d, 0.5))
    pts = np.c_[xs.ravel(), ys.ravel()]
    pts = pts[shapely.contains_xy(I, pts[:, 0], pts[:, 1])]
    if not len(pts): return pts, np.zeros(0)
    U = hent.til_utm(pts) + np.array(SH)
    cc = ((U[:, 0] - x0) / dx).astype(int); rr = ((y1 - U[:, 1]) / dy).astype(int)
    ok = (rr >= 0) & (rr < Hh) & (cc >= 0) & (cc < W)
    v = np.full(len(pts), np.nan); v[ok] = ndh[rr[ok], cc[ok]]
    ok = ~np.isnan(v)
    return pts[ok], v[ok]


def t_felt(spek, kk, uv):
    """t fra kropp kk alene (nederste av planene) i lokale punkter uv."""
    k = spek['kropper'][kk]
    pl, _ = plan_kropp(k, k['form'], k['langs'], k.get('ender', ('fri', 'fri')))
    T = np.min(np.stack([a * uv[:, 0] + b * uv[:, 1] + c for a, b, c in pl]), axis=0)
    return np.maximum(T, 0)


STRAFF = dict(sal=0.0, valm=0.12, halvvalm=0.16, pult=0.35, flatt=0.05)


def tilpass_kropp(spek, kk, pts, z, tvang=None):
    """Prøv mønretning og takform for kropp kk mot DOM-punktene (lokal). Gir beste (form, langs, rms, h, th)."""
    k = spek['kropper'][kk]
    w_u, w_v = k['u1'] - k['u0'], k['v1'] - k['v0']
    best = None; alle = []
    for langs in (True, False):
        if tvang and tvang.get('langs') is not None and tvang['langs'] != langs: continue
        for form in ('sal', 'valm', 'halvvalm', 'pult', 'pult-', 'flatt'):
            f0 = form.rstrip('-')
            if tvang and tvang.get('form') and tvang['form'] != f0: continue
            if form == 'flatt' and not langs: continue
            if f0 == 'pult' and (w_v if langs else w_u) > 8.0 and not (tvang and tvang.get('form') == 'pult'): continue   # pulttak bare på smale bygg (uthus, tilbygg)
            kk_ = dict(k, form=form, langs=langs, ender=ender_for(spek['kropper'], kk, langs))
            s2 = dict(spek, kropper=[kk_ if j == kk else q for j, q in enumerate(spek['kropper'])])
            T = t_felt(s2, kk, pts)
            if form == 'flatt':
                h = float(np.median(z)); th = 0.0; r = z - h
            else:
                A = np.c_[np.ones_like(T), T]
                sol = np.linalg.lstsq(A, z, rcond=None)[0]; h, th = float(sol[0]), float(sol[1])
                th = min(max(th, 0.12), 1.6); h = float(np.median(z - th * T))
                r = z - (h + th * T)
            rms = float(np.sqrt(np.mean(np.minimum(np.abs(r), 3.0) ** 2)))
            bredde = (w_v if langs else w_u)
            lengde = (w_u if langs else w_v)
            straff = STRAFF[f0] + (0.06 if lengde < 0.8 * bredde else 0.0)   # mønet langs den korte siden: litt mindre sannsynlig
            alle.append((rms + straff, form, langs, rms, h, th))
    alle.sort()
    return alle[0] if alle else None, alle


# ------------------------------------------------------------------ hus for hus

def tegning_spek():
    if os.path.exists(TEGNING_FIL):
        return json.load(open(TEGNING_FIL, encoding='utf8')).get('hus', {})
    return {}


def spek_for(x, T=None, logg=None):
    """Spesifikasjonen (kroppene, takform, mønretning) for huset x: kilder/tak-tegning.json, ellers DOM."""
    P = Polygon(x['p']).buffer(0)
    if P.geom_type != 'Polygon':
        P = max(P.geoms, key=lambda g: g.area)
    t = (T or {}).get(x['id'], {})
    th0 = math.radians(t['retning']) if t.get('retning') is not None else None
    th, K = kropper(P, th0, maks=t.get('maks_kropper', 3))
    spek = dict(th=th, kropper=[dict(k) for k in K])
    for k in spek['kropper']:
        k['form'] = 'sal'; k['langs'] = (k['u1'] - k['u0']) >= (k['v1'] - k['v0']); k['ender'] = ('fri', 'fri')
    pts, z = dom_punkter(P)
    hvorfor = []
    for kk, k in enumerate(spek['kropper']):
        tv = (t.get('kropper') or [{}] * len(K))[kk] if kk < len(t.get('kropper') or []) else {}
        tv = dict(tv)
        if t.get('form') and not tv.get('form'): tv['form'] = t['form']
        if t.get('mone') is not None and tv.get('langs') is None and len(K) == 1:
            tv['langs'] = mone_langs(k, t['mone'], th)
        if 'langs' in tv and isinstance(tv['langs'], str):
            tv['langs'] = mone_langs(k, tv['langs'], th)
        uv_all = til_lokal(pts, th) if len(pts) else np.zeros((0, 2))
        m = shapely.contains_xy(k['del_'].buffer(-0.3) if k['del_'].buffer(-0.3).area > 2 else k['del_'], uv_all[:, 0], uv_all[:, 1]) if len(uv_all) else np.zeros(0, bool)
        if m.sum() >= 6:
            b, alle = tilpass_kropp(spek, kk, uv_all[m], z[m], tvang=tv or None)
            if b is None:
                b, alle = tilpass_kropp(spek, kk, uv_all[m], z[m])
            _, form, langs, rms, h, th_ = b
            k['form'], k['langs'] = form, langs
            k['dom'] = dict(rms=round(rms, 2), h=round(h, 2), th=round(th_, 2), n=int(m.sum()))
            hvorfor.append(('tegning+DOM' if tv else 'DOM') + f" {form} {'langs' if langs else 'tvers'} rms {rms:.2f}")
        else:
            if tv.get('form'): k['form'] = tv['form']
            if tv.get('langs') is not None: k['langs'] = tv['langs']
            hvorfor.append(('tegning' if tv else 'standard') + f" {k['form']}")
        k['ender'] = ender_for(spek['kropper'], kk, k['langs'])
    spek['kilde'] = '; '.join(hvorfor)
    return P, spek


def mone_langs(k, mone, th):
    """mone: 'lang' (langs den lange siden), 'kort', eller en kompassvinkel i grader (retningen mønet går, 0 = øst, mot klokka)."""
    lang_u = (k['u1'] - k['u0']) >= (k['v1'] - k['v0'])
    if mone == 'lang': return lang_u
    if mone == 'kort': return not lang_u
    a = math.radians(float(mone)) - th
    return abs(math.cos(a)) >= abs(math.sin(a))


def takform_navn(spek):
    fs = [k['form'].rstrip('-') for k in spek['kropper']]
    if len(fs) == 1: return fs[0]
    return 'vinkel:' + '+'.join(fs)


def kandidater(d, ret):
    """Husene i Gamlebyen som har tak regnet fra kommunekartet (grunnmur.py) og ikke er fredet."""
    fra_grunnmur = set()
    for r in ret:
        g = r.get('grunn', '')
        if g.startswith('kommunekart FKB 29.10') and (r['op'] == 'ny' or r.get('felt') in ('tak2', 'p')):
            fra_grunnmur.add(r['id'])
        if g.startswith('husdeling'):
            fra_grunnmur.add(r['id'])
    porter = {p.get('bygg_id') for p in d.get('porter', [])}
    ut = []
    for x in d['bygg']:
        if x['id'] not in fra_grunnmur or x.get('skjul') or x.get('kirke') or len(x['p']) < 3: continue   # deler (tårn) står oppå taket
        if x['id'] in porter or x['id'] == 'bnr-193867537': continue
        ut.append(x)
    return ut


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    T = tegning_spek()
    nye, logg = [], {}
    for x in kandidater(d, ret):
        try:
            P, spek = spek_for(x, T)
            tak2, gavl2 = tak_hus(P, spek)
        except Exception as e:  # noqa
            logg[x['id']] = dict(feil=str(e)); continue
        if not tak2: continue
        form = takform_navn(spek)
        r = lambda felt, v: {"emne": "bygg", "id": x['id'], "op": "sett", "felt": felt, "verdi": v, "hvem": HVEM, "dato": DATO, "grunn": GRUNN}
        nye += [r('tak2', tak2), r('gavl2', gavl2), r('sk', None)]
        if x.get('takform') != 'knekk' and not T.get(x['id'], {}).get('knekk'):
            nye.append(r('takform', form))
        else:
            nye.append(r('takform', 'knekk'))
        # vegghøyde og takhelning fra samme tilpasning (DOM p50/p90 langs takflatene); rapport/hoyder (legg_inn.py, senere i
        # kjeden) overstyrer der Kartverket-målingen er sikker, så dette gjelder husene uten sikker måling
        fit = [(k['dom']['h'], k['dom']['th'], k['dom']['n']) for k in spek['kropper'] if k.get('dom') and k['dom']['rms'] < 1.5 and k['dom']['n'] >= 15]
        pz = dom_punkter(P)[1]
        p50 = float(np.median(pz)) if len(pz) >= 10 else 0.0
        if fit and p50 >= 2.0:          # huset synes i DOM (ikke overdekket i vollen, ikke under trær alene)
            w = np.array([f[2] for f in fit], float)
            h_ = float(np.average([f[0] for f in fit], weights=w)); th_ = float(np.average([f[1] for f in fit], weights=w))
            if h_ >= 2.3:
                h_ = round(min(h_, 25.0), 2); th_ = round(min(max(th_, 0.2), 1.2), 2)
                nye += [r('h', h_)] + ([r('th', th_)] if form != 'flatt' else [])
            else:                        # tilpasningen er ikke til å stole på (naboer eller trær i pikslene): bare vegghøyden
                nye.append(r('h', round(max(2.3, p50 - 1.0), 2)))
        if T.get(x['id'], {}).get('deler'):          # tårn o.l. tegningen viser og DOM bekrefter (kilder/tak-tegning.json)
            nye.append(r('deler', [dict(dict(vegg=x.get('vegg'), tak=x.get('tak')), **d) for d in T[x['id']]['deler']]))   # husets farger
        logg[x['id']] = dict(takform=form, kilde=spek['kilde'], kropper=[dict(form=k['form'], langs=k['langs'], ender=k['ender'],
                             mål=[round(k['u1'] - k['u0'], 1), round(k['v1'] - k['v0'], 1)], dom=k.get('dom')) for k in spek['kropper']])
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
    os.makedirs(os.path.join(ROT, 'rapport', 'tak'), exist_ok=True)
    json.dump(logg, open(os.path.join(ROT, 'rapport', 'tak', 'tak.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"{len(logg)} hus fikk rent tak: " + ', '.join(f"{k} {v}" for k, v in Counter(v.get('takform', 'feil') for v in logg.values()).most_common()))


def ark(x, y, rad=40, navn=None):
    """Plan nord opp: DOM−DTM (grå), modellens takflater farget etter helningsretning, mønene svart. rapport/tak/<navn>.png."""
    import cv2
    mpp = 0.1
    x0, y0, x1, y1 = x - rad, y - rad, x + rad, y + rad
    W = H = int(2 * rad / mpp)
    xs, ys = np.meshgrid(x0 + (np.arange(W) + 0.5) * mpp, y1 - (np.arange(H) + 0.5) * mpp)
    ndh, gt, SH, hent = dom()
    U = hent.til_utm(np.stack([xs, ys], -1)) + np.array(SH)
    gx0, gy1, dx, dy = gt
    c = ((U[..., 0] - gx0) / dx).astype(int); r = ((gy1 - U[..., 1]) / dy).astype(int)
    v = ndh[np.clip(r, 0, ndh.shape[0] - 1), np.clip(c, 0, ndh.shape[1] - 1)]
    g = (np.clip(np.nan_to_num(v) / 16, 0, 1) * 255).astype(np.uint8)
    im = cv2.cvtColor(cv2.applyColorMap(g, cv2.COLORMAP_VIRIDIS), cv2.COLOR_BGR2BGR555) if False else cv2.applyColorMap(g, cv2.COLORMAP_VIRIDIS)
    mod = np.full_like(im, 255)
    px = lambda q: (int((q[0] - x0) / mpp), int((y1 - q[1]) / mpp))
    d = datalag.alle()
    for b in d['bygg']:
        if b.get('skjul') or len(b['p']) < 3: continue
        if Polygon(b['p']).distance(Point(x, y)) > rad * 1.5: continue
        F = b.get('tak2') or b.get('sk') or []
        if isinstance(F, str): F = json.loads(F)
        for f in F:
            if len(f) < 3: continue
            A = np.array([[q[0], q[1], 1] for q in f]); kz = np.linalg.lstsq(A, np.array([q[2] for q in f]), rcond=None)[0]
            ang = math.atan2(kz[1], kz[0]); lys = 0.55 + 0.45 * math.cos(ang - math.radians(135)) if abs(kz[0]) + abs(kz[1]) > 0.05 else 0.8
            col = tuple(int(c_ * lys) for c_ in (90, 110, 230))
            cv2.fillPoly(mod, [np.array([px(q) for q in f], np.int32)], col)
            cv2.polylines(mod, [np.array([px(q) for q in f], np.int32)], True, (40, 40, 40), 1)
        for panel in (im, mod):
            cv2.polylines(panel, [np.array([px(q) for q in b['p']], np.int32)], True, (0, 0, 255) if panel is im else (0, 0, 0), 2)
        cc = np.array(Polygon(b['p']).representative_point().coords[0])
        cv2.putText(mod, b['id'].replace('bnr-193', '').replace('bnr-', ''), px(cc), 0, 0.45, (0, 0, 0), 1)
    os.makedirs(os.path.join(ROT, 'rapport', 'tak'), exist_ok=True)
    f = os.path.join(ROT, 'rapport', 'tak', f"{navn or f'{x:.0f}_{y:.0f}'}.png")
    cv2.imwrite(f, np.hstack([im, mod]))
    print(f)


def fra_kontroll():
    A = json.load(open(os.path.join(ROT, 'rapport', 'kontroll', 'avvik.json'), encoding='utf8'))
    T = json.load(open(TEGNING_FIL, encoding='utf8')) if os.path.exists(TEGNING_FIL) else dict(hus={})
    hus = T.setdefault('hus', {})
    for k in [k for k, v in hus.items() if v.get('kilde') == 'kontroll']:
        del hus[k]
    n = 0
    for r in A['hus']:
        if r.get('finnes') != 'ja' or r['id'] in hus or r.get('iou', 0) < 0.4 or r.get('slaatt_sammen'):
            continue
        t = r.get('takform_tegning', '')
        if t not in ('sal', 'valm', 'halvvalm'):
            continue
        e = dict(form=t, kilde='kontroll', tegning=r['tegning'], grunn=f"tegningen {r['tegning']}: {r['takform_tegning_tegn']['gavler']} gavl(er), {r['takform_tegning_tegn']['trekantede_takflater']} trekantede takflater")
        gv = r['takform_tegning_tegn'].get('gavl_vegger') or []
        if gv:
            a, b = np.array(gv[0][0]), np.array(gv[0][1]); u = b - a
            e['mone'] = round(math.degrees(math.atan2(u[0], -u[1])) % 180, 1)     # mønet står vinkelrett på gavlveggen
        hus[r['id']] = e; n += 1
    json.dump(T, open(TEGNING_FIL, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f"{n} hus fikk takform fra tegningene (kilder/tak-tegning.json)")


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'fra_kontroll':
        fra_kontroll()
    elif a and a[0] == 'ark':
        ark(float(a[1]), float(a[2]), float(a[3]) if len(a) > 3 else 40, a[4] if len(a) > 4 else None)
    else:
        main(tørt='--tørt' in a)
