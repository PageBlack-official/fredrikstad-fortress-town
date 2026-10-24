"""Legger målte høyder (vegg h og takhelning th, tilpasset per hus mot Kartverkets DOM−DTM) inn som rettelser. Bare høy og middels sikkerhet;
kirka bygges for seg (06_kirka). Idempotent: egne linjer tas ut før nye legges inn. Kjør: python3 -I rapport/hoyder/legg_inn.py"""
import json, os
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = json.load(open(os.path.join(ROT, 'rapport/hoyder/hoyder.json')))
B = json.load(open(os.path.join(ROT, 'data/bygg.json')))
R = [r for r in json.load(open(os.path.join(ROT, 'data/rettelser.json'))) if not r.get('grunn', '').startswith('Kartverket DOM')]
n = 0
for k, x in sorted(H.items(), key=lambda t: int(t[0])):
    i = int(k)
    if x.get('sikkerhet') not in ('høy', 'middels') or x.get('h_per_hus') is None or B[i].get('kirke'): continue
    g = f"Kartverket DOM−DTM 1 m, vegg og takhelning tilpasset per hus (rapport/hoyder), sikkerhet {x['sikkerhet']}, før {B[i]['h']} m"
    R.append({"emne": "bygg", "i": i, "op": "sett", "felt": "h", "verdi": x['h_per_hus'], "hvem": "Claude", "dato": "2026-10-24", "grunn": g})
    R.append({"emne": "bygg", "i": i, "op": "sett", "felt": "th", "verdi": x['takhelning'], "hvem": "Claude", "dato": "2026-10-24", "grunn": g})
    n += 1
json.dump(R, open(os.path.join(ROT, 'data/rettelser.json'), 'w'), ensure_ascii=False, indent=0)
print(n, 'hus fått målt høyde og takhelning')
