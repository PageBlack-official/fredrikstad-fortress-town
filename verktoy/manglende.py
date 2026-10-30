"""Tegnede hus uten modellhus (kontrollens «tegnet_uten_modell») og hus med feil omriss/høyde: kontaktark per flategruppe.

Kontrollen (verktoy/kontroll.py avvik) finner flategrupper i en 2015-tegning som ikke har noe modellhus under seg. Mange er
bare frihåndsforskyvning, men noen er hus modellen mangler, eller hus som står for kort/lavt. Dette verktøyet legger hver
gruppe ned på bakken (tegningens kamera baklengs: bunnkanten av gruppen på z = 0, og hele gruppen på z = 0 og z = 7 m, så
huset ligger mellom de to) og viser den ved siden av kildene som avgjør om huset finnes i dag:

    tegningen (gruppen rødt) | modellen i tegningens projeksjon | ortofoto 2024 med kommunekartets omriss (gult), modellhusene
    (rødt, id), Matrikkelens bygningspunkter (lilla) og gruppen på bakken (cyan: bunnkant, tynn: z 0/7 m) | kommunekartet
    (PDF-en rendret) | Kartverkets DOM−DTM

    python3 verktoy/manglende.py liste                 gruppene fra rapport/kontroll/avvik.json med plass på bakken
                                                       (rapport/manglende/grupper.json) og dommen fra kilder/bygg-merknader.json
    python3 verktoy/manglende.py ark [tegning ...]     kontaktark rapport/manglende/<tegning>-<n>.jpg (bare lokalt: viser
                                                       tegningen, ortofotoet og kommunekartet)
    python3 verktoy/manglende.py se x y [r] [navn]     samme fire kildepaneler for et vilkårlig punkt (modellmeter)

Dommen per gruppe står i kilder/bygg-merknader.json under «tegnet_uten_modell» (tegning, senter_pt, utfall, grunn) og leses
av kontroll.py: en gruppe med dom blir «avvik med grunn» (huset finnes ikke i dag, eller er tegnet fritt) eller «lagt inn»
(huset er lagt inn i modellen; gruppen skal da forsvinne neste gang kontrollen kjøres).
"""
import json, math, os, sys
import numpy as np, cv2
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))

UT = os.path.join(ROT, 'rapport', 'manglende')
AVVIK = os.path.join(ROT, 'rapport', 'kontroll', 'avvik.json')
R = 3.0


def bakken(P, u, v, z=0.0):
    """Tegningspunkt (pt) -> modellpunkt (x, y) på høyde z med projeksjonen P (2x4)."""
    A = P[:, :2]; b = np.array([u, v]) - P[:, 2] * z - P[:, 3]
    return np.linalg.solve(A, b)


def gruppe_poly(navn, g):
    import fasade_tegning as FT
    from shapely.ops import unary_union
    F, _ = FT.flater(navn)
    U = unary_union([F[j]['ytre'].buffer(0.8) for j in g['flater']]).buffer(-0.8)
    if U.geom_type != 'Polygon':
        U = max(getattr(U, 'geoms', [U]), key=lambda q: q.area)
    return U


def bunnkant(U, steg=1.0):
    """Nederste punkt per kolonne i gruppens omriss (tegningen: y ned) = husets fot mot betrakteren."""
    from shapely.geometry import LineString
    x0, y0, x1, y1 = U.bounds; ut = []
    for x in np.arange(x0 + 0.3, x1 - 0.3 + 1e-6, steg):
        s = U.intersection(LineString([(x, y0 - 1), (x, y1 + 1)]))
        if s.is_empty: continue
        ut.append((x, s.bounds[3]))
    return ut


