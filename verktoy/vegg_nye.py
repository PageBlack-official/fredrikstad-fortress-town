"""Veggfarge på husene som fortsatt har standardveggen (nye hus fra kommunekartet, 30.10). Ingen nøytrale vegger igjen:
    1) Street View har forrang (streetview_farger.py har allerede satt fargen der huset er sett; de rører vi ikke)
    2) 2017-tegningen som vektor (samme artwork som 2019-trykket, verktoy/farger_tegning.py): veggbåndet under fotavtrykket,
       når fotavtrykket dekker tegnede husflater (dekning >= 0,5)
    3) nabohuset: nærmeste hus med lest veggfarge (Street View, tegning), helst et som henger sammen med huset
Kjøres etter tak_fra_ortofoto.py og før bygg_merknader.py (merknadene vinner).

    python3 verktoy/vegg_nye.py [--tørt]
"""
import os, sys, json
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag
from shapely.geometry import Polygon

GRUNN = 'veggfarge til nye hus (verktoy/vegg_nye.py, 30.10)'
STANDARD = [226, 222, 212]
RAPPORT = os.path.join(ROT, 'rapport', 'bygg', 'vegg-nye.json')


def lest(x):
    v = x.get('vegg'); k = (x.get('farge_kilde') or '')
    return v and list(v) != STANDARD and not k.startswith('standard') and 'vegg: standard' not in k


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if r.get('grunn', '').split(':')[0] != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = [x for x in d['bygg'] if not x.get('skjul') and len(x['p']) >= 3]
    maal = [x for x in B if list(x.get('vegg') or STANDARD) == STANDARD]
    # 2) tegningen 2017: fotavtrykket i 2019-trykkets piksler, flyttet ±36 px til flest punkter står på husflater; vegg = største
    #    flate i båndet under fotavtrykket (samme metode som farger_tegning.les, men i et utsnitt rundt huset: raskt)
    import cv2, numpy as np, farger_tegning as FTG
    FTG.AI = os.path.join(ROT, 'kilder', 'ai', 'ai')
    tegn = {}
    try:
        fl = FTG.hus_flater(); jp, lab = FTG.etikett(fl); S = 2
        A = np.load(os.path.join(FTG.AI, 'modell_h_til_2019.npy'))
        for k, x in enumerate(maal):
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
                tegn[k] = dict(dekning=round(float(dek), 2), vegg=[int(c_) for c_ in vegg[0][0]])
    except FileNotFoundError as e:
        print('tegningen 2017 mangler lokalt:', e)
    kjente = [x for x in B if lest(x)]
    nye, ut = [], []
    for k, x in enumerate(maal):
        t = tegn.get(k); P = Polygon(x['p'])
        kilde = farge = None
        tv = t.get('vegg') if t else None
        papir = tv and max(tv) - min(tv) < 12 and (min(tv) > 247 or max(tv) < 140)    # papir eller skygge, ikke en veggfarge
        if t and t['dekning'] >= 0.5 and tv and not papir:
            farge = [int(c) for c in t['vegg']]; kilde = f"2017-tegningen som vektor (dekning {t['dekning']})"
        else:
            nab = sorted(((Polygon(n['p']).distance(P), n) for n in kjente if n['id'] != x['id']), key=lambda q: q[0])
            if nab:
                dist, n = nab[0]
                farge = list(n['vegg']); kilde = f"nabohuset {n['id']} ({n.get('navn') or n.get('type') or 'hus'}, {dist:.1f} m unna)"
        if not farge:
            ut.append(dict(id=x['id'], kilde=None)); continue
        fk = x.get('farge_kilde') or ''
        tak_del = fk.split(';')[0] if fk.startswith('tak:') else 'tak: ' + (fk or 'standard')
        for felt, verdi in (('vegg', farge), ('farge_kilde', f"{tak_del}; vegg: {kilde}")):
            nye.append(dict(emne='bygg', id=x['id'], op='sett', felt=felt, verdi=verdi, hvem='Claude', dato='2026-10-30', grunn=GRUNN))
        ut.append(dict(id=x['id'], navn=x.get('navn'), type=x.get('type'), vegg=farge, kilde=kilde))
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
        os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
        json.dump(ut, open(RAPPORT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    for u in ut: print(u['id'], u.get('vegg'), u['kilde'])
    print(f"{len(maal)} hus med standardvegg, {sum(1 for u in ut if u['kilde'])} fikk farge, {sum(1 for u in ut if not u['kilde'])} uten kilde")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
