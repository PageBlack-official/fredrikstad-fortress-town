"""Tegner de leste elementene oppå det rettede bildet (rett2/), slik at lesingen kan kontrolleres med øyet → kontroll/<bilde>.jpg"""
import json,glob,os
from PIL import Image,ImageDraw
M=json.load(open('rett2/meta.json')); os.makedirs('kontroll',exist_ok=True)
F={'vindu':(0,255,0),'butikk':(0,200,255),'dor':(255,60,0),'port':(255,0,200),'oksoye':(255,255,0)}
for f in sorted(glob.glob('ute/el-*.json')):
    for r in json.load(open(f)):
        m=M[r['bilde']]; im=Image.open(f"rett2/{r['bilde']}.jpg").convert('RGB'); d=ImageDraw.Draw(im)
        if r.get('ok'):
            for e in r['elementer']:
                X=lambda s:m['x0']+s*m['ppm']; Y=lambda z:m['y0']+m['hpx']-z*m['ppm']
                d.rectangle([X(e['s0']),Y(e['z1']),X(e['s1']),Y(e['z0'])],outline=F.get(e['type'],(255,255,255)),width=3)
        d.text((44,12),('OK ' if r.get('ok') else 'IKKE OK ')+(r.get('telling') or r.get('grunn',''))[:120],fill=(255,255,0))
        im.save(f"kontroll/{r['bilde']}.jpg",quality=88)
