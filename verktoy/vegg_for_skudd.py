#!/usr/bin/env python3
"""Veggen hvert rettet skudd er tatt av (kilder/gate/sv_rett_skudd.json, felt vegg), med venstre/høyre ende slik den står i bildet.
    python3 verktoy/vegg_for_skudd.py → JSON {id-del: {id, vegg, venstre, hoyre, lengde, h, n, adr}}"""
import json, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG  # noqa: E402
A = datalag.alle(); B = {x['id']: x for x in A['bygg']}
omg = VG.Omgivelser(A['bygg'], A['veier'], A['gardsrom'])
ut = {}
for s in json.load(open(os.path.join(ROT, 'kilder', 'gate', 'sv_rett_skudd.json'))):
    x = B[s['id']]; w = VG.vegger(x, omg, slaa_sammen=True)[s['vegg']]
    a, c, n = np.array(w['a'], float), np.array(w['c'], float), np.array(w['n'], float)
    hoyre_retn = np.array([-n[1], n[0]])
    v, h = (a, c) if (c - a) @ hoyre_retn > 0 else (c, a)
    ut[f"{s['id']}-{s['del_']}"] = {'id': s['id'], 'vegg': s['vegg'], 'venstre': [round(float(q), 3) for q in v], 'hoyre': [round(float(q), 3) for q in h],
                                    'lengde': round(float(np.linalg.norm(c - a)), 3), 'h': float(x.get('h') or 0), 'n': [round(float(q), 4) for q in n],
                                    'adr': x.get('adr') or ''}
print(json.dumps(ut, ensure_ascii=False))
