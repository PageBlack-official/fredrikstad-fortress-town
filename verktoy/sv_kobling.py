#!/usr/bin/env python3
"""Street View-koblingen sjekket mot geometrien (02.11, avvik A12).

Vegar 02.11 18:29: «Noter deg at Street view-bildene du har tatt ikke stemmer helt overens med 3d-modellene.»
Hver observasjon i kilder/streetview/avlesning.json (hovedbildet og hver side) har kamerapunkt og retning (pano_url «lat,lon hNNN»).
Fra kamerapunktet sendes stråler i vifte rundt retningen; den første husveggen hver stråle treffer, er det bildet viser der.
Observasjonen gjelder huset bare når huset er det første som treffes i den delen av bildet avlesningen sier
(«venstre» -> venstre halvdel 0..45°, «høyre» -> høyre halvdel, ellers midten ±20°). Ellers viser bildet et annet hus
(nabohuset, huset over gata eller et skur foran), og fargen, vinduene, dørene og sokkelen fra den observasjonen brukes ikke.

    python3 verktoy/sv_kobling.py          kilder/streetview/kobling-geometri.json (dommen per observasjon) og rapporten
    les(d)                                 avlesningen med bare observasjoner som peker på huset (brukes av streetview_farger.py,
                                           streetview_fasader.py, tak_farge.les_sv, sokkel.py, fasadesegmenter.py)

Hovedavlesningen (feltene på toppnivå) er hovedbildet. Peker den ikke på huset, men en side gjør det, tar den nyeste godkjente
siden plassen som hovedavlesning (farge, år). Nyeste godkjente observasjon fra 2016 eller senere vinner også når hovedbildet
er eldre (Mormors Café: hovedbildet fra 2010, siden mot Voldportgaten fra 2024).
"""
import json, math, os, re, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag  # noqa: E402

KILDE = os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json')
DOM = os.path.join(ROT, 'kilder', 'streetview', 'kobling-geometri.json')
MAKS = 90.0
MND = r'(jan|feb|mar|apr|mai|jun|jul|aug|sep|okt|nov|des)\w*\.? ?(20\d\d)'


def aar(s):
    m = re.search(r'(20\d\d)', str(s or ''))
    return int(m.group(1)) if m else None


def kamera(pu):
    m = re.match(r'\s*(-?[0-9.]+),\s*(-?[0-9.]+)\s*h\s*(-?[0-9.]+)', str(pu or ''))
    if not m: return None
    x, y = datalag.til_modell(float(m.group(2)), float(m.group(1)))
    return x, y, float(m.group(3))


def sektor(tekst):
    t = (tekst or '').lower()
    if 'venstre' in t and 'høyre' not in t: return (-45, 0)
    if 'høyre' in t and 'venstre' not in t: return (0, 45)
    return (-20, 20)


def slektninger(B):
    """id -> id-ene for samme bygning: fløyer (Tøihuset) og husdelingen (kilder/husdeling.json: biter av ett hus, sammenslåtte hus)."""
    slekt = {}
    for b in B:
        for f in (b.get('floyer') or []): slekt.setdefault(b['id'], set()).add(f)
    hd_f = os.path.join(ROT, 'kilder', 'husdeling.json')
    if os.path.exists(hd_f):
        HD = json.load(open(hd_f, encoding='utf8'))
        for D_ in HD.get('deling', []):
            g = {D_['id']} | set(D_.get('nye_id') or [])
            for x in g: slekt.setdefault(x, set()).update(g)
        for S_ in HD.get('sammen', []):
            for x in S_['ids']: slekt.setdefault(x, set()).update(S_['ids'])
    return slekt


