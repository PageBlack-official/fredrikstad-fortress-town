"""Legger målte høyder (vegg h og takhelning th, tilpasset per hus mot Kartverkets DOM−DTM) inn som rettelser. Bare høy og middels sikkerhet;
kirka bygges for seg (06_kirka). Idempotent: egne linjer tas ut før nye legges inn. Kjør: python3 -I rapport/hoyder/legg_inn.py"""
import json, os
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = json.load(open(os.path.join(ROT, 'rapport/hoyder/hoyder.json')))
import sys; sys.path.insert(0, ROT); import datalag
# husene med rettelsene lagt oppå (også nye bygg fra rettelseslaget, 29.10); plassene er de samme som i hoyder.json
raa = json.load(open(os.path.join(ROT, 'data/bygg.json')))
B = datalag.alle()['bygg']
NY_H = {r['id']: r['verdi'].get('h') for r in json.load(open(os.path.join(ROT, 'data/rettelser.json'))) if r['op'] == 'ny'}   # nye bygg: høyden de ble lagt inn med
import datetime
ALLE = json.load(open(os.path.join(ROT, 'data/rettelser.json')))
R = [r for r in ALLE if not r.get('grunn', '').startswith('Kartverket DOM')]
# en verdi som ikke er endret, beholder datoen den ble lagt inn; nye og endrede verdier får dagens dato
FOER = {(r['id'], r['felt']): r for r in ALLE if r.get('grunn', '').startswith('Kartverket DOM')}
def dato(i, felt, v):
    r = FOER.get((i, felt))
    return r['dato'] if r and r['verdi'] == v else datetime.date.today().isoformat()
n = 0
# målingen hører til huset med samme id (29.10: plassen i lista flyttet seg når et nytt bygg kom inn foran de andre nye,
# så høydene havnet på nabohuset); gamle målinger uten id faller tilbake til plassen
PLASS = {b['id']: j for j, b in enumerate(B)}
# unntak (30.10): hus der tilpasningen per hus måler feil (tårn i omrisset, DTM på vollen), lest av DOM for hånd med grunn
UNNTAK = json.load(open(os.path.join(ROT, 'kilder/hoyde-unntak.json')))['hus']
for k, x in sorted(H.items(), key=lambda t: int(t[0])):
    i = PLASS.get(x['id']) if x.get('id') else int(k)
    if i is None: continue
    if B[i].get('kirke'): continue
    # unntakene er lest av DOM for hånd og gjelder uansett sikkerhet på tilpasningen (30.10: lave tilbygg skilt ut av større omriss)
    if (x.get('sikkerhet') not in ('høy', 'middels') or x.get('h_per_hus') is None) and B[i]['id'] not in UNNTAK: continue
    g = f"Kartverket DOM−DTM 1 m, vegg og takhelning tilpasset per hus (rapport/hoyder), sikkerhet {x['sikkerhet']}, før {raa[i]['h'] if i < len(raa) else NY_H.get(B[i]['id'])} m"
    u = UNNTAK.get(B[i]['id'])
    if u:
        x = dict(x, h_per_hus=u['h'], takhelning=u['th']); g = f"Kartverket DOM−DTM lest for hånd (kilder/hoyde-unntak.json): {u['grunn']}"
    R.append({"emne": "bygg", "id": B[i]["id"], "op": "sett", "felt": "h", "verdi": x['h_per_hus'], "hvem": "Claude", "dato": dato(B[i]['id'], 'h', x['h_per_hus']), "grunn": g})
    R.append({"emne": "bygg", "id": B[i]["id"], "op": "sett", "felt": "th", "verdi": x['takhelning'], "hvem": "Claude", "dato": dato(B[i]['id'], 'th', x['takhelning']), "grunn": g})
    n += 1
# fløyer under felles tak (kilder/husdeling.json «felles_tak», Tøihuset 31.10): samme gesims og takhelning på alle, snittet av
# målingene veid med grunnflaten, så taket som er regnet for hele omrisset passer på hver fløy
from shapely.geometry import Polygon
HD = json.load(open(os.path.join(ROT, 'kilder/husdeling.json')))
for D in HD.get('deling', []):
    if not (D.get('felles_tak') and D.get('nye_id')): continue
    g = [D['id']] + D['nye_id']; areal = {b['id']: Polygon(b['p']).area for b in B if b['id'] in g}
    for felt in ('h', 'th'):
        L = [r for r in R if r.get('id') in g and r.get('felt') == felt and r.get('grunn', '').startswith('Kartverket DOM') and r['verdi'] is not None]
        if not L: continue
        v = round(sum(r['verdi'] * areal.get(r['id'], 0) for r in L) / max(1e-9, sum(areal.get(r['id'], 0) for r in L)), 2)
        for r in L: r['verdi'] = v; r['dato'] = dato(r['id'], felt, v); r['grunn'] += f"; felles tak med {', '.join(i for i in g if i != r['id'])} (snitt veid med grunnflaten)"
datalag.skriv_rettelser(R)
print(n, 'hus fått målt høyde og takhelning')