def plass(navn, g):
    """Gruppen lagt på bakken med kameraet til nærmeste modellhus (blokkens forskyvning)."""
    import kontroll as KO
    K = KO.les_kamera(navn)
    P = KO.P_hus(K, g['naermeste_modellhus']) if g.get('naermeste_modellhus') else np.array(K['A'], float)
    U = gruppe_poly(navn, g)
    bk = [bakken(P, u, v, 0.0) for u, v in bunnkant(U)]
    z0 = [bakken(P, u, v, 0.0) for u, v in U.exterior.coords]
    z7 = [bakken(P, u, v, 7.0) for u, v in U.exterior.coords]
    c = np.mean(np.array(bk), 0) if bk else np.mean(np.array(z0), 0)
    # midt i huset: et stykke bak bunnkanten (halvveis mot z = 7 m-flaten)
    m = 0.5 * (c + np.mean(np.array(z7), 0))
    return dict(bunnkant=[list(map(float, q)) for q in bk], z0=[list(map(float, q)) for q in z0], z7=[list(map(float, q)) for q in z7],
                fot=list(map(float, c)), midt=list(map(float, m)))


def dommer():
    M = json.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))
    return M.get('tegnet_uten_modell', [])


def dom_for(g, D=None):
    """Dommen for en gruppe: samme tegning og senter innen 12 pt (gruppene flytter seg litt når kamera eller omriss endres)."""
    D = dommer() if D is None else D
    best = None
    for d in D:
        if d['tegning'] != g['tegning']: continue
        a = math.dist(d['senter_pt'], g['senter_pt'])
        if a <= d.get('radius_pt', 12) and (best is None or a < best[0]):
            best = (a, d)
    return best[1] if best else None


def liste():
    A = json.load(open(AVVIK, encoding='utf8'))
    D = dommer(); ut = []
    for k, g in enumerate(A['tegnet_uten_modell']):
        try:
            p = plass(g['tegning'], g)
        except Exception as e:
            p = dict(feil=str(e))
        d = dom_for(g, D)
        ut.append(dict(nr=k, **g, plass=p, dom=d and d['utfall'], grunn=d and d['grunn']))
    os.makedirs(UT, exist_ok=True)
    json.dump(ut, open(os.path.join(UT, 'grupper.json'), 'w'), indent=1, ensure_ascii=False)
    for r in ut:
        f = r['plass'].get('fot')
        print(f"{r['nr']:3d} {r['tegning']:14s} {str(r['senter_pt']):16s} {r['areal_pt2']:6d} pt² ~{r['hus_anslag']} hus  "
              f"fot {f and f'({f[0]:.0f}, {f[1]:.0f})'}  {r['dom'] or '-'}")
    return ut


# ---------------------------------------------------------------- panelene

def kommunekart_utsnitt(x0, y0, x1, y1, mpp):
    """Kommunekartet (PDF-en) rendret over modellrektangelet, rotert til nord opp."""
    import pymupdf, kommunekart as KK
    T = KK._transform(); side = pymupdf.open(KK.PDF)[0]
    W, H = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    # modell -> pdf: roter -rot rundt (cx, cy), så x = (X - tx)/S, y = (ty - Y)/S
    def til_pdf(X, Y):
        a = math.radians(-T['rot']); dx, dy = X - T['cx'], Y - T['cy']
        Xr = T['cx'] + dx * math.cos(a) - dy * math.sin(a); Yr = T['cy'] + dx * math.sin(a) + dy * math.cos(a)
        return (Xr - T['tx']) / T['S'], (T['ty'] - Yr) / T['S']
    hj = [til_pdf(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    px0, py0 = min(h[0] for h in hj) - 2, min(h[1] for h in hj) - 2; px1, py1 = max(h[0] for h in hj) + 2, max(h[1] for h in hj) + 2
    z = T['S'] / mpp
    pm = side.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(px0, py0, px1, py1), alpha=False)
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3][:, :, ::-1].copy()
    # affin: utsnittets piksel (c, r) for modellpunkt
    src = np.float32([[(til_pdf(x, y)[0] - px0) * z, (til_pdf(x, y)[1] - py0) * z] for x, y in ((x0, y1), (x1, y1), (x0, y0))])
    dst = np.float32([[0, 0], [W, 0], [0, H]])
    M = cv2.getAffineTransform(src, dst)
    return cv2.warpAffine(im, M, (W, H), borderValue=(255, 255, 255))


