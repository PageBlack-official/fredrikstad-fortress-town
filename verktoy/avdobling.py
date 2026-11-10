#!/usr/bin/env python3
"""Vinduer som ligger oppå hverandre skyves fra hverandre, ekte duplikater droppes (regel 48, PAG-1496, 09.11).

Samme fasade lest/antatt to ganger havner som to lag vinduer oppå hverandre (regel 48). Dette steget rydder opp:
to vinduer «ligger oppå hverandre» med NØYAKTIG samme definisjon som regel 48 sin overlapp(a,b) (samme vegg: normalene
dot > 0.9 og sentrene innenfor 0,6 m vinkelrett; overlappbrøk = vannrett × loddrett / minste vindus flate; feil over 5 %).
Gjelder både per vegg i samme bygg og mellom to hus.

Resolusjon for et par (A,B) over 5 %:
  - along = (B.xy − A.xy)·(A.tx,A.ty); ox = (A.w/2+B.w/2) − |along|; oz = (A.h/2+B.h/2) − |B.z−A.z|.
  - Ekte duplikat (brøk ≥ 0.60 ELLER (|along|<0.25 og |B.z−A.z|<0.25)): DROPP den ene. Innad i samme bygg: den med
    høyest indeks. Mellom to hus: vinduet fra bygget hvis id sorterer sist leksikografisk. (A er alltid den med minst
    (id, indeks), B den største, så B droppes i begge tilfellene.)
  - Ellers KRYMP begge likt, sentrene står: ox ≤ oz → begge bredder −(ox+0.08); ellers → begge høyder −(oz+0.08).
    Sentrene flyttes ikke, så rytmen (regel 17), hjørneklaringen (regel 04) og «ingen blanke vegger» (regel 44) holder.
    Krymper et vindu smalere/lavere enn 0,4 m, droppes det i stedet. (Tidligere skjøv vi vinduene; det brøt 04/17/44.)
  - Opptil 6 pass over alle par til ingen par > 5 % igjen.

Bygg i kilder/avdobling-unnta.json hoppes HELT over (verken dropp eller skyv) — de re-leses fra Street View i stedet.

Vindu-format: [x, y, z(høyde), tx, ty, nx, ny, w(bredde), h(høyde), typ, bue, ant]. Dataene leses slik kartet viser dem
(datalag.koble_til_plass(datalag.alle())), ikke råfila; sett-rettelsen inneholder den rettede vind-arrayen. Idempotent
(egne linjer fjernes før det regnes på nytt). Står SIST i kjeden (etter fasade_rett.py).
    python3 verktoy/avdobling.py [--tørt]
"""
import json, math, os, sys, collections

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag  # noqa: E402

GRUNN = 'avdobling: vinduer som lå oppå hverandre skjøvet fra hverandre (verktoy/avdobling.py, PAG-1496)'
DATO = '2026-11-09'

# NØYAKTIG samme som regler/48_vinduer_ikke_oppaa_hverandre.py
DOT_SAMME_VEGG = 0.9    # normalene må peke samme vei for å være «samme vegg»
VINKELRETT_M = 0.6      # sentrene innenfor 0,6 m vinkelrett på veggen
TERSKEL = 0.05          # overlapp over 5 % av minste vindu er feil
RUTE = 3.0              # romlig rutenett for å slippe O(n^2)
DUP = 0.60              # brøk ≥ 60 % (eller nær-identiske sentre) = ekte duplikat, droppes
LUFT = 0.08             # luft mellom vinduer etter krymp
MIN_EL = 0.4            # krymper et vindu smalere/lavere enn dette, dropp det i stedet
MAKS_PASS = 6


def overlapp(a, b):
    """Overlappbrøk (av minste vindus flate), eller 0 hvis de ikke er på samme vegg/ikke rører. Kopi av regel 48."""
    xa, ya, za, txa, tya, nxa, nya, wa, ha = a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]
    xb, yb, zb, nxb, nyb, wb, hb = b[0], b[1], b[2], b[5], b[6], b[7], b[8]
    if nxa * nxb + nya * nyb < DOT_SAMME_VEGG:
        return 0.0
    dx, dy = xb - xa, yb - ya
    if abs(dx * nxa + dy * nya) > VINKELRETT_M:
        return 0.0
    langs = dx * txa + dy * tya
    ox = min(wa / 2, langs + wb / 2) - max(-wa / 2, langs - wb / 2)
    oz = min(za + ha / 2, zb + hb / 2) - max(za - ha / 2, zb - hb / 2)
    if ox <= 0 or oz <= 0:
        return 0.0
    minflate = min(wa * ha, wb * hb)
    return (ox * oz) / minflate if minflate > 0 else 0.0


def finn_par(V):
    """Alle par (akey, bkey, brøk) over terskel, med akey = min((id,indeks), ...). V = {bygg_id: [vind …]}."""
    rute = {}
    for bid, vs in V.items():
        for k, v in enumerate(vs):
            c = (math.floor(v[0] / RUTE), math.floor(v[1] / RUTE))
            rute.setdefault(c, []).append((bid, k, v))
    naboer = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    par, sett = [], set()
    for (cx, cy), her in rute.items():
        kand = []
        for dx, dy in naboer:
            kand += rute.get((cx + dx, cy + dy), [])
        for bi, k, v in her:
            for bj, l, w in kand:
                if (bi, k) == (bj, l):
                    continue
                nøkkel = (min((bi, k), (bj, l)), max((bi, k), (bj, l)))
                if nøkkel in sett:
                    continue
                sett.add(nøkkel)
                # overlapp bruker a sin tangent; regn med akey (kanonisk minste) som a, slik resolusjonen definerer A
                akey, bkey = nøkkel
                f = overlapp(V[akey[0]][akey[1]], V[bkey[0]][bkey[1]])
                if f > TERSKEL:
                    par.append((akey, bkey, f))
    return par


