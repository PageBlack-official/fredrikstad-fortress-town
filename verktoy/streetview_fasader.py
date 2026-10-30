#!/usr/bin/env python3
"""Street View-fasader inn i rettelseslaget: vinduer per etasje, dører, takvinduer (arker) og piper på gatesiden.

Kilde: kilder/streetview/avlesning.json (lest av i Vegars Chrome 29.10.2026; bare tall og ord, ingen Google-bilder i repoet).
Vegars regler 29.10: «Det trenger ikke å være perfekt.» Antall og rekkefølge betyr mer enn centimeter.
Kvartaltegningene er fasit der de finnes: de husene endres ikke, de sammenlignes bare (rapport/streetview-fasader/sammenligning.md).

    python3 verktoy/streetview_fasader.py          skriver rettelsene (idempotent: egne linjer fra forrige kjøring tas ut først)
    python3 verktoy/streetview_fasader.py --tørt   viser bare hva som ville blitt gjort
    python3 verktoy/streetview_fasader.py ark      kontrollark rapport/streetview-fasader/ark.png og ark-fasit.png (egne tegninger)

Kjøres etter verktoy/vinduer_regler.py (og etter grunnmur.py når omrissene endres): de andre veggene på huset får det
vinduer_regler gir dem, gatesiden får tallene fra Street View. Huset merkes fasade_kilde «streetview», så vinduer_regler
ikke skriver over det, og fasade_sv sier hvilken vegg som er sett (regel 17 bruker den).

Per hus:
  hoppes over   sikkerhet «ikke synlig», kirka/hus med deler, skjulte hus, og husene i kilder/streetview/hopp.json
                (merknaden sier at det er usikkert om det er riktig hus; i tvil: hopp over). Hus uten tall hoppes også over.
  fasit         fasade_kilde kvartaltegning, v33- eller Kaserna-rettelse: bare sammenligning, ingen endring
  gatesiden     kamerapunktet (viewpoint i pano_url) til modellmeter; veggen som vender mot punktet (utovernormal mot
                kameraet) og ligger innenfor heading ± KONE grader, uten annet hus i siktlinja. Felles vegg mot nabo telles ikke.
  vinduer       aksene og høydene fra vinduer_regler (brystning 0,9 m, etasje 3,0 m, 0,85 m fra hjørnet, regel 04-klaring),
                men antallet per etasje fra Street View. Antall akser = største antall åpninger i en etasje (dørene teller
                i 1. etasje). Hver etasje tar en delmengde av aksene med jevn rytme (regel 17), helst rett over en åpning
                under, helst symmetrisk. Får etasjene ikke plass under gesims (h − 0,3 m), presses etasjehøyden ned til 2,2 m;
                ellers droppes øverste rad og det står i rapporten.
  dører         antall og plassering fra friteksten (venstre/midt/høyre/hjørne, sett fra kameraet) → nærmeste ledige akse;
                døra tar vinduets plass i 1. etasje. «ingen» → ingen dør på gatesiden; «ikke synlig»/«usikkert» → dørene
                huset hadde på den veggen beholdes.
  arker         takvinduer → arker (format som bygg.json: x, y, z, nx, ny, bredde, høyde) på taket over gatesiden, i
                vindusaksene. Bare der taket stiger fra gatesiden (ikke på gavl); arker på andre takflater beholdes.
  piper         antallet fra Street View erstatter pipene (x, y, z, vinkel) og står på mønet over gatesiden.
Piper og arker skrives i grunndatahøyde (datalag.hoyden_styrer flytter dem med h og takhelning ved bygging)."""
import json, math, os, re, sys, itertools
import numpy as np
from shapely.geometry import Polygon, Point, LineString

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG, vinduer_regler as VR  # noqa: E402

KILDE = os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json')
HOPP = os.path.join(ROT, 'kilder', 'streetview', 'hopp.json')
UT = os.path.join(ROT, 'rapport', 'streetview-fasader')
GRUNN = 'Street View-fasader (Vegars Chrome 29.10.2026)'
DATO = '2026-10-29'
KONE = 35.0                 # grader: siktlinja heading ± KONE
R = VR.R
CC_MIN = 1.25               # m mellom akser: vindu 0,85 + 0,4 m murpille
DYBDE_ARK = 0.6             # m: arkens front står så langt inn på taket (fra veggen)
ETASJE_MIN = 2.2            # m: minste etasjehøyde når etasjene presses inn under gesims


# ---------------------------------------------------------------- lesing av friteksten
TALLORD = {'én': 1, 'en': 1, 'ett': 1, 'ei': 1, 'to': 2, 'tre': 3, 'fire': 4, 'fem': 5, 'seks': 6, 'sju': 7, 'åtte': 8}
POS = [(r'hvert hjørne|begge hjørner|hver ende', [0.04, 0.96]), (r'helt til venstre|venstre ende', [0.06]),
       (r'helt til høyre|høyre ende', [0.94]), (r'midt-venstre', [0.38]), (r'midt-høyre', [0.62]),
       (r'venstre', [0.2]), (r'høyre', [0.8]), (r'midt', [0.5])]
POS_RE = re.compile('|'.join('(' + p + ')' for p, _ in POS))


def tall(t):
    """Første heltall i teksten (siffer eller tallord), None om ingen."""
    if t is None:
        return None
    if isinstance(t, (int, float)):
        return int(t)
    m = re.search(r'\d+', str(t))
    if m:
        return int(m.group())
    for o in re.findall(r'\w+', str(t).lower()):
        if o in TALLORD:
            return TALLORD[o]
    return None


def toppdeler(s, skille=(',', ' + ', ';')):
    """Del teksten på komma/pluss/semikolon som står utenfor parenteser."""
    ut, dybde, start = [], 0, 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == '(':
            dybde += 1
        elif c == ')':
            dybde = max(0, dybde - 1)
        elif dybde == 0:
            for sk in skille:
                if s.startswith(sk, i):
                    ut.append(s[start:i]); start = i + len(sk); i += len(sk) - 1; break
        i += 1
    ut.append(s[start:])
    return [d.strip() for d in ut if d.strip()]


