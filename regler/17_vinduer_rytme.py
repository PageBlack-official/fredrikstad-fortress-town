"""Regel (Vegar, 27.10): de antatte husene skal ha vinduer og dører slik Gamlebyens hus har dem i kvartaltegningene, ikke et
generisk rutenett. Sjekkes på alle hus med fasade_kilde antatt (fasit-husene fra tegningene sjekkes ikke, de er fasiten):
- loddrett: hvert vindu over 1. etasje står rett over et vindu eller en dør (innen 0,2 m)
- rytme: innen en vegg og etasje står vinduene med lik avstand (en manglende akse, f.eks. der døra står, er lov)
- felles vegg: ingen vinduer eller dører der et nabohus står inntil (0,6 m)
- dør bare på gatesiden, en annen vegg mot gate, eller mot gårdsrom
- høyden styrer: overkanten minst 0,3 m under gesims
Veggene, gatesiden og felles vegg beregnes som i verktoy/vegger.py (samme kode som lager vinduene)."""
import sys
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import numpy as np, vegger as VG

b = data('bygg'); ret = data('rettelser')
v33 = {r['id'] for r in ret if r['op'] == 'sett' and r.get('felt') == 'vind' and r.get('grunn', '').startswith('v33')}
omg = VG.Omgivelser(b, data('veier'), data('gardsrom'))
F = {k: [] for k in ('loddrett', 'rytme', 'felles', 'dor', 'gesims')}
hus = n_vind = n_dor = 0
for i, x in gamleby(b):
    if x.get('skjul') or x.get('kirke') or x.get('fasade_kilde') != 'antatt' or x['id'] in v33 or not x.get('vind'):
        continue
    hus += 1; V = VG.vegger(x, omg, slaa_sammen=True); gi, _ = VG.gatesiden(V)
    per = {}
    for v in x['vind']:
        n_vind += v[9] == 0; n_dor += v[9] == 1
        q = np.array(v[:2]); k, t = VG.naermeste_vegg(V, q)
        if v[2] + v[8] / 2 > x['h'] - 0.3 + 1e-6:
            F['gesims'].append(f"- {x['id']} (bygg {i}): overkant {v[2] + v[8] / 2:.2f} m, gesims {x['h']} m")
        nrm = np.array([v[5], v[6]]); tan = np.array([v[3], v[4]])
        if any(omg.nabo(x['id'], q + tan * s * v[7] / 2 + nrm * VG.FELLES) for s in (-1, 0, 1)):
            F['felles'].append(f"- {x['id']} (bygg {i}): {'dør' if v[9] == 1 else 'vindu'} ved ({v[0]}, {v[1]}) mot nabohus")
        if k is None:
            continue
        per.setdefault(k, []).append((t, v))
        if v[9] == 1:
            w = V[k]
            if not (k == gi or w['gate'] is not None or w['gardsrom']):
                F['dor'].append(f"- {x['id']} (bygg {i}): dør på vegg {k + 1} som verken vender mot gate eller gårdsrom")
    for k, vs in per.items():
        lv = {}
        for t, v in vs:
            if v[9] == 0: lv.setdefault(round(v[2] - v[8] / 2, 1), []).append(t)
        z = sorted(lv)
        under_alle = {zz: [t for z0 in z if z0 < zz for t in lv[z0]] + [t for t, v in vs if v[9] == 1] for zz in z}
        for zz in z[1:]:
            for t in lv[zz]:
                if not under_alle[zz] or min(abs(t - s) for s in under_alle[zz]) > 0.2:
                    F['loddrett'].append(f"- {x['id']} (bygg {i}): vindu i høyde {zz} m på vegg {k + 1} har ikke vindu/dør under")
        for zz, ts in lv.items():
            ts = sorted(ts)
            if len(ts) < 3: continue
            d = np.diff(ts); s = d.min()
            if any(abs(g / s - round(g / s)) * s > 0.15 for g in d):
                F['rytme'].append(f"- {x['id']} (bygg {i}): ujevn avstand på vegg {k + 1}, høyde {zz} m: {', '.join(f'{g:.2f}' for g in d)}")
navn = dict(loddrett='vinduer uten vindu/dør rett under', rytme='vegger med ujevn vindusavstand', felles='vinduer/dører mot nabohus (felles vegg)',
            dor='dører som ikke vender mot gate eller gårdsrom', gesims='vinduer over gesims (i taket)')
feil = sum(len(v) for v in F.values())
linjer = [f"{hus} antatte hus, {n_vind} vinduer, {n_dor} dører; {feil} brudd"]
for k, v in F.items():
    linjer.append(f"\n## {navn[k]}: {len(v)}"); linjer += v[:30] + (['- …'] if len(v) > 30 else [])
linjer.append('\nReglene og tallene bak dem: rapport/vinduer/regler-fra-tegningene.md. Vinduene lages av verktoy/vinduer_regler.py.')
rapport('17_vinduer_rytme', feil == 0, linjer, 'rapport/vinduer/kontrollark.png')
