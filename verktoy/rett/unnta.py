"""Bygger UNNTA-lista for sv_rett_plan.py: godkjente vegger (kilder/gate/rett-*.json) = «ferdig»; prøvde panoramaer per vegg
(rapport/gate/sv_rett*/hent-*.json) som ikke ga godkjent lesning = lista over panoramaer som ikke skal tas igjen.
    python3 verktoy/rett/unnta.py > <unnta.json>"""
import json, os, glob
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ut = {}
for f in glob.glob(os.path.join(ROT, 'rapport', 'gate', 'sv_rett*', 'hent-*.json')):
    for k, v in json.load(open(f, encoding='utf8')).items():
        if v.get('pano'): ut.setdefault(k, []).append(v['pano'])
for f in glob.glob(os.path.join(ROT, 'kilder', 'gate', 'rett-*.json')):
    for r in json.load(open(f, encoding='utf8')):
        if r.get('godkjent'): ut[r['bilde']] = 'ferdig'
print(json.dumps(ut, ensure_ascii=False))
