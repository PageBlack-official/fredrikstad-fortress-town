#!/usr/bin/env python3
"""Velg panorama per gatefasade (07.11): nyeste opptak som ser veggen rett nok forfra og på passe avstand.

    python3 verktoy/sv_velg.py   (kilder/gate/sv_plan.json + sv_lager*.json) -> kilder/gate/sv_skudd.json

Regel: blant panoramaene foran veggen (2–28 m ut fra den, inntil 60° fra normalen) vinner nyeste år; innen samme år det som står
rettest og nærmest 10 m. Ingen kandidat: planens eget punkt (Google velger nærmeste panorama), merket «uten_lager».
"""
import json, math, os, sys, glob
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag as D


def main():
    plan = json.load(open(os.path.join(ROT, 'kilder', 'gate', 'sv_plan.json')))
    pan = {}
    for f in glob.glob(os.path.join(ROT, 'kilder', 'gate', 'sv_lager*.json')):
        pan.update(json.load(open(f)).get('panoramaer', {}))
    P = []
    for pid, v in pan.items():
        x, y = D.til_modell(v['lon'], v['lat'])
        P.append((pid, x, y, v.get('aar') or 0, v.get('dato'), v['lat'], v['lon']))
    ut, uten = [], 0
    for s in plan:
        a, b, m, q = s['a'], s['b'], s['m'], s['q']
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = uy, -ux
        if (q[0] - m[0]) * nx + (q[1] - m[1]) * ny < 0: nx, ny = -nx, -ny     # normalen peker mot gata
        best = None
        for pid, x, y, aar, dato, lat, lon in P:
            dx, dy = x - m[0], y - m[1]; d = math.hypot(dx, dy)
            if d < 2 or d > 28: continue
            ut_fra = (dx * nx + dy * ny) / d
            if ut_fra < 0.5: continue                                             # mer enn 60° fra normalen, eller bak veggen
            poeng = (aar, round(ut_fra, 1), -abs(d - 10))
            if best is None or poeng > best[0]:
                best = (poeng, pid, x, y, dato, lat, lon, d)
        r = dict(id=s['id'], del_=s['del'], deler=s['deler'], adresse=s['adresse'], gate=s['gate'], a=a, b=b, m=m, mlat=s['mlat'], mlon=s['mlon'])
        if best:
            _, pid, x, y, dato, lat, lon, d = best
            hd = (math.degrees(math.atan2(m[0] - x, m[1] - y)) + 360) % 360
            wj = L / s['deler']
            fov = max(60, min(100, 2 * math.degrees(math.atan(wj / 2 / max(d, 3))) * 1.4))
            r.update(pano=pid, lat=lat, lon=lon, dato=dato, heading=round(hd, 1), fov=round(fov), avstand=round(d, 1))
        else:
            uten += 1; r.update(pano=None, lat=s['lat'], lon=s['lon'], heading=s['heading'], fov=s['fov'], avstand=s['avstand'], uten_lager=True)
        ut.append(r)
    json.dump(ut, open(os.path.join(ROT, 'kilder', 'gate', 'sv_skudd.json'), 'w'), ensure_ascii=False, indent=0)
    aar = {}
    for r in ut:
        k = (r.get('dato') or '?')[-4:]; aar[k] = aar.get(k, 0) + 1
    print(f'{len(ut)} skudd, {len(pan)} panoramaer i lageret, {uten} uten kandidat; år: {dict(sorted(aar.items()))}')


if __name__ == '__main__':
    main()
