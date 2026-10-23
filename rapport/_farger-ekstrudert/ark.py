"""Kontrollark for visuell dom: 2019-utsnitt med fotavtrykket (magenta, ligger på mønehøyde i tegningen), dagens farge og
registerforslaget under. 12 hus per ark. Bruk: python3 -I ark.py -> rapport/farger-dom/ark-NN.png + kandidater.json"""
import json, numpy as np, sys, os
H_ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H_, '..', '_farger2019'))
import felles2019 as F
from PIL import Image, ImageDraw, ImageFont
M = np.load(os.path.join(F.ROT, 'pdf/affin2.npy')); b = F.last_bygg(); im = Image.fromarray(F.last_2019())
reg = json.load(open(os.path.join(H_, '..', 'farger2019.json')))
def proj(p): return F.px2019(np.c_[np.asarray(p, float), np.ones(len(p))] @ M)
kand = [i for i, x in enumerate(b) if x.get('p') and not x.get('skjul') and (reg[str(i)].get('vegg') or reg[str(i)].get('tak') or 'ingen husflate' in (reg[str(i)].get('merknad') or ''))]
json.dump(kand, open(os.path.join(H_, '..', 'farger-dom', 'kandidater.json'), 'w'))
CW, CH, S = 170, 150, 2; font = ImageFont.load_default()
def sw(d, xy, c, txt):
    x, y = xy
    if c: d.rectangle([x, y, x + 60, y + 26], fill=tuple(c), outline='black')
    else: d.rectangle([x, y, x + 60, y + 26], outline='gray'); d.text((x + 8, y + 8), '—', fill='gray', font=font)
    d.text((x + 64, y + 8), txt, fill='black', font=font)
for n in range(0, len(kand), 12):
    ark = Image.new('RGB', (4 * (CW * S + 14) + 10, 3 * (CH * S + 110) + 10), 'white'); D = ImageDraw.Draw(ark)
    for j, i in enumerate(kand[n:n + 12]):
        x = b[i]; P = proj(x['p']); cx, cy = P.mean(axis=0); cy += x['h'] * 1.2   # senter litt under mønet, der huset står
        crop = im.crop((int(cx - CW / 2), int(cy - CH / 2), int(cx + CW / 2), int(cy + CH / 2))).resize((CW * S, CH * S)); d = ImageDraw.Draw(crop)
        T = lambda q: ((q[0] - (cx - CW / 2)) * S, (q[1] - (cy - CH / 2)) * S)
        d.polygon([T(q) for q in P], outline='magenta', width=2)
        d.rectangle([0, 0, 70, 16], fill='white'); d.text((3, 3), f'bygg {i}', fill='black', font=font)
        ox, oy = 10 + (j % 4) * (CW * S + 14), 10 + (j // 4) * (CH * S + 110)
        ark.paste(crop, (ox, oy)); r = reg[str(i)]
        sw(D, (ox, oy + CH * S + 6), x.get('vegg'), 'vegg i dag'); sw(D, (ox + 170, oy + CH * S + 6), x.get('tak'), 'tak i dag')
        sw(D, (ox, oy + CH * S + 40), r.get('vegg'), f"vegg forslag ({r.get('sikkerhet','')})"); sw(D, (ox + 170, oy + CH * S + 40), r.get('tak'), 'tak forslag')
        D.text((ox, oy + CH * S + 74), (x.get('navn') or x.get('adr') or '')[:40] + f"  h {x['h']}", fill='black', font=font)
    ark.save(os.path.join(H_, '..', 'farger-dom', f'ark-{n // 12 + 1:02d}.png'))
print(len(kand), 'hus,', (len(kand) + 11) // 12, 'ark')
