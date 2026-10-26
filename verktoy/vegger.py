"""Veggene på et hus og hva de vender mot: gate, gårdsrom, nabohus (felles vegg / brannmur) eller ingenting.
Brukes av verktoy/vinduer_regler.py (lager vinduer), rapport/vinduer/mal_tegningene.py (måler fasit) og regel 17 (sjekker),
så alle tre mener det samme med «gatesiden» og «felles vegg».

Gater: data/veier.json (OSM, modellmeter). Gårdsrom: data/gardsrom.json. Nabohus: data/bygg.json (synlige bygg)."""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.strtree import STRtree

GATETYPER = {'primary', 'secondary', 'tertiary', 'residential', 'pedestrian', 'living_street', 'unclassified', 'service'}
STITYPER = {'footway', 'cycleway', 'path', 'steps'}
FELLES = 0.6        # kanten er felles vegg når nabohuset står innenfor 0,6 m langs minst halve lengden
SIKT = 40.0         # så langt ut fra veggen vi leter etter gate


def _linjer(veier, typer):
    return [LineString(v['p']) for v in veier if len(v['p']) >= 2 and v['t'].get('highway') in typer]


class Omgivelser:
    """Alt et hus kan vende mot, med romlige indekser (tåler hele byen, ikke bare Gamlebyen)."""

    def __init__(self, bygg, veier, gardsrom):
        self.poly = {}
        for x in bygg:
            if x.get('skjul') or len(x['p']) < 3:
                continue
            p = Polygon(x['p'])
            self.poly[x['id']] = p if p.is_valid else p.buffer(0)
        self.ids = list(self.poly)
        self.tre = STRtree([self.poly[i] for i in self.ids])
        self.gater = _linjer(veier, GATETYPER); self.gtre = STRtree(self.gater)
        self.stier = _linjer(veier, STITYPER); self.stre = STRtree(self.stier)
        self.gard = [Polygon(g['p']).buffer(0) for g in gardsrom if len(g['p']) >= 3]; self.gartre = STRtree(self.gard)

    def nabo(self, egen, q):
        """Står et annet hus i punktet q?"""
        pt = Point(q)
        for j in self.tre.query(pt):
            if self.ids[j] != egen and self.poly[self.ids[j]].contains(pt):
                return True
        return False

    def treff(self, egen, a, b):
        """Avstand fra a til første nabohus langs strålen a->b (None om ingen)."""
        s = LineString([a, b]); best = None
        for j in self.tre.query(s):
            if self.ids[j] == egen:
                continue
            g = self.poly[self.ids[j]].intersection(s)
            if not g.is_empty:
                d = Point(a).distance(g)
                best = d if best is None else min(best, d)
        return best

    @staticmethod
    def _foerste(tre, linjer, a, b):
        s = LineString([a, b]); best = None
        for j in tre.query(s):
            g = linjer[j].intersection(s)
            if not g.is_empty:
                d = Point(a).distance(g)
                best = d if best is None else min(best, d)
        return best

    def gate(self, a, b): return self._foerste(self.gtre, self.gater, a, b)
    def sti(self, a, b): return self._foerste(self.stre, self.stier, a, b)

    def i_gardsrom(self, q):
        pt = Point(q)
        return any(self.gard[j].contains(pt) for j in self.gartre.query(pt))


def _kanter(P, minste, slaa_sammen):
    """Kantene i polygonet som (k, a, c). slaa_sammen: kanter som fortsetter rett fram (under 8 graders knekk) blir én vegg."""
    m = len(P); ks = []
    for k in range(m):
        a, c = P[k], P[(k + 1) % m]
        if np.linalg.norm(c - a) >= 1e-6:
            ks.append([k, a.copy(), c.copy()])
    if not slaa_sammen or len(ks) < 4:
        return [q for q in ks if np.linalg.norm(q[2] - q[1]) >= minste]
    def rett(p, q):
        u = p[2] - p[1]; v = q[2] - q[1]
        return abs(math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u @ v))) < 8
    ut = []
    for q in ks:
        if ut and rett(ut[-1], q):
            ut[-1][2] = q[2]
        else:
            ut.append(q)
    if len(ut) > 1 and rett(ut[-1], ut[0]):
        ut[0][1] = ut[-1][1]; ut[0][0] = ut[-1][0]; ut.pop()
    return [q for q in ut if np.linalg.norm(q[2] - q[1]) >= minste]


