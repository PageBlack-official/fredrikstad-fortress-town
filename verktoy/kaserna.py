#!/usr/bin/env python3
"""Infanterikasernen (bnr-193867537) slik den blir etter ombyggingen til hotell (Fredriksborg, SG&CO-illustrasjonene 2026).

  python3 verktoy/kaserna.py     skriver rettelser for vinduer, dører, takarker, piper og sokkel, og data/teglmurer.json og
                                 data/vinterhager.json (gårdsmuren med rundbueporten og glasshuset i gården)

Fasaden følger illustrasjonene og bygget slik det står:
- to høye etasjer over en lys granittsokkel, vinduene i faste akser (omtrent 3,4 m) og like store i hele bygget
- små kjellervinduer i sokkelen under vinduene
- fire innganger mot torget: midt på hver langfløy og midt på hver side av hjørnet, grønne fløydører med overlys
- over inngangene i hjørnet et oksøye i en arke; ellers takarker over annenhver akse på langsidene
- 12 piper på mønene (det kalendariske systemet: årets måneder)
- gården lukkes av en teglmur fra fløyene til brannstasjonen; inngangen fra gata er en port med rundbue (målt i ortofoto 2024:
  murene står der i dag, porten midt i muren mot gata)
- glasshuset (vinterhagen) står mot hjørnets gårdsfasade

Tallene her er Page Blacks lesing av illustrasjonene og flyfotoet; når tegningene fra arkitekten kommer, rettes de her.
"""
import json, math, os, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag  # noqa: E402

ID = 'bnr-193867537'
BRANN = 'bnr-193868568'
DATO = '2026-10-27'
HVEM = 'Claude'
GRUNN = 'Kaserna etter ombyggingen (SG&CO-illustrasjonene for Fredriksborg, ortofoto 2024): verktoy/kaserna.py'

AKSE = 3.4            # meter mellom vindusaksene
KANT = 1.9            # fra hjørnet til første akse
SOKKEL = 1.1          # granittsokkel
ETG = [(3.0, 2.0), (6.6, 2.0)]   # (midt, høyde) for 1. og 2. etasje
VB = 1.15             # vindusbredde
KJELLER = (0.55, 0.42, 0.95)     # midt, høyde, bredde


def kanter(p):
    """Fasadene: hver kant med lengde, retning og utovernormal (polygonet går med klokka, så utover er til venstre)."""
    A = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2
    s = 1 if A < 0 else -1
    ut = []
    for i in range(len(p)):
        a, b = p[i], p[(i + 1) % len(p)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        tx, ty = dx / L, dy / L
        nx, ny = -ty * s, tx * s
        ut.append({'a': a, 'b': b, 'L': L, 't': (tx, ty), 'n': (nx, ny), 'mid': ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)})
    return ut


def akser(k):
    if k['L'] < 6:
        return []
    n = max(1, round((k['L'] - 2 * KANT) / AKSE) + 1)
    if n == 1:
        return [k['L'] / 2]
    st = (k['L'] - 2 * KANT) / (n - 1)
    return [KANT + i * st for i in range(n)]


def punkt(k, s):
    return (k['a'][0] + k['t'][0] * s, k['a'][1] + k['t'][1] * s)


def vindu(xy, z, k, w, h, typ=0):
    tx, ty = k['n'][1], -k['n'][0]          # tegnekoden: normal = (-ty, tx)
    return [round(xy[0], 2), round(xy[1], 2), round(z, 2), round(tx, 4), round(ty, 4), round(k['n'][0], 4), round(k['n'][1], 4), w, h, typ, 0, 0]


