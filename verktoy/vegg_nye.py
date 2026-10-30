"""Veggfarge etter fargeregelen (30.10, Vegar) for alle hus i Gamlebyen, og for hus utenfor som fortsatt har standardveggen.

  Nyeste kilde vinner:
    1) Street View 2016 eller senere: satt av verktoy/streetview_farger.py (rørt ikke her)
    2) tegningen: kvartaltegningen der kontrolløren har registrert huset, ellers 2015-trykkfila/2019-trykket
       (tak_farge.tegning_farger; Tøihuset lest for hånd)
    3) 2017-tegningen som vektor (verktoy/farger_tegning.py, samme artwork som 2019-trykket): veggbåndet under fotavtrykket,
       når fotavtrykket dekker tegnede husflater (dekning >= 0,5)
    4) Street View før 2015 (aug. 2010 o.l.): eldre enn tegningen, brukes bare der tegningen ikke har huset
    5) grunndataenes trykkfarge som ikke er dømt mot 2019-trykket (mange står hvite uten at trykket sier det)
    6) nabohuset: nærmeste hus med lest veggfarge, helst et som henger sammen med huset
  Skriver også farge_kilde = «vegg: …; tak: …» (tak_kilde fra verktoy/tak_farge.py) og vegg_kilde/vegg_aar, som
  verktoy/kontroll.py bruker til å skille «avvik med grunn» (kilden er nyere enn tegningen) fra feil.
  Lister hvert hus der regelen bytter farge (før -> etter, kilde, dato): rapport/farge/vegg-bytter.md og vegg.json.
Kjøres etter streetview_farger.py og tak_farge.py, før bygg_merknader.py (merknadene vinner).

    python3 verktoy/vegg_nye.py [--tørt]
"""
import os, sys, json
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
import tak_farge as T
import streetview_farger as SVF
from shapely.geometry import Polygon

GRUNN = 'veggfarge etter fargeregelen (verktoy/vegg_nye.py, 30.10)'
GAMMEL_GRUNN = 'veggfarge til nye hus (verktoy/vegg_nye.py, 30.10)'
STANDARD = T.STANDARD_VEGG
UT = os.path.join(ROT, 'rapport', 'farge')


