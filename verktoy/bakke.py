#!/usr/bin/env python3
"""Bakken i Gamlebyen mot kildene: overflater, gater, gjerder/murer/hekker og trær (29.10).

Fasit:
  - ortofoto 2024 (Fredrikstad kommune, kilder/ortofoto-2024, verktoy/flater.py ortofoto) for det som ses ovenfra: brostein, asfalt,
    grus, gress, bed, vann, og tynne linjer (gjerder, murer, hekker)
  - kommunekartet (kilder/kommunekart/kommunekart.pdf, Vegars nedlasting 29.10, bare lokalt) for arealtypene og eiendomsgrensene:
    gateareal, grønt, vann, åpen mark, og der fotoet ikke ser (trær over, skygge)
  - Kartverkets DOM/DTM 1 m (rapport/hoyder/kilder) for trærne (vegetasjon over 2 m som ikke er hus)

    python3 verktoy/bakke.py klasser      klassekart fra ortofoto + kommunekart (kilder/ortofoto-2024/bakke-klasser.png, ikke i git)
    python3 verktoy/bakke.py overflater   data/flater.json: overflater klassifisert per flate (fl-), id-er beholdes der flaten er den samme
    python3 verktoy/bakke.py innkjorsler  innkjørsler, plasser og oppmerkede felt (kommunekartets gateareal utenfor veibåndene)
    python3 verktoy/bakke.py gater        bredden på landskap.veier målt mot kommunekartets gateareal (rettelser er ikke nødvendig: grunndata)
    python3 verktoy/bakke.py gjerder      data/gjerder.json: gjerder, murer og hekker sett i ortofotoet langs eiendomsgrensene
    python3 verktoy/bakke.py traer        kontroll av trærne mot DOM−DTM og ortofoto; retter posisjon og krone (data/traer.json)
    python3 verktoy/bakke.py ark          kontrollark rapport/bakke/kvartal-NN.png (ortofoto | modellens bakke ovenfra; ikke i git)
"""
import json, math, os, sys
import numpy as np
import cv2

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
import flater as F
import kommunekart as KK

KK_DPI = 600
KK_PNG = os.path.join(ROT, 'kilder', 'kommunekart', f'kommunekart-{KK_DPI}.png')


# ---------- kommunekartet som bilde i modellmeter ----------
def _kk_side():
    if not os.path.exists(KK_PNG) or os.path.getmtime(KK_PNG) < os.path.getmtime(KK.PDF):
        import pymupdf
        pm = pymupdf.open(KK.PDF)[0].get_pixmap(dpi=KK_DPI, alpha=False)
        pm.save(KK_PNG)
    return cv2.imread(KK_PNG)


_KK = None


def kommunekart_bilde(x0, y0, x1, y1, mpp=0.25):
    """Kommunekartet (rendret PDF) resamplet til modellrektangelet, samme rutenett som flater.ortofoto(x0, y0, x1, y1, mpp).
    Utenfor kartrammen: svart (0,0,0)."""
    global _KK
    if _KK is None:
        _KK = _kk_side()
    T = KK._transform()
    W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    X = x0 + (np.arange(W) + 0.5) * mpp; Y = y1 - (np.arange(H) + 0.5) * mpp
    XX, YY = np.meshgrid(X, Y)
    # modell -> PDF: rotasjonen tilbake rundt (cx, cy), så den affine omvendt
    a = math.radians(-T['rot']); c, s = math.cos(a), math.sin(a)
    dx, dy = XX - T['cx'], YY - T['cy']
    xr, yr = T['cx'] + c * dx - s * dy, T['cy'] + s * dx + c * dy
    px = (xr - T['tx']) / T['S']; py = (T['ty'] - yr) / T['S']
    k = KK_DPI / 72.0
    mx, my = (px * k).astype(np.float32), (py * k).astype(np.float32)
    ut = cv2.remap(_KK, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    dek = KK.dekning()
    from shapely.geometry import Polygon
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array([((q[0] - x0) / mpp, (y1 - q[1]) / mpp) for q in dek.exterior.coords], np.int32)], 1)
    ut[m == 0] = 0
    return ut


# ---------- felles rutenett og masker ----------
MPP = 0.25


