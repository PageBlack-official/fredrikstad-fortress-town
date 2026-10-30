"""Husdelingen etter tegningen (30.10): ett modellhus per hus Vegar tegnet i 2015.

Kommunekartet (FKB) er fasit for ytterkanten av en husrekke, men deler den ikke alltid slik husene står: noen rekker er
ett omriss i kartet og fire hus i tegningen, andre er to omriss der tegningen viser ett hus. Tegningen er fasit for hvor
ett hus slutter og det neste begynner langs gata; Kartverkets DOM (møner og sprang i taket) og ortofoto 2024 bekrefter.

Kilden er kilder/husdeling.json (lest av tegningen med `forslag`, sett på og godkjent for hånd, med grunn per linje):
  deling   {"id", "kutt": [[[x, y], [x, y]], ...], "tegning", "grunn"}   kuttlinjene går fra gata (fasaden) inn gjennom huset
  sammen   {"ids": [a, b, ...], "tegning", "grunn"}                       det første beholder id-en og får hele omrisset
  skjul    {"id", "grunn"}                                                  bygg som ikke står der (ortofoto 2024 + DOM)
  nye      {"id"?, "p", "h"?, "tegning", "grunn"}                          hus tegningen viser og kommunekartet mangler
Nye id-er deles ut første gang (bnr- fra et matrikkelpunkt i biten, ellers neste pb-) og skrives tilbake i fila
("nye_id"), så de er faste; de registreres i kilder/id-register.txt. En id slettes aldri.

Per deling: biten der husets matrikkelpunkt står, beholder id-en (ellers den største). Farger, matrikkelfelt og fasadekilde
følger med til de nye bitene; vinduer, piper og arker følger biten de står i (fasade_tegning.py legg_inn fordeler vinduene
fra tegningen på nytt etter hvor de står langs veggen). Taket lages etterpå av verktoy/tak_enkel.py, høyden av
rapport/hoyder. Husene legges også inn i tegningens liste i kilder/kvartal-kobling.json, så kontrollen ser dem.

    python3 verktoy/husdeling.py                     rettelser fra kilder/husdeling.json (idempotent)
    python3 verktoy/husdeling.py forslag <tegning>   fasadedelingene i tegningen lagt ned på bakken (krever kontroll-render):
                                                     rapport/tak/deling-<tegning>.json og .png (tegning | DOM med kuttene)
"""
import json, math, os, sys
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import split, unary_union

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag

FIL = os.path.join(ROT, 'kilder', 'husdeling.json')
GRUNN = 'husdeling etter tegningen'
HVEM, DATO = 'Claude', '2026-10-30'


def les():
    if not os.path.exists(FIL):
        return dict(deling=[], sammen=[], skjul=[], nye=[])
    d = json.load(open(FIL, encoding='utf8'))
    for k in ('deling', 'sammen', 'skjul', 'nye'):
        d.setdefault(k, [])
    return d


def skriv(d):
    json.dump(d, open(FIL, 'w', encoding='utf8'), ensure_ascii=False, indent=1)


def _poly(x):
    P = Polygon(x['p']).buffer(0)
    return P if P.geom_type == 'Polygon' else max(P.geoms, key=lambda g: g.area)


def _rund(P):
    from shapely.geometry.polygon import orient
    P = orient(P.simplify(0.02), 1.0)
    return [[round(float(a), 2), round(float(b), 2)] for a, b in list(P.exterior.coords)[:-1]]


def del_omriss(P, kutt):
    """P delt med kuttlinjene (hver forlenget 2 m forbi endene). Gir bitene (Polygon), største først."""
    biter = [P]
    for (a, b) in kutt:
        a, b = np.array(a, float), np.array(b, float); u = (b - a) / (np.linalg.norm(b - a) + 1e-12)
        # linja forlenges til den går ut av huset på begge sider (biten av den lange linja som inneholder kuttets midtpunkt)
        Llang = LineString([a - u * 30, b + u * 30]); m = Point(*(0.5 * (a + b)))
        L = LineString([a - u * 2.0, b + u * 2.0])
        for g in biter:
            X = Llang.intersection(g)
            for q in getattr(X, 'geoms', [X]):
                if q.geom_type == 'LineString' and q.distance(m) < 0.05:
                    c0, c1 = np.array(q.coords[0]), np.array(q.coords[-1]); w = (c1 - c0) / (np.linalg.norm(c1 - c0) + 1e-12)
                    L = LineString([c0 - w * 0.3, c1 + w * 0.3])
        ny = []
        for g in biter:
            if not g.intersects(L):
                ny.append(g); continue
            try:
                r = [q for q in split(g, L).geoms if q.area > 0.3]
            except Exception:
                r = [g]
            ny += r
        biter = ny
    return sorted(biter, key=lambda g: -g.area)


