#!/usr/bin/env python3
"""Infanterikasernen (bnr-193867537) slik den blir etter ombyggingen til hotell (Fredriksborg, SG&CO-illustrasjonene 2026).

  python3 verktoy/kaserna.py     skriver rettelser for vinduer, dører, takarker, piper og sokkel, og data/teglmurer.json og
                                 data/vinterhager.json (gårdsmuren med rundbueporten og glasshuset i gården)

Står i kjeden (verktoy/bygg_kjede.py) etter fasadeverktøyene, og datalag.EGNE_FASADER gjør at de hopper over Kaserna.
Før 02.11 stod den ikke i kjeden: fasade_tegning.py (29.10) la Kvartal11 og Street View 2010 over, og veggen mot torget
mistet 34 av 45 vinduer (avvik A1). Regel 37 sammenligner det effektive bygget med beregn().

Fasaden følger illustrasjonene og bygget slik det står:
- to høye etasjer over en lys granittsokkel, vinduene i faste akser (omtrent 3,4 m) og like store i hele bygget
- små kjellervinduer i sokkelen under vinduene
- to nye innganger fra torget (godkjent av Riksantikvaren 2025): midt på hver side av hjørnet, grønne fløydører med overlys
- veranda: uteservering med plantekasser og parasoller langs hjørnesiden mot vest, der statuen står (SG&CO-kveldsbildet)
- over inngangene i hjørnet et oksøye i en arke; ellers takarker over annenhver akse på langsidene
- 12 piper på mønene (det kalendariske systemet: årets måneder)
- gården lukkes av en teglmur fra fløyene til brannstasjonen; inngangen fra gata er en port med rundbue (målt i ortofoto 2024:
  murene står der i dag, porten midt i muren mot gata)
- glasshuset (vinterhagen) står mot hjørnets gårdsfasade

Fra Metropolis (interiørarkitektene, metropolis.no/prosjekter/hotell-kasernen, Vegar 06.11; bildene i teknisk-veikart/arkiv/
kasernen-metropolis/): vinterhagen er et lyst glasshus med smale olivengrønne sprosser og saltak i glass, med plen, hekker og
blomstrende busker foran (SG&CO «Utefølelse inne»); okergul gesims under takfoten; kjellervinduene i granittsokkelen har segmentbue
(fotoet av døra). Dørene (grønne fløydører med overlys) og 24-ruters vinduer stemmer med fotoene.
Tallene her er Page Blacks lesing av illustrasjonene og flyfotoet; når tegningene fra arkitekten kommer, rettes de her.
"""
import json, math, os, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402

ID = 'bnr-193867537'
BRANN = 'bnr-193868568'
DATO = '2026-10-27'
HVEM = 'Claude'
GRUNN = 'Kaserna etter ombyggingen (SG&CO-illustrasjonene for Fredriksborg, ortofoto 2024): verktoy/kaserna.py'
GRUNN_PORT = 'portbygg og skur i Kasernens gårdsmur: murens tegl (verktoy/kaserna.py, avvik A2 02.11)'
# porten i muren mot gata: Kvartal11 (2015) tegner porten (hevet mur med bue, mørke fløydører) en firedel av muren fra fløyen og
# det grå skuret (FKB pb-46) midt på; 27.10 stod porten midt i muren, oppå skuret (avvik A2, 02.11)
PORT_MU1_S = 0.235

AKSE = 3.4            # meter mellom vindusaksene
KANT = 1.9            # fra hjørnet til første akse
SOKKEL = 1.1          # granittsokkel
ETG = [(3.0, 2.0), (6.6, 2.0)]   # (midt, høyde) for 1. og 2. etasje
VB = 1.15             # vindusbredde
KJELLER = (0.56, 0.62, 1.05, 2)  # midt, høyde, bredde, bue 2 = segmentbue (Metropolis-fotoet av døra, 06.11: buede kjellervinduer i granitten)
GESIMS = {'h': 0.34, 'farge': [214, 186, 120], 'skygge': [168, 142, 88]}   # okergul gesims under takfoten (Metropolis/SG&CO, fotoet av gavlen mot torget)
# dørene i gårdsfasadene (illustrasjonene viser ikke gården): Kvartal11 (2015), lest av fasade_tegning.py 29.10, i modellmeter.
# Døra står i aksen nærmest punktet. Døra under glasshuset kommer fra glasshuset (under_glass), ikke herfra. (avvik A1, 02.11)
GARDSDORER = [(3.9, -15.93), (38.64, 2.73)]


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