# ---------------------------------------------------------------- 2015-kildene (kommunen): avgjør revet / tegnet fritt
KOMMUNE = 'https://arcgis.fredrikstad.kommune.no/server/rest/services/Bakgrunnskart/'
HK = os.path.join(ROT, 'rapport', 'hoyder', 'kilder')


def hent_2015():
    """Kommunens DOM og DTM fra laserskanningen 2015 (samme år som tegningene), samme rute som Kartverkets dom1/dtm1.
    Ligger bare lokalt (kommunens data, lisens ikke avklart): rapport/hoyder/kilder/dom2015_25832.tif, dtm2015_25832.tif."""
    import urllib.request
    m = json.load(open(os.path.join(HK, 'dom1_25832.tif.json')))['url']
    bb = m.split('bbox=')[1].split('&')[0]; x0, y0, x1, y1 = map(int, bb.split(','))
    for tj, navn in (('DOM_2015_Fredrikstad_Hvaler_Sarpsborg', 'dom2015'), ('Terrengmodell_DTM_2015', 'dtm2015')):
        sti = os.path.join(HK, f'{navn}_25832.tif')
        if os.path.exists(sti): continue
        q = (f'{KOMMUNE}{tj}/ImageServer/exportImage?bbox={bb}&bboxSR=25832&imageSR=25832&size={x1 - x0},{y1 - y0}'
             f'&format=tiff&pixelType=F32&interpolation=RSP_NearestNeighbor&f=image')
        data = urllib.request.urlopen(q, timeout=180).read()
        if data[:4] not in (b'II*\x00', b'MM\x00*'): raise SystemExit(f'{navn}: ikke TIFF')
        open(sti, 'wb').write(data)
        json.dump({'url': q, 'kilde': 'Fredrikstad kommune, laserskanning 2015', 'lisens': 'ikke avklart: bare lokalt'}, open(sti + '.json', 'w'), indent=1)
        print('hentet', sti)


