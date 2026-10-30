"""Kontrolløren (30.10): Vegars 2015-tegninger mot 3D-modellen, hus for hus, i NØYAKTIG tegningens projeksjon.

Tegningene (kilder/kvartal-ai/*.ai) er parallellprojeksjoner med loddrett loddrett: bakken går gjennom en affin avbildning og
høyden er en ren loddrett forskyvning. Verktøyet finner den projeksjonen per tegning (ikke ved å gjette en kameravinkel):

  1. kamera:  asimut, helning, målestokk, forskyvning og høydeskala (tegningen kan overdrive høyden) som får modellhusenes
              silhuett og kanter til å falle oppå tegningen. Grovsøk over asimut/helning på silhuetten (IoU mot alt som er
              tegnet), så finjustering på strekene (avstandsbilde). Til slutt en fri affin bakke (6 tall) + høydeskala.
              Registreringskvaliteten måles per hus: hvor langt husets egne kanter må flyttes for å treffe strekene (pt og px).
  2. render:  verktoy/kontroll_iso.mjs tegner den ekte three.js-scenen (ut/enkel/index.html) med denne projeksjonen som
              projeksjonsmatrise: flate farger, id-bilde (byggindeks per piksel), normalbilde. Ingen trær, ingen bakke.
  3. ark:     rapport/kontroll/<tegning>.png: tegningen | modellen (svart strek fra id/normal-sprang, id-etiketter) | oppå
              hverandre (50 %) + differanse.
  4. avvik:   rapport/kontroll/avvik.json: per hus tegningen viser (og per modellhus) omriss-IoU, høydeforhold, takform,
              farger (tegningen 2015 og modellen, som har Street View 2024), vinduer per vegg, dører, arker, piper.

    python3 verktoy/kontroll.py kamera [tegning ...]   rapport/kontroll/_arbeid/<tegning>-kamera.json
    python3 verktoy/kontroll.py render [tegning ...]   (kaller node verktoy/kontroll_iso.mjs)
    python3 verktoy/kontroll.py ark [tegning ...]
    python3 verktoy/kontroll.py avvik
    python3 verktoy/kontroll.py alt

Tegningene er Vegars åndsverk og ligger bare lokalt (kilder/kvartal-ai er ikke i git); arkene i rapport/kontroll er bevis til
kontroll og skal ikke publiseres.
"""
import json, math, os, sys, subprocess, warnings
warnings.filterwarnings('ignore')
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import cv2
import fitz

AI = os.path.join(ROT, 'kilder', 'kvartal-ai')
UT = os.path.join(ROT, 'rapport', 'kontroll')
ARB = os.path.join(UT, '_arbeid')
R = 3.0                      # rasterpiksler per PDF-punkt i arkene og id-bildene
TEGNINGER = ['Kvartal2BITMP', 'Kvartal3', 'Kvartal4BITMP', 'kvartal5', 'kvartal6', 'kvartal7', 'Kvartal8BITMAP', 'Kvartal9',
             'Kvartal10', 'Kvartal11', 'Kvartal12', 'Kvartal13', 'Kvartal14', 'sistekvartal', 'tell', 'Glasshytta', 'kirke', 'Toihuset']


# ---------------------------------------------------------------- data og tegning

_D = None
def data():
    global _D
    if _D is None:
        import datalag
        _D = datalag.alle()
        for x in _D['bygg']:
            for k in ('tak2', 'gavl2', 'vind', 'sk'):
                if isinstance(x.get(k), str):
                    x[k] = json.loads(x[k])
    return _D


def kobling(navn):
    k = json.load(open(os.path.join(ROT, 'kilder', 'kvartal-kobling.json'), encoding='utf8'))
    return next((t for t in k['tegninger'] if t['navn'] == navn), None)


def tegning_bilde(navn, r=R):
    side = fitz.open(os.path.join(AI, navn + '.ai'))[0]
    pm = side.get_pixmap(matrix=fitz.Matrix(r, r), alpha=False)
    return np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3].copy(), side.rect


def tegning_maske(im):
    """Alt som er tegnet (ikke papirhvitt)."""
    return (im.min(axis=2) < 235).astype(np.uint8)


def strek(im):
    return (im.max(axis=2) < 90).astype(np.uint8)


# ---------------------------------------------------------------- projeksjonen

def P_fra_par(p):
    """Parallellprojeksjon som 2x4-matrise (modell x øst, y nord, z opp) -> tegning (PDF-punkt, y ned).
    p = dict(az, el, s, tx, ty, kz) eller dict(A=[[...4],[...4]]) (fri affin bakke + høydeskala)."""
    if 'A' in p:
        return np.array(p['A'], float)
    a, e, s = math.radians(p['az']), math.radians(p['el']), p['s']
    return np.array([[s * math.cos(a), -s * math.sin(a), 0.0, p['tx']],
                     [-s * math.sin(e) * math.sin(a), -s * math.sin(e) * math.cos(a), -s * math.cos(e) * p['kz'], p['ty']]])


def proj(P, x, y, z):
    return P @ np.array([x, y, z, 1.0])


def tak_flater(x):
    """Takflatene som 3D-polygoner (modellmeter), slik kartet tegner dem (h + t * th)."""
    th = x.get('th') or 0.82; h = x['h']
    F = x.get('tak2') or x.get('sk') or []
    ut = [[(q[0], q[1], h + q[2] * th) for q in f] for f in F if len(f) >= 3]
    if not ut:
        ut = [[(q[0], q[1], h) for q in x['p']]]
    return ut


def silhuett_px(P, x, r, shape, verdi=1, M=None):
    """Husets silhuett (vegger + tak) fylt inn i M (rasterpiksler)."""
    if M is None:
        M = np.zeros(shape, np.uint8)
    pts = x['p']; h = x['h']
    g = np.array([proj(P, q[0], q[1], 0) for q in pts]) * r
    t = np.array([proj(P, q[0], q[1], h) for q in pts]) * r
    polys = [g, t] + [np.array([g[k], g[(k + 1) % len(g)], t[(k + 1) % len(g)], t[k]]) for k in range(len(g))]
    polys += [np.array([proj(P, *q) for q in f]) * r for f in tak_flater(x)]
    cv2.fillPoly(M, [np.round(p).astype(np.int32) for p in polys], verdi)
    return M


def kanter_3d(x):
    """Husets kanter i 3D: fotavtrykk, gesims, hjørner og takkanter (alle; skjulte filtreres ikke - grovt mål)."""
    pts = x['p']; h = x['h']; L = []
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        L += [((a[0], a[1], 0), (b[0], b[1], 0)), ((a[0], a[1], h), (b[0], b[1], h)), ((a[0], a[1], 0), (a[0], a[1], h))]
    for f in tak_flater(x):
        for q1, q2 in zip(f, f[1:] + f[:1]):
            L.append((q1, q2))
    return L


def synlige_kanter(P, x, r, shape):
    """Bare kantene som vender mot tegneren: bunn/hjørner på synlige vegger, gesims, takkanter."""
    pts = x['p']; h = x['h']; L = []
    A2 = P[:, :2]
    n_ccw = 1 if _areal(pts) > 0 else -1
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        ux, uy = b[0] - a[0], b[1] - a[1]
        nrm = np.array([uy, -ux]) * n_ccw          # utover
        L.append(((a[0], a[1], h), (b[0], b[1], h)))
        if (A2 @ nrm)[1] > 1e-9:                    # peker ned i bildet = mot tegneren
            L += [((a[0], a[1], 0), (b[0], b[1], 0)), ((a[0], a[1], 0), (a[0], a[1], h)), ((b[0], b[1], 0), (b[0], b[1], h))]
    for f in tak_flater(x):
        if all(abs(q[2] - h) < 0.05 for q in f):
            continue
        for q1, q2 in zip(f, f[1:] + f[:1]):
            if q1[2] > h + 0.05 or q2[2] > h + 0.05:
                L.append((q1, q2))
    return L


def _areal(p):
    return 0.5 * sum(p[k][0] * p[(k + 1) % len(p)][1] - p[(k + 1) % len(p)][0] * p[k][1] for k in range(len(p)))


def kantpunkter(P, L, r, steg=1.5):
    Q = []
    for a, b in L:
        pa, pb = proj(P, *a) * r, proj(P, *b) * r
        n = max(2, int(np.hypot(*(pb - pa)) / steg))
        t = np.linspace(0, 1, n)[:, None]
        Q.append(pa + (pb - pa) * t)
    return np.vstack(Q) if Q else np.zeros((0, 2))


# ---------------------------------------------------------------- kamera

def bygg_i_tegning(navn):
    """Husene tegningen skal vise: koblingen fra kvartal-QA (px2019 i tegningens omriss) + kanthus. Kirka har egen kode."""
    D = data(); BY = {x['id']: x for x in D['bygg']}
    kob = kobling(navn)
    if navn == 'kirke':
        return [x for x in D['bygg'] if x.get('kirke') and not x.get('skjul')]
    ids = list(kob['bygg']) if kob else []
    return [BY[i] for i in ids if i in BY and not BY[i].get('skjul') and len(BY[i]['p']) >= 3]


