#!/usr/bin/env python3
"""Street View-plan (07.11): ett standpunkt per hus, foran husets gatefasade (den lengste veggen som har gate rett foran seg).

    python3 verktoy/sv_plan.py            -> kilder/gate/sv_plan.json

Per hus: veggen (a, b), punktet på gata rett foran (lat/lon), retning mot veggens midtpunkt og synsvinkel som rommer veggen.
Ingen bilder her; verktoy/sv_hent.mjs henter bildene (synlig Chromium, Google gir ikke Street View i hodeløs).
"""
import json, math, os, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag as D

GATER = {'residential', 'pedestrian', 'living_street', 'service', 'unclassified', 'tertiary', 'secondary', 'primary', 'footway', 'path', 'cycleway', 'track'}


def til_grader(x, y):
    mx = x / D._S + D._MX0; my = y / D._S + D._MY0
    return math.degrees(mx / D._R), math.degrees(2 * math.atan(math.exp(my / D._R)) - math.pi / 2)


def naermeste(p, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L))
    q = (ax + t * dx, ay + t * dy)
    return q, math.hypot(p[0] - q[0], p[1] - q[1])


def main():
    bygg = json.load(open(os.path.join(ROT, 'data', 'bygg.json')))
    veier = [v for v in json.load(open(os.path.join(ROT, 'data', 'veier.json'))) if (v.get('t') or {}).get('highway') in GATER]
    adr = {}
    for a in json.load(open(os.path.join(ROT, 'data', 'adresser.json'))):
        adr.setdefault(a['bygg_id'], []).append(a['adresse'])
    seg = [(v['p'][i], v['p'][i + 1], (v.get('t') or {}).get('name')) for v in veier for i in range(len(v['p']) - 1)]
    plan = []
    for h in bygg:
        P = h['p']; n = len(P)
        if n < 3: continue
        A = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n)) / 2
        best = None
        for i in range(n):
            a, b = P[i], P[(i + 1) % n]
            w = math.hypot(b[0] - a[0], b[1] - a[1])
            if w < 4: continue
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            ux, uy = (b[0] - a[0]) / w, (b[1] - a[1]) / w
            nx, ny = (uy, -ux) if A > 0 else (-uy, ux)          # utover
            for s0, s1, navn in seg:
                q, d = naermeste(m, s0, s1)
                if d > 30: continue
                fram = (q[0] - m[0]) * nx + (q[1] - m[1]) * ny
                if fram < 2 or fram < 0.8 * d: continue          # gata må ligge foran veggen, ikke på skrå bak
                score = d - 0.6 * w                                # nær gata og bred vegg
                if best is None or score < best[0]:
                    best = (score, a, b, m, q, d, w, navn)
        if not best: continue
        _, a, b, m, q, d, w, navn = best
        # lange vegger: ett bilde per ~22 m, hvert fra gata rett foran sin del (del = 0..k-1)
        k = max(1, math.ceil(w / 22))
        for j in range(k):
            t0, t1 = j / k, (j + 1) / k
            mj = (a[0] + (b[0] - a[0]) * (t0 + t1) / 2, a[1] + (b[1] - a[1]) * (t0 + t1) / 2)
            qj = min((naermeste(mj, s0, s1) for s0, s1, _n in seg), key=lambda r: r[1])[0] if k > 1 else q
            dj = max(3, math.hypot(mj[0] - qj[0], mj[1] - qj[1])); wj = w / k
            lon, lat = til_grader(*qj); mlon, mlat = til_grader(*mj)
            hd = (math.degrees(math.atan2(mj[0] - qj[0], mj[1] - qj[1])) + 360) % 360
            fov = max(60, min(110, 2 * math.degrees(math.atan(wj / 2 / dj)) * 1.35))
            plan.append({'id': h['id'], 'del': j, 'deler': k, 'adresse': adr.get(h['id'], []), 'gate': navn, 'a': a, 'b': b,
                         'm': [round(mj[0], 2), round(mj[1], 2)], 'q': [round(qj[0], 2), round(qj[1], 2)],
                         'lat': round(lat, 7), 'lon': round(lon, 7), 'mlat': round(mlat, 7), 'mlon': round(mlon, 7),
                         'heading': round(hd, 1), 'fov': round(fov), 'avstand': round(dj, 1), 'bredde': round(w, 1)})
    ut = os.path.join(ROT, 'kilder', 'gate', 'sv_plan.json')
    json.dump(plan, open(ut, 'w'), ensure_ascii=False, indent=1)
    hus = len({p['id'] for p in plan})
    print(f'{len(plan)} bilder for {hus} av {len(bygg)} hus med gatefasade; {len(bygg) - hus} uten gate foran (sorte sider, simuleres)')


def punkter(steg=10.0):
    """Punkter hver `steg` m langs gatene som har hus innen 25 m -> kilder/gate/sv_punkter.json (panoramalageret leter fra disse)."""
    bygg = json.load(open(os.path.join(ROT, 'data', 'bygg.json')))
    veier = [v for v in json.load(open(os.path.join(ROT, 'data', 'veier.json'))) if (v.get('t') or {}).get('highway') in GATER]
    sentra = [(sum(x for x, _ in h['p']) / len(h['p']), sum(y for _, y in h['p']) / len(h['p'])) for h in bygg if len(h['p']) >= 3]
    ut, sett = [], set()
    for v in veier:
        P = v['p']
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]; L = math.hypot(b[0] - a[0], b[1] - a[1])
            for k in range(int(L // steg) + 1):
                t = min(1, k * steg / max(L, 1e-9)); q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                if not any(math.hypot(q[0] - c[0], q[1] - c[1]) < 45 for c in sentra): continue
                nok = (round(q[0] / 6), round(q[1] / 6))
                if nok in sett: continue
                sett.add(nok)
                lon, lat = til_grader(*q)
                ut.append({'x': round(q[0], 1), 'y': round(q[1], 1), 'lat': round(lat, 7), 'lon': round(lon, 7)})
    json.dump(ut, open(os.path.join(ROT, 'kilder', 'gate', 'sv_punkter.json'), 'w'))
    print(len(ut), 'punkter langs gatene')


if __name__ == '__main__':
    punkter() if sys.argv[1:] == ['punkter'] else main()
