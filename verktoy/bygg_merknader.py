"""Merknadene på husene (Vegars kvartalskontroll og avgjørelser mot kildene) som rettelser, kjørt sist i kjeden, så de
ikke blir overskrevet av verktøyene som legger inn grunnlaget (grunnmur, høyder, regler, Street View, tegningene).

Kilde: kilder/bygg-merknader.json, én post per hus med «kilde» (hvem/hva som sa det) og «grunn». Operasjoner:
  sett        {felt: verdi}: farger, h, th, sokkel, takform, flatt, skjul …
  vegg        [{side: "SV", rader: [n1, n2 …] (nederst først, kjeller som "k3"), dorer: [{u, typ, b, h}]}]
              veggen som vender mot side (kompass, som Street View-avlesningen); vinduer i jevn rytme etter reglene,
              antall per etasje og dørene der merknaden sier (u = andel fra venstre sett utenfra). Erstatter veggens vind.
              «ved»: [x, y] velger veggen nærmest punktet blant veggene mot side (flere vegger mot samme side, kirka).
              Kirka (bygg.kirke) har egen modell i src/06: veggene der leses av verktoy/fasade_former.py (bygg.kirke.vinduer),
              ikke her.
              «rader_u»: [[u, …] per rad nederst først]: vinduene står der tegningen har dem (andel fra venstre sett utenfra),
              ikke i jevn rytme; en tom rad er en etasje uten synlige vinduer (nedre del skjult bak et lavere hus foran).
              «plass»: [fra, til] (andel fra venstre): merknaden gjelder bare den delen av veggen; resten står som før.
              «bare_telling»: true: tallene er Vegars/Claudes håndtelling i tegningen til kontrollen (verktoy/kontroll.py), og
              vinduene fra fasadeavlesningen står (de stemmer; det er kontrollens hulltelling som leser feil).
  takvinduer  [{side, andeler: [..], b, h}]  flate vinduer i takflaten som faller mot side, i andel langs takfoten
  piper       "ingen" | [indekser som fjernes]
  arker       "ingen"
Slåtte sammen hus (husdeling.py: «slaatt_sammen» på verten, de andre skjult): en vegg-merknad på et skjult hus gjelder den
delen av vertens vegg som det skjulte husets omriss dekker, og vertens egen vegg-merknad gjelder resten. Så kan to halvdeler
av samme fasade telles hver for seg i tegningen (Artillerigården: 868061 + 869572) og stå i ett hus etter Kartverkets DOM.
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


def etter_u(x, w, P, rader_u, dorer):
    """Vinduene der tegningen har dem: rader_u = [[u, …] per etasje nederst først], u = andel av veggen w fra venstre sett
    utenfra; dører (u, b, h, typ). Etasjehøydene som reglene (streetview_fasader.radhoyder, Kartverkets h). Gir (vind, info)."""
    L = w['L']; h = x['h']
    hoyder, _ = SV.radhoyder([('etg', len(r)) for r in rader_u], h, False)
    def pos(u, b):
        t = u * L if w['venstre_til_hoyre'] else (1 - u) * L
        t = min(max(t, b / 2 + 0.32), L - b / 2 - 0.32) if L > b + 0.64 else L / 2
        return w['a'] + w['u'] * t
    ut = []
    for u, b, dh, typ in dorer:
        dh = min(dh, h - SV.R['gesims'] - 0.1)
        ut.append(VR.element(P, pos(u, b), b, w['n'], dh / 2, b, dh, typ))
    plassert = []
    for r, (bz, vb, vh) in zip(rader_u, hoyder):
        n = 0
        for u in r:
            q = pos(u, vb)
            if bz < 2.5 and any(np.linalg.norm(q - np.array(d[:2])) < (vb + d[7]) / 2 for d in ut if d[9] in (1, 2)):
                continue                       # døra står der
            ut.append(VR.element(P, q, vb, w['n'], bz + vh / 2, vb, vh, 0)); n += 1
        plassert.append(n)
    return ut, dict(rader=plassert, dorer=len(dorer))


def vegg_ved(V, side, ved, maks_vinkel=35):
    """Veggen (indeks i V) som vender mot side (innen maks_vinkel grader) og står nærmest punktet ved."""
    a = math.radians(SV.KOMPASS[side]); f = np.array([math.sin(a), math.cos(a)]); q = np.array(ved, float)
    def avst(w):
        A, C = np.array(w['a'], float), np.array(w.get('c', np.array(w['a']) + np.array(w['u']) * w['L']), float)
        t = np.clip((q - A) @ (C - A) / max((C - A) @ (C - A), 1e-9), 0, 1); return float(np.linalg.norm(A + t * (C - A) - q))
    kand = [(avst(w), k) for k, w in enumerate(V) if np.array(w['n']) @ f >= math.cos(math.radians(maks_vinkel))]
    return min(kand)[1] if kand else None


def del_av_veggen(w, del_av):
    """Delen (t0, t1) i meter langs veggen w som et slått sammen hus dekker («eget»: det skjulte husets omriss projisert på
    veggen), eller den lengste delen ingen av de skjulte husene dekker («rest»: vertens egen del)."""
    def spenn(x):
        P = np.array(x['p'], float); n = np.array(w['n'], float)
        d = (P - w['a']) @ n
        T = sorted(float((q - w['a']) @ w['u']) for q, dd in zip(P, d) if abs(dd) < 1.0)
        return (max(0.0, T[0]), min(w['L'], T[-1])) if len(T) >= 2 else None
    slag, hva = del_av
    if slag == 'eget':
        return spenn(hva) or (0.0, 0.0)
    dekket = sorted(s for s in (spenn(x) for x in hva) if s)
    fri, t = [], 0.0
    for a, b in dekket:
        if a > t: fri.append((t, a))
        t = max(t, b)
    if t < w['L']: fri.append((t, w['L']))
    return max(fri, key=lambda f: f[1] - f[0]) if fri else (0.0, 0.0)


def main(tørt=False):
    M = json.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))
    ret = [r for r in datalag.les('rettelser') if not r.get('grunn', '').startswith(GRUNN)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    VERT = {j: x['id'] for x in d['bygg'] if not x.get('skjul') for j in (x.get('slaatt_sammen') or [])}
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
        if ('h' in (m.get('sett') or {}) or 'gml' in (m.get('sett') or {})) and x.get('fasade_kilde') in ('antatt', None) and x.get('gml') and not m.get('vegg'):
            if not x.get('fasade_kilde'): sett('fasade_kilde', 'antatt')
            sett('vind', VR.lag_vind(x, omg)[0])       # ny høyde: reglene legger vinduene på nytt (regel 17: ikke over gesims)
        if m.get('vegg') and x.get('kirke'):
            logg.append(f"{i}: kirka, veggene legges inn av fasade_former.py (bygg.kirke.vinduer)")
        elif m.get('vegg'):
            xv, sett_v, del_av = x, sett, None
            if x.get('skjul') and VERT.get(i) in BY:            # slått sammen: veggen står på verten, på delen huset dekker
                xv = BY[VERT[i]]; del_av = ('eget', x)
                def sett_v(felt, verdi, xv=xv, g=g):
                    nye.append({"emne": "bygg", "id": xv['id'], "op": "sett", "felt": felt, "verdi": verdi, "hvem": "Claude", "dato": DATO, "grunn": g})
                    xv[felt] = verdi
            elif x.get('slaatt_sammen'):
                del_av = ('rest', [BY[j] for j in x['slaatt_sammen'] if j in BY])
            V = VG.vegger(xv, omg, slaa_sammen=True); P = np.array(xv['p'], float)
            vind = list(xv.get('vind') or [])
            for vs in m['vegg']:
                if vs.get('bare_telling'):
                    logg.append(f"{i}: vegg mot {vs['side']}: bare telling til kontrollen"); continue
                wi = vegg_ved(V, vs['side'], vs['ved']) if vs.get('ved') else SV.retningsvegg(xv, V, vs['side'])
                if wi is None:
                    logg.append(f"{i}: ingen vegg mot {vs['side']}"); continue
                w = dict(V[wi]); w['venstre_til_hoyre'] = bool(w['u'] @ np.array([-w['n'][1], w['n'][0]]) > 0)
                t0, t1 = del_av_veggen(w, del_av) if del_av else (0.0, w['L'])
                if vs.get('plass'):
                    f0, f1 = vs['plass']; Lw = w['L']
                    t0, t1 = (f0 * Lw, f1 * Lw) if w['venstre_til_hoyre'] else ((1 - f1) * Lw, (1 - f0) * Lw)
                if t1 - t0 < 1.0:
                    logg.append(f"{i}: delen av vegg {wi} mot {vs['side']} er under 1 m"); continue
                if (t0, t1) != (0.0, w['L']):
                    w = dict(w, a=w['a'] + w['u'] * t0, L=t1 - t0,
                             fri=[[max(f0, t0) - t0, min(f1, t1) - t0] for f0, f1 in w['fri'] if min(f1, t1) > max(f0, t0)])
                dorer = [(q['u'], q.get('b', 1.05), q.get('h', 2.2), q.get('typ', 1)) for q in vs.get('dorer', [])]
                if vs.get('rader_u') is not None:
                    el, info = etter_u(xv, w, P, vs['rader_u'], dorer)
                else:
                    el, info = SV.lag_fasade(xv, w, P, rader_fra(vs.get('rader', [])), dorer, vs.get('stor', False))
                def paa_delen(v, wi=wi, w=w):
                    if VG.naermeste_vegg(V, np.array(v[:2]))[0] != wi: return False
                    t = float((np.array(v[:2]) - w['a']) @ w['u'])
                    return -0.05 <= t <= w['L'] + 0.05
                vind = [v for v in vind if not paa_delen(v)] + el
                for e in el: e[11] = 0
                logg.append(f"{i}: vegg mot {vs['side']} (vegg {wi} på {xv['id']}, {t0:.1f}–{t1:.1f} m av {V[wi]['L']:.1f} m): {info.get('rader')} vinduer, {info.get('dorer')} dører")
            sett_v('vind', vind)
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
            V = VG.vegger(x, omg, slaa_sammen=True); ark = [] if m.get('arker_erstatt') else list(x.get('arker') or [])
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
