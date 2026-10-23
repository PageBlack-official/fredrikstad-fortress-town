"""Del A: hus med kobling til kvartaltegning. Vegg- og takflater hentes som polygoner fra tegningen,
legges på 2019-JPG-en (tegning-pt -> trykk-pt -> trykk-px -> 2019-px) og fargen leses der.
Resultat: _farger2019/kvartal.json  {bygg: {vegger:[...], tak:[...]}}"""
import sys, os, glob, json, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from felles2019 import *
from shapely.geometry import Polygon

im = last_2019()
UT = {}
navn_liste = [os.path.basename(f)[8:-5] for f in sorted(glob.glob(os.path.join(ROT, 'kvartal/ut/kobling-*.json')))]
PL = plassering()


def poly_pt(o):
    pts = o['p']
    if len(pts) < 3:
        x0, y0, x1, y1 = o['b']
        return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    pg = Polygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)
    return pg


def innenfor(o, V, tol=1.0):
    """Flater som stikker ut av arket er avkuttede nabohus (kantstykker) og hoppes over."""
    x0, y0, x1, y1 = o['b']
    return x0 >= -tol and y0 >= -tol and x1 <= V['w'] + tol and y1 <= V['h'] + tol


def farge_2019(navn, pg_pt):
    """Dominerende 2019-farge i tegningspolygonet (pt). Returnerer (farge, andel, antall_px)."""
    geoms = [pg_pt] if pg_pt.geom_type == 'Polygon' else list(pg_pt.geoms)
    alle = []
    for g in geoms:
        p19 = kvartal_poly_2019(navn, list(g.exterior.coords))
        pix, n = median_i_polygon(im, p19, inn=1.2)
        if pix is not None:
            alle.append(pix)
    if not alle:
        return None, 0.0, 0
    pix = np.concatenate(alle)
    col, andel = dominant(pix)
    return col, andel, len(pix)


for navn in navn_liste:
    if navn not in PL:
        continue
    K = json.load(open(os.path.join(ROT, 'kvartal/ut/kobling-%s.json' % navn)))
    F = json.load(open(os.path.join(ROT, 'kvartal/ut/%s.json' % navn)))
    V = json.load(open(os.path.join(ROT, 'kvartal/vek/%s.json' % navn)))
    fas = {f['id']: f for f in F['fasader']}
    objs = V['o']
    tak_flater = [(f['id'], poly_pt(objs[f['id']])) for f in F['fasader'] if f['typ'] == 'tak']
    tak_flater = [(i, p) for i, p in tak_flater if not p.is_empty and p.area > 60 and innenfor(objs[i], V)]
    for c in K['koblinger']:
        if c.get('bygg') is None:
            continue
        bi = c['bygg']
        f = fas.get(c['fasade'])
        if f is None:
            continue
        ids = f.get('etasjeflater', [f['id']])
        if not all(innenfor(objs[i], V) for i in ids):
            continue
        W = None
        for i in ids:
            p = poly_pt(objs[i])
            W = p if W is None else W.union(p)
        if W is None or W.is_empty:
            continue
        col, andel, n = farge_2019(navn, W)
        (x0, y0), (x1, y1) = f['base']
        helning = 'h' if (y1 - y0) * (x1 - x0) > 0 else 'v'   # bildekoordinater: y ned. 'h': base faller mot høyre
        rec = UT.setdefault(str(bi), {'vegger': [], 'tak': []})
        rec['vegger'].append({'kvartal': navn, 'fasade': f['id'], 'farge2019': col, 'andel': round(andel, 2), 'px': n, 'cmyk': f['farge'],
                              'retning': helning, 'areal_pt': round(W.area, 1), 'mot_betrakter': c.get('side') is not None})
        # takflater som grenser til veggens overkant
        Wb = W.buffer(1.6)
        topp = W.bounds[1]
        for ti, R in tak_flater:
            if R.centroid.y > W.centroid.y:      # under veggen -> ikke taket
                continue
            try:
                felles = Wb.intersection(R).area
            except Exception:
                continue
            if felles < 4.0:
                continue
            if any(t['flate'] == ti and t['kvartal'] == navn for t in rec['tak']):
                continue
            rc, randel, rn = farge_2019(navn, R)
            rec['tak'].append({'kvartal': navn, 'flate': ti, 'farge2019': rc, 'andel': round(randel, 2), 'px': rn, 'cmyk': fas[ti]['farge'],
                               'areal_pt': round(R.area, 1), 'kontakt': round(felles, 1), 'vegg': f['id']})

json.dump(UT, open(os.path.join(ROT, 'soc/rapport/_farger2019/kvartal.json'), 'w'), ensure_ascii=False, indent=1)
print('bygg med kvartaldata', len(UT), 'med vegg', sum(1 for r in UT.values() if r['vegger']), 'med tak', sum(1 for r in UT.values() if r['tak']))
