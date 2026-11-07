"""Veggfarger lest av rettede fasader (verktoy/rett, FARGER.md) inn som sider i kilder/streetview/avlesning.json, så fargeregelen
(verktoy/streetview_farger.py: nyeste Street View-dato vinner, ordet foran RGB) bruker dem. Bare lesninger merket sikre.
Idempotent: sider med kilde «rettet fasade 07.11» byttes ut.
    python3 verktoy/rett/farger_inn.py <farger-sider.json>"""
import json, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KILDE = os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json')
MERKE = 'rettet fasade 07.11'
avl = json.load(open(KILDE, encoding='utf8'))
for a in avl.values():
    a['sider'] = [s for s in (a.get('sider') or []) if s.get('kilde') != MERKE]
n = 0
for r in json.load(open(sys.argv[1], encoding='utf8')):
    a = avl.setdefault(r['id'], {'id': r['id'], 'sider': []})
    a.setdefault('sider', []).append(r['side']); n += 1
json.dump(avl, open(KILDE, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(n, 'sider fra rettede fasader')
