#!/usr/bin/env python3
"""Bryggene: fergeleiet, gjestehavna, Isegran og båtplassene langs Glomma innen kartrammen, målt mot Fredrikstad kommunes
ortofoto 2024 (samme fliser og samme transform som verktoy/flater.py og verktoy/vann.py) med OpenStreetMap som struktur.

    python3 verktoy/brygger.py hent      OSM (man_made=pier, floating=yes, leisure=marina, mooring) -> kilder/brygger-osm.json
    python3 verktoy/brygger.py maal      data/brygger.json: OSM-bryggene sjekket mot ortofotoet, bryggene fotoet viser som OSM ikke har,
                                         og håndmålte rettinger (kilder/brygger-maalt.json); faste id-er (br-) i kilder/id-register.txt
    python3 verktoy/brygger.py ark       kontrollark før/etter per område (rapport/brygger/<omraade>-<for|etter>.jpg, ikke i git) og tall.json

Ortofotoet avgjør hvor bryggene ligger; OSM gir struktur (senterlinje, type, flytende eller fast). Ortofotoet er BARE kontroll
(lisensen er ikke avklart): ingen piksel fra det vises i kartet, og bildene med fotoet ligger ikke i git.

Hver brygge i data/brygger.json:
  id      br-<løpenummer>, fast (ankerpunkt i kilder/brygger-anker.json, som vannflatene); slettes aldri, skjules med grunn
  typ     fast (fast brygge / kai-utstikker på påler), flytebrygge, utrigger (smal finger ut fra en flytebrygge)
  p       omrisset (modellmeter, mot klokka); senterlinje + bredde fra OSM/håndmåling blir gjort om til omriss her
  z       dekkets høyde over vannflaten (m): fast ca. 1,0, flytende ca. 0,4 (src/18_brygger.js tegner fra vannflaten y=0,15)
  kilde   osm/<type>/<id>, ortofoto 2024 eller håndmålt, med grunn
"""
import json, math, os, sys, time, urllib.request, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag  # noqa: E402

OSM = os.path.join(ROT, 'kilder', 'brygger-osm.json')
MAALT = os.path.join(ROT, 'kilder', 'brygger-maalt.json')
ANKER = os.path.join(ROT, 'kilder', 'brygger-anker.json')
REG = os.path.join(ROT, 'kilder', 'id-register.txt')
RAMME = 860

HOYDE = {'fast': 1.0, 'flytebrygge': 0.4, 'utrigger': 0.35}
BREDDE = {'fast': 3.0, 'flytebrygge': 2.4, 'utrigger': 0.8}    # når OSM bare har en linje og ingen width

# områdene eieren nevnte (modellmeter x0, y0, x1, y1), til kontrollark og opptelling; det første som treffer, gjelder
OMRAADER = {
    'fergeleiet': (-110, 230, 220, 460),        # fergeleiet Gamlebyen, fergeleiet Sentrum på andre siden, bryggene nord for Gamlebyen
    'toldbodgaten': (-200, -100, 0, 230),       # gjestebrygga i Toldbodgaten og stikkerne ved båtopplaget
    'isegran': (-720, -450, -380, 230),         # Isegran: verftet, museumsbrygga, kanalen og havna i sør
    'ostbredden-sor': (-380, -700, -300, -400),  # båtplassene på østbredden sør for Gamlebyen
    'glomma-sor': (-860, -860, 860, -400),      # resten av elva sør (fergeleiet Smertu)
}


def omraade(x, y):
    for navn, (a, b, c, d) in OMRAADER.items():
        if a <= x <= c and b <= y <= d:
            return navn
    return 'ellers'


def fra_modell(x, y):
    R = 6378137.0
    mx, my = x / datalag._S + datalag._MX0, y / datalag._S + datalag._MY0
    return math.degrees(mx / R), math.degrees(2 * math.atan(math.exp(my / R)) - math.pi / 2)


# ---- hent: OSM ----
OSM_API = 'https://api.openstreetmap.org/api/0.6/map?bbox={},{},{},{}'


