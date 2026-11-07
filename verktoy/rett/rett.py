"""Retter ut fasaden i et Street View-bilde: de fire hjørnene (hjørnelesingen) til et rett-forfra-bilde av veggen med kartets lengde
og husets takfothøyde, 50 px per meter, med meterrutenett (s fra venstre hjørne, z over bakken).
python3 rett.py vegger.json hjorner-*.json  → rett/<bilde>.jpg og rett/meta.json"""
import sys, json, glob, os
import numpy as np
from PIL import Image, ImageDraw
PPM = 50
V = json.load(open(sys.argv[1]))
H = []
for f in sys.argv[2:]: H += json.load(open(f))
UT = os.environ.get('UT', 'rett'); os.makedirs(UT, exist_ok=True); meta = {}
def koeff(dst, src):
    # PIL PERSPECTIVE: for utpunkt (x,y) → inn (a x + b y + c)/(g x + h y + 1), (d x + e y + f)/(g x + h y + 1)
    A = []; bb = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); bb.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); bb.append(v)
    return np.linalg.solve(np.array(A, float), np.array(bb, float)).tolist()
for r in H:
    b = r['bilde']; v = V.get(b)
    if not r.get('synlig', True) or not v or 'feil' in v: meta[b] = {'hoppet': r.get('grunn') or (v or {}).get('feil') or 'ikke synlig'}; continue
    if r.get('utenfor'): meta[b] = {'hoppet': 'fasaden går ut av bildet: ' + ','.join(r['utenfor'])}; continue
    im = Image.open(os.environ.get('SVDIR', '../sv') + f'/{b}.jpg').convert('RGB'); Wp, Hp = im.size
    L, Hm = v['lengde'], v['h']
    w, h = max(2, int(round(L * PPM))), max(2, int(round(Hm * PPM)))
    px = lambda q: (q[0] * Wp, q[1] * Hp)
    src = [px(r['tv']), px(r['th']), px(r['bh']), px(r['bv'])]
    dst = [(0, 0), (w, 0), (w, h), (0, h)]
    out = im.transform((w, h), Image.PERSPECTIVE, koeff(dst, src), Image.BICUBIC)
    # meterrutenett: loddrett hver meter (s), vannrett hver meter (z); tall hver annen
    big = Image.new('RGB', (w + 60, h + 40), 'white'); big.paste(out, (40, 10)); d = ImageDraw.Draw(big)
    for s in range(0, int(L) + 1):
        X = 40 + s * PPM; d.line([(X, 10), (X, 10 + h)], fill=(255, 0, 255) if s % 2 == 0 else (255, 150, 255), width=1)
        if s % 2 == 0: d.text((X - 3, h + 14), str(s), fill=(200, 0, 200))
    for z in range(0, int(Hm) + 1):
        Y = 10 + h - z * PPM; d.line([(40, Y), (40 + w, Y)], fill=(0, 170, 255) if z % 2 == 0 else (140, 210, 255), width=1)
        if z % 2 == 0: d.text((4, Y - 6), f'{z} m', fill=(0, 120, 220))
    big.save(f'{UT}/{b}.jpg', quality=90)
    meta[b] = {'lengde': L, 'h': Hm, 'ppm': PPM, 'x0': 40, 'y0': 10, 'w': w, 'hpx': h, 'id': v['id'], 'adr': v['adr']}
json.dump(meta, open(f'{UT}/meta.json', 'w'), ensure_ascii=False, indent=0)
print(sum(1 for m in meta.values() if 'hoppet' not in m), 'rettet,', sum(1 for m in meta.values() if 'hoppet' in m), 'hoppet over')
