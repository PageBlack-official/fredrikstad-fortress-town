"""Landemerkene (30.10, natt/landemerker): det besøkende kjenner igjen, bygd etter Vegars 2015-tegninger (form), Kartverkets
DOM−DTM (plass og høyde) og Street View / ortofoto 2024 (dagens farger). Kjøres sist i kjeden (etter fasade_former.py), så
ingen annen rettelse overstyrer den. Hver post under LANDEMERKER sier hva som settes og hvorfor; elementene tegnes av src/07
(bygTaarn for deler med form 'taarn', bygArkade for bygg.arkader) og src/10 (portbyggene, data/porter.json).

    python3 verktoy/landemerker.py [--tørt]

Elementene er generelle (et nytt tårn eller en ny arkade = en ny post her, ingen ny kode):
  taarn    bygg.deler[] {form: 'taarn', c, r, sider, rot, skaft, krage, h, ut, tinde_h, tinder, vegg, veggs, topp, vinduer, stang, flagg}
  arkader  bygg.arkader[] {a, b, z0, h, topp, n, bredde, dybde, mork, felt?}   rundbuer med dybde langs veggen a→b; felt {z0, z1,
           bredde, dybde}: høye innfelte felt over hver bue i etasjen over (lisener mellom)
  fasade   vinduer erstattet på én fasade (polylinje i modellmeter): elementer i u (meter fra første punkt)
  atrium   bygg.atrium {gaard, kant, z, topp, glass, ramme} + ringtak (tak2/gavl2) fra kilder/atrier.json: gårdsrom med
           glasspyramide (kvadrat) eller glassvalm (rektangel) og ring av tak rundt (bygAtrium i src/07)
"""
import json, math, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, "verktoy"))
import datalag

GRUNN = 'landemerker (verktoy/landemerker.py, 30.10)'
DATO = '2026-10-30'

RAADHUS = 'bnr-193972012'
# Rådhuset (Langlet 1864). Kvartal14.ai: åttekantet tårn i lys sandstein med ett høyt rundbuevindu (lameller) per side under en
# utkraget, krenelert brystning på konsoller, flatt tak og flaggstang; ingen hjelm, lanterne eller urskive. Gatefasaden mot SSV har
# hjørnefelt | fem store rundbuer nede og fem rundbuevinduer oppe | smalt felt med rundbuet dør.
# DOM−DTM (Kartverket, 1 m): tårnet er et platå på 19,8–20,0 m over 4 × 4 ruter med midtpunkt (28,5, −87,8); taket rundt 10–12 m,
# takfoten mot gata 9–10 m (rapport/hoyder hadde 6,5 m med takhelning 0,73 = middels sikkerhet; tak_enkel.py tilpasset 9,79 m og 0,35,
# som gir mønet på 12,3 m mot DOM 12,1 m). Ortofoto 2024: åttekantet krans med tinder, ca. 4,3 m i diameter, lys grå flate inni;
# toppen står 5,5 m vest for DOM-platået fordi høye ting heller bort fra fotopunktet (relieffforskyvning), DOM ser loddrett.
# Tegningen: tårnaksen står 2,3 pt (< 0,5 m) fra DOM-aksen projisert med kontrollkameraet; toppen er tegnet 38 pt høyere, det
# samme som 45 % overhøyde (20 m · 4,28 pt/m · 0,45 = 38,5 pt), og tårnet er tegnet ca. 40 % bredere (5,8 mot 4,2 m). Tegningen
# har altså tårnet på samme sted, bare forstørret som landemerke.
RAADHUS_TAARN = dict(form='taarn', c=[28.5, -87.8], r=1.75, sider=8, rot=0, skaft=18.2, krage=0.7, h=20.0, ut=0.4, tinde_h=0.7,
                     tinder=16, vegg=[223, 184, 146], veggs=[206, 143, 81], topp=[200, 198, 192],
                     vinduer=dict(z=16.05, b=0.75, h=2.3), stang=3.0, flagg=[186, 12, 47], p=[[26.6, -89.7], [30.4, -89.7], [30.4, -85.9], [26.6, -85.9]],
                     kilde='form: Kvartal14.ai; plass og høyde: DOM−DTM (platå 19,8–20,0 m); diameter: ortofoto 2024 (4,3 m) og DOM; '
                           'farger: tegningens lyse og skyggeside (sandstein), toppen lys grå som i ortofotoet')
