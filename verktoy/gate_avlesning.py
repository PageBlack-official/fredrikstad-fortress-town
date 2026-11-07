#!/usr/bin/env python3
"""Gatevandringen (06.11, Vegar): hus lest fra gata med gatekameraet, med Vegars øyne eller et Street View-bilde der datoen er sjekket.

Kilde: kilder/gate/avlesning.json. Hvert hus peker på et standpunkt i kilder/gate/standpunkter.json (Street View-lenka: punkt, retning,
dato). Gatekameraet (verktoy/gatekamera.mjs) tegner kartet fra samme punkt, så modell og foto sammenlignes i samme bilde.

Hvorfor et eget steg, sist i kjeden (bygg_kjede.py): dette er nyeste kilde og den eneste som er sjekket mot riktig hus i samme bilde.
06.11 viste to feil i rangeringen før dette steget:
  1) kvartaltegningen (2015) var «fasit» for vinduene, så Street View mai 2024 ble bare sammenlignet (Voldgaten 8 og 9);
  2) sv_kobling.py kastet riktig avlesning av Voldgaten 9 fordi strålen fra panoramaets retning traff naboen (Voldgaten 8).
Gatekameraet løser 2) ved at retningen regnes fra standpunktet til huset; steget her løser 1) ved å stå sist.

Feltene er de samme som i kilder/streetview/avlesning.json (samme lesere i streetview_fasader.py), pluss:
  standpunkt   navnet i kilder/gate/standpunkter.json     kilde   hvem som så det og når
Bare feltene som er lest, endres; et felt som mangler, lar huset være som kjeden ga det.

    python3 verktoy/gate_avlesning.py          skriver rettelsene (idempotent: egne linjer fra forrige kjøring tas ut først)
    python3 verktoy/gate_avlesning.py --tørt   viser bare
"""
import json, math, os, sys
import numpy as np

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import vinduer_regler as VR  # noqa: E402
import datalag, vegger as VG, streetview_fasader as SVF, streetview_farger as SVC  # noqa: E402

KILDE = os.path.join(ROT, 'kilder', 'gate', 'avlesning.json')
PUNKT = os.path.join(ROT, 'kilder', 'gate', 'standpunkter.json')
GRUNN = 'Gatevandring (gatekamera + Street View med dato)'



def halvvinkler(bilde):
    """(tan av halv vannrett, tan av halv loddrett synsvinkel). Street View-lenkas fov er loddrett (målt 07.11, se verktoy/gatekamera.mjs)."""
    Fv = math.radians(float(bilde.get('fov', 75))); B, Hh = float(bilde.get('bredde', 1280)), float(bilde.get('hoyde', 720))
    tv = math.tan(Fv / 2)
    return tv * B / Hh, tv


def vannrett_fov(sp):
    """vannrett synsvinkel i grader for et standpunkt (fov i lenka er loddrett)"""
    th, _ = halvvinkler(sp)
    return 2 * math.degrees(math.atan(th))

def hexfarge(v):
    """Farge som hex: '#rrggbb' lest rett fra bildet, ellers ordet («blå», «burgunder») via streetview_farger."""
    if not v: return None
    v = str(v).strip()
    if v.startswith('#') and len(v) == 7: return v.lower()
    rgb = SVC.fra_ord(v, SVC.VEGG)
    return '#%02x%02x%02x' % tuple(int(c) for c in rgb) if rgb else None


def rgbfarge(v, tabell):
    v = str(v or '').strip()
    if v.startswith('#') and len(v) == 7: return [int(v[i:i + 2], 16) for i in (1, 3, 5)]
    return SVC.fra_ord(v, tabell)


MAALT_FOR = {}       # (hus, vegg) -> elementer målt fra tidligere bilder i samme kjøring (lange vegger: flere bilder)
KANT = 0.15          # m fri mur mellom et element og veggens ende (hjørnet eller naboens vegg)
TYPER = {'vindu': 0, 'dor': 1, 'dør': 1, 'port': 2, 'butikk': 0, 'oksoye': 3, 'oksøye': 3}


