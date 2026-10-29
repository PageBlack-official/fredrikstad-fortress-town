#!/usr/bin/env python3
"""Kontrollark for statuen på Torvet: rapport/torvet/statue.png.

    python3 verktoy/statue_ark.py

Tegner modellen (src/20_statuen-paa-torvet.js med data/statue.json) fra fire vinkler med verktoy/statue_ark.mjs, og setter ved siden
av frontvisningen referanseprofilen i samme målestokk: sokkelleddene og figurhøyden slik de står i dataene (målt i fotoene, se KILDER.md),
som omriss med vannrette hjelpelinjer gjennom hele arket. Linjene skal treffe leddene i modellen. Ingen fremmede bilder i arket:
referansen er tall og beskrivelse, kildene står som URL-er.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UT = os.path.join(ROT, 'rapport', 'torvet'); os.makedirs(UT, exist_ok=True)
import tempfile
TMP = tempfile.mkdtemp(prefix='statue-')     # panelene er mellomprodukt
subprocess.run(['node', os.path.join(ROT, 'verktoy', 'statue_ark.mjs'), os.path.join(TMP, 'statue.png')], check=True)
meta = json.load(open(os.path.join(TMP, 'statue-vinkler.json'), encoding='utf8'))
st = json.load(open(os.path.join(ROT, 'data', 'statue.json'), encoding='utf8'))[0]
paneler = [Image.open(os.path.join(TMP, f'statue-{i}.png')).convert('RGB') for i in range(4)]
W, H = paneler[0].size
PXM = H / 5.25; Y0 = 2.4 - 2.5            # statue_ark.mjs: ortografisk, 5,25 m høyt, sentrum y = 2,4
yp = lambda m: H - (m - Y0) * PXM         # meter over bakken -> rad i panelet (front/side/bak)
def _skrift():
    # en skrift med æøå: matplotlibs DejaVu (følger med pakken, samme på alle maskiner), ellers systemets, ellers Pillows innebygde
    kand = []
    try:
        import matplotlib; kand.append(os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans.ttf'))
    except ImportError:
        pass
    kand += ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/Library/Fonts/Arial Unicode.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf']
    return next((k for k in kand if os.path.exists(k)), None)
SKRIFT = _skrift()
f = lambda s: ImageFont.truetype(SKRIFT, s) if SKRIFT else ImageFont.load_default(size=s)
REF_W, TEKST_W, TOPP = 300, 620, 46
ark = Image.new('RGB', (REF_W + 4 * W + TEKST_W, H + TOPP + 30), (244, 241, 234)); d = ImageDraw.Draw(ark)
d.text((12, 10), f"Statuen på Torvet – {st['navn']} ({st['billedhugger']}, avduket {st['avduket']}): modellen fra fire vinkler mot referanseprofilen fra fotoene", fill=(30, 30, 30), font=f(20))
# referanseprofil i samme målestokk
cx = REF_W // 2; y = 0.0; linjer = []
for l in st['sokkel']:
    b0, b1 = l['b'], l.get('b2', l['b'])
    pts = [(cx - b0 / 2 * PXM, TOPP + yp(y)), (cx + b0 / 2 * PXM, TOPP + yp(y)), (cx + b1 / 2 * PXM, TOPP + yp(y + l['h'])), (cx - b1 / 2 * PXM, TOPP + yp(y + l['h']))]
    d.polygon(pts, outline=(180, 40, 40), width=2)
    d.text((6, TOPP + yp(y + l['h'] / 2) - 7), f"{l['del']} {l['b']:.2f}", fill=(140, 30, 30), font=f(11))
    y += l['h']; linjer.append(y)
fh = st['figur']['h'] * st.get('visningsskala', 1)
d.rectangle([cx - 0.3 * PXM, TOPP + yp(y + fh), cx + 0.3 * PXM, TOPP + yp(y)], outline=(180, 40, 40), width=2)
d.text((cx - 60, TOPP + yp(y + fh) - 18), f"figur {st['figur']['h']:.2f} m", fill=(140, 30, 30), font=f(13))
linjer.append(y + fh)
for i, p in enumerate(paneler):
    ark.paste(p, (REF_W + i * W, TOPP)); d.text((REF_W + i * W + 10, TOPP + 6), meta['vinkler'][i], fill=(40, 40, 40), font=f(15))
for m in [0.0] + linjer:                   # hjelpelinjer gjennom referansen og de tre ortografiske panelene
    yy = TOPP + yp(m); d.line([(0, yy), (REF_W + 3 * W, yy)], fill=(180, 40, 40), width=1)
d.text((REF_W + 3 * W - 140, TOPP + yp(linjer[-1]) - 16), f"{linjer[-1]:.2f} m", fill=(140, 30, 30), font=f(13))
# målestokk 1 m
x0 = REF_W + 10; d.line([(x0, TOPP + H - 8), (x0 + PXM, TOPP + H - 8)], fill=(0, 0, 0), width=3); d.text((x0, TOPP + H + 2), '1 m', fill=(0, 0, 0), font=f(13))
# tekst: hva kildene sier
tx = REF_W + 4 * W + 14; ty = TOPP + 4
rader = [('Hvem', f"{st['navn']} (innskrift på sokkelen: FREDERIK II). Ikke Christian V: Christian5.ai er C5-monogrammet."),
         ('Billedhugger', st['billedhugger']), ('Avduket', f"{st['avduket']} (byens 350-årsjubileum)"),
         ('Materiale', f"figur: {st['materiale']['figur']}; sokkel: {st['materiale']['sokkel']}"),
         ('Positur', st['figur']['positur']), ('Retning', f"ser mot {st['retning']}° (kompass), dvs. vest-nordvest; ryggen mot smuget mellom Torvgaten 61 og Infanterikasernen (som i alle fotoene fra 1925 til i dag)"),
         ('Plass', f"modell x={st['xy'][0]}, y={st['xy'][1]} (ortofoto 2024)"), ('Høyde i alt', f"{linjer[-1]:.2f} m (sokkel {linjer[-2]:.2f} m + figur {st['figur']['h']:.2f} m)"),
         ('Sikkerhet', st['sikkerhet']), ('Modellboks', ' '.join(f'{v:.2f}' for v in meta['boks']) + ' m')]
import textwrap
for k, v in rader:
    d.text((tx, ty), k, fill=(140, 30, 30), font=f(14)); ty += 18
    for linje in textwrap.wrap(v, 78):
        d.text((tx, ty), linje, fill=(30, 30, 30), font=f(13)); ty += 16
    ty += 6
d.text((tx, ty), 'Kilder', fill=(140, 30, 30), font=f(14)); ty += 18
for k in st['kilder']:
    for linje in textwrap.wrap(k, 82):
        d.text((tx, ty), linje, fill=(60, 60, 60), font=f(11)); ty += 14
ut = os.path.join(UT, 'statue.png'); ark.save(ut); print(ut, ark.size)