# gatefasaden (polylinje vest -> øst, veggene 0 og 18 i omrisset), elementene i meter fra vestenden
RAADHUS_FASADE = dict(linje=[[14.2, -93.92], [26.64, -97.6], [35.16, -100.43]], felt=[0.0, 3.1, 18.4, 21.95],
                      vinduer=[  # (u, z midt, b, h, typ, bue): typ 0 bue 1 = rundbuevindu, typ 2 = port med buet topp
                          (1.1, 6.6, 0.6, 1.8, 0, 1), (2.0, 6.6, 0.6, 1.8, 0, 1), (1.55, 2.4, 1.2, 2.0, 0, 1)] +
                          [(3.1 + (k + 0.5) * 15.3 / 5, 6.3, 1.5, 2.6, 0, 1) for k in range(5)] +
                          [(20.2, 1.6, 1.7, 3.2, 2, 0), (19.7, 6.0, 0.6, 1.8, 0, 1), (20.7, 6.0, 0.6, 1.8, 0, 1)],
                      arkade=dict(u0=3.1, u1=18.4, z0=0.5, h=3.6, topp=4.0, n=5, bredde=1.9, dybde=0.45, mork=[44, 48, 56]))

ARKADE_13394024 = dict(a=[-44.58, 47.49], b=[-31.55, 43.06], z0=0.0, h=2.9, topp=3.5, n=5, bredde=2.1, dybde=0.5, mork=[34, 33, 33],
                       felt=dict(z0=3.8, z1=6.0, bredde=2.0, dybde=0.15),
                       kilde='Kvartal10.ai: gårdsfasaden mot sør har en åpen arkade med fem rundbuer nede og gesimsbånd over; etasjen over har '
                             'høye, smale felt mellom lisener med samme deling som buene (ett felt over hver bue, felt 0,77 av delingen), fra like over '
                             'gesimsen til like under takfoten (natt/atrium 30.10)')

VOLDPORTEN = 'bnr-193869548'
# Voldporten (1695). DTM under huset er vollkrona (9,4–10,4 moh), så DOM−DTM (4–8 m) måler fra vollen, ikke fra veien. Veien i
# porten: 7,0 moh på innsiden (vest), 6,3 på utsiden (øst). DOM: mønet 17,8 moh, takfoten ca. 14,5. Fra veien: takfot 7,5 m, møne
# 10,8 m. Street View aug. 2010 (yttersiden SØ): portmur i grå naturstein med rundbuet tunnel (bredde ca. 0,47 av muren, toppen ca.
# 0,8 av murhøyden), hvitkalket vaktstue oppå, valmet teglstak med kort møne og én pipe midt på mønet. Tegningen (Glasshytta.ai,
# egen bit) viser det samme: huset på portmuren, valm mot enden.
VOLDPORT_PORT = dict(h=4.4, pw=3.8, ph=3.5)
# Vingemurene (30.10, natt/atrium): grå naturstein som holder vollen på hver side av porten.
#  SØ (yttersiden): Street View aug. 2010 viser to skrå murer fra hjørnene av portmuren, toppen fra portmurens gesims (4,4 m) ned
#  til gresset ved foten; brukerfotoet aug. 2019 viser den nordre fra siden (rett mur, skrå kappe). Ortofoto 2024 ser kappene ovenfra
#  som lyse striper fra hjørnene til foten: nordre fot (225,1, 37,0), søndre fot (221,1, 30,1). Foten ligger på bakken og står der
#  fotoet viser den (ingen relieffforskyvning); toppen ved porten er forskjøvet 0,5–1 m i fotoet, så muren går fra portmurens hjørne
#  (kommunekartet) til foten: 8,4 og 7,7 m, begge ca. 4° med klokka fra portaksen (svakt utoverspriket i Street View er perspektiv).
#  Foten stemmer med DTM: vollskråningen når veinivå (6,2–6,7 moh) ved x ≈ 225 (nord) og 221 (sør).
#  NV (innsiden): Street View aug. 2010 viser lave natursteinsmurer (ca. 1,3 m, en person ved porten til målestokk) fra portens
#  hjørner ut mot vollen på begge sider, foten nærmere kameraet enn porten (svakt utover); ortofotoet ser ikke dit (trær og skygge).
#  Lengden 4 m og vinkelen 30° ut fra fasadelinjen er lest av bildet (usikkert ±1 m, ±15°).
# Felt per mur: (ende 'SØ'/'NV', hjørne 'nord'/'sør', fot [x, y] eller None, sprik i grader ut fra fasadelinjen (når foten ikke er målt),
# lengde, høyde ved porten, høyde ved foten, tykkelse)
VOLDPORT_VINGER = [('SØ', 'nord', [225.1, 37.0], None, None, 4.4, 0.4, 0.8), ('SØ', 'sør', [221.1, 30.1], None, None, 4.4, 0.4, 0.8),
                   ('NV', 'nord', None, 30.0, 4.0, 1.3, 1.3, 0.6), ('NV', 'sør', None, 30.0, 4.0, 1.3, 1.3, 0.6)]