def kamera_fra_hjorner(w, C0, bilde, les):
    """Panoramaets posisjon fra Google kan ligge flere meter feil mot kartet (Voldgaten 9, 07.11: 5 m nærmere veggen enn i bildet).
    Hjørnene i bildet (husets fasade fra hjørne til hjørne, u_venstre/u_hoyre) gir kameraet ved to peilinger: C er punktet der
    strålene mot veggens to ender har de vinklene bildet viser. Ett hjørne: kameraet flyttes langs veggen til den peilingen stemmer.
    Bakkelinja (v_bakke) gir øyehøyden. Gir (C, øye, hvordan)."""
    th, tv = halvvinkler(bilde)
    hd = math.radians(float(bilde['heading'])); p = math.radians(float(bilde.get('pitch', 90)) - 90)
    f = np.array([math.sin(hd), math.cos(hd)]); r = np.array([math.cos(hd), -math.sin(hd)])
    A = w['a']; E = w['a'] + w['u'] * w['L']
    def u_av(Q, C):                        # vannrett bildeposisjon for punktet Q sett fra C
        v = Q - C; z = float(v @ f)
        return 0.5 + float(v @ r) / z / th / 2 if z > 0.1 else None
    def stråle(u):
        return (2 * u - 1) * th * r + f
    hj = les.get('hjorner') or {}
    uv, uh = hj.get('u_venstre'), hj.get('u_hoyre')
    uA, uE = u_av(A, C0), u_av(E, C0)
    venstre_er_A = (uA if uA is not None else 0) <= (uE if uE is not None else 1)
    PL, PR = (A, E) if venstre_er_A else (E, A)
    C, hvordan = C0, 'panorama'
    if uv is not None and uh is not None and abs(uh - uv) > 0.05:
        dL, dR = stråle(float(uv)), stråle(float(uh))
        M = np.array([[dL[0], -dR[0]], [dL[1], -dR[1]]])
        if abs(np.linalg.det(M)) > 1e-6:
            sL, sR = np.linalg.solve(M, PL - PR)
            if sL > 1 and sR > 1:
                C, hvordan = PL - sL * dL, 'to hjørner'
    elif uv is not None or uh is not None:
        P, u = (PL, float(uv)) if uv is not None else (PR, float(uh))
        d = stråle(u)                                                      # kameraet ligger på linja P - s*d; nærmest C0 på den
        s = float((P - C0) @ d) / float(d @ d)
        if s > 1:
            C, hvordan = P - s * d, 'ett hjørne'
    oye = float(bilde.get('oye', 2.5))
    vb = les.get('v_bakke')
    if vb is not None:
        um = (float(uv) + float(uh)) / 2 if (uv is not None and uh is not None) else 0.5
        X, Y = (2 * um - 1) * th, (1 - 2 * float(vb)) * tv
        y2 = Y * math.cos(p) + math.sin(p); z2 = -Y * math.sin(p) + math.cos(p)
        d = X * r + z2 * f; dn = float(d @ w['n'])
        if abs(dn) > 1e-6 and y2 < 0:
            s = float((w['a'] - C) @ w['n']) / dn
            if s > 0:
                e = -s * y2
                if 1.2 <= e <= 4.0: oye = e
    return C, oye, hvordan


def fra_bilde(w, C, bilde, boks, oye=2.5):
    """Tegn av bildet (Vegar 06.11): en boks i Street View-bildet (u0..u1, v0..v1 i andel av bredde/høyde, v fra toppen) blir
    (t0, t1, z0, z1) på veggen w: strålene fra kameraet (C, øyehøyde, retning, helning, vannrett synsvinkel) skjæres med veggens
    loddrette plan. Gir None når strålen ikke treffer veggen foran kameraet."""
    th, tv = halvvinkler(bilde)
    hd = math.radians(float(bilde['heading'])); p = math.radians(float(bilde.get('pitch', 90)) - 90)
    f = np.array([math.sin(hd), math.cos(hd)]); r = np.array([math.cos(hd), -math.sin(hd)])
    def punkt(u, v):
        X, Y = (2 * u - 1) * th, (1 - 2 * v) * tv
        y2 = Y * math.cos(p) + math.sin(p); z2 = -Y * math.sin(p) + math.cos(p)
        d = X * r + z2 * f; dn = float(d @ w['n'])
        if abs(dn) < 1e-6: return None
        s = float((w['a'] - C) @ w['n']) / dn
        if s <= 0: return None
        Q = C + s * d
        return float((Q - w['a']) @ w['u']), oye + s * y2
    um, vm = (boks['u0'] + boks['u1']) / 2, (boks['v0'] + boks['v1']) / 2
    a, b, c, d = punkt(boks['u0'], vm), punkt(boks['u1'], vm), punkt(um, boks['v1']), punkt(um, boks['v0'])
    if None in (a, b, c, d): return None
    t0, t1 = sorted((a[0], b[0]))
    return t0, t1, max(0.0, c[1]), d[1]


