#!/usr/bin/env python3
"""Vannet mot virkeligheten: Glomma, vollgravene, kaikantene ved Toldbodgaten og fergeleiet, Isegran og hvordan vannet møter land,
målt mot Fredrikstad kommunes ortofoto 2024 (samme fliser og samme transform som verktoy/flater.py).

    python3 verktoy/vann.py hent        ortofotoflisene over hele kartrammen (flater.hent_fliser, samme rutenett, bare flere fliser)
    python3 verktoy/vann.py maske       vann i ortofotoet -> kilder/ortofoto-2024/vannfasit.png (fasiten regel 16 måler mot; ikke i git)
    python3 verktoy/vann.py lag         data/vann.json på nytt: OSM-grunnlaget (kilder/vann-osm.json) rettet mot fasiten, med fast id (vn-),
                                        kanttype per kant (k = kai/mur/brygge, n = naturlig) og data/vannfelt.json til tegnekoden
    python3 verktoy/vann.py kontroll    kontrollark per strekning før/etter (rapport/vann/<strekning>-<for|etter>.jpg, ikke i git)
                                        og tallene (rapport/vann/avvik.json)

Ortofotoet er BARE kontroll (lisensen er ikke avklart). Ingen piksel fra det vises i kartet; strandlinja tegnes i kartets egen stil.
Det som ikke kan måles i fotoet (kanttype der fotoet tar feil, vann under broer), står for hånd i kilder/vann-maalt.json med grunn.
"""
import json, math, os, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag  # noqa: E402
import flater   # noqa: E402

RAMME = 860                              # kartrammen: så langt kartet lar seg dra (src/13_kart.js: GRENSE 560 + 300)
OMRAADE = (-960, -960, 1088, 1088)       # flisene som dekker rammen, på flater.py sitt rutenett (256 m fra -448)
MPP = 0.25                               # m per piksel i målingene (flisene er 0,125; halvparten holder for strandlinja)
N = int((OMRAADE[2] - OMRAADE[0]) / MPP)
FASIT = os.path.join(flater.ORTO, 'vannfasit.png')
OSM = os.path.join(ROT, 'kilder', 'vann-osm.json')
MAALT = os.path.join(ROT, 'kilder', 'vann-maalt.json')
ANKER = os.path.join(ROT, 'kilder', 'vann-anker.json')
REG = os.path.join(ROT, 'kilder', 'id-register.txt')

# strekningene eieren spurte om (modellmeter x0, y0, x1, y1)
STREKNINGER = {
    'glomma-vest': (-300, -420, -60, 140),     # Gamlebyens vestside mot Glomma: Toldbodgaten, kaia, Kongens Torv
    'fergeleiet': (-110, 100, 130, 300),       # Færgeporten og ferjekaia, fergeleiet over til Cicignon
    'vollgrav-nord': (150, -40, 460, 420),     # den nordøstre vollgraven, Vindebroen
    'vollgrav-sor': (-280, -440, 300, -60),    # den søndre vollgraven, Kronværket-siden
    'isegran': (-720, -200, -280, 230),        # øya, båthavna og kanalen på vestsiden
}


def til_px(x, y):
    return (x - OMRAADE[0]) / MPP, (OMRAADE[3] - y) / MPP


def fra_px(c, r):
    return OMRAADE[0] + c * MPP, OMRAADE[3] - r * MPP


def hent():
    flater.hent_fliser((-RAMME, -RAMME, RAMME, RAMME))


_M = None


def mosaikk():
    """Ortofotoet over OMRAADE, 0,25 m/px, rad 0 = nord (flater.ortofoto: samme fliser, samme transform)."""
    global _M
    if _M is None:
        _M, _ = flater.ortofoto(*OMRAADE, mpp=MPP)
    return _M


def tegn(vann, n=N):
    """Vannpolygonene (med hull) som maske i målenettet."""
    import cv2, numpy as np
    O = np.zeros((n, n), np.uint8)
    P = lambda p: np.round(np.array([til_px(x, y) for x, y in p]) * 8).astype(np.int32)
    for w in vann:
        if w.get('skjul'):
            continue
        cv2.fillPoly(O, [P(w['p'])], 1, shift=3)
        for h in w.get('h', []):
            if len(h) > 2:
                cv2.fillPoly(O, [P(h)], 0, shift=3)
    return O


