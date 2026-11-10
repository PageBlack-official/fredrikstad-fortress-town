#!/usr/bin/env python3
"""Frie vegger uten vinduer får vinduer i husets egen rytme (02.11, avvik A4/A13).

    python3 verktoy/blanke_vegger.py          rettelser «vind» for husene med blanke frie vegger (idempotent; --tørt viser bare)

En blank vegg på et hus som har vinduer på de andre sidene, er feil (Vegar 02.11), med mindre en kilde sier at veggen er blank:
  - tegningen: fasade_tegning har veggen med 0 vinduer (lest av kvartaltegningen),
  - en merknad (kilder/bygg-merknader.json «vegg») med 0 vinduer på den siden,
  - Street View (fasade_sv, godkjent i sv_kobling) med 0 vinduer på den veggen.
Hvilke vegger: fri (nabohus inntil under halve veggen, vegger.py), minst 3 m. Hus som ikke tegnes som vanlige hus hoppes over:
kirka, hus med eget fasadeverktøy (datalag.EGNE_FASADER), portaler (data/porter.json typ mur).
Rytmen: vinduene husets tegnede/sette fasader har (median bredde og høyde, de samme radhøydene); har huset ingen vinduer
(fasadekilde mangler), gjelder reglene fra kvartaltegningene (vinduer_regler.py: akser 2,8 m, 0,85 x 1,4 m, brystning 0,9 m).
Ingen dører legges til her. Står i kjeden etter landemerker.py (sist av verktøyene som skriver vind på vanlige hus).
"""
import json, math, os, sys
import numpy as np

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG, vinduer_regler as VR  # noqa: E402

GRUNN = 'blanke frie vegger får vinduer i husets rytme (verktoy/blanke_vegger.py, 02.11)'
SIDER = {'N': 0, 'NØ': 45, 'Ø': 90, 'SØ': 135, 'S': 180, 'SV': 225, 'V': 270, 'NV': 315}
MIN_L = 3.0


def az(n):
    return (math.degrees(math.atan2(n[0], n[1])) + 360) % 360


def vind_paa(x, w):
    a, u, n = w['a'], w['u'], w['n']
    return [v for v in (x.get('vind') or []) if abs((v[0] - a[0]) * n[0] + (v[1] - a[1]) * n[1]) < 0.6
            and -0.3 < (v[0] - a[0]) * u[0] + (v[1] - a[1]) * u[1] < w['L'] + 0.3]


def blank_i_kilde(x, w, P, merkn):
    """True når en kilde sier at veggen er blank."""
    a, c = w['a'], w['a'] + w['u'] * w['L']
    for k, info in (x.get('fasade_tegning') or {}).items():
        k = int(k)
        if k >= len(P): continue
        e0, e1 = np.array(P[k]), np.array(P[(k + 1) % len(P)]); m = (e0 + e1) / 2
        if abs(float((m - a) @ w['n'])) < 0.6 and -0.5 < float((m - a) @ w['u']) < w['L'] + 0.5:
            if sum(info.get('rader') or []) == 0 and not info.get('dorer'): return 'tegningen'
    for v in merkn:
        s = v.get('side')
        if s in SIDER and abs((az(w['n']) - SIDER[s] + 180) % 360 - 180) < 40 and sum(v.get('rader') or []) == 0:
            return 'merknad'
    sv = x.get('fasade_sv') or {}
    for o in [sv] + list(sv.get('sider') or []):
        nn = o.get('n')
        if nn and abs((az(w['n']) - az(nn) + 180) % 360 - 180) < 30 and sum(o.get('rader') or [1]) == 0:
            return 'Street View'
    return None


def rytme(x):
    v0 = [v for v in (x.get('vind') or []) if v[9] == 0 and v[2] < x['h']]
    if not v0:
        return VR.R['vb'], VR.R['vh'], [b + VR.R['vh'] / 2 for b in VR.rader(x['h'])]
    b = float(np.median([v[7] for v in v0])); hh = float(np.median([v[8] for v in v0]))
    # radene: vinduenes midthøyder slått sammen når de ligger under 1 m fra hverandre (kjellervinduer ikke med)
    # en rad må ha minst to vinduer når huset har det, så enkeltstående store vinduer (butikk, trapp) ikke blir egne rader
    zs = sorted(v[2] for v in v0 if v[8] >= 0.8); grupper, gr = [], []
    for z in zs:
        if gr and z - gr[0] > 1.0: grupper.append(gr); gr = []
        gr.append(z)
    if gr: grupper.append(gr)
    if any(len(g) >= 2 for g in grupper): grupper = [g for g in grupper if len(g) >= 2]
    rader = [float(np.median(g)) for g in grupper]
    return b, hh, [round(z, 2) for z in rader] or [b_ + VR.R['vh'] / 2 for b_ in VR.rader(x['h'])]


