"""Husfarger fra tegningen som vektor (28.10): 2017-tegningen (Gamlebyen+Isegran2017.ai, samme artwork som 2019-trykket) leses som
vektorflater, så trær og tekst som ligger over husene i trykket ikke skjuler fargen. Trær (grønt), strek (svart) og halvgjennomsiktige
teksturer tas ut; resten rastreres i tegnerekkefølge til et etikettbilde i 2019-trykkets piksler (kilder/ai/ai2017_til_2019.npy,
ORB-registrert, residual 1,4 px). Fotavtrykket projiseres med kilder/ai/modell_h_til_2019.npy (tilpasset px2019 i rapport/farger2019.json,
median 5 px) og flyttes ±36 px til flest punkter lander på husflater (husene er tegnet fritt). Tak = største flate under fotavtrykket,
vegg = største flate i båndet rett under. Bruk:
    python3 verktoy/farger_tegning.py forslag          -> rapport/farger-tegning/forslag.json + kontrollark (bare grå hus uten dom)
    python3 verktoy/farger_tegning.py legg-inn         -> rettelser (grunn: tegningen 2017 som vektor), idempotent
Kildefilene (.ai, jpg) ligger bare lokalt (kilder/ai, ikke i git): åndsverk, se KILDER.md."""
import sys, os, json, pickle, colorsys
import numpy as np, cv2
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROT)
import datalag
AI = os.path.join(ROT, 'kilder', 'ai'); UT = os.path.join(ROT, 'rapport', 'farger-tegning'); os.makedirs(UT, exist_ok=True)
GRUNN = 'tegningen 2017 som vektor (trær tatt bort), lest mot 2019-trykkets plassering (verktoy/farger_tegning.py)'
def er_tre(c):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(c) / 255)); return 0.18 < h < 0.48 and s > 0.18
def er_strek(c): return max(c) < 70
def hus_flater():
    rows = pickle.load(open(os.path.join(AI, 'ai2017-flater.pkl'), 'rb')); M = np.load(os.path.join(AI, 'ai2017_til_2019.npy'))
    ut = []
    for r in rows:
        if r['layer'] not in ('bygninger', 'Isegran') or er_tre(r['fill']) or er_strek(r['fill']): continue
        p = r['p'] @ M[:, :2].T + M[:, 2]; ut.append((p, r['fill']))
    return ut
def etikett(flater, S=2):
    jp = cv2.imread(os.path.join(AI, 'brosjyre2019-3.jpg')); H, W = jp.shape[:2]
    lab = np.full((H * S, W * S), -1, np.int32)
    for i, (p, c) in enumerate(flater): cv2.fillPoly(lab, [(p * S).astype(np.int32)], i)
    return jp, lab
def m2px(A, p, h):
    p = np.asarray(p, float); X = np.column_stack([p, np.full(len(p), h), np.ones(len(p))]); return X @ A
def dominerende(lab, maske, flater, minst=0.08):
    ids, n = np.unique(lab[maske], return_counts=True); tot = maske.sum(); ut = []
    for i, k in sorted(zip(ids, n), key=lambda t: -t[1]):
        if i < 0 or k < minst * tot: continue
        ut.append((flater[i][1], k / tot))
    return ut