def osm():
    """Grunnlaget fra OpenStreetMap, slik data/vann.json var før 27.10.2026 (natural=water)."""
    return json.load(open(OSM, encoding='utf8'))


def maalt():
    return json.load(open(MAALT, encoding='utf8')) if os.path.exists(MAALT) else {'vann': [], 'kant': []}


# ---- fasiten: vann i ortofotoet ----
MORK = 72        # HSV-verdi: vannet i april 2024 er mørkt brunt (målt 27.10: median 55, 95 % under 68); land rundt median 148
GLATT_SD = 7.0   # standardavvik i et vindu på 2,25 m: vannflaten er glatt, skygger på land har tekstur
MIN_OMR = 150    # m²: mindre mørke flekker er skygger, ikke vann
BAAT = 2500      # m²: land omgitt av vann mindre enn dette er båter, flytebrygger og glimt i krusninger (vannet går under dem)
GLIMT = 1.0      # m (radius): lyse prikker mindre enn dette er solglimt, ikke land
MORK_GRUMS = 92  # grumsete vann i vollgravene (alger, grunt): målt 76–78, siv og gress 109–151
GRONN = (36, 95, 45)   # HSV-tone og metning for skygge på gress og løv (vannet: tone 0–30, også det grumsete 24–28)
UTE = 4.0        # m: lenger ut på land enn dette fra OSM-vannet er mørke flater trær og skygger (vann OSM ikke kjenner, måles for hånd)
NAER = 5.0     # m: så langt fra OSM-vannet godtas det grumsete vannet
BRYGGE = 3.0     # m (radius): båter og brygger smalere enn ca. 6 m som stikker ut fra land, er vann i kartet (bare der OSM har vann)
INNE = 12.0     # m: lenger enn dette inne i OSM-vannet regnes alt som vann (krusninger og solglimt midt i elva er ikke land)
KANT_VOKS = 2.0  # m: så langt vokser vannet tilbake gjennom mørke piksler mot kanten (teksturvinduet og skyggen av kaimuren)


