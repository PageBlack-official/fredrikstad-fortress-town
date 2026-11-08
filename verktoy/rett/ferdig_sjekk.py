#!/usr/bin/env python3
"""Er de 28 husene i kilder/gate/ferdig-kandidater.json lukket? Oppgaven er ikke ferdig før dette skriptet gir exit 0.
Lov sluttstatus per hus i kilder/ferdig.json:
  «ferdig»: ingen avvik, bevis-bildet finnes.
  «trenger_vegar»: bare når kilden ikke kan gi svaret. Krever feltene «sporsmal» (ett spørsmål han kan svare ja/nei eller med et ord på) og «forsokt» (hva som er prøvd), og bevis-bildet.
«åpen» og «usikker» er ikke sluttstatus (Vegar 08.11: «Jobben var 28 hus»).
    python3 verktoy/rett/ferdig_sjekk.py"""
import json, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
hus = [h['id'] for h in json.load(open(os.path.join(ROT, 'kilder', 'gate', 'ferdig-kandidater.json'), encoding='utf8'))]
reg = json.load(open(os.path.join(ROT, 'kilder', 'ferdig.json'), encoding='utf8'))
n = {'ferdig': 0, 'trenger_vegar': 0}; feil = []
for i in hus:
    v = reg.get(i) or {}; st = v.get('status'); bevis = v.get('bevis') or ''
    if not bevis or not os.path.exists(os.path.join(ROT, bevis)): feil.append(f'{i}: bevis-bildet mangler'); continue
    if st == 'ferdig' and not v.get('avvik'): n['ferdig'] += 1
    elif st == 'trenger_vegar' and v.get('sporsmal') and v.get('forsokt'): n['trenger_vegar'] += 1
    else: feil.append(f"{i}: {st}: {' | '.join(str(a) for a in v.get('avvik', []))[:120]}")
print(f"{len(hus)} hus: {n['ferdig']} ferdig, {n['trenger_vegar']} trenger Vegar, {len(feil)} ikke lukket")
for f in feil: print('  ' + f)
sys.exit(1 if feil else 0)
