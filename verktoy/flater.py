#!/usr/bin/env python3
"""Bakkeflatene mot virkeligheten: ortofoto 2024 fra Fredrikstad kommune er fasit for torg, gater, plener, gårdsrom og parkering.

    python3 verktoy/flater.py hent        henter ortofotoflisene (kilder/ortofoto-2024/) og kommunens parkeringslag (kilder/parkering-kommunen.json)
    python3 verktoy/flater.py id          gir grønt og gårdsrom faste id-er (gr-/ga-<løpenummer>), rører aldri en id som finnes
    python3 verktoy/flater.py parkering   lager data/parkering.json fra kommunens lag + flatene målt i ortofoto (kilder/parkering-flater.json)
    python3 verktoy/flater.py ark [etter] kontrollark per område i rapport/flater/ (ortofoto med dagens flater tegnet på; «etter» = med rettelser)

Ortofotoet hentes i web-mercator (EPSG:3857). Modellens meter er web-mercator skalert ved origo (datalag.til_modell), så pikslene
ligger lineært i modellmeter: ingen egen projeksjon, ingen omregning per punkt. Lisensen er ikke avklart: flisene er bare til kontroll,
vises aldri i kartet og legges ikke i git (.gitignore); kontrollarkene er nedskalerte utsnitt.
"""
import json, math, os, sys, time, urllib.request, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag

ORTO = os.path.join(ROT, 'kilder', 'ortofoto-2024')
ORTO_URL = 'https://arcgis.fredrikstad.kommune.no/server/rest/services/Bakgrunnskart/Ortofoto_2024/MapServer/export'
PARK_URL = 'https://arcgis.fredrikstad.kommune.no/server/rest/services/TekniskDrift/Parkering/MapServer'
# området: vollene og et belte rundt (modellmeter), fliser på 256 m med 0,125 m per piksel
OMRAADE = (-448, -448, 832, 576)
FLIS, MPP = 256, 0.125


def _hent(url, fil=None, forsok=4):
    for k in range(forsok):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                b = r.read()
            if fil:
                open(fil, 'wb').write(b)
            return b
        except Exception as e:   # proxyen gir av og til 502 på første kall
            if k == forsok - 1:
                raise
            time.sleep(2 + 3 * k)


def til_merc(x, y):
    """Modellmeter -> EPSG:3857 (den omvendte av datalag.til_modell)."""
    return x / datalag._S + datalag._MX0, y / datalag._S + datalag._MY0


def hent_fliser(omraade=OMRAADE):
    """Ortofotoflisene over omraade (modellmeter). Samme rutenett (256 m fra OMRAADE-hjørnet), samme oppløsning og samme transform
    for alle verktøy; fliser som står i ortofoto-2024.json fra før, blir stående (verktoy/vann.py henter elva rundt hele kartrammen)."""
    os.makedirs(ORTO, exist_ok=True)
    mf = os.path.join(ORTO, 'ortofoto-2024.json')
    gml = {f['fil']: f for f in json.load(open(mf, encoding='utf8'))['fliser']} if os.path.exists(mf) else {}
    n = int(FLIS / MPP)
    rute = lambda v, a: a + math.floor((v - a) / FLIS) * FLIS   # rutenettet står fast på OMRAADE-hjørnet
    for ty in range(rute(omraade[1], OMRAADE[1]), omraade[3], FLIS):
        for tx in range(rute(omraade[0], OMRAADE[0]), omraade[2], FLIS):
            navn = f'flis_{tx}_{ty}.jpg'; fil = os.path.join(ORTO, navn)
            a, b = til_merc(tx, ty); c, d = til_merc(tx + FLIS, ty + FLIS)
            if not os.path.exists(fil):
                q = urllib.parse.urlencode({'bbox': f'{a},{b},{c},{d}', 'bboxSR': 3857, 'imageSR': 3857, 'size': f'{n},{n}',
                                            'format': 'jpg', 'f': 'image', 'transparent': 'false'})
                _hent(ORTO_URL + '?' + q, fil); print('hentet', navn)
            gml[navn] = {'fil': navn, 'x0': tx, 'y0': ty, 'x1': tx + FLIS, 'y1': ty + FLIS}
    meta = {'kilde': 'Fredrikstad kommune, Bakgrunnskart/Ortofoto_2024 (ArcGIS MapServer export)', 'url': ORTO_URL,
            'hentet': time.strftime('%Y-%m-%d'), 'lisens': 'ikke avklart: bare til kontroll, aldri vist i kartet, ikke i git',
            'srs': 'EPSG:3857 (bboxSR=imageSR=3857)', 'm_per_px': MPP, 'piksler': n,
            'transform': 'modell x = flis.x0 + (kolonne + 0,5) * m_per_px; modell y = flis.y1 - (rad + 0,5) * m_per_px (rad 0 øverst = nord)',
            'fliser': sorted(gml.values(), key=lambda f: (f['y0'], f['x0']))}
    json.dump(meta, open(mf, 'w', encoding='utf8'), ensure_ascii=False, indent=1)


