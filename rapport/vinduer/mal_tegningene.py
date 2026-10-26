"""Måler vinduene og dørene på husene som er lest fra Vegars kvartaltegninger (fasit) og skriver tallene til
rapport/vinduer/maalinger.json. Reglene i verktoy/vinduer_regler.py er satt fra disse tallene (se regler-fra-tegningene.md);
kjør denne på nytt når flere hus er lest fra tegningene, og se om tallene flytter seg. Bare tall går ut av tegningene.

    python3 rapport/vinduer/mal_tegningene.py"""
import json, os, sys, collections
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG

UTHUS = {'garage', 'garages', 'shed'}


def fasit_ider(rettelser, bygg):
    """Fasit: fasade_kilde kvartaltegning, og hus med v33-rettelse på vind (lest på ny fra tegningene 25.10)."""
    v33 = {r['id'] for r in rettelser if r['op'] == 'sett' and r.get('felt') == 'vind' and r.get('grunn', '').startswith('v33')}
    return {x['id'] for x in bygg if x.get('fasade_kilde') == 'kvartaltegning'} | v33


def fordel(V, W):
    """Vinduene (W) på veggene (V): {veggindeks: [(t, vindu)]}."""
    per = collections.defaultdict(list)
    for v in W:
        i, t = VG.naermeste_vegg(V, np.array(v[:2]))
        if i is not None:
            per[i].append((t, v))
    return per


def klasse(V, i, gi):
    """hoved (gatesiden), gate (annen vegg mot gate), bak (motsatt gatesiden, ikke mot gate), side, felles."""
    w = V[i]
    if w['felles'] >= 0.5: return 'felles'
    if i == gi: return 'hoved'
    if w['gate'] is not None: return 'gate'
    if gi is not None and float(w['n'] @ V[gi]['n']) < -0.7: return 'bak'
    return 'side'


def pct(a, q): return [round(float(x), 2) for x in np.percentile(a, q)] if len(a) else []
def andel(a): return round(float(np.mean(a)), 2) if len(a) else None


