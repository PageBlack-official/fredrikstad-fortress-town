"""Legger til anslått vannrett bildeposisjon (u, 0..1) for veggens to ender i hvert rettet skudd, til hjelp for hjørnelesingen.
fov i Street View-lenka er loddrett; bildet er 16:9. Googles posisjon kan bomme 3–5 m, så anslaget er bare et hint.
    python3 verktoy/rett/anslag_u.py <vegger.json> <skudd.json> > <vegger-med-u.json>"""
import json, math, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROT)
import datalag
V = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2]))
for s in S:
    k = f"{s['id']}-{s['vegg']}" if f"{s['id']}-{s['vegg']}" in V else f"{s['id']}-{s.get('del_', '')}"
    v = V.get(k)
    if not v or 'feil' in v: continue
    cx, cy = datalag.til_modell(s['lon'], s['lat'])
    tan_h = math.tan(math.radians(s['fov'] / 2)) * 16 / 9
    for ende in ('venstre', 'hoyre'):
        x, y = v[ende]
        a = math.degrees(math.atan2(x - cx, y - cy)) - s['heading']
        a = (a + 180) % 360 - 180
        v['u_' + ende] = round(0.5 + math.tan(math.radians(a)) / (2 * tan_h), 3) if abs(a) < 89 else None
print(json.dumps(V, ensure_ascii=False))
