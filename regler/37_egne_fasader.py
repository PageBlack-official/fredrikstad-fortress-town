"""Regel (02.11, avvik A1/A5): hus med eget fasadeverktøy (datalag.EGNE_FASADER) er det verktøyet gir, og har vinduer på alle vegger.
Vegar 02.11 16:44: «Infanterikasernenveggen som peker mot vest, at det mangler mange vinduer» og «versjonskonflikt».
Årsaken var at verktoy/kaserna.py (27.10) ikke stod i kjeden: fasade_tegning.py (29.10) la Kvartal11 og Street View 2010 over,
og veggen mot torget (44 m) fikk 11 vinduer i stedet for 45. Regelen er rød når
  - verktøyet ikke står i bygg_kjede.py etter fasadeverktøyene (da kan neste kjøring overstyre det igjen),
  - de effektive feltene (vind, arker, piper, sokkel) eller datafilene verktøyet skriver, ikke er det verktøyet gir nå,
  - en yttervegg på minst 10 m har færre vinduer i en etasje enn aksene tilsier (uavhengig av verktøyet: fanger også en feil i det).
"""
import sys, math, importlib.util
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402

linjer, ok = [], True
d = datalag.alle()
BY = {x['id']: x for x in d['bygg']}
kjede = open(os.path.join(ROT, 'verktoy', 'bygg_kjede.py'), encoding='utf8').read()
STEG = kjede[kjede.index('STEG'):]
for id_, verktoy in datalag.EGNE_FASADER.items():
    # 1. i kjeden, etter alle verktøy som skriver vind
    if verktoy not in STEG:
        ok = False; linjer.append(f"FEIL {id_}: {verktoy} står ikke i verktoy/bygg_kjede.py"); continue
    etter = [v for v in ('fasade_tegning.py', 'streetview_fasader.py', 'vinduer_regler.py', 'bygg_merknader.py', 'fasade_former.py', 'landemerker.py', 'fasadesegmenter.py')
             if STEG.index(v) > STEG.index(verktoy)]
    if etter:
        ok = False; linjer.append(f"FEIL {id_}: {verktoy} står før {', '.join(etter)} i kjeden (blir overstyrt)")
    # 2. det effektive bygget = verktøyet
    spec = importlib.util.spec_from_file_location('v_' + id_.replace('-', '_'), os.path.join(ROT, verktoy))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    felt, filer, *andre = m.beregn(d)
    x = BY[id_]
    for oid, of in (andre[0] if andre else {}).items():   # andre objekter verktøyet eier (portbygg og skur i Kasernens murer)
        for f, v in of.items():
            if json.dumps(BY[oid].get(f)) != json.dumps(v):
                ok = False; linjer.append(f"FEIL {oid}: feltet {f} er ikke det {verktoy} gir")
    for f, v in felt.items():
        # arker og piper lagres i grunnhøyden og flyttes av datalag.hoyden_styrer: sammenlign med det samme løpet
        if f in ('arker', 'piper'):
            raa = datalag.alle(raa=True); g = [dict(b) for b in raa['bygg']]
            r_ = [r for r in datalag.les('rettelser') if not (r.get('id') == id_ and r.get('felt') == f)]
            r_.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': f, 'verdi': v})
            v = {b['id']: b for b in datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, r_), g)['bygg']}[id_][f]
        if json.dumps(x.get(f)) != json.dumps(v):
            ok = False; linjer.append(f"FEIL {id_}: feltet {f} er ikke det {verktoy} gir (overstyrt av en annen linje i data/rettelser.json)")
    for navn, rader in filer.items():
        fil = open(os.path.join(ROT, 'data', navn + '.json'), encoding='utf8').read()
        if json.loads(fil) != json.loads(json.dumps(rader)):
            ok = False; linjer.append(f"FEIL {id_}: data/{navn}.json er ikke det {verktoy} gir (kjør verktøyet)")
    # 3. vinduer på alle ytterveggene (akse ca. 3,4 m), uavhengig av verktøyet
    p = x['p']; n = len(p)
    A = sum(p[i][0] * p[(i + 1) % n][1] - p[(i + 1) % n][0] * p[i][1] for i in range(n)) / 2
    glass = [v_ for v_ in d.get('vinterhager', []) if v_.get('bygg_id') == id_]
    def under_glass(q):
        for g in glass:
            gp = g['p']; inn = False
            for i in range(len(gp)):
                a, b = gp[i], gp[(i + 1) % len(gp)]
                if (a[1] > q[1]) != (b[1] > q[1]) and q[0] < a[0] + (q[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]): inn = not inn
            if inn: return True
        return False
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 10: continue
        tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = (ty, -tx) if A > 0 else (-ty, tx)
        midt = ((a[0] + b[0]) / 2 + nx * 3, (a[1] + b[1]) / 2 + ny * 3)
        if under_glass(midt): continue
        paa = [v_ for v_ in x.get('vind', []) if abs((v_[0] - a[0]) * nx + (v_[1] - a[1]) * ny) < 0.6 and -0.5 < (v_[0] - a[0]) * tx + (v_[1] - a[1]) * ty < L + 0.5]
        # rader: vinduene (typ 0) per høyde under gesimsen; en dør (typ 1) står i aksen for radene den dekker
        rader = {}
        for v_ in paa:
            if v_[9] == 0 and v_[2] < x['h']: rader[round(v_[2], 1)] = rader.get(round(v_[2], 1), 0) + 1
        for v_ in paa:
            if v_[9] == 1:
                for z in rader:
                    if z < v_[2] + v_[8] / 2: rader[z] += 1
        akser = max(1, round((L - 3.8) / 3.4) + 1)
        store = {z: c for z, c in rader.items() if z >= 1.2}   # etasjene (kjellervinduene i sokkelen står under 1,2 m)
        if len(store) < 2 or min(store.values()) < akser - 1:
            ok = False; linjer.append(f"FEIL {id_} vegg {i} ({L:.1f} m, normal {math.degrees(math.atan2(nx, ny)) % 360:.0f}°): {akser} akser, vinduer per etasje {dict(sorted(rader.items()))}")
        else:
            linjer.append(f"ok   {id_} vegg {i} ({L:.1f} m, normal {math.degrees(math.atan2(nx, ny)) % 360:.0f}°): {akser} akser, per etasje {dict(sorted(rader.items()))}")
rapport('37_egne_fasader', ok, [f"{len(datalag.EGNE_FASADER)} hus med eget fasadeverktøy"] + linjer)
