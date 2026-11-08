#!/usr/bin/env python3
"""Skuddlista for husene uten sikker veggfarge (rapport/farger/status.json, «uten_sikker»): sv_rett_plan.py med UNNTA (det som er prøvd) og bare panoramaer fra 2016 eller senere.
    python3 verktoy/rett/farge_skudd.py → kilder/gate/sv_farge_skudd.json, og «med_skudd»/«uten_skudd» i status.json. Henter ingenting."""
import json, os, subprocess, sys, tempfile
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATUS = os.path.join(ROT, 'rapport', 'farger', 'status.json'); UT = os.path.join(ROT, 'kilder', 'gate', 'sv_farge_skudd.json')
st = json.load(open(STATUS, encoding='utf8')); ider = sorted(st['uten_sikker'])
with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
    f.write(subprocess.check_output([sys.executable, os.path.join(ROT, 'verktoy', 'rett', 'unnta.py')], text=True))
print(subprocess.run([sys.executable, os.path.join(ROT, 'verktoy', 'sv_rett_plan.py')] + ider, env={**os.environ, 'UNNTA': f.name, 'SV_UT': UT, 'MIN_AAR': '2016'},
                     capture_output=True, text=True, check=True).stdout[:600])
os.unlink(f.name)
skudd = json.load(open(UT, encoding='utf8')); med = sorted({s['id'] for s in skudd})
st['med_skudd'] = med; st['uten_skudd'] = sorted(set(ider) - set(med))
json.dump(st, open(STATUS, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(f"{len(ider)} hus uten sikker farge: {len(skudd)} skudd på {len(med)} hus, {len(st['uten_skudd'])} hus uten panorama som ser en hel vegg fra 2016+")
