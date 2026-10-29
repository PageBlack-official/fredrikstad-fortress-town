#!/usr/bin/env python3
"""Grunnmuren fra kommunekartet: husomrissene i Gamlebyen byttes til kommunens oppmålte omriss (FKB), som rettelser.

    python3 verktoy/grunnmur.py            lager rettelsene (idempotent: egne linjer fra en tidligere kjøring tas ut først)
    python3 verktoy/grunnmur.py --tørt     viser bare tallene
    python3 verktoy/grunnmur.py ark        kontrollarket rapport/grunnmur/oversikt.png (ikke i git)

Hele løpet (hver del er idempotent, rekkefølgen betyr noe):
    python3 verktoy/grunnmur.py && python3 -I rapport/hoyder/hent.py && python3 -I rapport/hoyder/legg_inn.py \\
      && python3 verktoy/grunnmur.py && python3 verktoy/vinduer_regler.py && python3 verktoy/grunnmur.py ark
(andre kjøring av grunnmur.py leser de nye høydene, så pipene står på taket og vinduene i tegnede hus under gesimsen.)

Kilde: kilder/kommunekart/kommunekart.pdf (verktoy/kommunekart.py). Fasit for omriss i Gamlebyen fra 29.10.2026.
Hva som gjøres per hus (bare gml=1, bare innenfor kartrammen):
  én-til-én        modellhuset får kommunens omriss (sett p, ph), id-en følger huset
  slått sammen     ett modellhus dekker flere kommunehus: delen der husets matrikkelpunkt står (ellers største overlapp)
                   beholder id, farger og tegnede vinduer; resten blir nye bygg
  delt i modellen  flere modellhus ligger i samme kommunehus: kommunens omriss deles mellom dem (nærmeste modellhus), så
                   alle id-er, farger og tegnede vinduer beholdes
  mangler          kommunehus uten modellhus blir nye bygg (op «ny»); under MINSTE m² hoppes over og listes
  uten kommunehus  modellhuset slettes aldri; står det ikke noe høyere enn 1 m i Kartverkets DOM−DTM, skjules det med grunn
  fredet           kirka (06_kirka), Kaserna (verktoy/kaserna.py) og portbyggene (data/porter.json) røres ikke
Id til nye bygg: bnr-<bygningsnummer> når et matrikkelpunkt står i omrisset og nummeret ikke er brukt, ellers neste pb-.
Taket (tak2, gavl2) regnes på nytt fra fotavtrykket for hver husrekke med et endret hus (verktoy/tak.py); gavlene arves
fra det gamle taket der veggen står omtrent samme sted, ellers gavl_regel. r, rf og tk følger omrisset.
"""
import json, math, os, sys
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, MultiPoint
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, kommunekart, tak  # noqa: E402

GRUNN = 'kommunekart FKB 29.10'
DATO = '2026-10-29'
HVEM = 'Claude'
MINSTE = 6.0                     # m²: mindre kommunehus (søppelskur, trapper) hoppes over og listes
KAPASITET_DEL = 0.5              # et modellhus «ligger i» et kommunehus når minst halve arealet er inni
NAER = 4.0                       # m: matrikkelpunkt like utenfor omrisset regnes med (som verktoy/matrikkel.py)
STANDARD_VEGG = [226, 222, 212]  # nye hus: nøytral lys grå til Vegar velger farge
STANDARD_TAK = [150, 144, 138]
UT = os.path.join(ROT, 'rapport', 'grunnmur')


def egen(r):
    return r.get('grunn', '').startswith(GRUNN)


def rett(id_, felt, verdi, grunn=GRUNN):
    return {"emne": "bygg", "id": id_, "op": "sett", "felt": felt, "verdi": verdi, "hvem": HVEM, "dato": DATO, "grunn": grunn}


def poly(x):
    P = Polygon(x['p'], [r for r in (x.get('ph') or []) if len(r) > 2])
    return P if P.is_valid else P.buffer(0)


def rund(P):
    """shapely-polygon -> (p, ph) som i data/bygg.json: med klokka, uten gjentatt startpunkt, 2 desimaler."""
    P = orient(P, -1.0)
    ring = lambda r: [[round(x, 2), round(y, 2)] for x, y in list(r.coords)[:-1]]
    return ring(P.exterior), [ring(r) for r in P.interiors]


def storste(G):
    if G.is_empty:
        return G
    if isinstance(G, Polygon):
        return G
    ps = [g for g in getattr(G, 'geoms', []) if isinstance(g, Polygon)]
    return max(ps, key=lambda g: g.area) if ps else Polygon()


def rekt(P):
    """r = [cx, cy, bredde langs vinkel, dybde, vinkel] fra minste omsluttende rektangel (som de gamle dataene), rf = fyllgrad."""
    R = P.minimum_rotated_rectangle; q = np.array(R.exterior.coords)[:4]
    e1, e2 = q[1] - q[0], q[2] - q[1]
    ang = math.degrees(math.atan2(e1[1], e1[0]))
    while ang <= -90: ang += 180
    while ang > 90: ang -= 180
    c = R.centroid
    r = [round(c.x, 2), round(c.y, 2), round(float(np.hypot(*e1)), 2), round(float(np.hypot(*e2)), 2), round(ang, 1)]
    return r, round(P.area / max(R.area, 1e-9), 2)