def _i(P, q, buf=0.35):
    return P.buffer(buf).contains(Point(q[0], q[1]))


def main(tørt=False):
    import grunnmur as GM
    H = les()
    ret = [r for r in datalag.les('rettelser') if not r.get('grunn', '').startswith(GRUNN)]
    # husene husdelingen selv har laget (nye_id, nye): andre verktøys linjer på dem holdes utenfor tilstanden her, men skrives tilbake
    egne = {i for D in H['deling'] for i in (D.get('nye_id') or [])} | {N['id'] for N in H['nye'] if N.get('id')}
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, [r for r in ret if r.get('id') not in egne]), grunn)
    BY = {x['id']: x for x in d['bygg']}
    reg = [l.strip() for l in open(os.path.join(ROT, 'kilder', 'id-register.txt'), encoding='utf8') if l.strip()]
    brukt = set(reg) | set(BY)
    MP = GM.matrikkelpunkter()
    def neste_pb():
        n = max(int(i[3:]) for i in brukt if i.startswith('pb-') and i[3:].isdigit()) + 1
        return f'pb-{n}'
    nye_rett, logg, nye_reg = [], [], []
    def r(id_, felt, v, g):
        nye_rett.append({"emne": "bygg", "id": id_, "op": "sett", "felt": felt, "verdi": v, "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: {g}"})
    barn_av = {}
    for D in H['deling']:
        x = BY.get(D['id'])
        if not x or x.get('skjul'):
            logg.append(f"{D['id']}: finnes ikke / skjult, deling hoppet over"); continue
        P = _poly(x)
        biter = del_omriss(P, D['kutt'])
        if len(biter) < 2:
            logg.append(f"{D['id']}: kuttene deler ikke omrisset"); continue
        # biten med husets eget matrikkelpunkt beholder id-en
        eget = [m for m in MP if f"bnr-{m['bygningsnummer']}" == D['id']]
        k0 = 0
        if eget:
            for k, g in enumerate(biter):
                if g.buffer(0.5).contains(Point(*eget[0]['xy'])): k0 = k; break
        orden = [k0] + [k for k in range(len(biter)) if k != k0]
        ider = list(D.get('nye_id') or [])
        for n_, k in enumerate(orden[1:]):
            if n_ < len(ider): continue
            g = biter[k]; ny = None
            for m in MP:
                kand = f"bnr-{m['bygningsnummer']}"
                if kand not in brukt and g.buffer(0.3).contains(Point(*m['xy'])):
                    ny = kand; break
            ny = ny or neste_pb()
            brukt.add(ny); ider.append(ny)
        D['nye_id'] = ider
        g0 = biter[k0]
        gr = D.get('grunn', '')
        r(x['id'], 'p', _rund(g0), gr); r(x['id'], 'ph', [], gr)
        rr, rf = GM.rekt(g0); r(x['id'], 'r', rr, gr); r(x['id'], 'rf', rf, gr); r(x['id'], 'tk', [rr], gr)
        for felt in ('vind', 'piper', 'arker'):
            if x.get(felt):
                v = x[felt] if not isinstance(x[felt], str) else json.loads(x[felt])
                r(x['id'], felt, [q for q in v if _i(g0, q)], gr)
        barn_av[x['id']] = []
        for n_, k in enumerate(orden[1:]):
            g = biter[k]; ny = ider[n_]
            obj = {kk: vv for kk, vv in x.items() if kk not in ('tak2', 'gavl2', 'sk', 'vind', 'piper', 'arker', 'skjul', 'navn', 'adr', 'matrikkel', 'tegnet_vegger', 'fasade_tegning', '_knekk')}
            obj.update(id=ny, p=_rund(g), ph=[], navn=None, adr=None)
            rr, rf = GM.rekt(g); obj.update(r=rr, rf=rf, tk=[rr])
            ms = [GM.mfelt(m) for m in MP if f"bnr-{m['bygningsnummer']}" == ny]
            obj['matrikkel'] = ms or None
            for felt in ('vind', 'piper', 'arker'):
                if x.get(felt):
                    v = x[felt] if not isinstance(x[felt], str) else json.loads(x[felt])
                    obj[felt] = [q for q in v if _i(g, q)]
            if obj.get('fasade_kilde') == 'kvartaltegning':
                obj['fasade_fra'] = x['id']
            nye_rett.append({"emne": "bygg", "id": ny, "op": "ny", "verdi": obj, "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: {gr} (del av {x['id']})"})
            barn_av[x['id']].append(ny)
            if ny not in reg: nye_reg.append(ny)
        logg.append(f"{x['id']}: delt i {len(biter)} ({', '.join([x['id']] + ider[:len(biter) - 1])})")
    for S in H['sammen']:
        ids = [i for i in S['ids'] if i in BY and not BY[i].get('skjul')]
        if len(ids) < 2:
            logg.append(f"sammen {S['ids']}: for få synlige"); continue
        G = unary_union([_poly(BY[i]).buffer(0.08, join_style='mitre') for i in ids]).buffer(-0.08, join_style='mitre')
        if G.geom_type != 'Polygon':
            G = max(G.geoms, key=lambda g: g.area)
        G = Polygon(G.exterior)
        keep = ids[0]; gr = S.get('grunn', '')
        r(keep, 'p', _rund(G), gr); r(keep, 'ph', [], gr)
        rr, rf = GM.rekt(G); r(keep, 'r', rr, gr); r(keep, 'rf', rf, gr); r(keep, 'tk', [rr], gr)
        for felt in ('vind', 'piper', 'arker'):
            v = []
            for i in ids:
                q = BY[i].get(felt)
                if q: v += q if not isinstance(q, str) else json.loads(q)
            if v: r(keep, felt, v, gr)
        r(keep, 'slaatt_sammen', ids[1:], gr)
        for i in ids[1:]:
            nye_rett.append({"emne": "bygg", "id": i, "op": "skjul", "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: slått sammen med {keep} ({gr})"})
        logg.append(f"sammen: {', '.join(ids)} -> {keep}")
    for S in H['skjul']:
        if S['id'] in BY:
            nye_rett.append({"emne": "bygg", "id": S['id'], "op": "skjul", "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: {S['grunn']}"})
            logg.append(f"skjult {S['id']}")
    for N in H['nye']:
        P = Polygon(N['p']).buffer(0)
        if not N.get('id'):
            ny = None
            for m in MP:
                kand = f"bnr-{m['bygningsnummer']}"
                if kand not in brukt and P.buffer(0.3).contains(Point(*m['xy'])):
                    ny = kand; break
            N['id'] = ny or neste_pb(); brukt.add(N['id'])
        rr, rf = GM.rekt(P)
        obj = dict(id=N['id'], p=_rund(P), ph=[], h=N.get('h', 4.0), th=N.get('th', 0.82), r=rr, rf=rf, tk=[rr],
                   tak=N.get('tak', GM.STANDARD_TAK), vegg=N.get('vegg', GM.STANDARD_VEGG), navn=None, type='house', adr=None, gml=1,
                   farge_kilde=N.get('farge_kilde', 'standard (nytt hus etter tegningen)'), fasade_kilde='antatt',
                   matrikkel=[GM.mfelt(m) for m in MP if f"bnr-{m['bygningsnummer']}" == N['id']] or None)
        nye_rett.append({"emne": "bygg", "id": N['id'], "op": "ny", "verdi": obj, "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: {N['grunn']}"})
        if N['id'] not in reg: nye_reg.append(N['id'])
        logg.append(f"nytt {N['id']}")
    if not tørt:
        skriv(H)
        datalag.skriv_rettelser(ret + nye_rett)
        if nye_reg:
            with open(os.path.join(ROT, 'kilder', 'id-register.txt'), 'a', encoding='utf8') as f:
                f.write(''.join(i + '\n' for i in nye_reg))
        # kontrollens husliste: nye biter står i samme tegning som huset de er delt fra
        kf = os.path.join(ROT, 'kilder', 'kvartal-kobling.json'); K = json.load(open(kf, encoding='utf8'))
        tegning_nye = {N['id']: N.get('tegning') for N in H['nye']}
        for t in K['tegninger']:
            b = t['bygg']
            for far, barn in barn_av.items():
                if far in b:
                    for c in barn:
                        if c not in b: b.append(c)
            for i, tg in tegning_nye.items():
                if tg == t['navn'] and i not in b: b.append(i)
        json.dump(K, open(kf, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f"husdeling: {len(H['deling'])} delinger, {len(H['sammen'])} sammenslåinger, {len(H['skjul'])} skjult, {len(H['nye'])} nye; {len(nye_reg)} nye id-er")
    for l in logg:
        print('  ' + l)


# ------------------------------------------------------------------ forslag fra tegningen

def forslag(navn):
    """Fasadedelingene i tegningen lagt ned på modellveggene. For hver synlig modellvegg: tegningens veggflater på den
    (tildelt etter id-bildet fra kontroll-render), sortert langs veggen; der én flate slutter og neste begynner, er det en
    husgrense i tegningen. Tegningens x-koordinat bestemmer punktet langs veggen entydig (projeksjonen har loddrett
    loddrett: x avhenger ikke av høyden)."""
    import cv2
    import kontroll as KT
    import fasade_tegning as FT
    D = datalag.alle(); BY = {x['id']: x for x in D['bygg']}
    K = KT.les_kamera(navn)
    im, rect = KT.tegning_bilde(navn, KT.R); H_, W_ = im.shape[:2]; R = KT.R
    f, idx, typ, nrm, idxa, ids = KT._les_render(navn, H_, W_)
    F, _ = FT.flater(navn)
    Lf = np.full((H_, W_), -1, np.int32)
    for j, fl in enumerate(F):
        cv2.fillPoly(Lf, [(np.array(fl['ytre'].exterior.coords) * R).round().astype(np.int32)], j)
    tild = {}
    for j, fl in enumerate(F):
        if min(fl['farge']) > 0.97 or max(fl['farge']) < 0.2 or not FT.er_vegg(fl['ytre']) or fl['ytre'].area < 25: continue
        m = Lf == j; n = int(m.sum())
        if n < 30: continue
        v = idx[m]; vals, cnt = np.unique(v[v > 0], return_counts=True)
        if len(vals) and cnt.max() >= 0.35 * n:
            tild.setdefault(ids[int(vals[np.argmax(cnt)])], []).append(j)
    ut = []
    for i, js in tild.items():
        x = BY.get(i)
        if not x: continue
        P = KT.P_hus(K, i); P2 = P[:, :2]; pts = x['p']; ccw = 1 if KT._areal(pts) > 0 else -1
        vegger = []
        for kk in range(len(pts)):
            a, b = np.array(pts[kk], float), np.array(pts[(kk + 1) % len(pts)], float); L = float(np.linalg.norm(b - a))
            if L < 2.0: continue
            nrm_ = np.array([b[1] - a[1], -(b[0] - a[0])]) * ccw / L
            if (P2 @ nrm_)[1] <= 1e-6: continue
            q = Polygon([KT.proj(P, a[0], a[1], 0), KT.proj(P, b[0], b[1], 0), KT.proj(P, b[0], b[1], x['h']), KT.proj(P, a[0], a[1], x['h'])]).buffer(0)
            vegger.append(dict(k=kk, a=a, b=b, L=L, q=q, n=-nrm_))
        pr = {}
        for j in js:
            best = None
            for w in vegger:
                ov = w['q'].intersection(F[j]['ytre']).area / max(F[j]['ytre'].area, 1e-6)
                if best is None or ov > best[0]: best = (ov, w)
            if best and best[0] > 0.3: pr.setdefault(best[1]['k'], []).append(j)
        for w in vegger:
            jl = pr.get(w['k'], [])
            if len(jl) < 2: continue
            xa = KT.proj(P, *w['a'], 0)[0]; xb = KT.proj(P, *w['b'], 0)[0]
            seg = []
            for j in sorted(jl, key=lambda j: F[j]['ytre'].bounds[0]):
                x0, _, x1, _ = F[j]['ytre'].bounds
                if seg and x0 < seg[-1][1] - 2.0:
                    seg[-1][1] = max(seg[-1][1], x1); seg[-1][2].append(j); continue
                seg.append([x0, x1, [j]])
            for s1, s2 in zip(seg, seg[1:]):
                xg = 0.5 * (s1[1] + s2[0])
                s = (xg - xa) / (xb - xa) if abs(xb - xa) > 1e-6 else -1
                if not (0.0 < s < 1.0): continue
                g = w['a'] + s * (w['b'] - w['a'])
                if min(s, 1 - s) * w['L'] < 2.0: continue
                c1 = max(s1[2], key=lambda j: F[j]['ytre'].area); c2 = max(s2[2], key=lambda j: F[j]['ytre'].area)
                fa, fb = [int(round(c * 255)) for c in F[c1]['farge']], [int(round(c * 255)) for c in F[c2]['farge']]
                # kuttet går fra veggen rett inn til det går ut av huset (første gang)
                Pm = _poly(x); inn = LineString([g - w['n'] * 0.3, g + w['n'] * 60])
                X = inn.intersection(Pm.boundary)
                dist = sorted([inn.project(p) for p in getattr(X, 'geoms', [X]) if p.geom_type == 'Point' and inn.project(p) > 1.0])
                ende = g + w['n'] * ((dist[0] - 0.3) if dist else 12)
                ut.append(dict(id=i, vegg=w['k'], s=round(float(s), 3), punkt=[round(float(g[0]), 2), round(float(g[1]), 2)],
                               kutt=[[round(float(g[0] - w['n'][0] * 0.3), 2), round(float(g[1] - w['n'][1] * 0.3), 2)], [round(float(ende[0]), 2), round(float(ende[1]), 2)]],
                               x_tegning=round(float(xg), 1), farger=[fa, fb], dE=round(float(KT.dE(fa, fb)), 1)))
    os.makedirs(os.path.join(ROT, 'rapport', 'tak'), exist_ok=True)
    json.dump(ut, open(os.path.join(ROT, 'rapport', 'tak', f'deling-{navn}.json'), 'w'), indent=1)
    # arket: tegningen med grensene | DOM med kuttene
    A = im.copy()
    for n_, c in enumerate(ut):
        xx = int(c['x_tegning'] * R)
        cv2.line(A, (xx, 0), (xx, H_ - 1), (0, 0, 255), 1)
        cv2.putText(A, str(n_), (xx + 2, 30 + 18 * (n_ % 8)), 0, 0.6, (0, 0, 255), 2)
    import tak_enkel as TE
    xs = [q for c in ut for q in (c['kutt'][0][0], c['kutt'][1][0])] or [0]; ys = [q for c in ut for q in (c['kutt'][0][1], c['kutt'][1][1])] or [0]
    bb = [Polygon(BY[i]['p']).bounds for i in K['bygg'] if i in BY]
    x0 = min(b[0] for b in bb) - 5; x1 = max(b[2] for b in bb) + 5; y0 = min(b[1] for b in bb) - 5; y1 = max(b[3] for b in bb) + 5
    mpp = 0.1; Wd, Hd = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    gx, gy = np.meshgrid(x0 + (np.arange(Wd) + 0.5) * mpp, y1 - (np.arange(Hd) + 0.5) * mpp)
    ndh, gt, SH, hent = TE.dom(); U = hent.til_utm(np.stack([gx, gy], -1)) + np.array(SH)
    cc = ((U[..., 0] - gt[0]) / gt[2]).astype(int); rr = ((gt[1] - U[..., 1]) / gt[3]).astype(int)
    v = ndh[np.clip(rr, 0, ndh.shape[0] - 1), np.clip(cc, 0, ndh.shape[1] - 1)]
    B = cv2.applyColorMap((np.clip(np.nan_to_num(v) / 16, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    pxx = lambda q: (int((q[0] - x0) / mpp), int((y1 - q[1]) / mpp))
    for i in K['bygg']:
        if i not in BY or BY[i].get('skjul'): continue
        cv2.polylines(B, [np.array([pxx(q) for q in BY[i]['p']], np.int32)], True, (255, 255, 255), 2)
        cv2.putText(B, KT.kort_id(i), pxx(Polygon(BY[i]['p']).representative_point().coords[0]), 0, 0.5, (255, 255, 255), 1)
    for n_, c in enumerate(ut):
        cv2.line(B, pxx(c['kutt'][0]), pxx(c['kutt'][1]), (0, 0, 255), 3)
        cv2.putText(B, str(n_), pxx(c['kutt'][0]), 0, 0.8, (0, 0, 255), 2)
    s = A.shape[0] / B.shape[0]
    B = cv2.resize(B, (int(B.shape[1] * s), A.shape[0]))
    cv2.imwrite(os.path.join(ROT, 'rapport', 'tak', f'deling-{navn}.png'), np.hstack([A[:, :, ::-1], B]))
    for n_, c in enumerate(ut):
        print(n_, c['id'], 'vegg', c['vegg'], 's', c['s'], 'dE', c['dE'], c['kutt'])




# ------------------------------------------------------------------ fasadelinjene: tegningen mot modellen langs gata

def linjer(navn, vis=True):
    """Hver synlig fasadelinje (modellvegger på rett linje i flere hus) med modellens husgrenser og tegningens veggflater
    målt i meter langs linja. Tegningens flate hører til linja når bunnkanten ligger på veggens bunnlinje i tegningen
    (innen 5 pt) og flaten dekker veggen. Gir [dict(a, u, modell=[(id, s0, s1)], tegning=[(s0, s1, farge, flater)])]."""
    import kontroll as KT
    import fasade_tegning as FT
    D = datalag.alle(); BY = {x['id']: x for x in D['bygg']}
    K = KT.les_kamera(navn)
    F, _ = FT.flater(navn)
    vegger = []
    for i in K['bygg']:
        x = BY.get(i)
        if not x or x.get('skjul'): continue
        P = KT.P_hus(K, i); P2 = P[:, :2]; pts = x['p']; ccw = 1 if KT._areal(pts) > 0 else -1
        for kk in range(len(pts)):
            a, b = np.array(pts[kk], float), np.array(pts[(kk + 1) % len(pts)], float); L = float(np.linalg.norm(b - a))
            if L < 1.0: continue
            nrm_ = np.array([b[1] - a[1], -(b[0] - a[0])]) * ccw / L
            if (P2 @ nrm_)[1] <= 1e-6: continue
            vegger.append(dict(id=i, k=kk, a=a, b=b, L=L, u=(b - a) / L, n=nrm_, P=P, h=x['h']))
    # linjer: vegger på samme rette linje (innen 6° og 1,2 m), som henger sammen (glipp under 2 m)
    brukt = [False] * len(vegger); L_ = []
    for s, w in enumerate(vegger):
        if brukt[s]: continue
        grp = [w]; brukt[s] = True; endret = True
        while endret:
            endret = False
            for t, v in enumerate(vegger):
                if brukt[t]: continue
                for g in grp:
                    if abs(v['u'] @ g['n']) < 0.1 and v['n'] @ g['n'] > 0.9 and abs((v['a'] - g['a']) @ g['n']) < 1.2:
                        sa = sorted([(v['a'] - g['a']) @ g['u'], (v['b'] - g['a']) @ g['u']]); sg = [0, g['L']]
                        if sa[0] < sg[1] + 2.0 and sa[1] > sg[0] - 2.0:
                            grp.append(v); brukt[t] = True; endret = True; break
        a0 = grp[0]['a']; u = grp[0]['u']
        if u @ np.array([1.0, 0.0]) < 0 and abs(u[0]) > 0.3: u = -u
        mod = []
        for g in grp:
            s0, s1 = sorted([(g['a'] - a0) @ u, (g['b'] - a0) @ u]); mod.append([g['id'], round(float(s0), 2), round(float(s1), 2), g['k']])
        smin = min(m[1] for m in mod); a0 = a0 + u * smin
        for m in mod: m[1] = round(m[1] - smin, 2); m[2] = round(m[2] - smin, 2)
        L_.append(dict(a=a0, u=u, n=grp[0]['n'], vegger=grp, modell=sorted(mod, key=lambda m: m[1])))
    # tegningens veggflater på linjene
    for ln in L_:
        ln['tegning'] = []
    for j, fl in enumerate(F):
        if min(fl['farge']) > 0.97 or max(fl['farge']) < 0.2 or fl['ytre'].area < 30 or not FT.er_vegg(fl['ytre']): continue
        Pf = fl['ytre']; x0, y0, x1, y1 = Pf.bounds; xm = 0.5 * (x0 + x1)
        best = None
        for li, ln in enumerate(L_):
            for g in ln['vegger']:
                P = g['P']
                xa, ya = KT.proj(P, *g['a'], 0); xb, yb = KT.proj(P, *g['b'], 0)
                lo, hi = min(xa, xb), max(xa, xb)
                ov = min(hi, x1) - max(lo, x0)
                if ov < 0.5 * (x1 - x0) and ov < 6: continue
                xc = min(max(xm, lo), hi)
                yb_ = ya + (yb - ya) * ((xc - xa) / (xb - xa) if abs(xb - xa) > 1e-6 else 0)
                # bunnkanten til flaten ved xc
                g_ = Pf.intersection(LineString([(xc, -1e4), (xc, 1e4)]))
                if g_.is_empty: continue
                bunn = g_.bounds[3]
                d = abs(bunn - yb_)
                if d < 5 and (best is None or d < best[0]):
                    best = (d, li, g)
        if best is None: continue
        _, li, g = best; ln = L_[li]; P = g['P']
        # x -> s langs linja: x = P0 . (a + s u) + P0[3]
        s_ = lambda xx: (xx - (P[0, 0] * ln['a'][0] + P[0, 1] * ln['a'][1] + P[0, 3])) / (P[0, 0] * ln['u'][0] + P[0, 1] * ln['u'][1])
        sa, sb = sorted([s_(x0), s_(x1)])
        ln['tegning'].append([round(float(sa), 2), round(float(sb), 2), [int(round(c * 255)) for c in fl['farge']], j, round(Pf.area)])
    for ln in L_:
        T = sorted(ln['tegning'])
        seg = []
        for t in T:
            if seg and t[0] < seg[-1][1] - 0.6:
                seg[-1][1] = max(seg[-1][1], t[1]); seg[-1][3].append(t[3])
                if t[4] > seg[-1][4]: seg[-1][2] = t[2]; seg[-1][4] = t[4]
                continue
            seg.append([t[0], t[1], t[2], [t[3]], t[4]])
        ln['seg'] = seg
    if vis:
        for li, ln in enumerate(L_):
            if not ln['seg']: continue
            print(f"linje {li}: start {ln['a'].round(2).tolist()} retning {ln['u'].round(3).tolist()} lengde {max(m[2] for m in ln['modell']):.1f}")
            print('   modell : ' + ' | '.join(f"{KT.kort_id(m[0])} v{m[3]} {m[1]:.1f}-{m[2]:.1f}" for m in ln['modell']))
            print('   tegning: ' + ' | '.join(f"{s[0]:.1f}-{s[1]:.1f} {tuple(s[2])} f{s[3]}" for s in ln['seg']))
    return L_


def sprang(navn=None, ids=None, terskel=1.0, vis=True):
    """Sprang i mønet (Kartverkets DOM): for hver kropp med møne over 9 m (verktoy/tak_enkel.py) måles DOM−DTM langs mønet
    (median over ±1 m på tvers, hver 0,5 m). Et sprang på minst `terskel` m som står i minst 2 m på begge sider, er en
    husgrense i taket. Med navn: bare husene i tegningen, og tegningens fasadegrenser (linjer()) innen 3 m sies fra om."""
    import tak_enkel as TE
    D = datalag.alle(); BY = {x['id']: x for x in D['bygg']}
    if navn:
        K = json.load(open(os.path.join(ROT, 'kilder', 'kvartal-kobling.json')))
        ids = next(t for t in K['tegninger'] if t['navn'] == navn)['bygg']
    T = TE.tegning_spek()
    grenser = []
    if navn:
        try:
            for ln in linjer(navn, vis=False):
                for s in ln['seg']:
                    for q in (s[0], s[1]):
                        grenser.append(ln['a'] + ln['u'] * q)
        except Exception as e:  # noqa
            print('linjer:', e)
    ut = []
    for i in ids:
        x = BY.get(i)
        if not x or x.get('skjul') or len(x['p']) < 3: continue
        P, spek = TE.spek_for(x, T)
        th = spek['th']
        for k in spek['kropper']:
            if k['form'] in ('flatt',): continue
            if k['langs']:
                s0, s1 = k['u0'], k['u1']; qm = 0.5 * (k['v0'] + k['v1'])
                pnt = lambda s, q, qm=qm, th=th: TE.fra_lokal(np.array([[s, qm + q]]), th)[0]
            else:
                s0, s1 = k['v0'], k['v1']; qm = 0.5 * (k['u0'] + k['u1'])
                pnt = lambda s, q, qm=qm, th=th: TE.fra_lokal(np.array([[qm + q, s]]), th)[0]
            if s1 - s0 < 9: continue
            ss = np.arange(s0 + 0.5, s1 - 0.4, 0.5)
            z = []
            for s in ss:
                pts = np.array([pnt(s, q) for q in (-1.0, -0.5, 0, 0.5, 1.0)])
                ndh, gt, SH, hent = TE.dom()
                U = hent.til_utm(pts) + np.array(SH)
                c = ((U[:, 0] - gt[0]) / gt[2]).astype(int); r = ((gt[1] - U[:, 1]) / gt[3]).astype(int)
                z.append(float(np.nanmedian(ndh[r, c])))
            z = np.array(z)
            for j in range(4, len(ss) - 4):
                a_, b_ = np.median(z[max(0, j - 6):j]), np.median(z[j:j + 6])
                if abs(a_ - b_) >= terskel and min(np.ptp(z[max(0, j - 4):j]), np.ptp(z[j:j + 4])) < terskel * 0.8:
                    if ut and ut[-1]['id'] == i and abs(ut[-1]['s'] - ss[j]) < 2.0:
                        if abs(a_ - b_) > ut[-1]['sprang']:
                            ut[-1].update(s=float(ss[j]), sprang=round(float(abs(a_ - b_)), 2))
                        continue
                    ut.append(dict(id=i, s=float(ss[j]), sprang=round(float(abs(a_ - b_)), 2), kropp=k, th=th, pnt=pnt))
    res = []
    for c in ut:
        k = c['kropp']; w = (k['v1'] - k['v0']) if k['langs'] else (k['u1'] - k['u0'])
        a = c['pnt'](c['s'], -w / 2 - 1.0); b = c['pnt'](c['s'], w / 2 + 1.0)
        m = c['pnt'](c['s'], 0)
        d = min([float(np.linalg.norm(np.array(g) - m)) for g in grenser] or [99])
        res.append(dict(id=c['id'], sprang=c['sprang'], kutt=[[round(float(a[0]), 2), round(float(a[1]), 2)], [round(float(b[0]), 2), round(float(b[1]), 2)]],
                        tegningsgrense_m=round(d, 1)))
        if vis:
            print(f"{c['id']}: sprang {c['sprang']} m, kutt {res[-1]['kutt']}, nærmeste fasadegrense i tegningen {d:.1f} m")
    return res


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'forslag':
        for n in a[1:]:
            forslag(n)
    elif a and a[0] == 'sprang':
        for n in a[1:]:
            sprang(n)
    elif a and a[0] == 'linjer':
        for n in a[1:]:
            linjer(n)
    else:
        main(tørt='--tørt' in a)
