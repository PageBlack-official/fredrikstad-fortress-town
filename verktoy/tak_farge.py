"""Takfarge for alle hus i Gamlebyen etter fargeregelen (30.10, Vegar):

  TAK:   ortofoto 2024 er nyeste kilde og ser rett ned på taket, så det avgjør kuløren for alle tak. Tegningen (2015) brukes
         der fotoet ikke ser taket (trær over, slagskygge, for lite tak) eller ikke kan skille (falmet/mosegrodd tegl).
  VEGG:  nyeste kilde vinner: Street View 2016 eller senere > 2019-trykket/2015-tegningen > Street View før 2015
         (verktoy/streetview_farger.py og verktoy/vegg_nye.py, felles hjelpere her).
  Tilnærmet riktig er nok, feil kulør er ikke lov. Når fotoet og tegningen har samme kulør, får huset tegningens farge (Vegars
  palett); når de har ulik kulør, vinner fotoet, og huset står med «avvik med grunn» mot tegningen (fotoet er nyere).

Takfargen fra fotoet: hver takflate (tak2 i modellen, ellers hele omrisset) måles for seg, 0,5 m inn fra veggen og 0,3 m inn fra
grat og møne, så nabotak og takfot ikke teller. Sola står i SØ i fotoet; flatene i skygge er blå av himmellyset og sier lite om
kuløren, så bare flatene i sol (median lyshet minst 85 % av den lyseste flaten) brukes. Medianen av dem klassifiseres (klasse()):
terskelene er målt på hus med kjent tak (Street View 2016+ med høy sikkerhet og kvartaltegningene), se rapport/farge/tak-kalibrering.json.

Tegningens farge per hus (tegning_farger()): kvartaltegningen der kontrolløren har registrert huset (rapport/kontroll/avvik.json,
verktoy/kontroll.py: tegningens flatefarge under huset i tegningens egen projeksjon, IoU >= 0,45, Kvartal11 er ugyldig), ellers
2015-trykkfila/2019-trykket slik grunndataene og fargedommen (farger-dom) har dem.

    python3 verktoy/tak_farge.py [--tørt]   rettelser (tak, taks, tak_kilde, tak_aar) + rapport/farge/tak.json og tak-kalibrering.json
    python3 verktoy/tak_farge.py ark        kontrollark rapport/farge/tak.png (oversikt) og rapport/farge/tak-<gruppe>.png:
                                            ortofoto | modellens tak ovenfra, per kvartal (bildene viser ortofotoet: bare lokalt)
Rekkefølge i kjeden: streetview_farger.py -> tak_farge.py -> vegg_nye.py -> bygg_merknader.py (merknadene vinner).
"""
import json, os, re, sys, colorsys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
from shapely.geometry import Polygon

GRUNN = 'takfarge etter fargeregelen (verktoy/tak_farge.py, 30.10)'
UT = os.path.join(ROT, 'rapport', 'farge')
STANDARD_VEGG = [226, 222, 212]
ATRIER = json.load(open(os.path.join(ROT, 'kilder', 'atrier.json'), encoding='utf8'))['hus']
STANDARD_TAK = [150, 144, 138]
# grunner til linjer som er fargeregelens egne (de tas bort før tegningens farge leses, og erstattes ved hver kjøring)
REGEL_GRUNNER = ('Street View (Vegars Chrome 29.10.2026)', 'takfarge fra ortofoto 2024', 'veggfarge til nye hus',
                 'veggfarge etter fargeregelen', GRUNN)
UGYLDIGE_TEGNINGER = set()     # tegninger kontrolløren ikke kan stole på (Kvartal11 tatt ut 30.10: koblingen er Infanterikasernen nå)
TEGNINGSAAR = 2015
# Mellombåndet (falmet/mosegrodd tegl og brungrå tak gir samme tall i fotoet): 'tegning' = tegningens farge (30.10), 'foto' = brungrå
# fra fotoet. 30.10: 'foto' (hovedagentens kryssjekk av kvartal 12: klart grå tak ble røde med 'tegning'; taket følger fotoet 2024).
MELLOM = 'foto'
# tegningens farge lest for hånd der kontrolløren leser feil flate (piksel i tegningen rendret med pymupdf, 30.10)
HAANDLEST = {
    # Tøihuset: tegningen har oker vegger og rødbrunt tak (173, 100, 86). Street View mai 2024 (høy sikkerhet) viser umalt rød tegl
    # med hvite rundbuevinduer og hvit pusset vestgavl, og et brunt, mosegrodd teglstak; ortofotoet ser taket brungrått. Veggen tar
    # Street View (nyere enn tegningen, streetview_farger.py); taket er brunt tegl, mørkere og brunere enn tegningens, så tak og vegg
    # ikke flyter sammen (avlest for hånd i fotoet og Street View 30.10).
    'bnr-193870279': {'tak': ([140, 106, 92], 'ortofoto 2024 (brungrått) + Street View mai 2024 (brunt mosegrodd teglstak), lest for hånd'),
                      'vegg': ([217, 165, 125], 'kvartaltegningen Toihuset (lest for hånd)')},
}