def maske():
    """Vann i fotoet: mørke, glatte, sammenhengende flater der OSM sier det er vann (OSM velger komponenten, kanten kommer fra fotoet).
    Båter, flytebrygger og glimt fylles. Vann under broer og brygger som fotoet ikke ser, legges til fra kilder/vann-maalt.json."""
    import cv2, numpy as np
    M = mosaikk()
    el = lambda meter: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * meter / MPP) | 1,) * 2)
    # solglimt i krusningene er små lyse prikker: en gråtone-åpning (1,5 m) tar dem bort før terskel og tekstur
    V = cv2.morphologyEx(cv2.cvtColor(M, cv2.COLOR_BGR2HSV)[..., 2], cv2.MORPH_OPEN, el(GLIMT)).astype(np.float32)
    m = cv2.blur(V, (9, 9)); sd = np.sqrt(np.maximum(cv2.blur(V * V, (9, 9)) - m * m, 0)); del m
    Vm = cv2.medianBlur(V.astype(np.uint8), 5); del V
    O = tegn(osm())
    naer = cv2.dilate(O, el(NAER))   # grumsete, grunt vann (vollgravene) godtas lysere, men bare nær vannet OSM kjenner
    H = cv2.medianBlur(cv2.cvtColor(M, cv2.COLOR_BGR2HSV)[..., 0], 5); S = cv2.medianBlur(cv2.cvtColor(M, cv2.COLOR_BGR2HSV)[..., 1], 5)
    gronn = (H >= GRONN[0]) & (H <= GRONN[1]) & (S >= GRONN[2]); del H, S   # skygge av trær på gress er grønn, vannet er brunt
    kand = (((Vm <= MORK) | ((Vm <= MORK_GRUMS) & (naer > 0))) & (sd <= GLATT_SD) & ~gronn).astype(np.uint8); del sd, naer
    mork = ((Vm <= MORK) & ~gronn).astype(np.uint8); del Vm, gronn   # til å vokse vannet helt inn til kanten (under)
    kand = cv2.morphologyEx(kand, cv2.MORPH_CLOSE, el(0.75))   # sømmer i ortofotomosaikken og tynne linjer (ferjewiren)
    kand = cv2.morphologyEx(kand, cv2.MORPH_OPEN, el(0.5))
    n, lab, st, _ = cv2.connectedComponentsWithStats(kand, connectivity=4)
    treff = np.bincount(lab.ravel(), weights=O.ravel(), minlength=n)
    behold = (treff / np.maximum(st[:, cv2.CC_STAT_AREA], 1) > 0.5) & (st[:, cv2.CC_STAT_AREA] * MPP * MPP >= MIN_OMR)
    behold[0] = False
    W = behold[lab].astype(np.uint8); del lab, kand
    W &= cv2.dilate(O, el(UTE))      # mørke trær og skygger på land: fotoet flytter strandlinja høyst UTE m ut fra OSM
    W |= cv2.erode(O, el(INNE))
    # teksturtesten (vindu 2,25 m) spiser vannet ca. 1 m inn fra en lys kai, og skyggen av kaimuren er mørk, men ikke glatt.
    # Vannet vokser derfor tilbake gjennom mørke piksler, høyst KANT_VOKS m (målt 27.10 ved Toldbodgaten: fasiten lå 1,5–2 m ute)
    k3 = np.ones((3, 3), np.uint8)
    for _ in range(int(KANT_VOKS / MPP)):
        W |= cv2.dilate(W, k3) & mork
    del mork
    W &= cv2.dilate(O, el(UTE))
    W |= baater(M, O, W)
    W |= skjult() & O
    W |= cv2.morphologyEx(W, cv2.MORPH_CLOSE, el(BRYGGE)) & O   # båter og brygger ut fra land: vannet går under dem
    land = 1 - W
    n, lab, st, _ = cv2.connectedComponentsWithStats(land, connectivity=4)
    smaa = st[:, cv2.CC_STAT_AREA] * MPP * MPP < BAAT
    kant = np.zeros(n, bool); kant[np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))] = True
    W[(smaa & ~kant)[lab] & (land > 0)] = 1; del lab, land
    for f in maalt()['vann']:   # målt for hånd: vann fotoet ikke ser (under broer, smale grøfter i sivet), eller land fotoet tror er vann
        if 'linje' in f:          # grøft: midtlinje og bredde
            from shapely.geometry import LineString
            f = dict(f, p=list(LineString(f['linje']).buffer(f['bredde'] / 2, cap_style=2, join_style=2).exterior.coords))
        P = np.round(np.array([til_px(x, y) for x, y in f['p']]) * 8).astype(np.int32)
        cv2.fillPoly(W, [P], 1 if f['vann'] else 0, shift=3)
    cv2.imwrite(FASIT, W * 255, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    print('fasit ->', os.path.relpath(FASIT, ROT), f'{W.sum() * MPP * MPP / 1e6:.3f} km² vann i ortofotoet (hele flisområdet)')


BAAT_LYS = (215, 45)   # HSV-verdi minst / metning høyst: hvite skrog (målt 27.10: 240–255); kaidekket ved fergeleiet når 190–210
BAAT_MAKS = 300.0      # m²: en lys flekk større enn dette er kai, plass eller tak, ikke båt


def baater(M, O, W):
    """Båter som ligger fortøyd langs land og brygger, er vann i kartet (vannet går under dem). Fotoet ser dem som land
    fordi de henger sammen med land; de kjennes på at de er hvite, små og ligger der OSM har vann. Skyggen og presenningen
    rundt tas med av en lukking på 1 m. Gir masken som legges til vannet (bare innenfor OSM-vannet)."""
    import cv2, numpy as np
    el = lambda meter: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * meter / MPP) | 1,) * 2)
    hsv = cv2.cvtColor(M, cv2.COLOR_BGR2HSV)
    lys = ((hsv[..., 2] >= BAAT_LYS[0]) & (hsv[..., 1] <= BAAT_LYS[1])).astype(np.uint8); del hsv
    lys &= cv2.dilate(O, el(1.0)) & (1 - W)
    n, lab, st, _ = cv2.connectedComponentsWithStats(lys, connectivity=8)
    liten = st[:, cv2.CC_STAT_AREA] * MPP * MPP <= BAAT_MAKS; liten[0] = False
    ved = np.bincount(lab.ravel(), weights=cv2.dilate(W, el(1.0)).ravel(), minlength=n) > 0   # flyter: rører vannet
    liten &= ved
    B = liten[lab].astype(np.uint8); del lab
    B = cv2.morphologyEx(B, cv2.MORPH_CLOSE, el(1.0))
    B = cv2.dilate(B, el(0.75))      # skyggen og fenderne rundt skroget
    return B & O