def posisjoner(s):
    """Plasseringsord i teksten (0 = venstre, 1 = høyre sett fra kameraet), i rekkefølge."""
    ut = []
    for m in POS_RE.finditer(s):
        for k, (_, v) in enumerate(POS):
            if m.group(k + 1):
                ut += v; break
    return ut


def les_etasjer(a):
    """Radene nederst først: [(slag, antall)], slag = kjeller | etg | loft. Takarkenes rad tas ut (arkene telles fra
    takvinduer). None når avlesningen ikke har tall."""
    tekst = str(a.get('etasjer') or '').lower()
    liste = a.get('vinduer_per_etasje') or []
    m = re.match(r'\s*(\d+)', tekst)
    if not m or not liste:
        return None
    n = int(m.group(1)); t = [tall(v) for v in liste]
    rader, i = [], 0
    if 'kjeller' in tekst and len(t) > n:
        rader.append(('kjeller', t[0])); i = 1
    for _ in range(n):
        if i < len(t):
            rader.append(('etg', t[i])); i += 1
    if re.search(r'ark(er)?\b', tekst):
        ekstra = None
    elif re.search(r'oppbygg|risalitt|2\. etg', tekst):
        ekstra = 'etg'
    else:
        ekstra = 'loft'
    for v in t[i:]:
        if ekstra:
            rader.append((ekstra, v))
    return rader


DORORD = r'dør|port|inngang|luke'


def dorslag(s):
    """(bredde, høyde, typ) for en dør ut fra ordene."""
    if re.search(r'kjeller|luke|\blav\b', s):
        return 0.9, 1.6, 1
    if re.search(r'garasje|kjøreport|portrom|treporter|plankeport|\bport\b|dobbel port|dobbelport', s):
        return 2.4, 2.5, 2 if 'rundbue' in s else 1
    if 'rundbue' in s:
        return 1.1, 2.2, 2
    if re.search(r'dobbel', s):
        return 1.3, 2.3, 1
    return R['db'], R['dh'], 1


def les_dorer(t):
    """Dørene på gatesiden: [(s, bredde, høyde, typ)], s = 0..1 fra venstre sett fra kameraet. [] = ingen; None = ukjent."""
    if t is None:
        return None
    s = str(t).lower().strip()
    if re.match(r'(ikke synlig|ikke sett|usikker)', s) or (s.startswith('ingen synlig') and re.search(r'hekk|dekker|skjult', s)):
        return None
    if s.startswith('ingen'):
        return []
    n = tall(s.split(',')[0].split(':')[0]) if re.match(r'\s*\d', s) else None
    kropp = s.split(':', 1)[1] if ':' in s[:12] else s
    dorer = []
    deler = toppdeler(kropp)
    for d in deler:
        if re.fullmatch(r'\d+', d):
            continue
        if not re.search(DORORD, d) and not posisjoner(d):
            continue
        ps = posisjoner(re.sub(r'\(.*?\)', '', d)) or posisjoner(d) or [None]
        for p in (ps if (n and len(ps) > 1) or 'hjørne' in d or ' og ' in d else ps[:1]):
            dorer.append([p, *dorslag(d)])
    if n is None:
        n = len(dorer) or 1
    if not dorer:
        dorer = [[None, *dorslag(s)]]
    while len(dorer) < n:
        dorer.append([None] + dorer[-1][1:])
    dorer = dorer[:n]
    frie = [i for i, d in enumerate(dorer) if d[0] is None]
    for k, i in enumerate(frie):     # uten plassering: jevnt fordelt (én: midt)
        dorer[i][0] = (k + 1) / (len(frie) + 1)
    return [tuple(d) for d in sorted(dorer, key=lambda d: d[0])]


def les_arker(t):
    """Takvinduene som arker: [(bredde, høyde)]. None = ukjent."""
    if t is None:
        return None
    if isinstance(t, (int, float)):
        return [(1.25, 1.35)] * int(t)
    s = str(t).lower()
    if s.startswith('ikke') or s.startswith('usikker'):
        return None
    ut = []
    for d in toppdeler(s):
        n = tall(re.sub(r'\(.*?\)', '', d))
        if n is None:
            n = 1 if re.search(r'ark|takvindu|takluke|velux', d) else 0
        if re.search(r'midtark|midtgavl|gavlark|tre vinduer|3-delt|tredelt', d):
            st = (2.4, 1.6)
        elif re.search(r'små|lite|liten|takluke|velux', d):
            st = (0.8, 0.9)
        else:
            st = (1.25, 1.35)
        ut += [st] * n
    return ut


def les_piper(t):
    """Pipene: [s] (0..1 fra venstre, None = jevnt fordelt). None = ukjent."""
    if t is None:
        return None
    s = str(t).lower()
    if s.startswith('usikker') or s.startswith('ikke'):
        return None
    ut = []
    for d in toppdeler(s):
        n = tall(re.sub(r'\(.*?\)', '', d))
        if n is None:
            continue
        ps = posisjoner(d)
        ut += [ps[k] if k < len(ps) else None for k in range(n)]
    frie = [i for i, p in enumerate(ut) if p is None]
    for k, i in enumerate(frie):
        ut[i] = (k + 1) / (len(frie) + 1)
    return sorted(ut)


def kamera(a):
    u = a.get('pano_url') or ''
    m = re.search(r'viewpoint=([-\d.]+),([-\d.]+)', u) or re.match(r'\s*([-\d.]+),\s*([-\d.]+)', u)
    h = re.search(r'heading=([-\d.]+)', u) or re.search(r'\bh\s*([-\d.]+)', u)
    if not m or not h:
        return None, None
    lat, lon = float(m.group(1)), float(m.group(2))
    return np.array(datalag.til_modell(lon, lat)), float(h.group(1))


KOMPASS = {'N': 0, 'NNØ': 22.5, 'NØ': 45, 'ØNØ': 67.5, 'Ø': 90, 'ØSØ': 112.5, 'SØ': 135, 'SSØ': 157.5, 'S': 180, 'SSV': 202.5,
           'SV': 225, 'VSV': 247.5, 'V': 270, 'VNV': 292.5, 'NV': 315, 'NNV': 337.5}