# kartfarger (flate, i samme lyshet som trykket) for klassene fotoet kan skille
PALETT = {'rød tegl': (196, 92, 72), 'falmet tegl': (170, 108, 92), 'mørk brun': (110, 88, 78), 'brungrå': (132, 122, 112), 'svart/antrasitt': (70, 70, 72), 'mørk grå': (104, 104, 102),
          'grå': (150, 150, 148), 'lys grå': (176, 176, 172), 'grønn (kobber)': (112, 168, 146)}
FAMILIE_AV_KLASSE = {'rød tegl': 'rød', 'falmet tegl': 'rød', 'mørk brun': 'brun', 'brungrå': 'grå', 'svart/antrasitt': 'grå', 'mørk grå': 'grå', 'grå': 'grå',
                     'lys grå': 'grå', 'grønn (kobber)': 'grønn'}


# ------------------------------------------------------------------ felles: kulør, Street View-dato, tegningens farge

def familie(rgb):
    """Kulørfamilie for regelen «feil kulør er ikke lov»: rød, oransje (oker, fersken, laks), gul, grønn, blå, grå (grå, svart,
    hvit, svært umettet) og brun (mørk og varm)."""
    if rgb is None:
        return None
    r, g, b = [v / 255 for v in rgb[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hd = h * 360
    if l > 0.93 or s < 0.12 or l < 0.16 or (l > 0.85 and s < 0.3 and (max(rgb[:3]) - min(rgb[:3])) < 26):
        return 'grå'
    if (hd < 70 or hd >= 335) and l < 0.36:
        return 'brun'
    if 18 <= hd < 50 and l < 0.48 and s < 0.45:      # brunt panel i sol (146,104,80; Street View 867715): brunt, ikke oransje
        return 'brun'
    if hd < 18 or hd >= 335:
        return 'rød'
    if hd < 42:
        return 'oransje'
    if hd < 70:
        return 'gul'
    if hd < 170:
        return 'grønn'
    if hd < 260:
        return 'blå' if s > 0.18 else 'grå'
    return 'rød'                                     # lilla/rosa: nærmest rødt i dette kartet


NABO = [{'rød', 'oransje'}, {'oransje', 'gul'}, {'rød', 'brun'}, {'oransje', 'brun'}]


def samme_kulor(a, b):
    """Samme kulør, eller nabokulører (rød/oransje, oransje/gul, brun/rød, brun/oransje) som ligger nær hverandre (ΔE < 25)."""
    fa, fb = familie(a), familie(b)
    if fa is None or fb is None:
        return False
    return fa == fb or ({fa, fb} in NABO and _dE(a, b) < 25)


def _lab(rgb):
    import cv2
    return cv2.cvtColor(np.uint8([[list(rgb[:3])]]), cv2.COLOR_RGB2LAB)[0, 0].astype(float) * [100 / 255, 1, 1] - [0, 128, 128]


def _dE(a, b):
    return float(np.linalg.norm(_lab(a) - _lab(b)))


MND = r'(?:jan|feb|mars|apr|mai|juni|juli|aug|sep|okt|nov|des)\w*\.?'


def sv_aar(tekst):
    """Årstallet til et Street View-bilde fra avlesningens datotekst («aug. 2010», «mai 2024 (og aug. 2010)»): første årstall
    (det avlesningen sier gjelder), ellers None."""
    m = re.search(r'(20[0-3]\d)', str(tekst or ''))
    return int(m.group(1)) if m else None


def sv_vegg_aar(a):
    """Året veggfargen i avlesningen er sett. Veggteksten kan si det selv («lys grå (mai 2024); mørk grønn i aug. 2010»: første
    del gjelder). Ellers: nyeste side med veggfarge der sidens dato er oppgitt; ellers hele avlesningens dato."""
    v = (a.get('vegg') or {})
    for felt in (v.get('farge'), v.get('lys')):
        forste = re.split(r'[;]', str(felt or ''))[0]
        y = sv_aar(forste) if re.search(MND + r' ?20\d\d', forste) else None
        if y:
            return y
    hel = sv_aar(a.get('bilde_dato'))
    sider = [sv_aar(s.get('bilde_dato')) for s in a.get('sider') or [] if s.get('vegg_farge') and sv_aar(s.get('bilde_dato'))]
    if sider and hel:
        # den sette veggfargen står i hovedavlesningen; en side med samme dato som hovedbildet bekrefter den
        return hel if hel in sider else max(sider)
    return hel or (max(sider) if sider else None)


def les_sv():
    p = os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json')
    return json.load(open(p, encoding='utf8')) if os.path.exists(p) else {}


def gamlebyen_ider():
    """Husene i Gamlebyen = modellhusene registeret har koblet til et kommunehus (kilder/register/gamlebyen.json)."""
    reg = json.load(open(os.path.join(ROT, 'kilder', 'register', 'gamlebyen.json'), encoding='utf8'))
    ut = set()
    for b in reg['bygg']:
        m = b.get('modell_id')
        for i in (m if isinstance(m, list) else [m]):
            if i:
                ut.add(i)
    # og husene kontrolløren har registrert i en 2015-tegning (IoU >= 0,30): de står i Gamlebyen selv om registeret ikke har koblet
    # dem til et kommunehus (Laboratoriet 870198 i sistekvartal fikk ingen farge etter regelen, 30.10)
    p = os.path.join(ROT, 'rapport', 'kontroll', 'avvik.json')
    if os.path.exists(p):
        ut |= {h['id'] for h in json.load(open(p, encoding='utf8')).get('hus', []) if (h.get('iou') or 0) >= 0.30}
    return ut


def tilstand_uten_regelen(rettelser=None):
    """Byggene med alle rettelser unntatt fargeregelens egne linjer: fargene her er grunndataenes (2015-trykkfila), fargedommen
    mot 2019-trykket og Vegars/hovedagentens merknader."""
    ret = rettelser if rettelser is not None else datalag.les('rettelser')
    uten = [r for r in ret if not str(r.get('grunn', '')).startswith(REGEL_GRUNNER)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    return datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, uten), grunn)['bygg']


def mulig_tak(rgb):
    """En takfarge fotoet tillater i Gamlebyen: tegl (rød/brun), grått/svart eller kobber; ikke hvitt (papir, hvit vegg) og ikke
    gult (en veggflate kontrolløren tok for tak)."""
    return rgb is not None and min(rgb[:3]) <= 215 and familie(rgb) in ('rød', 'brun', 'grå', 'grønn')


def trykk_bekreftet(rettelser=None):
    """Husene der trykkets farge i grunndataene er dømt mot 2019-trykket (rapport/farger-dom/dom.txt: «I» = stemmer, eller en
    palettbokstav = rettet; «?» = ikke synlig) eller satt for hånd fra trykket/tegningen (fargedommens rettelser, merknadene).
    Resten av grunndataenes farger (mange står hvite) er ikke dømt og regnes ikke som tegningens farge."""
    ok = set()
    p = os.path.join(ROT, 'rapport', 'farger-dom', 'dom.json')
    raa = datalag.alle(raa=True)['bygg']
    if os.path.exists(p):
        for k, v in json.load(open(p, encoding='utf8')).items():
            if v not in ('?', 'X') and int(k) < len(raa):
                ok.add(raa[int(k)]['id'])
    ret = rettelser if rettelser is not None else datalag.les('rettelser')
    for r in ret:
        g = str(r.get('grunn', ''))
        if r.get('felt') in ('vegg', 'tak') and (g.startswith('2019-trykket') or g.startswith('farger-dom') or g.startswith('Torvgata')
                                                or g.startswith('merknad på huset')):
            ok.add(r['id'])
    return ok


_SV = None
def sv_ord_farge(id_):
    """Veggfargen Street View-ordet gir for huset (alle år), eller None."""
    global _SV
    if _SV is None:
        _SV = les_sv()
    a = _SV.get(id_) or {}
    if a.get('sikkerhet') in ('ikke synlig', 'lav'):          # «kun glimt gjennom porten» (972152) avgjør ikke mot tegningen
        return None
    import streetview_farger as SVF
    return SVF.fra_ord((a.get('vegg') or {}).get('farge'), SVF.VEGG)


def tegning_farger(bygg_uten=None, rettelser=None):
    """id -> {'vegg': (rgb, kilde), 'tak': (rgb, kilde), 'vegg_svak': …, 'tak_svak': …}. Rekkefølgen for tegningens farge:
    kvartaltegningen der kontrolløren har registrert huset godt (IoU >= 0,45) > trykkets farge dømt mot 2019-trykket >
    kvartaltegningen med svakere registrering (IoU 0,30–0,45). Udømte trykkfarger står som *_svak (brukes bare til slutt)."""
    ut = {}
    ret = rettelser if rettelser is not None else datalag.les('rettelser')
    B = bygg_uten if bygg_uten is not None else tilstand_uten_regelen(ret)
    ok = trykk_bekreftet(ret)
    for x in B:
        fk = str(x.get('farge_kilde') or '')
        if fk.startswith('standard') or fk.startswith('tak: standard'):
            continue
        d = {}
        sterk = x['id'] in ok or fk.startswith('kvartaltegning')
        navn = 'kvartaltegningen (merknad)' if fk.startswith('kvartaltegning') else '2019-trykket (dømt)' if sterk else '2015-trykkfila (ikke dømt)'
        for f, std in (('vegg', STANDARD_VEGG), ('tak', STANDARD_TAK)):
            if x.get(f) and list(x[f]) != std:
                d[f if sterk else f + '_svak'] = (list(x[f]), navn)
        if d:
            ut[x['id']] = d
    p = os.path.join(ROT, 'rapport', 'kontroll', 'avvik.json')
    if os.path.exists(p):
        best = {}
        for h in json.load(open(p, encoding='utf8')).get('hus', []):
            if h.get('tegning') in UGYLDIGE_TEGNINGER or (h.get('iou') or 0) < 0.30:
                continue
            if h['id'] not in best or h['iou'] > best[h['id']]['iou']:
                best[h['id']] = h
        strek = lambda c: max(c) < 90 and max(c) - min(c) < 18          # strek, vindu, slagskygge: ingen husfarge
        for i, h in best.items():
            d = ut.setdefault(i, {}); god = h['iou'] >= 0.45
            vf = h.get('veggfarge') or {}
            if vf.get('tegning') and not strek(vf['tegning']) and (god or 'vegg' not in d):
                d['vegg'] = (list(vf['tegning']), f"kvartaltegningen {h['tegning']} ({vf.get('side')} side, IoU {h['iou']:.2f})")
                # Har tegningen en annen fasade på huset med kuløren Street View så (uansett år), er det den: den største flaten kan
                # være gårdsveggen eller nabofasaden (867588 Dunkejongården: grå gårdsvegg, okergul gatefasade som Street View 2010)
                sv = sv_ord_farge(i)
                alle = h.get('veggfarger_tegning') or []
                if sv and alle and not samme_kulor(vf['tegning'], sv):
                    stor = alle[0][1]
                    for c, ar in alle:
                        if ar >= 0.2 * stor and not strek(c) and samme_kulor(c, sv):
                            d['vegg'] = (list(c), f"kvartaltegningen {h['tegning']} (fasaden med Street Views kulør, IoU {h['iou']:.2f})")
                            break
                    else:
                        # liten tegnet flate (under en tredel av medianen, ~900 pt²) med annen kulør enn Street View: tegningen har ikke
                        # sett huset godt (frihånd forskjøvet, gårdsveggen eller nabofasaden over); da er den svak og Street View før 2015
                        # går foran. Gjelder alle kulører: på 870228 er den grønne flekken (220 pt²) en port i den gule fasaden, på 867626
                        # er den gule (326 pt²) nabohuset (sett på kontrollarkene 30.10). 870252 (381 pt², grå) er husets egen fasade
                        if stor < 350:
                            d['vegg_svak'] = d.pop('vegg')
            tf = h.get('takfarge') or {}
            t = tf.get('tegning')
            # mørkegrå tak finnes i tegningene (66, 66, 65); bare helt svart er strek
            if t and not (max(t) < 58 and max(t) - min(t) < 18) and mulig_tak(t) and (god or 'tak' not in d):
                d['tak'] = (list(t), f"kvartaltegningen {h['tegning']} (IoU {h['iou']:.2f})")
    for i, v in HAANDLEST.items():
        ut.setdefault(i, {}).update(v)
    return ut


# ------------------------------------------------------------------ fotoet

def klasse(rgb, amax=None):
    """Median av takflatene i sol (rgb) og høyeste røde a* på en flate i halvlys (amax) -> (klasse, sikker).
    Fotoet (april 2024) er overeksponert i full sol: teglrødt blir laksefarget eller beige der. Flatene i halvlys (lyshet
    0,4–0,85 av full sol, ikke den blå skyggen) beholder kuløren, så rødt leses på den røde a* i Lab over alle flatene i lys
    (amax), grått på medianen i sol. Kalibrert med øyet (kvartal 12, Tøihuset, Glasshytta) og mot kjente tak
    (rapport/farge/tak-kalibrering.json):
      tegl, rød:       a* >= 6 på en flate i lys, eller a* >= 5 i sol (eller >= 2,5 med sterk gul b* >= 16 der sola blekner alt)
      grå (skifer, blikk, papp): b* < 7 og a* < 2,5 overalt
      kobber:          a* < -6 (blågrønt)
      mellom:          falmet/mosegrodd rødbrun tegl og brungrå betongstein/tegl gir samme tall (a* 1–5, b* 7–14):
                       fotoet skiller ikke, sikker=False -> tegningen avgjør."""
    L, a, b = _lab(rgb)
    amax = a if amax is None else max(a, amax)
    if a < -6 and b < 6 and L > 30:
        return 'grønn (kobber)', True
    if L < 33:
        return ('mørk brun' if a >= 2.5 else 'svart/antrasitt'), False      # slagskygge: fotoet ser ikke kuløren sikkert
    if amax >= 6 or a >= 5 or (a >= 2.5 and b >= 16):
        return ('rød tegl' if L >= 52 else 'mørk brun'), True
    if b < 7 and amax < 2.5:
        return ('svart/antrasitt' if L < 45 else 'mørk grå' if L < 62 else 'grå' if L < 86 else 'lys grå'), True
    return ('brungrå' if L >= 52 else 'mørk brun'), False


def forskyvning(P, im, px, maks):
    """Ortofotoet er ikke sant ortofoto: høye tak heller bort fra bildesenteret (1–3 m). Flytter omrisset (±maks m, steg
    0,25 m) dit kantene i fotoet er sterkest langs omrisset, med litt straff for avstand. Gir (dx, dy) i meter."""
    import cv2
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    G = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    G = cv2.GaussianBlur(G, (5, 5), 0)
    ring = P.exterior
    pts = np.array([ring.interpolate(t).coords[0] for t in np.arange(0, ring.length, 0.25)])
    q0 = np.array([px(*p_) for p_ in pts])
    best = (-1e9, 0.0, 0.0)
    for dx in np.arange(-maks, maks + 1e-6, 0.25):
        for dy in np.arange(-maks, maks + 1e-6, 0.25):
            q = (q0 + [dx / 0.125, -dy / 0.125]).astype(int)
            ok = (q[:, 0] >= 0) & (q[:, 0] < G.shape[1]) & (q[:, 1] >= 0) & (q[:, 1] < G.shape[0])
            if ok.mean() < 0.9:
                continue
            sc = G[q[ok, 1], q[ok, 0]].mean() * (1 - 0.06 * np.hypot(dx, dy))
            if sc > best[0]:
                best = (sc, float(dx), float(dy))
    return best[1], best[2]


def mal_tak(x, foto_cache={}):
    """Takflatene i fotoet: [{n, med, V, veg}] per flate (omrisset flyttet dit taket står i fotoet, forskyvning())."""
    import cv2, flater as FL
    from shapely import affinity
    P = Polygon(x['p']).buffer(0)
    if P.geom_type != 'Polygon':
        P = max(P.geoms, key=lambda g: g.area)
    M = 4.0
    x0, y0, x1, y1 = P.bounds
    im, px = FL.ortofoto(x0 - M, y0 - M, x1 + M, y1 + M, 0.125)
    rgb = im[:, :, ::-1].astype(float)
    dx, dy = forskyvning(P, im, px, min(3.0, max(1.0, 0.3 * float(x.get('h') or 4))))
    faces = x.get('tak2') or []
    if isinstance(faces, str):
        faces = json.loads(faces)
    polys = [affinity.translate(Polygon([q[:2] for q in f]).buffer(0), dx, dy) for f in faces if len(f) >= 3]
    P = affinity.translate(P, dx, dy)
    polys = polys or [P]
    I = P.buffer(-0.5)
    if I.is_empty or I.area < 3:                     # skur og små uthus: hele taket, 0,3 m inn
        I, polys = P.buffer(-0.3), [P]
    # innglasset gårdsrom (kilder/atrier.json): glasset og karmen er ikke taket, de tas ut med 0,5 m margin (30.10: blågrå
    # glasspyramide i 16308102 trakk medianen mot grått)
    A = ATRIER.get(x.get('id'))
    if A:
        I = I.difference(affinity.translate(Polygon(A['gaard']), dx, dy).buffer(0.5))
    x['_foto_flytt'] = (dx, dy)
    res = []
    for F in polys:
        G = (F.buffer(-0.3) if len(polys) > 1 else F).intersection(I)
        if G.is_empty or G.area < 0.8:
            continue
        m = np.zeros(im.shape[:2], np.uint8)
        for g in getattr(G, 'geoms', [G]):
            if g.geom_type == 'Polygon':
                cv2.fillPoly(m, [np.array([px(*q) for q in g.exterior.coords], np.int32)], 1)
        v = rgb[m > 0]
        if len(v) < 40:
            continue
        exg = 2 * v[:, 1] - v[:, 0] - v[:, 2]
        veg = float(((exg > 18) & (v[:, 1] > v[:, 0])).mean())
        # pikselvis rødhet (30.10): falmet tegl er laksefarget i sol (a* 4–6 på de røde pikslene), grå tak har a* 0–3 overalt
        lab = cv2.cvtColor(v.reshape(-1, 1, 3)[:, :, ::-1].astype(np.uint8), cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(float)
        L_, a_ = lab[:, 0] * 100 / 255, lab[:, 1] - 128
        ok = (L_ > 35) & ~((exg > 18) & (v[:, 1] > v[:, 0]))
        a75 = float(np.percentile(a_[ok], 75)) if ok.sum() >= 20 else None
        rf = float(((a_ > 8) & ok).sum() / max(1, ok.sum()))
        res.append(dict(n=int(len(v)), med=np.median(v, axis=0).round(1).tolist(), V=float(np.median(v.max(axis=1))) / 255, veg=round(veg, 3),
                        a75=a75, rf=round(rf, 3)))
    return res


def foto_dom(flater_):
    """Flatene -> (median i sol, klasse, sikker, grunn). None når fotoet ikke ser taket."""
    if not flater_:
        return None, None, False, 'for lite tak å måle'
    n = sum(f['n'] for f in flater_)
    veg = sum(f['veg'] * f['n'] for f in flater_) / n
    if veg > 0.35:
        return None, None, False, f'trær over taket ({veg:.0%} grønt)'
    mx = max(f['V'] for f in flater_)
    sol = [f for f in flater_ if f['V'] >= 0.85 * mx]
    med = np.average([f['med'] for f in sol], axis=0, weights=[f['n'] for f in sol])
    if mx < 0.3:
        return med.round().tolist(), None, False, 'taket ligger i slagskygge'
    lys = [f for f in flater_ if f['V'] >= 0.4 and f['n'] >= 0.08 * n]
    amax = max((_lab([int(c) for c in f['med']])[1] for f in lys if _lab([int(c) for c in f['med']])[0] >= 40), default=None)
    k, sikker = klasse(med, amax)
    # rødt bare fra én flate i halvlys mens sola ser nøytralt grått og nesten ingen piksler er røde: nabotakets kant eller refleks
    # (16308102 i kvartal 14: blågrått pyramidetak ble rødt, 30.10) -> mellombåndet avgjør
    fl_rf = [f for f in flater_ if f.get('rf') is not None]
    rf_alle = sum(f['rf'] * f['n'] for f in fl_rf) / max(1, sum(f['n'] for f in fl_rf))
    if k == 'rød tegl' and _lab([int(c) for c in med])[1] < 2 and rf_alle < 0.03:
        k, sikker = 'brungrå', False
    if not sikker and MELLOM == 'foto' and k in ('brungrå', 'mørk brun') and mx >= 0.3:
        # mellombåndet avgjøres pikselvis (kalibrert med øyet på kvartal 12 og 13, 30.10): rødhet på flatene i lys -> falmet tegl,
        # ellers grått. Grå tak i kvartal 12 har a*75 0–3 og ingen røde piksler; 7510 (laksefarget tegl i sol) har a*75 5.
        fl_ = [f for f in lys if f.get('a75') is not None] or [f for f in flater_ if f.get('a75') is not None]
        if fl_:
            w = sum(f['n'] for f in fl_)
            a75 = sum(f['a75'] * f['n'] for f in fl_) / w
            rf = sum(f['rf'] * f['n'] for f in fl_) / w
            k = 'falmet tegl' if (a75 >= 4 or rf >= 0.03) else k
        sikker = True
        return med.round().tolist(), k, sikker, 'mellombånd'
    return med.round().tolist(), k, sikker, ('' if sikker else 'falmet/mosegrodd: fotoet skiller ikke tegl fra grått')


def sv_tak_klasse(a):
    """Takets kulør i Street View-ordet (første del, før komma/parentes): 'falmet tegl' (rødt/rødbrunt), 'mørk brun' (brunt),
    'brungrå' (grått, sort, blikk, skifer) eller None. Street View ser taket på skrå og skiller det fotoet ovenfra ikke skiller
    (rapport/farge/tak-kalibrering.json 30.10: av 15 brungrå i mellombåndet med Street View 2016+ var 6 rød/rødbrun tegl)."""
    if not a or a.get('sikkerhet') == 'ikke synlig':
        return None
    t = str((a.get('tak') or {}).get('farge') if isinstance(a.get('tak'), dict) else a.get('tak') or '').lower()
    if not t or t.startswith(('ikke', 'skjult', 'mørk (', 'mørkt')):
        return None
    f = re.split(r'[,(;–]', t)[0]
    gra = re.search(r'grå|sort|svart|blikk|skifer|papp|antrasitt', f)
    if re.search(r'rød', f) and not gra:
        return 'falmet tegl'
    if gra and not re.search(r'rød|brun', f):          # «brun/grå tegl» sier ikke kuløren: fotoet står
        return 'brungrå'
    if re.search(r'\bbrun', f) and not gra:          # brun tegl (867855): mørk brun
        return 'mørk brun'
    return None


# ------------------------------------------------------------------ regelen

def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    B_uten = tilstand_uten_regelen(ret)
    TF = tegning_farger(B_uten, ret)
    ids = gamlebyen_ider()
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)       # uten forrige kjøring av dette verktøyet
    sv = les_sv()
    nye, ut, kal = [], [], []
    for x in d['bygg']:
        if x['id'] not in ids or x.get('skjul') or x.get('kirke') or len(x['p']) < 3:
            continue
        fl = mal_tak(x)
        med, k, sikker, hvorfor = foto_dom(fl)
        if hvorfor == 'mellombånd':
            # fotoet ser falmet tegl og brungrått likt; Street View-ordet for taket avgjør der det har en kulør
            svk = sv_tak_klasse(sv.get(x['id']))
            if svk and svk != k:
                hvorfor = f"mellombånd: Street View {sv_aar((sv.get(x['id']) or {}).get('bilde_dato')) or ''} ({(sv[x['id']].get('tak') or {}).get('farge')})"
                k = svk
            else:
                hvorfor = ''
        tegn = (TF.get(x['id']) or {}).get('tak')
        if tegn and not mulig_tak(tegn[0]):
            tegn = None
        svak = (TF.get(x['id']) or {}).get('tak_svak')
        if svak and not mulig_tak(svak[0]):
            svak = None
        tfam = familie(tegn[0]) if tegn else None
        kfam = FAMILIE_AV_KLASSE.get(k)
        if tegn and 'lest for hånd' in tegn[1] and 'Street View' in tegn[1]:
            # håndlest mot fotoet og Street View 2016+ (HAANDLEST): øyet har sett begge, går foran maskinklassen
            farge, kilde, aar = tegn[0], tegn[1], 2024
        elif k and sikker:
            # samme kulør og omtrent samme lyshet: tegningens farge (en skyggetone fra tegningen, som svart på et lysegrått tak, nei)
            if tegn and k != 'falmet tegl' and (tfam == kfam or {tfam, kfam} <= {'rød', 'brun', 'oransje'} or (kfam == 'grå' and tfam == 'blå')) \
                    and _dE(tegn[0], PALETT[k]) < 40:
                farge, kilde, aar = tegn[0], f"ortofoto 2024 ({k}) = {tegn[1]}: tegningens farge", 2024
            else:
                farge, kilde, aar = list(PALETT[k]), f"ortofoto 2024 ({k}{'; ' + hvorfor if hvorfor else ''})" + (f"; tegningen har {tfam} ({tegn[1]})" if tegn else ''), 2024
        elif tegn:
            farge, kilde, aar = tegn[0], f"{tegn[1]} (ortofoto 2024: {hvorfor})", TEGNINGSAAR
        elif svak and (not k or {familie(svak[0]), FAMILIE_AV_KLASSE.get(k)} <= {'rød', 'brun', 'oransje'} or familie(svak[0]) == FAMILIE_AV_KLASSE.get(k)):
            farge, kilde, aar = svak[0], f"{svak[1]}; samme kulør som ortofoto 2024 eller fotoet ser ikke ({hvorfor})", TEGNINGSAAR
        elif k:
            farge, kilde, aar = list(PALETT[k]), f"ortofoto 2024 ({k}, usikker: {hvorfor}; ingen tegning)", 2024
        else:
            ut.append(dict(id=x['id'], foto=med, klasse=None, grunn=hvorfor, farge=None, kilde='ingen kilde: står som før'))
            continue
        for felt, verdi in (('tak', [int(c) for c in farge]), ('taks', None), ('tak_kilde', kilde), ('tak_aar', aar)):
            nye.append(dict(emne='bygg', id=x['id'], op='sett', felt=felt, verdi=verdi, hvem='Claude', dato='2026-10-30', grunn=GRUNN))
        ut.append(dict(id=x['id'], navn=x.get('navn'), flytt=x.get('_foto_flytt'), foto=med, klasse=k, sikker=sikker, grunn=hvorfor, tegning=tegn,
                       for_=x.get('tak'), farge=[int(c) for c in farge], kilde=kilde, aar=aar))
        # kalibrering: fotoets klasse mot kjente tak
        a = sv.get(x['id']) or {}
        tw = str((a.get('tak') or {}).get('farge') or '')
        if med and sv_aar(a.get('bilde_dato')) and sv_aar(a.get('bilde_dato')) >= 2016 and a.get('sikkerhet') in ('høy', 'middels') \
                and tw and not tw.startswith('ikke'):
            kal.append(dict(id=x['id'], kilde='Street View ' + str(a.get('bilde_dato')), ord=tw, foto=med, klasse=k, sikker=sikker))
        if med and tegn and tegn[1].startswith('kvartaltegningen'):
            kal.append(dict(id=x['id'], kilde=tegn[1], tegning=tegn[0], tegning_familie=tfam, foto=med, klasse=k, sikker=sikker))
    for u in ut:
        print(u['id'].ljust(15), str(u.get('foto')).ljust(22), str(u.get('klasse')).ljust(16), str(u.get('for_')).ljust(16), '->', u['farge'], u['kilde'][:90])
    n_foto = sum(1 for u in ut if u.get('aar') == 2024)
    print(f"{len(ut)} tak: {n_foto} etter fotoet, {sum(1 for u in ut if u.get('aar') == TEGNINGSAAR)} etter tegningen, "
          f"{sum(1 for u in ut if u['farge'] is None)} uten kilde")
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
        os.makedirs(UT, exist_ok=True)
        json.dump(ut, open(os.path.join(UT, 'tak.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        json.dump(kal, open(os.path.join(UT, 'tak-kalibrering.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)


# ------------------------------------------------------------------ kontrollark

def grupper(d, ids):
    """Kvartal: tegningen kontrolløren registrerte huset i; husene utenfor tegningene samles i ruter på 120 m."""
    p = os.path.join(ROT, 'rapport', 'kontroll', 'avvik.json')
    teg = {}
    if os.path.exists(p):
        for h in json.load(open(p, encoding='utf8')).get('hus', []):
            if h['id'] not in teg or (h.get('iou') or 0) > teg[h['id']][1]:
                teg[h['id']] = (h['tegning'], h.get('iou') or 0)
    g = {}
    for x in d['bygg']:
        if x['id'] not in ids or x.get('skjul') or len(x['p']) < 3:
            continue
        c = Polygon(x['p']).centroid
        navn = teg[x['id']][0] if x['id'] in teg else f"rute_{int(c.x // 120)}_{int(c.y // 120)}"
        g.setdefault(navn, []).append(x)
    return g


def tak_ovenfra(x, img, px, s):
    import cv2
    farge = x.get('tak') or STANDARD_TAK
    faces = x.get('tak2') or []
    if isinstance(faces, str):
        faces = json.loads(faces)
    if not faces:
        cv2.fillPoly(img, [np.array([px(*q) for q in x['p']], np.int32)], tuple(int(c) for c in farge[::-1]))
    sol = np.array([0.55, -0.6, 0.58]); sol /= np.linalg.norm(sol)       # sol fra SØ, som i fotoet
    for f in faces:
        if len(f) < 3:
            continue
        A = np.array(f, float)
        n = np.cross(A[1] - A[0], A[2] - A[0]); n = n / (np.linalg.norm(n) + 1e-9)
        if n[2] < 0:
            n = -n
        k = 0.62 + 0.45 * max(0.0, float(n @ sol))
        c = tuple(int(min(255, v * k)) for v in farge[::-1])
        cv2.fillPoly(img, [np.array([px(*q[:2]) for q in f], np.int32)], c)
    cv2.polylines(img, [np.array([px(*q) for q in x['p']], np.int32)], True, (40, 40, 40), 1)


def ark():
    import cv2, flater as FL
    d = datalag.alle(); ids = gamlebyen_ider()
    G = grupper(d, ids)
    os.makedirs(UT, exist_ok=True)
    kilde = {u['id']: u for u in json.load(open(os.path.join(UT, 'tak.json'), encoding='utf8'))} if os.path.exists(os.path.join(UT, 'tak.json')) else {}
    rader = []
    for navn in sorted(G):
        xs = G[navn]
        P = [Polygon(x['p']) for x in xs]
        x0 = min(p.bounds[0] for p in P) - 4; y0 = min(p.bounds[1] for p in P) - 4
        x1 = max(p.bounds[2] for p in P) + 4; y1 = max(p.bounds[3] for p in P) + 4
        mpp = max(0.125, max(x1 - x0, y1 - y0) / 700)
        foto, px = FL.ortofoto(x0, y0, x1, y1, mpp)
        mod = np.full_like(foto, 236)
        for x in d['bygg']:                              # naboer grå, husene i gruppen i sin takfarge
            if x.get('skjul') or len(x['p']) < 3 or x['id'] in {y['id'] for y in xs}:
                continue
            Q = Polygon(x['p'])
            if Q.bounds[2] < x0 or Q.bounds[0] > x1 or Q.bounds[3] < y0 or Q.bounds[1] > y1:
                continue
            cv2.fillPoly(mod, [np.array([px(*q) for q in x['p']], np.int32)], (205, 205, 205))
        for x in xs:
            tak_ovenfra(x, mod, px, mpp)
        for x in xs:
            c = Polygon(x['p']).representative_point(); q = tuple(int(v) for v in px(c.x, c.y))
            u = kilde.get(x['id'], {})
            merke = x['id'].split('-')[-1][-4:] + ('*' if u.get('aar') == 2024 and u.get('tegning') and 'tegningen har' in u.get('kilde', '') else
                                                   'T' if u.get('aar') == TEGNINGSAAR else '')
            for im_ in (foto, mod):
                cv2.putText(im_, merke, (q[0] - 14, q[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 3)
                cv2.putText(im_, merke, (q[0] - 14, q[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 160), 1)
        for x in xs:
            cv2.polylines(foto, [np.array([px(*q) for q in x['p']], np.int32)], True, (255, 0, 255), 1)
            f_ = (kilde.get(x['id']) or {}).get('flytt')
            if f_ and (abs(f_[0]) + abs(f_[1])) > 0:          # omrisset der taket ble målt (forskjøvet i fotoet)
                cv2.polylines(foto, [np.array([px(q[0] + f_[0], q[1] + f_[1]) for q in x['p']], np.int32)], True, (255, 255, 0), 1)
        lim = np.hstack([foto, np.full((foto.shape[0], 8, 3), 255, np.uint8), mod])
        top = np.full((26, lim.shape[1], 3), 255, np.uint8)
        cv2.putText(top, f"{navn}: ortofoto 2024 (venstre; lilla = omrisset, cyan = der taket ble malt) | modellens tak ovenfra (hoyre). T = tegningens farge (fotoet ser ikke/skiller ikke), * = fotoet og tegningen ulik kulor",
                    (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        lim = np.vstack([top, lim])
        cv2.imwrite(os.path.join(UT, f'tak-{navn}.png'), lim)
        rader.append(lim)
    # oversikt: kvartalene (tegningene) i et rutenett, tre per rad, samme bredde; rutene utenfor tegningene står i egne ark
    B = 900
    kv = [r for n, r in zip(sorted(G), rader) if not n.startswith('rute_')]
    ov = [cv2.resize(r, (B, int(r.shape[0] * B / r.shape[1]))) for r in kv]
    rad_ = []
    for i in range(0, len(ov), 3):
        bit = ov[i:i + 3]; H = max(b.shape[0] for b in bit)
        bit = [np.vstack([b, np.full((H - b.shape[0], B, 3), 255, np.uint8)]) for b in bit]
        bit += [np.full((H, B, 3), 255, np.uint8)] * (3 - len(bit))
        rad_.append(np.hstack(bit))
    cv2.imwrite(os.path.join(UT, 'tak.png'), np.vstack(rad_))
    print(len(rader), 'grupper ->', os.path.join(UT, 'tak.png'))


if __name__ == '__main__':
    if sys.argv[1:2] == ['ark']:
        ark()
    else:
        main('--tørt' in sys.argv)
