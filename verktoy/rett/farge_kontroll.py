#!/usr/bin/env python3
"""Kontroll av innflettede veggfarger (rapport/farger/kandidater.json).
    python3 verktoy/rett/farge_kontroll.py standpunkter <ut.json>            kamera per bilde, til verktoy/gatekamera.mjs
    python3 verktoy/rett/farge_kontroll.py sjekk                             kjeden skal ha satt fargen: vegg_kilde med Street View, samme kulør som ordet (exit 1 ellers)
    python3 verktoy/rett/farge_kontroll.py ark <for-mappe> <etter-mappe> <ut.jpg>   Street View | før | etter, én rad per bilde"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import farge_kandidater as FK
from PIL import Image, ImageDraw
F = os.path.join(FK.ROT, 'rapport', 'farger', 'kandidater.json')


def rader():
    alle = {(r['bilde'], f"{r['lat']}, {r['lon']} h {r['heading']}"): r for r in FK.les_bilder()}
    ut = []
    for k in json.load(open(F, encoding='utf8')):
        s = k['side']; b = s['retning'].split('verktoy/rett, ')[1].rstrip(')')
        r = alle.get((b, s['pano_url']))
        if r: ut.append((k, r))
    return ut


hva = sys.argv[1]
if hva == 'standpunkter':
    # gatekameraet tegner ikke pitch over 88,5 (LESMEG): samme retning, litt lavere blikk
    json.dump([{'navn': r['bilde'], 'pano': '', 'dato': r['dato'], 'lat': r['lat'], 'lon': r['lon'], 'heading': r['heading'], 'pitch': min(r['pitch'], 88.5), 'fov': r['fov'], 'oye': 2.5}
               for _, r in rader()], open(sys.argv[2], 'w', encoding='utf8'), ensure_ascii=False, indent=0)
elif hva == 'sjekk':
    B = {x['id']: x for x in FK.datalag.alle()['bygg']}; feil = 0; n = 0
    for k, r in rader():
        x = B[k['id']]; n += 1; o = k['side']['vegg_farge']
        ok = 'Street View' in (x.get('vegg_kilde') or '') and FK.T.samme_kulor(x.get('vegg'), FK.fra_ord(o, FK.VEGG))
        feil += not ok
        print('OK  ' if ok else 'FEIL', k['id'].ljust(16), o.ljust(11), x.get('vegg'), (x.get('vegg_kilde') or '')[:70])
    print(f'{n} sider, {feil} feil'); sys.exit(1 if feil else 0)
elif hva == 'ark':
    R = rader(); B, H = 427, 240; a = Image.new('RGB', (3 * B, len(R) * (H + 16)), 'white'); d = ImageDraw.Draw(a)
    for i, (k, r) in enumerate(R):
        y = i * (H + 16)
        for j, f in enumerate((r['fil'], os.path.join(sys.argv[2], r['bilde'] + '.png'), os.path.join(sys.argv[3], r['bilde'] + '.png'))):
            if os.path.exists(f): a.paste(Image.open(f).convert('RGB').resize((B, H)), (j * B, y))
        d.text((4, y + H + 2), f"{r['bilde']}  {k['side']['vegg_farge']}   Street View | før | etter", fill='black')
    os.makedirs(os.path.dirname(os.path.abspath(sys.argv[4])), exist_ok=True); a.save(sys.argv[4], quality=88)
