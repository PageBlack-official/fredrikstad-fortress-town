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
for k, x in sorted(H.items(), key=lambda t: int(t[0])):
    i = int(k)
    if x.get('sikkerhet') not in ('høy', 'middels') or x.get('h_per_hus') is None or B[i].get('kirke'): continue
    g = f"Kartverket DOM−DTM 1 m, vegg og takhelning tilpasset per hus (rapport/hoyder), sikkerhet {x['sikkerhet']}, før {raa[i]['h'] if i < len(raa) else NY_H.get(B[i]['id'])} m"
    R.append({"emne": "bygg", "id": B[i]["id"], "op": "sett", "felt": "h", "verdi": x['h_per_hus'], "hvem": "Claude", "dato": dato(B[i]['id'], 'h', x['h_per_hus']), "grunn": g})
    R.append({"emne": "bygg", "id": B[i]["id"], "op": "sett", "felt": "th", "verdi": x['takhelning'], "hvem": "Claude", "dato": dato(B[i]['id'], 'th', x['takhelning']), "grunn": g})
    n += 1
datalag.skriv_rettelser(R)
print(n, 'hus fått målt høyde og takhelning')
