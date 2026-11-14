#!/usr/bin/env python3
"""Rett ut en LANG gatefasade som ikke får plass i ett Street View-panorama (14.11, CEO PAG-1594): flere frontale pano langs
veggen, hver rektifisert mot kjente kanter, stitchet i meter med overlapp til ett rett-forfra-bilde av hele veggen.

Gjenbrukbar modul (ikke engangsskript): samme utdata-format og meterrutenett som verktoy/rett/rett.py, men veggen dekkes av
flere BITER. Hver bit er et pano som ser en DEL av veggen frontalt nok; biten rektifiseres til sitt meter-intervall [s0, s1] på
veggen og limes inn på den felles meterlerreten (0..lengde i s, 0..h i z, 50 px/m). I overlapp vinner den biten som står nærmest
frontalt (minst «vekt» = midtavstand fra bitens eget sentrum), med en myk fjæring så skjøten ikke syns som en hard kant.

  python3 verktoy/rett/rett_lang.py <vegger.json> <biter.json>   -> UT/<vegg>.jpg + UT/meta.json   (UT=miljø, standard rett_lang)

vegger.json: {"<vegg-id>": {id, vegg, venstre:[x,y], hoyre:[x,y], lengde, h, adr?}}   (én post for HELE veggen)
biter.json:  [{vegg:"<vegg-id>", bilde:"<bildenavn i SVDIR>", s0, s1, tv:[u,v], th:[u,v], bh:[u,v], bv:[u,v]}]
             s0,s1 = meter langs veggen fra venstre hjørne som denne biten dekker; tv/th/bh/bv = de fire hjørnene av
             DEN DELVEGGEN (s0..s1, bakke..takfot) lest i bildet som andel (u vannrett 0..1, v loddrett 0..1).
SVDIR = mappa med <bilde>.jpg (standard ../sv). Les delveggens hjørner som i HJORNER.md, men for s0- og s1-snittet, ikke husets
hjørner: venstre kant = der s0-loddlinja står på veggen, høyre kant = der s1-loddlinja står (bruk nedløpsrør/port/vindusmidter/
vannbordet som vannrett linje til å treffe meteren)."""
import sys, json, os, glob
import numpy as np
from PIL import Image, ImageDraw

PPM = 50


def koeff(dst, src):
    # PIL PERSPECTIVE (samme som rett.py): utpunkt (x,y) -> inn (a x+b y+c)/(g x+h y+1), (d x+e y+f)/(g x+h y+1)
    A = []
    bb = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        bb.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        bb.append(v)
    return np.linalg.solve(np.array(A, float), np.array(bb, float)).tolist()


def main(veggfil, bitfil):
    V = json.load(open(veggfil, encoding='utf8'))
    biter = json.load(open(bitfil, encoding='utf8'))
    UT = os.environ.get('UT', 'rett_lang')
    SVDIR = os.environ.get('SVDIR', '../sv')
    os.makedirs(UT, exist_ok=True)
    meta = {}
    # gruppér biter per vegg
    per = {}
    for b in biter:
        per.setdefault(b['vegg'], []).append(b)
    for vid, bs in per.items():
        v = V.get(vid)
        if not v:
            meta[vid] = {'hoppet': 'ingen veggpost'}
            continue
        L, Hm = v['lengde'], v['h']
        W = max(2, int(round(L * PPM)))
        H = max(2, int(round(Hm * PPM)))
        akk = np.zeros((H, W, 3), float)   # vektet sum
        vekt = np.zeros((H, W), float)     # sum av vekter (myk fjæring i overlapp)
        for b in sorted(bs, key=lambda x: x['s0']):
            im = Image.open(os.path.join(SVDIR, f"{b['bilde']}.jpg")).convert('RGB')
            Wp, Hp = im.size
            px = lambda q: (q[0] * Wp, q[1] * Hp)
            s0, s1 = b['s0'], b['s1']
            w = max(2, int(round((s1 - s0) * PPM)))
            # rektifiser biten til sitt eget delrektangel (w x H)
            src = [px(b['tv']), px(b['th']), px(b['bh']), px(b['bv'])]
            dst = [(0, 0), (w, 0), (w, H), (0, H)]
            ut = im.transform((w, H), Image.PERSPECTIVE, koeff(dst, src), Image.BICUBIC)
            arr = np.asarray(ut, float)
            x0 = int(round(s0 * PPM))
            # fjæring: vekt faller mot 0 ved bitens venstre/høyre kant (lineær rampe over 0,6 m), så overlapp blandes mykt
            ramp = max(1, int(round(0.6 * PPM)))
            wv = np.ones(w, float)
            for i in range(min(ramp, w)):
                wv[i] = min(wv[i], (i + 1) / ramp)
                wv[w - 1 - i] = min(wv[w - 1 - i], (i + 1) / ramp)
            for xi in range(w):
                X = x0 + xi
                if X < 0 or X >= W:
                    continue
                akk[:, X, :] += arr[:, xi, :] * wv[xi]
                vekt[:, X] += wv[xi]
        m = vekt > 0
        out = np.zeros((H, W, 3), np.uint8)
        out[m] = np.clip(akk[m] / vekt[m][:, None], 0, 255).astype(np.uint8)
        big = Image.new('RGB', (W + 60, H + 40), 'white')
        big.paste(Image.fromarray(out), (40, 10))
        d = ImageDraw.Draw(big)
        for s in range(0, int(L) + 1):
            X = 40 + s * PPM
            d.line([(X, 10), (X, 10 + H)], fill=(255, 0, 255) if s % 2 == 0 else (255, 150, 255), width=1)
            if s % 2 == 0:
                d.text((X - 3, H + 14), str(s), fill=(200, 0, 200))
        for z in range(0, int(Hm) + 1):
            Y = 10 + H - z * PPM
            d.line([(40, Y), (40 + W, Y)], fill=(0, 170, 255) if z % 2 == 0 else (140, 210, 255), width=1)
            if z % 2 == 0:
                d.text((4, Y - 6), f'{z} m', fill=(0, 120, 220))
        big.save(f'{UT}/{vid}.jpg', quality=90)
        meta[vid] = {'lengde': L, 'h': Hm, 'ppm': PPM, 'x0': 40, 'y0': 10, 'w': W, 'hpx': H,
                     'id': v['id'], 'adr': v.get('adr', ''), 'biter': len(bs)}
    json.dump(meta, open(f'{UT}/meta.json', 'w'), ensure_ascii=False, indent=0)
    print(sum(1 for x in meta.values() if 'hoppet' not in x), 'vegger stitchet,',
          sum(1 for x in meta.values() if 'hoppet' in x), 'hoppet over')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('bruk: python3 verktoy/rett/rett_lang.py <vegger.json> <biter.json>   (env UT, SVDIR)')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
