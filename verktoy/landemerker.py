"""Landemerkene (30.10, natt/landemerker): det besøkende kjenner igjen, bygd etter Vegars 2015-tegninger (form), Kartverkets
DOM−DTM (plass og høyde) og Street View / ortofoto 2024 (dagens farger). Kjøres sist i kjeden (etter fasade_former.py), så
ingen annen rettelse overstyrer den. Hver post under LANDEMERKER sier hva som settes og hvorfor; elementene tegnes av src/07
(bygTaarn for deler med form 'taarn', bygArkade for bygg.arkader) og src/10 (portbyggene, data/porter.json).

    python3 verktoy/landemerker.py [--tørt]

Elementene er generelle (et nytt tårn eller en ny arkade = en ny post her, ingen ny kode):
  taarn    bygg.deler[] {form: 'taarn', c, r, sider, rot, skaft, krage, h, ut, tinde_h, tinder, vegg, veggs, topp, vinduer, stang, flagg}
  arkader  bygg.arkader[] {a, b, z0, h, topp, n, bredde, dybde, mork}   rundbuer med dybde langs veggen a→b
  fasade   vinduer erstattet på én fasade (polylinje i modellmeter): elementer i u (meter fra første punkt)
"""
import json, math, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
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
                       kilde='Kvartal10.ai: gårdsfasaden mot sør har en åpen arkade med fem rundbuer nede og gesimsbånd over')

VOLDPORTEN = 'bnr-193869548'
# Voldporten (1695). DTM under huset er vollkrona (9,4–10,4 moh), så DOM−DTM (4–8 m) måler fra vollen, ikke fra veien. Veien i
# porten: 7,0 moh på innsiden (vest), 6,3 på utsiden (øst). DOM: mønet 17,8 moh, takfoten ca. 14,5. Fra veien: takfot 7,5 m, møne
# 10,8 m. Street View aug. 2010 (yttersiden SØ): portmur i grå naturstein med rundbuet tunnel (bredde ca. 0,47 av muren, toppen ca.
# 0,8 av murhøyden), hvitkalket vaktstue oppå, valmet teglstak med kort møne og én pipe midt på mønet. Tegningen (Glasshytta.ai,
# egen bit) viser det samme: huset på portmuren, valm mot enden.
VOLDPORT_PORT = dict(h=4.4, pw=3.8, ph=3.5)
# vaktstuens vinduer (høyde over portmuren): SSV-langsida som Glasshytta.ai (dør ved vestenden, to vinduer; andeler 0,25, 0,53, 0,81
# av fasaden målt i tegningen), NV-enden som Street View aug. 2010 (to vinduer med 2 x 3 ruter ved 0,30 og 0,65 av bredden).
# SØ-enden (yttersiden) har ingen vinduer, bare relieffet og to blindfelt (Street View 2010); tegningens tomme ramme der er blindfeltet.
VOLDPORT_FASADER = [dict(linje=[[201.31, 40.3], [214.4, 33.99]], andeler=True,
                         vinduer=[(0.25, 1.05, 0.9, 2.0, 1, 0), (0.53, 1.75, 0.8, 1.1, 0, 0), (0.81, 1.75, 0.8, 1.1, 0, 0)]),
                    dict(linje=[[201.31, 40.3], [204.74, 47.43]], andeler=True,
                         vinduer=[(0.30, 1.75, 0.8, 1.2, 0, 0), (0.65, 1.75, 0.8, 1.2, 0, 0)])]


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
        if -0.3 <= s <= Lab + 0.3 and d < 0.8 and v[5] * n[0] + v[6] * n[1] > 0.9 and v[2] - v[8] / 2 < A['topp']:
            continue
        ut.append(list(v))
    return ut


def porter_voldporten(tørt):
    f = os.path.join(ROT, 'data', 'porter.json'); P = json.load(open(f, encoding='utf8'))
    for p in P:
        if p.get('bygg_id') == VOLDPORTEN:
            p.update(VOLDPORT_PORT)
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
    print(VOLDPORTEN, f'portmur {VOLDPORT_PORT["h"]} m, vaktstue h {x.get("h")} (kilder/hoyde-unntak.json)')
    if not tørt:
        datalag.skriv_rettelser(ret + nye)


if __name__ == '__main__':
    main('--tørt' in sys.argv)
