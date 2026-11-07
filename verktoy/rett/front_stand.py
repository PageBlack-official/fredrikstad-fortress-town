"""Standpunkter rett foran hver godkjente rettede fasade (kilder/gate/rett-*.json), for gatekamera.mjs: kontroll av at modellen
viser det som ble lest. python3 verktoy/rett/front_stand.py > <fil>.json, så node verktoy/gatekamera.mjs ut/enkel/index.html <fil>.json <utmappe>"""
import json, glob, math, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROT)
import datalag
d = datalag.alle(); B = {x['id']: x for x in d['bygg']}
def til_ll(x, y):
    mx = x / datalag._S + datalag._MX0; my = y / datalag._S + datalag._MY0
    return math.degrees(mx / datalag._R), math.degrees(2 * math.atan(math.exp(my / datalag._R)) - math.pi / 2)
ut = []
for f in sorted(glob.glob(os.path.join(ROT, 'kilder', 'gate', 'rett-*.json'))):
    for r in json.load(open(f, encoding='utf8')):
        if not r.get('godkjent') or r['id'] in datalag.EGNE_FASADER: continue
        a, c = np.array(r['venstre'], float), np.array(r['hoyre'], float); m = (a + c) / 2; u = (c - a) / np.linalg.norm(c - a)
        n = np.array([u[1], -u[0]]); cen = np.mean(np.array(B[r['id']]['p'], float), axis=0)
        if np.dot(n, m - cen) < 0: n = -n
        D = max(r['lengde'] * 0.85, r['h'] * 1.5, 10.0); cam = m + n * D
        lon, lat = til_ll(*cam); v = m - cam
        ut.append({'navn': r['bilde'], 'pano': '', 'dato': '', 'lat': lat, 'lon': lon, 'heading': (math.degrees(math.atan2(v[0], v[1])) + 360) % 360,
                   'pitch': 88.4, 'fov': 75, 'oye': round(min(r['h'] / 2, 4.0), 1)})
print(json.dumps(ut))