def vegger(x, omg, minste=0.3, slaa_sammen=False):
    """Veggene på huset x, med retning, utovernormal og hva veggen vender mot.
    Hver vegg: k (kantnummer i x['p'] der veggen starter), a, c, u (enhetsvektor langs), n (utover), L,
    felles (andel med nabohus inntil), fri (liste av [t0, t1] langs veggen uten nabohus inntil),
    gate (m til gate rett ut, None), sti, bygg (m til nærmeste hus rett ut), gardsrom (vender mot gårdsrom)."""
    P = np.array(x['p'], float); ut = []
    pg = omg.poly.get(x['id']) or Polygon(P).buffer(0)
    for k, a, c in _kanter(P, minste, slaa_sammen):
        d = c - a; L = float(np.linalg.norm(d))
        u = d / L; n = np.array([-u[1], u[0]])
        mid = (a + c) / 2
        if pg.contains(Point(mid + n * 0.25)):
            n = -n
        ts = np.linspace(0.1, 0.9, 9)
        felles = sum(omg.nabo(x['id'], a + d * t + n * FELLES) for t in ts) / len(ts)
        # fri strekning: prøver hver 0,2 m (også rett ved hjørnene), sammenhengende biter uten nabohus inntil
        steg = max(2, int(L / 0.2)); fri, start = [], None
        for j in range(steg + 1):
            s = L * j / steg; ledig = not omg.nabo(x['id'], a + u * min(max(s, 0.05), L - 0.05) + n * FELLES)
            if ledig and start is None: start = s
            if not ledig and start is not None: fri.append([start, s]); start = None
        if start is not None: fri.append([start, L])
        gs, ss, bs, gr = [], [], [], 0
        for t in (0.25, 0.5, 0.75):
            q0 = a + d * t + n * 0.3; q1 = q0 + n * SIKT
            db = omg.treff(x['id'], q0, q1); dg = omg.gate(q0, q1); dst = omg.sti(q0, q1)
            bs.append(db if db is not None else SIKT)
            gs.append(dg if dg is not None and (db is None or dg < db) else None)
            ss.append(dst if dst is not None and (db is None or dst < db) else None)
            gr += omg.i_gardsrom(q0 + n * 2.0)
        g = [v for v in gs if v is not None]; s = [v for v in ss if v is not None]
        ut.append(dict(k=k, a=a, c=c, u=u, n=n, L=L, felles=felles, fri=fri,
                       gate=(float(np.median(g)) if len(g) >= 2 else None),
                       sti=(float(np.median(s)) if len(s) >= 2 else None),
                       bygg=float(np.median(bs)), gardsrom=gr >= 2))
    return ut


def gatesiden(V):
    """Veggen huset vender mot gata: fri vegg med kortest vei til gate rett ut (lik avstand: den lengste).
    Står ingen vegg mot gate, brukes sti, og deretter den mest åpne veggen. Gir (vegg-indeks i V, hvordan den ble valgt)."""
    fri = [i for i, v in enumerate(V) if v['felles'] < 0.5 and v['L'] >= 2.0]
    if not fri:
        return None, 'ingen fri vegg'
    for felt, hvordan in (('gate', 'gate'), ('sti', 'sti')):
        kand = [i for i in fri if V[i][felt] is not None]
        if kand:
            return min(kand, key=lambda i: (round(V[i][felt] / 3), -V[i]['L'])), hvordan
    return max(fri, key=lambda i: (V[i]['bygg'], V[i]['L'])), 'mest åpne vegg'


def naermeste_vegg(V, q, maks=1.0):
    """Veggen et vindu i punktet q står på, og posisjonen langs den (None om lenger unna enn maks)."""
    best = None
    for i, v in enumerate(V):
        t = float((q - v['a']) @ v['u']); d = abs(float((q - v['a']) @ v['n']))
        if -0.5 <= t <= v['L'] + 0.5 and d < maks and (best is None or d < best[0]):
            best = (d, i, t)
    return (best[1], best[2]) if best else (None, None)