def les(b, maal, flater, lab, jp, S=2, ark=True):
    A = np.load(os.path.join(AI, 'modell_h_til_2019.npy')); forslag = {}
    H, W = lab.shape
    for i in maal:
        x = b[i]; px = m2px(A, x['p'], x.get('h', 4)); best = None
        for dx in range(-36, 37, 4):
            for dy in range(-36, 37, 4):
                q = ((px + [dx, dy]) * S).astype(np.int32); m = np.zeros_like(lab, np.uint8); cv2.fillPoly(m, [q], 1); mm = m.astype(bool)
                if mm.sum() == 0: continue
                dekning = (lab[mm] >= 0).mean(); straff = np.hypot(dx, dy) / 200
                if best is None or dekning - straff > best[0]: best = (dekning - straff, dx, dy, mm, dekning)
        if best is None: continue
        _, dx, dy, mm, dekning = best
        tak = dominerende(lab, mm, flater)
        # bånd under fotavtrykket: 4 px per meter vegghøyde, flyttet ned fra laveste kant
        q = ((px + [dx, dy]) * S).astype(np.int32); hp = int(4 * S * max(2.5, x.get('h', 4)))
        band = np.zeros_like(lab, np.uint8); cv2.fillPoly(band, [q + [0, hp]], 1); band[mm] = 0; bm = band.astype(bool)
        vegg = [v for v in dominerende(lab, bm, flater) if not tak or v[0] != tak[0][0]]
        def par(liste):
            if not liste: return None, None
            lys = max(liste[:2], key=lambda t: sum(t[0])); mork = min(liste[:2], key=lambda t: sum(t[0]))
            return list(lys[0]), (list(mork[0]) if len(liste) > 1 and mork[0] != lys[0] else None)
        t, ts = par(tak); v, vs = par(vegg)
        forslag[x['id']] = dict(plass=i, navn=x.get('navn'), tak=t, taks=ts, vegg=v, veggs=vs, dekning=round(float(dekning), 2), flytt=[dx, dy], naa=dict(vegg=x.get('vegg'), tak=x.get('tak')))
        if ark:
            c = px.mean(axis=0) + [dx, dy]; x0, y0 = int(c[0] - 90), int(c[1] - 90)
            crop = jp[max(0, y0):y0 + 180, max(0, x0):x0 + 180].copy()
            cv2.polylines(crop, [(px + [dx, dy] - [max(0, x0), max(0, y0)]).astype(np.int32)], True, (255, 0, 255), 1)
            crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
            sw = np.full((crop.shape[0], 160, 3), 255, np.uint8)
            for k, (navn, col) in enumerate([('vegg nå', x.get('vegg')), ('vegg ny', v), ('tak nå', x.get('tak')), ('tak ny', t)]):
                if col: cv2.rectangle(sw, (10, 10 + k * 120), (150, 100 + k * 120), tuple(int(z) for z in col[::-1]), -1)
                cv2.putText(sw, navn, (12, 112 + k * 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            out = np.concatenate([crop, sw], axis=1)
            cv2.putText(out, f"{x['id']} {x.get('navn') or x.get('type')} dekning {dekning:.2f}", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)
            cv2.imwrite(os.path.join(UT, f"{x['id']}.jpg"), out)
    return forslag
def gra(c): return not c or max(c[:3]) - min(c[:3]) < 14
if __name__ == '__main__':
    b = datalag.koble_til_plass(datalag.alle())['bygg']
    dom = json.load(open(os.path.join(ROT, 'rapport', 'farger-dom', 'dom.json')))
    maal = [i for i, x in enumerate(b) if x.get('gml') and not x.get('skjult') and not x.get('kirke') and gra(x.get('vegg')) and dom.get(str(i), '-') in ('?', '-')]
    if sys.argv[1:] == ['forslag']:
        flater = hus_flater(); jp, lab = etikett(flater); print(len(flater), 'husflater i tegningen;', len(maal), 'grå hus uten dom')
        f = les(b, maal, flater, lab, jp); json.dump(f, open(os.path.join(UT, 'forslag.json'), 'w'), indent=1, ensure_ascii=False)
        print(len(f), 'forslag ->', os.path.join(UT, 'forslag.json'))
    elif sys.argv[1:] == ['legg-inn']:
        f = json.load(open(os.path.join(UT, 'forslag.json')))
        R = [r for r in datalag.les('rettelser') if not r.get('grunn', '').startswith('tegningen 2017 som vektor')]; n = 0
        for id_, v in f.items():
            if v['dekning'] < 0.5 or not v['vegg']: continue
            for felt in ('vegg', 'veggs', 'tak', 'taks'):
                if v.get(felt): R.append(dict(emne='bygg', id=id_, op='sett', felt=felt, verdi=v[felt], hvem='Claude', dato='2026-10-28', grunn=GRUNN + f", dekning {v['dekning']}"))
            n += 1
        datalag.skriv_rettelser(R); print(n, 'hus fått farge fra tegningen')
