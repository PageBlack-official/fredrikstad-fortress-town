"""Regel (05.11): stedene i søket (data/steder.json, verktoy/steder.py) er til å stole på.
- hvert sted har id (ingen to like), navn, en kategori som finnes, plass innenfor det kartet tegner, og kilde
- et sted som peker på et bygg, peker på et bygg som finnes og ikke er skjult
- ingen kategori i søket er tom, og ingen to steder har samme navn innen 60 m (dobbeltoppføringer fra OSM)
- ingen to linjer i lista med samme kategori, navn og type (06.11); flere plasser står som «punkter» på ett sted
- OSM-stedene har hentedato, og den er ikke eldre enn 120 dager (åpningstider og nedlagte steder endrer seg)"""
import datetime, math, unicodedata
from _felles import *
S = data('steder'); bygg = {b['id']: b for b in data('bygg')}
kat = {k['id'] for k in S['kategorier']}
feil = []; linjer = []
xs = [p[0] for b in bygg.values() if b.get('p') and not b.get('skjul') for p in b['p']]; ys = [p[1] for b in bygg.values() if b.get('p') and not b.get('skjul') for p in b['p']]
UT = (min(xs) - 30, max(xs) + 30, min(ys) - 30, max(ys) + 30)
ids = [s.get('id') for s in S['steder']]
for i in sorted({i for i in ids if ids.count(i) > 1}): feil.append(f'- id brukt to ganger: {i}')
enkel = lambda n: ''.join(c for c in unicodedata.normalize('NFD', (n or '').lower()) if c.isalnum())
for s in S['steder']:
    hvem = s.get('id') or s.get('navn')
    if not s.get('navn'): feil.append(f'- {hvem}: mangler navn')
    if s.get('kategori') not in kat: feil.append(f"- {hvem}: kategori {s.get('kategori')} finnes ikke")
    if not (UT[0] <= s.get('x', 1e9) <= UT[1] and UT[2] <= s.get('y', 1e9) <= UT[3]): feil.append(f'- {hvem}: står utenfor kartet ({s.get("x")}, {s.get("y")})')
    if not s.get('kilde'): feil.append(f'- {hvem}: mangler kilde')
    if s.get('bygg_id') and (s['bygg_id'] not in bygg or bygg[s['bygg_id']].get('skjul')): feil.append(f"- {hvem}: peker på bygg {s['bygg_id']} som ikke finnes")
for k in kat:
    if not any(s['kategori'] == k for s in S['steder']): feil.append(f'- kategorien {k} er tom')
st = [s for s in S['steder'] if s['kategori'] not in ('toalett', 'parkering')]
for i, a in enumerate(st):
    for b in st[i + 1:]:
        if enkel(a['navn']) == enkel(b['navn']) and math.hypot(a['x'] - b['x'], a['y'] - b['y']) < 60: feil.append(f"- dobbel: {a['navn']} ({a['id']}, {b['id']})")
# lista viser hvert sted én gang (06.11: Parkering hadde samme gate to og tre ganger): samme kategori + navn + type skal være ett sted
# med «punkter»; typen står i typen, ikke i navnet; hver plass står i kartet
from collections import Counter as _C
for (k, n, t), c in _C((s['kategori'], enkel(s['navn']), s.get('type')) for s in S['steder']).items():
    if c > 1: feil.append(f'- {c} like linjer i lista: {n} ({t}, {k})')
for s in S['steder']:
    if 'beboerparkering' in s['navn'].lower() and s['navn'].lower() != 'beboerparkering': feil.append(f"- typen står i navnet: {s['navn']}")
    for p in s.get('punkter') or []:
        if not (UT[0] <= p['x'] <= UT[1] and UT[2] <= p['y'] <= UT[3]): feil.append(f"- {s['id']}: plass {p['id']} står utenfor kartet")
hentet = {s.get('hentet') for s in S['steder'] if s.get('kilde') == 'OpenStreetMap'}
for h in hentet:
    if not h: feil.append('- OSM-steder uten hentedato'); continue
    alder = (datetime.date.today() - datetime.date.fromisoformat(h)).days
    if alder > 120: feil.append(f'- OSM-stedene er {alder} dager gamle: kjør python3 verktoy/steder.py hent og bygg')
from collections import Counter
linjer.append('- ' + ', '.join(f'{k} {n}' for k, n in Counter(s['kategori'] for s in S['steder']).items()) + f"; {sum(1 for s in S['steder'] if s.get('bygg_id'))} i et bygg")
rapport('47_steder', not feil, (feil or ['- alle steder har id, kategori, plass, kilde og gyldig bygg']) + linjer)
