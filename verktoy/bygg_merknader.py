"""Merknadene på husene (Vegars kvartalskontroll og avgjørelser mot kildene) som rettelser, kjørt sist i kjeden, så de
ikke blir overskrevet av verktøyene som legger inn grunnlaget (grunnmur, høyder, regler, Street View, tegningene).

Kilde: kilder/bygg-merknader.json, én post per hus med «kilde» (hvem/hva som sa det) og «grunn». Operasjoner:
  sett        {felt: verdi}: farger, h, th, sokkel, takform, flatt, skjul …
  vegg        [{side: "SV", rader: [n1, n2 …] (nederst først, kjeller som "k3"), dorer: [{u, typ, b, h}]}]
              veggen som vender mot side (kompass, som Street View-avlesningen); vinduer i jevn rytme etter reglene,
              antall per etasje og dørene der merknaden sier (u = andel fra venstre sett utenfra). Erstatter veggens vind.
  takvinduer  [{side, andeler: [..], b, h}]  flate vinduer i takflaten som faller mot side, i andel langs takfoten
  piper       "ingen" | [indekser som fjernes]
  arker       "ingen"
Kjør:  python3 verktoy/bygg_merknader.py [--tørt]   (etter fasade_tegning.py legg_inn, før id_flytt.py)
"""
import json, math, os, sys, re
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG, vinduer_regler as VR, streetview_fasader as SV
from shapely.geometry import Polygon, Point

GRUNN = 'merknad på huset (kilder/bygg-merknader.json)'
DATO = '2026-10-29'


def rader_fra(spec):
    ut = []
    for r in spec:
        if isinstance(r, str) and r.startswith('k'):
            ut.append(('kjeller', int(r[1:])))
        elif isinstance(r, str) and r.startswith('l'):
            ut.append(('loft', int(r[1:])))
        else:
            ut.append(('etg', int(r)))
    return ut


def takflate_mot(x, side):
    """Takflaten (tak2) som faller mot kompassretningen side: fallretningen (nedover) nærmest side."""
    a = math.radians(SV.KOMPASS[side]); f = np.array([math.sin(a), math.cos(a)])
    best = None
    for fl in x.get('tak2') or []:
        if len(fl) < 3: continue
        A = np.array([[q[0], q[1], 1] for q in fl]); k = np.linalg.lstsq(A, np.array([q[2] for q in fl]), rcond=None)[0]
        g = -np.array(k[:2]); n = np.linalg.norm(g)
        if n < 1e-6: continue
        s = float(g / n @ f) * Polygon([q[:2] for q in fl]).area
        if best is None or s > best[0]: best = (s, fl, k)
    return best