def resolv(V, maks=MAKS_PASS):
    """Skyv/dropp til ingen par > 5 % (eller maks pass). Returnerer (droppet_per_bygg, skjovet_per_bygg, restpar)."""
    droppet = collections.Counter()
    skjovet = collections.Counter()
    for _ in range(maks):
        par = sorted(finn_par(V), key=lambda p: (p[0], p[1]))
        if not par:
            break
        rørt, dropp = set(), set()   # endepunkter rørt dette passet; (id,indeks) som skal slettes
        for akey, bkey, f in par:
            if akey in rørt or bkey in rørt or akey in dropp or bkey in dropp:
                continue   # vent til neste pass så vi ikke dobbelt-flytter samme vindu
            A = V[akey[0]][akey[1]]
            B = V[bkey[0]][bkey[1]]
            along = (B[0] - A[0]) * A[3] + (B[1] - A[1]) * A[4]
            ox = (A[7] / 2 + B[7] / 2) - abs(along)
            oz = (A[8] / 2 + B[8] / 2) - abs(B[2] - A[2])
            if f >= DUP or (abs(along) < 0.25 and abs(B[2] - A[2]) < 0.25):
                # ekte duplikat: dropp B (= høyest indeks i samme bygg / id som sorterer sist mellom hus)
                dropp.add(bkey)
                droppet[bkey[0]] += 1
            elif ox <= oz:
                # delvis overlapp vannrett: krymp BEGGE bredder likt, sentrene står (ingen rytme-/hjørne-/blank-brudd).
                # Hvert vindu −(ox+LUFT) gir luft LUFT mellom dem. Blir noe for smalt, dropp B i stedet.
                d = ox + LUFT
                if min(A[7], B[7]) - d < MIN_EL:
                    dropp.add(bkey); droppet[bkey[0]] += 1
                else:
                    A[7] = round(A[7] - d, 3); B[7] = round(B[7] - d, 3)
                    skjovet[akey[0]] += 1; skjovet[bkey[0]] += 1
            else:
                # delvis overlapp loddrett: krymp BEGGE høyder likt, z-sentrene står
                d = oz + LUFT
                if min(A[8], B[8]) - d < MIN_EL:
                    dropp.add(bkey); droppet[bkey[0]] += 1
                else:
                    A[8] = round(A[8] - d, 3); B[8] = round(B[8] - d, 3)
                    skjovet[akey[0]] += 1; skjovet[bkey[0]] += 1
            rørt.add(akey)
            rørt.add(bkey)
        for bid, idx in sorted(dropp, key=lambda t: (t[0], -t[1])):
            del V[bid][idx]   # synkende indeks per bygg, så indeksene holder
    return droppet, skjovet, finn_par(V)


def hent_tilstand():
    """Bygg slik kartet viser dem, UTEN våre egne linjer (idempotent), i minnet — skriver ingenting."""
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True)
    grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    d = datalag.koble_til_plass(d)
    return d['bygg'], ret


def les_unnta():
    p = os.path.join(ROT, 'kilder', 'avdobling-unnta.json')
    if not os.path.exists(p):
        return set()
    o = json.load(open(p, encoding='utf8'))
    if isinstance(o, list):
        return set(o)
    if isinstance(o, dict):
        for k in ('ids', 'id', 'bygg'):
            if isinstance(o.get(k), list):
                return set(o[k])
        for v in o.values():   # første liste-verdi
            if isinstance(v, list):
                return set(v)
    return set()


def beregn(bygg, unnta):
    """Finn og rydd overlapp. Returnerer (nye {id: rettet_vind}, logg, restpar)."""
    V, orig = {}, {}
    for b in bygg:
        if b.get('skjul') or not b.get('vind') or b['id'] in unnta:
            continue
        V[b['id']] = [list(v) for v in b['vind']]
        orig[b['id']] = [list(v) for v in b['vind']]
    droppet, skjovet, rest = resolv(V)
    nye, logg = {}, []
    for bid in sorted(V):
        if V[bid] != orig[bid]:
            nye[bid] = V[bid]
            logg.append((bid, len(orig[bid]), len(V[bid]), droppet[bid], skjovet[bid]))
    return nye, logg, rest


def main(tørt=False):
    bygg, ret = hent_tilstand()
    unnta = les_unnta()
    nye, logg, rest = beregn(bygg, unnta)
    for bid, f0, f1, d, s in logg:
        print(f"{bid}: {f0} -> {f1} vinduer ({d} droppet, {s} skjøvet)")
    n_drop = sum(l[3] for l in logg)
    n_skyv = sum(l[4] for l in logg)
    print(f"{len(logg)} bygg ryddet: {n_drop} vinduer droppet (ekte duplikater), {n_skyv} skjøvet. "
          f"Unntak hoppet over: {', '.join(sorted(unnta)) or 'ingen'}")
    if rest:
        print(f"ADVARSEL: {len(rest)} par > 5 % gjenstår etter {MAKS_PASS} pass:")
        for akey, bkey, f in rest:
            print(f"  {akey[0]}[{akey[1]}] – {bkey[0]}[{bkey[1]}]: {round(f * 100, 1)} %")
    if not tørt:
        ret += [{'emne': 'bygg', 'id': i, 'op': 'sett', 'felt': 'vind', 'verdi': v,
                 'hvem': 'Claude', 'dato': DATO, 'grunn': GRUNN} for i, v in sorted(nye.items())]
        datalag.skriv_rettelser(ret)


if __name__ == '__main__':
    main('--tørt' in sys.argv)
