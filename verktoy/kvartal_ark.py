"""Kvartal-QA: kontrollark per kvartaltegning (tegning til venstre, modell til høyre i samme utsnitt og målestokk) + oversiktsark.
Kalles som `python3 -I verktoy/kvartal_qa.py ark` etter kvartal_bilder.mjs. Leser kilder/kvartal-kobling.json,
rapport/kvartal-qa/_arbeid/ (visninger, modellbilder med skjermposisjoner) og tegningsrasteret i kilder/kvartal-ai/png/.

Vinkelvalg (målt, ikke skjønn): for hver vinkel tilpasses en similaritet (RANSAC) fra byggenes skjermpunkt i modellbildet
(midt på veggen, __skjerm3) til byggenes punkt i tegningen (px2019 ført tilbake gjennom registreringen). Vinkelen med lavest
median restavvik vinner. Restavviket oppgis i trykkpiksler (× tegningsskalaen ~0,32), så det kan sammenlignes med at px2019
selv bommer 5–25 px. Samme similaritet brukes til å legge modellbildet i tegningens utsnitt og målestokk.
"""
import os, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROT)
import datalag

UT = os.path.join(ROT, 'rapport', 'kvartal-qa'); ARB = os.path.join(UT, '_arbeid')
PNG = os.path.join(ROT, 'kilder', 'kvartal-ai', 'png')
BREDDE = 1600; PANEL = 780; GAP = 13
C_ZOOM = 4.5
PX_PER_M = 3.245   # trykkpiksler per meter på bakken: skalaen i kilder/ai/ai/modell_h_til_2019.npy dekomponert (asimut 340°, høyde 50°)
FARGE = {'kvartaltegning': (0, 130, 60), 'antatt': (215, 110, 0), None: (110, 110, 110)}


def font(sz, fet=False):
    for p in (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if fet else []) + ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


F_T, F_S, F_L, F_X = font(30, True), font(17), font(13, True), font(14)


def kort(bid):
    return bid.replace('bnr-', '')[-5:] if bid.startswith('bnr-') else bid


def tilpass(src, dst):
    src = np.float32(src); dst = np.float32(dst)
    if len(src) < 3: return None, None, 0
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=60, maxIters=5000, confidence=0.999)
    if M is None: return None, None, 0
    inl = inl.ravel().astype(bool)
    r = np.linalg.norm(src @ M[:, :2].T + M[:, 2] - dst, axis=1)
    return M, float(np.median(r[inl])), int(inl.sum())


def tilpass_rot0(src, dst):
    """Skala + forskyvning, rotasjon låst til 0 (tegningen og modellbildet skal stå samme vei opp om vinkelen er riktig).
    Robust: minste kvadrater, kast punkt over 2,5 × median, tilpass på nytt (3 runder)."""
    src = np.float64(src); dst = np.float64(dst); keep = np.ones(len(src), bool)
    if len(src) < 2: return None, None, 0
    for _ in range(3):
        a, b = src[keep], dst[keep]
        A = np.zeros((2 * len(a), 3)); A[0::2, 0] = a[:, 0]; A[0::2, 1] = 1; A[1::2, 0] = a[:, 1]; A[1::2, 2] = 1
        (sk, tx, ty), *_ = np.linalg.lstsq(A, b.ravel(), rcond=None)
        r = np.linalg.norm(src * sk + [tx, ty] - dst, axis=1)
        med = np.median(r[keep]); ny = r <= max(2.5 * med, 20)
        if ny.sum() < 2 or (ny == keep).all(): break
        keep = ny
    M = np.array([[sk, 0, tx], [0, sk, ty]])
    return M, float(np.median(r[keep])), int(keep.sum())