def vingemurer(p, ret):
    """Vingemurene som [x0, y0, x1, y1, h0, h1, tykk] (innerflatens linje fra porten ut, høyde over veien i porten), fra
    portbyggets omriss og veiretningen (ret peker inn mot byen, mot NV)."""
    import numpy as np
    P = [np.array(q[:2], float) for q in p[:4]]
    inn = np.array(ret, float) / np.hypot(*ret); c = sum(P) / 4
    # endene: kantene som står mest på tvers av veien
    kanter = sorted([(abs(((P[(k + 1) % 4] - P[k]) / np.hypot(*(P[(k + 1) % 4] - P[k]))) @ inn), k) for k in range(4)])[:2]
    ut = []
    for ende, side, fot, sprik, L, h0, h1, t in VOLDPORT_VINGER:
        for _, k in kanter:
            a, b = P[k], P[(k + 1) % 4]; m = (a + b) / 2
            if (ende == 'NV') != ((m - c) @ inn > 0):
                continue
            nord = a if a[1] > b[1] else b
            sor = b if nord is a else a
            q = nord if side == 'nord' else sor
            ax = -inn if ende == 'SØ' else inn                 # utover fra porten langs veien
            tv = (q - m) / np.hypot(*(q - m))                    # ut fra aksen, på tvers
            if fot is not None:
                e = np.array(fot, float)
            else:                                                # langs fasadelinjen ut fra hjørnet, sprik utover langs veien
                v = np.radians(sprik); e = q + (tv * np.cos(v) + ax * np.sin(v)) * L
            ut.append([round(float(q[0]), 2), round(float(q[1]), 2), round(float(e[0]), 2), round(float(e[1]), 2), h0, h1, t])
    return ut
# vaktstuens vinduer (høyde over portmuren): SSV-langsida som Glasshytta.ai (dør ved vestenden, to vinduer; andeler 0,25, 0,53, 0,81
# av fasaden målt i tegningen), NV-enden som Street View aug. 2010 (to vinduer med 2 x 3 ruter ved 0,30 og 0,65 av bredden).
# SØ-enden (yttersiden) har ingen vinduer, bare relieffet og to blindfelt (Street View 2010); tegningens tomme ramme der er blindfeltet.
VOLDPORT_FASADER = [dict(linje=[[201.31, 40.3], [214.4, 33.99]], andeler=True,
                         vinduer=[(0.25, 1.05, 0.9, 2.0, 1, 0), (0.53, 1.75, 0.8, 1.1, 0, 0), (0.81, 1.75, 0.8, 1.1, 0, 0)]),
                    dict(linje=[[201.31, 40.3], [204.74, 47.43]], andeler=True,
                         vinduer=[(0.30, 1.75, 0.8, 1.2, 0, 0), (0.65, 1.75, 0.8, 1.2, 0, 0)])]


ATRIER = json.load(open(os.path.join(ROT, 'kilder', 'atrier.json'), encoding='utf8'))['hus']
KAPP = 7.5 / 0.82            # som tak.py: over t = KAPP er taket flatt


def _halvplan(a, b, c, bounds):
    """{p: a*x + b*y + c <= 0} innenfor bounds (utvidet)."""
    from shapely.geometry import Polygon, box
    x0, y0, x1, y1 = bounds; B = box(x0 - 60, y0 - 60, x1 + 60, y1 + 60)
    n = math.hypot(a, b)
    if n < 1e-12:
        return B if c <= 0 else Polygon()
    a, b, c = a / n, b / n, c / n
    p0 = (-a * c, -b * c); u = (-b, a); R = 1e4
    return Polygon([(p0[0] + u[0] * R, p0[1] + u[1] * R), (p0[0] - u[0] * R, p0[1] - u[1] * R),
                    (p0[0] - u[0] * R - a * R, p0[1] - u[1] * R - b * R), (p0[0] + u[0] * R - a * R, p0[1] + u[1] * R - b * R)]).intersection(B)