def dekket_av_nabo(bid, w, rute):
    """True når et NABOBYGG har vinduer som dekker denne veggen: minst 3 fremmede vinduer med samme normal (dot>0.9)
    innen 0,6 m vinkelrett på veggplanet og innenfor veggens lengde. Da er veggen mot nabohuset, ikke en blank fri vegg
    (pb-1 Brannbatteriet ligger mot Provianthusets lange vegg: samme fasade antatt to ganger). Rekkefølge-uavhengig:
    sjekker vinduene slik de står i dataene som sendes inn (regel 44 kjører på sluttdataene, der nabohusene er fylt)."""
    a, n, u, L = w['a'], w['n'], w['u'], w['L']
    cx, cy = a[0] + u[0] * L / 2, a[1] + u[1] * L / 2
    treff = 0
    for dx in range(-int(L / 2 / RUTE_N) - 2, int(L / 2 / RUTE_N) + 3):
        for dy in (-1, 0, 1):
            for (yb, v) in rute.get((math.floor(cx / RUTE_N) + dx, math.floor(cy / RUTE_N) + dy), ()):
                if yb == bid:
                    continue
                if v[5] * n[0] + v[6] * n[1] < 0.9:
                    continue
                if abs((v[0] - a[0]) * n[0] + (v[1] - a[1]) * n[1]) > 0.6:
                    continue
                s = (v[0] - a[0]) * u[0] + (v[1] - a[1]) * u[1]
                if -0.3 < s < L + 0.3:
                    treff += 1
    return treff >= 3


RUTE_N = 4.0


def beregn(d=None):
    d = d or datalag.alle()
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    porter = {p.get('bygg_id') for p in d.get('porter', []) if p.get('typ') == 'mur'}   # portaler; hus på portblokk (Voldporten) er med
    M = {}
    for m in json.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))['hus']:
        M.setdefault(m['id'], []).extend(m.get('vegg') or [])
    # alle vinduer i et romlig rutenett, til å se om et nabobygg dekker en ellers «blank» vegg
    vindu_rute = {}
    for b in d['bygg']:
        if b.get('skjul'):
            continue
        for v in (b.get('vind') or []):
            vindu_rute.setdefault((math.floor(v[0] / RUTE_N), math.floor(v[1] / RUTE_N)), []).append((b['id'], v))
    nye, logg = {}, []
    for x in d['bygg']:
        if x.get('skjul') or not x.get('gml') or x.get('kirke') or x['id'] in datalag.EGNE_FASADER or x['id'] in porter:
            continue
        if not x.get('p') or len(x['p']) < 3 or (x.get('h') or 0) < 2.2:
            continue
        V = VG.vegger(x, omg, slaa_sammen=True)
        blanke = []
        rett = set(x.get('fasade_rett') or [])   # vegger lest fra rettet Street View (verktoy/fasade_rett.py): blank er lest, ikke glemt
        for wi, w in enumerate(V):
            if wi in rett: continue
            if w['felles'] >= 0.5 or w['L'] < MIN_L or vind_paa(x, w): continue
            if dekket_av_nabo(x['id'], w, vindu_rute): continue   # veggen ligger mot et nabohus som har vinduer der (ikke fri/blank)
            kilde = blank_i_kilde(x, w, x['p'], M.get(x['id'], []))
            if kilde: continue
            blanke.append(w)
        if not blanke: continue
        b, hh, rader = rytme(x)
        P = np.array(x['p'], float); ut = []
        for w in blanke:
            for t in VR.akser(w['L']):
                if not any(f0 <= t - b / 2 - 0.3 and t + b / 2 + 0.3 <= f1 for f0, f1 in w['fri']): continue
                q = w['a'] + w['u'] * t
                if not VR.hjorne_ok(P, q, b): continue
                for z in rader:
                    if z + hh / 2 > x['h'] - 0.2: continue
                    ut.append(VR.element(P, q, b, w['n'], z, round(b, 2), round(hh, 2), 0))
        if ut:
            nye[x['id']] = list(x.get('vind') or []) + ut
            logg.append((x['id'], x.get('navn'), len(blanke), len(ut)))
    return nye, logg


def main(tørt=False):
    nye, logg = beregn()
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    if not tørt:
        # beregnet uten egne linjer: kjør på tilstanden uten dem (idempotent)
        datalag.skriv_rettelser(ret)
        nye, logg = beregn()
        ret += [{'emne': 'bygg', 'id': i, 'op': 'sett', 'felt': 'vind', 'verdi': v, 'hvem': 'Claude', 'dato': '2026-11-02', 'grunn': GRUNN}
                for i, v in sorted(nye.items())]
        datalag.skriv_rettelser(ret)
    for l in logg: print(*l)
    print(f"{len(logg)} hus fikk vinduer på {sum(l[2] for l in logg)} blanke frie vegger ({sum(l[3] for l in logg)} vinduer)")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