def _vil_ha(t):
    """Taggene som gir brygger (og det som forteller hvor de er: marina, fortøyning, fergekai)."""
    return (t.get('man_made') in ('pier', 'quay') or t.get('floating') == 'yes' or t.get('leisure') in ('marina', 'slipway')
            or 'mooring' in t or t.get('amenity') == 'ferry_terminal')


def _get(url):
    for k in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'fredrikstad-fortress-town (Page Black)'}), timeout=150).read()
        except Exception:
            if k == 3:
                raise
            time.sleep(5 + 10 * k)


def hent():
    """Overpass (overpass-api.de) kutter forbindelsen gjennom proxyen (rapport/benker-gjerder), derfor OSM-API-et direkte (/map),
    i 4 x 4 ruter over kartrammen, og taggene filtreres her. Samme objekter som Overpass-spørringen
    man_made=pier|quay, floating=yes, leisure=marina|slipway, mooring=*, amenity=ferry_terminal ville gitt."""
    import xml.etree.ElementTree as ET
    noder, veier, rel = {}, {}, {}
    n = 4; s = 2 * RAMME / n
    for i in range(n):
        for j in range(n):
            lo0, la0 = fra_modell(-RAMME + i * s, -RAMME + j * s); lo1, la1 = fra_modell(-RAMME + (i + 1) * s, -RAMME + (j + 1) * s)
            x = ET.fromstring(_get(OSM_API.format(f'{lo0:.6f}', f'{la0:.6f}', f'{lo1:.6f}', f'{la1:.6f}')))
            for e in x:
                t = {k.get('k'): k.get('v') for k in e.findall('tag')}
                if e.tag == 'node':
                    noder[e.get('id')] = (float(e.get('lon')), float(e.get('lat')), t)
                elif e.tag == 'way':
                    veier[e.get('id')] = ([nd.get('ref') for nd in e.findall('nd')], t)
                elif e.tag == 'relation':
                    rel[e.get('id')] = ([(m.get('type'), m.get('ref'), m.get('role')) for m in e.findall('member')], t)
            print('rute', i, j, len(noder), len(veier), len(rel))
    M = lambda ref: [round(v, 2) for v in datalag.til_modell(noder[ref][0], noder[ref][1])]
    ut = []
    for k, (lo, la, t) in noder.items():
        if _vil_ha(t):
            ut.append({'osm': f'node/{k}', 'tags': t, 'geo': [M(k)]})
    for k, (nds, t) in veier.items():
        if _vil_ha(t) and all(r in noder for r in nds):
            ut.append({'osm': f'way/{k}', 'tags': t, 'geo': [M(r) for r in nds]})
    for k, (mm, t) in rel.items():
        if _vil_ha(t):
            ringer = [[M(r) for r in veier[ref][0] if r in noder] for typ, ref, rolle in mm if typ == 'way' and rolle == 'outer' and ref in veier]
            ut.append({'osm': f'relation/{k}', 'tags': t, 'geo': ringer})
    meta = {'kilde': 'OpenStreetMap, API 0.6 /map over kartrammen (±860 m)', 'lisens': 'ODbL 1.0, © OpenStreetMap-bidragsyterne',
            'hentet': time.strftime('%Y-%m-%d'), 'filter': 'man_made=pier|quay, floating=yes, leisure=marina|slipway, mooring=*, amenity=ferry_terminal',
            'koordinater': 'modellmeter (datalag.til_modell)', 'objekter': ut}
    with open(OSM, 'w', encoding='utf8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=0)
    print(f'{len(ut)} OSM-objekter -> {os.path.relpath(OSM, ROT)}')
    for o in ut:
        print(' ', o['osm'], {k: v for k, v in o['tags'].items() if k in ('man_made', 'floating', 'leisure', 'mooring', 'name', 'width', 'area', 'amenity')}, len(o['geo']))


def maalt():
    return json.load(open(MAALT, encoding='utf8'))


# ---- maal: data/brygger.json ----
def _poly_fra(f, typ):
    """Omriss fra en håndmåling eller et OSM-objekt: «p» (polygon) eller «linje» + «bredde» (flate ender, rette hjørner)."""
    from shapely.geometry import Polygon, LineString
    if 'p' in f:
        return Polygon(f['p']).buffer(0)
    return LineString(f['linje']).buffer(f.get('bredde', BREDDE[typ]) / 2, cap_style=2, join_style=2)


BOM_SOK = 1.5      # m: hver bom søkes så langt til hver side av der avstanden setter den
BOM_LYS = 9.0      # gjennomsnittlig lyshet over vannet langs bommen (white top-hat, 1,1 m) for at bommen regnes som sett i fotoet


def _rad(f, hindre):
    """Utriggere langs en brygge, målt i ortofotoet: bommene ligger omtrent hver «avstand» m fra «rad»[0] til «rad»[1] og går «lengde» m
    ut i retning «ut». Hver bom flyttes til der fotoet viser en lys, tynn linje (søk ±BOM_SOK m langs brygga); en bom fotoet ikke
    viser (ingen lys linje), tas ikke med. En bom som krysser en annen brygge (utstikkerne), tas ikke med."""
    import cv2, numpy as np
    import flater
    from shapely.geometry import LineString
    (ax, ay), (bx, by) = f['rad']; L = math.hypot(bx - ax, by - ay); dx, dy = (bx - ax) / L, (by - ay) / L
    ux, uy = f['ut']; n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
    lg = f['lengde']; mpp = 0.125
    xs = [ax, bx, ax + ux * lg, bx + ux * lg]; ys = [ay, by, ay + uy * lg, by + uy * lg]
    im, px = flater.ortofoto(min(xs) - 3, min(ys) - 3, max(xs) + 3, max(ys) + 3, mpp=mpp)
    th = cv2.morphologyEx(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(float)

    def lys(t):   # snittet langs bommen, fra 2 m ut (bryggekanten selv er lys) til enden
        s = np.linspace(2.0, lg, int(lg / mpp))
        c, r = px(ax + dx * t + ux * s, ay + dy * t + uy * s)
        c = np.clip(np.round(c).astype(int), 0, th.shape[1] - 1); r = np.clip(np.round(r).astype(int), 0, th.shape[0] - 1)
        return th[r, c].mean()
    ut, sist = [], -99.0; t = f['avstand'] / 2
    while t < L:
        kand = [(lys(t + d), t + d) for d in np.arange(-BOM_SOK, BOM_SOK + 1e-6, mpp) if 0 <= t + d <= L and t + d - sist >= 2.0]
        if kand:
            verdi, tt = max(kand)
            p0, p1 = (ax + dx * tt, ay + dy * tt), (ax + dx * tt + ux * lg, ay + dy * tt + uy * lg)
            if verdi >= BOM_LYS and not any(LineString([(p0[0] + ux * 1.5, p0[1] + uy * 1.5), p1]).distance(h) < 1.0 for h in hindre):
                b = dict(f, linje=[[round(p0[0], 2), round(p0[1], 2)], [round(p1[0], 2), round(p1[1], 2)]])
                if foto_bom(list(_poly_fra(b, 'utrigger').exterior.coords)) >= BOM_LYS:   # samme mål som regel 18
                    ut.append(b); sist = tt
        t += f['avstand']
    return ut


def _ringen(pg):
    from shapely.geometry.polygon import orient
    pg = orient(pg.simplify(0.05), 1.0)
    return [[round(x, 2), round(y, 2)] for x, y in list(pg.exterior.coords)[:-1]]


def _retning(pg):
    """Vinkelen (radianer, fra x-aksen) til bryggas lange side: plankene ligger på tvers av den."""
    r = list(pg.minimum_rotated_rectangle.exterior.coords)
    a, b, c = r[0], r[1], r[2]
    if math.hypot(b[0] - a[0], b[1] - a[1]) >= math.hypot(c[0] - b[0], c[1] - b[1]):
        return round(math.atan2(b[1] - a[1], b[0] - a[0]), 3)
    return round(math.atan2(c[1] - b[1], c[0] - b[0]), 3)


def _ider(polys):
    """Faste id-er (br-<løpenummer>) som vannflatene: hver id har et ankerpunkt i kilder/brygger-anker.json; en brygge som lages
    på nytt, får id-en til ankeret som ligger i den (eller innen 1 m). En id gjenbrukes aldri og står i kilder/id-register.txt."""
    from shapely.geometry import Point
    anker = json.load(open(ANKER, encoding='utf8')) if os.path.exists(ANKER) else {}
    reg = [l.strip() for l in open(REG, encoding='utf8') if l.strip()]
    n = max([int(i[3:]) for i in reg if i.startswith('br-')], default=0)
    ider, brukt, nye = [None] * len(polys), set(), []
    for i in sorted(range(len(polys)), key=lambda i: -polys[i].area):
        pg = polys[i]
        treff = [k for k, a in anker.items() if k not in brukt and pg.contains(Point(a))] or \
                [k for k, a in anker.items() if k not in brukt and pg.distance(Point(a)) < 1.0]
        if treff:
            ider[i] = treff[0]
        else:
            n += 1; ider[i] = f'br-{n}'; a = pg.representative_point()
            anker[ider[i]] = [round(a.x, 2), round(a.y, 2)]; nye.append(ider[i])
        brukt.add(ider[i])
    with open(ANKER, 'w', encoding='utf8') as f:
        f.write('{\n' + ',\n'.join(f'"{k}":{json.dumps(v)}' for k, v in sorted(anker.items(), key=lambda kv: int(kv[0][3:]))) + '\n}\n')
    if nye:
        open(REG, 'a', encoding='utf8').write('\n'.join(nye) + '\n')
    return ider, sorted(set(anker) - brukt, key=lambda k: int(k[3:]))


def lag_brygger():
    """Bryggene som liste av (polygon, egenskaper), fra OSM (rettet i kilder/brygger-maalt.json «osm») og håndmålingene («nye»)."""
    from shapely.geometry import box
    osm = json.load(open(OSM, encoding='utf8'))['objekter']; M = maalt()
    ramme = box(-RAMME, -RAMME, RAMME, RAMME)
    ut = []
    for o in osm:
        t = o['tags']; r = M['osm'].get(o['osm'], {})
        if not o['osm'].startswith('way') or len(o['geo']) < 2 or r.get('skjul'):
            continue
        if t.get('man_made') != 'pier' and 'typ' not in r:   # kai (quay), slipp, fergeleie-punkt: ikke brygge, med mindre målt for hånd
            continue
        typ = r.get('typ') or ('flytebrygge' if t.get('floating') == 'yes' else 'fast')
        lukket = o['geo'][0] == o['geo'][-1] and len(o['geo']) > 3
        f = {'p': o['geo'][:-1]} if lukket else {'linje': o['geo'], 'bredde': float(str(t.get('width', BREDDE[typ])).split()[0])}
        flate = r.get('flate') or {'metal': 'metall', 'wood': 'tre'}.get(t.get('surface') or t.get('material'), 'tre')
        ut.append((_poly_fra(f, typ), {'typ': typ, 'flate': flate, 'navn': t.get('name'), 'kilde': f"OSM {o['osm']}",
                                       'grunn': r.get('grunn', 'OSM, sjekket mot ortofoto 2024')}))
    enkle = [f for f in M['nye'] if 'rad' not in f]
    for f in enkle:
        ut.append((_poly_fra(f, f['typ']), {'typ': f['typ'], 'flate': f.get('flate', 'tre'), 'navn': f.get('navn'),
                                            'kilde': 'håndmålt i ortofoto 2024 (kilder/brygger-maalt.json)', 'grunn': f['grunn']}))
    hindre = [pg for pg, e in ut if e['typ'] != 'utrigger']
    for f in [f for f in M['nye'] if 'rad' in f]:
        for k, b in enumerate(_rad(f, hindre)):
            ut.append((_poly_fra(b, 'utrigger'), {'typ': 'utrigger', 'flate': 'tre', 'navn': f"{f['navn']} ({k + 1})",
                                                  'kilde': 'håndmålt i ortofoto 2024 (kilder/brygger-maalt.json, rad)', 'grunn': f['grunn']}))
    return [(pg.intersection(ramme), e) for pg, e in ut if pg.intersection(ramme).area > 0.2]


def maal():
    br = lag_brygger()
    br = [(pg if pg.geom_type == 'Polygon' else max(pg.geoms, key=lambda g: g.area), e) for pg, e in br]
    ider, borte = _ider([pg for pg, _ in br])
    data = []
    for (pg, e), idd in sorted(zip(br, ider), key=lambda z: int(z[1][3:])):
        c = pg.representative_point()
        x = {'id': idd, 'typ': e['typ'], 'p': _ringen(pg), 'z': HOYDE[e['typ']], 'retning': _retning(pg), 'flate': e['flate'],
             'omraade': omraade(c.x, c.y), 'kilde': e['kilde'], 'grunn': e['grunn']}
        if e.get('navn'):
            x['navn'] = e['navn']
        data.append(x)
    for idd in borte:   # en id slettes aldri: brygga som ikke finnes lenger, står skjult med grunn
        data.append({'id': idd, 'typ': 'fast', 'p': [], 'z': 1.0, 'skjul': 'verktoy/brygger.py: brygga finnes ikke lenger i kildene'})
    with open(os.path.join(ROT, 'data', 'brygger.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(v, ensure_ascii=False, separators=(',', ':')) for v in data) + '\n]\n')
    tall = {}
    for x in data:
        if not x.get('skjul'):
            tall.setdefault(x['omraade'], {}).setdefault(x['typ'], 0); tall[x['omraade']][x['typ']] += 1
    print(f'data/brygger.json: {len(data)} brygger', json.dumps(tall, ensure_ascii=False))


# ---- kontroll mot fotoet ----
VANN_MORK = 78   # HSV-verdi: elva er mørk brun (målt 27.10 i ortofotoet: 51–57); bryggedekket er grått, blågrått eller lyst (60–200)
BRUN = 3         # R - B: vannet er brunt (R over B med 5–10); bryggedekket er grått eller blågrått (B >= R)


def foto_andel(p):
    """Andelen av omrisset der ortofotoet viser noe annet enn mørkt, brunt vann (bryggedekk, landgang, båt ved brygga).
    Tynne utriggere (under 0,6 m) måles med 0,3 m ekstra på hver side, så pikslene rundt bommen kommer med."""
    import cv2, numpy as np
    from shapely.geometry import Polygon
    pg = Polygon(p)
    if pg.minimum_rotated_rectangle.area and pg.area / max(pg.length / 2, 1e-6) < 0.6:
        pg = pg.buffer(0.3, join_style=2)
    x0, y0, x1, y1 = pg.bounds
    import flater
    im, px = flater.ortofoto(x0 - 1, y0 - 1, x1 + 1, y1 + 1, mpp=0.125)
    m = np.zeros(im.shape[:2], np.uint8)
    cv2.fillPoly(m, [np.round(np.array([px(x, y) for x, y in pg.exterior.coords]) * 8).astype(np.int32)], 1, shift=3)
    v = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 2].astype(int); rb = im[..., 2].astype(int) - im[..., 0].astype(int)
    vann = (v <= VANN_MORK) & (rb >= BRUN)
    return float(((~vann) & (m > 0)).sum() / max(m.sum(), 1))


def tynn(p):
    """Smalere enn 0,6 m (bom): måles som linje, ikke flate."""
    from shapely.geometry import Polygon
    pg = Polygon(p)
    return pg.area / max(pg.length / 2, 1e-6) < 0.6


def foto_bom(p):
    """Lysheten over vannet langs midtlinja til en tynn bom (white top-hat, 1,1 m), samme mål som _rad bruker. BOM_LYS eller mer = sett."""
    import cv2, numpy as np
    import flater
    from shapely.geometry import Polygon
    r = list(Polygon(p).minimum_rotated_rectangle.exterior.coords)[:4]
    s = [((r[i][0] + r[(i + 1) % 4][0]) / 2, (r[i][1] + r[(i + 1) % 4][1]) / 2) for i in range(4)]
    a, b = (s[0], s[2]) if math.dist(s[0], s[2]) > math.dist(s[1], s[3]) else (s[1], s[3])
    im, px = flater.ortofoto(min(a[0], b[0]) - 3, min(a[1], b[1]) - 3, max(a[0], b[0]) + 3, max(a[1], b[1]) + 3, mpp=0.125)
    th = cv2.morphologyEx(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(float)
    def snitt(t):
        c, rr = px(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        return float(th[np.clip(np.round(rr).astype(int), 0, th.shape[0] - 1), np.clip(np.round(c).astype(int), 0, th.shape[1] - 1)].mean())
    # den ene enden står på brygga (lys kant); som i _rad måles bommen fra ca. 2 m ut, fra den enden som gir mest
    return max(snitt(np.linspace(0.2, 1.0, 40)), snitt(np.linspace(0.0, 0.8, 40)))


def ark():
    """Kontrollark per område: FØR (kartet i dag: ingen brygger; gule ringer = bryggene som synes i ortofotoet) og ETTER
    (data/brygger.json: fast gul, flytebrygge magenta, utrigger grønn). Bildene inneholder ortofoto og ligger ikke i git."""
    import cv2, numpy as np
    import flater
    mappe = os.path.join(ROT, 'rapport', 'brygger'); os.makedirs(mappe, exist_ok=True)
    br = [b for b in datalag.les('brygger') if not b.get('skjul')]
    sett = maalt()['sett']; vann = datalag.alle()['vann']
    FARGE = {'fast': (0, 220, 255), 'flytebrygge': (255, 0, 255), 'utrigger': (60, 230, 60)}
    for navn, (x0, y0, x1, y1) in OMRAADER.items():
        pkt = [s for s in sett if omraade(s[0], s[1]) == navn]; bb = [b for b in br if b['omraade'] == navn]
        if not pkt and not bb:
            continue
        xs = [s[0] for s in pkt] + [q[0] for b in bb for q in b['p']]; ys = [s[1] for s in pkt] + [q[1] for b in bb for q in b['p']]
        a, b_, c, d = min(xs) - 15, min(ys) - 15, max(xs) + 15, max(ys) + 15
        mpp = max(c - a, d - b_) / 1400
        M, px = flater.ortofoto(a, b_, c, d, mpp=mpp)
        P = lambda p: np.round(np.array([px(*q) for q in p]) * 8).astype(np.int32)
        for tittel in ('for', 'etter'):
            im = M.copy()
            for v in vann:
                if len(v['p']) > 2:
                    cv2.polylines(im, [P(v['p'])], True, (255, 170, 0), 1, cv2.LINE_AA, shift=3)
            if tittel == 'etter':
                for x in bb:
                    cv2.polylines(im, [P(x['p'])], True, FARGE[x['typ']], 2 if x['typ'] != 'utrigger' else 1, cv2.LINE_AA, shift=3)
            for s in pkt:
                q = px(s[0], s[1]); cv2.circle(im, (int(q[0]), int(q[1])), 9, (0, 255, 255) if tittel == 'for' else (255, 255, 255), 1, cv2.LINE_AA)
            cv2.rectangle(im, (0, 0), (im.shape[1], 34), (0, 0, 0), -1)
            tekst = (f'{navn} FOR: kartet i dag har ingen brygger; {len(pkt)} brygger synes i ortofotoet (gule ringer)' if tittel == 'for' else
                     f'{navn} ETTER: {len(bb)} brygger i kartet (fast gul, flytebrygge magenta, utrigger gronn); ringer = sett i fotoet')
            cv2.putText(im, tekst, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(im, 'ortofoto 2024 (Fredrikstad kommune, bare kontroll); bla = vannkanten i kartet', (8, im.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1, cv2.LINE_AA)
            cv2.imwrite(os.path.join(mappe, f'{navn}-{tittel}.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 84])
        print(navn, len(pkt), 'sett,', len(bb), 'i kartet')


if __name__ == '__main__':
    kmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'hent': hent, 'maal': maal, 'ark': ark}.get(kmd, lambda: print(__doc__))()