def atrium_plan(x, A, wg=None, kapp=KAPP):
    """Ringtaket rundt et (konvekst) gårdsrom som rett skjelett der bare noen yttervegger har takfot (A['takfot']: punkter på
    dem); de andre er brannmurer, og taket stiger fra gårdsrommet opp mot dem. Med konvekst gårdsrom og takfot på rette
    yttervegger er skjelettet eksakt: t(p) = min( min_s d_s(p), max_k g_k(p) ), d_s = avstanden inn fra takfotveggen s,
    g_k = avstanden ut fra gårdsromskanten k (det skarpe offsetet av et konvekst polygon er maks av kantavstandene).
    Fløyene kan ha ulik helning (Kartverkets DOM: nordfløyen er brattere mot gata enn mot gården, vestfløyen er et slakt
    pulttak): flaten mot gårdsromskant k får helning wg[k] ganger takfotsidens. Det er et vektet rett skjelett, og formelen
    holder fortsatt (offsetet av et konvekst polygon med vektede kanter er maks av de vektede kantavstandene).
    Gir (U, S, K, t_fun): ringen, takfotplanene og gårdsromsplanene [(navn, a, b, c)] med t = a*x + b*y + c, og t (vektorisert)."""
    import numpy as np
    from shapely.geometry import Polygon, Point, LineString
    from shapely.geometry.polygon import orient
    P = orient(Polygon(x['p']).buffer(0), 1.0); G = orient(Polygon(A['gaard']), 1.0)
    U = P.difference(G)
    plan = []
    R = list(P.exterior.coords)[:-1]
    for k in range(len(R)):
        a, b = np.array(R[k]), np.array(R[(k + 1) % len(R)]); L = np.hypot(*(b - a))
        if L < 0.3 or not any(LineString([a, b]).distance(Point(q)) < 0.6 for q in A['takfot']):
            continue
        n = np.array([-(b - a)[1], (b - a)[0]]) / L                  # innover (ytre ring mot klokka)
        plan.append(('takfot', float(n[0]), float(n[1]), float(-n @ a)))
    if not plan:
        raise SystemExit(f"{x['id']}: ingen takfotvegg ved punktene {A['takfot']}")
    Rg = list(G.exterior.coords)[:-1]
    for k in range(len(Rg)):
        a, b = np.array(Rg[k]), np.array(Rg[(k + 1) % len(Rg)]); L = np.hypot(*(b - a))
        n = np.array([(b - a)[1], -(b - a)[0]]) / L                  # utover fra gårdsrommet
        w = 1.0 if wg is None else wg[k]                              # wg[k]: helningen mot gårdsromskant k / takfotsidens
        plan.append(('gaard', float(n[0]) * w, float(n[1]) * w, float(-n @ a) * w))
    S = [q for q in plan if q[0] == 'takfot']; K = [q for q in plan if q[0] == 'gaard']
    def t_fun(X, Y):
        ds = np.min([a * X + b * Y + c for _, a, b, c in S], axis=0); gk = np.max([a * X + b * Y + c for _, a, b, c in K], axis=0)
        return np.clip(np.minimum(ds, gk), 0, kapp)
    return U, S, K, t_fun


def atrium_tak(x, A, wg=None, kapp=KAPP):
    """tak2 og gavl2 for ringtaket (formatet til tak.py: [x, y, t] per hjørne)."""
    import numpy as np
    from shapely.geometry import LineString, Polygon
    from shapely.geometry.polygon import orient
    from shapely.ops import unary_union
    import tak
    U, S, K, t_fun = atrium_plan(x, A, wg, kapp)
    KAPP = kapp
    bd = U.bounds; flater = []
    hp = lambda a, b, c: _halvplan(a, b, c, bd)
    # gårdsromsflatene: g_k er størst (maks) og ikke over noen takfotflate
    gfl = []
    for k, (_, a, b, c) in enumerate(K):
        F = U
        for m, (_, a2, b2, c2) in enumerate(K):
            if m != k: F = F.intersection(hp(a2 - a, b2 - b, c2 - c))
        for _, a2, b2, c2 in S:
            F = F.intersection(hp(a - a2, b - b2, c - c2))
        gfl.append(F); flater.append((F, (a, b, c)))
    # takfotflatene: d_s er minst blant takfotveggene; resten av ringen (det gårdsromsflatene ikke tar)
    rest = U.difference(unary_union([F.buffer(1e-7) for F in gfl]))
    for s, (_, a, b, c) in enumerate(S):
        F = rest
        for m, (_, a2, b2, c2) in enumerate(S):
            if m != s: F = F.intersection(hp(a - a2, b - b2, c - c2))
        flater.append((F, (a, b, c)))
    # flatt over KAPP
    ut = []
    for F, pl in flater:
        F1 = F.intersection(hp(pl[0], pl[1], pl[2] - KAPP)); ut.append((F1, pl))
        F2 = F.difference(F1)
        if F2.area > 0.05: ut.append((F2, (0.0, 0.0, KAPP)))
    tak2 = []
    for F, pl in ut:
        for g in getattr(F, 'geoms', [F]):
            if g.geom_type != 'Polygon' or g.area < 0.02: continue
            for e in tak._enkle(orient(g, 1.0)):
                cs = np.array(e.exterior.coords)[:-1]
                tak2.append([[round(float(px), 2), round(float(py), 2), round(float(min(max(pl[0] * px + pl[1] * py + pl[2], 0), KAPP)), 3)] for px, py in cs])
    # gavl2: ytterveggene uten takfot (brannmurene), fra veggtoppen opp til taket, delt der flaten under skifter
    P = orient(Polygon(x['p']).buffer(0), 1.0); R = list(P.exterior.coords)[:-1]; gavl2 = []
    for k in range(len(R)):
        seg = LineString([R[k], R[(k + 1) % len(R)]])
        for F, pl in ut:
            Sg = seg.intersection(F.buffer(1e-4))
            for s in getattr(Sg, 'geoms', [Sg]):
                if s.geom_type != 'LineString' or s.length < 0.05: continue
                (xa, ya), (xb, yb) = s.coords[0], s.coords[-1]
                ta = min(max(pl[0] * xa + pl[1] * ya + pl[2], 0), KAPP); tb = min(max(pl[0] * xb + pl[1] * yb + pl[2], 0), KAPP)
                if ta < 0.02 and tb < 0.02: continue
                gavl2.append([[round(xa, 2), round(ya, 2), round(float(ta), 3)], [round(xb, 2), round(yb, 2), round(float(tb), 3)]])
    return tak2, gavl2