LUTNING = 0.15    # m sideveis per m høyde: hus lener ut i ortofotoet (ikke sant ortofoto); sett 27.10 ved lagerbygget sør for Toldbodgaten: taket 1–2 m ut over vannet
LUTNING_MAKS = 3.0


def skjult():
    """Der fotoet ikke ser vannkanten: under trekronene (data/traer.json) og under taket på hus som lener ut over vannet
    (data/bygg.json, fotavtrykket utvidet med LUTNING * høyde). Der gjelder OSM-kanten; fotoet tar den ikke bort."""
    import cv2, numpy as np
    S = np.zeros((N, N), np.uint8)
    D = datalag.alle()
    for t in D['traer']:
        c, r = til_px(t[0], t[1])
        cv2.circle(S, (int(round(c * 8)), int(round(r * 8))), int(round(t[2] / MPP * 8)), 1, -1, shift=3)
    for b in D['bygg']:
        if b.get('skjul') or len(b.get('p') or []) < 3:
            continue
        u = min(LUTNING * (b.get('h') or 6), LUTNING_MAKS); pad = int(u / MPP) + 2
        Pf = np.array([til_px(x, y) for x, y in b['p']])
        c0, r0 = np.floor(Pf.min(0)).astype(int) - pad; c1, r1 = np.ceil(Pf.max(0)).astype(int) + pad
        if c1 <= 0 or r1 <= 0 or c0 >= N or r0 >= N:
            continue
        m = np.zeros((r1 - r0, c1 - c0), np.uint8)
        cv2.fillPoly(m, [np.round((Pf - [c0, r0]) * 8).astype(np.int32)], 1, shift=3)
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * u / MPP) | 1,) * 2))
        a, b_, c, d = max(r0, 0), max(c0, 0), min(r1, N), min(c1, N)
        S[a:c, b_:d] |= m[a - r0:c - r0, b_ - c0:d - c0]
    return S


def les_fasit():
    import cv2
    if not os.path.exists(FASIT):
        return None
    return (cv2.imread(FASIT, cv2.IMREAD_GRAYSCALE) > 127).astype('uint8')


def ramme():
    import numpy as np
    R = np.zeros((N, N), np.uint8)
    (c0, r0), (c1, r1) = til_px(-RAMME, RAMME), til_px(RAMME, -RAMME)
    R[int(r0):int(r1), int(c0):int(c1)] = 1
    return R


def dekning(K, T, R):
    """(andel av kartets vann som er vann i fotoet, andel av fotoets vann kartet dekker), innen R."""
    kt = int((K & T & R).sum())
    return kt / max(int((K & R).sum()), 1), kt / max(int((T & R).sum()), 1)


def kantavvik(K, T, boks=None):
    """Avstand i meter fra kartets strandlinje til fotoets: median, 90- og 99-persentil (innen boks)."""
    import cv2, numpy as np
    if boks:
        (c0, r0), (c1, r1) = til_px(boks[0], boks[3]), til_px(boks[2], boks[1])
        sl = (slice(int(r0), int(r1)), slice(int(c0), int(c1)))
        K, T = K[sl], T[sl]
    kk = lambda m: m - cv2.erode(m, np.ones((3, 3), np.uint8))
    kK = kk(K)
    kK[:2, :] = kK[-2:, :] = kK[:, :2] = kK[:, -2:] = 0       # kanten av utsnittet er ikke strandlinje
    d = cv2.distanceTransform(1 - kk(T), cv2.DIST_L2, 5)[kK > 0] * MPP
    if not len(d):
        return None
    return [round(float(np.percentile(d, q)), 2) for q in (50, 90, 99)]