def matrikkelpunkter():
    k = json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json'), encoding='utf8'))
    ut = []
    for p in k['punkter']:
        if p['status'] in ('RA', 'GR', 'BR', 'BF'):
            continue
        x, y = datalag.til_modell(*p['lonlat'])
        ut.append(dict(p, xy=(x, y)))
    return ut


def mfelt(p):
    return {k: p[k] for k in ('bygningsnummer', 'uuid', 'type', 'kulturminne', 'sefrak', 'adresser', 'matrikkelenheter')}


def typ_fra_matrikkel(ms):
    if not ms:
        return 'yes'
    t = ms[0]['type']
    return 'garage' if t == 181 else 'shed' if 180 <= t < 190 else 'yes'


def del_mellom(K, medlemmer, res=0.1):
    """Kommunehuset K delt mellom modellhusene (id -> polygon) som ligger i det: hvert punkt i K går til modellhuset det
    ligger i, ellers det nærmeste (rasteret på res m). Delelinjene forenkles 0,15 m; det største huset får resten av K, så
    delene dekker K uten glipper eller overlapp."""
    import cv2
    ids = sorted(medlemmer, key=lambda m: medlemmer[m].area)
    x0, y0, x1, y1 = K.bounds
    W, H = int((x1 - x0) / res) + 2, int((y1 - y0) / res) + 2
    gx, gy = np.meshgrid(x0 + (np.arange(W) + 0.5) * res, y1 - (np.arange(H) + 0.5) * res)
    inne = shapely.contains_xy(K, gx, gy)
    d = np.stack([shapely.distance(medlemmer[m], shapely.points(gx, gy)) for m in ids], -1)
    lab = np.where(inne, np.argmin(d, -1), -1)
    ut = {}
    for k, m in enumerate(ids[:-1]):
        cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biter = []
        for c in cs:
            c = c[:, 0, :].astype(float)
            if len(c) < 3:
                continue
            q = Polygon(np.c_[x0 + (c[:, 0] + 0.5) * res, y1 - (c[:, 1] + 0.5) * res]).buffer(res * 0.5, join_style='mitre')
            biter.append(q)
        D = storste(unary_union(biter).simplify(0.15).intersection(K).buffer(0)) if biter else Polygon()
        for m2 in ut.values():
            D = storste(D.difference(m2))
        ut[m] = D
    rest = K
    for D in ut.values():
        rest = rest.difference(D)
    ut[ids[-1]] = storste(rest.buffer(0))
    return ut