MAALT_FOR = {}       # (hus, vegg) -> elementer målt fra tidligere bilder i samme kjøring (lange vegger: flere bilder)
KANT = 0.15          # m fri mur mellom et element og veggens ende (hjørnet eller naboens vegg)
TYPER = {'vindu': 0, 'dor': 1, 'dør': 1, 'port': 2, 'butikk': 0, 'oksoye': 3, 'oksøye': 3}


def fra_bilde(w, C, bilde, boks, oye=2.5):
    """Tegn av bildet (Vegar 06.11): en boks i Street View-bildet (u0..u1, v0..v1 i andel av bredde/høyde, v fra toppen) blir
    (t0, t1, z0, z1) på veggen w: strålene fra kameraet (C, øyehøyde, retning, helning, vannrett synsvinkel) skjæres med veggens
    loddrette plan. Gir None når strålen ikke treffer veggen foran kameraet."""
    th, tv = halvvinkler(bilde)
    hd = math.radians(float(bilde['heading'])); p = math.radians(float(bilde.get('pitch', 90)) - 90)
    f = np.array([math.sin(hd), math.cos(hd)]); r = np.array([math.cos(hd), -math.sin(hd)])
    def punkt(u, v):
        X, Y = (2 * u - 1) * th, (1 - 2 * v) * tv
        y2 = Y * math.cos(p) + math.sin(p); z2 = -Y * math.sin(p) + math.cos(p)
        d = X * r + z2 * f; dn = float(d @ w['n'])
        if abs(dn) < 1e-6: return None
        s = float((w['a'] - C) @ w['n']) / dn
        if s <= 0: return None
        Q = C + s * d
        return float((Q - w['a']) @ w['u']), oye + s * y2
    um, vm = (boks['u0'] + boks['u1']) / 2, (boks['v0'] + boks['v1']) / 2
    a, b, c, d = punkt(boks['u0'], vm), punkt(boks['u1'], vm), punkt(um, boks['v1']), punkt(um, boks['v0'])
    if None in (a, b, c, d): return None
    t0, t1 = sorted((a[0], b[0]))
    return t0, t1, max(0.0, c[1]), d[1]


KANT = 0.15          # m fri mur mellom et element og veggens ende (hjørnet eller naboens vegg)
TYPER = {'vindu': 0, 'dor': 1, 'dør': 1, 'port': 2, 'butikk': 0, 'oksoye': 3, 'oksøye': 3}