def tilpass_fast(src, dst, sk):
    """Målestokken er kjent (tegningspiksler per meter / skjermpiksler per meter), rotasjonen låst til 0: bare forskyvningen
    tilpasses, som median av differansene (robust mot px2019 som bommer)."""
    src = np.float64(src); dst = np.float64(dst)
    if len(src) < 1: return None, None, 0
    t = np.median(dst - sk * src, axis=0)
    r = np.linalg.norm(sk * src + t - dst, axis=1)
    return np.array([[sk, 0, t[0]], [0, sk, t[1]]]), float(np.median(r)), len(src)


def merk(d, xy, tekst, farge, f=F_L):
    x, y = xy
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=farge, outline=(255, 255, 255))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1): d.text((x + 6 + dx, y - 8 + dy), tekst, fill=(255, 255, 255), font=f)
    d.text((x + 6, y - 8), tekst, fill=farge, font=f)


def main():
    K = json.load(open(os.path.join(ROT, 'kilder', 'kvartal-kobling.json')))
    V = {v['n']: v for v in json.load(open(os.path.join(ARB, 'visninger.json')))}
    data = datalag.koble_til_plass(datalag.alle()); bygg = {b['id']: b for b in data['bygg']}
    # målestokk per zoom fra tegningene som kan tilpasses (az 20), til arkene med for få bygg
    global C_ZOOM
    cz = []
    for t in K['tegninger']:
        v = V.get(t['navn']); jf = os.path.join(ARB, f"{t['navn']}-az20.json")
        if not v or not os.path.exists(jf): continue
        J = json.load(open(jf)); pt = {b['id']: b['px_tegning'] for b in v['bygg'] if not b.get('runde2')}
        par = [(b['midt'], pt[b['id']]) for b in J['bygg'] if b['id'] in pt]
        M, med, ni = tilpass_rot0([p[0] for p in par], [p[1] for p in par])
        if M is not None and ni >= 3: cz.append(M[0, 0] * J['zoom'])
    C_ZOOM = float(np.median(cz)) if cz else 4.5
    print('målestokk × zoom', round(C_ZOOM, 3), 'fra', len(cz), 'ark', [round(c, 2) for c in cz])
    stat = {}
    for t in K['tegninger']:
        n = t['navn']; v = V.get(n)
        if not v: print('ingen visning', n); continue
        teg = Image.open(os.path.join(PNG, n + '.png')).convert('RGB'); tw, th = teg.size
        skala_trykk = t.get('skala') or 0.322
        fasade = {b['id']: b.get('fasade') for b in v['bygg']}
        runde2 = {b['id'] for b in v['bygg'] if b.get('runde2')}
        pt_teg = {b['id']: b['px_tegning'] for b in v['bygg']}
        # vinkelvalg
        resultat = {}
        for az in v['vinkler']:
            jf = os.path.join(ARB, f'{n}-az{az}.json')
            if not os.path.exists(jf): continue
            J = json.load(open(jf))
            par = [(b['midt'], pt_teg[b['id']]) for b in J['bygg'] if b['id'] not in runde2]
            # målestokk: trykket har PX_PER_M trykkpiksler per meter (modell_h_til_2019 dekomponert), tegningen skala_trykk trykkpiksler per tegningspiksel,
            # modellbildet J.kam.mpp meter per skjermpiksel
            sk = PX_PER_M / skala_trykk * J['kam']['mpp']
            M, med, ninl = tilpass_fast([p[0] for p in par], [p[1] for p in par], sk)
            Mfri, medfri, _n = tilpass([p[0] for p in par], [p[1] for p in par])
            resultat[az] = dict(J=J, M=M, med_teg=med, inliers=ninl, n=len(par), med_fri_trykk=None if medfri is None else medfri * skala_trykk,
                                rot_fri=None if Mfri is None else float(np.degrees(np.arctan2(Mfri[1, 0], Mfri[0, 0]))),
                                med_trykk=None if med is None else med * skala_trykk,
                                skala=None if M is None else float(np.hypot(*M[:, 0])))
        if not resultat: print('mangler modellbilder', n); continue
        maalbare = {az: r for az, r in resultat.items() if r['M'] is not None and r['n'] >= 3}
        if maalbare:
            valgt = min(maalbare, key=lambda az: maalbare[az]['med_teg']); grunn = 'lavest restavvik'
        else:
            valgt = 20 if 20 in resultat else list(resultat)[0]; grunn = 'for få bygg til å måle; vinkelen fra trykket (az 20)'
        R = resultat[valgt]; J = R['J']
        mod = Image.open(os.path.join(ARB, f'{n}-az{valgt}.png')).convert('RGB')
        # modellbildet i tegningens utsnitt: similariteten om den finnes, ellers skalert så byggenes punkt dekker samme bredde
        M = R['M'] if valgt in maalbare else None
        if M is None:
            ps = np.array([b['midt'] for b in J['bygg']], float); pt = np.array([pt_teg[b['id']] for b in J['bygg']], float)
            # for få bygg til å velge vinkel: samme kjente målestokk (PX_PER_M, kam.mpp), plassert på snittet av alle byggpunktene (også runde 2)
            s = PX_PER_M / skala_trykk * J['kam']['mpp']
            c0 = ps.mean(0); c1 = pt.mean(0)
            M = np.array([[s, 0, c1[0] - s * c0[0]], [0, s, c1[1] - s * c0[1]]])
            utsnitt = f'målestokk fra kameraet, plassert på {len(ps)} byggpunkt (usikkert)'
        else:
            utsnitt = 'målestokk fra kameraet, forskyvning fra byggpunktene'
        modw = cv2.warpAffine(np.array(mod), M, (tw, th), flags=cv2.INTER_LINEAR, borderValue=(235, 235, 235))
        Mdel = {}
        if t.get('deler'):
            # tegningen er satt sammen av hus fra hver sin kant av byen: hvert utsnitt får sitt eget hus, plassert midt i utsnittet
            modw[:] = 235
            for dl in t['deler']:
                x0, y0, bw, bh = dl['utsnitt_i_tegningen']; c = np.array([x0 + bw / 2, y0 + bh / 2])
                b = min(J['bygg'], key=lambda b: np.hypot(*(np.array(pt_teg[b['id']]) - c)) if b['id'] not in Mdel else 1e9)
                Md = M.copy(); Md[:, 2] = c - Md[:, :2] @ np.array(b['midt']); Mdel[b['id']] = Md
                pad = 60; X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(tw, x0 + bw + pad), min(th, y0 + bh + pad)
                w_ = cv2.warpAffine(np.array(mod), Md, (tw, th), flags=cv2.INTER_LINEAR, borderValue=(235, 235, 235))
                modw[Y0:Y1, X0:X1] = w_[Y0:Y1, X0:X1]
            utsnitt = 'delt: hvert hus i tegningen har sitt eget modellutsnitt'
        modw = Image.fromarray(modw)
        # felles skala inn i panelene
        k = min(PANEL / tw, 620 / th) if th > tw * 0.8 else PANEL / tw
        pw, ph = int(tw * k), int(th * k)
        tegp = teg.resize((pw, ph), Image.LANCZOS); modp = modw.resize((pw, ph), Image.LANCZOS)
        dt, dm = ImageDraw.Draw(tegp), ImageDraw.Draw(modp)
        for b in J['bygg']:
            bid = b['id']; f = FARGE.get(fasade.get(bid), FARGE[None]); lab = kort(bid) + ('~' if bid in runde2 else '')
            Mb = Mdel.get(bid, M)
            for dd, pnt in ((dt, np.array(pt_teg[bid]) * k), (dm, (Mb[:, :2] @ np.array(b['midt']) + Mb[:, 2]) * k)):
                inne = 0 <= pnt[0] < pw and 0 <= pnt[1] < ph
                c = np.clip(pnt, [6, 10], [pw - 70, ph - 10])     # punkt utenfor utsnittet: merket settes i kanten med «(utenfor)»
                merk(dd, c, lab if inne else lab + ' (utenfor)', f)
        # arket
        TOP = 118
        ider = t['bygg']
        linjer = []
        cur = ''
        for bid in ider:
            b = bygg[bid]; nav = b.get('navn')
            s_ = f"{kort(bid)}={bid}" + (f" {nav}" if nav else '') + f" ({'tegning' if b.get('fasade_kilde') == 'kvartaltegning' else (b.get('fasade_kilde') or 'ingen')}, h {b.get('h')})"
            if len(cur) + len(s_) > 170: linjer.append(cur); cur = ''
            cur += ('   ' if cur else '') + s_
        if cur: linjer.append(cur)
        Hark = TOP + ph + 40 + 20 * len(linjer) + 70
        ark = Image.new('RGB', (BREDDE, Hark), (255, 255, 255)); d = ImageDraw.Draw(ark)
        d.text((GAP, 10), f"{n}", fill=(0, 0, 0), font=F_T)
        d.text((GAP + 10 + d.textlength(n, font=F_T), 22),
               f"{t['antall']} bygg  ·  fasade fra tegning {t['fasade_kvartaltegning']}  ·  antatt {t['fasade_antatt']}" + (f"  ·  uten fasadekilde {t['fasade_ingen']}" if t['fasade_ingen'] else ''),
               fill=(30, 30, 30), font=F_S)
        reg = (f"registrering mot 2019-trykket: {t['residual_median_px']} px median, {t['inliers']} inliers" if t.get('residual_median_px') is not None
               else f"registrering: {t.get('registreringsmetode')}")
        vinktekst = '  ·  '.join(f"az {az}: {('%.0f px' % r['med_trykk']) if r['med_trykk'] is not None else '–'}" +
                                 (f", fri dreining {r['rot_fri']:.0f}°" if r.get('rot_fri') is not None else '') for az, r in resultat.items())
        d.text((GAP, 52), f"Vinkel az {valgt} ({grunn}). Restavvik byggpunkt (trykk-px, n={R['n']}): {vinktekst}", fill=(70, 70, 70), font=F_S)
        d.text((GAP, 76), f"{reg}  ·  modellutsnitt: {utsnitt}  ·  modell v{open(os.path.join(ROT, 'VERSJON')).read().strip()}  ·  28.10.2026", fill=(70, 70, 70), font=F_S)
        ark.paste(tegp, (GAP, TOP)); ark.paste(modp, (GAP * 2 + PANEL, TOP))
        d.rectangle([GAP * 2 + PANEL, TOP, GAP * 2 + PANEL + pw, TOP + ph], outline=(200, 200, 200))
        y = TOP + ph + 6
        d.text((GAP, y), 'Strektegning 2015 (Page Black)', fill=(0, 0, 0), font=F_S)
        d.text((GAP * 2 + PANEL, y), f'3D-modellen, az {valgt}', fill=(0, 0, 0), font=F_S)
        y += 28
        d.text((GAP, y), 'Merker: grønn = fasade fra kvartaltegning, oransje = antatt (regler), grå = ingen fasadekilde; ~ = koblet i runde 2/for hånd. '
                         'Punktet i tegningen er px2019 ført tilbake (kan bomme 15–80 px her).', fill=(90, 90, 90), font=F_X)
        y += 24
        for l in linjer: d.text((GAP, y), l, fill=(40, 40, 40), font=F_X); y += 20
        if ark.width > BREDDE: ark = ark.resize((BREDDE, int(ark.height * BREDDE / ark.width)))
        ark.save(os.path.join(UT, n + '.jpg'), quality=86, optimize=True)
        stat[n] = dict(valgt_az=valgt, grunn=grunn, vinkler={az: dict(median_trykk_px=None if r['med_trykk'] is None else round(r['med_trykk'], 1),
                                                                      inliers=r['inliers'], n=r['n'], skala=None if r['skala'] is None else round(r['skala'], 3),
                                                                      fri_rotasjon_grader=None if r['rot_fri'] is None else round(r['rot_fri'], 1),
                                                                      median_fri_trykk_px=None if r['med_fri_trykk'] is None else round(r['med_fri_trykk'], 1)) for az, r in resultat.items()})
        print(n, stat[n])
    json.dump(stat, open(os.path.join(UT, 'vinkler.json'), 'w'), ensure_ascii=False, indent=1)
    oversikt(K, data['bygg'], stat)