def dom(d=None, avl=None):
    from shapely.geometry import Polygon, LineString, Point
    from shapely.strtree import STRtree
    d = d or datalag.alle(); avl = avl or json.load(open(KILDE, encoding='utf8'))
    B = [b for b in d['bygg'] if not b.get('skjul') and b.get('p') and len(b['p']) >= 3]
    P = [Polygon(b['p']).buffer(0) for b in B]; T = STRtree(P)
    # et skjult hus som er slått sammen med et annet (husdeling «sammen»), teller som verten
    vert = {}
    for b in d['bygg']:
        if b.get('skjul') and b.get('slaatt_sammen_med'): vert[b['id']] = b['slaatt_sammen_med']
    for b in B:
        for s in (b.get('slaatt_sammen') or []):
            vert[s] = b['id']
    slekt = slektninger(B)

    def forste(cx, cy, hd):
        a = math.radians(hd); L = LineString([(cx, cy), (cx + math.sin(a) * MAKS, cy + math.cos(a) * MAKS)]); best = None
        for j in T.query(L):
            g = P[j].intersection(L)
            if g.is_empty: continue
            dist = Point(cx, cy).distance(g)
            if best is None or dist < best[0]: best = (dist, B[j]['id'])
        return best[1] if best else None
    ut = {}
    for i, a in avl.items():
        mål = {i, vert.get(i, i)} | slekt.get(i, set()) | slekt.get(vert.get(i, i), set())
        obs = [('hoved', a.get('pano_url'), a.get('merknad') or '')] + [(f'side{k}', s.get('pano_url'), s.get('retning') or '') for k, s in enumerate(a.get('sider') or [])]
        for navn, pu, tekst in obs:
            k = kamera(pu)
            if not k: continue
            cx, cy, hd = k; s0, s1 = sektor(tekst if navn != 'hoved' else '')
            vinkler = list(range(s0, s1 + 1, 3))
            treff = [forste(cx, cy, hd + v) for v in vinkler]
            andel = sum(1 for t in treff if t in mål) / len(treff)
            andre = sorted({t for t in treff if t and t not in mål}, key=lambda t: -treff.count(t))
            ut.setdefault(i, {})[navn] = {'ok': andel > 0, 'andel': round(andel, 2), 'sektor': [s0, s1],
                                         'ser': andre[0] if andre and andel == 0 else None, 'kamera': [round(cx, 1), round(cy, 1), hd]}
    return ut


def les(d=None):
    """Avlesningen med bare observasjoner som peker på huset; hovedavlesningen er nyeste godkjente observasjon."""
    avl = json.load(open(KILDE, encoding='utf8'))
    D = json.load(open(DOM, encoding='utf8'))['dom'] if os.path.exists(DOM) else dom(d, avl)
    ut = {}
    for i, a in avl.items():
        dd = D.get(i, {})
        sider = [s for k, s in enumerate(a.get('sider') or []) if dd.get(f'side{k}', {}).get('ok', True)]
        hoved_ok = dd.get('hoved', {}).get('ok', True)
        a2 = dict(a, sider=sider)
        kand = ([('hoved', aar(a.get('bilde_dato')), a)] if hoved_ok else []) + [('side', aar(s.get('bilde_dato')), s) for s in sider if s.get('vegg_farge')]
        if not kand:
            continue
        hv, hy, ho = max(kand, key=lambda t: (t[1] or 0, t[0] == 'hoved'))
        if hv == 'side':
            a2['vegg'] = {'farge': ho.get('vegg_farge'), 'rgb': ho.get('vegg_rgb'), 'lys': ho.get('lys')}
            a2['bilde_dato'] = ho.get('bilde_dato'); a2['pano_url'] = ho.get('pano_url')
            a2['hoved_fra'] = 'side'
        ut[i] = a2
    return ut


def main():
    d = datalag.alle(); avl = json.load(open(KILDE, encoding='utf8'))
    D = dom(d, avl)
    n = sum(len(v) for v in D.values()); feil = [(i, k, v) for i, o in D.items() for k, v in o.items() if not v['ok']]
    json.dump({'om': __doc__.strip().splitlines()[0], 'laget': '2026-11-02', 'verktoy': 'verktoy/sv_kobling.py',
               'tall': {'observasjoner': n, 'peker_ikke_paa_huset': len(feil), 'hus': len({f[0] for f in feil})}, 'dom': D},
              open(DOM, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f"{n} observasjoner, {len(feil)} peker ikke på huset ({len({f[0] for f in feil})} hus)")


if __name__ == '__main__':
    main()