# ---- lag: OSM rettet mot fasiten, med fast id og kanttype ----
GLATT = 1.0          # m: avvik smalere enn dette er støy i begge kildene og rettes ikke
BRO_FLATE = 400.0    # m²: en stripe som deler vannet i to store flater (bro, demning) tas ikke bort
MIN_RETT = 10.0      # m²: minste flate som legges til eller tas bort
MIN_FLATE = 100.0    # m²: mindre biter som blir igjen, tas ikke med
FORENKLE = 0.35      # m: toleranse når kanten gjøres om fra piksler til linje


def _ider(polys):
    """Faste id-er (vn-<løpenummer>), registrert i kilder/id-register.txt som bygg og flater. Hver id har et ankerpunkt i
    kilder/vann-anker.json; en flate som lages på nytt får id-en til ankeret som ligger i den. En id gjenbrukes aldri."""
    from shapely.geometry import Point
    anker = json.load(open(ANKER, encoding='utf8')) if os.path.exists(ANKER) else {}
    reg = [l.strip() for l in open(REG, encoding='utf8') if l.strip()]
    n = max([int(i[3:]) for i in reg if i.startswith('vn-')], default=0)
    ider, brukt, nye = [None] * len(polys), set(), []
    rekkefolge = sorted(range(len(polys)), key=lambda i: -polys[i].area)   # store flater velger først
    for i in rekkefolge:
        pg = polys[i]
        treff = [k for k, a in anker.items() if k not in brukt and pg.contains(Point(a))] or \
                [k for k, a in anker.items() if k not in brukt and pg.distance(Point(a)) < 20]
        if treff:
            ider[i] = treff[0]
        else:
            n += 1; ider[i] = f'vn-{n}'; a = pg.representative_point()
            anker[ider[i]] = [round(a.x, 1), round(a.y, 1)]; nye.append(ider[i])
        brukt.add(ider[i])
    json.dump(anker, open(ANKER, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    if nye:
        open(REG, 'a', encoding='utf8').write('\n'.join(nye) + '\n')
    borte = sorted(set(anker) - brukt)
    return ider, borte


def _ringer(pg):
    from shapely.geometry.polygon import orient
    pg = orient(pg, 1.0)   # ytre ring mot klokka, hull med klokka: land ligger alltid til høyre for kanten
    r = lambda c: [[round(x, 2), round(y, 2)] for x, y in list(c.coords)[:-1]]
    return r(pg.exterior), [r(h) for h in pg.interiors]


def kanttyper(ring, hand):
    """Én bokstav per kant (kant i går fra ring[i] til ring[i+1]): k = kai/mur/brygge (rett, hard kant), n = naturlig (gress, stein, siv).
    Kanttypen settes per strekning for hånd (kilder/vann-maalt.json «kant»: et belte langs en linje, sjekket mot ortofotoet);
    alt annet er naturlig. (27.10: en automatisk måling av «hard flate på land» tok vissent aprilgress, grusstier og tak
    for kai i vollgravene og bommet på halve Toldbodkaia; den ble forkastet.)"""
    import numpy as np
    from shapely.geometry import Point
    P = np.array(ring, float); Q = np.roll(P, -1, 0)
    k = np.zeros(len(ring), bool)
    for b in hand:
        for i in range(len(ring)):
            if b['geo'].distance(Point(*((P[i] + Q[i]) / 2))) <= b['bredde'] / 2:
                k[i] = b['kant'] == 'k'
    return ''.join('k' if x else 'n' for x in k)


def lag():
    import cv2, numpy as np
    from shapely.geometry import Polygon, LineString, box
    from shapely.ops import unary_union
    raa = osm(); T = les_fasit()
    if T is None:
        raise SystemExit('fasiten mangler: kjør python3 verktoy/vann.py hent og maske')
    L = np.zeros((N, N), np.int32)
    Pp = lambda p: np.round(np.array([til_px(x, y) for x, y in p]) * 8).astype(np.int32)
    for i, w in enumerate(raa):
        cv2.fillPoly(L, [Pp(w['p'])], i + 1, shift=3)
        for h in w.get('h', []):
            cv2.fillPoly(L, [Pp(h)], 0, shift=3)
    O = (L > 0).astype(np.uint8)
    R = ramme()
    el = lambda m: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(m / MPP) | 1,) * 2)
    fjern = cv2.morphologyEx(O & (1 - T) & R, cv2.MORPH_OPEN, el(GLATT))
    legg = cv2.morphologyEx(T & (1 - O) & R, cv2.MORPH_OPEN, el(GLATT))
    tall = {'fjernet_m2': 0, 'lagt_til_m2': 0, 'beholdt_bro_m2': 0}
    for navn, m in (('fjern', fjern), ('legg', legg)):
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
        stor = st[:, cv2.CC_STAT_AREA] * MPP * MPP >= MIN_RETT; stor[0] = False
        if navn == 'fjern':   # en stripe som deler vannet i to (bro, demning) blir stående: broene ligger oppå vannet i kartet
            for j in np.nonzero(stor)[0]:
                x, y, w_, h_ = st[j, :4]; pad = int(50 / MPP)
                r0, r1, c0, c1 = max(0, y - pad), min(N, y + h_ + pad), max(0, x - pad), min(N, x + w_ + pad)
                k = lab[r0:r1, c0:c1] == j; o = O[r0:r1, c0:c1]
                store = lambda b: int((cv2.connectedComponentsWithStats(b, connectivity=4)[2][1:, cv2.CC_STAT_AREA] * MPP * MPP >= BRO_FLATE).sum())
                if store((o & ~k).astype(np.uint8)) > store(o):
                    stor[j] = False; tall['beholdt_bro_m2'] += round(float(st[j, cv2.CC_STAT_AREA] * MPP * MPP), 1)
        m[:] = stor[lab]
        tall['fjernet_m2' if navn == 'fjern' else 'lagt_til_m2'] = round(float(m.sum() * MPP * MPP))
    Wm = ((O & (1 - fjern)) | legg).astype(np.uint8)
    # nye piksler hører til nærmeste OSM-flate
    _, idx = cv2.distanceTransformWithLabels((L == 0).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    zr, zc = np.nonzero(L)   # DIST_LABEL_PIXEL nummererer nullpikslene i kilden (her L > 0) i radrekkefølge
    tab = np.zeros(len(zr) + 1, np.int32); tab[1:] = L[zr, zc]
    E = tab[idx] * Wm; del idx, zr, zc
    B = box(*[v + s for v, s in zip((-RAMME, -RAMME, RAMME, RAMME), (0.5, 0.5, -0.5, -0.5))])
    Bindre = box(-RAMME + 1, -RAMME + 1, RAMME - 1, RAMME - 1)
    polys, tags = [], []
    for i, w in enumerate(raa):
        src = Polygon(w['p'], [h for h in w.get('h', []) if len(h) > 2]).buffer(0)
        ute = src.difference(Bindre)   # utenfor kartrammen beholdes OSM som det er
        deler = [ute] if not ute.is_empty else []
        m = (E == i + 1).astype(np.uint8)
        if m.any():
            cs, hi = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            f = lambda cc: [fra_px(px + 0.5, py + 0.5) for px, py in cv2.approxPolyDP(cc, FORENKLE / MPP, True)[:, 0]]
            for k, c in enumerate(cs):
                if hi[0][k][3] != -1:
                    continue
                ytre = f(c)
                if len(ytre) < 3:
                    continue
                hull = []; ch = hi[0][k][2]
                while ch != -1:
                    hh = f(cs[ch])
                    if len(hh) > 2 and cv2.contourArea(cs[ch]) * MPP * MPP > 4:
                        hull.append(hh)
                    ch = hi[0][ch][0]
                deler.append(Polygon(ytre, hull).buffer(0).intersection(B))
        g = unary_union([d for d in deler if not d.is_empty])
        for pg in getattr(g, 'geoms', [g]):
            if pg.geom_type == 'Polygon' and pg.area > MIN_FLATE:
                polys.append(pg); tags.append(w['t'])
    ider, borte = _ider(polys)
    hand = [{'geo': LineString(b['linje']) if 'linje' in b else Polygon(b['omraade']), 'bredde': b.get('bredde', 0), 'kant': b['kant']}
            for b in maalt()['kant']]
    vann = []
    for pg, t, idd in sorted(zip(polys, tags, ider), key=lambda z: int(z[2][3:])):
        p, h = _ringer(pg)
        vann.append({'id': idd, 'p': p, 'h': h, 't': t, 'kant': kanttyper(p, hand),
                     'hkant': [kanttyper(r, hand) for r in h], 'kilde': 'OSM rettet mot ortofoto 2024 (verktoy/vann.py lag)'})
    for idd in borte:   # en id slettes aldri: flaten som ikke finnes lenger, står skjult med grunn
        vann.append({'id': idd, 'p': [], 'h': [], 't': {'natural': 'water'}, 'kant': '', 'hkant': [],
                     'skjul': 'verktoy/vann.py: flaten finnes ikke lenger i ortofoto 2024'})
    with open(os.path.join(ROT, 'data', 'vann.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(v, ensure_ascii=False, separators=(',', ':')) for v in vann) + '\n]\n')
    kai = sum(v['kant'].count('k') + sum(x.count('k') for x in v['hkant']) for v in vann)
    print(f"data/vann.json: {len(vann)} flater, {sum(len(v['p']) + sum(map(len, v['h'])) for v in vann)} punkter, {kai} kai-kanter", tall)
    os.makedirs(os.path.join(ROT, 'rapport', 'vann'), exist_ok=True)
    json.dump(tall, open(os.path.join(ROT, 'rapport', 'vann', 'retting.json'), 'w'), indent=1)
    felt(vann)


# ---- vannfeltet: avstand til land (r) og kanttype (g) som tekstur til tegnekoden ----
FELT_MPP = 1.4
FELT_MAKS = 42.0


def felt(vann=None):
    """data/vannfelt.json: r = avstand til land / maks (skumkanten), g = 1 der nærmeste strandkant er kai/mur (rett kant, ikke skum).
    Samme utstrekning som før, så tegnekoden ikke merker noe annet enn den nye kanalen."""
    import cv2, numpy as np, base64
    vann = vann or datalag.alle()['vann']
    gml = datalag.les('vannfelt')
    x0, y0, w, h = gml['x0'], gml['y0'], gml['w'], gml['h']
    W, H = int(round(w / FELT_MPP)), int(round(h / FELT_MPP))
    px = lambda p: np.round(np.array([((x - x0) / FELT_MPP, (y0 + h - y) / FELT_MPP) for x, y in p]) * 8).astype(np.int32)
    M = np.zeros((H, W), np.uint8); K = np.zeros((H, W), np.uint8); Nl = np.zeros((H, W), np.uint8)
    for v in vann:
        if v.get('skjul') or len(v['p']) < 3:
            continue
        cv2.fillPoly(M, [px(v['p'])], 1, shift=3)
        for r in v['h']:
            cv2.fillPoly(M, [px(r)], 0, shift=3)
    for v in vann:
        if v.get('skjul') or len(v['p']) < 3:
            continue
        for r, kt in [(v['p'], v.get('kant', ''))] + list(zip(v['h'], v.get('hkant', []))):
            q = px(r)
            for i in range(len(r)):
                cv2.line(K if kt[i:i + 1] == 'k' else Nl, tuple(map(int, q[i])), tuple(map(int, q[(i + 1) % len(r)])), 1, 2, shift=3)
    d = cv2.distanceTransform(M, cv2.DIST_L2, 5) * FELT_MPP
    R = np.clip(d / FELT_MAKS * 255, 0, 255).astype(np.uint8)
    dk = cv2.distanceTransform(1 - K, cv2.DIST_L2, 5); dn = cv2.distanceTransform(1 - Nl, cv2.DIST_L2, 5)
    G = (cv2.GaussianBlur(((dk < dn) * 255).astype(np.uint8), (0, 0), 1.2) // 16 * 17).astype(np.uint8)   # 16 trinn pakker bedre
    img = np.dstack([np.zeros_like(R), G, R])   # BGR: r = avstand, g = kai
    ok, b = cv2.imencode('.png', img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    with open(os.path.join(ROT, 'data', 'vannfelt.json'), 'w') as f:
        json.dump({'png': 'data:image/png;base64,' + base64.b64encode(b.tobytes()).decode(), 'x0': x0, 'y0': y0, 'w': w, 'h': h,
                   'maks': FELT_MAKS, 'kanaler': 'r = avstand til land / maks, g = 1 der nærmeste strandkant er kai/mur (verktoy/vann.py felt)'},
                  f, separators=(',', ':'))
    print(f'data/vannfelt.json: {W}x{H} px, {len(b) // 1000} kB')


def kontroll():
    """Kontrollark per strekning: ortofotoet med fotoets strandlinje (gul), før (OSM, rød) og etter (data/vann.json:
    kai magenta, naturlig grønn). Bildene inneholder ortofoto og ligger ikke i git; tallene (avvik.json) gjør det."""
    import cv2, numpy as np
    mappe = os.path.join(ROT, 'rapport', 'vann'); os.makedirs(mappe, exist_ok=True)
    M = mosaikk(); T = les_fasit()
    for_ = tegn(osm()); etter_v = datalag.alle()['vann']; etter = tegn(etter_v)
    tall = {}
    for navn, bx in STREKNINGER.items():
        (c0, r0), (c1, r1) = til_px(bx[0], bx[3]), til_px(bx[2], bx[1])
        c0, r0, c1, r1 = map(int, (c0, r0, c1, r1))
        s = 1300 / max(r1 - r0, c1 - c0)
        for tittel, K, vv in (('for', for_, None), ('etter', etter, etter_v)):
            im = cv2.resize(M[r0:r1, c0:c1], None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            cs, _ = cv2.findContours(T[r0:r1, c0:c1].copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(im, [np.round(c * s).astype(np.int32) for c in cs], -1, (0, 230, 255), 1, cv2.LINE_AA)
            if vv is None:
                cs, _ = cv2.findContours(K[r0:r1, c0:c1].copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(im, [np.round(c * s).astype(np.int32) for c in cs], -1, (40, 40, 255), 2, cv2.LINE_AA)
            else:
                for v in vv:
                    if v.get('skjul'):
                        continue
                    for r, kt in [(v['p'], v.get('kant', ''))] + list(zip(v['h'], v.get('hkant', []))):
                        for i in range(len(r)):
                            a = til_px(*r[i]); b = til_px(*r[(i + 1) % len(r)])
                            pa = (int((a[0] - c0) * s), int((a[1] - r0) * s)); pb = (int((b[0] - c0) * s), int((b[1] - r0) * s))
                            cv2.line(im, pa, pb, (255, 0, 255) if kt[i:i + 1] == 'k' else (60, 220, 60), 2, cv2.LINE_AA)
            a = kantavvik(K, T, bx)
            tall.setdefault(navn, {})[tittel] = a
            cv2.rectangle(im, (0, 0), (im.shape[1], 34), (0, 0, 0), -1)
            cv2.putText(im, f"{navn} {'FOR (OSM, rod)' if vv is None else 'ETTER (kai magenta, naturlig gronn)'}: avvik mot ortofoto median {a[0]} m, p90 {a[1]} m, p99 {a[2]} m",
                        (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(im, 'gul = strandlinja i ortofoto 2024 (Fredrikstad kommune, bare kontroll)', (8, im.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 230, 255), 1, cv2.LINE_AA)
            cv2.imwrite(os.path.join(mappe, f'{navn}-{tittel}.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 84])
    R = ramme()
    tall['_rammen'] = {'for': [round(x, 4) for x in dekning(for_, T, R)], 'etter': [round(x, 4) for x in dekning(etter, T, R)],
                       'forklaring': '[andel av kartets vann som er vann i ortofotoet, andel av ortofotoets vann kartet dekker], innen ±860 m',
                       'kantavvik_for': kantavvik(for_ & R, T & R), 'kantavvik_etter': kantavvik(etter & R, T & R)}
    json.dump(tall, open(os.path.join(mappe, 'avvik.json'), 'w'), indent=1)
    print(json.dumps(tall, indent=1))


if __name__ == '__main__':
    kmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'hent': hent, 'maske': maske, 'lag': lag, 'felt': felt, 'kontroll': kontroll}.get(kmd, lambda: print(__doc__))()