def hent():
    hent_fliser(OMRAADE)
    x0, y0, x1, y1 = OMRAADE
    # parkering: alle tre lagene, hele området (modell -> grader via 3857)
    import pyproj
    tr = pyproj.Transformer.from_crs(3857, 4326, always_xy=True)
    lo0, la0 = tr.transform(*til_merc(x0, y0)); lo1, la1 = tr.transform(*til_merc(x1, y1))
    ut = {'kilde': 'Fredrikstad kommune ArcGIS TekniskDrift/Parkering', 'url': PARK_URL, 'hentet': time.strftime('%Y-%m-%d'),
          'lisens': 'Ikke oppgitt i tjenesten (data.norge.no: «ingen vilkår»); bekreft med kart@fredrikstad.kommune.no', 'lag': {}}
    for lag, navn in ((0, 'automater'), (1, 'plasser'), (2, 'soner')):
        q = urllib.parse.urlencode({'where': '1=1', 'outFields': '*', 'geometry': f'{lo0},{la0},{lo1},{la1}', 'geometryType': 'esriGeometryEnvelope',
                                    'inSR': 4326, 'outSR': 4326, 'f': 'geojson'})
        ut['lag'][navn] = json.loads(_hent(f'{PARK_URL}/{lag}/query?{q}'))['features']
    info = json.loads(_hent(f'{PARK_URL}/1?f=json'))
    ut['koder'] = {f['name']: {str(c['code']): c['name'] for c in f['domain']['codedValues']} for f in info['fields'] if f.get('domain')}
    json.dump(ut, open(os.path.join(ROT, 'kilder', 'parkering-kommunen.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print('parkering:', {k: len(v) for k, v in ut['lag'].items()})


def ortofoto(x0, y0, x1, y1, mpp=0.25):
    """Utsnitt av ortofotoet over modellrektangelet, satt sammen av flisene. Gir (bilde BGR, px) der px(x, y) -> (kolonne, rad)."""
    import cv2, numpy as np
    meta = json.load(open(os.path.join(ORTO, 'ortofoto-2024.json'), encoding='utf8'))
    W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp)); ut = np.full((H, W, 3), 255, np.uint8)
    f = meta['m_per_px'] / mpp
    for fl in meta['fliser']:
        if fl['x1'] <= x0 or fl['x0'] >= x1 or fl['y1'] <= y0 or fl['y0'] >= y1:
            continue
        im = cv2.imread(os.path.join(ORTO, fl['fil']))
        if im is None:
            continue
        im = cv2.resize(im, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        c0 = int(round((fl['x0'] - x0) / mpp)); r0 = int(round((y1 - fl['y1']) / mpp))
        a, b = max(c0, 0), max(r0, 0); c, d = min(c0 + im.shape[1], W), min(r0 + im.shape[0], H)
        if c > a and d > b:
            ut[b:d, a:c] = im[b - r0:d - r0, a - c0:c - c0]
    return ut, (lambda x, y: ((x - x0) / mpp, (y1 - y) / mpp))


# ---- faste id-er for flater som ikke hadde det (samme mønster som bygg: id + register, aldri gjenbruk) ----
ID_EMNER = {'gront': 'gr', 'gardsrom': 'ga'}


def gi_id():
    reg_fil = os.path.join(ROT, 'kilder', 'id-register.txt'); reg = [l.strip() for l in open(reg_fil, encoding='utf8') if l.strip()]
    nye = []
    for emne, pre in ID_EMNER.items():
        liste = datalag.les(emne)
        brukt = [int(i.split('-')[1]) for i in reg if i.startswith(pre + '-')]
        n = max(brukt, default=0)
        for x in liste:
            if 'id' not in x:
                n += 1; x['id'] = f'{pre}-{n}'; nye.append(x['id'])
        # id først i hvert objekt, så git-diffen og lesingen er grei
        liste = [{'id': x['id'], **{k: v for k, v in x.items() if k != 'id'}} for x in liste]
        with open(os.path.join(ROT, 'data', emne + '.json'), 'w', encoding='utf8') as f:   # én linje per objekt, som før
            f.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in liste) + '\n]\n')
    if nye:
        open(reg_fil, 'a', encoding='utf8').write('\n'.join(nye) + '\n')
    print(len(nye), 'nye id-er')


