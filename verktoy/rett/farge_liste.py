#!/usr/bin/env python3
"""Husene i Gamlebyen som mangler veggfarge fra virkeligheten: vegg_kilde har verken «Street View» eller «Vegar». Skjulte hus, kirka og hus med egen fasademodell (Kaserna) er ute.
For hvert hus: bildene fra 2016 eller senere som alt finnes i rapport/gate/sv*/ (SV_ROT).
    python3 verktoy/rett/farge_liste.py → rapport/farger/husliste.json og husliste.md"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import farge_kandidater as FK

ROT = FK.ROT
A = FK.datalag.alle()
hus = [x for x in A['bygg'] if x.get('gml') and not x.get('skjul') and not x.get('kirke') and x['id'] not in FK.datalag.EGNE_FASADER
       and 'Street View' not in (x.get('vegg_kilde') or '') and 'Vegar' not in (x.get('vegg_kilde') or '')]
bilder = {}
for r in FK.les_bilder():
    bilder.setdefault(r['id'], []).append({'bilde': r['bilde'], 'mappe': r['mappe'], 'dato': r['dato'], 'pano': r['pano']})
ut = [{'id': x['id'], 'adresse': x.get('adr') or x.get('navn') or '', 'vegg_kilde': x.get('vegg_kilde'), 'bilder': bilder.get(x['id'], [])} for x in hus]
ut.sort(key=lambda h: (h['adresse'] == '', h['adresse'], h['id']))
os.makedirs(os.path.join(ROT, 'rapport', 'farger'), exist_ok=True)
json.dump({'hus': ut}, open(os.path.join(ROT, 'rapport', 'farger', 'husliste.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
med = sum(1 for h in ut if h['bilder'])
with open(os.path.join(ROT, 'rapport', 'farger', 'husliste.md'), 'w', encoding='utf8') as f:
    f.write(f'# Hus i Gamlebyen uten veggfarge fra virkeligheten\n\n{len(ut)} hus. {med} har Street View-bilder fra 2016 eller senere, {len(ut) - med} har ingen.\n\n| Id | Adresse | Fargen kommer fra | Bilder 2016+ |\n|---|---|---|---|\n')
    for h in ut:
        f.write(f"| {h['id']} | {h['adresse']} | {(h['vegg_kilde'] or 'ingen kilde')[:40]} | {', '.join(b['mappe'] + '/' + b['bilde'] + ' (' + b['dato'] + ')' for b in h['bilder']) or '–'} |\n")
print(f'{len(ut)} hus, {med} med bilder fra 2016 eller senere')