def retningsvegg(x, V, retning):
    """Når siktlinja ikke finner veggen (kamerapunktet er omtrentlig): veggen som vender den veien avlesningen sier
    («NV (gavl mot …)» = veggen med utovernormal mot nordvest), fri (ikke felles med nabo), innen 35°."""
    m = re.match(r'\s*([NSØV]{1,3})\b', retning or '')
    if not m or m.group(1) not in KOMPASS:
        return None
    a = math.radians(KOMPASS[m.group(1)]); f = np.array([math.sin(a), math.cos(a)])
    kand = [(float(w['n'] @ f) * min(w['L'], 12), i) for i, w in enumerate(V) if w['felles'] < 0.5 and w['L'] >= 2.0 and w['n'] @ f >= math.cos(math.radians(35))]
    return max(kand)[1] if kand else None


def sider(a):
    """Avlesningens sider (29.10 kveld: «sider», én per fasade som er sett) som egne avlesninger med husets felles felt
    (navn, merknad, sikkerhet). Gammelt format (én fasade på toppnivå) gir én side. Sider som ikke er sett, tas ut."""
    S = a.get('sider')
    if not S:
        return [a]
    ut = []
    for sd in S:
        tekst = ' '.join(str(sd.get(k) or '') for k in ('retning', 'etasjer')).lower()
        if 'ikke synlig' in tekst:
            continue
        b = {k: a.get(k) for k in ('id', 'navn', 'merknad', 'sikkerhet', 'adresse')}
        b.update(sd)
        b['takvinduer'] = sd.get('takvinduer_arker', sd.get('takvinduer'))
        b['merknad'] = ' '.join(str(x) for x in (sd.get('retning'), a.get('merknad')) if x)
        ut.append(b)
    return ut


# ---------------------------------------------------------------- geometri
def stiger(x, w):
    """Stiger taket fra veggen (takfot), eller er veggen en gavl? None når huset ikke har tak2."""
    mid = (w['a'] + w['c']) / 2
    t1 = t_paa_tak(x.get('tak2'), *(mid - w['n'] * 1.0)); t3 = t_paa_tak(x.get('tak2'), *(mid - w['n'] * 2.0))
    return None if t1 is None or t3 is None else t3 - t1 >= 0.5


def gatevegg(x, V, omg, C, heading, gavl=False):
    """Veggen Street View-bildet viser. Kamerapunktet i pano_url er punktet som ble bedt om; Google kan ha tatt bildet et
    stykke unna (merknadene sier opptil 80 m), så retningen (heading, rettet av agenten) veier tyngst:
      vender mot seeren   utovernormal mot -heading (minst cos 60°) og mot kamerapunktet
      i siktlinja         punkter på veggen innenfor heading ± KONE sett fra kamerapunktet
      ikke skjult         siktlinja går ikke gjennom et annet hus eller gjennom huset selv
    Poeng = synlig lengde × hvor rett veggen vender mot seeren; sier avlesningen «gavlen mot gata», teller gavlvegger dobbelt.
    Gir (indeks, notat) eller (None, grunn)."""
    f = np.array([math.sin(math.radians(heading)), math.cos(math.radians(heading))])
    egen = Polygon(x['p']).buffer(0).buffer(-0.05)
    kand = []
    for i, w in enumerate(V):
        if w['felles'] >= 0.5 or w['L'] < 2.0:
            continue
        mot = float(-f @ w['n'])
        mid = (w['a'] + w['c']) / 2; vm = C - mid
        if mot < 0.5 or vm @ w['n'] <= 0:
            continue
        inn = synlig = 0; ts = np.linspace(0.05, 0.95, 19)
        for t in ts:
            q = w['a'] + (w['c'] - w['a']) * t; v = q - C; d = np.linalg.norm(v)
            if d < 1e-6 or (C - q) @ w['n'] <= 0:
                continue
            if math.degrees(math.acos(max(-1, min(1, v @ f / d)))) <= KONE:
                inn += 1
                ende = q + w['n'] * 0.3
                synlig += omg.treff(x['id'], C, ende) is None and not LineString([C, ende]).intersects(egen)
        if inn:
            vekt = mot * (2.0 if gavl and stiger(x, w) is False else 1.0)
            kand.append((synlig / len(ts) * w['L'] * vekt, inn / len(ts) * w['L'] * vekt, i, synlig))
    if not kand:
        return None, 'siktlinja fra kamerapunktet treffer ingen fri vegg som vender mot seeren'
    best = max(kand)
    if best[3] == 0:     # alle sikt-treff går gjennom et hus: kamerapunktet er omtrentlig, ta den som vender best mot seeren
        best = max(kand, key=lambda k: k[1])
        return best[2], 'siktlinja går gjennom et annet hus (kamerapunktet er omtrentlig)'
    return best[2], ''


def t_paa_tak(t2, x, y):
    """Avstand inn fra takfoten i punktet (høyeste takflate over punktet), som verktoy/grunnmur.py."""
    best = None
    for fl in t2 or []:
        F = Polygon([q[:2] for q in fl])
        if F.is_valid and F.buffer(0.05).contains(Point(x, y)):
            A = np.array([[q[0], q[1], 1] for q in fl]); z = np.array([q[2] for q in fl])
            k = np.linalg.lstsq(A, z, rcond=None)[0]
            v = float(k[0] * x + k[1] * y + k[2]); best = v if best is None else max(best, v)
    return best


def til_grunn(z, x, g):
    """Høyde slik kartet viser den -> grunndatahøyde (det datalag.hoyden_styrer regner om fra)."""
    if g is None:
        return round(z, 2)
    h0, h1 = g.get('h', 0), x.get('h', 0); f = x.get('th', 0.82) / 0.82
    if abs(h1 - h0) < 0.05 and abs(f - 1) < 0.01:
        return round(z, 2)
    return round(h0 + (z - h1) / f, 2) if z > h1 else round(z - h1 + h0, 2)


def radhoyder(rader, h, stor):
    """Brystning og vindushøyde per rad. Gir ([(bryst, vb, vh)], droppede rader)."""
    vb, vh = (1.15, 1.9) if stor else (R['vb'], R['vh'])
    kj = [r for r in rader if r[0] == 'kjeller']; resten = [r for r in rader if r[0] != 'kjeller']
    ut = [(0.25, R['vb'], 0.6)] if kj else []
    b0 = 1.5 if kj else R['bryst']; tak = h - R['gesims']
    m = len(resten); dropp = 0
    while m:
        for vhh in ((vh, 1.4, 1.2) if stor else (vh, 1.2)):
            e = R['etasje'] if m == 1 else min(R['etasje'], (tak - vhh - b0) / (m - 1))
            if b0 + vhh <= tak + 1e-9 and (m == 1 or e >= ETASJE_MIN):
                return ut + [(b0 + e * k, vb if vhh >= 1.4 else R['vb'], vhh) for k in range(m)], dropp
        m -= 1; dropp += 1
    return ut, dropp