def main():
    raa = {x['id']: x for x in datalag.les('bygg')}
    d = datalag.alle()
    b = {x['id']: x for x in d['bygg']}[ID]
    brann = {x['id']: x for x in d['bygg']}[BRANN]
    h, h0, f = b['h'], raa[ID]['h'], b.get('th', 0.82) / 0.82
    raa_z = lambda z: round(h0 + (z - h) / f, 2)    # arker og piper lagres i grunnhøyden (datalag.hoyden_styrer flytter dem)
    K = kanter(b['p'])
    # torget ligger nord (Kongens torv): fasader med normal mot nord er torgsiden
    torg = [k for k in K if k['n'][1] > 0.3 and k['L'] > 10]
    hjorne = sorted([k for k in torg if k['L'] < 25], key=lambda k: k['mid'][0])      # de to sidene av hjørnet mot torget
    lang = [k for k in torg if k['L'] >= 25]                                            # langfløyene mot torget
    inngang = set(id(k) for k in hjorne + lang)
    # glasshuset står mot hjørnets gårdsfasade (den kanten som vender mot sørvest og er nærmest gården midt i)
    gard_hjorne = min((k for k in K if k['n'][1] < -0.7 and 15 < k['L'] < 25), key=lambda k: k['mid'][0])
    GH_B, GH_D, GH_H = 17.0, 6.5, 4.4
    vind, arker = [], []
    for k in K:
        ss = akser(k)
        if not ss:
            continue
        midt = min(range(len(ss)), key=lambda i: abs(ss[i] - k['L'] / 2))
        for i, s in enumerate(ss):
            xy = punkt(k, s)
            dor = id(k) in inngang and i == midt
            under_glass = k is gard_hjorne and abs(s - k['L'] / 2) < GH_B / 2
            if dor:
                vind.append(vindu(xy, 1.75, k, 1.7, 3.3, 1)[:10] + [2, 0])   # grønn fløydør med overlys
            elif under_glass:
                if i == midt:
                    vind.append(vindu(xy, 1.6, k, 1.6, 3.0, 1)[:10] + [2, 0])   # dør fra hotellet ut i glasshuset
            else:
                ku = (xy[0] + k['n'][0] * 0.2, xy[1] + k['n'][1] * 0.2)      # foran granittsokkelen
                vind.append(vindu(ku, KJELLER[0], k, KJELLER[2], KJELLER[1]))
                vind.append(vindu(xy, ETG[0][0], k, VB, ETG[0][1]))
            vind.append(vindu(xy, ETG[1][0], k, VB, ETG[1][1]))
        # takarker: oksøye over inngangen i hjørnet, ellers over annenhver akse på langsidene (ikke på gavlene)
        if k['L'] < 15.5 and id(k) not in inngang:
            continue
        inn = 0.7
        for i, s in enumerate(ss):
            okse = k in hjorne and i == midt
            if not okse and (k in hjorne or i % 2 == 0 or i in (0, len(ss) - 1)):
                continue
            x, y = punkt(k, s); x -= k['n'][0] * inn; y -= k['n'][1] * inn
            bw, hb = (1.6, 1.7) if okse else (1.2, 1.5)
            arker.append([round(x, 2), round(y, 2), raa_z(h + 0.75), round(k['n'][0], 4), round(k['n'][1], 4), bw, hb])
            z = h + 0.75 - 0.25 + (hb + 0.25) / 2
            vind.append([round(x + k['n'][0] * 0.02, 2), round(y + k['n'][1] * 0.02, 2), round(z, 2), round(k['n'][1], 4), round(-k['n'][0], 4),
                         round(k['n'][0], 4), round(k['n'][1], 4), 1.0 if okse else 0.75, 1.0 if okse else 0.95, 3 if okse else 0, 0, 0])
    # piper: 12 på mønene, fordelt etter mønelengde (møner lest av takflatene i tak2)
    rygg = [((-3.17, -13.03), (14.42, 12.5), 4), ((14.44, 12.5), (31.36, 5.03), 2), ((31.37, 5.03), (38.29, 19.23), 2), ((39.64, 20.62), (65.76, 11.89), 4)]
    rise = max(q[2] for fl in raa[ID]['tak2'] for q in fl)
    piper = []
    for a, c, n in rygg:
        ang = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))
        for j in range(n):
            u = (j + 0.5) / n
            piper.append([round(a[0] + (c[0] - a[0]) * u, 2), round(a[1] + (c[1] - a[1]) * u, 2), round(h0 + rise - 0.6, 2), round(ang, 1)])
    # gårdsmuren: fra fløyenes ender til brannstasjonen, porten midt i muren mot gata
    p = b['p']; bp = brann['p']
    sw0 = min(p, key=lambda q: q[1])                                       # vestfløyens sørhjørne
    sw1 = [(bp[5][0] + bp[0][0]) / 2, (bp[5][1] + bp[0][1]) / 2]           # brannstasjonens vestgavl
    se0 = min(p, key=lambda q: math.hypot(q[0] - 68.6, q[1] - 2.9))        # østfløyens sørhjørne
    se1 = bp[3]                                                             # brannstasjonens nordøsthjørne
    murer = [
        {'id': 'mu-1', 'navn': 'Gårdsmuren mot gata', 'p': [se0, se1], 'h': 3.0, 'tykk': 0.5, 'farge_fra': ID,
         'port': {'s': 0.5, 'bredde': 3.4, 'hoyde': 4.0, 'pilar': 5.4, 'pilar_h': 5.0, 'navn': 'Porten inn til gården'}},
        {'id': 'mu-2', 'navn': 'Gårdsmuren mot kirka', 'p': [sw0, sw1], 'h': 3.0, 'tykk': 0.5, 'farge_fra': ID},
    ]
    g = gard_hjorne; m = g['mid']; t = g['t']; n = g['n']
    hj = [[m[0] + t[0] * sa * GH_B / 2 + n[0] * dd, m[1] + t[1] * sa * GH_B / 2 + n[1] * dd] for sa, dd in ((-1, 0), (1, 0), (1, GH_D), (-1, GH_D))]
    vinterhager = [{'id': 'vh-1', 'navn': 'Vinterhagen', 'bygg_id': ID, 'p': [[round(a, 2), round(c, 2)] for a, c in hj], 'h': GH_H}]
    for navn, rader in (('teglmurer', murer), ('vinterhager', vinterhager)):
        with open(os.path.join(ROT, 'data', navn + '.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rader) + '\n]\n')
    # rettelsene: én linje per felt, eldre Kaserna-linjer for samme felt erstattes
    nye = {'vind': vind, 'arker': arker, 'piper': piper, 'sokkel': {'h': SOKKEL, 'farge': [206, 202, 192]}}
    rett = [r for r in json.load(open(os.path.join(ROT, 'data', 'rettelser.json'), encoding='utf8'))
            if not (r.get('id') == ID and r.get('felt') in nye)]
    rett += [{'emne': 'bygg', 'id': ID, 'op': 'sett', 'felt': fe, 'verdi': v, 'hvem': HVEM, 'dato': DATO, 'grunn': GRUNN} for fe, v in nye.items()]
    datalag.skriv_rettelser(rett)
    reg = os.path.join(ROT, 'kilder', 'id-register.txt')
    har = set(l.strip() for l in open(reg, encoding='utf8'))
    with open(reg, 'a', encoding='utf8') as fh:
        fh.write(''.join(i + '\n' for i in ('mu-1', 'mu-2', 'vh-1') if i not in har))
    vin = sum(1 for v in vind if v[9] in (0, 3)); dor = sum(1 for v in vind if v[9] == 1)
    print(f'Kaserna: {vin} vinduer, {dor} dører, {len(arker)} takarker, {len(piper)} piper; 2 gårdsmurer med port, 1 vinterhage')


if __name__ == '__main__':
    main()