def main():
    d = datalag.alle(); b = d['bygg']; ret = datalag.les('rettelser')
    fas = fasit_ider(ret, b)
    omg = VG.Omgivelser(b, d['veier'], d['gardsrom'])
    hus = [x for x in b if x['id'] in fas and x.get('gml') and not x.get('skjul') and x.get('vind') and not x.get('kirke')]
    vin = [v for x in hus for v in x['vind'] if v[9] == 0]; dor = [v for x in hus for v in x['vind'] if v[9] == 1]
    S = collections.defaultdict(list)
    for x in hus:
        V = VG.vegger(x, omg); per = fordel(V, x['vind']); gi, hvordan = VG.gatesiden(V)
        S['gatevalg'].append(hvordan)
        # etasjer: brystning 0,9 + 3,0 k; formelen er alle k der overkanten (bryst + 1,4) står minst 0,3 under gesims
        rader = {round((v[2] - v[8] / 2 - 0.9) / 3.0) for v in x['vind'] if v[9] == 0 and abs(((v[2] - v[8] / 2 - 0.9) / 3.0) - round((v[2] - v[8] / 2 - 0.9) / 3.0)) < 0.05}
        rader = {k for k in rader if k >= 0}
        formel = {k for k in range(6) if 0.9 + 3.0 * k + 1.4 <= x['h'] - 0.3}
        if rader: S['etasjer'].append((x['h'], max(rader) + 1, max(formel) + 1 if formel else 0))
        S['dorer_per_hus'].append(sum(1 for v in x['vind'] if v[9] == 1))
        for i, w in enumerate(V):
            vs = per.get(i, []); kl = klasse(V, i, gi)
            ws = [(t, v) for t, v in vs if v[9] == 0]; ds = [(t, v) for t, v in vs if v[9] == 1]
            S['vegg'].append(dict(typ=x['type'], L=w['L'], kl=kl, nv=len(ws), nd=len(ds), gard=w['gardsrom']))
            nedre = sorted(t for t, v in ws if v[2] < 2.6)
            for t, v in ds:
                akser = sorted({round(tt, 1) for tt, vv in ws})
                if len(nedre) >= 2:
                    s = float(np.median(np.diff(nedre))); r = ((t - nedre[0]) / s) % 1.0
                    S['dor_i_rytme'].append(min(r, 1 - r) * s < 0.35)
                    alle = sorted(nedre + [t]); midt = min(alle, key=lambda q: abs(q - w['L'] / 2))
                    S['dor_aksen_naermest_midten'].append(abs(midt - t) < 0.05 or abs(t - w['L'] / 2) < 1.6)
                S['dor'].append(dict(kl=kl, rel=t / w['L'], over=any(abs(tt - t) < 0.3 and vv[2] > 2.5 for tt, vv in ws)))
            if len(nedre) >= 2:
                dd = np.diff(nedre); S['cc'] += list(dd); S['cc_lik'].append(float(dd.std() / dd.mean()) < 0.05)
            if nedre:
                S['kant'].append(min(nedre[0], w['L'] - nedre[-1]))
                S['kol'].append((w['L'], len(nedre), kl))
                alle_t = sorted([t for t, v in vs if v[2] < 2.6])
                S['sym'].append(max(min(abs((w['L'] - t) - s) for s in alle_t) for t in alle_t))
            lv = collections.defaultdict(list)
            for t, v in ws:
                lv[round(v[2] - v[8] / 2, 1)].append(t)
            z = sorted(lv)
            for zz in z[1:]:
                under = [t for z0 in z if z0 < zz for t in lv[z0]] + [t for t, v in ds]
                for t in lv[zz]:
                    S['loddrett'].append(min(abs(t - s) for s in under) < 0.2)
    R = dict(hus=len(hus), vinduer=len(vin), dorer=len(dor))
    R['vindu_bredde'] = collections.Counter(v[7] for v in vin).most_common(4)
    R['vindu_hoyde'] = collections.Counter(v[8] for v in vin).most_common(4)
    R['brystning'] = collections.Counter(round(v[2] - v[8] / 2, 2) for v in vin).most_common(6)
    R['dor_bredde'] = collections.Counter(v[7] for v in dor).most_common(3)
    R['dor_hoyde'] = collections.Counter(v[8] for v in dor).most_common(3)
    R['dor_underkant'] = collections.Counter(round(v[2] - v[8] / 2, 2) for v in dor).most_common(3)
    R['dor_bue_andel'] = andel([v[10] for v in dor])
    R['etasjer_som_formelen_andel'] = andel([a == f for h, a, f in S['etasjer']])
    R['etasjer_over_formelen_andel'] = andel([a > f for h, a, f in S['etasjer']])
    R['cc_p10_25_50_75_90'] = pct(S['cc'], [10, 25, 50, 75, 90])
    R['cc_lik_innen_vegg_andel'] = andel(S['cc_lik'])
    R['kant_til_senter_p10_25_50_75_90'] = pct(S['kant'], [10, 25, 50, 75, 90])
    R['kant_085_andel'] = andel(np.abs(np.array(S['kant']) - 0.85) < 0.1)
    R['symmetri_andel_under_0_3m'] = andel(np.array(S['sym']) < 0.3)
    R['loddrett_andel'] = andel(S['loddrett'])
    K = {}
    for kl in ('hoved', 'gate', 'side', 'bak', 'felles'):
        for gr, f in (('hus', lambda w: w['typ'] not in UTHUS), ('uthus', lambda w: w['typ'] in UTHUS)):
            ws = [w for w in S['vegg'] if w['kl'] == kl and f(w) and w['L'] >= 3]
            K[f'{kl}/{gr}'] = dict(vegger_over_3m=len(ws), med_vindu=andel([w['nv'] > 0 for w in ws]), med_dor=andel([w['nd'] > 0 for w in ws]))
    R['veggklasser'] = K
    L = {}
    for lo, hi in ((0, 2), (2, 3), (3, 4), (4, 6), (6, 9), (9, 13), (13, 20), (20, 999)):
        ws = [w for w in S['vegg'] if w['kl'] != 'felles' and lo <= w['L'] < hi]
        ks = [n for LL, n, kl in S['kol'] if lo <= LL < hi]
        if ws:
            L[f'{lo}-{hi}'] = dict(vegger=len(ws), med_vindu=andel([w['nv'] > 0 for w in ws]), akser_median=float(np.median(ks)) if ks else 0)
    R['lengde'] = L
    D = S['dor']
    R['dor_klasse'] = dict(collections.Counter(x['kl'] for x in D))
    R['dor_rel_p10_25_50_75_90'] = pct([x['rel'] for x in D], [10, 25, 50, 75, 90])
    R['dor_i_vindusrytmen_andel'] = andel(S['dor_i_rytme'])
    R['dor_aksen_naer_midten_andel'] = andel(S['dor_aksen_naermest_midten'])
    R['dor_vindu_over_andel'] = andel([x['over'] for x in D])
    R['dorer_per_hus'] = dict(sorted(collections.Counter(S['dorer_per_hus']).items()))
    R['gatevalg'] = dict(collections.Counter(S['gatevalg']))
    json.dump(R, open(os.path.join(ROT, 'rapport', 'vinduer', 'maalinger.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False))


if __name__ == '__main__':
    main()