# --------------------------------------------------------------------------------------------------------------
def plan():
    ret_alle = datalag.les('rettelser')
    mine_ny = {r['id'] for r in ret_alle if egen(r) and r['op'] == 'ny'}
    ret_ovrige = [r for r in ret_alle if not egen(r)]
    # tilstanden uten egne linjer (linjer andre verktøy har skrevet for mine nye bygg hoppes over her, de skrives tilbake)
    d = datalag.alle(raa=True); grunn = [dict(x) for x in d['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(d, [r for r in ret_ovrige if r.get('id') not in mine_ny]), grunn)
    B = d['bygg']; plass = {x['id']: i for i, x in enumerate(B)}
    grunn_h = {x['id']: x.get('h', 0) for x in grunn}
    K = kommunekart.omriss(); DEK = kommunekart.dekning()
    porter = {p['bygg_id'] for p in d.get('porter', []) if p.get('bygg_id')}
    fredet = {x['id']: ('kirka (06_kirka)' if x.get('kirke') else 'portbygg (data/porter.json)' if x['id'] in porter else '')
              for x in B}
    fredet['bnr-193867537'] = 'Kaserna (verktoy/kaserna.py)'
    fredet = {k: v for k, v in fredet.items() if v}
    vis = [x for x in B if len(x['p']) >= 3 and not x.get('skjul')]
    P = {x['id']: poly(x) for x in vis}
    gml = [x for x in vis if x.get('gml')]
    gml0 = [x['id'] for x in vis if not x.get('gml')]
    tre = shapely.STRtree(K)
    Kin = [j for j in kommunekart.i_gamlebyen(K, DEK) if not any(P[i].intersection(K[j]).area > 0.5 * K[j].area for i in gml0 if P[i].intersects(K[j]))]
    Kin_set = set(Kin)
    ov = {}
    for x in vis:
        for j in tre.query(P[x['id']]):
            j = int(j)
            if j in Kin_set:
                a = P[x['id']].intersection(K[j]).area
                if a > 0.5:
                    ov[(x['id'], j)] = a
    # eier av hvert kommunehus: modellhuset med størst overlapp (må være vesentlig for en av dem)
    eier = {}
    for (i, j), a in ov.items():
        if a / K[j].area >= 0.2 or a / P[i].area >= 0.3:
            if j not in eier or a > ov[(eier[j], j)]:
                eier[j] = i
    DEK_inne = DEK.buffer(-0.3)
    i_dekning = lambda i: DEK_inne.contains(P[i])     # huset må ligge helt innenfor kartrammen (et hus rammen kutter, er ikke målt helt)
    # modellhus som ligger i et kommunehus (minst halve arealet)
    ligger_i = {}
    for (i, j), a in ov.items():
        if a / P[i].area >= KAPASITET_DEL:
            if i not in ligger_i or a > ov[(i, ligger_i[i])]:
                ligger_i[i] = j
    A = {}
    for j, i in eier.items():
        A.setdefault(i, []).append(j)
    MP = matrikkelpunkter()
    egne_punkt = {p['bygningsnummer']: p for p in MP}

    nytt = {}           # id -> nytt omriss (endrede og nye hus)
    nye_bygg = []       # (polygon, kommune-indeks, hvorfor)
    logg = dict(endret=[], delt=[], delt_i_modell=[], nye=[], skjult=[], uendret=[], usikre=[], smaa=[], fredet=[])
    brukt_K = set()
    # 1. kommunehus der flere modellhus ligger: del omrisset mellom dem
    medl = {}
    for i, j in ligger_i.items():
        if x_gml(B, plass, i) and i_dekning(i):
            medl.setdefault(j, []).append(i)
    for j, ms in medl.items():
        if len(ms) < 2 and eier.get(j) in ms:
            continue
        ms = sorted(set(ms + ([eier[j]] if eier.get(j) and x_gml(B, plass, eier[j]) and eier[j] not in fredet else [])))
        if len(ms) < 2:
            continue
        if any(m in fredet for m in ms):
            logg['fredet'].append(f"kommunehus {j}: delt mellom {', '.join(ms)} i modellen, men et av dem er fredet; uendret")
            brukt_K.add(j); continue
        deler = del_mellom(K[j], {m: P[m] for m in ms})
        for m, D in deler.items():
            if D.is_empty or D.area < 1:
                continue
            nytt[m] = D
        logg['delt_i_modell'].append(dict(kommunehus=j, areal=round(K[j].area, 1), hus=ms))
        brukt_K.add(j)
    # 2. modellhus med sine kommunehus
    for x in gml:
        i = x['id']
        if not i_dekning(i):
            logg['uendret'].append(f"{i} ({x.get('navn') or x.get('type')}): utenfor eller kuttet av kartrammen, kommunekartet har ikke hele huset")
            continue
        js = [j for j in A.get(i, []) if j not in brukt_K]
        if i in fredet:
            for j in js:
                rest = storste(K[j].difference(P[i].buffer(0.05)))
                if K[j].intersection(P[i]).area > 0.5 * K[j].area or rest.area < MINSTE:
                    logg['fredet'].append(f"{i} ({fredet[i]}): kommunehus {j} ({K[j].area:.0f} m²) dekket av det fredede bygget")
                else:
                    nye_bygg.append((rest, j, f"del av kommunehus {j} utenfor fredet {i}"))
                brukt_K.add(j)
            logg['uendret'].append(f"{i} ({x.get('navn')}): fredet, {fredet[i]}")
            continue
        if i in nytt:
            continue          # delt i modellen (steg 1)
        if not js:
            continue          # uten kommunehus: steg 4
        if len(js) == 1:
            nytt[i] = K[js[0]]; brukt_K.add(js[0])
            logg['endret'].append(i)
            continue
        # slått sammen: delen med husets matrikkelpunkt beholder id-en
        num = int(i[4:]) if i.startswith('bnr-') else None
        pk = egne_punkt.get(num)
        hold = None
        if pk:
            for j in js:
                if K[j].buffer(0.5).contains(Point(pk['xy'])):
                    hold = j
        if hold is None:
            hold = max(js, key=lambda j: ov[(i, j)])
        nytt[i] = K[hold]; brukt_K.update(js)
        andre = [j for j in js if j != hold]
        for j in andre:
            nye_bygg.append((K[j], j, f"skilt ut fra {i}"))
        logg['delt'].append(dict(id=i, navn=x.get('navn'), beholder=hold, nye=andre,
                                 hvorfor='matrikkelpunkt' if pk and hold is not None and K[hold].buffer(0.5).contains(Point(pk['xy'])) else 'størst overlapp'))
    # 3. kommunehus uten modellhus. Står et skjult modellhus der, er det huset (skjult etter flyfotoet, som er forskjøvet
    #    flere steder): det vises igjen med kommunens omriss og beholder id-en
    skjulte = {x['id']: poly(x) for x in B if x.get('gml') and x.get('skjul') and len(x['p']) >= 3 and x['id'] not in fredet}
    gjenreist = []
    for j in Kin:
        if j in brukt_K or j in eier:
            continue
        kand = [(K[j].intersection(Ph).area, h) for h, Ph in skjulte.items() if Ph.intersects(K[j])]
        kand = [(a, h) for a, h in kand if a / K[j].area >= 0.2 or a / skjulte[h].area >= 0.3]
        if kand and K[j].area >= MINSTE:
            a, h = max(kand); skjulte.pop(h)
            nytt[h] = K[j]; brukt_K.add(j); gjenreist.append(h)
            logg['endret'].append(h)
            logg.setdefault('gjenreist', []).append(f"{h}: var skjult ({B[plass[h]]['skjul']}); kommunekartet har bygningen (kommunehus {j}, {K[j].area:.0f} m²)")
            continue
        if K[j].area < MINSTE:
            c = K[j].centroid
            logg['smaa'].append(f"kommunehus {j}: {K[j].area:.1f} m² ved ({c.x:.1f}, {c.y:.1f})")
            continue
        nye_bygg.append((K[j], j, 'mangler i modellen'))
    # nye bygg skal ikke ligge oppå hus som står (fredet, utenfor Gamlebyen)
    staar = [P[x['id']] for x in vis if x['id'] not in nytt and (x['id'] in fredet or not x.get('gml'))]
    st_tre = shapely.STRtree(staar) if staar else None
    def frigjor(G):
        if st_tre is None:
            return G
        for k in st_tre.query(G):
            if staar[int(k)].intersection(G).area > 0.05:
                G = storste(G.difference(staar[int(k)].buffer(0.02)))
        return G
    for i in list(nytt):
        nytt[i] = frigjor(nytt[i])
    nye_bygg = [(frigjor(G), j, h) for G, j, h in nye_bygg]
    nye_bygg = [(G, j, h) for G, j, h in nye_bygg if G.area >= MINSTE]
    # 4. modellhus uten kommunehus: DOM−DTM avgjør (hent.py-metoden)
    uten = [x for x in gml if i_dekning(x['id']) and x['id'] not in nytt and x['id'] not in fredet and not A.get(x['id'])]
    hoyde = dom_p50({x['id']: P[x['id']] for x in uten})
    skjul = []
    for x in uten:
        i = x['id']; p50, p90, n = hoyde.get(i, (None, None, 0))
        if x.get('navn') and p90 is not None and p90 < 1.0:
            logg['usikre'].append(f"{i} ({x['navn']}, {P[i].area:.0f} m²): ingen bygning i kommunekartet og ingenting over 1 m i DOM−DTM (p90 {p90:.1f} m), men huset har navn i tegnforklaringen (kan være overdekket, f.eks. et kruttmagasin i vollen); står til Vegar har sett på det")
            continue
        navn = x.get('navn') or x.get('type')
        if p50 is not None and n >= 4 and p90 < 1.0 and not x.get('navn'):   # hus med navn (tegnforklaringen) skjules aldri av seg selv
            skjul.append({"emne": "bygg", "id": i, "op": "skjul", "hvem": HVEM, "dato": DATO,
                          "grunn": f"{GRUNN}: ingen bygning i kommunekartet, og Kartverkets DOM−DTM har ingenting over 1 m i omrisset (p90 {p90:.1f} m)"})
            logg['skjult'].append(f"{i} ({navn}): p90 {p90:.1f} m")
        else:
            logg['usikre'].append(f"{i} ({navn}, {P[i].area:.0f} m²): ingen bygning i kommunekartet, men DOM−DTM p50 {p50 if p50 is None else round(p50, 1)} m, p90 {p90 if p90 is None else round(p90, 1)} m; står")
    # 5. matrikkelpunktene fordeles på omrissene: et punkt med et nummer som allerede er id til et hus, følger det huset
    #    (bygningsnummeret følger huset); ellers huset punktet står i (minste ved overlapp), ellers nærmeste innen NAER m
    nye_bygg = sorted(nye_bygg, key=lambda t: -t[0].area)
    alle_poly = {x['id']: P[x['id']] for x in vis}
    alle_poly.update(nytt)
    for k, (G, j, hvorfor) in enumerate(nye_bygg):
        alle_poly[f'ny:{k}'] = G
    tre2_ids = list(alle_poly); tre2 = shapely.STRtree([alle_poly[i] for i in tre2_ids])
    til = {}
    for p in MP:
        eier_id = f"bnr-{p['bygningsnummer']}"
        if eier_id in alle_poly and alle_poly[eier_id].distance(Point(p['xy'])) <= NAER:
            til.setdefault(eier_id, []).append(p); continue
        q = Point(p['xy'])
        hit = [tre2_ids[int(k)] for k in tre2.query(q, predicate='within')]
        if not hit:
            near = [(alle_poly[tre2_ids[int(k)]].distance(q), tre2_ids[int(k)]) for k in tre2.query(q.buffer(NAER))]
            hit = [min(near)[1]] if near and min(near)[0] <= NAER else []
        if hit:
            til.setdefault(min(hit, key=lambda i: alle_poly[i].area), []).append(p)
    # 6. id-er til nye bygg: bnr- fra et matrikkelpunkt som hører til omrisset og ikke er brukt, ellers neste pb-
    reg = [l.strip() for l in open(os.path.join(ROT, 'kilder', 'id-register.txt'), encoding='utf8') if l.strip()]
    brukt_id = set(reg) | set(plass)
    # nye bygg fra en tidligere kjøring beholder id-en sin om omrisset er det samme (id slettes aldri)
    forrige = {r['id']: Polygon(r['verdi']['p']) for r in ret_alle if egen(r) and r['op'] == 'ny'}
    neste_pb = 1 + max([int(r[3:]) for r in reg if r.startswith('pb-')] or [0])
    endelig = {i: G for i, G in nytt.items()}
    nye = []
    for k, (G, j, hvorfor) in enumerate(nye_bygg):
        gammel = next((fid for fid, FP in forrige.items() if FP.is_valid and FP.intersection(G).area > 0.8 * max(G.area, FP.area)), None)
        mine = sorted(til.pop(f'ny:{k}', []), key=lambda p: p['bygningsnummer'])
        if gammel:
            nid = gammel; forrige.pop(gammel)
        else:
            nid = next((f"bnr-{p['bygningsnummer']}" for p in mine if f"bnr-{p['bygningsnummer']}" not in brukt_id), None)
            if nid is None:
                nid = f'pb-{neste_pb}'; neste_pb += 1
        brukt_id.add(nid)
        til[nid] = mine
        nye.append(dict(id=nid, G=G, j=j, hvorfor=hvorfor))
        endelig[nid] = G
    alle_poly = {x['id']: P[x['id']] for x in vis}
    alle_poly.update(endelig)
    # 7. tak for alle husrekker med et endret eller nytt hus
    endret_ids = set(endelig)
    rekke_ids = [x['id'] for x in vis if x.get('gml') and x['id'] not in endelig] + list(endelig)
    rekke_poly = [alle_poly[i] for i in rekke_ids]
    gamle = {x['id']: x for x in vis}
    gamle_gavler = [(np.array(g[0][:2]), np.array(g[-1][:2])) for x in vis if x.get('gml')
                    for g in (x.get('gavl2') or []) if max(q[2] for q in g) > 0.3]
    gamle_kanter = [(np.array(a), np.array(b)) for x in vis if x.get('gml') for a, b in kanter(P[x['id']])]
    nye_tak = {}
    for g in ([] if os.environ.get('GRUNNMUR_UTEN_TAK') else tak.rekker(rekke_poly)):   # GRUNNMUR_UTEN_TAK=1: bare til feilsøking
        ids = [rekke_ids[k] for k in g]
        if not (set(ids) & endret_ids):
            continue
        U = tak.omriss_rekke([rekke_poly[k] for k in g])
        kU = tak._kanter(tak._rydd(U))
        fg = lambda a, b, U=U, kU=kU: gavl_arv(a, b, gamle_gavler, gamle_kanter, U)
        try:
            F, U2 = tak.skjelett(U, fg)
        except Exception as e:  # noqa: BLE001
            logg['usikre'].append(f"tak for rekka {', '.join(ids)} feilet ({e}); de gamle takflatene står")
            continue
        for k, i in zip(g, ids):
            if i in fredet:
                continue
            t2, g2 = tak.per_hus(F, U2, rekke_poly[k], fg)
            if t2:
                nye_tak[i] = (t2, g2)
    # 8. rettelser
    linjer = []
    for i, G in nytt.items():
        x = B[plass[i]]; p, ph = rund(G)
        linjer.append(rett(i, 'p', p)); linjer.append(rett(i, 'ph', ph))
        r, rf = rekt(G); linjer += [rett(i, 'r', r), rett(i, 'rf', rf), rett(i, 'tk', [r])]
    for i, (t2, g2) in nye_tak.items():
        if i in plass:
            linjer += [rett(i, 'tak2', t2, f'{GRUNN}: tak fra fotavtrykket (verktoy/tak.py)'),
                       rett(i, 'gavl2', g2, f'{GRUNN}: tak fra fotavtrykket (verktoy/tak.py)')]
    for i in nytt:
        x = B[plass[i]]; G = nytt[i]; Pg = poly(x)
        ms = forny_matrikkel(i, x.get('matrikkel') or [], til.get(i, []))
        if ms != (x.get('matrikkel') or []):
            linjer.append(rett(i, 'matrikkel', ms))
        # piper og arker følger det nye taket; vinduer fra tegningene flyttes inn på den nye veggen
        if i in nye_tak and x.get('piper'):
            t2 = nye_tak[i][0]; h0 = grunn_h.get(i, x.get('h', 0))
            pip = []
            for q in grunn_obj(grunn, i, 'piper') or x['piper']:
                if not G.buffer(-0.2).contains(Point(q[0], q[1])):
                    continue
                t = t_paa_tak(t2, q[0], q[1])
                pip.append([q[0], q[1], round(h0 + t * 0.82, 2)] + list(q[3:]))
            if pip != x['piper']:
                linjer.append(rett(i, 'piper', pip, f'{GRUNN}: pipene står på det nye taket'))
        if x.get('arker'):
            ark = [flytt_med_veggen(q, Pg, G) for q in x['arker']]
            ark = [q for q in ark if q is not None]
            if ark != x['arker']:
                linjer.append(rett(i, 'arker', ark, f'{GRUNN}: arkene følger veggen'))
        if x.get('vind') and er_fasit(x, ret_ovrige):
            rest = []
            vind, flyttet, ute = flytt_vinduer(x['vind'], Pg, G, x.get('h', 99), rest)
            linjer.append(rett(i, 'vind', vind, f'{GRUNN}: vinduene fra kvartaltegningen flyttet inn på den nye veggen'))
            # vinduer på en del som er skilt ut som nytt bygg, følger med dit
            videre = 0
            for nb in nye:
                if not rest: break
                her = [v for v in rest if nb['G'].buffer(0.6).contains(Point(v[0], v[1]))]
                if not her: continue
                vv, f2, u2 = flytt_vinduer(her, Pg, nb['G'], 99)
                if vv:
                    nb.setdefault('vind', []).extend(vv); nb['fasade_fra'] = i; videre += len(vv)
                rest = [v for v in rest if v not in her]
            if flyttet or ute:
                logg.setdefault('vinduer', []).append(f"{i} ({x.get('navn')}): {len(vind)} vinduer/dører beholdt, {flyttet} skjøvet langs veggen for hjørneklaring, {videre} fulgte med til utskilt del, {ute - videre} tatt ut (ingen vegg å stå på)")
    hgj = dom_p50({nb['id']: nb['G'] for nb in nye})    # første gjetning på vegghøyden; legg_inn.py setter målt høyde der den er sikker
    for nb in nye:
        i, G = nb['id'], nb['G']; p, ph = rund(G); r, rf = rekt(G)
        ms = [mfelt(q) for q in sorted(til.get(i, []), key=lambda q: q['bygningsnummer'])]
        if i.startswith('bnr-') and int(i[4:]) not in [m['bygningsnummer'] for m in ms]:
            ms = [mfelt(egne_punkt[int(i[4:])])] + ms
        t2, g2 = nye_tak.get(i, ([], []))
        p50 = hgj.get(i, (None,))[0]
        hgjett = round(float(np.clip(p50 - 1.0, 2.2, 15.0)), 1) if p50 is not None else (2.6 if G.area < 30 else 6.0)
        obj = {"id": i, "p": p, "ph": ph, "h": hgjett, "r": r, "rf": rf, "tk": [r], "tak": STANDARD_TAK, "vegg": STANDARD_VEGG,
               "taks": [round(v * 0.75) for v in STANDARD_TAK], "veggs": [round(v * 0.86) for v in STANDARD_VEGG],
               "navn": None, "type": typ_fra_matrikkel(ms), "adr": None, "cov": 0.0, "gml": 1, "tak2": t2, "gavl2": g2,
               "piper": [], "vind": [], "fasade_kilde": "antatt", "farge_kilde": "standard: nytt hus fra kommunekartet, farge ikke valgt",
               "matrikkel": ms, "kilde": f"{GRUNN} (kommunehus {nb['j']}: {nb['hvorfor']})"}
        if not ms:
            obj.pop('matrikkel')
        if nb.get('vind'):      # delen har vinduer fra kvartaltegningen til huset den er skilt ut fra: fasit, vinduer_regler.py rører den ikke
            obj['vind'] = nb['vind']; obj['fasade_kilde'] = 'kvartaltegning'; obj['fasade_fra'] = nb['fasade_fra']
        linjer.append({"emne": "bygg", "id": i, "op": "ny", "verdi": obj, "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: {nb['hvorfor']}"})
        logg['nye'].append(dict(id=i, areal=round(G.area, 1), kommunehus=nb['j'], hvorfor=nb['hvorfor'], type=obj['type'],
                                xy=[round(G.centroid.x, 1), round(G.centroid.y, 1)]))
    for h in gjenreist:
        linjer.append(rett(h, 'skjul', None, f'{GRUNN}: bygningen står i kommunekartet (FKB); skjult etter flyfotoet, som er forskjøvet her'))
    linjer += skjul
    # tidligere nye bygg som ikke lenger trengs: id-en slettes aldri, bygget skjules med grunn
    for fid, FP in forrige.items():
        old = next(r for r in ret_alle if egen(r) and r['op'] == 'ny' and r['id'] == fid)
        linjer.append(old)
        linjer.append({"emne": "bygg", "id": fid, "op": "skjul", "hvem": HVEM, "dato": DATO, "grunn": f"{GRUNN}: omrisset finnes ikke lenger i planen"})
    logg['tall'] = dict(kommunehus_i_gamlebyen=len(Kin), endret=len(logg['endret']), slatt_sammen=len(logg['delt']),
                        delt_i_modellen=len(logg['delt_i_modell']), gjenreist=len(gjenreist), nye=len(nye), skjult=len(skjul), usikre=len(logg['usikre']),
                        smaa_hoppet_over=len(logg['smaa']), tak_regnet_paa_nytt=len(nye_tak),
                        uendret=len(logg['uendret']))
    return ret_ovrige, linjer, logg, dict(K=K, Kin=Kin, P=P, endelig=endelig, nye=nye, gml=gml, DEK=DEK)


def x_gml(B, plass, i):
    return bool(B[plass[i]].get('gml'))


def grunn_obj(grunn, i, felt):
    for x in grunn:
        if x['id'] == i:
            return x.get(felt)
    return None


def kanter(P):
    c = np.array(P.exterior.coords)
    return [(c[k], c[k + 1]) for k in range(len(c) - 1) if np.hypot(*(c[k + 1] - c[k])) > 0.3]


def gavl_arv(a, b, gamle_gavler, gamle_kanter, U):
    """Gavl der det gamle taket hadde gavl på omtrent samme vegg (innen 1 m, parallell, minst halve lengden);
    valm der det gamle taket hadde valm; ellers tak.gavl_regel (fløyende som er korte nok får saltak)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = float(np.hypot(*(b - a)))
    if L < 1e-6:
        return False
    u = (b - a) / L; n = np.array([-u[1], u[0]])
    def dekning(segs):
        cov = 0.0
        for s0, s1 in segs:
            l = float(np.hypot(*(s1 - s0)))
            if l < 1e-6 or abs(((s1 - s0) / l) @ u) < 0.97:
                continue
            m = (s0 + s1) / 2
            if abs((m - a) @ n) > 1.0:
                continue
            t0, t1 = sorted([(s0 - a) @ u, (s1 - a) @ u]); cov += max(0.0, min(t1, L) - max(t0, 0.0))
        return cov
    if dekning(gamle_gavler) >= 0.5 * L:
        return True
    if dekning(gamle_kanter) >= 0.5 * L:
        return False
    Ur = tak._rydd(U)
    kU = tak._kanter(Ur)
    best = min(kU, key=lambda k: np.hypot(*(k[0] - a)) + np.hypot(*(k[1] - b)))
    return tak.gavl_regel(Ur, best[0], best[1], kU)


def t_paa_tak(t2, x, y):
    """t (avstand inn fra takfoten) i punktet: høyeste flate over punktet."""
    best = 0.0
    for f in t2:
        F = Polygon([q[:2] for q in f])
        if F.is_valid and F.buffer(0.05).contains(Point(x, y)):
            A = np.array([[q[0], q[1], 1] for q in f]); z = np.array([q[2] for q in f])
            k = np.linalg.lstsq(A, z, rcond=None)[0]
            best = max(best, float(k[0] * x + k[1] * y + k[2]))
    return best


def er_fasit(x, ret):
    v33 = {r['id'] for r in ret if r['op'] == 'sett' and r.get('felt') == 'vind' and r.get('grunn', '').startswith('v33')}
    kas = {r['id'] for r in ret if r['op'] == 'sett' and r.get('felt') == 'vind' and r.get('grunn', '').startswith('Kaserna')}
    return x.get('fasade_kilde') == 'kvartaltegning' or x['id'] in v33 or x['id'] in kas


def ny_vegg(q, u_gammel, G, maks=2.0):
    """Veggen på det nye omrisset et punkt på den gamle veggen hører til: parallell (innen ~18°), nærmest, innen maks m."""
    best = None
    for a, b in kanter(G) + [(np.array(r.coords[k]), np.array(r.coords[k + 1])) for r in G.interiors for k in range(len(r.coords) - 1)]:
        L = float(np.hypot(*(b - a)))
        if L < 0.3:
            continue
        u = (b - a) / L
        if abs(u @ u_gammel) < 0.95:
            continue
        t = float((q - a) @ u); n = np.array([-u[1], u[0]]); dperp = abs(float((q - a) @ n))
        utenfor = max(0.0, -t, t - L)
        dd = dperp + 2 * utenfor
        if dd <= maks and (best is None or dd < best[0]):
            best = (dd, a, b, u, L)
    return best


def flytt_med_veggen(q, P_gml, G):
    """Ark (x, y, z, nx, ny, ...) flyttes vinkelrett så den står like langt fra den nye veggen som fra den gamle."""
    qq = np.array(q[:2], float); nrm = np.array(q[3:5], float)
    u_g = np.array([-nrm[1], nrm[0]])
    vn = ny_vegg(qq, u_g, G, maks=3.0); vg = ny_vegg(qq, u_g, P_gml, maks=3.0)
    if vn is None or vg is None:
        return list(q) if G.contains(Point(qq)) else None
    u = vn[3]; n = np.array([-u[1], u[0]])
    d_gml, d_ny = float((qq - vg[1]) @ n), float((qq - vn[1]) @ n)
    ny = qq + n * (d_gml - d_ny)
    return [round(float(ny[0]), 2), round(float(ny[1]), 2)] + list(q[2:])


def flytt_vinduer(vind, P_gml, G, h, rest=None):
    """Vinduer og dører fra kvartaltegningen flyttes vinkelrett inn på den nye veggen; rekkefølge, høyde og størrelse står.
    Vinduer som ellers ville stått i hjørnet (regel 04: halv bredde + 0,3 m), skyves langs veggen; er veggen for kort,
    tas de ut. Vinduer uten vegg på det nye omrisset legges i rest (de kan stå på en del som er skilt ut som eget bygg)."""
    ut, flyttet, borte = [], 0, 0
    for v in vind:
        q = np.array(v[:2], float); u_g = np.array(v[3:5], float); w = v[7]
        bv = ny_vegg(q, u_g, G)
        if bv is None:
            borte += 1
            if rest is not None: rest.append(v)
            continue
        _, a, b, u, L = bv
        if u @ u_g < 0:
            u = -u; a, b = b, a
        t = float((q - a) @ u)
        lo, hi = w / 2 + 0.32, L - w / 2 - 0.32
        if lo > hi:
            borte += 1; continue
        t2 = min(max(t, lo), hi)
        if abs(t2 - t) > 1e-3:
            flyttet += 1
        p = a + u * t2
        n_g = np.array(v[5:7], float); n = np.array([-u[1], u[0]])
        if n @ n_g < 0:
            n = -n
        ut.append([round(float(p[0]), 2), round(float(p[1]), 2), v[2], round(float(u[0]), 4), round(float(u[1]), 4),
                   round(float(n[0]), 4), round(float(n[1]), 4)] + list(v[7:]))
    return ut, flyttet, borte


def forny_matrikkel(i, gamle, punkter):
    """Matrikkelfeltet etter nytt omriss: punktene som står i omrisset; husets eget nummer (id-en) står alltid."""
    ms = [mfelt(p) for p in sorted(punkter, key=lambda p: p['bygningsnummer'])]
    if i.startswith('bnr-'):
        n = int(i[4:])
        if n not in [m['bygningsnummer'] for m in ms]:
            eget = next((m for m in gamle if m['bygningsnummer'] == n), None)
            if eget:
                ms = [eget] + ms
    return ms


def dom_p50(polys):
    """p50, p90 og antall piksler av Kartverkets DOM−DTM i hvert omriss (samme kilde og forskyvning som rapport/hoyder)."""
    import importlib.util
    H = os.path.join(ROT, 'rapport', 'hoyder')
    spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    dom, gt = hent.les(os.path.join(H, 'kilder', 'dom1_25832.tif')); dtm, _ = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif'))
    ndh = dom - dtm; x0, y1, dx, dy = gt; Hh, W = ndh.shape
    SH = tuple(json.load(open(os.path.join(H, 'tall.json')))['forskyvning'])
    cx = x0 + (np.arange(W) + 0.5) * dx; cy = y1 - (np.arange(Hh) + 0.5) * dy
    ut = {}
    for i, Pm in polys.items():
        u = hent.til_utm(np.array(Pm.exterior.coords)) + SH
        pg = Polygon(u)
        a, b, c, d = pg.bounds
        c0, c1 = max(0, int((a - x0) / dx)), min(W, int((c - x0) / dx) + 2)
        r0, r1 = max(0, int((y1 - d) / dy)), min(Hh, int((y1 - b) / dy) + 2)
        XX, YY = np.meshgrid(cx[c0:c1], cy[r0:r1])
        inn = shapely.contains_xy(pg.buffer(-0.5) if pg.buffer(-0.5).area > 4 else pg, XX, YY)
        v = ndh[r0:r1, c0:c1][inn]; v = v[~np.isnan(v)]
        ut[i] = (float(np.percentile(v, 50)), float(np.percentile(v, 90)), int(len(v))) if len(v) else (None, None, 0)
    return ut


# --------------------------------------------------------------------------------------------------------------
def ark():
    """Før/etter i plan, nord opp: kommunens omriss grått, gamle modellomriss rødt, nye blått. Ikke i git."""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ret = datalag.les('rettelser')
    d0 = datalag.alle(raa=True); g0 = [dict(x) for x in d0['bygg']]
    mine_ny = {r['id'] for r in ret if egen(r) and r['op'] == 'ny'}
    foer = datalag.hoyden_styrer(datalag.legg_paa_rettelser(d0, [r for r in ret if not egen(r) and r.get('id') not in mine_ny]), g0)['bygg']
    etter = datalag.alle()['bygg']
    K = kommunekart.omriss(); DEK = kommunekart.dekning()
    gml = [x for x in etter if x.get('gml') and len(x['p']) >= 3 and not x.get('skjul')]
    allp = unary_union([poly(x) for x in gml if DEK.contains(poly(x).representative_point())])
    x0, y0, x1, y1 = allp.bounds
    fig, ax = plt.subplots(figsize=(30, 30 * (y1 - y0) / (x1 - x0)), dpi=150)
    for k in K:
        if k.intersects(allp.buffer(20)):
            for g in getattr(k, 'geoms', [k]):
                ax.fill(*g.exterior.xy, fc='#c9c9c9', ec='none')
    ids_etter = {x['id'] for x in gml}
    for x in foer:
        if x.get('gml') and len(x['p']) >= 3 and not x.get('skjul'):
            q = np.array(x['p'] + [x['p'][0]]); ax.plot(q[:, 0], q[:, 1], c='#d1242f', lw=0.9)
    for x in etter:
        if x.get('gml') and len(x['p']) >= 3 and not x.get('skjul'):
            q = np.array(x['p'] + [x['p'][0]]); ax.plot(q[:, 0], q[:, 1], c='#0969da', lw=0.7)
            if str(x.get('kilde', '')).startswith(GRUNN):
                c = poly(x).representative_point(); ax.plot(c.x, c.y, 'o', ms=3, c='#0969da')
        elif x.get('skjul') and str(x['skjul']).find(GRUNN) >= 0:
            q = np.array(x['p'] + [x['p'][0]]); ax.plot(q[:, 0], q[:, 1], c='#d1242f', lw=1.6, ls=':')
            c = poly(x).representative_point(); ax.text(c.x, c.y, x['id'], fontsize=7, color='#d1242f')
    ax.set_xlim(x0 - 15, x1 + 15); ax.set_ylim(y0 - 15, y1 + 15); ax.set_aspect('equal')
    ax.set_title('Gamlebyen: kommunens omriss (grått), gamle modellomriss (rødt), nye (blått; prikk = nytt bygg; rød prikket = skjult)', fontsize=13)
    os.makedirs(UT, exist_ok=True)
    fig.savefig(os.path.join(UT, 'oversikt.png'), bbox_inches='tight'); plt.close(fig)
    print('skrev', os.path.join(UT, 'oversikt.png'))


def main(tørt=False):
    ret_ovrige, linjer, logg, _ = plan()
    os.makedirs(UT, exist_ok=True)
    json.dump(logg, open(os.path.join(UT, 'plan.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(json.dumps(logg['tall'], ensure_ascii=False))
    if tørt:
        return
    # ny-linjene først (datalaget lager de nye byggene før noen rettelse peker på dem uansett), så resten i rekkefølge
    datalag.skriv_rettelser(ret_ovrige + linjer)
    nye_ids = [r['id'] for r in linjer if r['op'] == 'ny']
    reg_f = os.path.join(ROT, 'kilder', 'id-register.txt')
    reg = [l.strip() for l in open(reg_f, encoding='utf8') if l.strip()]
    ny_reg = [i for i in nye_ids if i not in reg]
    if ny_reg:
        with open(reg_f, 'a', encoding='utf8') as f:
            f.write(''.join(i + '\n' for i in ny_reg))
    print(f"{len(linjer)} rettelser skrevet, {len(ny_reg)} nye id-er i registeret")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'ark':
        ark()
    else:
        main('--tørt' in sys.argv)
