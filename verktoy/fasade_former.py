"""Formene i tegningen som fasadeavlesningen ikke fanger (30.10): rundbuevinduer, grønne porter i hvite portaler og antall piper,
lest av Vegars kvartaltegning for hus der kontrolløren (rapport/kontroll/avvik.md) fant avvik. Vinduenes antall og plass står som
før (fasade_tegning.py / merknadene); her endres bare formen, portalfargen og pipene.

  vindu_bue     alle vinduer (typ 0) får rund bue øverst (bue = 1; tegnes i src/07: typ 0 med bue 0,5–1,5)
  port_gronn    portene (typ 2, buet topp) blir grønne fløydører med overlys (bue = 2, som Kaserna)
  portal_hvit   hvitt veggfelt rundt hver port, gesims til bakke (b + 2 × kant)
  piper         pipene som tegningen viser, [x, y]; mønehøyden regnes av datalaget (til_monet / hoyden_styrer)
  kirka         høydene (bygg.kirke.hoyder, tegnes i src/06) og silhuetten i h/tak2 som kontrolløren registrerer tegningen mot

    python3 verktoy/fasade_former.py [--tørt]       etter bygg_merknader.py (sist i kjeden)
"""
import os, sys, json
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag

GRUNN = 'former fra tegningen (verktoy/fasade_former.py, 30.10)'
FORMER = {
    # Tøihuset: tegningen (kilder/kvartal-ai/Toihuset.ai) har rundbuevinduer med sprosser, grønne porter med buet topp i hvite
    # portaler, og to takhatter side om side på nordfløyen ~17 % fra vestenden pluss én pipe på sørfløyen ~59 % fra vestenden
    # (modellen hadde 19 piper langs mønene). Fargene: tak_farge.HAANDLEST.
    'bnr-193870279': dict(kilde='kvartaltegningen Toihuset', vindu_bue=True, port_gronn=True, portal_hvit=(244, 241, 232), portal_kant=0.45,
                          piper=[[-112.5, -82.2], [-117.1, -81.1], [-48.7, -157.8]]),
}


KIRKE = 'bnr-193867529'
# Kirkas høyder (meter over bakken). Skipet: Kartverkets DOM−DTM 25.10 (takfot 8,8 m, møne 14,4 m). Tårnet (30.10): DOM−DTM har
# murkronen på 18–19 m langs tårnkanten og 32 m midt over lanternen/kuppelen; spiret er for tynt for 1 m-rutene, så toppen over
# kuppelen er fra kvartaltegningen kirke.ai i tegningens egen målestokk (tårnmur 447 pt = 18,5 m, hele tårnet 910 pt = 37,6 m).
# src/06 leser disse (bygg.kirke.hoyder); h og tak2 på kirka er silhuetten verktoy/kontroll.py registrerer tegningen mot.
KIRKE_HOYDER = dict(WH=8.8, RISE=5.6, SH=18.5, SK1=22.8, OV1=26.9, LA0=28.0, LA1=30.5, KU1=32.0, SP1=36.7, TS=0.7,
                    kilde='DOM−DTM (Kartverket) for skip, murkrone og lanterne; kirke.ai for spiret')

# Landemerke (Vegar 30.10: «for at det skal funke i et slikt kart må tårnet fungere mer dramatisk – ikke korrekt ... landemerker man
# bruker for å orientere seg»). Tårnet vises 1,6 ganger de målte høydene (omtrent som trykkfila: mur 34 m, spir 60 m), detaljene over
# muren 1,3 ganger. KIRKE_HOYDER er fortsatt de målte tallene; kontrollen og silhuetten bruker dem.
KIRKE_VISNING = dict(skala=1.6, detalj=1.3, grunn='landemerke: dramatisk, ikke korrekt (Vegar 30.10)')


