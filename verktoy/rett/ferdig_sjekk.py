#!/usr/bin/env python3
"""Er de 28 husene i kilder/gate/ferdig-kandidater.json tegnet og klare for Vegars dom? Oppgaven (rapport/ferdig/OPPGAVE3.md) er ikke ferdig før dette skriptet gir exit 0.
Bare Vegar kan si «ferdig». Lov sluttstatus per hus i kilder/ferdig.json, med «runde»: 2 (runde 1 teller ikke: kontrollbildene hadde ikke samme kamera):
  «tegnet»: rettet etter kildene, ingen kjente avvik, bevis-bildet finnes.
  «trenger_vegar»: bare når kilden ikke kan gi svaret. Krever feltene «sporsmal» og «forsokt», og bevis-bildet.
Minst 26 hus skal være tegnet. «åpen» og «usikker» er ikke sluttstatus.
    python3 verktoy/rett/ferdig_sjekk.py"""
import json, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAAL = 26
hus = [h['id'] for h in json.load(open(os.path.join(ROT, 'kilder', 'gate', 'ferdig-kandidater.json'), encoding='utf8'))]
reg = json.load(open(os.path.join(ROT, 'kilder', 'ferdig.json'), encoding='utf8'))
n = {'tegnet': 0, 'trenger_vegar': 0}; feil = []
for i in hus:
    v = reg.get(i) or {}; st = v.get('status'); bevis = v.get('bevis') or ''
    if v.get('runde') != 2: feil.append(f'{i}: ikke gjort i runde 2'); continue
    if not bevis or not os.path.exists(os.path.join(ROT, bevis)): feil.append(f'{i}: bevis-bildet mangler'); continue
    if st == 'tegnet' and not v.get('avvik'): n['tegnet'] += 1
    elif st == 'trenger_vegar' and v.get('sporsmal') and v.get('forsokt'): n['trenger_vegar'] += 1
    else: feil.append(f"{i}: {st}: {' | '.join(str(a) for a in v.get('avvik', []))[:120]}")
print(f"{len(hus)} hus: {n['tegnet']} tegnet (mål {MAAL}), {n['trenger_vegar']} trenger Vegar, {len(feil)} ikke lukket")
for f in feil: print('  ' + f)
sys.exit(0 if not feil and n['tegnet'] >= MAAL else 1)