def _hovedmaske(M):
    """Komponentene som utgjør hovedmotivet (minst 8 % av det tegnede), så nabokvartal-biter i hjørnene ikke drar kameraet."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(M, 8)
    if n <= 1:
        return M
    a = st[1:, cv2.CC_STAT_AREA]; tot = a.sum()
    keep = [j + 1 for j in range(len(a)) if a[j] >= 0.08 * tot]
    return np.isin(lab, keep).astype(np.uint8)


def _iou(A, B):
    i = np.logical_and(A, B).sum(); u = np.logical_or(A, B).sum()
    return i / max(u, 1)


def kamera_fra_trykket(navn):
    """Startkamera: bakken modell -> 2019-trykket (kilder/ai/modell_h_til_2019.npy) -> tegningen (SIFT-koblingen, residual
    under 1 px). Høyden: ortografisk loddrett skala s*cos(helning) fra bakkens singulærverdier."""
    A = np.load(os.path.join(ROT, 'kilder', 'ai', 'modell_h_til_2019.npy'))
    kob = kobling(navn)
    if kob is None:
        return None
    T = np.vstack([np.array(kob['tegning_til_trykk']), [0, 0, 1]]); Ti = np.linalg.inv(T)
    Mg = np.array([[A[0, 0], A[1, 0], A[3, 0]], [A[0, 1], A[1, 1], A[3, 1]], [0, 0, 1]])
    G = (np.diag([72 / 150, 72 / 150, 1]) @ Ti @ Mg)[:2]
    s = np.linalg.svd(G[:, :2], compute_uv=False)
    k = s[0] * math.sqrt(max(0.0, 1 - (s[1] / s[0]) ** 2))
    P = np.array([[G[0, 0], G[0, 1], 0.0, G[0, 2]], [G[1, 0], G[1, 1], -k, G[1, 2]]])
    # koblingen mot trykket kan ha truffet feil kvartal (Kvartal11 lå på Kvartal12 i trykket): startforskyvning satt for hånd (pt)
    if kob.get('startforskyvning'):
        P[:, 3] += np.array(kob['startforskyvning']['d'], float)
    return P


def _endre(P0, v, c0):
    """P0 endret om punktet c0 (tegning): dreiing v[0] grader, målestokk v[1], skjevhet v[2], ulik målestokk v[3],
    forskyvning v[4:6], høydeskala v[6]."""
    rot = math.radians(v[0])
    Mx = v[1] * np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]]) @ np.array([[1 + v[3], v[2]], [0, 1 - v[3]]])
    P = np.zeros((2, 4))
    P[:, :2] = Mx @ P0[:, :2]
    P[:, 2] = np.array([0.0, P0[1, 2] * v[6]])
    P[:, 3] = Mx @ (P0[:, 3] - c0) + c0 + np.array(v[4:6])
    return P


def tegnet_hoydeskala(navn):
    """Tegningens loddrette målestokk (pt per meter) målt på veggene som er koblet for hånd (kilder/fasade-tegning): tegnet
    vegghøyde (venstre og høyre loddkant, PDF-punkt) delt på modellens gesimshøyde h (Kartverket). Medianen; tegningen
    overdriver høyden i forhold til en ortografisk projeksjon, og det er tegningens målestokk som gjelder for overlegget."""
    f = os.path.join(ROT, 'kilder', 'fasade-tegning', navn + '.json')
    if not os.path.exists(f):
        return None, 0
    BY = {x['id']: x for x in data()['bygg']}
    r = []
    for v in json.load(open(f))['vegger']:
        x = BY.get(v['id']); g = v.get('geo') or {}
        if not x or not g.get('H_venstre') or not x.get('h'): continue
        r.append(0.5 * (g['H_venstre'] + g['H_hoyre']) / x['h'])
    return (float(np.median(r)), len(r)) if r else (None, 0)


def _konvolutt(M):
    """Nedre og øvre kant av det tegnede per kolonne (NaN der kolonnen er tom)."""
    har = M.any(axis=0)
    H = M.shape[0]
    bunn = np.where(har, H - 1 - np.argmax(M[::-1], axis=0), np.nan).astype(float)
    topp = np.where(har, np.argmax(M, axis=0), np.nan).astype(float)
    return bunn, topp


# Tegneretningen i de tegningene der omrisset passer best (Kvartal8BITMAP, 10, 12, 13, 2BITMP, kvartal5; første kjøring 30.10):
# bakkedelen av projeksjonen delt på største singulærverdi. Brukes som fast form når en tegning ikke lar seg tilpasse fritt
# (få hus, biter limt inn): da tilpasses bare målestokk og forskyvning.
FORM_REF = np.array([[0.965, 0.19], [0.25, -0.685]])


def tilpass_kamera(navn, logg=print):
    """Projeksjonen per tegning, i to lag:
      1. Felles tegneretning (FORM_REF, samme for alle tegningene: Vegar tegnet dem i ett isometrisk system, 2019-trykket er
         satt sammen av dem), høydeskala K målt på tegningens egne vegger (tegnet vegghøyde / Kartverkets h), og målestokk +
         forskyvning tilpasset omrisset av hovedmotivet (nedre kant per kolonne = husfotene, øvre kant, IoU) og flatekantene.
         Hus fra koblingen som havner utenfor det tegnede (under halve silhuetten på tegnet flate), tas ut og listes.
      2. Hver blokk (hus som står inntil hverandre, tegnet som ett stykke) får sin egen forskyvning (±25 pt) som legger
         blokkens kanter på tegningens flatekanter. Tegningen er frihånd og satt sammen av biter; forskyvningen rapporteres per
         blokk og er ikke en feil i modellen. Innen blokken er alt felles, så avvik i lengde, høyde og form mellom husene står igjen.
    Gir dict(A (felles 2x4), forskyvning {id: [dx, dy] pt}, blokker, mål)."""
    from scipy.optimize import minimize
    from scipy.ndimage import map_coordinates
    import fasade_tegning as FT
    im, rect = tegning_bilde(navn, 1.0)
    H, W = im.shape[:2]
    M_alt = tegning_maske(im)
    Mt = _hovedmaske(M_alt)
    Mtd = cv2.dilate(M_alt, np.ones((7, 7), np.uint8))
    bt, tt = _konvolutt(Mt)
    K, nK = tegnet_hoydeskala(navn)
    logg(f"  høydeskala fra tegnede vegger: {K and round(K, 3)} pt/m ({nK} vegger)" if K else "  høydeskala: ingen koblede vegger, tilpasses")
    dtf = flatekant_avstand(navn, 1.0)
    dtf = np.pad(dtf, ((0, max(0, H - dtf.shape[0])), (0, max(0, W - dtf.shape[1]))), constant_values=20)[:H, :W]
    # tegningens flatekanter som punkter (til kantmålet tegning -> modell), bare i hovedmotivet
    Fk = (dtf < 0.6) & (cv2.dilate(Mt, np.ones((5, 5), np.uint8)) > 0)
    yy_, xx_ = np.nonzero(Fk[::2, ::2]); Qt = np.c_[xx_ * 2, yy_ * 2].astype(float)
    D = data()
    P0 = kamera_fra_trykket(navn)
    if P0 is None:
        P0 = kamera_fra_trykket('Kvartal13')
    s_trykk = float(np.linalg.svd(P0[:, :2], compute_uv=False)[0])
    if not K:      # kirka: ingen lest vegg (og kirkas h i data er 0: formen ligger i b.kirke). Høyden som i de andre tegningene:
        K = 0.71 * s_trykk; nK = 0      # median høyde/bakke-forhold i de 17 andre (30.10)
        logg(f"  høydeskala satt til median av de andre tegningene: {K:.3f} pt/m")
    # kandidatene: koblingen + alle bygg hvis midtpunkt havner på det tegnede med trykkets kamera
    if navn == 'kirke':
        alle = [x for x in D['bygg'] if x.get('kirke') and not x.get('skjul')]
    elif kobling(navn) is None:      # Tøihuset: ingen kobling mot trykket; husene fasadeavlesningen er koblet til
        ft = os.path.join(ROT, 'kilder', 'fasade-tegning', navn + '.json')
        fid = set(v['id'] for v in json.load(open(ft))['vegger']) if os.path.exists(ft) else set()
        alle = [x for x in D['bygg'] if x['id'] in fid and not x.get('skjul')]
    else:
        lov = set(i for i in (kobling(navn) or {}).get('bygg', []))
        Mbig = cv2.dilate(Mt, np.ones((31, 31), np.uint8))
        alle = []
        for x in D['bygg']:
            if x.get('skjul') or len(x['p']) < 3 or x.get('kirke'): continue
            c = proj(P0, *np.mean(x['p'], 0), x['h'] * 0.5)
            inne = 0 <= c[0] < W and 0 <= c[1] < H and Mbig[int(c[1]), int(c[0])]
            if x['id'] in lov or (inne and not (kobling(navn) or {}).get('bare_koblede')):
                alle.append(x)
    # biter (kvartal-kobling.json «biter», 30.10): hus Vegar tegnet som en egen bit et annet sted på arket enn der det felles
    # kameraet legger dem; forskyvningen (pt) er satt for hånd fra arket og finjusteres med blokksøket under
    BIT = {}
    for b_ in (kobling(navn) or {}).get('biter', []):
        for i_ in b_['ids']:
            BIT[i_] = np.array(b_['d'], float)
            if not any(x['id'] == i_ for x in alle):
                alle += [x for x in D['bygg'] if x['id'] == i_ and not x.get('skjul') and len(x['p']) >= 3]
    def Px(P, x):
        if x['id'] in BIT:
            P = P.copy(); P[:, 3] = P[:, 3] + BIT[x['id']]
        return P
    st = dict(B=list(alle))

    def fast_P(w):
        rot = math.radians(w[1])
        Rm = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
        P = np.zeros((2, 4)); P[:, :2] = w[0] * Rm @ FORM_REF; P[:, 3] = w[2:4]
        P[1, 2] = -(K if K else w[4])
        return P

    def sil(P, B):
        M = np.zeros((H, W), np.uint8)
        for x in B:
            silhuett_px(Px(P, x), x, 1.0, (H, W), 1, M)
        return M

    def kant(P, B):
        L = [l for x in B if x['id'] not in BIT for l in synlige_kanter(P, x, 1, None)]
        if not L: L = [l for x in B for l in synlige_kanter(P, x, 1, None)]
        Q = kantpunkter(P, L, 1.0, 1.5)
        a = float(np.mean(np.minimum(map_coordinates(dtf, [Q[:, 1], Q[:, 0]], order=1, mode='constant', cval=20), 6)))
        T = np.ones((H, W), np.uint8)
        for p_, q_ in L:
            pa, pb = proj(P, *p_), proj(P, *q_)
            cv2.line(T, tuple(np.round(pa).astype(int)), tuple(np.round(pb).astype(int)), 0, 1)
        dm = cv2.distanceTransform(T, cv2.DIST_L2, 3)
        b = float(np.mean(np.minimum(map_coordinates(dm, [Qt[:, 1], Qt[:, 0]], order=1, mode='nearest'), 6)))
        return 0.5 * (a + b)

    def mål(w):
        if not 0.85 * s_trykk < w[0] < 1.15 * s_trykk or abs(w[1]) > 6: return 1e3, None
        P = fast_P(w); B = st['B']; Ms = sil(P, B)
        if Ms.sum() < 50: return 1e3, None
        bm, tm = _konvolutt(Ms); beggeb = ~np.isnan(bm) & ~np.isnan(bt)
        if beggeb.sum() < 20: return 1e3, None
        eb = np.abs(bm[beggeb] - bt[beggeb]); et = np.abs(tm[beggeb] - tt[beggeb]); bare = (np.isnan(bm) != np.isnan(bt)).sum()
        f = np.median(eb) + 0.5 * np.mean(np.minimum(eb, 30)) + 0.5 * np.median(et) + 0.25 * np.mean(np.minimum(et, 30)) + 0.5 * bare / max(beggeb.sum(), 1) * 30 + 20 * (1 - _iou(Ms, Mt))
        k = kant(P, B)
        return f + 3 * k, dict(bunn=float(np.median(eb)), topp=float(np.median(et)), iou=float(_iou(Ms, Mt)), bare=int(bare), kant=k, omriss=float(f))

    def start():
        B = st['B']; out = []
        for f in (0.92, 1.0, 1.08):
            w = [s_trykk * f, 0.0, 0.0, 0.0] + ([] if K else [3.5])
            Pq = fast_P(w)
            Ms = sil(Pq, B)
            ys, xs = np.nonzero(Ms)
            if not len(xs):
                pts = np.vstack([np.array([proj(Pq, q[0], q[1], 0) for q in x['p']]) for x in B]); w[2], w[3] = -pts.mean(0) + [W / 2, H / 2]
                Ms = sil(fast_P(w), B); ys, xs = np.nonzero(Ms)
            else:
                pass
            yt, xt = np.nonzero(Mt)
            # samme tyngdepunkt (silhuetten kan ligge delvis utenfor bildet: bruk fotavtrykkenes midtpunkt i stedet)
            pts = np.vstack([np.array([proj(fast_P(w), q[0], q[1], 0) for q in x['p']]) for x in B])
            w[2] += xt.mean() - pts[:, 0].mean(); w[3] += yt.mean() - pts[:, 1].mean() + 0.3 * (K or 3.5) * 6
            out.append(w)
        return out

    def tilpass(starter, merke):
        beste = None
        for w in starter:
            r = minimize(lambda v: mål(v)[0], w, method='Powell', options=dict(xtol=1e-3, ftol=1e-4, maxfev=1200))
            r = minimize(lambda v: mål(v)[0], r.x, method='Nelder-Mead', options=dict(xatol=1e-3, fatol=1e-4, maxfev=500))
            f, info = mål(r.x)
            if info is None: continue
            logg(f"  {merke}: omriss {info['omriss']:.1f}, kant {info['kant']:.2f} pt, nedre kant {info['bunn']:.1f} pt, øvre {info['topp']:.1f} pt, IoU {info['iou']:.3f}")
            if beste is None or f < beste[0]:
                beste = (f, list(map(float, r.x)), info)
        return beste

    beste = tilpass(start(), 'felles')
    utenfor = []
    for runde in (2, 3):
        P = fast_P(beste[1]); inn = []; ut_ = []
        for x in alle:
            Ms = silhuett_px(Px(P, x), x, 1.0, (H, W)); n = Ms.sum()
            (inn if n and (Ms & Mtd).sum() / n >= 0.5 else ut_).append(x)
        if set(x['id'] for x in inn) == set(x['id'] for x in st['B']) or not inn:
            break
        st['B'] = inn; utenfor = [x['id'] for x in ut_]
        logg(f"  runde {runde}: {len(inn)} hus på det tegnede, {len(ut_)} utenfor")
        beste = tilpass([beste[1]], f'felles, runde {runde}')
    P = fast_P(beste[1])
    # blokkene: egen forskyvning
    B = st['B']; bl = FT.blokker(B); BY = {x['id']: x for x in B}
    kob_ids = set((kobling(navn) or {}).get('bygg', []))
    utenfor = [i for i in utenfor if i in kob_ids]          # bare koblede hus som havnet utenfor er verdt å nevne
    forsk = {}; blokker = []
    for ids in bl:
        X = [BY[i] for i in ids]
        Pb = Px(P, X[0])
        Q = np.vstack([kantpunkter(Pb, synlige_kanter(Pb, x, 1, None), 1.0, 1.5) for x in X])
        Ms = sil(P, X); ys, xs = np.nonzero(Ms)
        def sc(d):
            k = float(np.mean(np.minimum(map_coordinates(dtf, [Q[:, 1] + d[1], Q[:, 0] + d[0]], order=1, mode='constant', cval=20), 6)))
            yy, xx = np.clip(ys + int(round(d[1])), 0, H - 1), np.clip(xs + int(round(d[0])), 0, W - 1)
            pres = float(Mtd[yy, xx].mean()) if len(xs) else 0
            return k + 6 * (1 - pres) + 0.03 * math.hypot(*d)
        best = (sc((0, 0)), 0.0, 0.0)
        rad = 8 if X[0]['id'] in BIT else 25          # biter: forskyvningen er satt for hånd, søket bare finjusterer
        for dx in np.arange(-rad, rad + 0.1, 1.0):
            for dy in np.arange(-rad, rad + 0.1, 1.0):
                v = sc((dx, dy))
                if v < best[0]: best = (v, dx, dy)
        _, dx, dy = best
        r = minimize(sc, [dx, dy], method='Nelder-Mead', options=dict(xatol=0.05, fatol=1e-4, maxfev=200))
        dx, dy = (float(r.x[0]), float(r.x[1])) if r.fun < best[0] else (dx, dy)
        k0, k1 = sc((0, 0)), sc((dx, dy))
        for i in ids:
            b0 = BIT.get(i, np.zeros(2))
            forsk[i] = [round(dx + float(b0[0]), 2), round(dy + float(b0[1]), 2)]
        blokker.append(dict(ids=ids, d=[round(dx, 2), round(dy, 2)], kant_for=round(k0, 2), kant_etter=round(k1, 2)))
        logg(f"    blokk {len(ids):2d} hus ({ids[0][-6:]}…): forskyvning {dx:+.1f}, {dy:+.1f} pt, mål {k0:.2f} -> {k1:.2f}")
    U, S, Vt = np.linalg.svd(P[:, :2])
    el = math.degrees(math.asin(min(1.0, S[1] / S[0])))
    az = math.degrees(math.atan2(-P[0, 1], P[0, 0]))
    par = dict(az=round(az, 2), el=round(el, 2), s=round(float(S[0]), 4), K=round(float(-P[1, 2]), 4),
               kz=round(float(-P[1, 2] / (S[0] * math.cos(math.radians(el)))), 3), K_kilde='tegnede vegger' if nK else 'median av de andre tegningene')
    logg(f"  kamera: dreiing {par['az']:.1f}°, helning {par['el']:.1f}°, {par['s']:.3f} pt/m, høyde {par['K']:.3f} pt/m = {par['kz']:.2f} × ortografisk")
    return dict(tegning=navn, par=par, A=P.tolist(), forskyvning=forsk, blokker=blokker, maal=beste[2], bygg=[x['id'] for x in B],
                utenfor_tegningen=utenfor, enhet='PDF-punkt (tegningens side), y ned; [x, y, z, 1] modellmeter -> punkt; forskyvning i pt per bygg')


def P_hus(K, i):
    """Projeksjonen for ett hus: den felles + blokkens forskyvning."""
    P = np.array(K['A'], float).copy()
    d = K.get('forskyvning', {}).get(i)
    if d:
        P[:, 3] += d
    return P


def flatekant_avstand(navn, r=R):
    """Avstandsbilde (PDF-punkt) til nærmeste kant av en farget flate i tegningen (vektorstienes ytre ring: vegger og tak; ikke
    vinduene, som er hull). Det er hjørnene og kantene til husene."""
    import fasade_tegning as FT
    F, rect = FT.flater(navn)
    Wp, Hp = int(rect.width * r) + 1, int(rect.height * r) + 1
    T = np.zeros((Hp, Wp), np.uint8)
    for f in F:
        if min(f['farge']) > 0.97 or f['ytre'].area < 4: continue
        c = np.array(f['ytre'].exterior.coords) * r
        cv2.polylines(T, [np.round(c).astype(np.int32)], True, 1, 1)
    return cv2.distanceTransform(1 - T, cv2.DIST_L2, 5) / r


def hus_forskyvning(navn, K, maks=10.0):
    """Registreringskontroll per hus: avstanden fra husets synlige modellkanter (projisert med tegningens kamera) til nærmeste
    flatekant i tegningen (median, pt og px), og forskyvningen (±maks pt) som ville lagt dem best oppå hverandre.
    Liten avstand = projeksjonen treffer huset. Stor forskyvning = tegningen har huset et annet sted (frihånd) eller
    modellhuset avviker (omriss/høyde) - skilles i avvikslisten."""
    from scipy.ndimage import map_coordinates
    BY = {x['id']: x for x in data()['bygg']}
    dt = flatekant_avstand(navn)
    ut = {}
    for i in K['bygg']:
        x = BY[i]; P = P_hus(K, i)
        Q = kantpunkter(P, synlige_kanter(P, x, 1, None), R, 2.0)
        if len(Q) < 5:
            continue
        def d(dx, dy):
            v = map_coordinates(dt, [Q[:, 1] + dy * R, Q[:, 0] + dx * R], order=1, mode='constant', cval=20)
            return v
        d0 = d(0, 0); best = (float(np.mean(np.minimum(d0, 8))), 0.0, 0.0)
        for dx in np.arange(-maks, maks + 0.1, 0.5):
            for dy in np.arange(-maks, maks + 0.1, 0.5):
                m = float(np.mean(np.minimum(d(dx, dy), 8))) + 0.02 * math.hypot(dx, dy)
                if m < best[0]:
                    best = (m, dx, dy)
        _, dx, dy = best
        d1 = d(dx, dy)
        ut[i] = dict(median_pt=round(float(np.median(d0)), 2), median_px=round(float(np.median(d0)) * R, 1),
                     andel_innen_2pt=round(float(np.mean(d0 <= 2)), 2),
                     beste_forskyvning_pt=[round(float(dx), 2), round(float(dy), 2)], median_etter_pt=round(float(np.median(d1)), 2))
    return ut


def kamera(navn, logg=print, bare_reg=False):
    os.makedirs(ARB, exist_ok=True)
    logg(navn)
    K = les_kamera(navn) if bare_reg else tilpass_kamera(navn, logg)
    K['hus_forskyvning'] = hus_forskyvning(navn, K)
    v = [h['median_pt'] for h in K['hus_forskyvning'].values()]
    K['registrering'] = dict(median_pt=round(float(np.median(v)), 2) if v else None, median_px=round(float(np.median(v)) * R, 1) if v else None,
                             andel_under_3pt=round(float(np.mean(np.array(v) <= 3)), 2) if v else None, R=R)
    logg(f"  registrering: median {K['registrering']['median_pt']} pt ({K['registrering']['median_px']} px ved {R:g} px/pt), "
         f"{K['registrering']['andel_under_3pt']:.0%} av husene innen 3 pt")
    json.dump(K, open(os.path.join(ARB, navn + '-kamera.json'), 'w'), indent=1)
    return K


def les_kamera(navn):
    return json.load(open(os.path.join(ARB, navn + '-kamera.json')))


# ---------------------------------------------------------------- render (den ekte scenen)

def render(navner, logg=print):
    """Lager jobbfila og kjører verktoy/kontroll_iso.mjs mot ut/enkel/index.html (bygges først med python3 bygg.py enkel)."""
    jobb = []
    for n in navner:
        K = les_kamera(n)
        _, rect = tegning_bilde(n, 0.1)
        jobb.append(dict(navn=n, W=int(round(rect.width * R)), H=int(round(rect.height * R)), R=R, A=K['A'], vis=K['bygg'], forsk=K.get('forskyvning', {})))
    jf = os.path.join(ARB, 'jobb.json'); json.dump(jobb, open(jf, 'w'))
    html = os.path.join(ROT, 'ut', 'enkel', 'index.html')
    subprocess.run(['node', os.path.join(ROT, 'verktoy', 'kontroll_iso.mjs'), html, jf, ARB], check=True)


# ---------------------------------------------------------------- bildene fra render

def _les_render(navn, H, W):
    from PIL import Image
    def les(k):
        a = np.array(Image.open(os.path.join(ARB, f'{navn}-{k}.png')).convert('RGB'))
        out = np.full((H, W, 3), 255, np.uint8); h, w = min(H, a.shape[0]), min(W, a.shape[1]); out[:h, :w] = a[:h, :w]
        return out
    f, i, n, ia = les('farge'), les('id'), les('normal'), les('idalle')
    def dek(a):
        bg = (a == 255).all(axis=2)
        idx = a[:, :, 0].astype(np.int32) * 256 + a[:, :, 1]; typ = a[:, :, 2].astype(np.int32)
        idx[bg] = 0; typ[bg] = 0
        return idx, typ
    idx, typ = dek(i); idxa, _ = dek(ia)
    ids = {int(k): v for k, v in json.load(open(os.path.join(ARB, f'{navn}-id.json'))).items()}
    return f, idx, typ, n, idxa, ids


def strek_fra_render(idx, typ, nrm):
    """Svart strek der bygg, flatetype eller normal skifter (som Vegars kantstrek)."""
    e = np.zeros(idx.shape, bool)
    nv = nrm.astype(np.float32) / 127.5 - 1
    for dy, dx in ((0, 1), (1, 0)):
        a = idx[:idx.shape[0] - dy, :idx.shape[1] - dx]; b = idx[dy:, dx:]
        ta = typ[:typ.shape[0] - dy, :typ.shape[1] - dx]; tb = typ[dy:, dx:]
        na = nv[:nv.shape[0] - dy, :nv.shape[1] - dx]; nb = nv[dy:, dx:]
        d = (a != b) | (ta != tb) | (((na * nb).sum(axis=2) < 0.94) & (a > 0))
        e[:e.shape[0] - dy, :e.shape[1] - dx] |= d
    return cv2.dilate(e.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0


def kort_id(i):
    return i.replace('bnr-193', '').replace('bnr-', '') if i.startswith('bnr-193') else i.replace('bnr-', '')


def _font(st):
    from PIL import ImageFont
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, st)
    return ImageFont.load_default()


def etikett_punkter(idx, ids, B_ids):
    """Etikettplass per bygg: punktet lengst inne i husets største synlige bit."""
    ut = {}
    for k in np.unique(idx):
        if k == 0 or ids.get(int(k)) not in B_ids: continue
        m = (idx == k).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        if n <= 1: continue
        j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        mm = (lab == j).astype(np.uint8)
        d = cv2.distanceTransform(mm, cv2.DIST_L2, 3)
        y, x = np.unravel_index(np.argmax(d), d.shape)
        ut[ids[int(k)]] = (int(x), int(y), int(st[j, cv2.CC_STAT_AREA]))
    return ut


def ark(navn, logg=print):
    """rapport/kontroll/<tegning>.png: tegningen | modellen i samme projeksjon (id-etiketter) | 50 % oppå hverandre | differanse."""
    from PIL import Image, ImageDraw
    K = les_kamera(navn)
    im, rect = tegning_bilde(navn, R); H, W = im.shape[:2]
    f, idx, typ, nrm, idxa, ids = _les_render(navn, H, W)
    e = strek_fra_render(idx, typ, nrm)
    mod = f.copy(); mod[e] = (20, 20, 20)
    B_ids = set(K['bygg'])
    lp = etikett_punkter(idx, ids, B_ids)
    over = (im.astype(np.float32) * 0.5 + mod.astype(np.float32) * 0.5).astype(np.uint8)
    Mt = tegning_maske(im) > 0; Mm = idx > 0
    diff = np.full_like(im, 255)
    diff[Mt & Mm] = (205, 205, 205); diff[Mt & ~Mm] = (225, 40, 40); diff[~Mt & Mm] = (40, 90, 230)
    stk = strek(im) > 0; diff[stk] = (60, 60, 60)
    em = e & Mm; diff[em] = (0, 0, 160)
    panel = []
    for bilde, tittel, merk in ((im, 'Tegningen 2015 (Page Black)', False), (mod, 'Modellen i tegningens projeksjon', True),
                                (over, 'Oppå hverandre, 50 %', True), (diff, 'Differanse: rødt = bare tegningen, blått = bare modellen', True)):
        pi = Image.fromarray(bilde); d = ImageDraw.Draw(pi)
        if merk:
            ft = _font(15)
            for i, (x, y, a) in lp.items():
                t = kort_id(i)
                for ox, oy in ((-1, -1), (1, 1), (-1, 1), (1, -1), (0, 2), (2, 0), (-2, 0), (0, -2)):
                    d.text((x + ox, y + oy), t, font=ft, fill=(255, 255, 255), anchor='mm')
                d.text((x, y), t, font=ft, fill=(140, 0, 120), anchor='mm')
        ImageDraw.Draw(pi).text((12, 8), tittel, font=_font(22), fill=(0, 0, 0))
        panel.append(pi)
    sk = 2 / 3
    w2, h2 = int(W * sk), int(H * sk)
    panel = [p_.resize((w2, h2), Image.LANCZOS) for p_ in panel]
    hode = 70
    ut = Image.new('RGB', (2 * w2 + 10, 2 * h2 + 10 + hode), (255, 255, 255))
    for k, p_ in enumerate(panel):
        ut.paste(p_, ((k % 2) * (w2 + 10), hode + (k // 2) * (h2 + 10)))
    d = ImageDraw.Draw(ut); par = K['par']; rg = K.get('registrering', {})
    flytt = [b for b in K.get('blokker', []) if math.hypot(*b['d']) > 3]
    d.text((12, 6), f"{navn}", font=_font(30), fill=(0, 0, 0))
    d.text((12 + 14 * len(navn) + 40, 10), f"kamera: dreiing {par['az']:.1f}°, helning {par['el']:.1f}°, {par['s']:.2f} pt/m bakke, {par['K']:.2f} pt/m høyde ({par['K_kilde']})  ·  "
           f"registrering: husenes kanter {rg.get('median_pt')} pt fra tegningens flatekanter (median), {int(100 * (rg.get('andel_under_3pt') or 0))} % av husene innen 3 pt",
           font=_font(16), fill=(0, 0, 0))
    d.text((12 + 14 * len(navn) + 40, 36), f"{len(B_ids)} modellhus i tegningen · blokker flyttet i tegningen (frihånd, > 3 pt): {len(flytt)} av {len(K.get('blokker', []))}"
           f" · modell {open(os.path.join(ROT, 'VERSJON')).read().strip()} · {__import__('datetime').date.today().isoformat()}", font=_font(16), fill=(60, 60, 60))
    os.makedirs(UT, exist_ok=True)
    ut.save(os.path.join(UT, navn + '.png'), optimize=True)
    logg(f"  {navn}.png {ut.size[0]}x{ut.size[1]}")


# ---------------------------------------------------------------- avvik

def _lab(rgb):
    from skimage.color import rgb2lab
    return rgb2lab(np.array(rgb, float).reshape(1, 1, 3) / 255.0)[0, 0]


def dE(a, b):
    if a is None or b is None: return None
    return float(np.linalg.norm(_lab(a) - _lab(b)))


def kulor(rgb):
    """Grov fargefamilie: grønt er grønt (Vegars regel: tilnærmet riktig holder, feil kulør er ikke lov)."""
    import colorsys
    r, g, b = [v / 255 for v in rgb]
    h, l, s_ = colorsys.rgb_to_hls(r, g, b)
    if l > 0.88: return 'hvit'
    if s_ < 0.14 or (l < 0.2): return 'grå/svart' if l < 0.8 else 'hvit'
    hd = h * 360
    if hd < 18 or hd >= 335: return 'rød' if l > 0.3 else 'brun'
    if hd < 45: return 'oransje/brun' if l > 0.35 else 'brun'
    if hd < 70: return 'gul/beige'
    if hd < 170: return 'grønn'
    if hd < 260: return 'blå'
    return 'lilla/rosa'


def takform_modell(x):
    """Takform fra modellens takflater (tak2/sk, gavl2): sal, valm, halvvalm, pult, flatt, knekk, sammensatt."""
    if x.get('takform') == 'knekk':
        return 'knekk'
    # takformen verktoy/tak_enkel.py bygde taket med (30.10): flatene er laget av nettopp denne formen, så den leses direkte
    # (geometriregelen under tok brannmurer mot naboen for halvvalm og tvers-møne for valm)
    tf = x.get('takform') or ''
    if tf in ('sal', 'valm', 'halvvalm', 'pult', 'flatt'):
        return tf
    if tf.startswith('vinkel:'):
        fs = [f.rstrip('-') for f in tf[7:].split('+')]
        return f"{fs[0]}/sammensatt" if len(set(fs)) == 1 else 'sammensatt'
    F = x.get('tak2') or x.get('sk') or []
    if not F:
        return 'flatt'
    from shapely.geometry import Polygon as Pg
    fot = Pg(x['p']).minimum_rotated_rectangle
    c = np.array(fot.exterior.coords)[:4]
    e1, e2 = c[1] - c[0], c[2] - c[1]
    lang = e1 if np.hypot(*e1) >= np.hypot(*e2) else e2
    lang = lang / max(np.hypot(*lang), 1e-9)
    hel = []; ende_full = 0; ende_halv = 0; tmax = max((q[2] for f_ in F for q in f_), default=0)
    if tmax < 0.3:
        return 'flatt'
    for f_ in F:
        if len(f_) < 3: continue
        A = np.array([[q[0], q[1], 1] for q in f_]); z = np.array([q[2] for q in f_])
        k = np.linalg.lstsq(A, z, rcond=None)[0][:2]
        if np.hypot(*k) < 0.05: continue
        hel.append(f_)
        fall = -k / np.hypot(*k)
        if abs(fall @ lang) > 0.8:                     # flaten faller langs husets lengderetning: endeflate
            if min(q[2] for q in f_) > 0.3 * tmax: ende_halv += 1
            else: ende_full += 1
    gavl = len(x.get('gavl2') or [])
    if len(hel) == 1: return 'pult'
    if ende_full and not gavl: return 'valm'
    if ende_halv or (ende_full and gavl): return 'halvvalm'
    if len(hel) >= 2 and not ende_full: return 'sal' if len(hel) <= 3 else 'sal/sammensatt'
    return 'sammensatt'


def vinduer_modell(x, a, b):
    """Modellens vinduer og dører på veggen a->b (utovernormal), i etasjerader (3 m)."""
    V = x.get('vind') or []
    ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy) or 1
    tx, ty = ux / L, uy / L
    rader = {}; dorer = 0; n = 0
    for v in V:
        vx, vy, vz, vtx, vty, nx, ny = v[:7]
        typ = v[9] if len(v) > 9 else 0
        t = (vx - a[0]) * tx + (vy - a[1]) * ty
        dist = abs(-(vx - a[0]) * ty + (vy - a[1]) * tx)
        if not (-0.3 <= t <= L + 0.3 and dist < 0.8 and abs(nx * (-ty) + ny * tx) > 0.8 or (-0.3 <= t <= L + 0.3 and dist < 0.8 and abs(nx * ty - ny * tx) > 0.8)):
            continue
        if typ in (1, 2): dorer += 1
        else:
            r = int(vz // 3.0); rader[r] = rader.get(r, 0) + 1; n += 1
    return n, [rader[k] for k in sorted(rader)], dorer


def _rader(vs, gap=0.12):
    vs = sorted(vs)
    if not vs: return []
    rad = [[vs[0]]]
    for v in vs[1:]:
        (rad[-1].append(v) if v - rad[-1][-1] < gap else rad.append([v]))
    return [len(r) for r in rad]


def analyser(navn, logg=print):
    """Avvik hus for hus i én tegning. Gir dict(hus: [...], tegnet_uten_modell: [...], modell_uten_tegning: [...])."""
    import fasade_tegning as FT
    from shapely.geometry import Polygon as Pg, box
    from shapely.ops import unary_union
    D = data(); BY = {x['id']: x for x in D['bygg']}
    K = les_kamera(navn)
    im, rect = tegning_bilde(navn, R); H, W = im.shape[:2]
    f, idx, typ, nrm, idxa, ids = _les_render(navn, H, W)
    inv = {v: k for k, v in ids.items()}
    B = [BY[i] for i in K['bygg'] if i in BY]
    F, _ = FT.flater(navn)
    ftf = os.path.join(ROT, 'kilder', 'fasade-tegning', navn + '.json'); FTJ = {}
    if os.path.exists(ftf):
        for v_ in json.load(open(ftf))['vegger']:
            FTJ.setdefault(v_['id'], []).append(v_)
    # flatene rastret i tegneordenen (senere stier ligger oppå)
    Lf = np.full((H, W), -1, np.int32)
    for j, fl in enumerate(F):
        c = (np.array(fl['ytre'].exterior.coords) * R).round().astype(np.int32)
        cv2.fillPoly(Lf, [c], j)
        for h_ in fl['hull']:
            for g_ in getattr(h_, 'geoms', [h_]):
                if g_.geom_type == 'Polygon':
                    cv2.fillPoly(Lf, [(np.array(g_.exterior.coords) * R).round().astype(np.int32)], -1)
    tildelt = {}; foreldrelos = []; utenfor_sett = {}
    for j, fl in enumerate(F):
        if min(fl['farge']) > 0.97 or max(fl['farge']) < 0.2: continue
        m = Lf == j; n = int(m.sum())
        if n < 4 * R * R: continue
        v = idx[m]; va = idxa[m]
        vals, cnt = np.unique(v, return_counts=True)
        o = np.argsort(-cnt)
        top = [(int(vals[k]), int(cnt[k])) for k in o if vals[k] > 0]
        if top and top[0][1] >= 0.35 * n:
            tildelt.setdefault(ids[top[0][0]], []).append(j)
        else:
            va_ = va[va > 0]
            if len(va_) >= 0.35 * n:
                vv, cc = np.unique(va_, return_counts=True); i2 = ids[int(vv[np.argmax(cc)])]
                utenfor_sett.setdefault(i2, []).append(j)
            elif (v == 0).sum() >= 0.5 * n:
                foreldrelos.append(j)
    # tegnede hus uten modellhus: sammenhengende grupper av flater uten modell under
    grupper = []
    if foreldrelos:
        U = unary_union([F[j]['ytre'].buffer(0.8) for j in foreldrelos])
        Mh = _hovedmaske(tegning_maske(im))
        for g in getattr(U, 'geoms', [U]):
            if g.area < 120: continue
            cpt = g.representative_point()
            if not Mh[min(H - 1, int(cpt.y * R)), min(W - 1, int(cpt.x * R))]: continue     # nabokvartal-bit i kanten av arket
            js = [j for j in foreldrelos if g.intersects(F[j]['ytre'])]
            vegger = [j for j in js if FT.er_vegg(F[j]['ytre'])]
            # antall hus: vegger på samme side som ikke overlapper i x
            xs = sorted([(F[j]['ytre'].bounds[0], F[j]['ytre'].bounds[2]) for j in vegger])
            nh = 0; slutt = -1e9
            for x0, x1 in xs:
                if x0 > slutt - 1.5: nh += 1; slutt = x1
                else: slutt = max(slutt, x1)
            c = g.centroid
            # nærmeste modellhus (for å si hvor)
            naer = None
            yy, xx = np.nonzero(idx > 0)
            if len(xx):
                d2 = (xx - c.x * R) ** 2 + (yy - c.y * R) ** 2; k = int(np.argmin(d2)); naer = ids.get(int(idx[yy[k], xx[k]]))
            grupper.append(dict(senter_pt=[round(c.x, 1), round(c.y, 1)], areal_pt2=round(g.area), flater=js, vegger=len(vegger),
                                hus_anslag=max(1, nh), naermeste_modellhus=naer))
    # per hus
    Mt = tegning_maske(im) > 0
    ut = []
    for x in B:
        i = x['id']; k_ = inv.get(i)
        Pm = P_hus(K, i)
        Mm = (idx == k_) if k_ else np.zeros((H, W), bool)
        js = tildelt.get(i, [])
        Md = np.isin(Lf, js) if js else np.zeros((H, W), bool)
        r = dict(id=i, adr=x.get('adr'), navn=x.get('navn'), h=x.get('h'), fasade_kilde=x.get('fasade_kilde'), farge_kilde=x.get('farge_kilde'),
                 synlig_px=int(Mm.sum()), flater=js)
        if Mm.sum() < 30:
            r['finnes'] = 'skjult i modellbildet'; ut.append(r); continue
        if not js:
            # er huset tegnet i det hele tatt? (det tegnede under modellhuset)
            r['finnes'] = 'nei (modellen har huset, tegningen viser ikke noe her)' if (Mt & Mm).sum() < 0.3 * Mm.sum() else 'uklart (tegnet flate under, men ingen flate tildelt)'
            ut.append(r); continue
        r['finnes'] = 'ja'
        k3 = np.ones((3, 3), np.uint8)
        a_ = cv2.dilate(Mm.astype(np.uint8), k3) > 0; b_ = cv2.dilate(Md.astype(np.uint8), k3) > 0
        r['iou'] = round(float((a_ & b_).sum() / max((a_ | b_).sum(), 1)), 3)
        r['andel_av_modell_dekket'] = round(float((Md & Mm).sum() / max(Mm.sum(), 1)), 2)
        r['andel_av_tegning_dekket'] = round(float((Md & Mm).sum() / max(Md.sum(), 1)), 2)
        # vegger: modellens synlige vegger i tegningen og flatene på dem
        P2 = Pm[:, :2]; ccw = 1 if _areal(x['p']) > 0 else -1
        vegger_m = []
        pts = x['p']
        for kk in range(len(pts)):
            a, b = pts[kk], pts[(kk + 1) % len(pts)]
            L = math.dist(a, b)
            if L < 1.5: continue
            nrm_ = np.array([b[1] - a[1], -(b[0] - a[0])]) * ccw / L
            if (P2 @ nrm_)[1] <= 1e-6: continue
            q = Pg([proj(Pm, a[0], a[1], 0), proj(Pm, b[0], b[1], 0), proj(Pm, b[0], b[1], x['h']), proj(Pm, a[0], a[1], x['h'])]).buffer(0)
            if q.area < 2: continue
            vegger_m.append(dict(k=kk, a=a, b=b, L=L, q=q, lys=bool((P2 @ nrm_)[0] < 0)))
        veggflater = [j for j in js if FT.er_vegg(F[j]['ytre'])]
        takflater = [j for j in js if j not in veggflater]
        vk = {}
        for j in veggflater:
            P_ = F[j]['ytre']; best = None
            for v in vegger_m:
                ov = v['q'].intersection(P_).area / max(P_.area, 1e-6)
                if best is None or ov > best[0]: best = (ov, v)
            if best and best[0] > 0.3:
                vk.setdefault(best[1]['k'], []).append(j)
        # sammenslått? flere tegnede fasader (ikke-overlappende veggflater med ulik farge) på én modellvegg
        sammen = []
        for kk, jl in vk.items():
            if len(jl) < 2: continue
            xs = sorted([(F[j]['ytre'].bounds[0], F[j]['ytre'].bounds[2], F[j]['farge'], F[j]['ytre'].area) for j in jl])
            seg = []
            for x0, x1, fa, ar in xs:
                if ar < 40: continue
                if seg and x0 < seg[-1][1] - 2: seg[-1] = (seg[-1][0], max(seg[-1][1], x1), seg[-1][2]); continue
                seg.append((x0, x1, fa))
            if len(seg) >= 2:
                ulike = len(set(tuple(round(c, 2) for c in s_[2]) for s_ in seg))
                hoyder = []
                for j in jl:
                    P_ = F[j]['ytre']; x0, y0, x1, y1 = P_.bounds; hoyder.append(y1 - y0)
                sammen.append(dict(vegg=kk, fasader=len(seg), ulike_farger=ulike))
        r['tegnede_fasader_per_vegg'] = {str(kk): len(jl) for kk, jl in vk.items()}
        if sammen:
            r['slaatt_sammen'] = sammen
        # høyder: tegnet vegghøyde i hjørnene / modellens K*h. Veggene som er lest for hånd (kilder/fasade-tegning) først;
        # ellers flatene på veggen slått sammen (sokkel + vegg) og målt i venstre og høyre loddkant (den høyeste av de to:
        # en hjørnekant kan være skjult av huset foran)
        Kp = K['par']['K']; gs = []; kilde_g = None
        for v_ in FTJ.get(i, []):
            g_ = v_.get('geo') or {}
            if g_.get('H_venstre'):
                gs.append(0.5 * (g_['H_venstre'] + g_['H_hoyre']) / (Kp * x['h'])); kilde_g = 'fasadeavlesningen (vegger lest for hånd)'
        if not gs:
            for kk, jl in vk.items():
                U = unary_union([F[j]['ytre'].buffer(2.0) for j in jl]).buffer(-2.0)
                if U.is_empty: continue
                x0, y0, x1, y1 = U.bounds; dd = min(1.0, (x1 - x0) * 0.06); hh_ = []
                for xx in (x0 + dd, x1 - dd):
                    g = U.intersection(LineString_([(xx, -1e4), (xx, 1e4)]))
                    if g.is_empty: continue
                    bb = g.bounds; hh_.append(bb[3] - bb[1])
                if hh_: gs.append(max(hh_) / (Kp * x['h'])); kilde_g = 'veggflatene i tegningen'
        if gs:
            r['gesims_forhold'] = round(float(np.median(gs)), 2); r['gesims_kilde'] = kilde_g
        # silhuetthøyde per kolonne (gesims + tak), tegning / modell
        cols = np.nonzero(Mm.any(axis=0) & Md.any(axis=0))[0]
        if len(cols) > 5:
            em = np.array([np.ptp(np.nonzero(Mm[:, c])[0]) for c in cols]); ed = np.array([np.ptp(np.nonzero(Md[:, c])[0]) for c in cols])
            ok = (em > 3 * R) & (ed > 3 * R)
            if ok.sum() > 5:
                r['silhuett_forhold'] = round(float(np.median(ed[ok] / em[ok])), 2)
        # takform
        r['takform_modell'] = takform_modell(x)
        gavl = 0; gavl_vegger = []
        vegg_av = {j: kk for kk, jl in vk.items() for j in jl}
        for j in veggflater:
            P_ = Pg(F[j]['ytre'].exterior).simplify(0.8)
            c = np.array(P_.exterior.coords)[:-1]
            x0, y0, x1, y1 = P_.bounds
            if x1 - x0 < 4: continue
            venstre = c[c[:, 0] < x0 + 1.5]; hoyre = c[c[:, 0] > x1 - 1.5]
            if not len(venstre) or not len(hoyre): continue
            tl, tr = venstre[:, 1].min(), hoyre[:, 1].min()
            midt = c[(c[:, 0] > x0 + 0.25 * (x1 - x0)) & (c[:, 0] < x1 - 0.25 * (x1 - x0))]
            hh = max(y1 - y0, 1)
            if len(midt) and midt[:, 1].min() < min(tl, tr) - 0.18 * hh:
                gavl += 1
                if j in vegg_av:
                    w_ = next(v for v in vegger_m if v['k'] == vegg_av[j])
                    gavl_vegger.append([list(map(float, w_['a'])), list(map(float, w_['b']))])
        tri = 0
        for j in takflater:
            P_ = Pg(F[j]['ytre'].exterior).simplify(1.2)
            if P_.area < 20: continue
            n_ = len(P_.exterior.coords) - 1
            if n_ == 3: tri += 1
        r['takform_tegning_tegn'] = dict(gavler=gavl, trekantede_takflater=tri, takflater=len(takflater), gavl_vegger=gavl_vegger)
        r['takform_tegning'] = ('halvvalm' if gavl and tri else 'sal' if gavl else 'valm' if tri else ('ukjent (ingen gavl/endeflate synlig)' if takflater else 'ukjent'))
        # farger: tegningens flatefarger (lys side) mot modellen
        def farge_av(jl, lys):
            best = None
            for j in jl:
                fa = tuple(int(round(c * 255)) for c in F[j]['farge'])
                # hvilken side: modellveggen flaten ligger på
                ar = F[j]['ytre'].area
                if best is None or ar > best[1]: best = (fa, ar)
            return best[0] if best else None
        lys_vegger = [j for kk, jl in vk.items() for j in jl if any(v['k'] == kk and v['lys'] for v in vegger_m)]
        sk_vegger = [j for kk, jl in vk.items() for j in jl if any(v['k'] == kk and not v['lys'] for v in vegger_m)]
        tv = farge_av(lys_vegger, True); ts = farge_av(sk_vegger, False)
        mv = x.get('vegg'); mvs = x.get('veggs') or ([int(mv[0] * 0.72), int(mv[1] * 0.8), int(mv[2] * 0.8)] if mv else None)
        if tv and mv:
            r['veggfarge'] = dict(tegning=tv, modell=mv, side='lys', dE=round(dE(tv, mv), 1), kulor_tegning=kulor(tv), kulor_modell=kulor(mv))
        elif ts and mv:
            r['veggfarge'] = dict(tegning=ts, modell=mvs, side='skygge', dE=round(dE(ts, mvs), 1), kulor_tegning=kulor(ts), kulor_modell=kulor(mvs))
        if takflater and x.get('tak'):
            tt_ = max(takflater, key=lambda j: F[j]['ytre'].area)
            fa = tuple(int(round(c * 255)) for c in F[tt_]['farge'])
            mt = x['tak']; mts = x.get('taks') or [int(mt[0] * 0.72), int(mt[1] * 0.8), int(mt[2] * 0.8)]
            d1, d2 = dE(fa, mt), dE(fa, mts)
            r['takfarge'] = dict(tegning=fa, modell=mt if d1 <= d2 else mts, dE=round(min(d1, d2), 1), kulor_tegning=kulor(fa), kulor_modell=kulor(mt))
        # vinduer per synlig vegg: hullene i tegningens veggflater mot modellens vind
        vind = []
        for v in vegger_m:
            jl = vk.get(v['k'], [])
            if not jl: continue
            U = unary_union([F[j]['ytre'] for j in jl])
            lest = next((w_ for w_ in FTJ.get(i, []) if w_['vegg'] == v['k']), None)
            vs = []; dor_t = 0
            if lest:      # fasadeavlesningen: ett element per vindu/dør (sprossene er slått sammen der)
                kilde_v = 'fasadeavlesningen'
                for e_ in lest['elementer']:
                    if e_['vb'] < 0.12 and e_['hv'] > 0.3: dor_t += 1
                    else: vs.append(e_['v'])
            else:         # hullene i veggflaten; glass med sprosser er flere hull: hull tettere enn 0,9 pt er ett vindu
                kilde_v = 'hullene i veggflaten'
                hull = [h_ for j in jl for h_ in F[j]['hull'] if 0.3 < h_.area < 0.4 * F[j]['ytre'].area]
                vindu = unary_union([h_.buffer(0.45) for h_ in hull]) if hull else None
                deler = [g_ for g_ in getattr(vindu, 'geoms', [vindu]) if g_ is not None and not g_.is_empty and g_.area > 1.2]
                for h_ in deler:
                    hb = h_.bounds; cx = 0.5 * (hb[0] + hb[2])
                    g = U.convex_hull.intersection(LineString_([(cx, -1e4), (cx, 1e4)]))
                    if g.is_empty: continue
                    gb = g.bounds; Hh = max(gb[3] - gb[1], 1e-6)
                    vb = (gb[3] - hb[3]) / Hh; ht = (hb[3] - hb[1]) / Hh
                    if vb < 0.1 and ht > 0.22: dor_t += 1
                    else: vs.append((gb[3] - 0.5 * (hb[1] + hb[3])) / Hh)
            n_m, rader_m, dor_m = vinduer_modell(x, v['a'], v['b'])
            vind.append(dict(vegg=v['k'], lengde_m=round(v['L'], 1), kilde=kilde_v, tegning=dict(vinduer=len(vs), rader=_rader(vs), dorer=dor_t),
                             modell=dict(vinduer=n_m, rader=rader_m, dorer=dor_m)))
        r['vinduer'] = vind
        # arker og piper (anslått): små flater på taket
        sma = [j for j in js if F[j]['ytre'].area < 0.05 * max(Md.sum() / R / R, 1)]
        ark_t = 0; pipe_t = 0
        for j in sma:
            P_ = F[j]['ytre']; x0, y0, x1, y1 = P_.bounds
            c = P_.representative_point()
            ty_ = typ[min(H - 1, int(c.y * R)), min(W - 1, int(c.x * R))]
            if ty_ != 2: continue
            if (y1 - y0) > 1.3 * (x1 - x0) and P_.area < 25: pipe_t += 1
            elif FT.er_vegg(P_) or P_.area >= 25: ark_t += 1
        r['arker'] = dict(tegning_anslag=ark_t, modell=len(x.get('arker') or []))
        r['piper'] = dict(tegning_anslag=pipe_t, modell=len(x.get('piper') or []))
        ut.append(r)
    modell_uten = []
    return dict(tegning=navn, hus=ut, tegnet_uten_modell=grupper, hus_utenfor_tegningens_sett=list(utenfor_sett), koblet_men_utenfor=K.get('utenfor_tegningen', []))


def LineString_(c):
    from shapely.geometry import LineString
    return LineString(c)


ALV = {'feil': 3, 'avvik med grunn': 1, 'avvik': 2, 'ok': 0}


def vurder(r, navn):
    """Alvorlighet per kategori for ett hus."""
    v = {}
    def sett(k, a, hva): v[k] = dict(alvor=a, hva=hva)
    f = r.get('finnes', '')
    if f.startswith('nei'):
        sett('finnes', 'feil', f)
    elif f.startswith('uklart'):
        sett('finnes', 'avvik', f)
    elif f == 'ja':
        sett('finnes', 'ok', 'ja')
    if 'slaatt_sammen' in r:
        s_ = r['slaatt_sammen']; n = max(x['fasader'] for x in s_)
        sett('slaatt_sammen', 'feil' if any(x['ulike_farger'] >= 2 for x in s_) else 'avvik',
             f"tegningen har {n} fasader på én modellvegg (vegg {', '.join(str(x['vegg']) for x in s_)}; ulike farger: {max(x['ulike_farger'] for x in s_)})")
    if 'iou' in r:
        i = r['iou']; sett('omriss', 'feil' if i < 0.45 else 'avvik' if i < 0.65 else 'ok', f"IoU {i:.2f} (modell dekket {r['andel_av_modell_dekket']:.0%}, tegning dekket {r['andel_av_tegning_dekket']:.0%})")
    if 'gesims_forhold' in r:
        g = r['gesims_forhold']; d = abs(g - 1)
        sett('gesims', 'feil' if d > 0.35 else 'avvik' if d > 0.18 else 'ok', f"tegnet/modell {g:.2f}" + (" (tegningen høyere)" if g > 1 else " (tegningen lavere)" if g < 1 else ""))
    if 'silhuett_forhold' in r:
        g = r['silhuett_forhold']; d = abs(g - 1)
        sett('mone', 'feil' if d > 0.35 else 'avvik' if d > 0.18 else 'ok', f"silhuetthøyde tegnet/modell {g:.2f}")
    if 'takform_modell' in r:
        t, m = r.get('takform_tegning', ''), r['takform_modell']
        if t.startswith('ukjent'):
            sett('takform', 'ok', f"modell {m}; tegningen viser ikke gavl/endeflate")
        else:
            lik = (t == m) or (m.startswith(t)) or (t == 'sal' and m in ('sal/sammensatt', 'knekk')) or (t == 'halvvalm' and m in ('sammensatt',))
            sett('takform', 'ok' if lik else 'feil', f"tegning {t}, modell {m}")
    for k, navn_ in (('veggfarge', 'veggfarge'), ('takfarge', 'takfarge')):
        c = r.get(k)
        if not c: continue
        sv = 'Street View' in (r.get('farge_kilde') or '')
        if c['kulor_tegning'] != c['kulor_modell'] and c['dE'] > 18:
            a = 'avvik med grunn' if sv else 'feil'
        elif c['dE'] > 22:
            a = 'avvik med grunn' if sv else 'avvik'
        else:
            a = 'ok'
        sett(navn_, a, f"tegning {tuple(c['tegning'])} ({c['kulor_tegning']}), modell {tuple(c['modell'])} ({c['kulor_modell']}), ΔE {c['dE']}" + (f"; modellens farge: {r.get('farge_kilde')}" if r.get('farge_kilde') else ''))
    vv = r.get('vinduer') or []
    if vv:
        verst = None
        for w in vv:
            dt = abs(w['tegning']['vinduer'] - w['modell']['vinduer'])
            rad = w['tegning']['rader'] != w['modell']['rader'] and len(w['tegning']['rader']) != len(w['modell']['rader'])
            sc = dt + (2 if rad else 0)
            if verst is None or sc > verst[0]: verst = (sc, w, dt, rad)
        sc, w, dt, rad = verst
        a = 'feil' if dt >= 3 or (rad and w['tegning']['vinduer'] >= 2) else 'avvik' if dt >= 1 else 'ok'
        sett('vinduer', a, f"vegg {w['vegg']} ({w['lengde_m']} m): tegning {w['tegning']['vinduer']} vinduer i rader {w['tegning']['rader']}, modell {w['modell']['vinduer']} i rader {w['modell']['rader']}")
        dd = [(w['tegning']['dorer'], w['modell']['dorer'], w['vegg']) for w in vv if w['tegning']['dorer'] != w['modell']['dorer']]
        sett('dorer', 'avvik' if dd else 'ok', '; '.join(f"vegg {g}: tegning {a_}, modell {b_}" for a_, b_, g in dd) if dd else 'like')
    for k in ('arker', 'piper'):
        c = r.get(k)
        if c:
            sett(k, 'avvik' if abs(c['tegning_anslag'] - c['modell']) >= 3 else 'ok', f"tegning ~{c['tegning_anslag']} (grovt anslag fra små takflater, også takvinduer), modell {c['modell']}")
    return v


VEKT = dict(finnes=10, slaatt_sammen=9, omriss=6, takform=6, gesims=5, mone=4, vinduer=4, veggfarge=3, takfarge=3, dorer=1, arker=1, piper=0.5)


def avvik(navner, logg=print):
    alle = []; tegnet_uten = []; per = {}
    for n in navner:
        if not os.path.exists(os.path.join(ARB, f'{n}-id.png')):
            logg(f"  {n}: ikke rendret, hoppes over"); continue
        A = analyser(n, logg)
        per[n] = A
        for r in A['hus']:
            r['tegning'] = n; r['vurdering'] = vurder(r, n); alle.append(r)
        for g in A['tegnet_uten_modell']:
            g['tegning'] = n; tegnet_uten.append(g)
        logg(f"  {n}: {len(A['hus'])} hus, {len(A['tegnet_uten_modell'])} tegnede grupper uten modellhus")
    tot = {}
    for r in alle:
        for k, v in r['vurdering'].items():
            tot.setdefault(k, {}).setdefault(v['alvor'], 0); tot[k][v['alvor']] += 1
    tot['tegnet_hus_uten_modell'] = dict(feil=sum(g['hus_anslag'] for g in tegnet_uten))
    json.dump(dict(laget=__import__('datetime').date.today().isoformat(), verktoy='verktoy/kontroll.py avvik', totalt=tot,
                   hus=alle, tegnet_uten_modell=tegnet_uten, per_tegning={n: dict(koblet_men_utenfor=A['koblet_men_utenfor'], hus_utenfor_tegningens_sett=A['hus_utenfor_tegningens_sett'])
                                                                         for n, A in per.items()}),
              open(os.path.join(UT, 'avvik.json'), 'w'), indent=1, ensure_ascii=False)
    logg(json.dumps(tot, ensure_ascii=False))
    return alle, tegnet_uten, tot


def md(logg=print):
    """rapport/kontroll/avvik.md = det jeg har sett på arkene (rapport/kontroll/merknader.md, skrevet for hånd etter å ha sett
    på hvert ark) + tallene fra avvik.json: totaler, registrering per tegning og én tabell per tegning."""
    d = json.load(open(os.path.join(UT, 'avvik.json')))
    L = [open(os.path.join(UT, 'merknader.md'), encoding='utf8').read().rstrip(), '', '## Totaltall per kategori (maskinelt, se forbeholdene over)', '',
         '| kategori | feil | avvik | avvik med grunn | ok |', '|---|---|---|---|---|']
    for k, v in d['totalt'].items():
        L.append(f"| {k} | {v.get('feil', 0)} | {v.get('avvik', 0)} | {v.get('avvik med grunn', 0)} | {v.get('ok', 0)} |")
    L += ['', '## Registrering per tegning', '', '| tegning | hus | dreiing | helning | bakke pt/m | høyde pt/m (kilde) | kanter fra tegningen, median | hus innen 3 pt | blokker flyttet > 3 pt | koblet, men utenfor tegningen |', '|---|---|---|---|---|---|---|---|---|---|']
    for n in TEGNINGER:
        f = os.path.join(ARB, n + '-kamera.json')
        if not os.path.exists(f): continue
        K = json.load(open(f)); p_ = K['par']; rg = K.get('registrering', {})
        fl = sum(1 for b in K.get('blokker', []) if math.hypot(*b['d']) > 3)
        L.append(f"| {n} | {len(K['bygg'])} | {p_['az']:.1f}° | {p_['el']:.1f}° | {p_['s']:.2f} | {p_['K']:.2f} ({p_['K_kilde']}) | {rg.get('median_pt')} pt = {rg.get('median_px')} px | {int(100 * (rg.get('andel_under_3pt') or 0))} % | {fl} av {len(K.get('blokker', []))} | {', '.join(kort_id(i) for i in K.get('utenfor_tegningen', [])) or '-'} |")
    L += ['', '## Per hus (maskinelt)', '', 'Alvor: **F** feil, A avvik, G avvik med grunn (modellens farge er Street View, tegningen er 2015). Tomt = ok eller ikke målt.', '']
    kat = ['finnes', 'slaatt_sammen', 'omriss', 'gesims', 'mone', 'takform', 'veggfarge', 'takfarge', 'vinduer', 'dorer', 'arker', 'piper']
    kort = dict(feil='**F**', avvik='A', ok='', **{'avvik med grunn': 'G'})
    for n in TEGNINGER:
        H_ = [r for r in d['hus'] if r['tegning'] == n]
        if not H_: continue
        L += [f'### {n}', '', '| hus | ' + ' | '.join(kat) + ' | merknad |', '|' + '---|' * (len(kat) + 2)]
        for r in H_:
            v = r['vurdering']
            mer = '; '.join(f"{k}: {x['hva']}" for k, x in v.items() if x['alvor'] in ('feil',) and k in ('takform', 'vinduer', 'gesims', 'slaatt_sammen', 'takfarge', 'veggfarge'))
            L.append(f"| {kort_id(r['id'])} | " + ' | '.join(kort.get(v.get(k, {}).get('alvor', ''), '') for k in kat) + f" | {mer[:300]} |")
        tu = [g for g in d['tegnet_uten_modell'] if g['tegning'] == n]
        if tu:
            L.append('')
            L.append('Tegnet uten modellhus under (flategrupper, maskinelt; små grupper er ofte bare frihåndsforskyvning): ' +
                     '; '.join(f"ved {kort_id(g['naermeste_modellhus'] or '?')} ({g['areal_pt2']} pt², ~{g['hus_anslag']} hus)" for g in tu))
        L.append('')
    open(os.path.join(UT, 'avvik.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')
    logg('  avvik.md')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'alt'
    navn = sys.argv[2:] or TEGNINGER
    if cmd in ('kamera', 'reg'):
        for n in navn:
            kamera(n, bare_reg=(cmd == 'reg'))
    elif cmd == 'render':
        render(navn)
    elif cmd == 'ark':
        for n in navn:
            ark(n)
    elif cmd == 'avvik':
        avvik(navn); md()
    elif cmd == 'md':
        md()
    elif cmd == 'alt':
        for n in navn: kamera(n)
        render(navn)
        for n in navn: ark(n)
        avvik(navn); md()
