"""Vinduer og dører på de antatte husene, etter reglene Gamlebyens hus følger i Vegars kvartaltegninger.
Tallene er målt på fasit-husene (rapport/vinduer/mal_tegningene.py -> maalinger.json, forklart i regler-fra-tegningene.md).
Resultatet legges som rettelser (felt vind) i data/rettelser.json; hus med fasit fra tegningene (fasade_kilde kvartaltegning
eller v33-rettelse) røres ikke. Idempotent: egne rettelser fra en tidligere kjøring tas ut først.

    python3 verktoy/vinduer_regler.py          lager rettelsene
    python3 verktoy/vinduer_regler.py --tørt   viser bare hva som ville blitt gjort

Reglene (tall fra 121 fasit-hus, 2518 vinduer, 121 dører):
  vindu       0,85 x 1,4 m (68 % av vinduene), brystning 0,9 m, etasjehøyde 3,0 m (brystning 0,9 / 3,9 / 6,9)
  etasjer     alle rader der overkanten står minst 0,3 m under gesims (h): høyden styrer (82 % av fasit følger formelen)
  akser       vinduene står i akser med lik avstand, mål 2,8 m senter-senter (median 2,82, kvartiler 2,71–3,01),
              første og siste akse 0,85 m fra hjørnet (56 % av veggene; median), symmetrisk om veggens midtakse
  loddrett    samme akser i alle etasjer (72 % i fasit)
  korte vegger under 3 m: ingen vinduer (fasit: 1 % under 2 m, 23 % 2–3 m, 79 % 3–4 m); 3–4,5 m: ett vindu midt på
  felles vegg nabohus inntil (0,6 m): ingen vinduer (fasit: 4 %)
  dør         1,05 x 2,2 m fra bakken, på gatesiden (84 % av fasitdørene står mot gate), i aksen nærmest midten (68 %);
              døra tar vinduets plass i 1. etasje, vinduene over står. Uthus/garasjer: ingen dør (fasit: 13 %)."""
import json, math, os, sys
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG

GRUNN = 'regler fra kvartaltegningene (27.10)'
DATO = '2026-10-27'
UTHUS = {'garage', 'garages', 'shed'}
R = dict(vb=0.85, vh=1.4, bryst=0.9, etasje=3.0, gesims=0.3, cc=2.8, cc_min=2.4, cc_maks=3.4, kant=0.85,
         kort=3.0, ett_vindu=4.5, db=1.05, dh=2.2, hjorne_klaring=0.3)


def er_fasit(x, v33):
    return x.get('fasade_kilde') == 'kvartaltegning' or x['id'] in v33


def rader(h):
    """Brystningshøyder for etasjene som får plass under gesims."""
    ut, k = [], 0
    while R['bryst'] + R['etasje'] * k + R['vh'] <= h - R['gesims']:
        ut.append(R['bryst'] + R['etasje'] * k); k += 1
    return ut


def akser(L, odde=False):
    """Aksene (avstand fra start) på en fri strekning L: lik avstand nær 2,8 m, 0,85 m fra endene, symmetrisk.
    odde=True (veggen med dør): oddetall akser når det går med avstand 2,2–3,6 m, så døra får midtaksen."""
    if L < R['kort']:
        return []
    if L < R['ett_vindu'] or L - 2 * R['kant'] < R['cc_min']:
        return [L / 2]
    spenn = L - 2 * R['kant']
    def beste(lo, hi, bare_odde):
        kand = [(abs(spenn / (n - 1) - R['cc']), n) for n in range(2, int(spenn / lo) + 2)
                if lo - 1e-9 <= spenn / (n - 1) <= hi + 1e-9 and (not bare_odde or n % 2 == 1)]
        return min(kand)[1] if kand else None
    n = (beste(R['cc_min'] - 0.2, R['cc_maks'] + 0.2, True) if odde else None) or beste(R['cc_min'], R['cc_maks'], False) \
        or max(2, round(spenn / R['cc']) + 1)
    return [R['kant'] + i * spenn / (n - 1) for i in range(n)]


