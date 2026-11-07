#!/usr/bin/env python3
"""Hus der kartet og Street View-lesningen er uenige om antall åpninger på gatefasaden (07.11).
Leser kilder/gate/avlesning-med-bildene-07nov.json (lesningene fra bildene), sammenligner med kartet slik det står nå.
Bare hele fasader i ett bilde (deler = 1) med begge hjørner lest. -> rapport/gate/avvik-07nov.json"""
import json, math, os, sys
import numpy as np
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in dir() else '.'
R = os.path.expanduser('~/sot-maskin/gate'); sys.path[:0] = [R, R + '/verktoy']
import datalag as D, vegger as VG, streetview_fasader as SVF
avl = json.load(open(R + '/kilder/gate/avlesning-med-bildene-07nov.json'))
sp = {p['navn']: p for p in json.load(open(R + '/kilder/gate/standpunkter-med-bildene-07nov.json'))}
d = D.alle()
B = {x['id']: x for x in d['bygg']}
omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
ut = []
for a in avl:
    if a.get('hvem') != 'Claude' or a.get('deler', 1) != 1 or not a.get('maalt'): continue
    hj = a.get('hjorner') or {}
    if hj.get('u_venstre') is None or hj.get('u_hoyre') is None: continue
    x = B.get(a['id']); s = sp.get(a['standpunkt'])
    if not x or not s: continue
    C = np.array(D.til_modell(s['lon'], s['lat'])); v = np.array(x['p'], float).mean(axis=0) - C
    V = VG.vegger(x, omg, slaa_sammen=True)
    wi, _ = SVF.gatevegg(x, V, omg, C, (math.degrees(math.atan2(v[0], v[1])) + 360) % 360)
    if wi is None: continue
    kart = [e for e in (x.get('vind') or []) if VG.naermeste_vegg(V, np.array(e[:2]))[0] == wi]
    sv = [e for e in a['maalt'] if hj['u_venstre'] - 0.01 <= (e['u0'] + e['u1']) / 2 <= hj['u_hoyre'] + 0.01]
    nk_d = sum(1 for e in kart if e[9] in (1, 2)); ns_d = sum(1 for e in sv if e.get('type') in ('dor', 'dør', 'port'))
    if abs(len(kart) - len(sv)) >= 2 or nk_d != ns_d:
        ut.append(dict(id=a['id'], adresse=x.get('adresse') or x.get('navn'), bilde=a['standpunkt'][3:], dato=s.get('dato'),
                       kart=len(kart), streetview=len(sv), dorer_kart=nk_d, dorer_sv=ns_d, merknad=a.get('merknad')))
ut.sort(key=lambda r: -abs(r['kart'] - r['streetview']))
json.dump(ut, open(R + '/rapport/gate/avvik-07nov.json', 'w'), ensure_ascii=False, indent=1)
n = sum(1 for a in avl if a.get('hvem') == 'Claude' and a.get('deler', 1) == 1 and (a.get('hjorner') or {}).get('u_venstre') is not None and (a.get('hjorner') or {}).get('u_hoyre') is not None and a.get('maalt'))
print(f'{len(ut)} av {n} sammenlignbare fasader avviker (antall åpninger ±2 eller dører)')
for r in ut[:12]: print(' ', r['id'], r['adresse'], 'kart', r['kart'], 'SV', r['streetview'], 'dører', r['dorer_kart'], r['dorer_sv'])