def lag_fasade_maalt(x, w, P, maalt, C=None, bilde=None, deler=(0, 1), les=None):
    """Gul side (Vegar 06.11): elementene står der bildet viser dem. Hvert element har enten bildeboks (u0, u1, v0, v1: tegnes av
    gjennom kameraet, fra_bilde) eller andeler av veggen (x0, x1 fra venstre sett fra gata; y0, y1 fra bakken til takfoten).
    Ingen rytme- eller hjørneregler bestemmer. Kantsjekken (som skulle ha stoppet butikkvinduet i Voldportgaten 75 fra å gå inn i
    Voldgaten 9) krymper bare det som krysser veggens ende eller et annet element, og logger det. Gir (vind, info)."""
    L = w['L']; H = max(2.4, float(x['h']) - SVF.R['gesims'] * 0.5)
    ut, kant, kastet, plass, utenfor = [], 0, 0, [], 0
    oye, hvordan = float((bilde or {}).get('oye', 2.5)), None
    if C is not None and bilde and les:
        C, oye, hvordan = kamera_fra_hjorner(w, C, bilde, les)
    for e in maalt:
        typ = TYPER.get(str(e.get('type', 'vindu')).lower(), 0)
        if 'u0' in e and C is not None and bilde:
            m = fra_bilde(w, C, bilde, e, oye)
            if m is None:
                kastet += 1; continue
            t0, t1, z0, z1 = m
            if t1 < 0 or t0 > L:
                utenfor += 1; continue
        else:
            x0, x1 = sorted((float(e['x0']), float(e['x1']))); y0, y1 = sorted((float(e['y0']), float(e['y1'])))
            k, n = deler
            x0, x1 = (k + x0) / n, (k + x1) / n
            if not w['venstre_til_hoyre']:
                x0, x1 = 1 - x1, 1 - x0
            t0, t1, z0, z1 = x0 * L, x1 * L, y0 * H, y1 * H
        if t0 < KANT: t0 = KANT; kant += 1
        if t1 > L - KANT: t1 = L - KANT; kant += 1
        z0, z1 = max(0.0, z0), min(z1, H - 0.08)
        if typ in (1, 2) and z0 < 0.25: z0 = 0.0                              # dører står på bakken (trapp: der bildet viser)
        for (p0, p1, q0, q1) in plass:                                         # overlapp med et element ved siden av
            if t0 < p1 and t1 > p0 and z0 < q1 and z1 > q0:
                if (t0 + t1) / 2 >= (p0 + p1) / 2: t0 = p1 + 0.08
                else: t1 = p0 - 0.08
                kant += 1
        b = t1 - t0
        while b >= 0.3 and not VR.hjorne_ok(P, w['a'] + w['u'] * ((t0 + t1) / 2), b):
            b -= 0.1; kant += 1
        if b < 0.3 or z1 - z0 < 0.3:
            kastet += 1; continue
        tm = (t0 + t1) / 2; t0, t1 = tm - b / 2, tm + b / 2
        el = VR.element(P, w['a'] + w['u'] * tm, round(b, 2), w['n'], round((z0 + z1) / 2, 2), round(b, 2), round(z1 - z0, 2), typ)
        f = hexfarge(e.get('farge'))
        if f: el = el + [f]
        ut.append(el); plass.append((t0, t1, z0, z1))
    dorer = sum(1 for e in ut if e[9] in (1, 2))
    return ut, dict(maalt=len(ut), kantsjekk=kant, kastet=kastet, utenfor=utenfor, dorer=dorer, kamera=hvordan, oye=round(oye, 2))


def aaret(dato):
    """År fra en dato som «2024-05» eller «mai 2024» (Street View-kortet)."""
    import re
    m = re.search(r'(19|20)\d\d', str(dato or ''))
    return int(m.group(0)) if m else 0


def tilstand():
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    return ret, d, {g['id']: g for g in grunn}



def _oyekontroll():
    """husene som er godkjent etter øyekontroll (kilder/gate/godkjent-*.json); None = ingen kontroll lagt inn (alle slipper)"""
    import glob as _g
    filer = sorted(_g.glob(os.path.join(ROT, 'kilder', 'gate', 'godkjent-*.json')))
    if not filer: return lambda i: True
    ok = set()
    for f in filer: ok |= set(json.load(open(f, encoding='utf8')).get('godkjent', {}))
    return lambda i: i in ok

