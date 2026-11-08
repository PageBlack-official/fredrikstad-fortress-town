#!/usr/bin/env python3
"""Street View-skudd for rettede fasader (07.11): hele gatefasaden med begge hjørner og takfoten i ett bilde, så bildet kan rettes ut
(verktoy/fasade_rett.py). Nattens skudd (sv_velg.py) var valgt for å se fasaden forfra på kort hold; de fleste kuttet et hjørne eller
takfoten. Her velges for hver gatevegg det panoramaet (kilder/gate/sv_lager.json) som ser hele veggen:
  - begge hjørner innenfor den vannrette synsvinkelen (fov 75 loddrett = 107° vannrett i 16:9; 8° margin hver side, Googles
    posisjon kan ligge 3–5 m feil),
  - takfoten under bildets overkant og bakken over underkanten (pitch 97t: 7° opp),
  - skrått høyst 60° fra veggens normal (ellers blir oppløsningen for dårlig i den fjerne enden),
  - nyeste år først, så nærmest.
    python3 verktoy/sv_rett_plan.py id id ...  → kilder/gate/sv_rett_skudd.json (samme felt som sv_skudd.json, pluss vegg og pitch)
Env: UNNTA (verktoy/rett/unnta.py), SV_UT (skuddfil), MIN_AAR (bare panoramaer fra det året eller senere: veggfarger krever 2016+)."""
import json, math, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG  # noqa: E402
FOV, PITCH, OYE = 75.0, 97.0, 2.5
HALV_V = math.degrees(math.atan(math.tan(math.radians(FOV / 2)) * 16 / 9))   # halv vannrett synsvinkel
MARGIN = 6.0

def main(ider):
    A = datalag.alle(); B = {x['id']: x for x in A['bygg']}
    omg = VG.Omgivelser(A['bygg'], A['veier'], A['gardsrom'])
    pan = json.load(open(os.path.join(ROT, 'kilder', 'gate', 'sv_lager.json')))['panoramaer']
    PP = [(k, np.array(datalag.til_modell(v['lon'], v['lat']), float), v) for k, v in pan.items()]
    # fri vegg: 4 m ut fra veggen står det ikke noe hus (landskap.veier har bare deler av gatene i byen)
    from shapely.geometry import Point, Polygon
    from shapely.strtree import STRtree
    polys = [Polygon(b['p']).buffer(0) for b in A['bygg'] if b.get('p') and len(b['p']) > 2 and not b.get('skjul')]
    tre = STRtree(polys)
    def vei_naer(q, r=None):
        pt = Point(float(q[0]), float(q[1]))
        return not any(polys[i].contains(pt) for i in tre.query(pt))
    from shapely.geometry import LineString
    def fri_sikt(P, q):
        # siktlinja fra panoramaet til et punkt 0,5 m foran veggen krysser ingen hus
        ls = LineString([(float(P[0]), float(P[1])), (float(q[0]), float(q[1]))])
        return not any(polys[i].intersects(ls) for i in tre.query(ls))
    # UNNTA (07.11 natt): JSON {"id-vegg": "ferdig" | [pano, ...]}: ferdig = veggen er godkjent lest; liste = panoramaer som er prøvd
    # (hjørner skjult, fasaden bak mur/trær, uskarp) og ikke skal tas igjen. Neste runde får da neste beste vinkel.
    unnta = json.load(open(os.environ['UNNTA'])) if os.environ.get('UNNTA') else {}
    min_aar = int(os.environ.get('MIN_AAR') or 0)
    ut, mangler = [], []
    for id_ in ider:
        x = B.get(id_)
        if x is None: continue
        h = float(x.get('h') or 6)
        for wi, w in enumerate(VG.vegger(x, omg, slaa_sammen=True)):
            a, c, n = np.array(w['a'], float), np.array(w['c'], float), np.array(w['n'], float)
            L = float(np.linalg.norm(c - a)); m = (a + c) / 2
            if L < 3 or not vei_naer(m + n * 3): continue
            u_ = unnta.get(f'{id_}-{wi}')
            if u_ == 'ferdig': continue
            beste = None
            for pid, P, v in PP:
                if u_ and pid in u_: continue
                if v.get('aar', 0) < min_aar: continue
                dv = P - m; d = float(np.linalg.norm(dv))
                if d < 4 or d > 40 or dv @ n < 2: continue
                skraa = math.degrees(math.acos(max(-1, min(1, (dv @ n) / d))))
                if skraa > 65: continue
                hd = math.degrees(math.atan2(m[0] - P[0], m[1] - P[1]))
                vink = []
                for q in (a, c):
                    r = q - P; vink.append(((math.degrees(math.atan2(r[0], r[1])) - hd + 540) % 360) - 180)
                if max(abs(t) for t in vink) > HALV_V - MARGIN: continue
                inn = n * 0.5
                if not all(fri_sikt(P, q + inn + (m - q) * 0.03) for q in (a, c, m)): continue
                naermest = min(float(np.linalg.norm(a - P)), float(np.linalg.norm(c - P)), d)
                topp = math.degrees(math.atan2(h - OYE, naermest)); bunn = math.degrees(math.atan2(-OYE, naermest))
                if topp > (PITCH - 90) + FOV / 2 - 3 or bunn < (PITCH - 90) - FOV / 2 + 3: continue
                n_ = (-v.get('aar', 0), d)
                if beste is None or n_ < beste[0]: beste = (n_, pid, P, v, hd, d, skraa)
            if beste is None: mangler.append(f'{id_} vegg {wi} ({L:.1f} m)'); continue
            _, pid, P, v, hd, d, skraa = beste
            ut.append({'id': id_, 'del_': wi, 'deler': 1, 'vegg': wi, 'adresse': x.get('adr') or '', 'pano': pid, 'lat': v['lat'], 'lon': v['lon'],
                       'dato': v.get('dato'), 'heading': round((hd + 360) % 360, 1), 'fov': FOV, 'pitch': PITCH, 'avstand': round(d, 1), 'skraa': round(skraa)})
    json.dump(ut, open(os.environ.get('SV_UT') or os.path.join(ROT, 'kilder', 'gate', 'sv_rett_skudd.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'{len(ut)} skudd, {len(mangler)} vegger uten panorama som ser hele veggen: ' + '; '.join(mangler[:12]))

if __name__ == '__main__':
    main(sys.argv[1:])