def doraksen(ts, t0, t1):
    """Døra står i aksen nærmest midten. Er det partall akser, står den midt mellom de to midterste (vinduene på
    hver side står da i rytmen) når det er minst 0,4 m luft til vinduene; ellers tar den den midterste aksen."""
    m = (t0 + t1) / 2
    if len(ts) % 2 == 0 and len(ts) >= 2:
        a, b = ts[len(ts) // 2 - 1], ts[len(ts) // 2]
        if b - a - R['vb'] - R['db'] >= 0.8:
            return (a + b) / 2, True
    return min(ts, key=lambda t: abs(t - m)), False


def hjorne_ok(P, q, w):
    """Samme mål som regel 04: halv bredde + 0,3 m til nærmeste hjørne langs kanten vinduet står på."""
    best = None; n = len(P)
    for k in range(n):
        a, c = P[k], P[(k + 1) % n]; u = c - a; L = np.linalg.norm(u)
        if L < 1e-9: continue
        u = u / L; t = float((q - a) @ u); d = abs(float((q - a)[0] * u[1] - (q - a)[1] * u[0]))
        if 0 <= t <= L and (best is None or d < best[0]): best = (d, t, L)
    return not (best and best[0] < 1.0 and min(best[1], best[2] - best[1]) < w / 2 + R['hjorne_klaring'] + 0.02)


def paa_veggen(P, q):
    """Punktet på husets omriss nærmest q, og kantens retning der (vinduet legges på den faktiske kanten)."""
    best = None; n = len(P)
    for k in range(n):
        a, c = P[k], P[(k + 1) % n]; u = c - a; L = np.linalg.norm(u)
        if L < 1e-9: continue
        u = u / L; t = min(max(float((q - a) @ u), 0), L); p = a + u * t; d = float(np.linalg.norm(q - p))
        if best is None or d < best[0]: best = (d, p, u)
    return best[1], best[2]


def element(P, sentrum, w, nvec, z, b, h, typ):
    p, u = paa_veggen(P, sentrum)
    if float(np.array([-u[1], u[0]]) @ nvec) < 0: u = -u      # n = (-ty, tx): høyrehendt basis i src/07
    nx, ny = -u[1], u[0]
    return [round(float(p[0]), 2), round(float(p[1]), 2), round(z, 2), round(float(u[0]), 4), round(float(u[1]), 4),
            round(float(nx), 4), round(float(ny), 4), b, h, typ, 0, 1]


def lag_vind(x, omg):
    """vind for ett antatt hus. Gir (vind, notat)."""
    P = np.array(x['p'], float); h = x['h']
    V = VG.vegger(x, omg, slaa_sammen=True); gi, hvordan = VG.gatesiden(V)
    bryst = rader(h); uthus = x.get('type') in UTHUS
    dor_mulig = not uthus and h >= R['dh'] + R['gesims'] and gi is not None
    ut = []; dor_satt = False
    for i, w in enumerate(V):
        if w['felles'] >= 0.5:
            continue
        # aksene legges på hele veggen, så rytmen holder også der et nabohus står inntil et stykke; akser som havner
        # mot nabohuset (bredde/2 + 0,3 m) utelates
        def ledig(t, b):
            return any(f0 <= t - b / 2 - 0.3 and t + b / 2 + 0.3 <= f1 for f0, f1 in w['fri'])
        med_dor = i == gi and dor_mulig
        ts = akser(w['L'], odde=med_dor)
        if not ts: continue
        midt, mellom = doraksen(ts, 0, w['L']) if med_dor else (None, False)
        if midt is not None and not ledig(midt, R['db']):
            frie = [t for t in ts if ledig(t, R['db'])]
            midt, mellom = (min(frie, key=lambda t: abs(t - w['L'] / 2)), False) if frie else (None, False)
        if mellom: ts = sorted(ts + [midt])     # egen dørakse midt mellom to vindusakser; ingen vinduer over den
        # aksen må holde hjørneklaring (regel 04) for det bredeste elementet den skal bære
        ok = [t for t in ts if ledig(t, R['db'] if t == midt else R['vb'])
              and hjorne_ok(P, w['a'] + w['u'] * t, R['db'] if t == midt else R['vb'])]
        if midt is not None and midt not in ok: midt = None
        for t in ok:
            q = w['a'] + w['u'] * t
            if t == midt:
                ut.append(element(P, q, R['db'], w['n'], R['dh'] / 2, R['db'], R['dh'], 1)); dor_satt = True
            for k, bz in enumerate(bryst):
                if t == midt and (k == 0 or mellom): continue
                ut.append(element(P, q, R['vb'], w['n'], bz + R['vh'] / 2, R['vb'], R['vh'], 0))
    return ut, dict(gate=hvordan, etasjer=len(bryst), dor=dor_satt, uthus=uthus)


def main(tørt=False):
    ret = datalag.les('rettelser')
    ret = [r for r in ret if not (r['emne'] == 'bygg' and r.get('felt') == 'vind' and r.get('grunn') == GRUNN)]
    v33 = {r['id'] for r in ret if r['op'] == 'sett' and r.get('felt') == 'vind' and r.get('grunn', '').startswith('v33')}
    d = datalag.alle(raa=True); grunn = [dict(x) for x in d['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(d, ret), grunn)    # slik kartet viser husene uten disse rettelsene
    b = d['bygg']; omg = VG.Omgivelser(b, d['veier'], d['gardsrom'])
    nye, logg = [], []
    for x in b:
        if not x.get('gml') or x.get('skjul') or x.get('kirke') or x.get('deler') or er_fasit(x, v33) or x.get('fasade_kilde') != 'antatt':
            continue
        vind, notat = lag_vind(x, omg)
        nye.append({"emne": "bygg", "id": x['id'], "op": "sett", "felt": "vind", "verdi": vind, "hvem": "Claude", "dato": DATO, "grunn": GRUNN})
        logg.append(dict(id=x['id'], navn=x.get('navn'), type=x.get('type'), h=x['h'], foer=len(x.get('vind') or []),
                         etter=len(vind), vinduer=sum(v[9] == 0 for v in vind), dorer=sum(v[9] == 1 for v in vind), **notat))
    json.dump(logg, open(os.path.join(ROT, 'rapport', 'vinduer', 'kjoring.json'), 'w'), ensure_ascii=False, indent=0)
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
    print(f"{len(nye)} antatte hus fikk vind etter reglene: {sum(l['vinduer'] for l in logg)} vinduer, {sum(l['dorer'] for l in logg)} dører "
          f"(før: {sum(l['foer'] for l in logg)} elementer); {sum(1 for l in logg if not l['etter'])} uten noe (lave eller inneklemte)")
    return logg


if __name__ == '__main__':
    main('--tørt' in sys.argv)
