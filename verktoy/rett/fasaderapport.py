"""Hvilke hus i Gamlebyen har fasader lest fra virkeligheten, og hvilke er simulert (07.11, nattplanens punkt «rapport»).
    python3 verktoy/rett/fasaderapport.py > rapport/fasadekilder.md"""
import json, os, sys, glob
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROT)
import datalag
d = datalag.alle()
gml = [x for x in d['bygg'] if x.get('gml') and not x.get('skjul')]
godkj = set()
for f in glob.glob(os.path.join(ROT, 'kilder', 'gate', 'godkjent-*.json')):
    j = json.load(open(f, encoding='utf8'))
    for e in (j if isinstance(j, list) else j.get('hus', j.get('godkjent', []))):
        godkj.add(e if isinstance(e, str) else e.get('id'))
NAVN = {'kvartaltegning': 'Vegars kvartaltegning (2015)', 'streetview': 'Street View, automatisk lest', 'antatt': 'simulert etter regler'}
rader = []
for x in gml:
    kilde = x.get('fasade_kilde') or 'antatt'
    rett = x.get('fasade_rett') or []
    if rett: k = f"Street View rettet og lest i meter ({len(rett)} vegg{'er' if len(rett) > 1 else ''}), resten: {NAVN.get(kilde, kilde)}"
    elif x['id'] in godkj: k = 'Street View, øyekontrollert 07.11'
    else: k = NAVN.get(kilde, kilde)
    rader.append((x.get('adr') or '', x['id'], k))
teller = {}
for _, _, k in rader:
    kk = 'Street View rettet' if k.startswith('Street View rettet') else k
    teller[kk] = teller.get(kk, 0) + 1
print('# Fasadekilder i Gamlebyen\n')
print(f'{len(rader)} hus i kommunekartet innenfor Gamlebyen.\n')
for k, n in sorted(teller.items(), key=lambda t: -t[1]): print(f'- {k}: {n}')
print('\n| Adresse | Bygg | Fasaden er |\n|---|---|---|')
for a, i, k in sorted(rader, key=lambda r: (r[2], r[0])): print(f'| {a} | {i} | {k} |')
