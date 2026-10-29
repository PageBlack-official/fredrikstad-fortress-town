"""Kommunekartet (Fredrikstad kommunes kartportal, FKB-bygningene) som omriss i modellmeter.

Kilde: kilder/kommunekart/kommunekart.pdf, lastet ned av Vegar fra kommunens kartportal 29.10.2026. Husene er de grå
vektorflatene (fyll 0,61 grå). Kartet brukes som mål for vår egen modellering (som å tegne av et flyfoto), ikke vist i kartet.
Transformasjonen PDF -> modell (målestokk, forskyvning, rotasjon 1,65° = meridiankonvergens, teoretisk 1,67°) står i
kilder/kommunekart/pdf_til_modell.json; den ble tilpasset mot modellens omriss (IoU 0,77 samlet, median 0,92 per hus).

    from kommunekart import omriss, dekning
    K = omriss()      # liste med shapely-polygoner (x øst, y nord, meter)
"""
import json, os
import shapely
import shapely.affinity as A
from shapely.geometry import Polygon, box

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPE = os.path.join(ROT, 'kilder', 'kommunekart')
PDF = os.path.join(MAPPE, 'kommunekart.pdf')
GRAA = 0.61


def _transform():
    return json.load(open(os.path.join(MAPPE, 'pdf_til_modell.json')))


def _til_modell(P, T):
    P = A.affine_transform(P, [T['S'], 0, 0, -T['S'], T['tx'], T['ty']])
    return A.rotate(P, T['rot'], origin=(T['cx'], T['cy']))


def _delstier(items):
    """Linjestykkene i en tegning delt i lukkede delstier (ny delsti der et stykke ikke starter der forrige sluttet)."""
    stier, cur, prev = [], [], None
    for it in items:
        if it[0] != 'l':
            continue
        a, b = (it[1].x, it[1].y), (it[2].x, it[2].y)
        if prev is not None and (abs(a[0] - prev[0]) > 1e-3 or abs(a[1] - prev[1]) > 1e-3):
            stier.append(cur); cur = []
        if not cur:
            cur.append(a)
        cur.append(b); prev = b
    if cur:
        stier.append(cur)
    return [s for s in stier if len(s) >= 4]


def omriss(pdf=PDF):
    """Kommunens husomriss i modellmeter. Delstier i samme tegning gir hull (gårdsrom) etter partallsregelen."""
    import pymupdf
    if not os.path.exists(pdf):
        raise SystemExit(f'mangler {pdf} (Vegars nedlasting fra kommunens kartportal; ligger bare lokalt)')
    T = _transform(); side = pymupdf.open(pdf)[0]; ut = []
    for x in side.get_drawings():
        f = x.get('fill')
        if not (f and all(abs(c - GRAA) < 0.02 for c in f)):
            continue
        ringer = [Polygon(s).buffer(0) for s in _delstier(x['items'])]
        ringer = sorted([r for r in ringer if r.area > 0.05], key=lambda r: -r.area)
        if not ringer:
            continue
        P = ringer[0]
        for r in ringer[1:]:
            P = P.difference(r) if P.contains(r) else P.union(r)
        P = shapely.make_valid(P).buffer(0)
        for g in getattr(P, 'geoms', [P]):
            if g.geom_type == 'Polygon' and g.area > 2:
                g = _til_modell(g, T)
                ut.append(g if g.is_valid else g.buffer(0))
    # samme hus kan stå to ganger i PDF-en (to kartlag oppå hverandre): behold ett
    tre = shapely.STRtree(ut); bort = set()
    for i, k in enumerate(ut):
        if i in bort:
            continue
        for j in tre.query(k):
            j = int(j)
            if j > i and j not in bort and k.intersection(ut[j]).area > 0.9 * k.union(ut[j]).area:
                bort.add(j)
    ut = [k for i, k in enumerate(ut) if i not in bort]
    return _bygningsdeler(ut)


