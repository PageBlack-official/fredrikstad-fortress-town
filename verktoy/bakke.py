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
    print('flater fra ortofotoet:', len(liste), {k: v for k, v in tall.items() if v[0]}, len(nye_id), 'nye id-er')
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
        if abs(fo) > 0.5 and abs(fo) < b / 2 and n >= 5:
            P = v['p']; Q = []
            for i, q in enumerate(P):
                a = P[max(0, i - 1)]; c = P[min(len(P) - 1, i + 1)]
                dx, dy = c[0] - a[0], c[1] - a[1]; l = math.hypot(dx, dy) or 1
                Q.append([round(q[0] - dy / l * fo, 2), round(q[1] + dx / l * fo, 2)] + q[2:])
            v['p'] = Q
        flatetype()
        v['maalt'] = f'{kilde}: {n} målinger, bredde {b} m' + (f', flyttet {fo:+.1f} m sideveis' if abs(fo) > 0.5 and abs(fo) < b / 2 and n >= 5 else '')
    # en vei der typen skifter (brostein -> grus, asfalt …), deles der den skifter, så båndet tegnes med riktig flate hele veien
    nye, delt = [], 0
    for v in L['veier']:
        if 'maalt' not in v or len(v['p']) < 2: nye.append(v); continue
        biter = del_etter_type(v, kl, R, mpp)
        if len(biter) > 1:   # hver bit får bredden målt for seg (samme kilde som hele veien)
            delt += 1
            for w in biter:
                r = (maal_vei(w, kkl, ok_kk, R, mpp, luke=1.2) or maal_vei(w, kl, ok_or, R, mpp, luke=0.75)) if w['k'] == 'kjore' else maal_vei(w, kl, ok_or, R, mpp, maks=8, luke=0.5, maks_b=6.0)
                if r and r[2] >= 5: w['w'] = max(1.0, round(r[0] * 2) / 2); w['maalt'] = v['maalt'].split(':')[0] + f': {r[2]} målinger, bredde {w["w"]} m (delt der flatetypen skifter)'
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
        g['grunn'] = (f"ortofoto 2024: {'grønn stripe' if g['typ'] == 'hekk' else 'mørk smal stripe (gjerdet og skyggen)'} på {g['andel']:.0%} av lengden"
                      + (f"; DOM−DTM {g['h']} m" if g['typ'] in ('mur', 'hekk') else '') + f"; langs {g['kilde_linje']}")
        g['kilde'] = 'ortofoto 2024 + kommunekartets eiendomsgrenser + Kartverket DOM−DTM (verktoy/bakke.py gjerder)'
    valgt = [{k: g[k] for k in ('id', 'typ', 'p', 'h', 'grunn', 'kilde')} for g in sorted(valgt, key=lambda g: int(g['id'].split('-')[1]))]
    ny = _uu([LineString(g['p']).buffer(1.0) for g in valgt]) if valgt else None
    forkastet = []
    for g in d.get('gardsrom', []):   # gjerdene kartet hadde før 29.10, var gårdsromkantene
        if g.get('skjul') or len(g['p']) < 3: continue
        p = g['p'] + [g['p'][0]]; l = LineString(p)
        if ny is None or l.intersection(ny).length < 0.5 * l.length: forkastet.append({'p': p, 'lengde': round(l.length, 1)})
    tall = {t: (sum(1 for g in valgt if g['typ'] == t), round(sum(math.dist(*g['p']) for g in valgt if g['typ'] == t))) for t in ('gjerde', 'mur', 'hekk')}
    print(f'{len(kand)} kandidatstykker, {len(valgt)} sett i fotoet:', tall, f'; {len(forkastet)} av kartets gjerder fra før (gårdsromkantene) ses ikke og er tatt ut')
    if skriv:
        with open(os.path.join(ROT, 'data', 'gjerder.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(g, ensure_ascii=False, separators=(',', ':')) for g in valgt) + '\n]\n')
        mangler = [g['id'] for g in valgt if g['id'] not in reg]
        if mangler: open(reg_fil, 'a', encoding='utf8').write('\n'.join(mangler) + '\n')
        os.makedirs(ARK_MAPPE, exist_ok=True)
        json.dump(forkastet, open(os.path.join(ARK_MAPPE, 'gjerder-forkastet.json'), 'w'), indent=0)
    return valgt


# ---------- trærne ----------
KRONE_F = 1.1   # kartets krone (src/12: hovedklase s*0.74 + sideklaser s*0.58 ut) når ca. 1,1 * s fra stammen


def tretopper(R, mpp=MPP, d=None):
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
    krone = (ns > 2.5) & (hus == 0)
    krone = cv2.morphologyEx(krone.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    topp = peak_local_max(np.where(krone, ns, 0), min_distance=int(2.5 / mpp), threshold_abs=3.0, labels=krone.astype(int))
    mk = np.zeros(n.shape, np.int32)
    for i, (rr, cc) in enumerate(topp, 1): mk[rr, cc] = i
    reg = watershed(-ns, mk, mask=krone)
    areal = np.bincount(reg.ravel(), minlength=len(topp) + 1) * mpp * mpp
    x0, y0, x1, y1 = R; ut = []
    for i, (rr, cc) in enumerate(topp, 1):
        ut.append((x0 + (cc + 0.5) * mpp, y1 - (rr + 0.5) * mpp, float(ns[rr, cc]), math.sqrt(areal[i] / math.pi)))
    return ut, krone


def vegetasjon(R, mpp=MPP, d=None):
    """Vegetasjon over 1,5 m i DOM−DTM (glattet 0,4 m), uten hus (fotavtrykk + 1,5 m). 0/1-maske."""
    d = d or datalag.alle()
    n = np.nan_to_num(ndsm(R, mpp), nan=0.0); hus = maske(hus_polygoner(d), R, mpp)
    r = int(round(1.5 / mpp)); husb = cv2.dilate(hus, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    vann = maske([w['p'] for w in d['vann'] if w.get('p')], R, mpp)
    # stammen står på land: kroner som henger ut over vollgraven og elva teller ikke
    return ((cv2.GaussianBlur(n, (0, 0), 0.4 / mpp) > 1.5) & (husb == 0) & (vann == 0)).astype(np.uint8)


def traer(skriv=True, maks_flytt=12.0):
    """Kontroll av trærne (data/traer.json, [x, y, s, bakkehøyde]) i Gamlebyen mot Kartverkets DOM−DTM, som ser kronene
    (ortofotoet fra april ser bare greinene). Trærne ble lest fra Google-flyfotoet 23.10, som er forskjøvet flere steder.
      1. tretoppene i DOM−DTM kobles én-til-én til trærne innen 3 m (ungarsk metode); treet flyttes til toppen (over 0,7 m)
      2. et tre som ikke fikk topp og står mer enn 1 m utenfor vegetasjonen, flyttes til nærmeste vegetasjon (0,5 m inn),
         når den er innen maks_flytt m
      3. kronen gjøres større når kronen i DOM−DTM er over 30 % større enn kartets (kartets krone når ca. 1,15 * s fra stammen);
         mindre gjøres den ikke (DOM-en har løvfrie kroner, som måler for smått)
      4. bakkehøyden følger terrenget der treet flyttes
    Antallet trær endres ikke, med ett unntak: et tre som står i vannet uten vegetasjon innen 2 x maks_flytt, er ikke et tre
    (Google-flyfotoet: mørkt, kornete vann lest som krone) og tas ut, med grunn i kilder/bakke-maalt.json «traer_fjernet».
    Trær på land som står lenger enn maks_flytt fra vegetasjon, står uendret og listes (rapport/bakke/traer.json)."""
    from scipy.optimize import linear_sum_assignment
    from shapely.geometry import Point
    from shapely.prepared import prep
    d = datalag.alle(); dom = domene(); R = ramme(dom); mpp = MPP
    T = datalag.les('traer')
    topper, _ = tretopper(R, mpp, d)
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
    C = np.sqrt(((tt[:, None, :] - tp[None, :, :]) ** 2).sum(2)); C2 = np.where(C <= 3.0, C, 1e6)
    ri, ci = linear_sum_assignment(C2)
    kobling = {idx[a]: b for a, b in zip(ri, ci) if C2[a, b] < 1e6}
    tall = {'topp': 0, 'til_vegetasjon': 0, 'krone': 0, 'for_langt': 0}; liste = []
    for i in idx:
        t = T[i]; rec = {'i': i, 'fra': [t[0], t[1]], 's': t[2]}
        if i in kobling:
            x, y, h, rad = topper[kobling[i]]
            rec.update(topp=[round(x, 2), round(y, 2)], hoyde=round(h, 1), radius=round(rad, 2))
            if math.hypot(x - t[0], y - t[1]) > 0.7: t[0], t[1] = round(x, 1), round(y, 1); tall['topp'] += 1
            if t[2] and rad > 1.3 * 1.15 * t[2]: t[2] = round(min(rad / 1.15, 9.0), 2); tall['krone'] += 1
        else:
            r, c = rc(t[0], t[1]); dv = dist[r, c] * mpp; rec['avstand_veg'] = round(float(dv), 2)
            i_vann = vann[r, c] > 0
            if 1.0 < dv <= maks_flytt or (i_vann and dv <= 2 * maks_flytt):
                nr, nc = naer[lab[r, c]]; vx, vy = xy(nr, nc)
                ux, uy = vx - t[0], vy - t[1]; l = math.hypot(ux, uy) or 1
                t[0], t[1] = round(vx + ux / l * 0.5, 1), round(vy + uy / l * 0.5, 1); tall['til_vegetasjon'] += 1
            elif i_vann:   # i vollgraven/elva og ingen vegetasjon innen 2 x maks_flytt: ikke et tre (mørkt, kornete vann lest som krone)
                rec['fjernet'] = True; tall['fjernet_vann'] = tall.get('fjernet_vann', 0) + 1
            elif dv > maks_flytt:
                tall['for_langt'] += 1; rec['for_langt'] = True
        r, c = rc(t[0], t[1])
        if [t[0], t[1]] != rec['fra'] and 0 <= r < H and 0 <= c < W: t[3] = round(float(max(0.0, th[r, c])), 2)
        rec['til'] = [t[0], t[1]]
        liste.append(rec)
    fjern = {r['i'] for r in liste if r.get('fjernet')}
    if fjern:
        m = maalt(); gml = m.get('traer_fjernet', [])
        gml += [{'p': T[i], 'grunn': 'i vann (data/vann.json) og ingen vegetasjon over 1,5 m i DOM−DTM innen '
                 f'{2 * maks_flytt:g} m: ikke et tre (Google-flyfotoet 23.10: mørkt vann lest som krone)', 'hvem': 'Claude', 'dato': '2026-10-29'} for i in sorted(fjern)]
        sett_ = set(); m['traer_fjernet'] = [g for g in gml if not (tuple(g['p'][:2]) in sett_ or sett_.add(tuple(g['p'][:2])))]
        if skriv: json.dump(m, open(MAALT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        T = [t for i, t in enumerate(T) if i not in fjern]
        idx = [i - sum(1 for j in fjern if j < i) for i in idx if i not in fjern]
    # sluttkontroll: andel trær på vegetasjon (innen 1 m)
    paa = sum(1 for i in idx if dist[rc(T[i][0], T[i][1])] * mpp <= 1.0)
    print(f"{len(T)} trær, {len(idx)} i rammen rundt Gamlebyen, {len(topper)} topper i DOM−DTM: {len(kobling)} koblet til topp ({tall['topp']} flyttet), "
          f"{tall['til_vegetasjon']} flyttet inn til vegetasjon, {tall['krone']} kroner større, {tall['for_langt']} mer enn {maks_flytt:g} m fra vegetasjon (uendret); "
          f"etter: {paa / len(idx):.1%} står på vegetasjon (innen 1 m)")
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
    elif k == 'gjerder': gjerder()
    elif k == 'traer': traer()
    elif k == 'ark': ark([int(a) for a in sys.argv[2:]] or None)
    else: print(__doc__)
