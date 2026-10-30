"""Avgjørelse per tegningshus som avviker fra Street View (30.10): feil vegg, feil vindu eller huset er endret siden 2015.
Leser rapport/streetview-fasader/kjoring.json (fasithusene, gatesiden kameraet så) og vektoravlesningen av tegningene
(feltet fasade_tegning på huset, kilder/fasade-tegning/). Skriver rapport/bygg/sv-avvik.md og .json.

Regler, i rekkefølge:
  1 veggen kameraet så, er ikke tegnet           -> feil vegg (sammenligningen brukte en vegg tegningen ikke viser)
  2 tegningens rader på veggen = Street View     -> feil vindu, rettet (den gamle avlesningen talte feil; vektoravlesningen stemmer)
  3 Street View = radene på en annen tegnet vegg -> feil vegg (kameraet så en annen side enn sammenligningen valgte)
  4 like mange etasjer, høyst 2 vinduer i avvik  -> feil vindu (avlesningen av foto eller tegning, ±1 per rad; tegningen står)
  5 færre vinduer i bildet enn i tegningen       -> feil vindu (trær, vinkel eller bare en del av veggen i bildet; tegningen står)
  6 ellers (flere etasjer/vinduer i dag)          -> endret siden 2015

    python3 verktoy/sv_avvik.py
"""
import json, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG


def main():
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    K = json.load(open(os.path.join(ROT, 'rapport', 'streetview-fasader', 'kjoring.json'), encoding='utf8'))
    ut = []
    for e in K:
        if not e.get('status', '').startswith('fasit'):
            continue
        x = BY.get(e['id'])
        if not x: continue
        S = [n for t, n in e['sv']['rader'] if t == 'etg' and n is not None]
        Vm = VG.vegger(x, omg, slaa_sammen=True); Vu = VG.vegger(x, omg, slaa_sammen=False)
        w = Vm[e['vegg']]; mid = (np.array(w['a']) + np.array(w['c'])) / 2
        ft = x.get('fasade_tegning') or {}
        tegnet = {}
        for k, inf in ft.items():
            vu = Vu[int(k)] if int(k) < len(Vu) else None
            if vu is None: continue
            tegnet[int(k)] = (inf, (np.array(vu['a']) + np.array(vu['c'])) / 2, vu)
        # den tegnede veggen som ligger på veggen kameraet så (samme linje, midtpunkt nær)
        paa = None
        for k, (inf, m, vu) in tegnet.items():
            if abs(float(np.dot(np.array(vu['n']), np.array(w['n'])))) > 0.95 and abs(float(np.dot(m - mid, np.array(w['n'])))) < 1.0:
                paa = (k, inf); break
        sv_txt = '/'.join(map(str, S)) or '0'
        if paa is not None and paa[1].get('tegning') == 'Street View':
            vurd, grunn = 'feil vegg (Street View lagt på)', f"Street View så {e['side'].split(' ')[0]}-siden ({w['L']:.0f} m), som tegningen ikke viser: veggen har nå Street View {S} i stedet for reglene"
        elif paa is None:
            vurd, grunn = 'feil vegg', f"Street View så {e['side'].split(' ')[0]}-siden ({w['L']:.0f} m), som tegningen ikke viser; tegningen viser {', '.join(f'{inf['rader']}' for inf, _, _ in tegnet.values()) or 'ingen lest vegg'}"
        else:
            D = paa[1]['rader']
            if D == S and not e.get('avvik'):
                continue
            andre = [inf['rader'] for k, (inf, _, _) in tegnet.items() if k != paa[0]]
            if D == S:
                vurd, grunn = 'feil vindu (rettet)', f"vektoravlesningen gir {D}, som Street View; den gamle avlesningen hadde {e['modell']['rader']}"
            elif S in andre:
                vurd, grunn = 'feil vegg', f"Street View {S} er radene på en annen tegnet vegg; på veggen sammenligningen valgte, viser tegningen {D}"
            elif len(D) == len(S) and sum(abs(a - b) for a, b in zip(D, S)) <= 2:
                vurd, grunn = 'feil vindu', f"tegningen {D}, Street View {S}: samme etasjer, høyst to vinduer i avvik (avlesning); tegningen står"
            elif sum(S) < sum(D) and len(S) <= len(D):
                vurd, grunn = 'feil vindu', f"tegningen {D}, Street View {S}: bildet viser færre vinduer enn tegningen (trær, vinkel eller bare en del av veggen); tegningen står"
            else:
                vurd, grunn = 'endret siden 2015', f"tegningen {D}, Street View {S} ({e.get('sikkerhet')} sikkerhet): flere etasjer eller vinduer i dag enn i tegningen"
        ut.append(dict(id=e['id'], navn=x.get('navn'), side=e['side'].split(' (')[0], sv=S, modell=e['modell']['rader'], vurdering=vurd, grunn=grunn, sikkerhet=e.get('sikkerhet')))
    json.dump(ut, open(os.path.join(ROT, 'rapport', 'bygg', 'sv-avvik.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    import collections
    c = collections.Counter(u['vurdering'] for u in ut)
    L = ['# Tegningshus som avviker fra Street View: avgjørelse per hus', '',
         'Laget av verktoy/sv_avvik.py (30.10) fra rapport/streetview-fasader/kjoring.json og vektoravlesningen av tegningene. '
         'Reglene står øverst i verktøyet. Tegningen er fasit for vinduer og dører; «endret siden 2015» betyr at Street View viser en annen fasade i dag, '
         'og huset står fortsatt etter tegningen til Vegar sier noe annet.', '',
         ' · '.join(f'{k}: {v}' for k, v in c.most_common()), '',
         '| id | navn | siden kameraet så | Street View | før (modell) | vurdering | grunn |', '|---|---|---|---|---|---|---|']
    for u in sorted(ut, key=lambda u: (u['vurdering'], u['id'])):
        L.append(f"| {u['id']} | {u['navn'] or ''} | {u['side']} | {u['sv']} | {u['modell']} | {u['vurdering']} | {u['grunn']} |")
    open(os.path.join(ROT, 'rapport', 'bygg', 'sv-avvik.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print(len(ut), 'hus:', dict(c))


if __name__ == '__main__':
    main()