def oversikt(K, bygg, stat):
    """Plan over Gamlebyen: hvert gml-bygg farget etter tegningen det er koblet til, ukoblede i rødt omriss. Ingen trykk/tegning i bildet."""
    gml = [b for b in bygg if b.get('gml') == 1 and not b.get('skjul')]
    P = np.concatenate([np.asarray(b['p'], float) for b in gml])
    x0, y0 = P.min(0) - 10; x1, y1 = P.max(0) + 10
    W = BREDDE; s = (W - 40) / (x1 - x0); H = int((y1 - y0) * s) + 40
    tab_h = 30 + 24 * (len(K['tegninger']) + 2)
    im = Image.new('RGB', (W, H + tab_h), (255, 255, 255)); d = ImageDraw.Draw(im)
    til = lambda q: [(20 + (x - x0) * s, 20 + (y1 - y) * s) for x, y in q]
    rng = np.random.default_rng(7)
    farger = {t['navn']: tuple(int(c) for c in rng.integers(60, 210, 3)) for t in K['tegninger']}
    eier = {}
    for t in K['tegninger']:
        for bid in t['bygg']: eier.setdefault(bid, []).append(t['navn'])
    for b in gml:
        e = eier.get(b['id'])
        if e: d.polygon(til(b['p']), fill=farger[e[0]], outline=(0, 0, 0) if len(e) == 1 else (255, 0, 255))
        else: d.polygon(til(b['p']), fill=(245, 245, 245), outline=(220, 0, 0))
    for t in K['tegninger']:
        ps = [np.asarray(next(b for b in gml if b['id'] == bid)['p'], float).mean(0) for bid in t['bygg']]
        if not ps: continue
        c = til([np.mean(ps, 0)])[0]
        d.text((c[0] - 30, c[1] - 9), t['navn'], fill=(0, 0, 0), font=F_L, stroke_width=3, stroke_fill=(255, 255, 255))
    d.text((20, 4), 'Kvartal-QA 28.10.2026: hvilke bygg hver kvartaltegning viser (plan, nord opp). Rødt omriss = gml-bygg uten tegning; lilla omriss = koblet til flere tegninger.', fill=(0, 0, 0), font=F_S)
    y = H + 10
    hode = f"{'tegning':<16}{'bygg':>6}{'tegning':>9}{'antatt':>8}{'ingen':>7}{'resid.px':>10}{'inliers':>9}{'vinkel':>8}{'restavvik az20/az40 (trykk-px)':>34}"
    mono = None
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
        if os.path.exists(p): mono = ImageFont.truetype(p, 15)
    d.text((20, y), hode, fill=(0, 0, 0), font=mono or F_X); y += 24
    for t in K['tegninger']:
        st = stat.get(t['navn'], {}); vk = st.get('vinkler', {})
        rv = '/'.join(str(vk.get(az, {}).get('median_trykk_px')) if (vk.get(az, {}).get('n') or 0) >= 3 else '–' for az in (20, 40))
        rad = f"{t['navn']:<16}{t.get('antall', 0):>6}{t.get('fasade_kvartaltegning', 0):>9}{t.get('fasade_antatt', 0):>8}{t.get('fasade_ingen', 0):>7}{str(t.get('residual_median_px') if t.get('residual_median_px') is not None else 'anker'):>10}{str(t.get('inliers')):>9}{str(st.get('valgt_az', '–')):>8}{rv:>34}"
        d.text((20, y), rad, fill=(30, 30, 30), font=mono or F_X); y += 24
    if hode: pass
    im.save(os.path.join(UT, 'oversikt.jpg'), quality=88, optimize=True)
    print('oversikt', im.size)