def atrium_hoyde(x, A):
    """Ringtaket tilpasset Kartverkets DOM−DTM: h (takfot), th (helning mot gata) og wg[k] (helningen mot hver gårdsromskant
    i forhold til th), robust minste kvadrater (avvik over 3 m teller som 3 m), h som median av restene (som tak_enkel.py).
    Glassets topp: pyramide/valm fra karmen (h) til toppen, tilpasset DOM−DTM i gårdsrommet. Gir dict(h, th, wg, topp, rms, n)."""
    import numpy as np
    import tak_enkel as TE
    from scipy.optimize import minimize
    from shapely.geometry import Polygon
    U, S, K, _ = atrium_plan(x, A)
    pts, z = TE.dom_punkter(U, 0.5)
    ds = np.min([a * pts[:, 0] + b * pts[:, 1] + c for _, a, b, c in S], axis=0)
    G = np.array([a * pts[:, 0] + b * pts[:, 1] + c for _, a, b, c in K])
    def modell(v):
        th, sl = v[0], np.asarray(v[1:])
        m = np.clip(np.minimum(th * ds, np.max(sl[:, None] * G, axis=0)), 0, th * KAPP); return m, float(np.median(z - m))
    def feil(v):
        if v[0] < 0.1 or v[0] > 1.6 or min(v[1:]) < 0.05 or max(v[1:]) > 1.6: return 99.0
        m, h = modell(v); return float(np.sqrt(np.mean(np.minimum(np.abs(z - h - m), 3) ** 2)))
    best = None
    for th0 in (0.4, 0.6, 0.8):
        for s0 in (0.2, 0.45, 0.7):
            r = minimize(feil, [th0] + [s0] * len(K), method='Nelder-Mead', options=dict(xatol=1e-3, fatol=1e-4, maxiter=4000))
            if best is None or r.fun < best.fun: best = r
    v = best.x; m, h = modell(v); th = float(v[0])
    G2 = Polygon(A['gaard']); pg, zg = TE.dom_punkter(G2, 0.5)
    g = np.max([a * pg[:, 0] + b * pg[:, 1] + c for _, a, b, c in K], axis=0)          # <= 0 inne i gårdsrommet
    r = 1 - np.clip(-g / max(1e-6, float(-g.min())), 0, 1)                            # 0 i toppen, 1 ved karmen
    stig = float(np.linalg.lstsq((1 - r)[:, None], zg - h, rcond=None)[0][0])
    return dict(h=round(h, 2), th=round(th, 2), wg=[round(float(q) / th, 3) for q in v[1:]], topp=round(h + max(stig, 0.5), 2),
                rms=round(float(best.fun), 2), n=int(len(z)))


def valm_rektangel(p):
    """Valmtak (tak2-format, z = avstand inn fra takfoten, som tak_enkel.py) over et firkantet omriss: møne langs langsida, like
    fall på alle fire sider. Til hus tak_enkel.py ikke rører (portbyggene)."""
    import numpy as np
    P = [np.array(q[:2], float) for q in p[:4]]
    L01 = np.linalg.norm(P[1] - P[0]); L12 = np.linalg.norm(P[2] - P[1])
    if L12 > L01:
        P = P[1:] + P[:1]; L01, L12 = L12, L01
    w = L12 / 2; u = (P[1] - P[0]) / L01
    m0 = (P[0] + P[3]) / 2 + u * w; m1 = (P[1] + P[2]) / 2 - u * w
    r = lambda q, z: [round(float(q[0]), 2), round(float(q[1]), 2), round(z, 3)]
    return [[r(P[0], 0), r(P[1], 0), r(m1, w), r(m0, w)], [r(P[2], 0), r(P[3], 0), r(m0, w), r(m1, w)],
            [r(P[1], 0), r(P[2], 0), r(m1, w)], [r(P[3], 0), r(P[0], 0), r(m0, w)]]


