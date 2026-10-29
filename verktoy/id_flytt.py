"""Flytter hus over på riktig bnr-id etter Matrikkelens bygningspunkt (kilder/id-etter-matrikkel.json).

Huset som står der punktet står, er det fysiske huset; alt det har (omriss, høyde, tak, farger, fasade, piper, arker,
matrikkelfelt) legges på id-en som skal være dets. Har id-en et objekt fra før, settes feltene (sett); ellers lages det (ny).
Huset som mister sin id til et annet, skjules med grunn hvis ingen id i lista tar det. Id-er slettes aldri (LESMEG).
Idempotent: egne rettelser (grunn begynner med GRUNN) tas ut først, og alt regnes fra dataene uten dem.
Kjøres etter grunnmur.py, vinduer_regler.py og streetview_fasader.py (de bygger på plass, denne på id).

    python3 verktoy/id_flytt.py [--tørt]
"""
import json, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
from shapely.geometry import Polygon, Point

GRUNN = 'id etter Matrikkelen (29.10)'
DATO = '2026-10-29'
UTEN = {'id'}


def main(tørt=False):
    cfg = json.load(open(os.path.join(ROT, 'kilder', 'id-etter-matrikkel.json'), encoding='utf8'))
    ret = [r for r in datalag.les('rettelser') if not r.get('grunn', '').startswith(GRUNN)]
    d = datalag.alle(raa=True); grunn = [dict(x) for x in d['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(d, ret), grunn)
    B = d['bygg']; BY = {x['id']: x for x in B}
    pkt = {p['bygningsnummer']: p for p in json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json')))['punkter']}
    kilde = {}
    for f in cfg['flytt']:
        her = [x for x in B if not x.get('skjul') and x.get('gml') and Polygon(x['p']).buffer(0.05).contains(Point(*f['punkt']))]
        if len(her) != 1:
            raise SystemExit(f"{f['id']}: {len(her)} hus i punktet {f['punkt']}")
        kilde[f['id']] = her[0]['id']
    tatt = set(kilde.values())
    nye, logg = [], []
    for f in cfg['flytt']:
        t, s = f['id'], kilde[f['id']]
        if s == t:
            logg.append(f"{t}: står allerede riktig"); continue
        inn = {k: v for k, v in json.loads(json.dumps(BY[s])).items() if k not in UTEN}
        inn.pop('skjul', None)
        n = int(t[4:])
        if n in pkt:
            p = pkt[n]
            inn['matrikkel'] = [{k: p[k] for k in ('bygningsnummer', 'uuid', 'type', 'kulturminne', 'sefrak', 'adresser', 'matrikkelenheter')}] + \
                [m for m in (inn.get('matrikkel') or []) if m.get('bygningsnummer') not in (n,) and m.get('bygningsnummer') != (int(s[4:]) if s.startswith('bnr-') else None)]
        g = f"{GRUNN}: {f['grunn']}"
        if t in BY:
            for k in sorted(set(inn) | (set(BY[t]) - UTEN)):
                if k == 'skjul':
                    continue
                nye.append({"emne": "bygg", "id": t, "op": "sett", "felt": k, "verdi": inn.get(k), "hvem": "Claude", "dato": DATO, "grunn": g})
            if BY[t].get('skjul'):
                nye.append({"emne": "bygg", "id": t, "op": "sett", "felt": "skjul", "verdi": None, "hvem": "Claude", "dato": DATO, "grunn": g})
        else:
            nye.append({"emne": "bygg", "id": t, "op": "ny", "verdi": dict(id=t, **inn), "hvem": "Claude", "dato": DATO, "grunn": g})
        logg.append(f"{t} <- huset som hadde {s}")
    for s in tatt:
        if s not in kilde:            # huset ga fra seg id-en og fikk ingen ny: skjules
            ny_id = next(t for t, v in kilde.items() if v == s)
            nye.append({"emne": "bygg", "id": s, "op": "skjul", "hvem": "Claude", "dato": DATO,
                        "grunn": f"{GRUNN}: huset har id {ny_id} (Matrikkelen); denne id-en brukes ikke lenger"})
            logg.append(f"{s} skjult (huset er nå {ny_id})")
    # id-registeret: nye id-er legges til (bare tillegg)
    reg = os.path.join(ROT, 'kilder', 'id-register.txt')
    have = set(open(reg).read().split())
    nyreg = [f['id'] for f in cfg['flytt'] if f['id'] not in have]
    for l in logg: print(l)
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
        if nyreg:
            with open(reg, 'a') as fh:
                fh.write(''.join(i + '\n' for i in nyreg))
    print(f"{len(nye)} rettelser; nye id-er i registeret: {nyreg}")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
