"""Kvartal-QA (28.10, nattskift): kontrollark per kvartaltegning, tegningen ved siden av modellen sett fra samme kant.

Kilden er Vegars strektegninger fra 2015 (Dropbox: 00 Kunder/Visit Fredrikstad & Hvaler/Gamlebyen kart tegning/strektegninger,
.ai-filene, PDF inni). De ligger bare lokalt i kilder/kvartal-ai/ (åndsverk, ikke i git), det samme gjør 2019-trykket
(kilder/ai/ai/brosjyre2019-3.jpg). Det som går i git, er koblingen (kilder/kvartal-kobling.json) og arkene (rapport/kvartal-qa/).

    python3 -I verktoy/kvartal_qa.py rastrer     .ai -> kilder/kvartal-ai/png/<navn>.png (150 dpi, alle lag på)
    python3 -I verktoy/kvartal_qa.py registrer   SIFT + RANSAC (similaritet) tegning -> 2019-trykket, flere skalaer
    python3 -I verktoy/kvartal_qa.py kobling     bygg med px2019 innenfor tegningens omriss -> kilder/kvartal-kobling.json
                                                 + rapport/kvartal-qa/_arbeid/visninger.json (kamera per tegning)
    node verktoy/kvartal_bilder.mjs ut/enkel/index.html rapport/kvartal-qa/_arbeid/visninger.json rapport/kvartal-qa/_arbeid
                                                 modellbilder fra to vinkler + skjermposisjonen til hvert bygg
    python3 -I verktoy/kvartal_qa.py ark         velger vinkel per tegning (målt), lager rapport/kvartal-qa/<navn>.jpg og oversikt.jpg

Alt leses gjennom datalag.py; bygg pekes på med id, aldri plass i lista (plass brukes bare som oppslag i rapport/farger2019.json).
"""
import sys, os, json, glob
import numpy as np, cv2

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROT)
import datalag

KV = os.path.join(ROT, 'kilder', 'kvartal-ai'); PNG = os.path.join(KV, 'png')
TRYKK = os.path.join(ROT, 'kilder', 'ai', 'ai', 'brosjyre2019-3.jpg')
KOBLING = os.path.join(ROT, 'kilder', 'kvartal-kobling.json')
UT = os.path.join(ROT, 'rapport', 'kvartal-qa'); ARB = os.path.join(UT, '_arbeid')
REG = os.path.join(ARB, 'registrering.json')
DPI = 150
NAVN = ['Kvartal2BITMP', 'Kvartal3', 'Kvartal4BITMP', 'kvartal5', 'kvartal6', 'kvartal7', 'Kvartal8BITMAP', 'Kvartal9',
        'Kvartal10', 'Kvartal11', 'Kvartal12', 'Kvartal13', 'Kvartal14', 'sistekvartal', 'tell', 'Glasshytta', 'kirke']
SKALAER = [0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6]
UTVID = 15            # px i trykket rundt det tegnede omrisset (px2019 kan bomme 5–25 px)
NAER_PX = 65          # runde 2: tom tegnet bit -> nærmeste ukoblede bygg innenfor så mange px i trykket
KANT_ANDEL = 0.15     # tegnede biter mindre enn 15 % av den største regnes som nabokvartal i kanten av tegningen
VINKLER = [20, 40]    # az: 20 = målt fra trykket (modell_h_til_2019 dekomponert), 40 = plakatvinkelen i kartet


def rastrer():
    import pymupdf
    os.makedirs(PNG, exist_ok=True)
    for n in NAVN:
        d = pymupdf.open(os.path.join(KV, n + '.ai'))
        ocg = d.get_ocgs()
        if ocg: d.set_layer(-1, on=list(ocg.keys()))      # alle lag synlige
        pix = d[0].get_pixmap(dpi=DPI, alpha=False); pix.save(os.path.join(PNG, n + '.png'))
        print(n, pix.width, pix.height, 'lag', len(ocg))


def _maske_tegning(g):
    """Tegnede piksler (ikke papirhvitt), med gårdsrom fylt (ytre omriss fylt)."""
    m = (g < 245).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    f = np.zeros_like(m); cv2.drawContours(f, cs, -1, 255, -1)
    return f