def domene():
    """Gamlebyen innenfor vollene og vollene selv: festningsflatene (landskap.fest) og brosteinsflaten, i modellmeter."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    d = datalag.alle(raa=True)
    ps = [Polygon(p).buffer(0) for p in d['landskap']['fest']] + [Polygon(d['brostein']).buffer(0)]
    return unary_union(ps).buffer(0)


def ramme(geom, marg=4):
    x0, y0, x1, y1 = geom.bounds
    return (math.floor(x0 - marg), math.floor(y0 - marg), math.ceil(x1 + marg), math.ceil(y1 + marg))


def maske(polys, R, mpp=MPP, hull=True):
    """Polygoner (shapely eller punktlister) -> 0/1-maske i rutenettet R = (x0, y0, x1, y1)."""
    from shapely.geometry import Polygon
    x0, y0, x1, y1 = R
    W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    m = np.zeros((H, W), np.uint8)
    pk = lambda cs: np.array([((q[0] - x0) / mpp, (y1 - q[1]) / mpp) for q in cs], np.int32)
    for P in polys:
        if not hasattr(P, 'geom_type'):
            if len(P) < 3: continue
            cv2.fillPoly(m, [pk(P)], 1); continue
        for g in getattr(P, 'geoms', [P]):
            if g.geom_type != 'Polygon' or g.is_empty: continue
            cv2.fillPoly(m, [pk(g.exterior.coords)], 1)
            if hull:
                for i in g.interiors: cv2.fillPoly(m, [pk(i.coords)], 0)
    return m


def linjemaske(linjer, R, bredde, mpp=MPP):
    x0, y0, x1, y1 = R
    W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    m = np.zeros((H, W), np.uint8)
    for p, b in zip(linjer, bredde if hasattr(bredde, '__len__') else [bredde] * len(linjer)):
        Q = np.array([((q[0] - x0) / mpp, (y1 - q[1]) / mpp) for q in p], np.int32)
        cv2.polylines(m, [Q], False, 1, max(1, int(round(b / mpp))))
    return m


def ndsm(R, mpp=MPP):
    """Kartverkets DOM − DTM (1 m, CC BY 4.0) i rutenettet R. Forskyvningen fra rapport/hoyder (0, −1 m) er lagt på.
    NaN utenfor dekningen."""
    sys.path.insert(0, os.path.join(ROT, 'rapport', 'hoyder'))
    import importlib
    H = importlib.import_module('hent')
    kil = os.path.join(ROT, 'rapport', 'hoyder', 'kilder')
    dom, gt = H.les(os.path.join(kil, 'dom1_25832.tif')); dtm, _ = H.les(os.path.join(kil, 'dtm1_25832.tif'))
    try:
        sh = json.load(open(os.path.join(ROT, 'rapport', 'hoyder', 'tall.json')))['forskyvning']
    except Exception:
        sh = [0.0, -1.0]   # rapport/hoyder/rapport.md: 0,0 m øst, −1,0 m nord
    x0, y0, x1, y1 = R
    W, H_ = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    X = x0 + (np.arange(W) + 0.5) * mpp - sh[0]; Y = y1 - (np.arange(H_) + 0.5) * mpp - sh[1]
    XX, YY = np.meshgrid(X, Y)
    U = H.til_utm(np.stack([XX, YY], -1))
    c = (U[..., 0] - gt[0]) / gt[2] - 0.5; r = (gt[1] - U[..., 1]) / gt[3] - 0.5
    n = dom - dtm
    return cv2.remap(n.astype(np.float32), c.astype(np.float32), r.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=np.nan)


# ---------- ortofotoet klassifisert ----------
# klassekoder (felles for ortofoto, kommunekart og modell)
K = {'ukjent': 0, 'brostein': 1, 'asfalt': 2, 'grus': 3, 'heller': 4, 'gress': 5, 'plen': 6, 'bed': 7, 'vann': 8, 'hus': 9,
     'belagt': 10, 'skygge': 11, 'tre': 12}
NAVN = {v: k for k, v in K.items()}
BELAGT = (1, 2, 3, 4, 10)
GRONT = (5, 6)


def ortofoto_klasser(R, mpp=MPP):
    """Ortofoto 2024 -> klasse per piksel: gress (grønt), bed (bar jord), vann, belagt, skygge. Hus og trær legges på av kallet.
    Gir (klasse, bilde, trekk) der trekk har L, a, b (Lab, 0–255) og tekstur (std av høypass ved 0,125 m)."""
    x0, y0, x1, y1 = R
    im, _ = F.ortofoto(x0, y0, x1, y1, mpp)
    fin, _ = F.ortofoto(x0, y0, x1, y1, 0.125)
    g = cv2.cvtColor(fin, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = g - cv2.GaussianBlur(g, (0, 0), 2)
    tex = np.sqrt(cv2.GaussianBlur(hp * hp, (0, 0), 4))
    tex = cv2.resize(tex, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    kl = np.full(im.shape[:2], K['belagt'], np.uint8)
    hvit = im.min(2) >= 250
    kl[(v < 95) & ~F.gront_maske(im).astype(bool)] = K['skygge']
    jord = (h >= 5) & (h <= 22) & (s >= 55) & (v >= 55) & (v <= 175) & (lab[..., 0] < 165)
    kl[jord] = K['bed']
    kl[F.gront_maske(im).astype(bool)] = K['gress']
    kl[hvit] = K['belagt']
    # vann: mørkt og blått/grønnbrunt i store flater (vannmasken fra verktoy/vann.py når den finnes er bedre; her: kartets vann)
    return kl, im, {'L': lab[..., 0], 'a': lab[..., 1], 'b': lab[..., 2], 'tex': tex}


def glatt(kl, k=3, behold=()):
    """Flertallsfilter (k x k) på klassekartet, så enkeltpiksler og støy forsvinner."""
    ut = kl.copy(); best = np.zeros(kl.shape, np.float32) - 1
    for c in np.unique(kl):
        m = cv2.blur((kl == c).astype(np.float32), (k, k))
        sett = m > best; ut[sett] = c; best[sett] = m[sett]
    for c in behold:
        ut[kl == c] = c
    return ut


# ---------- kommunekartet klassifisert ----------
KK_FARGER = {   # RGB i den rendrede PDF-en (verdiene fra get_drawings, 0–1 x 255)
    'hus': [(156, 156, 156), (179, 179, 179), (209, 209, 209)],
    'gate': [(240, 240, 240), (235, 235, 235), (224, 224, 224), (217, 217, 217), (225, 225, 225)],
    'gront': [(164, 219, 132), (217, 240, 191), (159, 230, 149), (235, 240, 217)],
    'vann': [(217, 250, 255)],
    'aapen': [(250, 247, 235), (250, 250, 250), (255, 255, 255)],
}


def kommunekart_klasser(R, mpp=MPP):
    """Kommunekartets arealtyper per piksel (nærmeste farge): hus, belagt (gateareal), gress (grøntareal), vann, ukjent (åpen/hvit
    mark, tekst og grenser). Gir også eiendomsgrensene (rød) som egen maske."""
    im = kommunekart_bilde(*R, mpp)
    rgb = im[..., ::-1].astype(np.int32)
    kl = np.zeros(im.shape[:2], np.uint8); best = np.full(im.shape[:2], 1e9)
    kode = {'hus': K['hus'], 'gate': K['belagt'], 'gront': K['gress'], 'vann': K['vann'], 'aapen': K['ukjent']}
    for navn, fs in KK_FARGER.items():
        for f in fs:
            d = ((rgb - np.array(f)) ** 2).sum(2)
            sett = (d < best) & (d < 120); kl[sett] = kode[navn]; best[sett] = d[sett]
    rod = (rgb[..., 0] > 180) & (rgb[..., 1] < 110) & (rgb[..., 2] < 110)
    utenfor = im.max(2) == 0
    kl[utenfor] = K['ukjent']
    return kl, rod.astype(np.uint8), ~utenfor


# ---------- fasit for bakken: ortofoto der det ses, kommunekartet der det ikke ses ----------
def hus_polygoner(d=None):
    from shapely.geometry import Polygon
    d = d or datalag.alle()
    ut = []
    for b in d['bygg']:
        if b.get('skjul') or not b.get('p') or len(b['p']) < 3: continue
        P = Polygon(b['p']).buffer(0)
        if not P.is_empty: ut.append(P)
    return ut


def fasit(R, mpp=MPP, d=None):
    """Bakken slik kildene viser den, per piksel i R. Gir dict med:
      kl      klasse (gress, bed, belagt, vann, hus) for hele bakken
      sett    1 der ortofotoet ser bakken (ikke hus, tre, skygge, takutstikk); 0 der kommunekartet eller nabopikslene avgjør
      orto, trekk, kk, rod, ndsm
    Hus = modellens fotavtrykk (kommunens FKB-omriss i Gamlebyen). Vann = data/vann.json (regel 16: 99,4 % mot ortofotoet)."""
    d = d or datalag.alle()
    kl, im, T = ortofoto_klasser(R, mpp)
    kk, rod, kk_inn = kommunekart_klasser(R, mpp)
    n = np.nan_to_num(ndsm(R, mpp), nan=0.0)
    hus = maske(hus_polygoner(d), R, mpp)
    vann = maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp)
    hoyt = (n > 1.5).astype(np.uint8)
    hoyt = cv2.morphologyEx(hoyt, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    # takutstikk og helning i fotoet (ikke ekte ortofoto): 1,25 m rundt hus og alt som står høyt ses ikke som bakke
    r = int(round(1.25 / mpp))
    skjult = cv2.dilate(np.maximum(hus, hoyt), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    sett = (skjult == 0) & (kl != K['skygge']) & (vann == 0)
    ut = np.full(kl.shape, K['ukjent'], np.uint8)
    ut[sett] = kl[sett]
    # det fotoet ikke ser: kommunekartets arealtype der den er gress eller gate
    kkok = (~sett) & np.isin(kk, (K['gress'], K['belagt']))
    ut[kkok] = kk[kkok]
    # resten: nærmeste klasse fotoet ser
    mangler = (ut == K['ukjent'])
    if mangler.any() and (~mangler).any():
        _, lab = cv2.distanceTransformWithLabels(mangler.astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
        kilde = np.zeros(lab.max() + 1, np.uint8)
        yy, xx = np.nonzero(~mangler); kilde[lab[yy, xx]] = ut[yy, xx]
        ut[mangler] = kilde[lab[mangler]]
    ut = glatt(ut, 5)
    ut[vann > 0] = K['vann']; ut[hus > 0] = K['hus']
    return {'kl': ut, 'sett': sett.astype(np.uint8), 'orto': im, 'trekk': T, 'kk': kk, 'rod': rod, 'kk_inn': kk_inn, 'ndsm': n,
            'hus': hus, 'vann': vann}


# kartets farger (src/03, 04, 08, 17), RGB
FARGE_KART = {1: (146, 140, 132), 2: (150, 146, 140), 3: (214, 204, 182), 4: (190, 184, 174), 5: (128, 180, 136), 6: (126, 180, 134),
              7: (132, 108, 86), 8: (150, 212, 224), 10: (160, 157, 152)}


# ---------- modellens bakke ovenfra (samme lag og rekkefølge som src/03, 04, 08, 17) ----------
def terreng(R, mpp=MPP, d=None):
    """Festningsterrenget (landskap.terreng, src/08): (maske, høyde) i rutenettet R."""
    import base64
    d = d or datalag.alle()
    T = d['landskap']['terreng']; nx, ny, G = T['nx'], T['ny'], T['g']
    bits = np.unpackbits(np.frombuffer(base64.b64decode(T['m']), np.uint8))[:nx * ny].astype(bool)
    H = np.full(nx * ny, int(round((T.get('off', 0)) * 20)), np.uint8); hk = np.frombuffer(base64.b64decode(T['h']), np.uint8)
    H[bits] = hk[:bits.sum()]
    hv = H.reshape(ny, nx).astype(np.float32) / 20 - T.get('off', 0); inn = bits.reshape(ny, nx).astype(np.float32)
    x0, y0, x1, y1 = R
    W, Hh = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    X = x0 + (np.arange(W) + 0.5) * mpp; Y = y1 - (np.arange(Hh) + 0.5) * mpp
    XX, YY = np.meshgrid(X, Y)
    fx = ((XX - T['x0']) / G).astype(np.float32); fy = ((YY - T['y0']) / G).astype(np.float32)
    h = cv2.remap(hv, fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    m = cv2.remap(inn, fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) >= 0.5
    return m, h


def modell(R, mpp=MPP, d=None, farge=False):
    """Modellens bakke som klasse per piksel, tegnet i samme rekkefølge (høyde over bakken) som kartet:
    festningsflaten og terrenget (gress) < brostein (0,05) < flater som ikke er gress (0,09 + terreng) < veibånd (0,1) <
    parkering (0,12) < vann (0,15) < plen og gårdsromgress (0,28–0,3) < hus. Veibåndene (src/08) er grå bånd: de får
    flatetypen i landskap.veier[].flate når den finnes, ellers 'belagt'."""
    d = d or datalag.alle()
    x0, y0, x1, y1 = R
    W, H = int(round((x1 - x0) / mpp)), int(round((y1 - y0) / mpp))
    kl = np.zeros((H, W), np.uint8); z = np.full((H, W), -1.0, np.float32)
    rgb = np.zeros((H, W, 3), np.uint8); rgb[:] = (239, 236, 228)
    tm, th = terreng(R, mpp, d)

    def legg(m, hoyde, klasse, farge=None):
        nonlocal kl, z
        if np.isscalar(hoyde): hoyde = np.full(m.shape, hoyde, np.float32)
        s = (m > 0) & (hoyde >= z)
        kl[s] = klasse; z[s] = hoyde[s]; rgb[s] = farge or FARGE_KART.get(klasse, (255, 0, 255))

    legg(maske(d['landskap'].get('fest', []), R, mpp), 0.02, K['gress'])
    legg(tm.astype(np.uint8), th + 0.03, K['gress'])
    legg(maske([d['brostein']], R, mpp), 0.05, K['brostein'])
    for f in d.get('flater', []):
        if f.get('skjul') or f['typ'] == 'gress' or f['typ'] not in K: continue
        legg(maske([f['p']], R, mpp), np.maximum(0.09, th + 0.09), K[f['typ']])
    for v in d['landskap']['veier']:
        mm = linjemaske([[q[:2] for q in v['p']]], R, v['w'], mpp)
        zz = max(q[2] for q in v['p']) + (-0.03 if v['k'] == 'gang' else 0)
        legg(mm, np.maximum(zz, th + 0.0), K.get(v.get('flate'), K['belagt']), (146, 142, 134) if v['k'] == 'gang' else FARGE_KART[1] if v.get('flate') == 'brostein' else (128, 124, 120))
    for p in d.get('parkering', []):
        if p.get('p') and not p.get('skjul') and p.get('flate', 'asfalt') in K:   # parkering i gata (flate «gate») er gata selv
            legg(maske([p['p']], R, mpp), np.maximum(0.12, th + 0.12), K[p.get('flate', 'asfalt')], (160, 157, 152))
    legg(maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp), 0.15, K['vann'])
    for g in d['gront']:
        if not g.get('skjul'): legg(maske([g['p']], R, mpp), 0.28, K['plen'])
    for g in d.get('gardsrom', []):
        if g.get('skjul'): continue
        if 'gress' in g: legg(maske(g['gress'], R, mpp), 0.3, K['plen'])
        elif g['typ'] == 'gress': legg(maske([g['p']], R, mpp), 0.3, K['plen'])
    for f in d.get('flater', []):
        if f.get('skjul') or f['typ'] not in ('gress', 'plen'): continue
        legg(maske([f['p']], R, mpp), np.maximum(0.28, th + 0.28), K[f['typ']])
    for b in d['bygg']:
        if b.get('skjul') or not b.get('p') or len(b['p']) < 3: continue
        m = maske([b['p']], R, mpp) > 0
        kl[m] = K['hus']; rgb[m] = tuple(b.get('tak') or (150, 144, 138))[:3]
    return (kl, rgb) if farge else kl


def gruppe(kl):
    """Klasser -> gruppe for sammenligning: 1 belagt, 2 grønt (gress/plen), 3 bed, 4 vann, 5 hus, 0 ingenting."""
    g = np.zeros(kl.shape, np.uint8)
    g[np.isin(kl, BELAGT)] = 1; g[np.isin(kl, GRONT)] = 2; g[kl == K['bed']] = 3; g[kl == K['vann']] = 4; g[kl == K['hus']] = 5
    return g


def belagt_type(f, mpp=MPP, sigma=1.5):
    """Belagt mark -> brostein, asfalt eller grus, fra fargen og teksturen i sollys (glattet over ca. 2 x sigma m, bare piksler
    fotoet ser og som ikke er skygge). Målt på kjente flater i ortofoto 2024 (verktoy/bakke.py, 29.10):
      brostein (Torvet, gatene): Lab-b 129–133, tekstur 4–14
      asfalt (Rådhusgården, kaia vest): Lab-L 150–205, b under 133,5, tekstur under 3,5 (glatt)
      grus (stiene på vollene, plassen ved Smedjegaten): b 134 og over (gulere), L 165 og over
    Det fotoet ikke ser (skygge, tre), får typen til nærmeste piksel det ser i samme belagte flate."""
    T = f['trekk']; s = ((f['sett'] > 0) & (T['L'] > 150)).astype(np.float32)
    k = int(round(sigma / mpp))
    def snitt(a):
        return cv2.GaussianBlur(a * s, (0, 0), k) / np.maximum(cv2.GaussianBlur(s, (0, 0), k), 1e-3)
    L, b, tx = snitt(T['L']), snitt(T['b']), snitt(T['tex'])
    w = cv2.GaussianBlur(s, (0, 0), k)
    typ = np.full(L.shape, K['brostein'], np.uint8)
    typ[(b >= 134.0) & (L >= 165)] = K['grus']
    typ[(L >= 150) & (L <= 205) & (b < 133.5) & (tx < 3.5)] = K['asfalt']
    ukjent = w < 0.05
    if ukjent.any() and (~ukjent).any():
        _, lab = cv2.distanceTransformWithLabels(ukjent.astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
        kil = np.zeros(lab.max() + 1, np.uint8); yy, xx = np.nonzero(~ukjent); kil[lab[yy, xx]] = typ[yy, xx]
        typ[ukjent] = kil[lab[ukjent]]
    return glatt(typ, 9), s


def belagt_endelig(f, standard, mpp=MPP, min_m2=15.0, min_sett=0.5):
    """Typen på belagt mark med standard der fotoet ikke er sikkert: en flate med annen type enn standarden (brostein i byen,
    grus på vollene) må være minst min_m2 og ses i sollys på minst min_sett av arealet; ellers får den standarden.
    standard: kart med klassekoden per piksel."""
    typ, s = belagt_type(f, mpp)
    bel = f['kl'] == K['belagt']
    ut = standard.copy()
    for c in (K['brostein'], K['asfalt'], K['grus']):
        m = (bel & (typ == c) & (standard != c)).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
        if n <= 1: continue
        sol = np.bincount(lab.ravel(), weights=(s > 0).ravel().astype(float), minlength=n)
        ok = np.zeros(n, bool)
        ok[1:] = (st[1:, 4] * mpp * mpp >= min_m2) & (sol[1:] / np.maximum(st[1:, 4], 1) >= min_sett)
        ut[ok[lab] & (m > 0)] = c
    return ut


# ---------- overflatene i Gamlebyen (data/flater.json) ----------
MAALT = os.path.join(ROT, 'kilder', 'bakke-maalt.json')
GEN_KILDE = 'ortofoto 2024 klassifisert, kommunekartet der fotoet ikke ser (verktoy/bakke.py overflater)'
MIN_M2 = {'gress': 4.0, 'bed': 2.0, 'grus': 6.0, 'asfalt': 10.0, 'brostein': 6.0, 'heller': 6.0}


def maalt():
    """Det som er målt eller dømt for hånd (kilder/bakke-maalt.json): flater med fast type, gater, gjerder og trær."""
    if not os.path.exists(MAALT):
        return {}
    return json.load(open(MAALT, encoding='utf8'))


def bakkekart(d=None, R=None, mpp=MPP):
    """Den endelige typen per piksel i Gamlebyen (domene): fasit (ortofoto/kommunekart), belagt delt i brostein/asfalt/grus,
    og flatene målt for hånd (kilder/bakke-maalt.json «flater») lagt oppå. Gir (kart, f, R)."""
    d = d or datalag.alle(); dom = domene(); R = R or ramme(dom)
    f = fasit(R, mpp, d)
    # grunntypen: brostein i byen (brosteinsflaten) og i kommunekartets gateareal inntil 15 m utenfor den (gatene langs vollene),
    # ellers grus (stiene og plassene på vollene)
    from shapely.geometry import Polygon as _P
    bro = maske([d['brostein']], R, mpp) > 0
    naer = maske([_P(d['brostein']).buffer(15)], R, mpp) > 0
    standard = np.where(bro | (naer & (f['kk'] == K['belagt'])), K['brostein'], K['grus']).astype(np.uint8)
    kl = f['kl'].copy(); t = belagt_endelig(f, standard, mpp); b = kl == K['belagt']; kl[b] = t[b]
    # det som er målt for hånd, går foran: flatene i flater-maalt.json (fl-1 …), parkeringsflatene og kilder/bakke-maalt.json
    faste = [(x['typ'], x['p']) for x in d.get('flater', []) if not x.get('skjul') and not x.get('kilde', '').startswith('ortofoto 2024 klassifisert') and x['typ'] in K]
    faste += [(p.get('flate', 'asfalt'), p['p']) for p in d.get('parkering', []) if p.get('p') and not p.get('skjul') and p.get('flate', 'asfalt') in K]   # «gate»: gata selv
    faste += [(m['typ'], m['p']) for m in maalt().get('flater', [])]
    # gatene dømt i Street View (kilder/bakke-maalt.json «gater»): båndet langs linja
    from shapely.geometry import LineString as _LS
    faste += [(g['typ'], [list(c) for c in _LS(g['linje']).buffer(g['bredde'] / 2, cap_style=2).exterior.coords]) for g in maalt().get('gater', [])]
    for typ, p in faste:
        mm = (maske([p], R, mpp) > 0) & ~np.isin(kl, (K['hus'], K['vann']))
        kl[mm & np.isin(kl, BELAGT + (K['gress'], K['bed']))] = K[typ] if typ != 'gress' else K['gress']
    kl[maske([dom], R, mpp) == 0] = K['ukjent']
    return kl, f, R


def _til_polygoner(m, R, mpp, min_m2, forenkle=0.2):
    """0/1-maske -> shapely-polygoner (med hull) i modellmeter."""
    from shapely.geometry import Polygon
    x0, y0, x1, y1 = R
    cs, hi = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    ut = []
    if hi is None:
        return ut
    hi = hi[0]
    til = lambda c: [(x0 + (q[0][0] + 0.5) * mpp, y1 - (q[0][1] + 0.5) * mpp) for q in c]
    for i, c in enumerate(cs):
        if hi[i][3] != -1 or len(c) < 3: continue
        hull = []; j = hi[i][2]
        while j != -1:
            if len(cs[j]) >= 3 and cv2.contourArea(cs[j]) * mpp * mpp >= 1.0: hull.append(til(cs[j]))
            j = hi[j][0]
        P = Polygon(til(c), hull).buffer(0).simplify(forenkle, preserve_topology=True)
        for g in getattr(P, 'geoms', [P]):
            if g.geom_type == 'Polygon' and g.area >= min_m2: ut.append(g)
    return ut


def uten_hull(P, dybde=0):
    """Kartet tegner flater uten hull (src/17: ShapeGeometry av ytterkanten). En flate med hull deles derfor i biter uten hull,
    med snitt gjennom hullene."""
    from shapely.geometry import LineString, box
    from shapely.ops import split
    if P.geom_type != 'Polygon' or not P.interiors or dybde > 12:
        return [P] if P.geom_type == 'Polygon' else [g for g in getattr(P, 'geoms', []) if g.geom_type == 'Polygon']
    h = P.interiors[0]; cx = h.centroid.x
    x0, y0, x1, y1 = P.bounds
    a = box(x0 - 1, y0 - 1, cx, y1 + 1); b = box(cx, y0 - 1, x1 + 1, y1 + 1)
    ut = []
    for del_ in (P.intersection(a), P.intersection(b)):
        for g in getattr(del_, 'geoms', [del_]):
            if g.geom_type == 'Polygon' and g.area > 0.05: ut += uten_hull(g, dybde + 1)
    return ut


def overflater(skriv=True):
    """data/flater.json: flatene i Gamlebyen etter ortofotoet. Innenfor brosteinsflaten (gatene og gårdsrommene) er brostein
    grunnen; flatene som lages, er det som ikke er brostein: gress (art plen), bed, grus, asfalt. På vollene er gress grunnen
    (terrenget); flatene er det som ikke er gress: grus, asfalt, brostein, bed. Flatene målt for hånd i flater-maalt.json
    (fl-1 …) og parkeringsflatene står foran og klassifiseres ikke på nytt. Id-er: en ny flate som dekker en gammel av samme
    type (IoU >= 0,5), arver id-en; ellers ny fl-<n> (kilder/id-register.txt). Plenene fra OSM (data/gront.json) som ligger i
    Gamlebyen, skjules med grunn: plenene tegnes fra fotoet."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    d = datalag.alle(); dom = domene()
    kl, f, R = bakkekart(d)
    mpp = MPP
    bro = maske([d['brostein']], R, mpp) > 0
    tm, _ = terreng(R, mpp, d)
    fest = (maske(d['landskap'].get('fest', []), R, mpp) > 0) | tm
    gml = [x for x in datalag.les('flater') if not x.get('kilde', '').startswith('ortofoto 2024 klassifisert')]
    eie = maske([x['p'] for x in gml if not x.get('skjul')] + [p['p'] for p in d.get('parkering', []) if p.get('p') and not p.get('skjul')], R, mpp) > 0
    ut = []
    for typ in ('gress', 'bed', 'grus', 'asfalt', 'brostein'):
        c = K['gress'] if typ == 'gress' else K[typ]
        m = (kl == c) if typ != 'gress' else np.isin(kl, GRONT)
        if typ == 'gress': m &= bro | ~fest          # på vollene er terrenget gresset
        if typ == 'brostein': m &= ~bro             # innenfor er brosteinen grunnen
        m &= ~eie
        k = max(1, int(round(0.5 / mpp))) | 1
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        for P in _til_polygoner(m, R, mpp, MIN_M2[typ]):
            P = P.intersection(dom)
            for g in getattr(P, 'geoms', [P]):
                if g.geom_type != 'Polygon' or g.area < MIN_M2[typ]: continue
                for q in uten_hull(g):
                    if q.area >= MIN_M2[typ] * 0.5: ut.append((typ, q))
    # en belagt flate eller et bed som er mest grønt i fotoet (regel 15: under 30 %), er gjettet der fotoet ikke ser
    # (under trær, i skygge): den tas ikke med, grunnen (brostein/terreng) står
    hin = [b_['p'] for b_ in d['bygg'] if b_.get('p') and not b_.get('skjul')]
    beholdt = []; ut_gront = 0
    for typ, q in ut:
        if typ != 'gress':
            pts = [[round(c[0], 2), round(c[1], 2)] for c in q.exterior.coords][:-1]   # som det skrives
            if F.maal_flate(pts, hin)[0] >= 0.25: ut_gront += 1; continue
        beholdt.append((typ, q))
    ut = beholdt
    # id: arv fra forrige kjøring
    gamle = [x for x in datalag.les('flater') if x.get('kilde', '').startswith('ortofoto 2024 klassifisert')]
    gpol = [(x, Polygon(x['p']).buffer(0)) for x in gamle]
    reg_fil = os.path.join(ROT, 'kilder', 'id-register.txt'); reg = [l.strip() for l in open(reg_fil, encoding='utf8') if l.strip()]
    n = max([int(i.split('-')[1]) for i in reg + [x['id'] for x in datalag.les('flater')] if i.startswith('fl-')] + [0])
    brukt, nye_id, liste = set(), [], []
    grunn = {'gress': 'ortofoto 2024: grønt (gress/plen), kommunekartets grøntareal under trær og i skygge',
             'bed': 'ortofoto 2024: bar jord (bed, kjøkkenhage)', 'grus': 'ortofoto 2024: glatt, lys og gul belegning (grus)',
             'asfalt': 'ortofoto 2024: glatt, mellomgrå belegning (asfalt)', 'brostein': 'ortofoto 2024: grå, kornete belegning (brostein/heller) utenfor brosteinsflaten'}
    for typ, q in sorted(ut, key=lambda t: (-t[1].area)):
        best, bi = 0, None
        for x, gp in gpol:
            if x['id'] in brukt or x['typ'] != typ or not gp.intersects(q): continue
            iou = gp.intersection(q).area / gp.union(q).area
            if iou > best: best, bi = iou, x['id']
        if best >= 0.5: fid = bi
        else: n += 1; fid = f'fl-{n}'; nye_id.append(fid)
        brukt.add(fid)
        o = {'id': fid, 'typ': typ}
        if typ == 'gress': o['art'] = 'plen' if bro[int((R[3] - q.representative_point().y) / mpp), int((q.representative_point().x - R[0]) / mpp)] else 'gress'
        o['p'] = [[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]]
        o['m2'] = round(q.area, 1); o['grunn'] = grunn[typ]; o['kilde'] = GEN_KILDE
        liste.append(o)
    liste.sort(key=lambda o: int(o['id'].split('-')[1]))
    tall = {t: (sum(1 for o in liste if o['typ'] == t), round(sum(o['m2'] for o in liste if o['typ'] == t))) for t in MIN_M2}
    print('flater fra ortofotoet:', len(liste), {k: v for k, v in tall.items() if v[0]}, len(nye_id), 'nye id-er;', ut_gront, 'belagte/bed tatt ut (mest grønt i fotoet)')
    if not skriv:
        return liste
    with open(os.path.join(ROT, 'data', 'flater.json'), 'w', encoding='utf8') as fh:
        fh.write('[\n' + ',\n'.join(json.dumps(u, ensure_ascii=False, separators=(',', ':')) for u in gml + liste) + '\n]\n')
    mangler = [o['id'] for o in liste if o['id'] not in reg]
    if mangler:
        open(reg_fil, 'a', encoding='utf8').write('\n'.join(mangler) + '\n')
    # OSM-plenene i Gamlebyen: tegnes nå fra fotoet
    gr = datalag.les('gront'); endret = 0
    for g in gr:
        P = Polygon(g['p']).buffer(0)
        if P.area > 0 and P.intersection(dom).area > 0.5 * P.area and not g.get('skjul'):
            g['skjul'] = 'Claude 2026-10-29: plenene i Gamlebyen tegnes fra ortofoto 2024 (data/flater.json, verktoy/bakke.py overflater)'; endret += 1
    if endret:
        with open(os.path.join(ROT, 'data', 'gront.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in gr) + '\n]\n')
    print(endret, 'OSM-plener i Gamlebyen skjult (tegnes fra fotoet)')
    return liste


# ---------- kontrollark ----------
ARK_MAPPE = os.path.join(ROT, 'rapport', 'bakke')
GJERDE_FARGE = {'gjerde': (40, 40, 220), 'stakitt': (40, 40, 220), 'mur': (0, 140, 255), 'hekk': (0, 120, 0)}


def linjer_i_kartet(d):
    """Gjerder, murer og hekker slik kartet har dem: (type, punkter). data/gjerder.json (liste med punkter, eller objekter med
    p og typ), data/murer.json (OSM) og data/teglmurer.json."""
    ut = []
    for g in d.get('gjerder', []):
        if isinstance(g, dict):
            if not g.get('skjul'): ut.append((g.get('typ', 'gjerde'), g['p']))
        else: ut.append(('gjerde', g))
    for m in d.get('murer', []): ut.append(('mur', m['p']))
    for m in d.get('teglmurer', []):
        if not m.get('skjul'): ut.append(('mur', m['p']))
    return ut


def ark(omraader=None):
    """Kontrollark per område (rapport/bakke/kvartal-NN.png, ikke i git: viser ortofotoet):
    venstre ortofoto 2024 | midten ortofoto med kartets linjer (gjerder rødt, murer oransje, hekker grønt, trekroner gult) |
    høyre modellens bakke ovenfra i kartets farger (lagene og rekkefølgen fra src/), med gjerder og trekroner."""
    os.makedirs(ARK_MAPPE, exist_ok=True)
    d = datalag.alle(); mpp = 0.2
    linjer = linjer_i_kartet(d)
    for nr, (navn, x0, y0, x1, y1) in enumerate(F.OMRAADER, 1):
        if omraader and nr not in omraader: continue
        R = (x0, y0, x1, y1)
        o, px = F.ortofoto(*R, mpp)
        _, rgb = modell(R, mpp, d, farge=True); m = rgb[..., ::-1].copy()
        mid = o.copy()
        P = lambda pts: np.array([px(*q[:2]) for q in pts], np.int32)
        for typ, pts in linjer:
            c = GJERDE_FARGE.get(typ, (40, 40, 220))
            cv2.polylines(mid, [P(pts)], False, c, 2, cv2.LINE_AA)
            cv2.polylines(m, [P(pts)], False, (60, 60, 60) if typ != 'hekk' else (40, 100, 40), 2, cv2.LINE_AA)
        KANT = {'asfalt': (40, 40, 40), 'grus': (60, 150, 200), 'bed': (30, 60, 110), 'brostein': (90, 90, 90), 'gress': (40, 120, 40)}
        for fl in d.get('flater', []):
            if fl.get('skjul') or fl['typ'] not in KANT: continue
            cv2.polylines(m, [P(fl['p'])], True, KANT[fl['typ']], 1, cv2.LINE_AA)
        lag = m.copy()
        for t in d['traer']:
            if x0 - 10 < t[0] < x1 + 10 and y0 - 10 < t[1] < y1 + 10:
                r = (t[2] or 3.5) * 0.95
                c = tuple(int(v) for v in px(t[0], t[1])); rr = int(r / mpp)
                cv2.circle(mid, c, rr, (0, 230, 255), 1, cv2.LINE_AA)
                cv2.circle(lag, c, rr, (98, 146, 92), -1, cv2.LINE_AA)
        m = cv2.addWeighted(lag, 0.55, m, 0.45, 0)
        for im in (o, mid, m):
            for gx in range(int(math.ceil(x0 / 20) * 20), x1, 20):
                c = int(px(gx, 0)[0]); cv2.line(im, (c, 0), (c, 10), (255, 255, 255), 1); cv2.putText(im, str(gx), (c + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            for gy in range(int(math.ceil(y0 / 20) * 20), y1, 20):
                r = int(px(0, gy)[1]); cv2.line(im, (0, r), (10, r), (255, 255, 255), 1); cv2.putText(im, str(gy), (12, r + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        ut = np.hstack([o, np.full((o.shape[0], 6, 3), 255, np.uint8), mid, np.full((o.shape[0], 6, 3), 255, np.uint8), m])
        bunn = np.full((26, ut.shape[1], 3), 32, np.uint8)
        cv2.putText(bunn, f'{nr:02d} {navn}: ortofoto 2024 (Fredrikstad kommune, bare kontroll) | med kartets gjerder (rodt), murer (oransje), hekker (gronnt), trekroner (gult) | modellens bakke ovenfra',
                    (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.imwrite(os.path.join(ARK_MAPPE, f'kvartal-{nr:02d}.png'), np.vstack([ut, bunn]))
    print('kontrollark:', ARK_MAPPE)


# ---------- gatene: bredde og kant ----------
def _straale(kl, ok, R, mpp, x, y, nx, ny, maks=20.0, luke=1.0):
    """Går fra (x, y) i retning (nx, ny) så lenge klassen er i ok (luker på inntil `luke` m tillates). Gir (avstand, stoppet)
    der stoppet = traff noe annet enn ok innenfor maks (en ekte kant), ellers None (åpen plass, utenfor kartet)."""
    x0, y0, x1, y1 = R; H, W = kl.shape
    sist, ute = 0.0, 0.0; t = 0.0; st = mpp * 0.8
    while t < maks:
        t += st
        c = int((x + nx * t - x0) / mpp); r = int((y1 - (y + ny * t)) / mpp)
        if not (0 <= r < H and 0 <= c < W): return None
        if ok[kl[r, c]]: sist = t; ute = 0.0
        else:
            ute += st
            if ute > luke: return sist
    return None


def maal_vei(v, kl, ok, R, mpp, steg=2.0, maks=20.0, luke=1.0, maks_b=18.0):
    """Bredde og forskyvning av kanten for én vei (landskap.veier): stråler vinkelrett ut til begge sider hver `steg` m.
    Gir (median bredde, median forskyvning mot venstre, antall målinger) eller None."""
    P = [q[:2] for q in v['p']]; br, fo = [], []
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < 0.5: continue
        ux, uy = (bx - ax) / L, (by - ay) / L; nx, ny = -uy, ux
        for k in range(int(L // steg) + 1):
            t = min(L, (k + 0.5) * steg)
            x, y = ax + ux * t, ay + uy * t
            vv = _straale(kl, ok, R, mpp, x, y, nx, ny, maks, luke); hh = _straale(kl, ok, R, mpp, x, y, -nx, -ny, maks, luke)
            if vv is None or hh is None or vv + hh < 1.0 or vv + hh > maks_b: continue
            br.append(vv + hh); fo.append((vv - hh) / 2)
    if len(br) < 3: return None
    return float(np.median(br)), float(np.median(fo)), len(br)


def _forskyv(P, fo):
    """Polylinja flyttet fo m mot venstre (normalen i hvert punkt)."""
    Q = []
    for i, q in enumerate(P):
        a = P[max(0, i - 1)]; c = P[min(len(P) - 1, i + 1)]
        dx, dy = c[0] - a[0], c[1] - a[1]; l = math.hypot(dx, dy) or 1
        Q.append([round(q[0] - dy / l * fo, 2), round(q[1] + dx / l * fo, 2)] + list(q[2:]))
    return Q


def gater(skriv=True):
    """Bredden på veibåndene (data/landskap.json «veier», tegnes i src/08) og hvor de står, målt mot kildene:
      kjørevei: kommunekartets gateareal (kanten mot hus, grønt og vann), der kommunekartet dekker; utenfor: ortofotoets belagte mark
      gangvei: ortofotoets belagte mark (grus/brostein/asfalt) mot gress, i bakkekartet
    Veien flyttes sideveis til midten av det målte arealet når den står mer enn 0,5 m skjevt. Flatetypen under båndet
    (flertallet i bakkekartet) skrives i «flate». Det som ikke kan måles (åpne plasser, under trær, utenfor kildene), står som før,
    og «maalt» sier hva som gjelder for hver vei."""
    d = datalag.alle(); L = datalag.les('landskap'); mpp = MPP
    dom = domene(); R = ramme(dom.buffer(40))
    kl, f, _ = bakkekart(d, R, mpp)
    kk = f['kk']; inn = f['kk_inn']
    ok_kk = np.zeros(256, bool); ok_kk[[K['belagt'], K['ukjent']]] = True
    ok_or = np.zeros(256, bool); ok_or[list(BELAGT)] = True
    kkl = kk.copy(); kkl[~inn] = 255   # utenfor kartrammen: stopp (ikke kant)
    tall = {'kjore': [0, 0], 'gang': [0, 0]}; endr = []
    from shapely.geometry import LineString
    for v in L['veier']:
        lin = LineString([q[:2] for q in v['p']])
        if not lin.intersects(dom.buffer(5)): continue
        tall[v['k']][1] += 1
        if v['k'] == 'kjore':
            r = maal_vei(v, kkl, ok_kk, R, mpp, luke=1.2)
            kilde = 'kommunekartets gateareal'
            if r is None:
                r = maal_vei(v, kl, ok_or, R, mpp, luke=0.75); kilde = 'ortofoto 2024 (belagt mark)'
        else:
            r = maal_vei(v, kl, ok_or, R, mpp, maks=8, luke=0.5, maks_b=6.0); kilde = 'ortofoto 2024 (belagt mark mot gress)'
        def flatetype():   # flertallstypen under hele båndet, etter at bredden er satt
            typer = _under_linje(kl, R, mpp, [q[:2] for q in v['p']], max(1.0, v['w']))
            if typer.size: v['flate'] = NAVN[int(np.bincount(typer).argmax())]
        if r is None or r[2] < 5:
            flatetype(); v['maalt'] = 'ikke målt (færre enn 5 målinger: åpen plass, under trær eller utenfor kildene)'; continue
        b, fo, n = r
        b = round(b * 2) / 2
        tall[v['k']][0] += 1
        endr.append((v['w'], b))
        v['w'] = max(1.0, b)
        flytt = abs(fo) > 0.5 and n >= 5 and (abs(fo) < b / 2 or (v['k'] == 'gang' and abs(fo) <= 2.0))   # en sti kan stå ved siden av seg selv
        if flytt: v['p'] = _forskyv(v['p'], fo)
        flatetype()
        v['maalt'] = f'{kilde}: {n} målinger, bredde {b} m' + (f', flyttet {fo:+.1f} m sideveis' if flytt else '')
    # gangveier som ortofotoet viser som gress nesten hele veien (minst 80 % av båndet der fotoet ser bakken), finnes ikke
    # som sti i dag: tas ut og listes (rapport/bakke/veier-fjernet.json)
    gront = np.isin(kl, GRONT); sett_ = f['sett'] > 0; ut_v, beholdt = [], []
    for v in L['veier']:
        if v['k'] == 'gang' and LineString([q[:2] for q in v['p']]).intersects(dom):
            xs = [q[0] for q in v['p']]; ys = [q[1] for q in v['p']]
            mm = linjemaske([[q[:2] for q in v['p']]], R, max(1.0, v['w']), mpp) > 0
            n_ = (mm & sett_).sum()
            if n_ > 40 and (mm & sett_ & gront).sum() / n_ >= 0.8:
                ut_v.append({'p': [q[:2] for q in v['p']], 'w': v['w'], 'grunn': f"ortofoto 2024: {(mm & sett_ & gront).sum() / n_:.0%} av båndet er gress der fotoet ser bakken"}); continue
        beholdt.append(v)
    L['veier'] = beholdt
    os.makedirs(ARK_MAPPE, exist_ok=True)
    json.dump(ut_v, open(os.path.join(ARK_MAPPE, 'veier-fjernet.json'), 'w'), ensure_ascii=False, indent=0)
    print(len(ut_v), 'gangveier tatt ut (gress i fotoet)')
    # en vei der typen skifter (brostein -> grus, asfalt …), deles der den skifter, så båndet tegnes med riktig flate hele veien
    nye, delt = [], 0
    for v in L['veier']:
        if 'maalt' not in v or len(v['p']) < 2: nye.append(v); continue
        biter = del_etter_type(v, kl, R, mpp)
        if len(biter) > 1:   # hver bit får bredden målt for seg (samme kilde som hele veien)
            delt += 1
            for w in biter:
                r = (maal_vei(w, kkl, ok_kk, R, mpp, luke=1.2) or maal_vei(w, kl, ok_or, R, mpp, luke=0.75)) if w['k'] == 'kjore' else maal_vei(w, kl, ok_or, R, mpp, maks=8, luke=0.5, maks_b=6.0)
                if r and r[2] >= 5:
                    w['w'] = max(1.0, round(r[0] * 2) / 2); fo = r[1]
                    fl = abs(fo) > 0.5 and (abs(fo) < w['w'] / 2 or (w['k'] == 'gang' and abs(fo) <= 2.0))
                    if fl: w['p'] = _forskyv(w['p'], fo)
                    w['maalt'] = v['maalt'].split(':')[0] + f': {r[2]} målinger, bredde {w["w"]} m' + (f', flyttet {fo:+.1f} m sideveis' if fl else '') + ' (delt der flatetypen skifter)'
        nye += biter
    L['veier'] = nye
    print('veier i Gamlebyen målt:', {k: f'{a} av {n}' for k, (a, n) in tall.items()}, f'; {delt} delt der flatetypen skifter')
    if endr:
        e = np.array(endr); print(f'bredde før {e[:, 0].mean():.1f} m snitt, etter {e[:, 1].mean():.1f} m; median endring {np.median(np.abs(e[:, 1] - e[:, 0])):.1f} m')
    if skriv:
        json.dump(L, open(os.path.join(ROT, 'data', 'landskap.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    return L


def del_etter_type(v, kl, R, mpp, steg=2.0, min_lengde=8.0):
    """Deler veien v der flatetypen under båndet skifter (flertall i ruter på steg x bredde, løp kortere enn min_lengde slås
    sammen med naboen). Gir liste med veier (samme w, k, b; egen flate)."""
    P = v['p']; seg = []
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); seg.append(L)
    tot = sum(seg)
    if tot < 2 * min_lengde: return [v]
    pos = lambda s_: _punkt_langs(P, seg, s_)
    n = max(2, int(tot // steg)); typer = []
    for i in range(n):
        s0, s1 = i * tot / n, (i + 1) * tot / n
        q0, q1 = pos(s0), pos(s1)
        t = _under_linje(kl, R, mpp, [q0[:2], q1[:2]], max(1.0, v['w']))
        typer.append(int(np.bincount(t).argmax()) if t.size else -1)
    # fyll ukjente med naboen, slå sammen korte løp
    for i in range(n):
        if typer[i] == -1: typer[i] = next((typer[j] for j in list(range(i, -1, -1)) + list(range(i, n)) if typer[j] != -1), K['brostein'])
    min_n = max(1, int(round(min_lengde / (tot / n))))
    endret = True
    while endret:
        endret = False; lop = []; i = 0
        while i < n:
            j = i
            while j < n and typer[j] == typer[i]: j += 1
            lop.append((i, j)); i = j
        for k, (i, j) in enumerate(lop):
            if j - i < min_n and len(lop) > 1:
                nabo = lop[k - 1] if k > 0 else lop[k + 1]
                for q in range(i, j): typer[q] = typer[nabo[0]]
                endret = True; break
    lop = []; i = 0
    while i < n:
        j = i
        while j < n and typer[j] == typer[i]: j += 1
        lop.append((i, j, typer[i])); i = j
    if len(lop) == 1:
        v['flate'] = NAVN[lop[0][2]]; return [v]
    ut = []
    for i, j, t in lop:
        s0, s1 = i * tot / n, j * tot / n
        pts = [pos(s0)] + [q for q, sq in zip(P, np.cumsum([0] + seg)) if s0 < sq < s1] + [pos(s1)]
        w = {**v, 'p': [[round(q[0], 2), round(q[1], 2)] + list(q[2:]) for q in pts], 'flate': NAVN[t]}
        ut.append(w)
    return ut


def _under_linje(kl, R, mpp, pts, bredde):
    """Klassene (bare belagte) under et bånd langs pts, regnet i et lite utsnitt av kartet."""
    x0, y0, x1, y1 = R
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]; m = bredde / 2 + 1
    c0 = max(0, int((min(xs) - m - x0) / mpp)); c1 = min(kl.shape[1], int((max(xs) + m - x0) / mpp) + 1)
    r0 = max(0, int((y1 - max(ys) - m) / mpp)); r1 = min(kl.shape[0], int((y1 - min(ys) + m) / mpp) + 1)
    if c1 <= c0 or r1 <= r0: return np.zeros(0, np.uint8)
    sub = kl[r0:r1, c0:c1]; mm = np.zeros(sub.shape, np.uint8)
    Q = np.array([((q[0] - x0) / mpp - c0, (y1 - q[1]) / mpp - r0) for q in pts], np.int32)
    cv2.polylines(mm, [Q], False, 1, max(1, int(round(bredde / mpp))))
    return sub[(mm > 0) & np.isin(sub, BELAGT)]


def _punkt_langs(P, seg, s_):
    for a, b, L in zip(P, P[1:], seg):
        if s_ <= L or b is P[-1]:
            f_ = 0 if L == 0 else min(1.0, s_ / L)
            return [a[0] + (b[0] - a[0]) * f_, a[1] + (b[1] - a[1]) * f_] + [a[k] + (b[k] - a[k]) * f_ for k in range(2, min(len(a), len(b)))]
        s_ -= L
    return list(P[-1])


# ---------- innkjørsler, plasser og oppmerkede felt (punkt 7) ----------
INN_KILDE = 'kommunekartets gateareal + ortofoto 2024 (verktoy/bakke.py innkjorsler)'


def _oppmerking(R, mpp, m):
    """Hvite oppmerkingsstreker i ortofotoet innenfor masken m (rutenett R, mpp): lyse, smale (under 0,3 m) og rette streker
    over 2 m. Gir liste med linjestykker i modellmeter."""
    x0, y0, x1, y1 = R
    fin, _ = F.ortofoto(x0, y0, x1, y1, 0.125)
    L = cv2.cvtColor(fin, cv2.COLOR_BGR2LAB)[..., 0]
    th = cv2.morphologyEx(L, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    mm = cv2.resize(m.astype(np.uint8), (L.shape[1], L.shape[0]), interpolation=cv2.INTER_NEAREST)
    lys = ((th > 28) & (L > 200) & (mm > 0)).astype(np.uint8) * 255
    seg = cv2.HoughLinesP(lys, 1, np.pi / 180, threshold=12, minLineLength=int(2.0 / 0.125), maxLineGap=3)
    if seg is None: return []
    return [((x0 + (a + .5) * .125, y1 - (b + .5) * .125), (x0 + (c + .5) * .125, y1 - (e + .5) * .125)) for a, b, c, e in seg.reshape(-1, 4)]


def _parkeringsrad(streker):
    """Tre eller flere parallelle streker med 2,2–3,2 m mellomrom er en oppmerket parkeringsrad. Gir antall plasser (0 = ingen)."""
    if len(streker) < 3: return 0
    v = [math.atan2(b[1] - a[1], b[0] - a[0]) % math.pi for a, b in streker]
    best = 0
    for i, vi in enumerate(v):
        gr = [j for j, vj in enumerate(v) if min(abs(vj - vi), math.pi - abs(vj - vi)) < 0.12]
        if len(gr) < 3: continue
        nx, ny = -math.sin(vi), math.cos(vi)
        pos = sorted(((streker[j][0][0] + streker[j][1][0]) / 2 * nx + (streker[j][0][1] + streker[j][1][1]) / 2 * ny) for j in gr)
        sl = [pos[0]]
        for q in pos[1:]:
            if q - sl[-1] > 0.6: sl.append(q)   # samme strek funnet flere ganger
        d = np.diff(sl); ok = ((d > 2.2) & (d < 3.2)).sum()
        best = max(best, int(ok))
    return best if best >= 2 else 0


def innkjorsler(skriv=True):
    """Innkjørsler, plasser og oppmerkede felt: kommunekartets gateareal som ikke dekkes av veibåndene (landskap.veier), husene,
    parkeringsflatene eller flatene målt for hånd, i Gamlebyen. Biter over 6 m² blir flater (art «innkjørsel» når biten er under
    150 m² og ligger inntil et veibånd, ellers «plass»), med typen fra bakkekartet (brostein/asfalt/grus). Hvite oppmerkingsstreker
    i ortofotoet (tre eller flere parallelle med 2,2–3,2 m mellomrom) gir «oppmerket»: antall plasser. Faste id-er fl-<n>."""
    from shapely.geometry import Polygon
    d = datalag.alle(); dom = domene(); R = ramme(dom); mpp = MPP
    kl, f, _ = bakkekart(d, R, mpp)
    gate = (f['kk'] == K['belagt']) & (maske([dom], R, mpp) > 0)
    band = np.zeros(gate.shape, np.uint8)
    for v in d['landskap']['veier']: band |= linjemaske([[q[:2] for q in v['p']]], R, v['w'], mpp)
    husb = cv2.dilate(maske(hus_polygoner(d), R, mpp), np.ones((3, 3), np.uint8))
    andre = [x for x in d.get('flater', []) if INN_KILDE not in x.get('kilde', '') and not x.get('kilde', '').startswith('ortofoto 2024 klassifisert')]
    eie = maske([x['p'] for x in andre if not x.get('skjul')] + [p['p'] for p in d.get('parkering', []) if p.get('p') and not p.get('skjul')], R, mpp)
    rest = gate & (band == 0) & (husb == 0) & (eie == 0)
    k = int(round(0.5 / mpp)) | 1
    rest = cv2.morphologyEx(rest.astype(np.uint8), cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    bandn = cv2.dilate(band, np.ones((5, 5), np.uint8))
    gamle = [(x, Polygon(x['p']).buffer(0)) for x in datalag.les('flater') if INN_KILDE in x.get('kilde', '')]
    reg_fil = os.path.join(ROT, 'kilder', 'id-register.txt'); reg = [l.strip() for l in open(reg_fil, encoding='utf8') if l.strip()]
    n = max([int(i.split('-')[1]) for i in reg + [x['id'] for x in datalag.les('flater')] if i.startswith('fl-')] + [0])
    ut, brukt = [], set()
    for P in _til_polygoner(rest, R, mpp, 6.0, 0.25):
        for q in uten_hull(P):
            if q.area < 6.0: continue
            pts = [[round(a_, 2), round(b_, 2)] for a_, b_ in list(q.exterior.coords)[:-1]]
            if F.maal_flate(pts, [b_['p'] for b_ in d['bygg'] if b_.get('p') and not b_.get('skjul')])[0] >= 0.25: continue   # mest grønt i fotoet
            mm = maske([q], R, mpp) > 0
            t = kl[mm & np.isin(kl, BELAGT)]
            typ = NAVN[int(np.bincount(t).argmax())] if t.size else 'brostein'
            art = 'innkjørsel' if q.area < 150 and (bandn[mm] > 0).any() else 'plass'
            x0_, y0_, x1_, y1_ = q.bounds; RR = (math.floor(x0_) - 1, math.floor(y0_) - 1, math.ceil(x1_) + 1, math.ceil(y1_) + 1)
            antall = _parkeringsrad(_oppmerking(RR, mpp, maske([q], RR, mpp))) if q.area >= 25 else 0
            arv = None
            for x, gp in gamle:
                if x['id'] not in brukt and gp.intersects(q) and gp.intersection(q).area / gp.union(q).area >= 0.5: arv = x['id']; break
            if not arv: n += 1; arv = f'fl-{n}'
            brukt.add(arv)
            o = {'id': arv, 'typ': typ, 'art': art, 'p': [[round(a, 2), round(b, 2)] for a, b in list(q.exterior.coords)[:-1]], 'm2': round(q.area, 1)}
            if antall: o['oppmerket'] = antall
            o['grunn'] = f"kommunekartet: gateareal utenfor veibåndene; ortofoto 2024: {typ}" + (f'; {antall} oppmerkede plasser (hvite streker)' if antall else '')
            o['kilde'] = INN_KILDE
            ut.append(o)
    tall = {a: sum(1 for o in ut if o['art'] == a) for a in ('innkjørsel', 'plass')}
    print(f"{len(ut)} biter gateareal utenfor veibåndene: {tall}, {sum(o['m2'] for o in ut):.0f} m²; oppmerket: {sum(1 for o in ut if o.get('oppmerket'))} "
          f"({sum(o.get('oppmerket', 0) for o in ut)} plasser)")
    if skriv:
        alle = [x for x in datalag.les('flater') if INN_KILDE not in x.get('kilde', '')] + ut
        with open(os.path.join(ROT, 'data', 'flater.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(u, ensure_ascii=False, separators=(',', ':')) for u in alle) + '\n]\n')
        mangler = [o['id'] for o in ut if o['id'] not in reg]
        if mangler: open(reg_fil, 'a', encoding='utf8').write('\n'.join(mangler) + '\n')
    return ut


# ---------- gjerder, murer og hekker ----------
def _strimmel(bilde, R, mpp, a, b, bredde=3.0, steg=0.125, ds=0.25):
    """Bildet samplet i en strimmel langs linjestykket a–b: rader langs linja (hver ds m), kolonner på tvers (−bredde … +bredde,
    hver steg m; positiv = venstre for a->b). Gir (strimmel, t-aksen)."""
    x0, y0, x1, y1 = R
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy, ux
    s_ = np.arange(ds / 2, L, ds); t = np.arange(-bredde, bredde + 1e-6, steg)
    SS, TT = np.meshgrid(s_, t, indexing='ij')
    X = a[0] + ux * SS + nx * TT; Y = a[1] + uy * SS + ny * TT
    c = ((X - x0) / mpp - 0.5).astype(np.float32); r = ((y1 - Y) / mpp - 0.5).astype(np.float32)
    return cv2.remap(bilde.astype(np.float32), c, r, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=np.nan), t


def _kandidater(d, R, mpp, f, dom):
    """Linjestykker der det kan stå gjerde, mur eller hekk: eiendomsgrensene i kommunekartet (rød) og kantene på gårdsrommene.
    Biter innen 2,5 m fra en husvegg (veggen, takutstikket og helningen i fotoet) og inne i kommunekartets gateareal tas bort."""
    from shapely.geometry import LineString, MultiLineString, Polygon
    from shapely.ops import unary_union, linemerge
    from skimage.morphology import skeletonize
    rod = f['rod'] & (maske([dom.buffer(5)], R, mpp) > 0)
    rod = cv2.morphologyEx(rod.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))   # de stiplede grensene
    sk = skeletonize(rod > 0).astype(np.uint8) * 255
    seg = cv2.HoughLinesP(sk, 1, np.pi / 180, threshold=10, minLineLength=int(2.5 / mpp), maxLineGap=int(1.5 / mpp))
    x0, y0, x1, y1 = R
    til = lambda c, r: (x0 + (c + 0.5) * mpp, y1 - (r + 0.5) * mpp)
    linjer = []
    if seg is not None:
        for q in seg.reshape(-1, 4):
            linjer.append(('eiendomsgrense', LineString([til(q[0], q[1]), til(q[2], q[3])])))
    for g in d.get('gardsrom', []):
        if g.get('skjul') or len(g['p']) < 3: continue
        P = g['p'] + [g['p'][0]]
        for a, b in zip(P, P[1:]): linjer.append(('gårdsrom', LineString([a, b])))
    # husveggen med takutstikket og helningen i fotoet (ikke ekte ortofoto): 2,5 m; gatearealet i kommunekartet har ikke gjerder
    husv = unary_union([P.buffer(2.5) for P in hus_polygoner(d)])
    gate = _til_polygoner((f['kk'] == K['belagt']).astype(np.uint8), R, mpp, 20.0, 0.5)
    if gate: husv = husv.union(unary_union([g.buffer(-0.75) for g in gate]))
    ut = []
    for kilde, l in linjer:
        if l.length < 1.5: continue
        r = l.difference(husv).intersection(dom.buffer(2))
        for g in getattr(r, 'geoms', [r]):
            if g.geom_type == 'LineString' and g.length >= 2.0:
                ut.append((kilde, list(g.coords)[0], list(g.coords)[-1]))
    return ut


def _sider_sett(sett, R, mpp, a, b, t0):
    """Andelen av sidene (0,5–1,5 m ut fra linja i t0) som fotoet ser i sol (ikke skygge, hus eller tre)."""
    Sv, t = _strimmel(sett.astype(np.float32), R, mpp, a, b)
    side = (np.abs(t - t0) >= 0.5) & (np.abs(t - t0) <= 1.5)
    return float(np.nanmean(Sv[:, side])) if side.any() else 0.0


def vurder_linje(a, b, L, gr, nd, R, mpp, sok=1.5, sett=None):
    """Ser etter gjerde, mur eller hekk langs a–b i ortofotoet (L = lyshet, gr = grønt) og DOM−DTM (nd), med linja forskjøvet
    inntil ±sok m på tvers (eiendomsgrensene i kommunekartet er rastret på ca. 1 m). Gir dict med type, forskyvning, andel av
    lengden der linja ses, mørk stripe (skyggen/gjerdet), grønn stripe og høyde, eller None."""
    A, t = _strimmel(L, R, mpp, a, b); G, _ = _strimmel(gr, R, mpp, a, b); N, _ = _strimmel(nd, R, mpp, a, b, steg=0.25)
    if A.shape[0] < 6 or np.isnan(A).mean() > 0.3: return None
    A = np.nan_to_num(A, nan=np.nanmean(A)); G = np.nan_to_num(G, nan=0)
    As = cv2.GaussianBlur(A, (1, 3), 0)
    m = As.mean(0)
    # mørk smal stripe: lyshet midt på mot 0,5–1,5 m til begge sider
    k1, k2 = int(0.5 / 0.125), int(1.5 / 0.125)
    dip = np.full(len(t), -1e9)
    for i in range(k2, len(t) - k2):
        sider = min(m[i - k2:i - k1 + 1].mean(), m[i + k1:i + k2 + 1].mean())
        dip[i] = sider - m[i]
    inn = np.abs(t) <= sok
    i = int(np.argmax(np.where(inn, dip, -1e9)))
    # per rad: ses stripen der?
    rad = np.array([min(As[j, i - k2:i - k1 + 1].mean(), As[j, i + k1:i + k2 + 1].mean()) - As[j, max(0, i - 1):i + 2].min() for j in range(As.shape[0])])
    andel_mork = float((rad > 14).mean())
    # grønn stripe (hekk): grønt i ±0,6 m rundt beste grønne forskyvning, lite grønt 1,5–2,5 m ut på minst én side
    gm = G.mean(0); gb = np.convolve(gm, np.ones(9) / 9, 'same')
    ig = int(np.argmax(np.where(inn, gb, -1)))
    # en hekk står fritt: mindre grønt på begge sider (en plenkant har grønt på den ene siden og er ikke hekk)
    sideg = max(gm[max(0, ig - 20):max(1, ig - 12)].mean() if ig > 12 else 1, gm[ig + 12:ig + 20].mean() if ig + 20 < len(gm) else 1)
    andel_gronn = float((G[:, max(0, ig - 4):ig + 5].mean(1) > 0.5).mean())
    tn = np.arange(-3.0, 3.0 + 1e-6, 0.25)
    def hoyde(tt):
        j = int(np.argmin(np.abs(tn - tt))); v = N[:, max(0, j - 2):j + 3]
        return float(np.nanmedian(np.nanmax(v, 1))) if np.isfinite(v).any() else 0.0
    ut = {'mork': float(dip[i]), 'andel_mork': andel_mork, 'gronn': float(gb[ig]), 'sideg': float(sideg), 'andel_gronn': andel_gronn}
    if andel_gronn >= 0.6 and gb[ig] - sideg >= 0.35 and hoyde(t[ig]) >= 0.4:
        h = hoyde(t[ig]); return {**ut, 'typ': 'hekk', 'fo': float(t[ig]), 'andel': andel_gronn, 'h': round(min(max(h, 0.8), 3.5), 1)}
    if dip[i] >= 14 and andel_mork >= 0.6 and (sett is None or _sider_sett(sett, R, mpp, a, b, t[i]) >= 0.7):
        h = hoyde(t[i])
        typ = 'mur' if h >= 0.9 else 'gjerde'
        return {**ut, 'typ': typ, 'fo': float(t[i]), 'andel': andel_mork, 'h': round(min(max(h, 1.0), 3.0), 1) if typ == 'mur' else 1.2}
    return None


def gjerder(skriv=True):
    """data/gjerder.json: gjerder, murer og hekker i Gamlebyen, sett i ortofoto 2024 langs eiendomsgrensene (kommunekartet),
    gårdsrommene og linjene kartet hadde. Hvert stykke er funnet i fotoet (mørk smal stripe = gjerdet og skyggen, eller grønn
    stripe = hekk) på minst 60 % av lengden; DOM−DTM avgjør mur (over 0,9 m) mot gjerde. Stykker som ikke ses, tas ikke med;
    linjene kartet hadde som ikke ses i fotoet, står i rapport/bakke/gjerder-forkastet.json. Murene fra OSM (data/murer.json) og
    teglmurene (data/teglmurer.json) røres ikke. Faste id-er gj-<n> (arves når et nytt stykke ligger på et gammelt)."""
    from shapely.geometry import LineString
    d = datalag.alle(); dom = domene(); R = ramme(dom); mpp = MPP
    f = fasit(R, mpp, d)
    L = f['trekk']['L']; gr = F.gront_maske(f['orto']).astype(np.float32); nd = f['ndsm']
    kand = _kandidater(d, R, mpp, f, dom)
    funnet = []
    # gjerdene kartet hadde før (gårdsromkantene, 29.10): de som ikke ses i fotoet nå, listes
    from shapely.ops import unary_union as _uu
    for kilde, a, b in kand:
        r = vurder_linje(a, b, L, gr, nd, R, mpp, sett=f['sett'])
        if r is None: continue
        lx, ly = b[0] - a[0], b[1] - a[1]; ll = math.hypot(lx, ly); nx, ny = -ly / ll, lx / ll
        fo = r['fo']
        p = [[round(a[0] + nx * fo, 2), round(a[1] + ny * fo, 2)], [round(b[0] + nx * fo, 2), round(b[1] + ny * fo, 2)]]
        funnet.append({'typ': r['typ'], 'p': p, 'h': r['h'], 'andel': round(r['andel'], 2), 'kilde_linje': kilde})
    # dubletter (samme linje fra flere kandidater): behold den lengste/sikreste
    funnet.sort(key=lambda g: -(math.dist(*g['p']) * g['andel']))
    valgt = []
    for g in funnet:
        l = LineString(g['p'])
        if any(l.buffer(0.6).intersection(LineString(v['p'])).length > 0.5 * min(l.length, LineString(v['p']).length) for v in valgt): continue
        valgt.append(g)
    for g in valgt: g.setdefault('art', g['typ'])
    # Street View-avlesningen: utsagnet bestemmer typen der fotoet har funnet linja; ellers legges linja til
    from shapely.geometry import Polygon as _Pg
    from shapely.ops import unary_union as _uu2
    husu = _uu2([P.buffer(0.2) for P in hus_polygoner(d)])
    sv, sv_hopp = gjerder_streetview(d, R, mpp, f)
    n_sv = n_sv_type = 0
    for g in sorted(sv, key=lambda g: -math.dist(*g['p'])):
        l = LineString(g['p']).difference(husu)
        if l.is_empty: continue
        l = max(getattr(l, 'geoms', [l]), key=lambda q: q.length)
        if l.length < 1.0: continue
        g['p'] = [[round(x, 2), round(y, 2)] for x, y in l.coords]
        lik = next((v for v in valgt if l.buffer(1.0).intersection(LineString(v['p'])).length > 0.5 * min(l.length, LineString(v['p']).length)), None)
        if lik is not None:
            if 'sv' not in lik:
                lik.update(typ=g['typ'], art=g['art'], h=g['h'], sv=g['grunn']); n_sv_type += 1
            continue
        g['andel'] = 1.0; g['kilde_linje'] = 'Street View'; valgt.append(g); n_sv += 1
    # tegningen: åpningene langs gata som er tegnet lukket (mur, plankegjerde, port). AV (29.10): med registreringen modell -> trykk
    # på 5–25 px (2–8 m) treffer murflaten i en 3–15 m åpning tak og husflater i stedet for muren; prøven på 40 åpninger ga 1 over
    # 0,5 etter at tak og store husflater var tatt ut. Slås på (TEGNING_GJERDER=1) når tegningene er registrert per kvartal.
    if os.environ.get('TEGNING_GJERDER') == '1':
      try:
        finnes = _uu2([LineString(v['p']).buffer(0.5) for v in valgt]) if valgt else None
        for g in gjerder_tegning(d, f, R, mpp, finnes):
            g['andel'] = 1.0; g['kilde_linje'] = 'tegningen'; valgt.append(g)
      except FileNotFoundError as e:
        print('tegningen mangler lokalt (kilder/ai):', e)
    # målt for hånd (kilder/bakke-maalt.json «gjerder»)
    for g in maalt().get('gjerder', []):
        valgt.append({'typ': g['typ'], 'art': g.get('art', g['typ']), 'p': g['p'], 'h': g.get('h', 1.5), 'grunn': g['grunn'], 'andel': 1.0, 'kilde_linje': 'hånd'})
    print(f'Street View: {len(sv)} stykker fra avlesningen, {n_sv} nye, {n_sv_type} ga typen til en linje fotoet fant; {len(sv_hopp)} utsagn hoppet over')
    gamle = [x for x in datalag.les('gjerder') if isinstance(x, dict) and x.get('id')]
    reg_fil = os.path.join(ROT, 'kilder', 'id-register.txt'); reg = [l.strip() for l in open(reg_fil, encoding='utf8') if l.strip()]
    n = max([int(i.split('-')[1]) for i in reg + [x['id'] for x in gamle] if i.startswith('gj-')] + [0]); nye = []; brukt = set()
    for g in valgt:
        l = LineString(g['p']); arv = None
        for x in gamle:
            if x['id'] not in brukt and x['typ'] == g['typ'] and l.buffer(0.5).intersection(LineString(x['p'])).length > 0.6 * l.length:
                arv = x['id']; break
        if not arv: n += 1; arv = f'gj-{n}'; nye.append(arv)
        brukt.add(arv); g['id'] = arv
        if 'grunn' not in g:
            g['grunn'] = (f"ortofoto 2024: {'grønn stripe' if g['typ'] == 'hekk' else 'mørk smal stripe (gjerdet og skyggen)'} på {g['andel']:.0%} av lengden"
                          + (f"; DOM−DTM {g['h']} m" if g['typ'] in ('mur', 'hekk') else '') + f"; langs {g['kilde_linje']}"
                          + (f"; typen fra {g['sv']}" if g.get('sv') else ''))
        g['kilde'] = {'Street View': 'Street View-avlesningen (verktoy/bakke.py gjerder)', 'tegningen': 'tegningen 2017 (Gamlebyen+Isegran2017.ai) registrert mot modellen (verktoy/bakke.py gjerder)', 'hånd': 'målt for hånd, kilder/bakke-maalt.json (verktoy/bakke.py gjerder)'}.get(
            g['kilde_linje'], 'ortofoto 2024 + kommunekartets eiendomsgrenser + Kartverket DOM−DTM (verktoy/bakke.py gjerder)')
    valgt = [{k: g[k] for k in ('id', 'typ', 'art', 'p', 'h', 'grunn', 'kilde') if k in g} for g in sorted(valgt, key=lambda g: int(g['id'].split('-')[1]))]
    ny = _uu([LineString(g['p']).buffer(1.0) for g in valgt]) if valgt else None
    forkastet = []
    for g in d.get('gardsrom', []):   # gjerdene kartet hadde før 29.10, var gårdsromkantene
        if g.get('skjul') or len(g['p']) < 3: continue
        p = g['p'] + [g['p'][0]]; l = LineString(p)
        if ny is None or l.intersection(ny).length < 0.5 * l.length: forkastet.append({'p': p, 'lengde': round(l.length, 1)})
    tall = {t: (sum(1 for g in valgt if g['typ'] == t), round(sum(LineString(g['p']).length for g in valgt if g['typ'] == t))) for t in ('gjerde', 'mur', 'hekk')}
    print(f'{len(kand)} kandidatstykker; {len(valgt)} gjerder/murer/hekker i kartet (foto, Street View, hånd):', tall, f'; {len(forkastet)} av kartets gjerder fra før (gårdsromkantene) ses ikke og er tatt ut')
    if skriv:
        with open(os.path.join(ROT, 'data', 'gjerder.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(g, ensure_ascii=False, separators=(',', ':')) for g in valgt) + '\n]\n')
        mangler = [g['id'] for g in valgt if g['id'] not in reg]
        if mangler: open(reg_fil, 'a', encoding='utf8').write('\n'.join(mangler) + '\n')
        os.makedirs(ARK_MAPPE, exist_ok=True)
        json.dump(forkastet, open(os.path.join(ARK_MAPPE, 'gjerder-forkastet.json'), 'w'), indent=0)
    return valgt


# ---------- gjerder fra Street View-avlesningen og fra hånd ----------
SV_FIL = os.environ.get('SV_AVLESNING', os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json'))
_KOMPASS = {'N': 0, 'NØ': 45, 'Ø': 90, 'SØ': 135, 'S': 180, 'SV': 225, 'V': 270, 'NV': 315}
_ART = [  # (mønster, typ, art, høyde)
    (r'hekk', 'hekk', 'hekk', 1.5), (r'portmur|natursteinportal|steinmur|gråsteinsmur|natursteinsmur|hvit mur', 'mur', 'mur', 2.2),
    (r'plankeport', 'gjerde', 'plankeport', 2.2), (r'plankegjerde|tregjerde|plankevegg', 'gjerde', 'plankegjerde', 1.9),
    (r'stakitt', 'gjerde', 'stakitt', 1.0), (r'smijern', 'gjerde', 'smijern', 1.2), (r'netting', 'gjerde', 'netting', 1.2),
    (r'kjetting', 'gjerde', 'kjetting', 0.6), (r'rekkverk', 'gjerde', 'rekkverk', 1.0), (r'\bgjerde\b', 'gjerde', 'gjerde', 1.2)]
_IKKE = r'nabo|bygg med|gård med|portbygg|vollmur|motsatt side|markise|benk|busk'


def sv_utsagn():
    """Gjerde-, mur- og hekkutsagnene i Street View-avlesningen: (bygg-id, typ, art, h, side, retning, kamera, heading, tekst).
    side: V (til venstre sett fra kameraet), H (til høyre), F (foran fasaden / langs gata / rundt hagen)."""
    import re
    if not os.path.exists(SV_FIL): return []
    a = json.load(open(SV_FIL, encoding='utf8')); ut = []
    def kam(u):
        if not u: return None, None
        m = re.search(r'viewpoint=([\d.]+),([\d.]+)', u) or re.match(r'([\d.]+),([\d.]+)', u)
        h = re.search(r'heading=([\d.]+)', u) or re.search(r'h([\d.]+)', u)
        return (datalag.til_modell(float(m.group(2)), float(m.group(1))) if m else None), (float(h.group(1)) if h else None)
    for k, v in a.items():
        kilder = [(v.get('gjerde_mur'), None, v.get('pano_url'))] + [(sd.get('gjerde_mur_foran'), sd.get('retning'), sd.get('pano_url')) for sd in v.get('sider', [])]
        for tekst, retning, url in kilder:
            if not tekst or re.match(r'^\s*(nei|ingen)', tekst.lower()): continue
            for ledd in re.split(r'[;,]', tekst):
                l = ledd.lower().strip()
                if not l or re.search(_IKKE, l): continue
                treff = next(((t, art, h) for mo, t, art, h in _ART if re.search(mo, l)), None)
                if not treff: continue
                side = 'V' if 'venstre' in l else 'H' if 'høyre' in l else 'VH' if ('begge' in l or 'mellom' in l and 'hagene' not in l) else 'F'
                if 'mellom hagene' in l: continue
                t, art, h = treff
                if art == 'hekk' and 'høy' in l: h = 2.0
                if art == 'plankegjerde' and 'høyt' in l: h = 2.2
                if art == 'stakitt' and 'på steinmur' in l: h = 1.4
                rd = None
                if retning:
                    m = re.match(r'\s*([NSØV]{1,2})\b', retning)
                    if m and m.group(1) in _KOMPASS: rd = _KOMPASS[m.group(1)]
                p_, hd = kam(url)
                ut.append((k, t, art, h, side, rd, p_, hd, ledd.strip()))
    return ut


def _sett_vegg(P, retning, kamera, heading):
    """Veggen (kant i omrisset) som vender mot retningen (kompass, grader) eller mot kameraet. Gir (a, b, n) med a til venstre og
    b til høyre sett fra gata (utenfra), n = normal ut, eller None."""
    pts = list(P.exterior.coords)[:-1]
    if P.exterior.is_ccw is False: pts = pts[::-1]   # mot klokka: normalen ut er (dy, -dx)
    best = None
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 2.0: continue
        n = ((b[1] - a[1]) / L, -(b[0] - a[0]) / L)
        if retning is not None:
            mal = (math.sin(math.radians(retning)), math.cos(math.radians(retning)))
        elif kamera is not None:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; dx, dy = kamera[0] - mx, kamera[1] - my; l = math.hypot(dx, dy) or 1
            mal = (dx / l, dy / l)
        else: return None
        c = n[0] * mal[0] + n[1] * mal[1]
        if c < math.cos(math.radians(50)): continue
        sk = c * min(L, 15)
        if best is None or sk > best[0]: best = (sk, a, b, n)
    if not best: return None
    _, a, b, n = best
    # sett utenfra (mot normalen): venstre ende er den med normalen dreid mot klokka … (a, b) går med klokka sett utenfra = venstre -> høyre
    return (b, a, n)


def _luke(start, retn, hus, maks=15.0):
    """Fra start i retning retn langs husrekka: avstanden til neste hus (fasadelinja), eller None innen maks."""
    from shapely.geometry import LineString
    l = LineString([start, (start[0] + retn[0] * maks, start[1] + retn[1] * maks)])
    best = None
    for P in hus:
        if P.distance(l) > 0.01: continue
        x = l.intersection(P.buffer(0.05))
        if x.is_empty: continue
        dd = min(math.hypot(q[0] - start[0], q[1] - start[1]) for g in getattr(x, 'geoms', [x]) for q in (g.coords if hasattr(g, 'coords') else g.exterior.coords))
        if dd > 0.3 and (best is None or dd < best): best = dd
    return best


def gjerder_streetview(d, R, mpp, f):
    """Gjerder, murer og hekker fra Street View-avlesningen (296 hus): hvert utsagn plasseres ved huset det står ved:
      til venstre / høyre (sett fra gata): i åpningen fra husets hjørne langs fasadelinja til neste hus (1–15 m); uten nabohus
      innen 15 m: 4 m (antatt lengde, står i grunnen)
      foran / langs gata / rundt hagen: parallelt med fasaden ved gatekanten (kommunekartets gateareal), når huset står minst 1,5 m
      inn fra gata; ellers foran åpningene på begge sider
    Gir liste med {typ, art, p, h, grunn}."""
    from shapely.geometry import Polygon
    hus = {b['id']: Polygon(b['p']).buffer(0) for b in d['bygg'] if b.get('p') and not b.get('skjul') and len(b['p']) >= 3}
    alle = list(hus.values())
    gate = f['kk'] == K['belagt']
    def til_gata(q, n):
        for t_ in np.arange(0.5, 20, 0.25):
            x, y = q[0] + n[0] * t_, q[1] + n[1] * t_
            r, c = int((R[3] - y) / mpp), int((x - R[0]) / mpp)
            if not (0 <= r < gate.shape[0] and 0 <= c < gate.shape[1]): return None
            if gate[r, c]: return t_
        return None
    ut, hopp = [], []
    for k, typ, art, h, side, rd, kam, hd, tekst in sv_utsagn():
        P = hus.get(k)
        if P is None or P.geom_type != 'Polygon': hopp.append((k, tekst, 'huset finnes ikke')); continue
        v = _sett_vegg(P, rd, kam, hd)
        if not v: hopp.append((k, tekst, 'fant ikke veggen mot gata')); continue
        a, b, n = v; L = math.hypot(b[0] - a[0], b[1] - a[1]); u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        andre = [Q for kk, Q in hus.items() if kk != k]
        biter = []
        sider = side if side != 'F' else ''
        if side == 'F':
            sb = til_gata(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), n)
            if sb is not None and sb >= 1.5:
                o = sb - 0.3; biter.append(([(a[0] + n[0] * o, a[1] + n[1] * o), (b[0] + n[0] * o, b[1] + n[1] * o)], f'foran fasaden, {o:.1f} m ut ved gatekanten'))
            else: sider = 'VH'
        for sd in sider:
            start, retn = (a, (-u[0], -u[1])) if sd == 'V' else (b, u)
            ll = _luke(start, retn, andre)
            antatt = ll is None
            ll = 4.0 if antatt else ll
            if ll < 1.0: continue
            # åpningen må ikke være en gate (kommunekartets gateareal): da står nabohuset på andre siden av en tverrgate
            sm = [(start[0] + retn[0] * t_, start[1] + retn[1] * t_) for t_ in np.arange(0.25, ll, 0.25)]
            ig = [gate[int((R[3] - y) / mpp), int((x - R[0]) / mpp)] for x, y in sm if 0 <= int((R[3] - y) / mpp) < gate.shape[0] and 0 <= int((x - R[0]) / mpp) < gate.shape[1]]
            if ig and np.mean(ig) > 0.3: continue
            biter.append(([tuple(start), (start[0] + retn[0] * ll, start[1] + retn[1] * ll)], ('til venstre' if sd == 'V' else 'til høyre') +
                          (f' i åpningen til nabohuset ({ll:.1f} m)' if not antatt else ' (ikke nabohus innen 15 m: 4 m antatt lengde)')))
        for pts, hvor in biter:
            ut.append({'typ': typ, 'art': art, 'p': [[round(x, 2), round(y, 2)] for x, y in pts], 'h': h, 'bygg_id': k,
                       'grunn': f'Street View: «{tekst}» ved {k}, {hvor}'})
    return ut, hopp


# ---------- gjerder og murer i tegningen (2017-tegningen = 2019-trykket) ----------
def _tegning():
    """Etikettbildet av tegningens hus- og murflater i 2019-trykkets piksler (x2) og fargene (verktoy/farger_tegning.py)."""
    import farger_tegning as FT
    fl = FT.hus_flater(); jp, lab = FT.etikett(fl)
    return FT, fl, lab


def aapninger(d, f, R, mpp):
    """Åpningene langs gata mellom to hus i Gamlebyen (1,5–15 m): fra hjørnet av en gatevegg langs fasadelinja til nabohuset.
    Gatevegg = vegg der kommunekartets gateareal ligger innen 3 m rett ut. Gir liste med (a, b, hus_a, hus_b)."""
    from shapely.geometry import Polygon, LineString
    hus = [(b['id'], Polygon(b['p']).buffer(0), b) for b in d['bygg'] if b.get('p') and not b.get('skjul') and b.get('gml') and len(b['p']) >= 3]
    alle = [(i, P) for i, P, _ in hus]
    gate = f['kk'] == K['belagt']
    def gate_ut(q, n):
        for t_ in np.arange(0.4, 3.0, 0.2):
            r, c = int((R[3] - q[1] - n[1] * t_) / mpp), int((q[0] + n[0] * t_ - R[0]) / mpp)
            if 0 <= r < gate.shape[0] and 0 <= c < gate.shape[1] and gate[r, c]: return True
        return False
    ut = []
    for hid, P, b in hus:
        if P.geom_type != 'Polygon': continue
        pts = list(P.exterior.coords)[:-1]
        if not P.exterior.is_ccw: pts = pts[::-1]
        for i in range(len(pts)):
            a, c = pts[i], pts[(i + 1) % len(pts)]; L = math.hypot(c[0] - a[0], c[1] - a[1])
            if L < 2: continue
            u = ((c[0] - a[0]) / L, (c[1] - a[1]) / L); n = (u[1], -u[0])
            if not gate_ut(((a[0] + c[0]) / 2, (a[1] + c[1]) / 2), n): continue
            for start, retn in ((a, (-u[0], -u[1])), (c, u)):
                andre = [Q for j, Q in alle if j != hid]
                ll = _luke(start, retn, andre)
                if ll is None or not (1.5 <= ll <= 15): continue
                e = (start[0] + retn[0] * ll, start[1] + retn[1] * ll)
                nabo = next((j for j, Q in alle if j != hid and Q.distance(_Pt(e)) < 0.3), None)
                ut.append((start, e, hid, nabo))
    # samme åpning fra begge husene: behold én
    rene = []
    for a, e, h1, h2 in ut:
        l = LineString([a, e])
        if any(l.buffer(0.8).contains(LineString([q[0], q[1]])) or LineString([q[0], q[1]]).buffer(0.8).contains(l) for q in rene): continue
        rene.append((a, e, h1, h2))
    return rene


def _Pt(q):
    from shapely.geometry import Point
    return Point(q)


def vurder_aapning_i_tegningen(a, e, husene, d, FT, fl, lab, H_MUR=2.0, S=2):
    """Er åpningen a–e tegnet lukket (mur, plankegjerde, port) i tegningen? Husene på begge sider registreres lokalt mot tegningen
    (flytt ±36 px til flest punkter av taket lander på husflater, som farger_tegning.py), så projiseres muren (h 0–2 m) med samme
    flytt. Gir (andel av murflaten som er tegnet, fargen som dekker mest) eller None når husene ikke kan registreres."""
    A = np.load(os.path.join(ROT, 'kilder', 'ai', 'modell_h_til_2019.npy'))
    H, W = lab.shape
    best = None
    for dx in range(-36, 37, 4):
        for dy in range(-36, 37, 4):
            dk = n = 0
            for b in husene:
                px = FT.m2px(A, b['p'], b.get('h', 4)); q = ((px + [dx, dy]) * S).astype(np.int32)
                x0, y0 = max(0, q[:, 0].min()), max(0, q[:, 1].min()); x1, y1 = min(W, q[:, 0].max() + 1), min(H, q[:, 1].max() + 1)
                if x1 <= x0 or y1 <= y0: continue
                m = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.fillPoly(m, [q - [x0, y0]], 1)
                dk += (lab[y0:y1, x0:x1][m > 0] >= 0).sum(); n += m.sum()
            if n == 0: continue
            sk = dk / n - math.hypot(dx, dy) / 200
            if best is None or sk > best[0]: best = (sk, dx, dy)
    if best is None or best[0] < 0.5: return None
    _, dx, dy = best
    base = FT.m2px(A, [a, e], 0.0); topp = FT.m2px(A, [a, e], H_MUR)
    q = (np.array([base[0], base[1], topp[1], topp[0]]) + [dx, dy]) * S
    q = q.astype(np.int32)
    x0, y0 = max(0, q[:, 0].min()), max(0, q[:, 1].min()); x1, y1 = min(W, q[:, 0].max() + 1), min(H, q[:, 1].max() + 1)
    if x1 <= x0 or y1 <= y0: return None
    m = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.fillPoly(m, [q - [x0, y0]], 1)
    # husene selv (tak og vegg) trekkes fra, så bare det som er tegnet i åpningen teller
    for b in husene:
        for hh in (b.get('h', 4), 0.0):
            hq = ((FT.m2px(A, b['p'], hh) + [dx, dy]) * S).astype(np.int32) - [x0, y0]; cv2.fillPoly(m, [hq], 0)
    if m.sum() < 20: return None
    l = lab[y0:y1, x0:x1][m > 0]
    # bare flater som kan være mur, gjerde eller port: ikke tak (rødt tegl) og ikke store husflater (over 4 x murflaten)
    flate = m.sum() / (S * S)
    def mur_flate(i):
        c = fl[i][1]; ar = abs(cv2.contourArea(np.asarray(fl[i][0], np.float32)))
        tak = c[0] > 160 and c[0] - c[2] > 60
        return (not tak) and ar <= 4 * flate
    ok_ids = {int(i) for i in np.unique(l[l >= 0]) if mur_flate(int(i))}
    treff = np.isin(l, list(ok_ids)) if ok_ids else np.zeros(l.shape, bool)
    andel = float(treff.mean())
    if andel == 0: return 0.0, None
    ids, k = np.unique(l[treff], return_counts=True)
    return andel, tuple(int(v) for v in fl[int(ids[np.argmax(k)])][1])


def gjerder_tegning(d, f, R, mpp, finnes):
    """Åpningene langs gata som tegningen viser lukket (andel >= 0,6 av murflaten tegnet), og som kartet ikke har gjerde, mur
    eller hekk i fra før (finnes: shapely-geometri med det som er funnet). Typen fra fargen i tegningen: grønn = hekk,
    lys (over 190) = mur (pusset portmur), ellers plankegjerde."""
    import colorsys
    from shapely.geometry import LineString
    FT, fl, lab = _tegning()
    bygg = {b['id']: b for b in d['bygg']}
    ut, sett, ikke = [], 0, 0
    for a, e, h1, h2 in aapninger(d, f, R, mpp):
        l = LineString([a, e])
        if finnes is not None and l.buffer(1.0).intersection(finnes).length > 0.5 * l.length: continue
        r = vurder_aapning_i_tegningen(a, e, [bygg[h] for h in (h1, h2) if h in bygg], d, FT, fl, lab)
        if r is None: continue
        andel, c = r
        if andel < 0.6 or c is None: ikke += 1; continue
        hh, ss, vv = colorsys.rgb_to_hsv(*(np.array(c) / 255))
        if 0.18 < hh < 0.48 and ss > 0.18: typ, art, h = 'hekk', 'hekk', 1.6
        elif min(c) > 190: typ, art, h = 'mur', 'mur', 2.2
        else: typ, art, h = 'gjerde', 'plankegjerde', 1.9
        sett += 1
        ut.append({'typ': typ, 'art': art, 'p': [[round(a[0], 2), round(a[1], 2)], [round(e[0], 2), round(e[1], 2)]], 'h': h,
                   'grunn': f'tegningen 2017/2019-trykket: åpningen mellom {h1} og {h2} er tegnet lukket ({andel:.0%} av murflaten, farge {list(c)}); '
                            'plassert i åpningen langs fasadelinja (kommunekartets omriss)'})
    print(f'tegningen: {sett} åpninger langs gata tegnet lukket, {ikke} tegnet åpne')
    return ut


# ---------- trærne ----------
KRONE_F = 1.1   # kartets krone (src/12: hovedklase s*0.74 + sideklaser s*0.58 ut) når ca. 1,1 * s fra stammen


def tretopper(R, mpp=MPP, d=None, med_vann=False, regioner=False):
    """Trærne i Kartverkets DOM−DTM: vegetasjon over 2,5 m som ikke er hus (1,5 m rundt fotavtrykkene tas bort), toppene som
    lokale maksima (minst 2,5 m mellom), kronen som vannskille-regionen rundt hver topp. Gir liste med (x, y, høyde, radius)
    og kronemasken."""
    from scipy import ndimage as ndi
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    d = d or datalag.alle()
    n = np.nan_to_num(ndsm(R, mpp, ), nan=0.0)
    hus = maske(hus_polygoner(d), R, mpp)
    r = int(round(1.5 / mpp)); hus = cv2.dilate(hus, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    ns = cv2.GaussianBlur(n, (0, 0), 0.8 / mpp)
    vann = maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp)
    krone = (ns > 2.5) & (hus == 0) & ((vann == 0) | med_vann)   # stammen står på land (med_vann: også der kartet har vann)
    krone = cv2.morphologyEx(krone.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    topp = peak_local_max(np.where(krone, ns, 0), min_distance=int(2.5 / mpp), threshold_abs=3.0, labels=krone.astype(int))
    mk = np.zeros(n.shape, np.int32)
    for i, (rr, cc) in enumerate(topp, 1): mk[rr, cc] = i
    reg = watershed(-ns, mk, mask=krone)
    areal = np.bincount(reg.ravel(), minlength=len(topp) + 1) * mpp * mpp
    x0, y0, x1, y1 = R; ut = []
    for i, (rr, cc) in enumerate(topp, 1):
        ut.append((x0 + (cc + 0.5) * mpp, y1 - (rr + 0.5) * mpp, float(ns[rr, cc]), math.sqrt(areal[i] / math.pi)))
    return (ut, krone, reg) if regioner else (ut, krone)


class _Rutenett:
    """Punktene (trestammene) i et rutenett, for å finne om det står et tre innen r m."""
    def __init__(self, r):
        self.r = r; self.c = {}
    def _k(self, x, y): return (int(math.floor(x / self.r)), int(math.floor(y / self.r)))
    def legg(self, x, y): self.c.setdefault(self._k(x, y), []).append((x, y))
    def fjern(self, x, y):
        l = self.c.get(self._k(x, y), [])
        for i, q in enumerate(l):
            if abs(q[0] - x) < 1e-6 and abs(q[1] - y) < 1e-6: l.pop(i); return
    def naer(self, x, y):
        kx, ky = self._k(x, y)
        return any(math.hypot(q[0] - x, q[1] - y) < self.r for dx in (-1, 0, 1) for dy in (-1, 0, 1) for q in self.c.get((kx + dx, ky + dy), []))


def _ledig_vegetasjon(veg, R, mpp, x, y, maks, opptatt):
    """Nærmeste vegetasjonspiksel (0,5 m inn fra kanten) innen maks m fra (x, y) uten tre innen 2,5 m. None hvis ingen."""
    x0, y0, x1, y1 = R
    c0 = max(0, int((x - maks - x0) / mpp)); c1 = min(veg.shape[1], int((x + maks - x0) / mpp) + 1)
    r0 = max(0, int((y1 - y - maks) / mpp)); r1 = min(veg.shape[0], int((y1 - y + maks) / mpp) + 1)
    if c1 <= c0 or r1 <= r0: return None
    sub = cv2.erode(veg[r0:r1, c0:c1], np.ones((5, 5), np.uint8))   # 0,5 m inn fra kanten av kronen
    yy, xx = np.nonzero(sub)
    if not len(yy): return None
    X = x0 + (c0 + xx + 0.5) * mpp; Y = y1 - (r0 + yy + 0.5) * mpp
    dd = np.hypot(X - x, Y - y); o = np.argsort(dd)
    for k in o[::3]:
        if dd[k] > maks: break
        if not opptatt.naer(X[k], Y[k]): return (float(X[k]), float(Y[k]))
    return None


def vegetasjon(R, mpp=MPP, d=None):
    """Vegetasjon over 1,5 m i DOM−DTM (glattet 0,4 m), uten hus (fotavtrykk + 1,5 m). 0/1-maske."""
    d = d or datalag.alle()
    n = np.nan_to_num(ndsm(R, mpp), nan=0.0); hus = maske(hus_polygoner(d), R, mpp)
    r = int(round(1.5 / mpp)); husb = cv2.dilate(hus, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    vann = maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp)
    # stammen står på land: kroner som henger ut over vollgraven og elva teller ikke
    return ((cv2.GaussianBlur(n, (0, 0), 0.4 / mpp) > 1.5) & (husb == 0) & (vann == 0)).astype(np.uint8)


AVSTAND_M = 5.0   # minste avstand mellom stammene i et tett felt uten egne topper (løvtrær i rekke/lund i Gamlebyen: 6–8 m)
KOBLE_M = 6.0   # et tre og en tretopp i DOM−DTM innen 6 m er samme tre (Google-flyfotoet var forskjøvet opptil ca. 10 m)


def traer(skriv=True, maks_flytt=12.0):
    """Kontroll av trærne (data/traer.json, [x, y, s, bakkehøyde]) i Gamlebyen mot Kartverkets DOM−DTM, som ser kronene
    (ortofotoet fra april ser bare greinene). Trærne ble lest fra Google-flyfotoet 23.10, som er forskjøvet flere steder.
      1. tretoppene i DOM−DTM kobles én-til-én til trærne innen 3 m (ungarsk metode); treet flyttes til toppen (over 0,7 m)
      2. et tre som ikke fikk topp og står mer enn 1 m utenfor vegetasjonen, flyttes til nærmeste vegetasjon (0,5 m inn),
         når den er innen maks_flytt m
      3. kronen gjøres større når kronen i DOM−DTM er over 30 % større enn kartets (kartets krone når ca. 1,15 * s fra stammen);
         mindre gjøres den ikke (DOM-en har løvfrie kroner, som måler for smått)
      4. bakkehøyden følger terrenget der treet flyttes
    Antallet følger DOM−DTM: ett tre per tretopp. Et tre uten topp som står inne i kronen til en topp (vannskilleregionen), er
    en dublett fra oppdelingen 23.10 og tas ut; en topp uten tre får et nytt (kronen fra DOM-en). Et tre i vannet uten vegetasjon
    innen 2 x maks_flytt er ikke et tre (mørkt vann lest som krone). Trær lenger enn maks_flytt fra vegetasjon er dømt med øyet i
    ortofotoet (kilder/bakke-maalt.json «traer_dommer»). Alt som tas ut eller legges til, står med grunn i kilder/bakke-maalt.json
    («traer_fjernet», «traer_nye»); koblingen per tre i rapport/bakke/traer.json."""
    from scipy.optimize import linear_sum_assignment
    from shapely.geometry import Point
    from shapely.prepared import prep
    d = datalag.alle(); dom = domene(); R = ramme(dom); mpp = MPP
    T = datalag.les('traer')
    topper, _, kronereg = tretopper(R, mpp, d, regioner=True)
    vtopp = np.array([[a, b] for a, b, _, _ in tretopper(R, mpp, d, med_vann=True)[0]])
    ekte = lambda t: len(vtopp) and np.hypot(vtopp[:, 0] - t[0], vtopp[:, 1] - t[1]).min() <= 1.0   # topp i DOM−DTM, også der kartet har vann
    veg = vegetasjon(R, mpp, d)
    dist, lab = cv2.distanceTransformWithLabels(1 - veg, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    yy, xx = np.nonzero(veg); naer = np.zeros((lab.max() + 1, 2), np.int32); naer[lab[yy, xx]] = np.stack([yy, xx], 1)
    _, th = terreng(R, mpp, d)
    vann = maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp)
    _, lab_l = cv2.distanceTransformWithLabels(vann, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    yy, xx = np.nonzero(vann == 0); naer_land = np.zeros((lab_l.max() + 1, 2), np.int32); naer_land[lab_l[yy, xx]] = np.stack([yy, xx], 1)
    H, W = veg.shape
    rc = lambda x, y: (int((R[3] - y) / mpp), int((x - R[0]) / mpp))
    xy = lambda r, c: (R[0] + (c + 0.5) * mpp, R[3] - (r + 0.5) * mpp)
    pd = prep(dom)
    # alle trær i rammen rundt Gamlebyen (vollene, vollgravene og beltet rundt), der DOM-en dekker
    nan = np.isnan(ndsm(R, mpp))
    idx = [i for i, t in enumerate(T) if 0 <= rc(t[0], t[1])[0] < H and 0 <= rc(t[0], t[1])[1] < W and not nan[rc(t[0], t[1])]]
    tp = np.array([[a, b] for a, b, _, _ in topper]); tt = np.array([[T[i][0], T[i][1]] for i in idx])
    C = np.sqrt(((tt[:, None, :] - tp[None, :, :]) ** 2).sum(2)); C2 = np.where(C <= KOBLE_M, C, 1e6)
    ri, ci = linear_sum_assignment(C2)
    kobling = {idx[a]: b for a, b in zip(ri, ci) if C2[a, b] < 1e6}
    tall = {'topp': 0, 'til_vegetasjon': 0, 'krone': 0, 'for_langt': 0}; liste = []
    opptatt = _Rutenett(2.5)
    for i in idx: opptatt.legg(T[i][0], T[i][1])
    for i in idx:
        t = T[i]; rec = {'i': i, 'fra': [t[0], t[1]], 's': t[2]}
        if i in kobling:
            x, y, h, rad = topper[kobling[i]]
            rec.update(topp=[round(x, 2), round(y, 2)], hoyde=round(h, 1), radius=round(rad, 2))
            if math.hypot(x - t[0], y - t[1]) > 0.7:
                opptatt.fjern(t[0], t[1]); t[0], t[1] = round(x, 1), round(y, 1); opptatt.legg(t[0], t[1]); tall['topp'] += 1
            if t[2] and rad > 1.3 * 1.15 * t[2]: t[2] = round(min(rad / 1.15, 9.0), 2); tall['krone'] += 1
        elif kronereg[rc(t[0], t[1])] > 0 or (len(tp) and C[idx.index(i)].min() <= KOBLE_M):
            # står inne i kronen til en topp, eller innen KOBLE_M m fra en topp, som et annet tre har: dublett fra oppdelingen 23.10
            k = kronereg[rc(t[0], t[1])] - 1 if kronereg[rc(t[0], t[1])] > 0 else int(np.argmin(C[idx.index(i)]))
            rec['dublett'] = [round(topper[k][0], 1), round(topper[k][1], 1)]
        else:
            r, c = rc(t[0], t[1]); dv = dist[r, c] * mpp; rec['avstand_veg'] = round(float(dv), 2)
            i_vann = vann[r, c] > 0 and not ekte(t)
            if 1.0 < dv <= maks_flytt or (i_vann and dv <= 2 * maks_flytt):
                # nærmeste vegetasjon der det ikke står et tre fra før (minst 2,5 m mellom stammene), så trærne ikke stables i kanten
                plass = _ledig_vegetasjon(veg, R, mpp, t[0], t[1], dv + 3.0, opptatt)
                if plass is None:
                    nr, nc = naer[lab[r, c]]; vx, vy = xy(nr, nc); ux, uy = vx - t[0], vy - t[1]; l = math.hypot(ux, uy) or 1
                    plass = (vx + ux / l * 0.5, vy + uy / l * 0.5)
                opptatt.fjern(t[0], t[1]); t[0], t[1] = round(plass[0], 1), round(plass[1], 1); opptatt.legg(t[0], t[1])
                tall['til_vegetasjon'] += 1
            elif i_vann:   # i vollgraven/elva og ingen vegetasjon innen 2 x maks_flytt: ikke et tre (mørkt, kornete vann lest som krone)
                rec['fjernet'] = True; tall['fjernet_vann'] = tall.get('fjernet_vann', 0) + 1
            elif dv > maks_flytt:
                tall['for_langt'] += 1; rec['for_langt'] = True
        r, c = rc(t[0], t[1])
        if 0 <= r < H and 0 <= c < W and vann[r, c] and 'topp' not in rec and not rec.get('fjernet') and not ekte(t):
            # landet i vannkanten: inn på nærmeste land
            nr, nc = naer_land[lab_l[r, c]]; vx, vy = xy(nr, nc); ux, uy = vx - t[0], vy - t[1]; l = math.hypot(ux, uy) or 1
            t[0], t[1] = round(vx + ux / l * 0.5, 1), round(vy + uy / l * 0.5, 1); r, c = rc(t[0], t[1])
        if [t[0], t[1]] != rec['fra'] and 0 <= r < H and 0 <= c < W: t[3] = round(float(max(0.0, th[r, c])), 2)
        rec['til'] = [t[0], t[1]]
        liste.append(rec)
    grunner = {r['i']: ('i vann (data/vann.json) og ingen vegetasjon over 1,5 m i DOM−DTM innen '
                        f'{2 * maks_flytt:g} m: ikke et tre (Google-flyfotoet 23.10: mørkt vann lest som krone)') for r in liste if r.get('fjernet')}
    # dømt med øyet i ortofotoet (kilder/bakke-maalt.json «traer_dommer»): trær uten vegetasjon innen maks_flytt
    dommer = maalt().get('traer_dommer', [])
    for r in liste:
        if r.get('for_langt'):
            dm = min(dommer, key=lambda q: math.hypot(q['p'][0] - r['fra'][0], q['p'][1] - r['fra'][1]), default=None)
            if dm and math.hypot(dm['p'][0] - r['fra'][0], dm['p'][1] - r['fra'][1]) < 0.5 and dm['dom'] == 'fjern':
                grunner[r['i']] = dm['grunn']; tall['dom_fjern'] = tall.get('dom_fjern', 0) + 1
    for r in liste:
        if 'dublett' in r:
            grunner[r['i']] = (f"dublett: står inne i kronen til tretoppen ved ({r['dublett'][0]}, {r['dublett'][1]}) i DOM−DTM, som har sitt eget tre "
                               '(tett felt delt i kroner av verktøyet 23.10)'); tall['dublett'] = tall.get('dublett', 0) + 1
    fjern = set(grunner)
    m = maalt()
    m['traer_fjernet'] = [{'p': T[i], 'grunn': grunner[i], 'hvem': 'Claude', 'dato': '2026-10-29'} for i in sorted(fjern)]
    if skriv: json.dump(m, open(MAALT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    T = [t for i, t in enumerate(T) if i not in fjern]
    idx = [i - sum(1 for j in fjern if j < i) for i in idx if i not in fjern]
    # tretopper uten tre i kartet: nytt tre der DOM−DTM har kronen
    brukte = set(kobling.values()); nye = []
    for k, (x, y, h, rad) in enumerate(topper):
        if k in brukte: continue
        r, c = rc(x, y)
        nye.append([round(x, 1), round(y, 1), round(max(2.0, min(8.0, rad / 1.1)), 2), round(float(max(0.0, th[r, c])), 2)])
    idx += list(range(len(T), len(T) + len(nye))); T += nye; tall['nye'] = len(nye)
    # trær i vegetasjon uten egen topp (kronene i et tett felt har ingen klar topp i den løvfrie DOM-en): minst AVSTAND_M m
    # mellom stammene, regnet fra trærne på toppene; tettere er dubletter fra oppdelingen 23.10
    fast = set(idx[len(idx) - len(nye):]) | {i - sum(1 for j in fjern if j < i) for i in kobling if i not in fjern}
    rut = _Rutenett(AVSTAND_M)
    for i in fast: rut.legg(T[i][0], T[i][1])
    tynn = set()
    for i in sorted((i for i in idx if i not in fast), key=lambda i: -(T[i][2] or 0)):
        if rut.naer(T[i][0], T[i][1]): tynn.add(i)
        else: rut.legg(T[i][0], T[i][1])
    if tynn:
        m['traer_fjernet'] += [{'p': T[i], 'grunn': f'dublett: under {AVSTAND_M:g} m fra et annet tre i et tett felt uten egne topper i DOM−DTM '
                                '(oppdelingen 23.10 la kronene for tett)', 'hvem': 'Claude', 'dato': '2026-10-29'} for i in sorted(tynn)]
        T = [t for i, t in enumerate(T) if i not in tynn]
        idx = [i - sum(1 for j in tynn if j < i) for i in idx if i not in tynn]
        tall['dublett'] = tall.get('dublett', 0) + len(tynn); fjern = fjern | {('tynn', i) for i in tynn}
    m['traer_nye'] = [{'p': t, 'grunn': 'tretopp i DOM−DTM uten tre i kartet', 'hvem': 'Claude', 'dato': '2026-10-29'} for t in nye]
    if skriv: json.dump(m, open(MAALT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    # sluttkontroll: andel trær på vegetasjon (innen 1 m)
    paa = sum(1 for i in idx if dist[rc(T[i][0], T[i][1])] * mpp <= 1.0)
    print(f"{len(T)} trær, {len(idx)} i rammen rundt Gamlebyen, {len(topper)} topper i DOM−DTM: {len(kobling)} koblet til topp ({tall['topp']} flyttet), "
          f"{tall['til_vegetasjon']} flyttet inn til vegetasjon, {tall['krone']} kroner større, {tall['for_langt']} mer enn {maks_flytt:g} m fra vegetasjon (uendret); "
          f"etter: {paa / len(idx):.1%} står på vegetasjon (innen 1 m); tatt ut: {len(fjern)} {dict((k, v) for k, v in tall.items() if k in ('fjernet_vann', 'dom_fjern', 'dublett'))}; nye fra DOM-toppene: {tall.get('nye', 0)}")
    if skriv:
        with open(os.path.join(ROT, 'data', 'traer.json'), 'w', encoding='utf8') as fh:
            json.dump(T, fh, separators=(',', ':'))
        os.makedirs(ARK_MAPPE, exist_ok=True)
        json.dump({'topper': [[round(a, 2), round(b, 2), round(h, 1), round(r, 2)] for a, b, h, r in topper], 'traer': liste, 'tall': tall},
                  open(os.path.join(ARK_MAPPE, 'traer.json'), 'w'), separators=(',', ':'))
    return liste, topper


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    if k == 'overflater': overflater()
    elif k == 'gater': gater()
    elif k == 'innkjorsler': innkjorsler()
    elif k == 'gjerder': gjerder()
    elif k == 'traer': traer()
    elif k == 'ark': ark([int(a) for a in sys.argv[2:]] or None)
    else: print(__doc__)