def kirke_silhuett(k, H):
    """Takflater (tak2-format, z over h = WH, th = 1) som gir kirkas silhuett: korsarmene med valm, tårnet som loddrette flater
    og hjelmen som pyramide til kuppelen, spiret som en smal trekant. Tårnet er 1,3 ganger grunnrisset om siden mot skipet
    (som src/06)."""
    import numpy as np
    WH = H['WH']; sk = [tuple(q) for q in k['skip']]; n = len(sk)
    F = []
    L = [np.hypot(sk[(i + 1) % n][0] - sk[i][0], sk[(i + 1) % n][1] - sk[i][1]) for i in range(n)]
    ender = [i for i in range(n) if L[i] > 12]
    for i in ender:
        j = (i + n // 2) % n
        if j not in ender or j < i:
            continue
        a0, a1, b0, b1 = np.array(sk[i]), np.array(sk[(i + 1) % n]), np.array(sk[j]), np.array(sk[(j + 1) % n])
        m1, m2 = (a0 + a1) / 2, (b0 + b1) / 2; ax = m2 - m1; Ln = np.hypot(*ax); u = ax / Ln; nn = np.array([-u[1], u[0]])
        w = np.hypot(*(a1 - a0)) / 2; R = H['RISE']
        P = lambda s_, t_, z: [round(float(v), 2) for v in (m1 + u * s_ + nn * t_)] + [round(z, 2)]
        F += [[P(0, -w, 0), P(Ln, -w, 0), P(Ln - w, 0, R), P(w, 0, R)], [P(0, w, 0), P(w, 0, R), P(Ln - w, 0, R), P(Ln, w, 0)],
              [P(0, w, 0), P(0, -w, 0), P(w, 0, R)], [P(Ln, -w, 0), P(Ln, w, 0), P(Ln - w, 0, R)]]
    t0 = np.array(k['torn'], float); c = np.mean(sk, axis=0)
    e = min(((t0[i] + t0[(i + 1) % 4]) / 2 for i in range(4)), key=lambda m: np.hypot(*(m - c)))
    t = e + (t0 - e) * 1.3; tc = t.mean(axis=0)
    zt = H['SH'] - WH
    for i in range(4):
        A, B = t[i], t[(i + 1) % 4]
        F.append([[*map(float, A), -WH], [*map(float, B), -WH], [*map(float, B), zt], [*map(float, A), zt]])
    zk = H['KU1'] - WH
    for i in range(4):
        A, B = t[i], t[(i + 1) % 4]
        F.append([[*map(float, A), zt], [*map(float, B), zt], [*map(float, tc + (B - tc) * 0.25), zk], [*map(float, tc + (A - tc) * 0.25), zk]])
    d = (t[1] - t[0]) / np.hypot(*(t[1] - t[0])) * 0.4
    F.append([[*map(float, tc - d), zk], [*map(float, tc + d), zk], [*map(float, tc), H['SP1'] - WH]])
    return [[[round(float(v), 2) for v in q] for q in f] for f in F]


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if not str(r.get('grunn', '')).startswith(GRUNN)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = {x['id']: x for x in d['bygg']}
    nye = []
    def sett(i, felt, verdi):
        nye.append(dict(emne='bygg', id=i, op='sett', felt=felt, verdi=verdi, hvem='Claude', dato='2026-10-30', grunn=f"{GRUNN}: {FORMER[i]['kilde']}"))
    for i, f in FORMER.items():
        x = B.get(i)
        if not x:
            print(i, 'finnes ikke'); continue
        vind = [list(v) for v in (x.get('vind') or [])]
        for v in vind:
            if f.get('vindu_bue') and v[9] == 0:
                v[10] = 1
            if f.get('port_gronn') and v[9] == 2:
                v[10] = 2
        sett(i, 'vind', vind)
        if f.get('portal_hvit'):
            felt = [list(fe) for fe in (x.get('veggfelt') or []) if list(fe[4:7]) != list(f['portal_hvit'])]
            for v in vind:
                if v[9] != 2:
                    continue
                b = v[7] / 2 + f.get('portal_kant', 0.6)
                felt.append([round(v[0] - v[3] * b, 2), round(v[1] - v[4] * b, 2), round(v[0] + v[3] * b, 2), round(v[1] + v[4] * b, 2)] + list(f['portal_hvit']))
            sett(i, 'veggfelt', felt)
        if f.get('piper') is not None:
            gamle = x.get('piper') or []
            nyp = []
            for px, py in f['piper']:
                n = min(gamle, key=lambda q: (q[0] - px) ** 2 + (q[1] - py) ** 2) if gamle else [px, py, x.get('h', 4) + 2, 0]
                mx, my = datalag.til_monet(x, px, py)
                nyp.append([round(mx, 2), round(my, 2), n[2], n[3]])
            sett(i, 'piper', nyp)
        print(i, f"{sum(1 for v in vind if v[9] == 0)} vinduer med rundbue, {sum(1 for v in vind if v[9] == 2)} porter grønne i hvite portaler, "
              f"{len(f.get('piper') or [])} piper (før {len(x.get('piper') or [])})")
    x = B.get(KIRKE)
    if x and x.get('kirke'):
        k = dict(x['kirke']); k['hoyder'] = KIRKE_HOYDER; k['visning'] = KIRKE_VISNING
        g = f"{GRUNN}: kirka (DOM−DTM + kirke.ai)"
        # fargene i data er de src/06 tegner (hvit puss, skifer: tegningen og ortofotoet viser mørkt skifertak), så kontrolløren
        # sammenligner riktig farge; kirka står utenfor fargeregelens verktøy (egen modell)
        for felt, verdi in (('kirke', k), ('h', KIRKE_HOYDER['WH']), ('th', 1.0), ('tak2', kirke_silhuett(k, KIRKE_HOYDER)),
                            ('tak', [128, 128, 132]), ('taks', [68, 68, 72]), ('vegg', [252, 252, 252]), ('veggs', [192, 196, 196]),
                            ('tak_kilde', 'src/06: skifer som kirke.ai og ortofoto 2024'), ('tak_aar', 2024),
                            ('vegg_kilde', 'src/06: hvit puss som kirke.ai og Street View 2024'), ('vegg_aar', 2024)):
            nye.append(dict(emne='bygg', id=KIRKE, op='sett', felt=felt, verdi=verdi, hvem='Claude', dato='2026-10-30', grunn=g))
        print(KIRKE, f"kirka: h {KIRKE_HOYDER['WH']} m (skipets takfot), tårnmur {KIRKE_HOYDER['SH']} m, spir {KIRKE_HOYDER['SP1']} m, silhuett i tak2")
    if not tørt:
        datalag.skriv_rettelser(ret + nye)


if __name__ == '__main__':
    main('--tørt' in sys.argv)
