"""FORSLAG til ny regel 02 (legges i regler/ når Vegar har godkjent målte høyder):
Høyden skal komme fra Kartverkets høydemodell (DOM−DTM 1 m) der målingen er sikker. For hvert hus med sikkerhet høy/middels i
rapport/hoyder/hoyder.json skal kartets vegg h og takhelning th ligge innen 0,3 m / 0,05 av målingen. Kvartaltegningens tegnet_h
gir i snitt 2,7 m for høyt (målt 24.10) og er ikke lenger fasit for høyde."""
import json, os
from _felles import *
H = json.load(open(os.path.join(ROT, 'rapport/hoyder/hoyder.json')))
b = data('bygg'); avvik = []
for k, x in H.items():
    i = int(k)
    if x.get('sikkerhet') not in ('høy', 'middels') or x.get('h_per_hus') is None or b[i].get('kirke'): continue
    if abs(b[i]['h'] - x['h_per_hus']) > 0.3 or abs(b[i].get('th', 0.82) - x['takhelning']) > 0.05:
        avvik.append(f"- bygg {i}: h {b[i]['h']} / th {b[i].get('th', 0.82)}, målt {x['h_per_hus']} / {x['takhelning']}")
rapport('02_hoyder_maalt', not avvik, [f"{len(avvik)} hus avviker fra målt høyde"] + avvik[:40])