def punkt_paa(linje, u):
    """Punkt og retning (enhetsvektor langs) u meter langs polylinjen."""
    for a, b in zip(linje, linje[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if u <= L or b is linje[-1]:
            t = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            return [a[0] + t[0] * u, a[1] + t[1] * u], t
        u -= L


def i_poly(p, P):
    inne = False
    for k in range(len(P)):
        (x1, y1), (x2, y2) = P[k][:2], P[k - 1][:2]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < (x2 - x1) * (p[1] - y1) / (y2 - y1 + 1e-12) + x1:
            inne = not inne
    return inne


def utover(x, p, t):
    n = (-t[1], t[0])
    if i_poly((p[0] + n[0] * 0.3, p[1] + n[1] * 0.3), x['p']):
        n = (-n[0], -n[1])
    return n


def fasade_vinduer(x, F):
    """Vinduene på fasaden erstattes: de gamle på linjen (normal som fasaden, under 0,6 m fra linjen) tas ut, de nye settes inn."""
    L = F['linje']; vind = [list(v) for v in (x.get('vind') or [])]
    def paa(v):
        for a, b in zip(L, L[1:]):
            Lab = math.hypot(b[0] - a[0], b[1] - a[1]); t = ((b[0] - a[0]) / Lab, (b[1] - a[1]) / Lab)
            n = utover(x, a, t); s = (v[0] - a[0]) * t[0] + (v[1] - a[1]) * t[1]; d = abs((v[0] - a[0]) * n[0] + (v[1] - a[1]) * n[1])
            if -0.5 <= s <= Lab + 0.5 and d < 0.6 and v[5] * n[0] + v[6] * n[1] > 0.95:
                return True
        return False
    beholdt = [v for v in vind if not paa(v)]
    nye = []
    Ltot = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(L, L[1:]))
    for u, z, b, h, typ, bue in F['vinduer']:
        if F.get('andeler'): u = u * Ltot
        # knekk i kommunekartets omriss teller som hjørne (regel 04): vinduet flyttes til halv bredde + 0,35 m fra knekken
        uk = 0.0
        for a_, b_ in zip(L[:-2], L[1:-1]):
            uk += math.hypot(b_[0] - a_[0], b_[1] - a_[1]); m = b / 2 + 0.35
            if abs(u - uk) < m: u = uk + m if u >= uk else uk - m
        p, t = punkt_paa(L, u); n = utover(x, p, t)
        nye.append([round(p[0], 2), round(p[1], 2), z, round(n[1], 4), round(-n[0], 4), round(n[0], 4), round(n[1], 4), b, h, typ, bue, 1])
    return beholdt + nye, len(vind) - len(beholdt)


def arkade_fra_fasade(x, F):
    A = F['arkade']; L = F['linje']
    a, _ = punkt_paa(L, A['u0']); b, _ = punkt_paa(L, A['u1'])
    # korden a-b kan ligge innenfor veggen der fasaden knekker: flytt den ut til det ytterste punktet av fasaden mellom a og b
    t = ((b[0] - a[0]), (b[1] - a[1])); Lab = math.hypot(*t); t = (t[0] / Lab, t[1] / Lab); n = utover(x, a, t)
    ut = max([0.0] + [(q[0] - a[0]) * n[0] + (q[1] - a[1]) * n[1] for q in L if 0 < (q[0] - a[0]) * t[0] + (q[1] - a[1]) * t[1] < Lab])
    a = [round(a[0] + n[0] * ut, 2), round(a[1] + n[1] * ut, 2)]; b = [round(b[0] + n[0] * ut, 2), round(b[1] + n[1] * ut, 2)]
    return dict(a=a, b=b, **{k: A[k] for k in ('z0', 'h', 'topp', 'n', 'bredde', 'dybde', 'mork')})


def uten_vinduer_bak(x, A):
    """Vinduer på veggen bak arkaden (under rammens overkant) tas ut: arkaden er fasaden der."""
    a, b = A['a'], A['b']; Lab = math.hypot(b[0] - a[0], b[1] - a[1]); t = ((b[0] - a[0]) / Lab, (b[1] - a[1]) / Lab); n = utover(x, a, t)
    ut = []
    for v in x.get('vind') or []:
        s = (v[0] - a[0]) * t[0] + (v[1] - a[1]) * t[1]; d = abs((v[0] - a[0]) * n[0] + (v[1] - a[1]) * n[1])
        topp = (A.get('felt') or {}).get('z1', A['topp'])                 # feltene over arkaden er fasaden der også
        if -0.3 <= s <= Lab + 0.3 and d < 0.8 and v[5] * n[0] + v[6] * n[1] > 0.9 and v[2] - v[8] / 2 < topp:
            continue
        ut.append(list(v))
    return ut


# Terrenget rundt Voldporten fra Kartverkets DTM (30.10): det beregnede terrenget (data/landskap.json, OSM-voller + brosjyren) har
# vollen 12 m for langt øst og 3 m for høy der (6,6 m mot DTM 3,7 m over gata ved (230, 52)), og flat mark under porten, så buen og
# vingemurene stod i en eng foran vollen. Flikken er DTM − 7,0 m (veien innenfor porten, 7,0–7,1 moh, er kartets bakkenivå 0), kappet
# ved 0 (bakken utenfor vollen, 5,3–6,2 moh, ligger under kartets bakkeplan). Under porthuset er DTM interpolert over vollkrona
# (9,4–10,4 moh), så husets omriss og passasjen settes til veinivå.
FLIKER = [dict(id='voldporten', bygg=VOLDPORTEN, x0=186.0, y0=12.0, x1=242.0, y1=66.0, g=1.0, ref=7.0, kant=8.0)]


def terrengflikker(tørt):
    import numpy as np, importlib.util
    from shapely.geometry import Polygon
    import shapely
    H = os.path.join(ROT, 'rapport', 'hoyder')
    spec = importlib.util.spec_from_file_location('hent', os.path.join(H, 'hent.py')); hent = importlib.util.module_from_spec(spec); spec.loader.exec_module(hent)
    dtm, gt = hent.les(os.path.join(H, 'kilder', 'dtm1_25832.tif'))
    SH = tuple(json.load(open(os.path.join(H, 'tall.json')))['forskyvning'])
    ex0, ny0, dx, dy = gt
    B = {x['id']: x for x in datalag.alle()['bygg']}
    ut = []
    for F in FLIKER:
        nx = int(round((F['x1'] - F['x0']) / F['g'])) + 1; ny = int(round((F['y1'] - F['y0']) / F['g'])) + 1
        xs, ys = np.meshgrid(F['x0'] + np.arange(nx) * F['g'], F['y0'] + np.arange(ny) * F['g'])
        U = hent.til_utm(np.c_[xs.ravel(), ys.ravel()]) + np.array(SH)
        c = ((U[:, 0] - ex0) / dx).astype(int); r = ((ny0 - U[:, 1]) / dy).astype(int)
        h = np.clip(dtm[r, c] - F['ref'], 0, None)
        hus = Polygon(B[F['bygg']]['p']).buffer(0.6, join_style='mitre')
        h[shapely.contains_xy(hus, xs.ravel(), ys.ravel())] = 0.0
        ut.append(dict(id=F['id'], x0=F['x0'], y0=F['y0'], g=F['g'], nx=nx, ny=ny, kant=F['kant'], h=[int(round(v * 100)) for v in h],
                       kilde=f"Kartverket DTM 1 m − {F['ref']} m (veien innenfor porten = kartets bakkenivå), kappet ved 0; porthuset og passasjen på "
                             "veinivå (DTM er interpolert over vollkrona der); verktoy/landemerker.py 30.10"))
        print(F['id'], f"terrengflikk {nx} × {ny} punkter, høyeste {h.max():.1f} m")
    if not tørt:
        with open(os.path.join(ROT, 'data', 'terrengflikker.json'), 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(',', ':')) for p in ut) + '\n]\n')


