"""Nærbilder for kontrollen av byggene (30.10): modellen så tett som kartet lar deg zoome (zoom 6), med pikseltetthet 2, så
hvert vindu kan telles, ved siden av kvartaltegningen. Én til tre visninger per tegning (husrekkene i tegningen, 55 m per bilde).

    python3 verktoy/bygg_naer.py visninger        rapport/bygg/_arbeid/naer-visninger.json
    DPR=2 node verktoy/kvartal_bilder.mjs ut/enkel/index.html rapport/bygg/_arbeid/naer-visninger.json rapport/bygg/_arbeid/naer2
    python3 verktoy/bygg_naer.py ark [navn …]     rapport/bygg/naer/<tegning>-<k>.jpg (tegning + nærbilde + tabell)
"""
import json, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
from shapely.geometry import Polygon, MultiPoint
ARB = os.path.join(ROT, 'rapport', 'bygg', '_arbeid'); UT = os.path.join(ROT, 'rapport', 'bygg', 'naer')
VIS = os.path.join(ARB, 'naer-visninger.json'); BILDER = os.path.join(ARB, 'naer2')
RUTE = 55.0


def hus_i_tegning(navn):
    K = json.load(open(os.path.join(ROT, 'kilder', 'fasade-kobling.json'), encoding='utf8'))
    ids = list((K.get(navn) or {}).get('hus', {}))
    try:
        import bygg_ark
        ids += [i for i in bygg_ark.husliste(navn, datalag.alle()) if i not in ids]
    except StopIteration:
        pass
    return ids


def visninger():
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg'] if not x.get('skjul')}
    navn = [v['n'] for v in json.load(open(os.path.join(ARB, 'visninger.json')))] + ['Toihuset']
    ut = []
    for n in navn:
        if n == 'kirke':
            pts = [Polygon(x['p']).centroid for x in BY.values() if x.get('kirke')]
            grupper = [[(p.x, p.y, None) for p in pts]]
        else:
            ids = [i for i in hus_i_tegning(n) if i in BY]
            pts = [(Polygon(BY[i]['p']).centroid.x, Polygon(BY[i]['p']).centroid.y, i) for i in ids]
            # husrekker: grådig gruppering i ruter på 55 m langs aksen med størst spredning
            grupper = []
            for p in sorted(pts, key=lambda q: (q[0] - q[1])):
                for g in grupper:
                    if max(abs(p[0] - q[0]) for q in g + [p]) < RUTE and max(abs(p[1] - q[1]) for q in g + [p]) < RUTE * 0.8:
                        g.append(p); break
                else:
                    grupper.append([p])
        for k, g in enumerate(grupper):
            if not g: continue
            cx, cy = float(np.mean([q[0] for q in g])), float(np.mean([q[1] for q in g]))
            ut.append(dict(n=f'{n}-{k + 1}', tegning=n, cx=round(cx, 2), cy=round(cy - 4, 2), zoom=6, vinkler=[20],
                           bygg=[dict(id=q[2], x=round(q[0], 2), y=round(q[1], 2), h=BY[q[2]]['h']) for q in g if q[2]]))
    json.dump(ut, open(VIS, 'w'), indent=0)
    print(len(ut), 'nærbilder ->', VIS)


def ark(n):
    from PIL import Image, ImageDraw, ImageFont
    import bygg_ark, vegger as VG
    V = next(v for v in json.load(open(VIS)) if v['n'] == n)
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    png = os.path.join(ROT, 'kilder', 'kvartal-ai', 'png', V['tegning'] + '.png')
    if not os.path.exists(png):
        import fitz
        pm = fitz.open(os.path.join(ROT, 'kilder', 'kvartal-ai', V['tegning'] + '.ai'))[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
        pm.save(png)
    teg = Image.open(png).convert('RGB')
    mod = Image.open(os.path.join(BILDER, f'{n}-az20.png')).convert('RGB')
    J = json.load(open(os.path.join(BILDER, f'{n}-az20.json')))
    H = 1300
    teg = teg.resize((int(teg.width * H / teg.height), H)); sk = H / mod.height; mod = mod.resize((int(mod.width * sk), H))
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    except Exception:
        F = FB = ImageFont.load_default()
    dr = ImageDraw.Draw(mod); skj = mod.height / J['H']
    ids = [b['id'] for b in V['bygg']]
    for b in J['bygg']:
        if not b.get('midt') or b['id'] not in ids: continue
        p = (b['midt'][0] * skj, b['midt'][1] * skj)
        if not (0 <= p[0] < mod.width and 0 <= p[1] < mod.height): continue
        lab = b['id'].replace('bnr-1938', '').replace('bnr-', '')
        dr.rectangle([p[0] - 2, p[1] - 9, p[0] + 9 * len(lab) + 2, p[1] + 9], fill=(255, 255, 255)); dr.text((p[0], p[1] - 9), lab, fill=(150, 0, 0), font=F)
    rader = []
    for i in ids:
        x = BY[i]
        rader.append([i.replace('bnr-', ''), (x.get('navn') or '')[:22], f"{x['h']:.1f}", '; '.join(bygg_ark.fasade(x, omg)) or '–',
                      str(len(x.get('arker') or [])), str(len(x.get('takvinduer') or [])), str(len(x.get('piper') or [])),
                      (x.get('fasade_kilde') or '')[:13], (x.get('farge_kilde') or '')[:30]])
    tab_h = 40 + 21 * (len(rader) + 1)
    out = Image.new('RGB', (teg.width + mod.width + 30, H + 70 + tab_h), 'white'); dd = ImageDraw.Draw(out)
    dd.text((10, 12), f"{n}: tegning 2015 (venstre), modellen så nær kartet zoomer (zoom 6, pikseltetthet 2), az 20 (høyre)", fill=(0, 0, 0), font=FB)
    out.paste(teg, (10, 55)); out.paste(mod, (teg.width + 20, 55))
    y = H + 70; kol = [0, 120, 320, 380, 1180, 1225, 1270, 1315, 1450]
    for c, t in zip(kol, ['id (bnr-)', 'navn', 'h m', 'vegger: retning lengde: vinduer per etasje (nederst først), D dører, P porter', 'ark', 'tv', 'pip', 'fasade', 'farge']):
        dd.text((10 + c, y), t, fill=(0, 0, 0), font=F)
    for r in rader:
        y += 21
        for c, t in zip(kol, r): dd.text((10 + c, y), t, fill=(30, 30, 30), font=F)
    os.makedirs(UT, exist_ok=True)
    f = os.path.join(UT, f'{n}.jpg'); out.save(f, quality=88)
    return f


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'visninger':
        visninger()
    elif a and a[0] == 'ark':
        for n in (a[1:] or [v['n'] for v in json.load(open(VIS))]):
            if os.path.exists(os.path.join(BILDER, f'{n}-az20.png')):
                print(ark(n))
    else:
        print(__doc__)
