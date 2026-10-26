"""Kontrollark: fasadetegninger av antatte hus før og etter verktoy/vinduer_regler.py, og fasit-hus fra kvartaltegningene
til sammenligning. Tegnes rett fra dataene (ingen kvartaltegning i bildet): hver vegg rullet ut, vinduer og dører i mål.

    python3 rapport/vinduer/kontrollark.py      -> rapport/vinduer/kontrollark.png og kontrollark-fasit.png"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datalag, vegger as VG, vinduer_regler as VR, mal_tegningene as M

# utvalget: navngitte hus, uthus, rekkehus med felles vegg, to etasjer, hjørnehus; fasit-hus med lignende form
UTVALG = ['bnr-193867634', 'bnr-193869556', 'bnr-193868460', 'bnr-13415889', 'bnr-13416575', 'pb-2',
          'bnr-193820883', 'bnr-193867308', 'bnr-193869548', 'bnr-193868568']
FASIT = ['bnr-193867499', 'bnr-193868355', 'bnr-193868428', 'bnr-193868347', 'bnr-193868061', 'bnr-193972489']
SK = 9   # piksler per meter
try:
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
except OSError:
    F = FB = ImageFont.load_default()
FARGE = {'hoved': (200, 60, 50), 'gate': (220, 140, 60), 'side': (90, 120, 170), 'bak': (90, 150, 110), 'felles': (150, 150, 150)}


def data(med_nye):
    ret = datalag.les('rettelser')
    if not med_nye:
        ret = [r for r in ret if r.get('grunn') != VR.GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    return datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)


def fasade(dr, x0, y0, x, V, vind, gi, tittel):
    """Plan til venstre, veggene rullet ut til høyre. Gir høyden panelet brukte."""
    P = np.array(x['p']); mn = P.min(0); mx = P.max(0); s = min(110 / max(mx - mn), 6)
    dr.text((x0, y0), tittel, fill=(0, 0, 0), font=FB)
    oy = y0 + 22
    for i, w in enumerate(V):   # plan
        kl = M.klasse(V, i, gi); a = (w['a'] - mn) * s; c = (w['c'] - mn) * s
        dr.line([(x0 + a[0], oy + 120 - a[1]), (x0 + c[0], oy + 120 - c[1])], fill=FARGE[kl], width=4 if kl == 'hoved' else 2)
        m = (a + c) / 2; dr.text((x0 + m[0] - 4, oy + 120 - m[1] - 7), str(i + 1), fill=(0, 0, 0), font=F)
    per = M.fordel(V, vind); xx = x0 + 140; hmax = x['h']
    for i, w in enumerate(V):
        if w['L'] < 1.0: continue
        kl = M.klasse(V, i, gi); bw = w['L'] * SK; bh = hmax * SK; bunn = oy + 115
        if xx + bw > x0 + 1560: xx = x0 + 140; oy += int(bh) + 30; bunn = oy + 115
        dr.rectangle([xx, bunn - bh, xx + bw, bunn], fill=(242, 236, 224) if kl != 'felles' else (215, 215, 215), outline=FARGE[kl], width=2)
        for f0, f1 in w['fri']:
            if f1 - f0 < w['L'] - 0.3: dr.line([(xx + f0 * SK, bunn + 3), (xx + f1 * SK, bunn + 3)], fill=(60, 60, 60), width=2)
        for t, v in per.get(i, []):
            vx = xx + (t - v[7] / 2) * SK; vy = bunn - (v[2] + v[8] / 2) * SK
            dr.rectangle([vx, vy, vx + v[7] * SK, vy + v[8] * SK], fill=(60, 66, 84) if v[9] == 0 else (110, 70, 50))
        dr.text((xx + 2, bunn + 6), f"{i + 1} {kl} {w['L']:.1f} m", fill=FARGE[kl], font=F)
        xx += bw + 14
    return oy + 140 - y0


def ark(ider, ut, med_for):
    d_for, d_etter = data(False), data(True)
    b_for = {x['id']: x for x in d_for['bygg']}; b_etter = {x['id']: x for x in d_etter['bygg']}
    omg = VG.Omgivelser(d_etter['bygg'], d_etter['veier'], d_etter['gardsrom'])
    im = Image.new('RGB', (1600, 9000), (255, 255, 255)); dr = ImageDraw.Draw(im); y = 10
    dr.text((10, y), 'Vinduer og dører: ' + ('antatte hus, før (generisk rutenett) og etter (regler fra kvartaltegningene 27.10)' if med_for else 'fasit-hus fra kvartaltegningene (til sammenligning)'), fill=(0, 0, 0), font=FB); y += 22
    dr.text((10, y), 'Farger: rød = gatesiden, oransje = annen vegg mot gate, blå = side, grønn = bakside, grå = felles vegg (nabohus inntil). Strek under veggen = fri del. Mørk = vindu, brun = dør. 1 m = 9 px.', fill=(60, 60, 60), font=F); y += 26
    for bid in ider:
        x = b_etter[bid]; V = VG.vegger(x, omg, slaa_sammen=True); gi, hv = VG.gatesiden(V)
        navn = x.get('navn') or x.get('type')
        if med_for:
            y += fasade(dr, 10, y, b_for[bid], V, b_for[bid].get('vind') or [], gi, f"{bid} {navn} (h {x['h']} m, {x['type']}) FØR: {len(b_for[bid].get('vind') or [])}")
        y += fasade(dr, 10, y, x, V, x.get('vind') or [], gi, f"{bid} {navn} (h {x['h']} m, {x['type']}) {'ETTER' if med_for else 'FASIT'}: {len(x.get('vind') or [])}  gateside valgt etter {hv}")
        dr.line([(10, y - 4), (1590, y - 4)], fill=(200, 200, 200)); y += 6
    im.crop((0, 0, 1600, y + 10)).save(ut, optimize=True)
    print(ut, y)


if __name__ == '__main__':
    her = os.path.dirname(os.path.abspath(__file__))
    ark(UTVALG + sys.argv[1:], os.path.join(her, 'kontrollark.png'), True)
    ark(FASIT, os.path.join(her, 'kontrollark-fasit.png'), False)
