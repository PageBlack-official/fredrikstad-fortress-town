"""Kontrollark per kvartal for byggene (29.10): (1) Vegars kvartaltegning, (2) modellen fra samme kant (az 20, kamera fra
kvartal-QA), (3) fasadetabell per hus: høyde, vinduer per vegg og etasje, dører, arker, takvinduer, piper, farge og kilde.
Tegningene og ortofoto er åndsverk/uavklart: arket med tegningen ligger i rapport/bygg/ (bildet i git er arket; .ai bare lokalt).

    python3 verktoy/bygg_ark.py visninger                 rapport/bygg/_arbeid/visninger.json (az 20, husene i hvert kvartal)
    node verktoy/kvartal_bilder.mjs ut/enkel/index.html rapport/bygg/_arbeid/visninger.json rapport/bygg/_arbeid [navn …]
    python3 verktoy/bygg_ark.py ark [navn …]              rapport/bygg/kvartal-<navn>.png
"""
import json, math, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
from shapely.geometry import Polygon, Point
ARB = os.path.join(ROT, 'rapport', 'bygg', '_arbeid'); UT = os.path.join(ROT, 'rapport', 'bygg')
KOMP = ['N', 'NØ', 'Ø', 'SØ', 'S', 'SV', 'V', 'NV']


def husliste(navn, d):
    kob = json.load(open(os.path.join(ROT, 'kilder', 'kvartal-kobling.json')))
    t = next(t for t in kob['tegninger'] if t['navn'] == navn)
    ids = list(t['bygg'])
    # nye bygg fra kommunekartet (ikke i koblingen) som står inne blant husene i kvartalet
    alle = {x['id']: x for x in d['bygg'] if not x.get('skjul') and x.get('gml')}
    kj = [Polygon(alle[i]['p']) for i in ids if i in alle]
    if kj:
        from shapely.ops import unary_union
        hull = unary_union(kj).convex_hull.buffer(2)
        for i, x in alle.items():
            if i not in ids and hull.contains(Polygon(x['p']).centroid):
                ids.append(i)
    return [i for i in ids if i in alle]


def visninger():
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg']}
    gml = json.load(open(os.path.join(ROT, 'rapport', 'kvartal-qa', '_arbeid', 'visninger.json')))
    ut = []
    for v in gml:
        ids = husliste(v['n'], d)
        bygg = [dict(id=i, x=round(Polygon(BY[i]['p']).centroid.x, 2), y=round(Polygon(BY[i]['p']).centroid.y, 2), h=BY[i]['h']) for i in ids]
        ut.append(dict(n=v['n'], cx=v['cx'], cy=v['cy'], zoom=v['zoom'], vinkler=[20], bygg=bygg))
    os.makedirs(ARB, exist_ok=True)
    json.dump(ut, open(os.path.join(ARB, 'visninger.json'), 'w'), indent=0)
    print(len(ut), 'visninger')


def kompass(n):
    az = math.degrees(math.atan2(n[0], n[1])) % 360
    return KOMP[int((az + 22.5) // 45) % 8]


def fasade(x, omg):
    import vegger as VG
    V = VG.vegger(x, omg, slaa_sammen=True); rad = {}
    for v in x.get('vind') or []:
        k, _ = VG.naermeste_vegg(V, np.array(v[:2]))
        if k is None: continue
        r = rad.setdefault(k, dict(etg={}, dor=0, port=0))
        if v[9] == 0: r['etg'][round(v[2] - v[8] / 2, 1)] = r['etg'].get(round(v[2] - v[8] / 2, 1), 0) + 1
        elif v[9] == 1: r['dor'] += 1
        else: r['port'] += 1
    ut = []
    for k, r in sorted(rad.items(), key=lambda t: -V[t[0]]['L']):
        w = V[k]; et = '/'.join(str(r['etg'][z]) for z in sorted(r['etg']))
        ut.append(f"{kompass(w['n'])} {w['L']:.0f}m: {et or '–'}{' D' + str(r['dor']) if r['dor'] else ''}{' P' + str(r['port']) if r['port'] else ''}")
    return ut


def ark(navn):
    from PIL import Image, ImageDraw, ImageFont
    import vegger as VG
    d = datalag.alle(); BY = {x['id']: x for x in d['bygg']}; omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    teg = Image.open(os.path.join(ROT, 'kilder', 'kvartal-ai', 'png', navn + '.png')).convert('RGB')
    mod = Image.open(os.path.join(ARB, f'{navn}-az20.png')).convert('RGB')
    J = json.load(open(os.path.join(ARB, f'{navn}-az20.json')))
    H = 900
    teg = teg.resize((int(teg.width * H / teg.height), H)); mod = mod.resize((int(mod.width * H / mod.height), H))
    dr = ImageDraw.Draw(mod)
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    except Exception:
        F = FB = ImageFont.load_default()
    sk = H / J['H']
    ids = [b['id'] for b in J['bygg']]
    for b in J['bygg']:
        if not b.get('midt'): continue
        p = (b['midt'][0] * sk, b['midt'][1] * sk)
        if not (0 <= p[0] < mod.width and 0 <= p[1] < H): continue
        lab = b['id'].replace('bnr-1938', '').replace('bnr-', '')
        dr.rectangle([p[0] - 2, p[1] - 8, p[0] + 7 * len(lab) + 2, p[1] + 8], fill=(255, 255, 255))
        dr.text((p[0], p[1] - 8), lab, fill=(150, 0, 0), font=F)
    rader = []
    for i in ids:
        x = BY[i]
        rader.append([i.replace('bnr-', ''), (x.get('navn') or '')[:22], f"{x['h']:.1f}", '; '.join(fasade(x, omg)) or '–',
                      str(len(x.get('arker') or [])), str(len(x.get('takvinduer') or [])), str(len(x.get('piper') or [])),
                      (x.get('fasade_kilde') or '')[:13], (x.get('farge_kilde') or '')[:22]])
    tab_h = 30 + 18 * (len(rader) + 2)
    W = teg.width + mod.width + 30
    out = Image.new('RGB', (max(W, 1500), H + 60 + tab_h), 'white'); dd = ImageDraw.Draw(out)
    dd.text((10, 10), f"{navn}: tegning 2015 (venstre), modellen fra samme kant, az 20 (høyre)", fill=(0, 0, 0), font=FB)
    out.paste(teg, (10, 50)); out.paste(mod, (teg.width + 20, 50))
    y = H + 60
    kol = [0, 110, 290, 340, 1020, 1060, 1100, 1140, 1260]
    hode = ['id (bnr-)', 'navn', 'h m', 'vegger: retning lengde: vinduer per etasje (nederst først), D dører, P porter', 'ark', 'tv', 'pip', 'fasade', 'farge']
    for c, t in zip(kol, hode): dd.text((10 + c, y), t, fill=(0, 0, 0), font=F)
    for r in rader:
        y += 18
        for c, t in zip(kol, r): dd.text((10 + c, y), t, fill=(30, 30, 30), font=F)
    f = os.path.join(UT, f'kvartal-{navn}.png'); out.save(f, optimize=True)
    return f


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'visninger':
        visninger()
    elif a and a[0] == 'ark':
        for n in (a[1:] or [v['n'] for v in json.load(open(os.path.join(ARB, 'visninger.json')))]):
            print(ark(n))
    else:
        print(__doc__)
