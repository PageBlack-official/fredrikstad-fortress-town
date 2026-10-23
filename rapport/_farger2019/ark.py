"""Per kvartaltegning: 2019-utsnittet til venstre, til høyre samme utsnitt med kvartalflatene fylt i forslagets farger (tak/vegg per bygg)."""
import sys, os, json
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
from felles2019 import *
from PIL import ImageDraw, ImageFont
UT = os.path.join(ROT, 'soc/rapport/farger2019-ark'); os.makedirs(UT, exist_ok=True)
f = json.load(open(os.path.join(ROT, 'soc/rapport/farger2019.json')))
KV = json.load(open(os.path.join(HER, 'kvartal.json')))
im = Image.open(os.path.join(ROT, 'kilder2019/brosjyre2019-3.jpg')).convert('RGB')
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
for navn in plassering():
    try:
        V = json.load(open(os.path.join(ROT, 'kvartal/vek/%s.json' % navn)))
    except FileNotFoundError:
        continue
    bb = kvartal_poly_2019(navn, [[0, 0], [V['w'], V['h']]])
    x0, y0 = (int(v) for v in bb[0]); x1, y1 = (int(v) for v in bb[1])
    a = im.crop((x0, y0, x1, y1))
    c = Image.new('RGB', a.size, (235, 235, 235)); dr = ImageDraw.Draw(c)
    tekst = []
    for bi, r in KV.items():
        rec = f.get(bi, {})
        for t in r['tak']:
            if t['kvartal'] != navn or not rec.get('tak'): continue
            p = kvartal_poly_2019(navn, V['o'][t['flate']]['p']) - (x0, y0)
            dr.polygon([tuple(q) for q in p], fill=tuple(rec['tak']), outline=(60, 60, 60))
        for v in r['vegger']:
            if v['kvartal'] != navn or not rec.get('vegg'): continue
            col = rec['vegg'] if v['retning'] == 'v' or not rec.get('veggs') else rec['veggs']
            p = kvartal_poly_2019(navn, V['o'][v['fasade']]['p']) - (x0, y0)
            dr.polygon([tuple(q) for q in p], fill=tuple(col), outline=(60, 60, 60))
            tekst.append((p.mean(axis=0), bi))
    for (px, py), bi in tekst:
        dr.text((px - 8, py - 6), bi, fill=(0, 0, 0), font=font)
    S = max(1.0, min(2.0, 900 / a.width))
    out = Image.new('RGB', (int(a.width * S) * 2 + 12, int(a.height * S)), 'white')
    out.paste(a.resize((int(a.width * S), int(a.height * S)), Image.LANCZOS), (0, 0))
    out.paste(c.resize((int(a.width * S), int(a.height * S)), Image.NEAREST), (int(a.width * S) + 12, 0))
    out.save(os.path.join(UT, navn + '.png'))
print('ark skrevet:', len(os.listdir(UT)))
