#!/usr/bin/env python3
"""Bygg bevis-montasje per hus: Street View | (før) | etter, én rad per lest/gatevegg, fra samme kamera.
Leser rapport/ferdig/mapping.json (id, vegg, navn, sv) og henter render <navn>.png fra oppgitte render-mapper.
Modell-rendrene strekkes med autocontrast (sol brenner ut fasader) før montasje, slik runde 1 gjorde.

  python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r2 [--for /tmp/f22/for-renders] [--ut rapport/ferdig] [id ...]

Uten --for lages SV | etter (to kolonner). Med --for lages SV | før | etter (tre kolonner).
Standard --ut er rapport/ferdig (skriver <id>.jpg = det ferdig_sjekk.py ser etter)."""
import json, os, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def arg(flag, standard=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return standard

etter_dir = arg('--etter', os.path.join(ROT, 'rapport', 'ferdig', 'renders_r2'))
for_dir = arg('--for')
ut_dir = arg('--ut', os.path.join(ROT, 'rapport', 'ferdig'))
flagg = {'--etter', '--for', '--ut'}
ids = [a for a in sys.argv[1:] if not a.startswith('--') and sys.argv[sys.argv.index(a) - 1] not in flagg]

RADH = 360   # høyde per bilde i montasjen
def last(sti, strekk=False):
    im = Image.open(sti).convert('RGB')
    if strekk:
        im = ImageOps.autocontrast(im, cutoff=1, preserve_tone=True)
    w = int(im.width * RADH / im.height)
    return im.resize((w, RADH))

def merk(im, tekst):
    d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    except Exception: f = ImageFont.load_default()
    d.rectangle([0, 0, 8 + d.textlength(tekst, font=f), 30], fill=(0, 0, 0))
    d.text((4, 3), tekst, fill=(255, 255, 255), font=f)
    return im

mapping = json.load(open(os.path.join(ROT, 'rapport', 'ferdig', 'mapping.json'), encoding='utf8'))
per_hus = {}
for e in mapping:
    per_hus.setdefault(e['id'], []).append(e)

os.makedirs(ut_dir, exist_ok=True)
mål = ids or list(per_hus.keys())
for hid in mål:
    vegger = sorted(per_hus.get(hid, []), key=lambda e: e['wall'])
    if not vegger:
        print(f'{hid}: ingen vegger i mapping'); continue
    rader = []
    for e in vegger:
        kol = []
        svp = os.path.join(ROT, e['sv'])
        if os.path.exists(svp): kol.append(merk(last(svp), f"SV v{e['wall']}"))
        if for_dir:
            fp = os.path.join(for_dir if os.path.isabs(for_dir) else os.path.join(ROT, for_dir), e['navn'] + '.png')
            if os.path.exists(fp): kol.append(merk(last(fp, True), 'for'))
        ep = os.path.join(etter_dir if os.path.isabs(etter_dir) else os.path.join(ROT, etter_dir), e['navn'] + '.png')
        if os.path.exists(ep): kol.append(merk(last(ep, True), 'etter'))
        if not kol: continue
        bredde = sum(k.width for k in kol) + 6 * (len(kol) - 1)
        rad = Image.new('RGB', (bredde, RADH), (255, 255, 255))
        x = 0
        for k in kol:
            rad.paste(k, (x, 0)); x += k.width + 6
        rader.append(rad)
    if not rader: print(f'{hid}: ingen bilder'); continue
    W = max(r.width for r in rader)
    H = sum(r.height for r in rader) + 6 * (len(rader) - 1)
    ut = Image.new('RGB', (W, H), (255, 255, 255))
    y = 0
    for r in rader:
        ut.paste(r, (0, y)); y += r.height + 6
    utp = os.path.join(ut_dir, hid + '.jpg')
    ut.save(utp, quality=88)
    print(f'{hid}: {len(rader)} rader -> {utp}')
