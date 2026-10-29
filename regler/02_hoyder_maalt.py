"""Regel (Vegar 28.10): Kartverket er fasit for høyde, tegningene for fasade (regel 03). Hvert hus i Gamlebyen som er målt
i Kartverkets DOM−DTM (rapport/hoyder/hoyder.json, sikkerhet høy eller middels) skal stå med den målte vegghøyden (h) og
takhelningen (th), lagt inn som rettelser med grunn. Hus uten sikker måling (lav sikkerhet, ikke i DOM-en) beholder tegning/OSM
og listes her, så de står på lista til kvalitetssikringen kvartal for kvartal. Kirka bygges for seg (06_kirka) og måles i regel 13.
Fram til 28.10 målte regelen mot tegnet høyde (tegnet_h/1,72) og var rød på 194 hus; tegningene viser høyde fra tegnevinkelen,
ikke målt vegg, og Vegar valgte Kartverket som fasit."""
import json, os
from _felles import *
H = json.load(open(os.path.join(ROT, 'rapport', 'hoyder', 'hoyder.json')))
b = data('bygg')
feil = []; maalt = 0; umaalt = []; navnfeil = []
HID = {e['id']: e for e in H.values() if e.get('id')}     # målingen følger id-en (29.10), plassen bare for gamle målinger
for i, x in gamleby(b):
    if x.get('skjult') or x.get('kirke'): continue
    m = HID.get(x['id']) if HID else H.get(str(i))
    if m and m.get('navn') and x.get('navn') and m['navn'] != x['navn']: navnfeil.append(f"- bygg {i}: hoyder.json sier «{m['navn']}», data sier «{x['navn']}» (rekkefølgen i bygg.json er endret?)")
    if m and m.get('sikkerhet') in ('høy', 'middels') and m.get('h_per_hus') is not None:
        maalt += 1
        if abs(x.get('h', 0) - m['h_per_hus']) > 0.05: feil.append(f"- {x['id']} ({x.get('navn') or x.get('type')}): h {x.get('h')} m, Kartverket gir {m['h_per_hus']} m")
        elif m.get('takhelning') is not None and abs(x.get('th', -9) - m['takhelning']) > 0.02: feil.append(f"- {x['id']} ({x.get('navn') or x.get('type')}): th {x.get('th')}, Kartverket gir {m['takhelning']}")
    else:
        umaalt.append(f"{x['id']} ({x.get('navn') or x.get('type')}, h {x.get('h')} m, {'lav sikkerhet' if m else 'ikke målt'})")
ok = not feil and not navnfeil
linjer = [f"{maalt} hus står med Kartverkets målte høyde; {len(feil)} avviker; {len(umaalt)} hus uten sikker måling beholder tegning/OSM"] + navnfeil + feil
if umaalt: linjer.append('- uten sikker måling (til kvartal-QA): ' + '; '.join(umaalt))
rapport('02_hoyder_maalt', ok, linjer)
