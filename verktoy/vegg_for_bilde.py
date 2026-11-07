#!/usr/bin/env python3
"""Hvilken vegg i kartet et Street View-bilde viser (07.11, rettet fasade): for hvert bilde (id-del) veggen gate_avlesning ville valgt
(standpunktets retning mot huset), med endepunkter i den rekkefølgen de står i bildet (venstre først), lengde og husets takfothøyde.
    python3 verktoy/vegg_for_bilde.py bilde1 bilde2 ...  → JSON {bilde: {id, vegg, venstre:[x,y], hoyre:[x,y], lengde, h, n:[nx,ny]}}"""
import json, math, os, sys, glob
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG, streetview_fasader as SVF  # noqa: E402
import gate_avlesning as GA  # noqa: E402

def main(bilder):
    kam = {}
    for f in glob.glob(os.path.join(ROT, 'rapport', 'gate', 'sv', 'hent-*.json')):
        kam.update({k: v for k, v in json.load(open(f)).items() if not k.startswith('_')})
    ret, d, grunn = GA.tilstand()
    B = {x['id']: x for x in d['bygg']}
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    ut = {}
    for bilde in bilder:
        id_ = bilde.rsplit('-', 1)[0]; x = B.get(id_); sp = kam.get(bilde)
        if x is None or sp is None: ut[bilde] = {'feil': 'finnes ikke'}; continue
        sp = dict(sp, bredde=1280, hoyde=720)
        C = np.array(datalag.til_modell(sp['lon'], sp['lat']))
        P = np.array(x['p'], float); v = P.mean(axis=0) - C
        heading = (math.degrees(math.atan2(v[0], v[1])) + 360) % 360
        V = VG.vegger(x, omg, slaa_sammen=True)
        wi, notat = SVF.gatevegg(x, V, omg, C, heading)
        if wi is None:
            for dh in sorted(range(-int(GA.vannrett_fov(sp)) // 2, int(GA.vannrett_fov(sp)) // 2 + 1, 5), key=abs):
                wi, notat = SVF.gatevegg(x, V, omg, C, (sp['heading'] + dh) % 360)
                if wi is not None: break
        if wi is None: ut[bilde] = {'id': id_, 'feil': notat}; continue
        w = V[wi]; a, c = np.array(w['a'], float), np.array(w['c'], float)
        # sett fra kameraet (som står foran veggen, på normalens side): venstre ende er den med størst kryssprodukt
        n = np.array(w['n'], float)
        hoyre_retn = np.array([-n[1], n[0]])          # mot høyre når man ser på veggen fra utsiden (som gate_avlesning)
        venstre, hoyre = (a, c) if (c - a) @ hoyre_retn > 0 else (c, a)
        ut[bilde] = {'id': id_, 'vegg': int(wi), 'venstre': [round(float(q), 3) for q in venstre], 'hoyre': [round(float(q), 3) for q in hoyre],
                     'lengde': round(float(np.linalg.norm(c - a)), 3), 'h': float(x.get('h') or 0), 'n': [round(float(q), 4) for q in n],
                     'adr': x.get('adr') or ''}
    print(json.dumps(ut, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1:])