def registrer():
    os.makedirs(ARB, exist_ok=True)
    T = cv2.imread(TRYKK, 0)
    sift = cv2.SIFT_create(nfeatures=40000)
    kT, dT = sift.detectAndCompute(T, None)
    bf = cv2.BFMatcher()
    ut = {}
    for n in NAVN:
        D0 = cv2.imread(os.path.join(PNG, n + '.png'), 0)
        forsok = []
        for f in SKALAER:
            D = cv2.resize(D0, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
            kD, dD = sift.detectAndCompute(D, None)
            if dD is None or len(kD) < 6: continue
            g = [a for a, b in bf.knnMatch(dD, dT, k=2) if a.distance < 0.8 * b.distance]
            if len(g) < 6: forsok.append(dict(f=f, treff=len(g), inliers=0)); continue
            src = np.float32([kD[a.queryIdx].pt for a in g]) / f; dst = np.float32([kT[a.trainIdx].pt for a in g])
            M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4, maxIters=20000, confidence=0.999)
            if M is None: forsok.append(dict(f=f, treff=len(g), inliers=0)); continue
            inl = inl.ravel().astype(bool)
            r = np.linalg.norm(src[inl] @ M[:, :2].T + M[:, 2] - dst[inl], axis=1)
            forsok.append(dict(f=f, treff=len(g), inliers=int(inl.sum()), median=float(np.median(r)), M=M.tolist(),
                               skala=float(np.hypot(*M[:, 0])), rot=float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))))
        gode = [x for x in forsok if x['inliers'] >= 3]
        best = max(gode, key=lambda x: (x['inliers'], -x['median'])) if gode else None
        # samstemmighet: hvor mange av skalaene ga samme transformasjon (± 2 % skala, ± 5 px senter)
        if best:
            Mb = np.array(best['M']); h, w = D0.shape; c = np.array([w / 2, h / 2]); cb = Mb[:, :2] @ c + Mb[:, 2]
            enige = sum(1 for x in gode if abs(x['skala'] / best['skala'] - 1) < 0.02 and
                        np.linalg.norm(np.array(x['M'])[:, :2] @ c + np.array(x['M'])[:, 2] - cb) < 5)
            best['enige_skalaer'] = enige
        sikker = bool(best and best['inliers'] >= 12 and best['median'] <= 3 and best.get('enige_skalaer', 0) >= 2)
        ut[n] = dict(best=best, sikker=sikker, metode='SIFT', forsok=[{k: v for k, v in x.items() if k != 'M'} for x in forsok])
        print(n, 'sikker' if sikker else 'USIKKER', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in (best or {}).items() if k != 'M'})
    # Andre runde for dem SIFT ikke klarer alene: maskert malmatching (TM_CCOEFF_NORMED) i fast skala nær medianen av de sikre,
    # rotasjon 0. Uten anker: i et vindu rundt SIFT-forslaget (kryssjekk). Med anker (ANKER, funnet ved å se på trykket): i vinduet rundt ankeret.
    sk = float(np.median([v['best']['skala'] for v in ut.values() if v['sikker']]))
    Tc = cv2.imread(TRYKK).astype(np.float32)
    for n, v in ut.items():
        if v['sikker']: continue
        D = cv2.imread(os.path.join(PNG, n + '.png')); g = cv2.cvtColor(D, cv2.COLOR_BGR2GRAY)
        mt = _maske_tegning(g); nlab, lab, st, _ = cv2.connectedComponentsWithStats(mt)
        deler = []
        anker = ANKER.get(n)
        if anker is None and v['best']:
            M = np.array(v['best']['M']); deler_inn = [(None, (M[0, 2], M[1, 2]))]
        elif anker is not None:
            deler_inn = anker
        else:
            print(n, 'ingen registrering'); continue
        for del_inn in deler_inn:
            bbox, t0 = del_inn[0], del_inn[1]
            if len(del_inn) > 2 and del_inn[2] == 'fast':      # ankeret brukes som det er (malmatchingen trekkes av tallet over huset)
                deler.append(dict(score=None, nest=None, skala=sk, M=[[sk, 0, t0[0]], [0, sk, t0[1]]], bbox=list(bbox), fast=True)); continue
            if bbox is None: x, y, w, h = 0, 0, g.shape[1], g.shape[0]; maske = (mt > 0)
            else: x, y, w, h = bbox; maske = (mt[y:y + h, x:x + w] > 0)
            bestt = None
            for s in np.arange(sk - 0.012, sk + 0.0121, 0.004):
                tpl = cv2.resize(D[y:y + h, x:x + w], None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
                mk = cv2.resize(maske.astype(np.uint8) * 255, (tpl.shape[1], tpl.shape[0]), interpolation=cv2.INTER_NEAREST)
                mk3 = cv2.merge([mk, mk, mk]).astype(np.float32) / 255
                # vindu rundt forventet plassering av utsnittets hjørne (±60 px rundt SIFT-forslaget, ±20 px rundt et anker)
                ex, ey = t0[0] + s * x, t0[1] + s * y; V = 20 if anker is not None else 60
                X0, Y0 = int(max(0, ex - V)), int(max(0, ey - V))
                vin = Tc[Y0:int(ey + V) + tpl.shape[0], X0:int(ex + V) + tpl.shape[1]]
                if vin.shape[0] < tpl.shape[0] or vin.shape[1] < tpl.shape[1]: continue
                res = np.nan_to_num(cv2.matchTemplate(vin, tpl, cv2.TM_CCOEFF_NORMED, mask=mk3), nan=-1, posinf=-1, neginf=-1)
                _, val, _, loc = cv2.minMaxLoc(res)
                r2 = res.copy(); cv2.circle(r2, loc, 8, -1, -1); andre = float(r2.max())
                if bestt is None or val > bestt['score']:
                    t = (X0 + loc[0] - s * x, Y0 + loc[1] - s * y)
                    bestt = dict(score=float(val), nest=andre, skala=float(s), M=[[s, 0, t[0]], [0, s, t[1]]], bbox=None if bbox is None else [int(q) for q in bbox])
            deler.append(bestt)
        avvik = None
        if anker is None and v['best']:
            Mb = np.array(v['best']['M']); Mt = np.array(deler[0]['M']); c = np.array([g.shape[1] / 2, g.shape[0] / 2])
            avvik = float(np.linalg.norm(Mb[:, :2] @ c + Mb[:, 2] - (Mt[:, :2] @ c + Mt[:, 2])))
        v['malmatching'] = dict(deler=deler, skala_median_sikre=sk, avvik_sift_mot_mal_px=avvik)
        if avvik is not None and avvik < 3 and deler[0]['score'] - deler[0]['nest'] > 0.1:
            v['sikker'] = True; v['metode'] = 'SIFT, kryssjekket med malmatching (avvik %.1f px)' % avvik
        elif anker is not None:
            v['metode'] = 'anker satt ved å se på trykket + malmatching per del (fast skala, rotasjon 0); USIKKER'
            v['best'] = dict(M=deler[0]['M'], median=None, inliers=0, treff=0, f=None, skala=deler[0]['skala'], rot=0.0)
        print(n, v['metode'], [(d['score'], d['nest'], [round(q, 1) for q in np.array(d['M'])[:, 2]]) for d in deler], 'avvik', avvik)
    json.dump(ut, open(REG, 'w'), ensure_ascii=False, indent=1)


# Tegninger SIFT ikke finner i trykket (små hus, trær over). Ankeret er sett med øynene i trykket 28.10 og er bare startpunkt for
# malmatchingen: (utsnitt i tegningen [x,y,b,h] eller None = hele, omtrentlig oversetting tegning->trykk (t_x, t_y) ved skala 0,322).
#   tell: Ingeniørgården (23) med det lille huset med to arker til venstre og den lave oransje bygningen under trærne.
#   Glasshytta: to hus limt sammen fra hver sin kant av byen, derfor ett anker per hus:
#     huset på buen = Voldporten med vaktstuen (25), huset med valmtak og buedør = ved Ravelinporten (27).
#     For huset på buen trekkes malmatchingen mot tallet «25» som ligger over huset i trykket; ankeret står fast (justert for øyet, ± ~5 px).
# Bygg satt for hånd: (id, grunn, del i ANKER). Bare der verken px2019 eller runde 2 når fram.
MANUELT = {
    'Glasshytta': [('bnr-193869580', 'legendenummer 27 (Ravelinporten) står ved huset i trykket; px2019 for Voldportravelinet ligger ~150 px unna', 1)],
}
ANKER = {
    'tell': [(None, (1523, 929))],
    'Glasshytta': [((29, 22, 154, 155), (1824, 719), 'fast'),
                   ((668, 254, 172, 131), (1877, 749))],
}


def _sentroide(p):
    p = np.asarray(p, float)
    if len(p) > 2 and np.allclose(p[0], p[-1]): p = p[:-1]
    x, y = p[:, 0], p[:, 1]; x1, y1 = np.roll(x, -1), np.roll(y, -1); a = x * y1 - x1 * y; A = a.sum() / 2
    if abs(A) < 1e-9: return p.mean(0)
    return np.array([((x + x1) * a).sum() / (6 * A), ((y + y1) * a).sum() / (6 * A)])


def kobling():
    reg = json.load(open(REG))
    data = datalag.koble_til_plass(datalag.alle()); bygg = data['bygg']
    f19 = json.load(open(os.path.join(ROT, 'rapport', 'farger2019.json')))
    T = cv2.imread(TRYKK, 0); H, W = T.shape
    kand = []          # (plass, id, px)
    uten_px = []
    for i, b in enumerate(bygg):
        if b.get('gml') != 1 or b.get('skjul'): continue
        px = (f19.get(str(i)) or {}).get('px2019')
        if not px: uten_px.append(b['id']); continue
        kand.append((i, b['id'], np.array(px, float)))
    tegninger = []; visninger = []
    for n in NAVN:
        r = reg[n]; best = r['best']
        post = dict(navn=n, fil=f'strektegninger/{n}.ai', raster=f'{DPI} dpi, alle lag synlige', sikker_registrering=r['sikker'])
        if not best:
            post.update(merknad='ingen registrering mot trykket', bygg=[], kant=[]); tegninger.append(post); continue
        g = cv2.imread(os.path.join(PNG, n + '.png'), 0); h, w = g.shape
        mm = r.get('malmatching') or {}
        if ANKER.get(n) and mm.get('deler'):
            deler = [(np.array(d['M']), d.get('bbox')) for d in mm['deler']]
        else:
            deler = [(np.array(best['M']), None)]
        mt = _maske_tegning(g)
        # hver tegnet bit for seg, så nabokvartal i kanten av tegningen kan skilles fra hovedmotivet
        nlab, lab, st, _ = cv2.connectedComponentsWithStats(mt)
        areal = st[1:, cv2.CC_STAT_AREA]; stoerst = areal.max() if len(areal) else 0
        hoved = np.zeros_like(mt); kant = np.zeros_like(mt)
        for k in range(1, nlab):
            (hoved if st[k, cv2.CC_STAT_AREA] >= KANT_ANDEL * stoerst else kant)[lab == k] = 255
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * UTVID + 1, 2 * UTVID + 1))
        mh = np.zeros((H, W), np.uint8); mk = np.zeros((H, W), np.uint8); delnr = np.full((H, W), -1, np.int16)
        for j, (M, bb) in enumerate(deler):
            sel = np.zeros_like(mt)
            if bb is None: sel[:] = 1
            else: x0, y0, bw, bh = bb; sel[y0:y0 + bh, x0:x0 + bw] = 1
            a = cv2.dilate(cv2.warpAffine(hoved * sel, M, (W, H), flags=cv2.INTER_NEAREST), ker)
            b_ = cv2.dilate(cv2.warpAffine(kant * sel, M, (W, H), flags=cv2.INTER_NEAREST), ker)
            mh |= a; mk |= b_; delnr[(a > 0) & (delnr < 0)] = j
        cv2.imwrite(os.path.join(ARB, n + '-maske.png'), np.dstack([mk // 2, mh, np.zeros_like(mh)]))
        hb, kb, pxt = [], [], {}
        for i, bid, px in kand:
            x, y = int(round(px[0])), int(round(px[1]))
            if not (0 <= x < W and 0 <= y < H): continue
            if mh[y, x]:
                hb.append((i, bid)); M = deler[max(0, int(delnr[y, x]))][0]
                A = np.vstack([M, [0, 0, 1]]); q = np.linalg.solve(A, [px[0], px[1], 1])[:2]   # px2019 tilbake i tegningens piksler
                pxt[bid] = [round(float(q[0]), 1), round(float(q[1]), 1)]
            elif mk[y, x]: kb.append((i, bid))
        M = deler[0][0]
        hj = np.array([[0, 0], [w, 0], [w, h], [0, h]], float) @ M[:, :2].T + M[:, 2]
        post.update(tegning_til_trykk=[[round(v, 6) for v in rad] for rad in M.tolist()],
                    enhet='tegning: piksler i 150 dpi-rasteret (= PDF-punkt × 150/72); trykk: piksler i brosjyre2019-3.jpg (2480×1754)',
                    registreringsmetode=r.get('metode'),
                    skala=round(float(np.hypot(*M[:, 0])), 5), rotasjon_grader=round(float(np.degrees(np.arctan2(M[1, 0], M[0, 0]))), 3),
                    residual_median_px=None if best.get('median') is None else round(best['median'], 2),
                    inliers=best.get('inliers'), treff=best.get('treff'), rasterskala_ved_matching=best.get('f'), enige_skalaer=best.get('enige_skalaer'),
                    omriss_i_trykket=[[round(v, 1) for v in p] for p in hj.tolist()])
        if len(deler) > 1:
            post['deler'] = [dict(utsnitt_i_tegningen=bb, tegning_til_trykk=[[round(v, 6) for v in rad] for rad in Md.tolist()]) for Md, bb in deler]
        post['_t'] = dict(hb=hb, kb=kb, pxt=pxt, mh=mh, delnr=delnr, deler=deler, naer=[], manuelt=[])
        tegninger.append(post)

    # Runde 2: tegnede biter uten et eneste bygg i runde 1 (px2019 bommer mest i utkanten av byen). Nærmeste gml-bygg som ikke er
    # koblet til noen tegning, innenfor NAER_PX fra biten, kobles med merket «naer». Til slutt det som er satt for hånd (MANUELT).
    runde1 = set(bid for t in tegninger if '_t' in t for _, bid in t['_t']['hb'])
    plass = {b['id']: i for i, b in enumerate(bygg)}
    pxd = {bid: px for _, bid, px in kand}
    for t in tegninger:
        if '_t' not in t: continue
        z = t['_t']; nlab, lab = cv2.connectedComponents((z['mh'] > 0).astype(np.uint8))
        har = set(int(lab[int(round(pxd[bid][1])), int(round(pxd[bid][0]))]) for _, bid in z['hb'])
        for k in range(1, nlab):
            if k in har: continue
            cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            kand2 = []
            for _, bid, px in kand:
                if bid in runde1: continue
                d = -max(cv2.pointPolygonTest(c, (float(px[0]), float(px[1])), True) for c in cs)
                if d <= NAER_PX: kand2.append((d, bid))
            if kand2:
                d, bid = min(kand2); runde1.add(bid)
                j = int(z['delnr'][lab == k].max()); M = z['deler'][max(0, j)][0]
                q = np.linalg.solve(np.vstack([M, [0, 0, 1]]), [pxd[bid][0], pxd[bid][1], 1])[:2]
                z['pxt'][bid] = [round(float(q[0]), 1), round(float(q[1]), 1)]
                z['naer'].append(dict(id=bid, avstand_px=round(float(d), 1))); z['hb'].append((plass[bid], bid))
        for bid, grunn, del_j in MANUELT.get(t['navn'], []):
            if bid in [x for _, x in z['hb']]: continue
            x0, y0, bw, bh = z['deler'][del_j][1] or (0, 0, 0, 0)
            z['pxt'][bid] = [x0 + bw / 2, y0 + bh / 2]
            z['manuelt'].append(dict(id=bid, grunn=grunn)); z['hb'].append((plass[bid], bid))
            runde1.add(bid)

    # Runde 3: bygg med fasade_kilde=kvartaltegning er lest fra en av tegningene, så de skal ligge i en. Står ett slikt bygg ukoblet,
    # kobles det til tegningen med nærmeste hovedomriss innenfor NAER_PX (merket «naer», med avstand).
    for _, bid, px in kand:
        if bid in runde1 or bygg[plass[bid]].get('fasade_kilde') != 'kvartaltegning': continue
        beste = None
        for t in tegninger:
            if '_t' not in t: continue
            z = t['_t']; cs, _ = cv2.findContours((z['mh'] > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cs: continue
            d = -max(cv2.pointPolygonTest(c, (float(px[0]), float(px[1])), True) for c in cs)
            if d <= NAER_PX and (beste is None or d < beste[0]): beste = (d, t, cs)
        if beste:
            d, t, cs = beste; z = t['_t']; runde1.add(bid)
            near = min(cs, key=lambda c: -cv2.pointPolygonTest(c, (float(px[0]), float(px[1])), True))
            m1 = np.zeros_like(z['mh']); cv2.drawContours(m1, [near], -1, 1, -1)
            j = int(z['delnr'][m1 > 0].max()); M = z['deler'][max(0, j)][0]
            q = np.linalg.solve(np.vstack([M, [0, 0, 1]]), [px[0], px[1], 1])[:2]
            z['pxt'][bid] = [round(float(q[0]), 1), round(float(q[1]), 1)]
            z['naer'].append(dict(id=bid, avstand_px=round(float(d), 1), grunn='fasade_kilde=kvartaltegning, ellers ukoblet'))
            z['hb'].append((plass[bid], bid))

    for t in tegninger:
        if '_t' not in t: continue
        z = t.pop('_t'); hb = z['hb']; n = t['navn']
        ids = [bid for _, bid in hb]
        kvt = sum(1 for i, _ in hb if bygg[i].get('fasade_kilde') == 'kvartaltegning')
        ant = sum(1 for i, _ in hb if bygg[i].get('fasade_kilde') == 'antatt')
        t.update(bygg=ids, antall=len(ids), fasade_kvartaltegning=kvt, fasade_antatt=ant, fasade_ingen=len(ids) - kvt - ant,
                 bygg_naer=z['naer'], bygg_manuelt=z['manuelt'], kant=[bid for _, bid in z['kb'] if bid not in ids])
        if ids:
            S = np.array([_sentroide(bygg[i]['p']) for i, _ in hb])
            c = S.mean(0)
            alle = np.concatenate([np.asarray(bygg[i]['p'], float) for i, _ in hb])
            ut = max(np.ptp(alle[:, 0]), np.ptp(alle[:, 1]), 25.0 if len(hb) >= 3 else 100.0)   # ett-to bygg: minst 100 m, så kirketårnet og naboene kommer med
            zoom = float(np.clip(372 / (0.95 * ut), 1.0, 6.0))   # 0,95: modellbildet havner omtrent i tegningens målestokk (similariteten ~1)
            naer = set(x['id'] for x in z['naer'] + z['manuelt'])
            visninger.append(dict(n=n, cx=round(float(c[0]), 2), cy=round(float(c[1]), 2), zoom=round(zoom, 2), vinkler=VINKLER,
                                  bygg=[dict(id=bygg[i]['id'], x=round(float(s[0]), 2), y=round(float(s[1]), 2), h=float(bygg[i].get('h') or 6),
                                             px_tegning=z['pxt'][bygg[i]['id']], fasade=bygg[i].get('fasade_kilde'), runde2=bygg[i]['id'] in naer)
                                        for (i, _), s in zip(hb, S)]))
    dobbel = {}
    for t in tegninger:
        for bid in t.get('bygg', []): dobbel.setdefault(bid, []).append(t['navn'])
    ut_json = dict(laget='2026-10-28', verktoy='verktoy/kvartal_qa.py',
                   metode='SIFT + RANSAC similaritet tegning->2019-trykk over flere rasterskalaer; bygg = gml=1, ikke skjult, '
                          f'px2019 (rapport/farger2019.json) innenfor tegningens tegnede omriss utvidet {UTVID} px i trykket. '
                          f'«kant» = bygg som bare treffer små biter av nabokvartal i kanten av tegningen (< {int(KANT_ANDEL*100)} % av hovedmotivet). '
                          f'Runde 2: en tegnet bit uten bygg får nærmeste ukoblede bygg innenfor {NAER_PX} px (bygg_naer); bygg_manuelt er satt for hånd med grunn.',
                   gml_bygg_uten_px2019=uten_px,
                   bygg_i_flere_tegninger={k: v for k, v in dobbel.items() if len(v) > 1},
                   tegninger=tegninger)
    json.dump(ut_json, open(KOBLING, 'w'), ensure_ascii=False, indent=1)
    json.dump(visninger, open(os.path.join(ARB, 'visninger.json'), 'w'), ensure_ascii=False, indent=1)
    alle_koblet = set(dobbel)
    gml = [b['id'] for b in bygg if b.get('gml') == 1 and not b.get('skjul')]
    print('gml-bygg', len(gml), 'koblet', len(alle_koblet), 'i flere', len(ut_json['bygg_i_flere_tegninger']), 'uten px2019', len(uten_px))
    for t in tegninger:
        print(t['navn'], t.get('antall'), 'kvt', t.get('fasade_kvartaltegning'), 'kant', len(t.get('kant', [])), 'res', t.get('residual_median_px'), 'inl', t.get('inliers'))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'rastrer': rastrer()
    elif cmd == 'registrer': registrer()
    elif cmd == 'kobling': kobling()
    elif cmd == 'ark':
        import importlib.util
        spec = importlib.util.spec_from_file_location('kvartal_ark', os.path.join(ROT, 'verktoy', 'kvartal_ark.py'))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.main()
    else: print(__doc__)