def ndh(x0, y0, x1, y1, mpp, dom='dom1', dtm='dtm1'):
    """DOM−DTM over modellrektangelet (se_her.ndh_utsnitt med valgfri kilde)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('hent', os.path.join(ROT, 'rapport', 'hoyder', 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    a, gt = hent.les(os.path.join(HK, f'{dom}_25832.tif')); b, _ = hent.les(os.path.join(HK, f'{dtm}_25832.tif'))
    nd = a - b; ex0, ny0, dx, dy = gt
    W, H = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    xs, ys = np.meshgrid(x0 + (np.arange(W) + 0.5) * mpp, y1 - (np.arange(H) + 0.5) * mpp)
    U = hent.til_utm(np.stack([xs, ys], -1))
    c = ((U[..., 0] - ex0) / dx).astype(int); r = ((ny0 - U[..., 1]) / dy).astype(int)
    ok = (r >= 0) & (r < nd.shape[0]) & (c >= 0) & (c < nd.shape[1])
    out = np.full((H, W), np.nan); out[ok] = nd[r[ok], c[ok]]
    return out


def ortofoto_2019(x0, y0, x1, y1, mpp):
    """Kommunens ortofoto 2019 over modellrektangelet (ett export-kall, EPSG:3857), bare til kontroll, lagres ikke."""
    import urllib.request, importlib.util
    spec = importlib.util.spec_from_file_location('hent', os.path.join(ROT, 'rapport', 'hoyder', 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    W, H = int((x1 - x0) / mpp), int((y1 - y0) / mpp)
    X0, Y0, S = hent.X0, hent.Y0, hent.S
    bb = f'{X0 + x0 * S},{Y0 + y0 * S},{X0 + x1 * S},{Y0 + y1 * S}'
    q = f'{KOMMUNE}Ortofoto_2019_Mosaikk/MapServer/export?bbox={bb}&bboxSR=3857&imageSR=3857&size={W},{H}&format=jpg&f=image'
    try:
        data = urllib.request.urlopen(q, timeout=60).read()
        im = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        return cv2.resize(im, (W, H)) if im is not None else np.full((H, W, 3), 200, np.uint8)
    except Exception:
        return np.full((H, W, 3), 200, np.uint8)


def hoydebilde(nd):
    hb = cv2.applyColorMap((np.clip(np.nan_to_num(nd, nan=0) / 15.0, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    return hb


def kildepaneler(x, y, rad=22.0, mpp=0.08, grp=None, merk=None):
    """ortofoto 2024, kommunekartet, DOM−DTM (Kartverket, i dag), DOM−DTM 2015 (kommunen), ortofoto 2019."""
    import flater as FL, kommunekart as KK, datalag
    from shapely.geometry import Point
    hent_2015()
    x0, y0, x1, y1 = x - rad, y - rad, x + rad, y + rad
    orto, px = FL.ortofoto(x0, y0, x1, y1, mpp)
    kk = kommunekart_utsnitt(x0, y0, x1, y1, mpp)
    nd = ndh(x0, y0, x1, y1, mpp); hb = hoydebilde(nd)
    nd15 = ndh(x0, y0, x1, y1, mpp, 'dom2015', 'dtm2015'); hb15 = hoydebilde(nd15)
    o19 = ortofoto_2019(x0, y0, x1, y1, mpp)
    def P(pts): return np.array([px(*q) for q in pts], np.int32)
    d = datalag.alle(); K = [k for k in KK.omriss() if k.distance(Point(x, y)) < rad * 1.6]
    for panel in (orto, kk, hb, hb15, o19):
        for b in d['bygg']:
            c = P(b['p'])
            if c[:, 0].max() < 0 or c[:, 1].max() < 0 or c[:, 0].min() > panel.shape[1] or c[:, 1].min() > panel.shape[0]: continue
            col = (150, 150, 150) if b.get('skjul') else (60, 60, 255)
            cv2.polylines(panel, [c], True, col, 1 if b.get('skjul') else 2)
            cc = c.mean(0).astype(int); cv2.putText(panel, b['id'].replace('bnr-193', '').replace('bnr-', ''), tuple(cc), 0, 0.45, col, 1, cv2.LINE_AA)
        for k in K:      # kommunekartets omriss oppå modellen (gult, tynt)
            cv2.polylines(panel, [P(np.array(k.exterior.coords))], True, (0, 230, 255), 1, cv2.LINE_AA)
        if grp:
            for k_, col, t in (('z0', (255, 255, 0), 1), ('z7', (255, 0, 255), 1)):
                if grp.get(k_): cv2.polylines(panel, [P(grp[k_])], True, col, t, cv2.LINE_AA)
            if len(grp.get('bunnkant', [])) > 1: cv2.polylines(panel, [P(grp['bunnkant'])], False, (255, 255, 0), 3, cv2.LINE_AA)
        if merk:
            for q in merk: cv2.circle(panel, tuple(int(v) for v in px(*q)), 6, (0, 0, 255), 2)
    for p in json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json')))['punkter']:
        mx, my = datalag.til_modell(*p['lonlat'])
        if x0 <= mx <= x1 and y0 <= my <= y1:
            q = tuple(int(v) for v in px(mx, my))
            for panel in (orto, kk):
                cv2.circle(panel, q, 4, (255, 0, 255), -1)
                cv2.putText(panel, f"{p['bygningsnummer']} {p.get('status', '')}", (q[0] + 5, q[1] - 5), 0, 0.4, (255, 0, 255), 1, cv2.LINE_AA)
    for a_, b_ in ((nd, hb), (nd15, hb15)):
        for gx in np.arange(x0 + 2, x1, 4.0):
            for gy in np.arange(y0 + 2, y1, 4.0):
                c, r = px(gx, gy)
                if 0 <= int(r) < a_.shape[0] and 0 <= int(c) < a_.shape[1] and not np.isnan(a_[int(r), int(c)]):
                    cv2.putText(b_, f"{a_[int(r), int(c)]:.0f}", (int(c) - 6, int(r) + 4), 0, 0.33, (255, 255, 255), 1)
    return orto, kk, hb, hb15, o19


def tittel(im, t):
    cv2.rectangle(im, (0, 0), (im.shape[1], 22), (255, 255, 255), -1)
    cv2.putText(im, t, (5, 16), 0, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return im


def ark(navner=None):
    import kontroll as KO
    G = json.load(open(os.path.join(UT, 'grupper.json'), encoding='utf8'))
    os.makedirs(UT, exist_ok=True)
    for r in G:
        n = r['tegning']
        if navner and n not in navner: continue
        if 'fot' not in r['plass']: continue
        im, _ = KO.tegning_bilde(n, R)
        far = cv2.imread(os.path.join(KO.ARB, f'{n}-farge.png'))
        U = gruppe_poly(n, r)
        bx0, by0, bx1, by1 = U.bounds; m = 45
        c0, r0 = int(max(0, (bx0 - m) * R)), int(max(0, (by0 - m) * R)); c1, r1 = int(min(im.shape[1], (bx1 + m) * R)), int(min(im.shape[0], (by1 + m) * R))
        a = im[r0:r1, c0:c1, ::-1].copy()
        b = far[r0:r1, c0:c1].copy() if far is not None else np.full_like(a, 255)
        pts = ((np.array(U.exterior.coords) * R) - [c0, r0]).astype(np.int32)
        for pnl in (a, b): cv2.polylines(pnl, [pts], True, (0, 0, 255), 2)
        S = 520
        def sk(p): f = S / max(p.shape[:2]); return cv2.resize(p, None, fx=f, fy=f)
        a, b = sk(a), sk(b)
        def pad(p): q = np.full((S, S, 3), 255, np.uint8); q[:p.shape[0], :p.shape[1]] = p; return q
        x, y = r['plass']['midt']
        o, k, h, h15, o19 = [cv2.resize(p, (S, S)) for p in kildepaneler(x, y, grp=r['plass'])]
        rad1 = np.hstack([tittel(pad(a), f"{n} gruppe {r['nr']}: tegningen ({r['areal_pt2']} pt2)"), tittel(pad(b), 'modellen, samme projeksjon'),
                          tittel(o, f"ortofoto 2024 ({x:.0f}, {y:.0f})  gult FKB, rodt modell")])
        rad2 = np.hstack([tittel(k, 'kommunekartet'), tittel(h, 'DOM-DTM Kartverket (i dag)'), tittel(h15, 'DOM-DTM 2015 (kommunen)')])
        rad3 = np.hstack([tittel(o19, 'ortofoto 2019 (kommunen)'), tittel(np.full((S, S, 3), 255, np.uint8), f"dom: {r.get('dom') or '-'}"), np.full((S, S, 3), 255, np.uint8)])
        if r.get('grunn'):
            ord_ = r['grunn'].split(); lin = [''];
            for w in ord_:
                if len(lin[-1]) + len(w) > 60: lin.append('')
                lin[-1] += w + ' '
            for i, l in enumerate(lin[:22]): cv2.putText(rad3, l, (S + 8, 50 + 20 * i), 0, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        f = os.path.join(UT, f"{n}-{r['nr']}.jpg")
        cv2.imwrite(f, np.vstack([rad1, rad2, rad3]), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(f)


def se(x, y, rad=22.0, navn=None):
    o, k, h, h15, o19 = kildepaneler(x, y, rad)
    os.makedirs(UT, exist_ok=True)
    f = os.path.join(UT, f"se-{navn or f'{x:.0f}_{y:.0f}'}.jpg")
    cv2.imwrite(f, np.vstack([np.hstack([tittel(o, f'ortofoto 2024 ({x:.0f}, {y:.0f})'), tittel(k, 'kommunekartet'), tittel(o19, 'ortofoto 2019')]),
                              np.hstack([tittel(h, 'DOM-DTM i dag'), tittel(h15, 'DOM-DTM 2015'), np.full_like(o, 255)])]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'liste'
    if cmd == 'liste': liste()
    elif cmd == 'ark': ark(sys.argv[2:] or None)
    elif cmd == 'se': se(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]) if len(sys.argv) > 4 else 22.0, sys.argv[5] if len(sys.argv) > 5 else None)