def tegning_2017(maal):
    """Veggfargen i 2017-tegningen som vektor for husene i maal (liste av bygg) -> {id: (rgb, dekning)}."""
    import cv2, numpy as np, farger_tegning as FTG
    FTG.AI = os.path.join(ROT, 'kilder', 'ai', 'ai')
    ut = {}
    try:
        fl = FTG.hus_flater(); jp, lab = FTG.etikett(fl); S = 2
        A = np.load(os.path.join(FTG.AI, 'modell_h_til_2019.npy'))
    except FileNotFoundError as e:
        print('tegningen 2017 mangler lokalt:', e); return ut
    for x in maal:
        px = FTG.m2px(A, x['p'], x.get('h', 4)) * S
        c = px.mean(axis=0); r = 140
        x0, y0 = int(max(c[0] - r, 0)), int(max(c[1] - r, 0)); x1, y1 = int(c[0] + r), int(c[1] + r)
        L = lab[y0:y1, x0:x1]
        if L.size == 0: continue
        best = None
        for dx in range(-72, 73, 8):
            for dy in range(-72, 73, 8):
                m = np.zeros(L.shape, np.uint8); cv2.fillPoly(m, [(px + [dx - x0, dy - y0]).astype(np.int32)], 1); mm = m.astype(bool)
                if mm.sum() == 0: continue
                dek = (L[mm] >= 0).mean() - np.hypot(dx, dy) / 400
                if best is None or dek > best[0]: best = (dek, dx, dy, mm, (L[mm] >= 0).mean())
        if best is None: continue
        _, dx, dy, mm, dek = best
        hp = int(4 * S * max(2.5, x.get('h', 4)))
        band = np.zeros(L.shape, np.uint8); cv2.fillPoly(band, [(px + [dx - x0, dy - y0 + hp]).astype(np.int32)], 1); band[mm] = 0
        tak = FTG.dominerende(L, mm, fl); vegg = [v for v in FTG.dominerende(L, band.astype(bool), fl) if not tak or v[0] != tak[0][0]]
        if vegg:
            tv = [int(c_) for c_ in vegg[0][0]]
            papir = max(tv) - min(tv) < 12 and (min(tv) > 247 or max(tv) < 140)    # papir eller skygge, ikke en veggfarge
            if dek >= 0.5 and not papir:
                ut[x['id']] = (tv, round(float(dek), 2))
    return ut


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') not in (GRUNN, GAMMEL_GRUNN)]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = [x for x in d['bygg'] if not x.get('skjul') and len(x['p']) >= 3]
    TF = T.tegning_farger(T.tilstand_uten_regelen(ret), ret)
    sv = T.les_sv(); ids = T.gamlebyen_ider()
    for_ = {x['id']: x for x in T.tilstand_uten_regelen(None)}     # fargen før regelen: alt som lå i rettelsene før denne kjøringen
    gamle = {x['id']: x.get('vegg') for x in datalag.alle()['bygg']}
    maal = [x for x in B if not x.get('kirke') and (x['id'] in ids or list(x.get('vegg') or STANDARD) == STANDARD)]
    t17 = tegning_2017([x for x in maal if x['id'] not in TF or 'vegg' not in TF[x['id']]])
    # veggfarger merknadene setter (kilder/bygg-merknader.json, legges på sist av bygg_merknader.py): de står, men kilden og
    # året skrives her, så kontrolløren ser hvor fargen kommer fra
    merk = {}
    for m in json.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))['hus']:
        st = m.get('sett') or {}
        if st.get('vegg'):
            merk[m['id']] = (st['vegg'], f"merknad: {st.get('farge_kilde') or m.get('kilde')}")
    nye, ut, satt = [], [], {}
    for x in maal:
        i = x['id']; farge = kilde = aar = None
        if i in merk:                                                               # 0) merknaden (Vegar/hovedagenten) vinner
            farge, kilde = merk[i]
            aar = T.sv_aar(kilde) if 'Street View' in kilde else T.TEGNINGSAAR
        elif str(x.get('vegg_kilde') or '').startswith('Street View') and (x.get('vegg_aar') or 0) >= SVF.NYERE_ENN:
            farge, kilde, aar = x['vegg'], x['vegg_kilde'], x['vegg_aar']          # 1) satt av streetview_farger.py
        elif (TF.get(i) or {}).get('vegg'):
            farge, kilde, aar = TF[i]['vegg'][0], TF[i]['vegg'][1], T.TEGNINGSAAR   # 2) tegningen
        else:
            a = sv.get(i) or {}
            v = a.get('vegg') or {}
            sva = T.sv_vegg_aar(a)
            f = None if a.get('sikkerhet') == 'ikke synlig' else (SVF.fra_ord(v.get('farge'), SVF.VEGG) or SVF.fra_tall(v.get('rgb'), v.get('lys')))
            svak = (TF.get(i) or {}).get('vegg_svak')
            if i in t17:
                farge, kilde, aar = t17[i][0], f"2017-tegningen som vektor (dekning {t17[i][1]})", 2017
            elif f:
                grunn_ = ('tegningens flate på huset er liten og har en annen kulør (feil fasade, tak_farge.tegning_farger)' if svak and 'kvartaltegningen' in svak[1]
                          else 'tegningen har ikke huset')
                farge, kilde, aar = f, f"Street View {sva or 'uten dato'} ({v.get('farge')}); eldre enn tegningen, men {grunn_}", sva
            elif svak:
                farge, kilde, aar = svak[0], svak[1], T.TEGNINGSAAR
            else:
                kjente = [n for n in B if n['id'] != i and (n['id'] in satt or (n.get('vegg') and list(n['vegg']) != STANDARD and n['id'] not in ids))]
                nab = sorted(((Polygon(n['p']).distance(Polygon(x['p'])), n) for n in kjente), key=lambda q: q[0])
                if nab:
                    dist, n = nab[0]
                    farge = satt.get(n['id'], n['vegg']); kilde = f"nabohuset {n['id']} ({n.get('navn') or n.get('type') or 'hus'}, {dist:.1f} m unna)"
        if not farge:
            ut.append(dict(id=i, kilde=None)); continue
        farge = [int(c) for c in farge]; satt[i] = farge
        tk = x.get('tak_kilde') or ''
        fk = f"vegg: {kilde}; tak: {tk or 'som før'}"
        linjer = [('farge_kilde', fk)]
        if not (kilde == x.get('vegg_kilde')):
            linjer = [('vegg', farge), ('veggs', None), ('vegg_kilde', kilde), ('vegg_aar', aar)] + linjer
        for felt, verdi in linjer:
            nye.append(dict(emne='bygg', id=i, op='sett', felt=felt, verdi=verdi, hvem='Claude', dato='2026-10-30', grunn=GRUNN))
        f0 = for_.get(i, {})
        gammel = gamle.get(i)
        ut.append(dict(id=i, navn=x.get('navn'), adr=x.get('adr'), for_=gammel, for_kilde=f0.get('farge_kilde'), vegg=farge, kilde=kilde, aar=aar,
                       byttet=bool(gammel) and not T.samme_kulor(gammel, farge)))
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
        os.makedirs(UT, exist_ok=True)
        json.dump(ut, open(os.path.join(UT, 'vegg.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    for u in ut:
        print(u['id'], u.get('for_'), '->', u.get('vegg'), u['kilde'])
    print(f"{len(maal)} hus, {sum(1 for u in ut if u['kilde'])} fikk veggfarge, {sum(1 for u in ut if not u['kilde'])} uten kilde, "
          f"{sum(1 for u in ut if u.get('byttet'))} byttet kulør")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