def beregn(d=None):
    """Kaserna fra dataene slik de står: (felt -> verdi for rettelsene, {datafil: rader}). Skriver ingenting."""
    raa = {x['id']: x for x in datalag.les('bygg')}
    d = d or datalag.alle()
    b = {x['id']: x for x in d['bygg']}[ID]
    brann = {x['id']: x for x in d['bygg']}[BRANN]
    h, h0, f = b['h'], raa[ID]['h'], b.get('th', 0.82) / 0.82
    raa_z = lambda z: round(h0 + (z - h) / f, 2)    # arker og piper lagres i grunnhøyden (datalag.hoyden_styrer flytter dem)
    K = kanter(b['p'])
    # torget ligger nord (Kongens torv): fasader med normal mot nord er torgsiden
    torg = [k for k in K if k['n'][1] > 0.3 and k['L'] > 10]
    hjorne = sorted([k for k in torg if k['L'] < 25], key=lambda k: k['mid'][0])      # de to sidene av hjørnet mot torget
    lang = [k for k in torg if k['L'] >= 25]                                            # langfløyene mot torget
    # Riksantikvaren (dispensasjon juni 2025, FB 21.06.25): to nye innganger fra Kongens torv, én på hver side av hjørnet
    # (resepsjonen og bakeriet), kopier av eksisterende dører. Langfløyene har ingen dør mot torget.
    inngang = set(id(k) for k in hjorne)
    # glasshuset står mot hjørnets gårdsfasade (den kanten som vender mot sørvest og er nærmest gården midt i)
    # (gården ligger mellom fløyene og brannstasjonen: nærmest brannstasjonens midte, ikke gavlene)
    bc = [sum(q[0] for q in brann['p']) / len(brann['p']), sum(q[1] for q in brann['p']) / len(brann['p'])]
    gard_hjorne = min((k for k in K if k['n'][1] < -0.7 and 17 < k['L'] < 25), key=lambda k: math.hypot(k['mid'][0] - bc[0] + 10, k['mid'][1] - bc[1]))
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
            elif not under_glass and k['n'][1] < -0.3 and any(math.hypot(xy[0] - g[0], xy[1] - g[1]) < AKSE / 2 for g in GARDSDORER):
                vind.append(vindu(xy, 1.6, k, 1.6, 3.0, 1)[:10] + [2, 0])   # dør fra gården (Kvartal11)
            elif under_glass:
                if i == midt:
                    vind.append(vindu(xy, 1.6, k, 1.6, 3.0, 1)[:10] + [2, 0])   # dør fra hotellet ut i glasshuset
            else:
                vind.append(vindu(xy, KJELLER[0], k, KJELLER[2], KJELLER[1])[:10] + [KJELLER[3], 0])   # i veggen; sokkelen (src/07) står 3 cm ut, vinduene 5 cm
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
         'port': {'s': PORT_MU1_S, 'bredde': 3.4, 'hoyde': 4.0, 'pilar': 5.4, 'pilar_h': 5.0, 'navn': 'Porten inn til gården'}},
        {'id': 'mu-2', 'navn': 'Gårdsmuren mot kirka', 'p': [sw0, sw1], 'h': 3.0, 'tykk': 0.5, 'farge_fra': ID},
    ]
    # porten mot kirka er portbygget pb-51 i data/porter.json (typ mur: FKB-omrisset er porten, src/10). Muren tegnes ikke gjennom
    # et portbygg («aapninger»: [fra, til, id] i meter langs muren, src/19); før 02.11 gikk mu-2 tvers gjennom buen i pb-51 (avvik A2)
    plass = {x['id']: x for x in d['bygg']}
    portbygg = [(pt['bygg_id'], Polygon(plass[pt['bygg_id']]['p']).buffer(0.05)) for pt in d.get('porter', [])
                if pt.get('typ') == 'mur' and pt.get('bygg_id') in plass and not plass[pt['bygg_id']].get('skjul')]
    for mu in murer:
        linje = LineString(mu['p'])
        aap = []
        for pid, P in portbygg:
            g = linje.intersection(P)
            if g.is_empty or g.length < 0.5:
                continue
            q = [Point(c) for c in (g.coords if hasattr(g, 'coords') else [c for gg in g.geoms for c in gg.coords])]
            ss = sorted(linje.project(c) for c in q)
            aap.append([round(ss[0], 2), round(ss[-1], 2), pid])
        if aap:
            mu['aapninger'] = sorted(aap)
    portfarge = sorted({q[2] for mu in murer for q in mu.get('aapninger', [])})
    # småbygg inntil muren på gårdssiden (FKB, under 15 m², ikke portbygg): skuret ved porten mot gata (pb-46, grått tak i
    # Kvartal11). Veggene i murens tegl, og ingen dør: reglene (vinduer_regler.py) satte en dør i veggen som står i muren (avvik A2)
    skur = sorted(x['id'] for x in d['bygg'] if not x.get('skjul') and x['id'] not in portfarge and x['id'] not in (ID, BRANN)
                  and Polygon(x['p']).area < 15 and any(LineString(mu['p']).distance(Polygon(x['p'])) < 0.6 for mu in murer))
    g = gard_hjorne; m = g['mid']; t = g['t']; n = g['n']
    hj = [[m[0] + t[0] * sa * GH_B / 2 + n[0] * dd, m[1] + t[1] * sa * GH_B / 2 + n[1] * dd] for sa, dd in ((-1, 0), (1, 0), (1, GH_D), (-1, GH_D))]
    # verandaen (uteservering): langs hjørnesiden som vender mot vest, med statuen ved enden (SG&CO-kveldsbildet med Fredrik II),
    # lavt dekke på torget, plantekasser rundt og parasoller; åpning midt foran
    vk = min(hjorne, key=lambda k: k['n'][0])
    VB_, VD_, VH_ = round(vk['L'] - 1.0, 2), 5.0, 0.18
    m, t, n = vk['mid'], vk['t'], vk['n']
    vp = [[m[0] + t[0] * sa * VB_ / 2 + n[0] * dd, m[1] + t[1] * sa * VB_ / 2 + n[1] * dd] for sa, dd in ((-1, 0.3), (1, 0.3), (1, VD_), (-1, VD_))]
    terrasser = [{'id': 'te-1', 'navn': 'Uteserveringen mot torget', 'bygg_id': ID, 'p': [[round(a, 2), round(c, 2)] for a, c in vp], 'h': VH_,
                  'parasoller': 5, 'aapning': 2.4}]
    # hagen foran glasshuset (SG&CO «Utefølelse inne»: plen helt inn til glasset, lave hekker, blomstrende busker): et felt ut i gården,
    # klippet mot fløyene, brannstasjonen og murene så det bare ligger i gården
    HAGE_D, HAGE_EKSTRA = 9.0, 3.0
    hp = [[m0[0] + t0[0] * sa * (GH_B / 2 + HAGE_EKSTRA) + n0[0] * dd, m0[1] + t0[1] * sa * (GH_B / 2 + HAGE_EKSTRA) + n0[1] * dd]
          for m0, t0, n0 in [(g['mid'], g['t'], g['n'])] for sa, dd in ((-1, 0.2), (1, 0.2), (1, GH_D + HAGE_D), (-1, GH_D + HAGE_D))]
    hage = Polygon(hp).difference(Polygon(b['p']).buffer(0.3)).difference(Polygon(brann['p']).buffer(2.0))
    for mu in murer: hage = hage.difference(LineString(mu['p']).buffer(1.2))
    hage = max(getattr(hage, 'geoms', [hage]), key=lambda q: q.area).simplify(0.2)
    plen = [[round(x, 2), round(y, 2)] for x, y in list(hage.exterior.coords)[:-1]]
    # hekkene: langs plenens ytterkant (ikke mot glasshuset), busker i hjørnene og langs glasset
    ytter = hage.exterior
    gl = Polygon(hj).buffer(0.6)
    hekker, cur = [], []
    for q in list(ytter.coords):
        if gl.contains(Point(q)):
            if len(cur) > 1: hekker.append(cur)
            cur = []
        else: cur.append([round(q[0] - (q[0] - hage.centroid.x) * 0.04, 2), round(q[1] - (q[1] - hage.centroid.y) * 0.04, 2)])
    if len(cur) > 1: hekker.append(cur)
    busker = []
    for j in range(7):
        u = (j + 0.5) / 7
        bx = hj[3][0] + (hj[2][0] - hj[3][0]) * u + g['n'][0] * 0.9; by = hj[3][1] + (hj[2][1] - hj[3][1]) * u + g['n'][1] * 0.9
        if hage.contains(Point(bx, by)): busker.append([round(bx, 2), round(by, 2), 0.7 if j % 2 else 0.55])
    vinterhager = [{'id': 'vh-1', 'navn': 'Vinterhagen', 'bygg_id': ID, 'p': [[round(a, 2), round(c, 2)] for a, c in hj], 'h': GH_H, 'rise': 1.6,
                    'hage': {'p': plen, 'hekker': hekker, 'busker': busker}}]
    nye = {'vind': vind, 'arker': arker, 'piper': piper, 'sokkel': {'h': SOKKEL, 'farge': [206, 202, 192], 'skygge': [146, 142, 136], 'type': 'naturstein'}, 'gesims': GESIMS}
    # portbyggene i Kasernemurene har murens tegl (Kasernens vegg). Verktøyet står sist i kjeden, så vegg_nye.py sin nabofarge
    # legger seg ikke over igjen (30.10 ble pb-51 satt for hånd og overstyrt av vegg_nye.py samme dag; avvik A5)
    andre = {pid: {'vegg': b['vegg'], 'veggs': b.get('veggs')} for pid in portfarge}
    andre.update({pid: {'vegg': b['vegg'], 'veggs': b.get('veggs'), 'vind': []} for pid in skur})
    return nye, {'teglmurer': murer, 'vinterhager': vinterhager, 'terrasser': terrasser}, andre