def main(tørt=False):
    M = json.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))
    ret = [r for r in datalag.les('rettelser') if not r.get('grunn', '').startswith(GRUNN)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    nye, logg = [], []
    for m in M['hus']:
        i = m['id']; x = BY.get(i)
        g = f"{GRUNN}: {m['kilde']}: {m['grunn']}"
        if x is None:
            logg.append(f"{i}: finnes ikke"); continue
        def sett(felt, verdi):
            nye.append({"emne": "bygg", "id": i, "op": "sett", "felt": felt, "verdi": verdi, "hvem": "Claude", "dato": DATO, "grunn": g})
            x[felt] = verdi
        for felt, verdi in (m.get('sett') or {}).items():
            sett(felt, verdi)
        if 'h' in (m.get('sett') or {}) and x.get('fasade_kilde') == 'antatt' and x.get('gml') and not m.get('vegg'):
            sett('vind', VR.lag_vind(x, omg)[0])       # ny høyde: reglene legger vinduene på nytt (regel 17: ikke over gesims)
        if m.get('vegg'):
            V = VG.vegger(x, omg, slaa_sammen=True); P = np.array(x['p'], float)
            vind = list(x.get('vind') or [])
            for vs in m['vegg']:
                wi = SV.retningsvegg(x, V, vs['side'])
                if wi is None:
                    logg.append(f"{i}: ingen vegg mot {vs['side']}"); continue
                w = V[wi]; w['venstre_til_hoyre'] = bool(w['u'] @ np.array([-w['n'][1], w['n'][0]]) > 0)
                dorer = [(q['u'], q.get('b', 1.05), q.get('h', 2.2), q.get('typ', 1)) for q in vs.get('dorer', [])]
                el, info = SV.lag_fasade(x, w, P, rader_fra(vs.get('rader', [])), dorer, vs.get('stor', False))
                vind = [v for v in vind if VG.naermeste_vegg(V, np.array(v[:2]))[0] != wi] + el
                for e in el: e[11] = 0
                logg.append(f"{i}: vegg mot {vs['side']} (vegg {wi}, {w['L']:.1f} m): {info.get('rader')} vinduer, {info.get('dorer')} dører")
            sett('vind', vind)
        if m.get('takvinduer'):
            tv = []
            for t in m['takvinduer']:
                b = takflate_mot(x, t['side'])
                if not b:
                    logg.append(f"{i}: ingen takflate mot {t['side']}"); continue
                _, fl, k = b
                # takfoten: kanten med lavest høyde; punktene midt i fallet, i andel langs takfoten
                kant = min(((fl[j], fl[(j + 1) % len(fl)]) for j in range(len(fl))), key=lambda e: e[0][2] + e[1][2])
                topp = max(q[2] for q in fl)
                g_ = -np.array(k[:2]) / np.linalg.norm(k[:2])
                for a_ in t['andeler']:
                    p = np.array(kant[0][:2]) + (np.array(kant[1][:2]) - np.array(kant[0][:2])) * a_
                    q = p - g_ * (topp / np.linalg.norm(k[:2])) * t.get('fall', 0.5)
                    tv.append([round(float(q[0]), 2), round(float(q[1]), 2), t.get('b', 0.6), t.get('h', 0.8)])
            sett('takvinduer', tv)
        if m.get('arker_legg'):
            V = VG.vegger(x, omg, slaa_sammen=True); ark = list(x.get('arker') or [])
            for a in m['arker_legg']:
                wi = SV.retningsvegg(x, V, a['side'])
                if wi is None: continue
                w = V[wi]
                for a_ in a['andeler']:
                    q = w['a'] + w['u'] * w['L'] * a_ - w['n'] * 1.4          # arkens front 1,4 m inn på taket, som i grunndataene
                    ark.append([round(float(q[0]), 2), round(float(q[1]), 2), x['h'], round(float(w['n'][0]), 4), round(float(w['n'][1]), 4), a.get('b', 1.25), a.get('h', 1.35)])
            sett('arker', ark)
        if m.get('veggfelt'):
            V = VG.vegger(x, omg, slaa_sammen=True); felt = []
            for vf in m['veggfelt']:
                wi = SV.retningsvegg(x, V, vf['side'])
                if wi is None: continue
                w = V[wi]; ltr = bool(w['u'] @ np.array([-w['n'][1], w['n'][0]]) > 0)
                def pkt(s_):
                    t = s_ if ltr else 1 - s_
                    q = w['a'] + w['u'] * w['L'] * t; return [round(float(q[0]), 2), round(float(q[1]), 2)]
                felt.append(pkt(vf['fra']) + pkt(vf['til']) + list(vf['farge']))
            sett('veggfelt', felt)
        if m.get('piper') == 'ingen':
            sett('piper', [])
        elif isinstance(m.get('piper'), list):
            sett('piper', [q for j, q in enumerate(x.get('piper') or []) if j not in m['piper']])
        if m.get('arker') == 'ingen':
            sett('arker', [])
        logg.append(f"{i}: {', '.join(k for k in ('sett', 'vegg', 'veggfelt', 'takvinduer', 'arker_legg', 'piper', 'arker') if m.get(k))}")
    for l in logg: print(l)
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
    print(f"{len(M['hus'])} hus, {len(nye)} rettelser")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