def porter_voldporten(tørt):
    f = os.path.join(ROT, 'data', 'porter.json'); P = json.load(open(f, encoding='utf8'))
    for p in P:
        if p.get('bygg_id') == VOLDPORTEN:
            p.update(VOLDPORT_PORT); p['bunn'] = 0.0   # veien i porten = kartets bakkenivå (terrengflikken setter terrenget dit)
            b = next(x for x in datalag.alle()['bygg'] if x['id'] == VOLDPORTEN)
            p['vingemurer'] = vingemurer(b['p'], p['ret'])
            p['vingemurer_kilde'] = ('SØ: Street View aug. 2010 og brukerfoto aug. 2019 (form), ortofoto 2024 (kappene ovenfra: lengde og retning), '
                                     'DTM (foten); NV: Street View aug. 2010 (lave murer, lengde og vinkel lest av bildet, usikker) – verktoy/landemerker.py')
            p['kilde'] = ('høyde og bue: Street View aug. 2010 (SØ) og DOM: takfot 7,5 m over veien = portmur 4,4 + vaktstue 3,1 '
                          '(verktoy/landemerker.py)')
    if not tørt:
        with open(f, 'w', encoding='utf8') as fh:
            fh.write('[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(',', ':')) for p in P) + '\n]\n')


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if not str(r.get('grunn', '')).startswith(GRUNN)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = {x['id']: x for x in d['bygg']}
    for x in B.values():
        for k in ('vind', 'tak2'):
            if isinstance(x.get(k), str):
                x[k] = json.loads(x[k])
    nye = []
    def sett(i, felt, verdi, hvorfor):
        nye.append(dict(emne='bygg', id=i, op='sett', felt=felt, verdi=verdi, hvem='Claude', dato=DATO, grunn=f'{GRUNN}: {hvorfor}'))

    # rådhuset
    x = B[RAADHUS]
    # høyden: kilder/hoyde-unntak.json, lagt inn av rapport/hoyder/legg_inn.py (regel 02 måler mot den)
    sett(RAADHUS, 'deler', [RAADHUS_TAARN], RAADHUS_TAARN['kilde'])
    vind, ut = fasade_vinduer(x, RAADHUS_FASADE)
    sett(RAADHUS, 'vind', vind, 'gatefasaden mot SSV fra Kvartal14.ai: rundbuevinduer, rundbuet dør, fem store rundbuer som arkade')
    sett(RAADHUS, 'arkader', [arkade_fra_fasade(x, RAADHUS_FASADE)], 'Kvartal14.ai: fem store rundbuer nede i gatefasaden, i dyp nisje')
    sett(RAADHUS, 'vegg', [221, 173, 132], 'veggfarge: Kvartal14.ai (lys side) = Street View aug. 2010 (gul tegl, NV-fasaden); trykkets laks var feil kulør')
    sett(RAADHUS, 'veggs', [190, 130, 84], 'skyggesiden i Kvartal14.ai')
    sett(RAADHUS, 'vegg_kilde', 'kvartaltegningen Kvartal14 = Street View aug. 2010 (gul tegl)', 'fargekilde')
    sett(RAADHUS, 'vegg_aar', 2015, 'fargekilde')
    print(RAADHUS, f'tårn {RAADHUS_TAARN["h"]} m, {len(RAADHUS_FASADE["vinduer"])} vinduer/dører på gatefasaden (tok ut {ut}), arkade 5 buer')

    # 13394024: arkaden mot gården
    x = B['bnr-13394024']
    A = {k: v for k, v in ARKADE_13394024.items() if k != 'kilde'}
    v2 = uten_vinduer_bak(x, A)
    sett('bnr-13394024', 'arkader', [A], ARKADE_13394024['kilde'])
    sett('bnr-13394024', 'vind', v2, 'vinduene bak arkaden tatt ut (arkaden er fasaden der)')
    print('bnr-13394024', f'arkade {A["n"]} buer, {len(x.get("vind") or []) - len(v2)} vinduer bak den tatt ut')

    # Voldporten
    x = B[VOLDPORTEN]
    tak = valm_rektangel(x['p'])
    sett(VOLDPORTEN, 'tak2', tak, 'valmtak med kort møne (Street View aug. 2010: «valm (pyramideaktig, kort møne)»; Glasshytta.ai: valm mot enden)')
    sett(VOLDPORTEN, 'gavl2', [], 'valmtak: ingen gavler')
    sett(VOLDPORTEN, 'takform', 'valm', 'Street View aug. 2010 og Glasshytta.ai')
    if tak:   # én pipe midt på mønet (Street View 2010 og tegningen)
        topp = max((q for f in tak for q in f), key=lambda q: q[2]); top = [q for f in tak for q in f if abs(q[2] - topp[2]) < 0.05]
        mx = sum(q[0] for q in top) / len(top); my = sum(q[1] for q in top) / len(top)
        sett(VOLDPORTEN, 'piper', [[round(mx, 2), round(my, 2), 0, (x.get('piper') or [[0, 0, 0, 0]])[0][3]]], 'én pipe midt på mønet (Street View 2010, Glasshytta.ai)')
    xv = dict(x, vind=[])
    vv = []
    for F in VOLDPORT_FASADER:
        v_, _ = fasade_vinduer(xv, F); vv += v_
    sett(VOLDPORTEN, 'vind', vv, 'vaktstuen: SSV-langsida fra Glasshytta.ai, NV-enden fra Street View aug. 2010, SØ-enden uten vinduer')
    porter_voldporten(tørt)
    terrengflikker(tørt)
    print(VOLDPORTEN, f'portmur {VOLDPORT_PORT["h"]} m, vaktstue h {x.get("h")} (kilder/hoyde-unntak.json)')

    # atriene (kilder/atrier.json): ringtak + glass
    U_ = json.load(open(os.path.join(ROT, 'kilder', 'hoyde-unntak.json'), encoding='utf8'))['hus']
    for i, A in ATRIER.items():
        x = B[i]
        f = atrium_hoyde(x, A)
        u = U_.get(i) or {}
        if abs(u.get('h', -9) - f['h']) > 0.1 or abs(u.get('th', -9) - f['th']) > 0.03:
            print(f"ADVARSEL {i}: DOM-tilpasningen gir h {f['h']} th {f['th']}, kilder/hoyde-unntak.json har {u.get('h')} {u.get('th')}: oppdater unntaket")
        h, th = u.get('h', f['h']), u.get('th', f['th'])
        tak2, gavl2 = atrium_tak(x, A, f['wg'])
        sett(i, 'tak2', tak2, f"ringtak rundt gårdsrommet (rett skjelett, takfot bare mot gata, helning mot gårdsromskantene {f['wg']} × th), "
                              f"tilpasset DOM−DTM: rms {f['rms']} m på {f['n']} punkter")
        sett(i, 'gavl2', gavl2, 'brannmurene: ytterveggene uten takfot opp til ringtaket')
        sett(i, 'takform', 'atrium', 'ring av tak rundt et innglasset gårdsrom (kilder/atrier.json)')
        sett(i, 'atrium', dict(gaard=A['gaard'], kant=A['kant'], z=h, topp=A.get('glass_topp') or f['topp'], glass=A['glass'], ramme=A['ramme']),
             A['kilde'] + f" Glassets topp: DOM−DTM i gårdsrommet ({f['topp']} m).")
        if A.get('takvinduer'):
            sett(i, 'takvinduer', A['takvinduer'], 'takvinduer: ' + A.get('takvinduer_kilde', 'kilder/atrier.json'))
        print(i, f"atrium: h {h} th {th}, glass til {f['topp']} m, {len(tak2)} takflater, {len(gavl2)} brannmurstykker, rms {f['rms']} m")
    if not tørt:
        datalag.skriv_rettelser(ret + nye)


if __name__ == '__main__':
    main('--tørt' in sys.argv)