def fil_tekst(rader):
    return '[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rader) + '\n]\n'


def main():
    nye, filer, andre = beregn()
    for navn, rader in filer.items():
        with open(os.path.join(ROT, 'data', navn + '.json'), 'w', encoding='utf8') as fh:
            fh.write(fil_tekst(rader))
    # rettelsene: egne linjer (GRUNN) tas ut og legges bakerst (idempotent, som de andre verktøyene i kjeden); andre linjer
    # for Kaserna slettes ikke (rettelser slettes aldri), de overstyres fordi verktøyet står sist i kjeden
    rett = [r for r in json.load(open(os.path.join(ROT, 'data', 'rettelser.json'), encoding='utf8'))
            if not (r.get('id') == ID and r.get('grunn') == GRUNN)]
    rett = [r for r in rett if r.get('grunn') != GRUNN_PORT]
    rett += [{'emne': 'bygg', 'id': ID, 'op': 'sett', 'felt': fe, 'verdi': v, 'hvem': HVEM, 'dato': DATO, 'grunn': GRUNN} for fe, v in nye.items()]
    rett += [{'emne': 'bygg', 'id': pid, 'op': 'sett', 'felt': fe, 'verdi': v, 'hvem': HVEM, 'dato': '2026-11-02', 'grunn': GRUNN_PORT}
             for pid, felt in andre.items() for fe, v in felt.items()]
    datalag.skriv_rettelser(rett)
    reg = os.path.join(ROT, 'kilder', 'id-register.txt')
    har = set(l.strip() for l in open(reg, encoding='utf8'))
    with open(reg, 'a', encoding='utf8') as fh:
        fh.write(''.join(i + '\n' for i in ('mu-1', 'mu-2', 'vh-1', 'te-1') if i not in har))
    vind = nye['vind']
    vin = sum(1 for v in vind if v[9] in (0, 3)); dor = sum(1 for v in vind if v[9] == 1)
    print(f'Kaserna: {vin} vinduer, {dor} dører, {len(nye["arker"])} takarker, {len(nye["piper"])} piper; 2 gårdsmurer med port, 1 vinterhage, 1 veranda')


if __name__ == '__main__':
    main()