# ---- parkering ----
def parkering():
    """data/parkering.json: én post per plass i kommunens lag 1 innenfor området. id = parkering-1-<OBJECTID> (kommunens nøkkel, samme
    som rapport/poi/steder.json). Selve parkeringen lages av verktoy/parkering.py lag (flater fra kilder/flater-maalt.json og kilder/parkering-maalt.json); uten målt flate er
    posten et punkt (x, y) og tegnes ikke på bakken."""
    # parkeringen eies av verktoy/parkering.py (29.10: kategori, regler, antall «ukjent» med kilde, flater fra parkering-maalt.json også)
    import parkering as _parkering
    _parkering.lag()
    maalt = json.load(open(os.path.join(ROT, 'kilder', 'flater-maalt.json'), encoding='utf8'))
    # andre bakkeflater målt i ortofotoet (grus, heller, asfalt): nye objekter med fast id (fl-N), aldri gjenbrukt
    fl = [{**x, 'kilde': 'målt i ortofoto 2024 (kilder/flater-maalt.json)'} for x in maalt['flater']]
    # flatene klassifisert fra ortofotoet (verktoy/bakke.py overflater) står i samme fil og blir stående
    fl += [x for x in datalag.les('flater') if 'verktoy/bakke.py' in x.get('kilde', '')]
    ids = [x['id'] for x in fl]
    if len(set(ids)) != len(ids):
        raise SystemExit('flate-id brukt to ganger')
    with open(os.path.join(ROT, 'data', 'flater.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(u, ensure_ascii=False, separators=(',', ':')) for u in fl) + '\n]\n')
    reg_fil = os.path.join(ROT, 'kilder', 'id-register.txt'); reg = {l.strip() for l in open(reg_fil, encoding='utf8')}
    nye = [i for i in ids if i not in reg]
    if nye:
        open(reg_fil, 'a', encoding='utf8').write('\n'.join(nye) + '\n')
    print(len(fl), 'andre flater')


def rad(linje, bredde):
    """Senterlinje gjennom en rad biler + bredde -> rektangel (modellmeter)."""
    (a, b), (c, d) = linje; l = math.hypot(c - a, d - b); nx, ny = -(d - b) / l * bredde / 2, (c - a) / l * bredde / 2
    return [[round(a + nx, 1), round(b + ny, 1)], [round(c + nx, 1), round(d + ny, 1)], [round(c - nx, 1), round(d - ny, 1)], [round(a - nx, 1), round(b - ny, 1)]]


# ---- måling mot ortofotoet: grønt, og rettelser av gårdsrom og grøntflater ----
def gront_maske(im):
    """Gress/vegetasjon i ortofotoet (april 2024: gulgrønt gress, lite løv): grønn tone og nok metning. 1 = grønt."""
    import cv2, numpy as np
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return (((h >= 26) & (h <= 85) & (s >= 45) & (v >= 35))).astype(np.uint8)


def _maske(P, px, shape):
    import cv2, numpy as np
    m = np.zeros(shape[:2], np.uint8)
    for p in P: cv2.fillPoly(m, [np.array([px(*q[:2]) for q in p], np.int32)], 1)
    return m


def maal_flate(p, hindre, mpp=0.25, marg=4):
    """Måler én flate: (andel grønt av det åpne, grønne polygoner i modellmeter, åpent areal m²).
    Åpent = flaten minus hindre (hus, parkering, andre flater)."""
    import cv2, numpy as np
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    x0, y0, x1, y1 = min(xs) - marg, min(ys) - marg, max(xs) + marg, max(ys) + marg
    im, px = ortofoto(x0, y0, x1, y1, mpp)
    aapen = _maske([p], px, im.shape) & (1 - _maske(hindre, px, im.shape))
    g = gront_maske(im) & aapen
    k = int(round(0.75 / mpp)) | 1
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)); g = cv2.morphologyEx(g, cv2.MORPH_OPEN, np.ones((k, k), np.uint8)) & aapen
    a = int(aapen.sum())
    andel = float(g.sum()) / a if a else 0.0
    poly = []
    cs, _ = cv2.findContours(g, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        if cv2.contourArea(c) * mpp * mpp < 8: continue
        c = cv2.approxPolyDP(c, 0.5 / mpp, True)
        if len(c) < 3: continue
        poly.append([[round(x0 + (q[0][0] + 0.5) * mpp, 1), round(y1 - (q[0][1] + 0.5) * mpp, 1)] for q in c])
    return andel, poly, a * mpp * mpp


def hindre_paa_bakken(d):
    """Det som står på eller dekker bakken og ikke er gress: husene (fotavtrykk), parkeringsflatene og de målte flatene."""
    h = [b['p'] for b in d['bygg'] if b.get('p') and not b.get('skjul')]
    h += [p['p'] for p in d.get('parkering', []) if p.get('p') and not p.get('skjul')]
    h += [f['p'] for f in d.get('flater', []) if not f.get('skjul') and f['typ'] != 'gress']
    return h


def maal():
    """Gårdsrommene: grønt målt i ortofotoet blir feltet `gress` (polygonene som tegnes) og `typ`. Grøntflater (OSM) som ligger over
    parkering eller målte belagte flater, klippes. Alt skrives som rettelser med grunn; en rettelse som allerede gjelder, skrives ikke igjen."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    d = datalag.alle(); rett = datalag.les('rettelser'); dato = time.strftime('%Y-%m-%d'); nye = []
    gjeldende = {}
    for r in rett: gjeldende[(r['emne'], r.get('id'), r.get('felt'), r['op'])] = r.get('verdi')
    def sett(emne, i, felt, verdi, grunn):
        if gjeldende.get((emne, i, felt, 'sett'), object()) == verdi: return
        nye.append({'emne': emne, 'id': i, 'op': 'sett', 'felt': felt, 'verdi': verdi, 'hvem': 'Claude', 'dato': dato, 'grunn': grunn})
    hindre = hindre_paa_bakken(d); tall = {'gardsrom': 0, 'typ': 0, 'gront_klippet': 0}
    for g in d['gardsrom']:
        andel, poly, a = maal_flate(g['p'], hindre)
        typ = 'gress' if andel >= 0.5 else 'belagt'
        grunn = f"ortofoto 2024: {andel:.0%} grønt av {a:.0f} m² åpent gårdsrom (verktoy/flater.py maal)"
        if g['typ'] != typ: sett('gardsrom', g['id'], 'typ', typ, grunn); tall['typ'] += 1
        sett('gardsrom', g['id'], 'gress', poly, grunn); tall['gardsrom'] += 1
    dekk = unary_union([Polygon(p).buffer(0) for p in [p['p'] for p in d.get('parkering', []) if p.get('p')] + [f['p'] for f in d.get('flater', []) if f['typ'] != 'gress']])
    raa = {g['id']: g['p'] for g in datalag.les('gront')}   # klippes alltid fra grunndataene, så en ny måling erstatter den gamle
    for g in d['gront']:
        P = Polygon(raa[g['id']]).buffer(0)
        o = P.intersection(dekk).area
        if o < 10: continue
        rest = P.difference(dekk)
        biter = sorted(getattr(rest, 'geoms', [rest]), key=lambda q: -q.area)
        ny = [[round(x, 1), round(y, 1)] for x, y in list(biter[0].exterior.coords)[:-1]]
        sett('gront', g['id'], 'p', ny, f"ortofoto 2024: {o:.0f} m² av grøntflaten er parkering/belagt (kilder/flater-maalt.json), klippet bort"
             + (f"; {len(biter) - 1} mindre bit(er) utelatt" if len(biter) > 1 else ''))
        tall['gront_klippet'] += 1
    datalag.skriv_rettelser(rett + nye)
    print(len(nye), 'nye rettelser', tall)


# ---- kontrollark ----
# områdene vurderes hvert for seg: Gamlebyens kvartaler innenfor vollene, vollene og utenfor (Kongsten, Tolboden, sørsiden)
OMRAADER = [
    ('A-nordvest', -230, 120, -40, 280), ('B-nord', -60, 120, 130, 280), ('C-nordost', 110, 120, 280, 280),
    ('D-vest', -230, -30, -40, 130), ('E-midt', -60, -30, 130, 130), ('F-ost', 110, -30, 280, 130),
    ('G-sorvest', -230, -200, -40, -20), ('H-sor', -60, -200, 130, -20), ('I-sorost', 110, -200, 280, -20),
    ('J-tolboden', -420, 180, -200, 400), ('K-kongsten', 270, -330, 560, -40), ('L-sorsiden', -40, -360, 260, -180),
    ('M-ostvollen', 260, -40, 520, 260),
]
FARGER = {'plen': (90, 220, 90), 'gress-gardsrom': (40, 255, 160), 'belagt-gardsrom': (200, 200, 200), 'brostein': (0, 140, 255),
          'kjorevei': (255, 0, 255), 'gangvei': (255, 200, 0), 'parkering': (0, 0, 255), 'flate-grus': (120, 200, 230), 'flate-heller': (230, 230, 230), 'flate-asfalt': (60, 60, 60), 'park-punkt': (0, 255, 255), 'fest': (0, 90, 0)}


def flater_i_kartet(etter=True):
    """Bakkeflatene slik kartet tegner dem (med rettelser når etter=True), som (art, punkter, id)."""
    d = datalag.alle(raa=not etter)
    ut = [('brostein', d['brostein'], 'brostein')]
    for g in d['gront']:
        if not g.get('skjul'): ut.append(('plen', g['p'], g.get('id')))
    for g in d.get('gardsrom', []):
        if g.get('skjul'): continue
        if 'gress' in g:   # målt i ortofotoet: kvartalet er belagt, gresset er polygonene
            ut.append(('belagt-gardsrom', g['p'], g.get('id'))); ut += [('gress-gardsrom', q, None) for q in g['gress']]
        else: ut.append(('gress-gardsrom' if g['typ'] == 'gress' else 'belagt-gardsrom', g['p'], g.get('id')))
    for p in d['landskap'].get('fest', []): ut.append(('fest', p, 'fest'))
    for v in d['landskap']['veier']:
        ut.append(('kjorevei' if v['k'] != 'gang' else 'gangvei', [q[:2] for q in v['p']], v.get('w')))
    for f in d.get('flater', []):
        if not f.get('skjul'): ut.append(('flate-' + f['typ'], f['p'], f['id']))
    for p in d.get('parkering', []):
        if p.get('p') and not p.get('skjul'): ut.append(('parkering', p['p'], p['id']))
        else: ut.append(('park-punkt', [[p['x'], p['y']]], p['id']))
    return ut


def ark(etter=False):
    import cv2, numpy as np
    mappe = os.path.join(ROT, 'rapport', 'flater'); os.makedirs(mappe, exist_ok=True)
    fl = flater_i_kartet(etter)
    for navn, x0, y0, x1, y1 in OMRAADER:
        im, px = ortofoto(x0, y0, x1, y1, 0.2)
        lag = im.copy()
        for art, P, ident in fl:
            c = FARGER[art]; Q = np.array([px(*q[:2]) for q in P], np.int32)
            if art in ('kjorevei', 'gangvei'):
                cv2.polylines(lag, [Q], False, c, max(1, int(ident / 0.2 / 3)), cv2.LINE_AA)
            elif art == 'park-punkt':
                cv2.circle(lag, tuple(Q[0]), 7, c, 2, cv2.LINE_AA); cv2.putText(lag, ident.split('-')[-1], tuple(Q[0] + [8, -4]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, c, 1)
            else:
                cv2.polylines(lag, [Q], True, c, 2, cv2.LINE_AA)
                if (art in ('plen', 'gress-gardsrom', 'belagt-gardsrom', 'parkering') or art.startswith('flate')) and ident:
                    m = Q.mean(0).astype(int); cv2.putText(lag, str(ident), tuple(m), cv2.FONT_HERSHEY_SIMPLEX, 0.45, c, 1, cv2.LINE_AA)
        ut = cv2.addWeighted(lag, 0.85, im, 0.15, 0)
        # rutenett hver 20. meter med modellkoordinater, så et avvik kan leses av direkte
        for gx in range(int(math.ceil(x0 / 20) * 20), x1, 20):
            c = int(px(gx, 0)[0]); cv2.line(ut, (c, 0), (c, 12), (255, 255, 255), 1); cv2.putText(ut, str(gx), (c + 2, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        for gy in range(int(math.ceil(y0 / 20) * 20), y1, 20):
            r = int(px(0, gy)[1]); cv2.line(ut, (0, r), (12, r), (255, 255, 255), 1); cv2.putText(ut, str(gy), (14, r + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        y = 18
        for art, c in FARGER.items():
            cv2.putText(ut, art, (ut.shape[1] - 150, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3); cv2.putText(ut, art, (ut.shape[1] - 150, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, c, 1); y += 16
        cv2.putText(ut, f"{navn} {'etter' if etter else 'for'} rettelser  (ortofoto 2024, Fredrikstad kommune, bare kontroll)", (40, ut.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.imwrite(os.path.join(mappe, f"{navn}-{'etter' if etter else 'for'}.jpg"), ut, [cv2.IMWRITE_JPEG_QUALITY, 82])
    print('kontrollark:', mappe)


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    if k == 'hent': hent()
    elif k == 'id': gi_id()
    elif k == 'parkering': parkering()
    elif k == 'maal': maal()
    elif k == 'ark': ark(len(sys.argv) > 2 and sys.argv[2] == 'etter')
    else: print(__doc__)