def velg(N, k, lov, stotte):
    """k av aksene 0..N-1 (blant lov) med jevn rytme (alle mellomrom et helt antall ganger det minste, som regel 17),
    flest mulig rett over en åpning under (stotte), helst symmetrisk. Gir (liste, rytme_ok)."""
    lov = sorted(lov)
    if k <= 0 or not lov:
        return [], True
    k = min(k, len(lov))
    def rytme(c):
        if len(c) < 3:
            return True
        d = np.diff(c); s = d.min()
        return bool(np.all(d % s == 0))
    def poeng(c):
        st = sum(i in stotte for i in c); sym = sum((N - 1 - i) not in c for i in c)
        d = np.diff(c) if len(c) > 1 else np.array([0])
        return (-st, sym, float(np.var(d)), abs(sum(c) / len(c) - (N - 1) / 2))
    if math.comb(len(lov), k) <= 40000:
        alle = list(itertools.combinations(lov, k))
        gode = [c for c in alle if rytme(c)]
        if gode:
            return list(min(gode, key=poeng)), True
        return list(min(alle, key=poeng)), False
    c = sorted({lov[round(i * (len(lov) - 1) / (k - 1))] for i in range(k)}) if k > 1 else [lov[len(lov) // 2]]
    return c, rytme(c)


def lag_fasade(x, w, P, rader, dorer, stor):
    """Elementene på gateveggen w. Gir (vind, info)."""
    h = x['h']; L = w['L']
    hoyder, dropp = radhoyder(rader, h, stor)
    rader = rader[:len(hoyder)]                 # kjellerraden står først; det som ikke får plass, faller fra toppen
    info = dict(droppet_rader=dropp)
    forste = next((i for i, r in enumerate(rader) if r[0] == 'etg'), None)
    bakke = {i for i, r in enumerate(rader) if r[0] == 'kjeller'} | ({forste} if forste is not None else set())

    def ledig(t, b):
        return any(f0 <= t - b / 2 - 0.3 and t + b / 2 + 0.3 <= f1 for f0, f1 in w['fri'])

    def hj(t, b):
        return VR.hjorne_ok(P, w['a'] + w['u'] * t, b)

    vmax = max([vb for _, vb, _ in hoyder] + [R['vb']])     # aksene må tåle det bredeste vinduet (regel 04)

    def sok(dorer):
        """Rutenett med lik avstand, så nær 0,85 m fra hjørnene som mulig, alle akser gyldige (ledig + hjørneklaring),
        og dørene på nærmeste ledige akse som tåler dørbredden (døra smalnes inn mot vinduet ved siden av)."""
        nd = len(dorer)
        N = max([(t or 0) + (nd if i in bakke else 0) for i, (_, t) in enumerate(rader)] + [nd])
        spenn = [(0.0, L)] + sorted([tuple(f) for f in w['fri'] if f[1] - f[0] < L - 0.1], key=lambda f: f[0] - f[1])
        for n in range(N, 0, -1):
            for s0, s1 in spenn:
                S = s1 - s0
                for kant in np.arange(R['kant'], min(S / 2, 3.0) + 1e-9, 0.05):
                    ts = [s0 + S / 2] if n == 1 else [s0 + kant + i * (S - 2 * kant) / (n - 1) for i in range(n)]
                    cc = (S - 2 * kant) / (n - 1) if n > 1 else S
                    if n > 1 and cc < CC_MIN:
                        break
                    if not all(ledig(t, vmax) and hj(t, vmax) for t in ts):
                        continue
                    tatt, dp = set(), []
                    for s, db, dh, typ in dorer:
                        mal = s * L if w['venstre_til_hoyre'] else (1 - s) * L
                        db2 = max(0.9, min(db, 2 * (cc - R['vb'] / 2 - 0.15))) if n > 1 else db
                        kand = sorted((abs(t - mal), i) for i, t in enumerate(ts) if i not in tatt and ledig(t, db2) and hj(t, db2))
                        if not kand:
                            break
                        i = kand[0][1]; tatt.add(i); dp.append((i, db2, min(dh, h - R['gesims'] - 0.1), typ))
                    if len(dp) == nd:
                        return N, ts, dp, cc
                if n == 1:
                    break
        return N, None, None, None

    N, ts, dp, cc = sok(dorer)
    info['akser_onsket'] = N
    if N == 0:                       # Street View: ingen vinduer og ingen dør på denne veggen
        return [], dict(info, akser=0, rader=[0] * len(rader), dorer=0, rytme_ok=True)
    if ts is None and dorer:
        N2, ts, dp, cc = sok([]); info['merk'] = 'dørene fikk ikke plass, bare vinduer'
    if ts is None:
        return [], dict(info, akser=0, merk='ingen gyldig akse på veggen', rader=[], dorer=0)
    n = len(ts)
    info.update(akser=n, cc=round(cc, 2), akser_t=[round(t, 2) for t in ts])
    dor_akser = {i for i, *_ in dp}
    ut = [VR.element(P, w['a'] + w['u'] * ts[i], db, w['n'], dh / 2, db, dh, typ) for i, db, dh, typ in dp]
    under = set(dor_akser); plassert = []; rytme_ok = True; sel = []
    for r, ((slag, k), (bz, vb, vh)) in enumerate(zip(rader, hoyder)):
        lov = [i for i in range(n) if not (r in bakke and i in dor_akser)]
        if vb > R['vb'] + 1e-9 and cc - vb < 0.4:
            vb = R['vb']
        sel, ok = velg(n, len(lov) if k is None else k, lov, under)     # tall mangler for raden: alle aksene
        rytme_ok &= ok; plassert.append(len(sel))
        ut += [VR.element(P, w['a'] + w['u'] * ts[i], vb, w['n'], bz + vh / 2, vb, vh, 0) for i in sel]
        under |= set(sel)
    info.update(rader=plassert, dorer=len(dp), rytme_ok=rytme_ok, topp_akser=sel)
    return ut, info


def lag_arker(x, g, w, P, arker, akser_t, topp):
    """Arker over gateveggen, i vindusaksene der taket har rom (på valmtak er det lite rom ut mot endene). Gir (arker, notat)."""
    if not arker:
        return [], ''
    t2 = x.get('tak2')
    if not t2:
        return [], 'huset har ikke tak2'
    th = x.get('th', 0.82); h = x['h']; Pg = Polygon(P).buffer(0); innenfor = Pg.buffer(-0.3)
    if not stiger(x, w):              # gavl mot gata eller flatt tak
        return [], 'taket stiger ikke fra gatesiden (gavl eller flatt tak), arker ikke lagt inn'

    def rom(t):
        """(front-z, plass under mønet) for en ark med front i t langs veggen, eller None."""
        q = w['a'] + w['u'] * t - w['n'] * DYBDE_ARK
        if not innenfor.contains(Point(*q)):
            return None
        tf = t_paa_tak(t2, *q)
        if tf is None:
            return None
        tm, d = tf, DYBDE_ARK
        while d < 40:      # oppover takflaten til mønet
            d += 0.25; qq = w['a'] + w['u'] * t - w['n'] * d
            if not Pg.contains(Point(*qq)):
                break
            v = t_paa_tak(t2, *qq)
            if v is None or v < tm - 0.05:
                break
            tm = max(tm, v)
        z = h + tf * th + 0.05
        return q, z, h + tm * th - z - 0.1

    MIN_ROM = 0.6 + 0.8 * 0.55
    k = len(arker)
    lov = [i for i, t in enumerate(akser_t or []) if (r := rom(t)) and r[2] >= MIN_ROM]
    if len(lov) >= k:
        sel, _ = velg(len(akser_t), k, lov, set(topp))
        ts = [akser_t[i] for i in sel]
    else:   # for få vindusakser med rom: jevnt fordelt over den lengste strekningen med rom
        prøver = [t for t in np.arange(0.5, w['L'] - 0.5 + 1e-9, 0.25) if (r := rom(t)) and r[2] >= MIN_ROM]
        bit, beste = [], []
        for t in prøver:
            bit = bit + [t] if bit and t - bit[-1] < 0.3 else [t]
            if len(bit) > len(beste):
                beste = bit
        ts = []
        if beste:
            a0, a1 = beste[0], beste[-1]; n = k
            while n > 1 and (a1 - a0) / (n - 1) < 1.1:
                n -= 1
            ts = [(a0 + a1) / 2] if n == 1 else [a0 + i * (a1 - a0) / (n - 1) for i in range(n)]
    ut = []
    for t, (bw, hb) in zip(ts, arker):
        q, z, plass = rom(t)
        hb2 = min(hb, plass - bw * 0.55); bw2 = bw
        if hb2 < 0.6:                    # lavt tak: smalere ark (mindre saltak)
            hb2 = min(hb, 0.6); bw2 = round(min(bw, (plass - hb2) / 0.55), 2)
        ut.append([round(float(q[0]), 2), round(float(q[1]), 2), til_grunn(z, x, g),
                   round(float(w['n'][0]), 4), round(float(w['n'][1]), 4), bw2, round(hb2, 2)])
    borte = k - len(ut)
    return ut, (f'{borte} av {k} arker fikk ikke rom under mønet' if borte else '')


def lag_piper(x, g, w, P, piper):
    """Piper på mønet over gateveggen, i rekkefølgen fra venstre. Gir (piper, notat)."""
    t2 = x.get('tak2')
    if not t2:
        return None, 'huset har ikke tak2, pipene beholdes'
    th = x.get('th', 0.82); Pg = Polygon(P).buffer(0)
    ang = round(math.degrees(math.atan2(w['u'][1], w['u'][0])), 1)
    ut = []
    for s in piper:
        t = (s if w['venstre_til_hoyre'] else 1 - s) * w['L']
        t = min(max(t, 1.0), w['L'] - 1.0) if w['L'] > 2 else w['L'] / 2
        best, d = None, 0.3
        while d < 60:
            q = w['a'] + w['u'] * t - w['n'] * d
            if not Pg.buffer(-0.5).contains(Point(*q)):
                if best:
                    break
                d += 0.25; continue
            v = t_paa_tak(t2, *q)
            if v is not None and (best is None or v > best[0] + 1e-3):
                best = (v, q)
            elif best is not None and v is not None and v < best[0] - 0.3:
                break
            d += 0.25
        if best is None:
            continue
        z = x['h'] + best[0] * th
        ut.append([round(float(best[1][0]), 2), round(float(best[1][1]), 2), til_grunn(z, x, g), ang])
    return ut, ''


# ---------------------------------------------------------------- sammenligning (fasit-husene)
def rader_paa_veggen(vind, V, wi):
    """Vinduer per rad (nederst først) og dører på vegg wi."""
    bunn, dor = [], 0
    for v in vind:
        k, _ = VG.naermeste_vegg(V, np.array(v[:2]))
        if k != wi:
            continue
        if v[9] in (1, 2) or (v[8] >= 1.9 and v[2] - v[8] / 2 < 0.3):
            dor += 1
        else:
            bunn.append(v[2])
    bunn.sort(); rader = []
    for b in bunn:
        if rader and b - rader[-1][0] < 1.0:
            rader[-1][1] += 1
        else:
            rader.append([b, 1])
    return [n for _, n in rader], dor


def like_rader(a, b):
    """Samme antall vinduer per rad, der rader uten vinduer ikke teller."""
    return [k for k in a if k] == [k for k in b if k]


def paa_siden(arker, w):
    return [a for a in arker or [] if a[3] * w['n'][0] + a[4] * w['n'][1] > 0.9]


# ---------------------------------------------------------------- hovedløpet
def tilstand():
    """Husene slik kartet viser dem uten dette verktøyets linjer."""
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    return ret, d, {g['id']: g for g in grunn}


FASIT_SV = {}
FASIT_SV_FIL = os.path.join(ROT, 'rapport', 'streetview-fasader', 'fasit-sv-vegger.json')


def kjor(tørt=False):
    FASIT_SV.clear()
    avl = json.load(open(KILDE, encoding='utf8'))
    hopp = {k: v for k, v in json.load(open(HOPP, encoding='utf8')).items() if not k.startswith('_')}
    ret, d, grunn = tilstand()
    fasit_ret = {r['id'] for r in ret if r['op'] == 'sett' and r.get('felt') == 'vind'
                 and (r.get('grunn', '').startswith('v33') or r.get('grunn', '').startswith('Kaserna'))}
    porter = {p['bygg_id'] for p in d.get('porter', []) if p.get('bygg_id')}
    B = {x['id']: x for x in d['bygg']}
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    nye, logg = [], []
    for id_, a in avl.items():
        x = B.get(id_); rad = dict(id=id_, navn=a.get('navn') or (x or {}).get('navn'), sikkerhet=a.get('sikkerhet'))
        def hoppet(grunn_):
            logg.append(dict(rad, status='hoppet over', grunn=grunn_))
        if x is None:
            hoppet('finnes ikke i bygg.json'); continue
        if a.get('sikkerhet') == 'ikke synlig':
            hoppet('ikke synlig fra gata'); continue
        if x.get('kirke') or x.get('deler'):
            hoppet('egen modell (kirka / bygg med deler)'); continue
        if x.get('skjul'):
            hoppet('skjult i kartet'); continue
        if id_ in porter:
            hoppet('portbygg (data/porter.json røres ikke)'); continue
        if id_ in hopp:
            hoppet(hopp[id_]); continue
        V = VG.vegger(x, omg, slaa_sammen=True)
        P = np.array(x['p'], float)
        er_fasit = x.get('fasade_kilde') == 'kvartaltegning' or id_ in fasit_ret
        # andre vegger beholder det de har (antatte hus i Gamlebyen: det vinduer_regler gir dem)
        if x.get('fasade_kilde') == 'antatt' and x.get('gml') and not x.get('deler'):
            base = VR.lag_vind(x, omg)[0]
        elif x.get('fasade_kilde') == 'streetview' and x.get('gml') and not x.get('deler') and not er_fasit:
            base = VR.lag_vind(x, omg)[0]       # forrige kjøring er tatt ut av tilstanden; reglene er grunnlaget
        else:
            base = x.get('vind') or []
        sett_vegger, gate_alle, sett_info, ark_ny, ark_sider, pip_ny = {}, [], [], [], [], None
        for sd in sider(a):
            r_ = dict(rad)
            rader = les_etasjer(sd); dorer = les_dorer(sd.get('dorer'))
            arker = les_arker(sd.get('takvinduer')); piper = les_piper(sd.get('piper'))
            if rader is None:
                hoppet(f"ingen vindustall ({sd.get('retning') or 'gatesiden'})"); continue
            C, heading = kamera(sd)
            if C is None:
                hoppet('pano_url mangler kamerapunkt/retning'); continue
            gavl = bool(re.search(r'gavl(en|siden)? mot|på gavlen|gavlen mot|-gavl', ' '.join(str(sd.get(k) or '') for k in ('etasjer', 'merknad', 'dorer', 'retning')).lower()))
            wi, notat = gatevegg(x, V, omg, C, heading, gavl)
            if wi is None:
                wi = retningsvegg(x, V, sd.get('retning'))
                if wi is None:
                    hoppet(f"{notat} ({sd.get('retning') or ''})"); continue
                notat = f"veggen valgt etter retningen i avlesningen ({sd.get('retning')}); {notat}"
            if wi in sett_vegger:
                logg.append(dict(r_, status='hoppet over', grunn=f"samme vegg ({wi}) som en annen side: {sd.get('retning')}")); continue
            w = V[wi]
            f = np.array([math.sin(math.radians(heading)), math.cos(math.radians(heading))])
            hoyre = np.array([-w['n'][1], w['n'][0]])          # seerens høyre når en ser mot veggen (mot -n)
            w['venstre_til_hoyre'] = bool(w['u'] @ hoyre > 0)
            mid = (w['a'] + w['c']) / 2
            r_.update(side=sd.get('retning'), vegg=wi, vegg_L=round(w['L'], 1), avstand=round(float(np.linalg.norm(mid - C)), 1),
                      vinkel=round(math.degrees(math.acos(max(-1, min(1, (mid - C) @ f / np.linalg.norm(mid - C))))), 0),
                      sv=dict(rader=[list(q) for q in rader], dorer=sd.get('dorer'), takvinduer=sd.get('takvinduer'), piper=sd.get('piper')),
                      notat=notat)
            if er_fasit:
                mr, md = rader_paa_veggen(x.get('vind') or [], V, wi)
                sv_rader = [k for _, k in rader]
                r_.update(status='fasit, bare sammenlignet', modell=dict(rader=mr, dorer=md, arker=len(paa_siden(x.get('arker'), w)),
                          piper=len(x.get('piper') or [])), avvik=not like_rader(mr, sv_rader), dorer_avvik=dorer is not None and md != len(dorer))
                logg.append(r_); sett_vegger[wi] = True
                # fasaden Street View gir på denne veggen: fasade_tegning.py legger den inn der tegningen ikke viser veggen (30.10)
                stor_ = bool(re.search(r'store vinduer', (sd.get('merknad') or '').lower()))
                g_, inf_ = lag_fasade(x, w, P, rader, dorer if dorer is not None else [], stor_)
                if g_ and not (inf_.get('akser', 0) < inf_.get('akser_onsket', 0) or inf_.get('merk')):
                    FASIT_SV.setdefault(id_, []).append(dict(mid=[round(float(mid[0]), 2), round(float(mid[1]), 2)],
                                                            n=[round(float(w['n'][0]), 4), round(float(w['n'][1]), 4)], vind=g_,
                                                            kilde=f"Street View {sd.get('bilde_dato') or ''}".strip(), rader=inf_.get('rader', [])))
                continue
            gamle_dorer = []
            for v in base:
                k, t = VG.naermeste_vegg(V, np.array(v[:2]))
                if k == wi and v[9] in (1, 2):
                    s_ = t / w['L'] if w['venstre_til_hoyre'] else 1 - t / w['L']
                    gamle_dorer.append((s_, v[7], v[8], v[9]))
            if dorer is None:
                dorer = gamle_dorer; r_['dorer_fra'] = 'beholdt (ukjent i Street View)'
            stor = bool(re.search(r'store vinduer', (sd.get('merknad') or '').lower()))
            gate, info = lag_fasade(x, w, P, rader, dorer, stor)
            if info.get('akser', 0) < info.get('akser_onsket', 0) or info.get('merk'):
                logg.append(dict(r_, status='hoppet over', grunn=f"veggen (vegg {wi}, {w['L']:.1f} m) har plass til {info.get('akser', 0)} akser, Street View trenger "
                       f"{info.get('akser_onsket')}{' – ' + info['merk'] if info.get('merk') else ''}: trolig feil vegg eller feil hus i modellen"
                       f"{'; ' + notat if notat else ''}"))
                continue
            sett_vegger[wi] = True; gate_alle += gate
            sett_info.append(dict(kilde=f"Street View {sd.get('bilde_dato') or ''}".strip(), sikkerhet=a.get('sikkerhet'), side=sd.get('retning'),
                                  vegg=[round(float(mid[0]), 2), round(float(mid[1]), 2)],
                                  n=[round(float(w['n'][0]), 4), round(float(w['n'][1]), 4)],
                                  kamera=[round(float(C[0]), 1), round(float(C[1]), 1)], heading=heading,
                                  rader=info.get('rader', []), dorer=info.get('dorer', 0)))
            if arker is not None:
                ny_ark, an = lag_arker(x, grunn.get(id_), w, P, arker, info.get('akser_t'), info.get('topp_akser') or [])
                if an: r_['arker_notat'] = an
                if ny_ark or not arker:
                    ark_ny += ny_ark; ark_sider.append(w); r_['arker'] = len(ny_ark)
            if piper is not None and pip_ny is None:
                pip, pn = lag_piper(x, grunn.get(id_), w, P, piper)
                if pip is not None:
                    pip_ny = pip; r_['piper'] = len(pip)
                    if len(pip) < len(piper): r_['piper_notat'] = f'{len(piper) - len(pip)} piper fant ikke plass på taket'
                else:
                    r_['piper_notat'] = pn
            r_.update(status='endret', info=info)
            logg.append(r_)
        if er_fasit or not sett_info:
            continue
        resten = [v for v in base if VG.naermeste_vegg(V, np.array(v[:2]))[0] not in sett_vegger]
        vind = resten + gate_alle
        linjer = [('vind', vind), ('fasade_kilde', 'streetview'), ('fasade_sv', sett_info[0] if len(sett_info) == 1 else dict(sett_info[0], sider=sett_info))]
        if ark_sider:
            behold = [q for q in (x.get('arker') or []) if not any(q in paa_siden(x.get('arker'), w) for w in ark_sider)]
            linjer.append(('arker', behold + ark_ny))
        if pip_ny is not None:
            linjer.append(('piper', pip_ny))
        for felt, verdi in linjer:
            nye.append({"emne": "bygg", "id": id_, "op": "sett", "felt": felt, "verdi": verdi, "hvem": "Claude", "dato": DATO, "grunn": GRUNN})
    os.makedirs(UT, exist_ok=True)
    json.dump(logg, open(os.path.join(UT, 'kjoring.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(FASIT_SV, open(FASIT_SV_FIL, 'w', encoding='utf8'), ensure_ascii=False)
    skriv_rapport(logg)
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
    e = [r for r in logg if r['status'] == 'endret']; h = [r for r in logg if r['status'] == 'hoppet over']
    fa = [r for r in logg if r['status'].startswith('fasit')]
    print(f"{len(e)} hus endret, {len(fa)} fasithus sammenlignet ({sum(1 for r in fa if r['avvik'])} med avvik), {len(h)} hoppet over"
          f"{' (tørt: ingenting skrevet)' if tørt else ''}")
    return logg


def skriv_rapport(logg):
    L = ['# Street View-fasader', '', f'Kjørt av verktoy/streetview_fasader.py. Kilde: kilder/streetview/avlesning.json. Kontrollark: ark.png (endrede hus), ark-fasit.png (fasithus).', '']
    e = [r for r in logg if r['status'] == 'endret']
    L += [f'## Endret ({len(e)})', '', '| id | navn | SV rader | lagt inn | dører | arker | piper | merknad |', '|---|---|---|---|---|---|---|---|']
    for r in e:
        i = r['info']; m = []
        if i.get('droppet_rader'): m.append(f"{i['droppet_rader']} rad(er) fikk ikke plass under gesims")
        if i.get('akser', 0) < i.get('akser_onsket', 0): m.append(f"plass til {i.get('akser')} av {i.get('akser_onsket')} akser")
        if not i.get('rytme_ok', True): m.append('rytmen ikke jevn')
        for k in ('arker_notat', 'piper_notat', 'notat', 'dorer_fra'):
            if r.get(k): m.append(r[k])
        L.append(f"| {r['id']} | {r.get('navn') or ''} | {[k for s, k in r['sv']['rader']]} | {i.get('rader')} | {i.get('dorer')} | "
                 f"{r.get('arker', '–')} | {r.get('piper', '–')} | {'; '.join(m)} |")
    fa = [r for r in logg if r['status'].startswith('fasit')]
    L += ['', f'## Fasithus fra kvartaltegningene, bare sammenlignet ({len(fa)})', '',
          'Gatesiden (veggen mot kameraet). Rader nederst først. Ingen endring er gjort.', '',
          '| id | navn | SV rader | tegning rader | SV dører | tegning dører | SV takv. | tegning arker | SV piper | tegning piper | avvik |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in fa:
        m = r['modell']; s = r['sv']
        L.append(f"| {r['id']} | {r.get('navn') or ''} | {[k for _, k in s['rader']]} | {m['rader']} | {s['dorer']} | {m['dorer']} | "
                 f"{s['takvinduer']} | {m['arker']} | {s['piper']} | {m['piper']} | {'ja' if r['avvik'] else ''} |")
    h = [r for r in logg if r['status'] == 'hoppet over']
    L += ['', f'## Hoppet over ({len(h)})', ''] + [f"- {r['id']} {r.get('navn') or ''}: {r['grunn']}" for r in h]
    open(os.path.join(UT, 'sammenligning.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')


# ---------------------------------------------------------------- kontrollark
def ark():
    """Fasaden rett forfra (sett fra kameraet) for hvert endret hus og hvert fasithus, tegnet fra dataene (ingen foto)."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
        FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
    except OSError:
        F = FB = ImageFont.load_default()
    logg = json.load(open(os.path.join(UT, 'kjoring.json'), encoding='utf8'))
    d = datalag.alle(); B = {x['id']: x for x in d['bygg']}
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    for navn, utvalg in (('ark.png', [r for r in logg if r['status'] == 'endret']),
                         ('ark-fasit.png', [r for r in logg if r['status'].startswith('fasit')])):
        if not utvalg:
            continue
        PW, PH, K = 520, 330, 3
        rows = math.ceil(len(utvalg) / K)
        im = Image.new('RGB', (PW * K, PH * rows + 40), (250, 249, 246)); dr = ImageDraw.Draw(im)
        dr.text((10, 10), ('Street View-fasader lagt inn' if navn == 'ark.png' else 'Fasithus (kvartaltegning): modellen som den er, SV-tallene til sammenligning')
                + ' – gatesiden sett fra kameraet, venstre i bildet = venstre i Street View. Blå = vindu, brun = dør, rød = pipe.', fill=(0, 0, 0), font=FB)
        for n, r in enumerate(utvalg):
            x = B[r['id']]; V = VG.vegger(x, omg, slaa_sammen=True); w = V[r['vegg']]
            hoyre = np.array([-w['n'][1], w['n'][0]]); lr = w['u'] @ hoyre > 0
            ox, oy = (n % K) * PW + 12, (n // K) * PH + 44
            s = r['sv']
            dr.text((ox, oy), f"{r['id']} {r.get('navn') or ''}"[:60], fill=(0, 0, 0), font=FB)
            dr.text((ox, oy + 16), f"SV rader {[k for _, k in s['rader']]}  dører: {str(s['dorer'])[:38]}", fill=(60, 60, 60), font=F)
            dr.text((ox, oy + 30), f"SV takvinduer {str(s['takvinduer'])[:20]}  piper {str(s['piper'])[:22]}  ({r['sikkerhet']})", fill=(60, 60, 60), font=F)
            mr, md = rader_paa_veggen(x.get('vind') or [], V, r['vegg'])
            dr.text((ox, oy + 44), f"modell rader {mr}  dører {md}  arker {len(paa_siden(x.get('arker'), w))}  piper {len(x.get('piper') or [])}  vegg {w['L']:.1f} m, h {x['h']}",
                    fill=(40, 110, 40) if like_rader(mr, [k or 0 for _, k in s['rader']]) else (150, 40, 40), font=F)
            # målestokk
            th = x.get('th', 0.82); tmax = 0.0; prof = []
            for j in range(41):
                t = w['L'] * j / 40; best = 0.0; dd = 0.2
                while dd < 40:
                    q = w['a'] + w['u'] * t - w['n'] * dd
                    if not Polygon(x['p']).buffer(0).contains(Point(*q)): break
                    v = t_paa_tak(x.get('tak2'), *q)
                    if v is not None: best = max(best, v)
                    dd += 0.4
                prof.append((t, x['h'] + best * th)); tmax = max(tmax, best)
            H = x['h'] + tmax * th + 2
            sk = min((PW - 30) / max(w['L'], 1), (PH - 80) / max(H, 1))
            bx, by = ox + 5, oy + PH - 20
            def X(t): return bx + sk * (t if lr else w['L'] - t)
            def Y(z): return by - sk * z
            dr.rectangle([min(X(0), X(w['L'])), Y(x['h']), max(X(0), X(w['L'])), by], fill=tuple(x.get('vegg') or (220, 220, 220)), outline=(60, 60, 60))
            dr.polygon([(X(t), Y(z)) for t, z in prof] + [(X(w['L']), Y(x['h'])), (X(0), Y(x['h']))], fill=tuple(x.get('tak') or (150, 150, 150)), outline=(60, 60, 60))
            dr.line([(bx - 4, by), (bx + sk * w['L'] + 4, by)], fill=(0, 0, 0), width=2)
            for v in x.get('vind') or []:
                k, t = VG.naermeste_vegg(V, np.array(v[:2]))
                if k != r['vegg']: continue
                x0, x1 = sorted((X(t - v[7] / 2), X(t + v[7] / 2)))
                dr.rectangle([x0, Y(v[2] + v[8] / 2), x1, Y(v[2] - v[8] / 2)],
                             fill=(110, 70, 50) if v[9] in (1, 2) else (90, 130, 190), outline=(30, 30, 30))
            for q in paa_siden(x.get('arker'), w):
                t = float((np.array(q[:2]) - w['a']) @ w['u']); z = q[2]
                x0, x1 = sorted((X(t - q[5] / 2), X(t + q[5] / 2)))
                zz = z
                dr.rectangle([x0, Y(zz + q[6]), x1, Y(zz - 0.25)], fill=tuple(x.get('vegg') or (220, 220, 220)), outline=(30, 30, 30))
                dr.polygon([(x0 - 2, Y(zz + q[6])), ((x0 + x1) / 2, Y(zz + q[6] + q[5] * 0.55)), (x1 + 2, Y(zz + q[6]))], fill=tuple(x.get('tak') or (120, 120, 120)), outline=(30, 30, 30))
                dr.rectangle([x0 + 3, Y(zz + q[6] - 0.15), x1 - 3, Y(zz + 0.1)], fill=(90, 130, 190))
            for q in x.get('piper') or []:
                t = float((np.array(q[:2]) - w['a']) @ w['u'])
                if -1 <= t <= w['L'] + 1:
                    dr.rectangle([X(t) - sk * 0.45, Y(q[2] + 1.4), X(t) + sk * 0.45, Y(q[2] - 0.3)], fill=(204, 98, 82), outline=(30, 30, 30))
        im.save(os.path.join(UT, navn))
        print('skrev', os.path.join(UT, navn))


if __name__ == '__main__':
    if 'ark' in sys.argv[1:]:
        ark()
    else:
        kjor('--tørt' in sys.argv)