def kjor(tørt=False):
    if not os.path.exists(KILDE):
        print('0 hus (ingen kilder/gate/avlesning.json)'); return
    avl = [a for a in json.load(open(KILDE, encoding='utf8')) if not a.get('id', '').startswith('_')]
    punkt = {p['navn']: p for p in json.load(open(PUNKT, encoding='utf8'))}
    OYE = _oyekontroll()
    ret, d, grunn = tilstand()
    B = {x['id']: x for x in d['bygg']}
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    dato = __import__('datetime').date.today().isoformat()
    nye, logg = [], []
    for a in avl:
        id_ = a['id']; x = B.get(id_); sp = punkt.get(a.get('standpunkt'))
        if x is not None and a.get('hvem') != 'Vegar' and (id_ in getattr(datalag, 'EGNE_FASADER', {}) or x.get('spesiell')):
            logg.append(f'{id_}: hoppet over (eget fasadeverktøy)'); continue
        if x is None or sp is None:
            logg.append(f'{id_}: hoppet over ({"finnes ikke" if x is None else "ukjent standpunkt"})'); continue
        if a.get('hvem') != 'Vegar' and not x.get('gml'):
            logg.append(f'{id_}: hoppet over (utenfor Gamlebyen, tegnes blekt med malte vinduer)'); continue
        C = np.array(datalag.til_modell(sp['lon'], sp['lat']))
        P = np.array(x['p'], float); mid_hus = P.mean(axis=0); v = mid_hus - C
        heading = (math.degrees(math.atan2(v[0], v[1])) + 360) % 360     # fra standpunktet mot huset, ikke panoramaets retning
        V = VG.vegger(x, omg, slaa_sammen=True)
        wi, notat = SVF.gatevegg(x, V, omg, C, heading)
        if wi is None:   # vinkelhus/lange rekker: midtpunktet ligger utenfor fasaden; søk over bildets bredde fra standpunktets retning
            for dh in sorted(range(-int(vannrett_fov(sp)) // 2, int(vannrett_fov(sp)) // 2 + 1, 5), key=abs):
                wi, notat = SVF.gatevegg(x, V, omg, C, (sp['heading'] + dh) % 360)
                if wi is not None:
                    heading = (sp['heading'] + dh) % 360; break
        if wi is None:
            logg.append(f'{id_}: hoppet over ({notat})'); continue
        w = V[wi]
        hoyre = np.array([-w['n'][1], w['n'][0]]); w['venstre_til_hoyre'] = bool(w['u'] @ hoyre > 0)
        kilde = f"{a.get('kilde', 'gatevandring')}; standpunkt {sp['navn']} ({sp.get('dato', '')})"
        linjer, info_ut = [], {}
        rader = SVF.les_etasjer(a)
        if a.get('maalt'):
            gate, info = lag_fasade_maalt(x, w, P, a['maalt'], C, sp, (int(a.get('del', 0)), int(a.get('deler', 1))), a)
            resten = [e for e in (x.get('vind') or []) if VG.naermeste_vegg(V, np.array(e[:2]))[0] != wi] + MAALT_FOR.get((id_, wi), [])
            # Skjult 1. etasje (hekk, biler, 07.11): bildet viser bare de øvre radene. Da står vinduene regelen satte under de målte,
            # i stedet for en blank 1. etasje.
            if gate and min(e[2] - e[8] / 2 for e in gate) > 2.2:
                bunn = min(e[2] - e[8] / 2 for e in gate)
                under = [e for e in (x.get('vind') or []) if VG.naermeste_vegg(V, np.array(e[:2]))[0] == wi and e[2] + e[8] / 2 < bunn - 0.2]
                gate = gate + under; info['beholdt_under'] = len(under)
            MAALT_FOR.setdefault((id_, wi), []).extend(gate)
            # Sorte sider (Vegar 06.11): veggene ingen ser fra gata får vinduene den gule siden har: samme vindusstørrelse (median av de
            # målte), sentrum der regelen satte dem. Krymper til hjørneklaringen hvis det trengs; dører og porter står som de var.
            mv = [e for e in gate if e[9] == 0]
            if len(mv) >= 2:
                bw, bh = float(np.median([e[7] for e in mv])), float(np.median([e[8] for e in mv]))
                sim = []
                for e in resten:
                    if e[9] != 0 or MAALT_FOR.get((id_, VG.naermeste_vegg(V, np.array(e[:2]))[0])):
                        sim.append(e); continue
                    b2 = bw
                    while b2 > 0.5 and not VR.hjorne_ok(P, np.array(e[:2], float), b2): b2 -= 0.05
                    e2 = list(e); e2[7] = round(b2, 2); e2[8] = round(bh, 2); sim.append(e2)
                resten = sim; info['simulert'] = sum(1 for e in resten if e[9] == 0)
            linjer += [('vind', resten + gate), ('fasade_kilde', 'gatevandring-maalt'),
                       ('fasade_sv', dict(kilde=kilde, vegg=[round(float(q), 2) for q in (w['a'] + w['c']) / 2],
                                          n=[round(float(q), 4) for q in w['n']], rader=[], dorer=info['dorer']))]
            info_ut = dict(maalt=info['maalt'], kantsjekk=info['kantsjekk'], kastet=info['kastet'], utenfor=info['utenfor'], kamera=info['kamera'], oye=info['oye'], simulert=info.get('simulert', 0))
            rader = None
            if a.get('hvem') != 'Vegar' and not (OYE(id_) and info['kamera'] in ('to hjørner', 'ett hjørne') and info['kastet'] == 0 and info['utenfor'] == 0
                                                  and info['kantsjekk'] <= 2 and info['maalt'] >= 2):
                linjer = [l for l in linjer if l[0] not in ('vind', 'fasade_kilde', 'fasade_sv')]
                info_ut = dict(maalt_avvist=info)
                L_ = MAALT_FOR.get((id_, wi), []); [L_.remove(e) for e in gate if e in L_]
            arker = SVF.les_arker(a.get('takvinduer')) if a.get('hvem') == 'Vegar' else None
            if arker is not None:
                ny, an = SVF.lag_arker(x, grunn.get(id_), w, P, arker, None, [])
                gavl = [q for q in (x.get('arker') or []) if abs(q[3] * w['n'][0] + q[4] * w['n'][1]) <= 0.5]
                behold = [q for q in (x.get('arker') or []) if q not in SVF.paa_siden(x.get('arker'), w) and q not in gavl]
                linjer.append(('arker', behold + ny)); info_ut['arker'] = len(ny)
        if rader is not None:
            dorer = SVF.les_dorer(a.get('dorer'))
            if dorer is None:   # ukjent: dørene huset har på veggen, beholdes
                dorer = []
                for e in x.get('vind') or []:
                    k, t = VG.naermeste_vegg(V, np.array(e[:2]))
                    if k == wi and e[9] in (1, 2):
                        dorer.append((t / w['L'] if w['venstre_til_hoyre'] else 1 - t / w['L'], e[7], e[8], e[9]))
            gate, info = SVF.lag_fasade(x, w, P, rader, dorer, bool(a.get('store_vinduer')), streng=True)
            if not gate or info.get('akser', 0) < info.get('akser_onsket', 0) or info.get('merk'):
                gate, info = SVF.lag_fasade(x, w, P, rader, dorer, bool(a.get('store_vinduer')))
                info['dor_ikke_eksakt'] = True
            if not gate or info.get('akser', 0) < info.get('akser_onsket', 0) or info.get('merk'):
                logg.append(f"{id_}: vinduene fikk ikke plass på vegg {wi} ({w['L']:.1f} m): {info}"); continue
            if a.get('butikk_nederst') and gate:
                # butikklokale i 1. etg (Voldportgaten 75, 06.11): vinduene i nederste rad blir utstillingsvinduer, 0,5 m over gata,
                # 2,1 m høye og så brede som aksene tåler (minst 0,5 m murpille)
                vind0 = [e for e in gate if e[9] == 0]
                if vind0:
                    z0 = min(e[2] for e in vind0); bred = min(2.0, max(0.85, info.get('cc', 2.0) - 0.5))
                    gate = [list(e[:2]) + [1.55] + list(e[3:7]) + [round(bred, 2), 2.1] + list(e[9:]) if (e[9] == 0 and abs(e[2] - z0) < 0.01) else e for e in gate]
                    # kantsjekk (Vegar 06.11: venstre butikkvindu i Voldportgaten 75 gikk inn i Voldgaten 9): smalere til hjørneklaringen holder
                    for e in gate:
                        if e[9] == 0 and abs(e[2] - 1.55) < 0.01 and abs(e[8] - 2.1) < 0.01:
                            while e[7] > 0.6 and not VR.hjorne_ok(P, np.array(e[:2], float), e[7]):
                                e[7] = round(e[7] - 0.05, 2)
                    info['butikkvinduer'] = sum(1 for e in vind0 if abs(e[2] - z0) < 0.01)
            resten = [e for e in (x.get('vind') or []) if VG.naermeste_vegg(V, np.array(e[:2]))[0] != wi]
            linjer += [('vind', resten + gate), ('fasade_kilde', 'gatevandring'),
                       ('fasade_sv', dict(kilde=kilde, vegg=[round(float(q), 2) for q in (w['a'] + w['c']) / 2],
                                          n=[round(float(q), 4) for q in w['n']], rader=info.get('rader', []), dorer=info.get('dorer', 0)))]
            info_ut = dict(rader=info.get('rader'), dorer=info.get('dorer'), butikkvinduer=info.get('butikkvinduer', 0))
            arker = SVF.les_arker(a.get('takvinduer'))
            if arker is not None:
                ny, an = SVF.lag_arker(x, grunn.get(id_), w, P, arker, info.get('akser_t'), info.get('topp_akser') or [])
                # Ark på gavlen (normal på tvers av gateveggen) kan ikke finnes på et saltak sett fra gata. 06.11: Voldgaten 9 hadde
                # to slike fra håndmodellen, der gavlen vendte mot gata; tak_enkel.py snudde taket 30.10, arkene ble stående.
                gavl = [q for q in (x.get('arker') or []) if abs(q[3] * w['n'][0] + q[4] * w['n'][1]) <= 0.5]
                behold = [q for q in (x.get('arker') or []) if q not in SVF.paa_siden(x.get('arker'), w) and q not in gavl]
                linjer.append(('arker', behold + ny)); info_ut['arker'] = len(ny); info_ut['arker_paa_gavl_fjernet'] = len(gavl)
        piper = SVF.les_piper(a.get('piper')) if a.get('hvem') == 'Vegar' else None
        if piper is not None:
            pip, pn = SVF.lag_piper(x, grunn.get(id_), w, P, piper)
            if pip is not None:
                linjer.append(('piper', pip)); info_ut['piper'] = len(pip)
        vegg = rgbfarge(a.get('vegg'), SVC.VEGG) if a.get('hvem') == 'Vegar' else None
        if vegg:
            # Fasadesegmenter fra kvartaltegningen (2015) går foran vegg i tegningen (src/07). Den leste veggen får én farge.
            seg = [s for s in (x.get('fasadesegmenter') or [])
                   if VG.naermeste_vegg(V, (np.array(s['a'], float) + np.array(s['b'], float)) / 2)[0] != wi]
            if len(seg) != len(x.get('fasadesegmenter') or []):
                linjer.append(('fasadesegmenter', seg or None)); info_ut['fasadesegmenter_fjernet'] = len(x['fasadesegmenter']) - len(seg)
            linjer += [('vegg', vegg), ('veggs', None), ('vegg_kilde', f"{a.get('vegg')} ({kilde})"), ('vegg_aar', aaret(sp.get('dato')))]
        for felt, nokkel in (('dor_farge', 'dorfarge'), ('karm_farge', 'karmfarge')):
            f = hexfarge(a.get(nokkel))
            if f: linjer.append((felt, f))
        if a.get('takform') in ('sal', 'valm', 'halvvalm', 'pult', 'vinkel'):
            linjer.append(('takform_lest', a['takform']))
        tak = rgbfarge(a.get('tak'), SVC.TAK) if a.get('hvem') == 'Vegar' else None
        if tak:
            linjer += [('tak', tak), ('taks', None), ('tak_kilde', f"{a.get('tak')} ({kilde})")]
        for felt, verdi in linjer:
            nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': felt, 'verdi': verdi, 'hvem': a.get('hvem', 'Claude'), 'dato': dato, 'grunn': GRUNN})
        logg.append(f"{id_}: vegg {wi} ({w['L']:.1f} m) {info_ut} vegg={vegg} tak={tak}")
    print('\n'.join(logg))
    print(f'{len({n["id"] for n in nye})} hus fra gatevandringen')
    if not tørt:
        datalag.skriv_rettelser(ret + nye)


if __name__ == '__main__':
    kjor('--tørt' in sys.argv)