def _matrikkelpunkter():
    import sys
    if ROT not in sys.path:
        sys.path.insert(0, ROT)
    import datalag
    from shapely.geometry import Point
    k = json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json'), encoding='utf8'))
    return [(p['bygningsnummer'], Point(datalag.til_modell(*p['lonlat']))) for p in k['punkter']
            if p['status'] not in ('RA', 'GR', 'BR', 'BF')]


def _bygningsdeler(ut):
    """Flater som ligger inni en større flate (minst 90 %), er en del av samme bygning i kartet (tårn, fløy med annen
    høyde). Står det et matrikkelpunkt i delen og et annet i resten av den store flaten, er det to bygninger: den store blir
    resten (stor minus del). Ellers er delen bare en bygningsdel og tas bort; bygningen er den store flaten."""
    pkt = _matrikkelpunkter()
    tre = shapely.STRtree(ut); bort = set(); ny = {}
    orden = sorted(range(len(ut)), key=lambda i: ut[i].area)
    for i in orden:
        k = ut[i]
        for j in tre.query(k):
            j = int(j)
            if j == i or j in bort or ut[j].area <= k.area:
                continue
            if k.intersection(ut[j]).area < 0.9 * k.area:
                continue
            stor = ny.get(j, ut[j])
            i_del = {n for n, q in pkt if k.buffer(0.3).contains(q)}
            resten = stor.difference(k.buffer(0.02))
            i_rest = {n for n, q in pkt if resten.contains(q)} - i_del
            if i_del and i_rest:
                ps = [g for g in getattr(resten, 'geoms', [resten]) if g.geom_type == 'Polygon']
                if ps:
                    ny[j] = max(ps, key=lambda g: g.area)
            else:
                bort.add(i)
            break
    return [ny.get(i, k) for i, k in enumerate(ut) if i not in bort]


def dekning(kant=0.0):
    """Området kartet dekker, i modellmeter: kartrammen (den største hvite flaten mindre enn siden; utenfor står topptekst
    og bunntekst). Hus utenfor rammen har ingen kommunedata."""
    import pymupdf
    side = pymupdf.open(PDF)[0]; S = side.rect; best = None
    for x in side.get_drawings():
        r = x['rect']; f = x.get('fill')
        if f and all(v > 0.97 for v in f) and r.width * r.height < 0.98 * S.width * S.height:
            if best is None or r.width * r.height > best.width * best.height:
                best = r
    r = best or S
    return _til_modell(box(r.x0, r.y0, r.x1, r.y1), _transform()).buffer(-kant)


def i_gamlebyen(K, dek=None):
    """Indeksene til kommunehusene som hører til Gamlebyen: festningsbyen innenfor vollene (konveks hylle av husene der
    + 30 m, så husene på vollene er med) og 12 m rundt alle gml-hus; bare hus som ligger helt innenfor kartrammen (0,3 m
    margin), for et hus rammen kutter, er ikke målt helt. Området regnes fra grunndataene
    (data/bygg.json, ikke rettelsene), så det ikke flytter seg når omrissene rettes."""
    import sys
    from shapely.ops import unary_union
    if ROT not in sys.path:
        sys.path.insert(0, ROT)
    import datalag
    dek = dek if dek is not None else dekning()
    ps = []
    for x in datalag.alle(raa=True)['bygg']:
        if x.get('gml') and len(x['p']) >= 3:
            P = Polygon(x['p']); ps.append(P if P.is_valid else P.buffer(0))
    indre = [P for P in ps if -260 < P.centroid.x < 290 and -270 < P.centroid.y < 320]
    R = unary_union(indre).convex_hull.buffer(30).union(unary_union(ps).buffer(12))
    ut = []
    for j, k in enumerate(K):
        c = k.representative_point()
        if dek.buffer(-0.3).contains(k) and R.contains(c):
            ut.append(j)
    return ut
