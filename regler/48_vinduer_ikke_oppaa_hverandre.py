"""Regel 48 (PAG-1496, Vegars funn 09.11): ingen vinduer skal ligge oppå hverandre i bygg[].vind.

To vinduer «ligger oppå hverandre» når de står på samme vegg (normalene peker samme vei, dot > 0.9,
og sentrene er innenfor 0,6 m vinkelrett på veggen) og rektanglene deres overlapper mer enn 5 % av det
minste vinduets flate. Sjekken gjelder både per vegg i samme bygg og mellom to hus (samme fasade lest/
antatt to ganger havner som to lag). Rød = publisering stoppes (sperren i publiser.sh leser denne regelen).

Vindu-format: [x, y, z(høyde), tx, ty, nx, ny, w(bredde), h(høyde), typ, bue, ant]. Bredde w ligger langs
tangenten (tx,ty), høyde h langs loddlinja (z). Dataene leses slik kartet viser dem (datalag), ikke råfila.
"""
import math
from _felles import data, rapport

DOT_SAMME_VEGG = 0.9    # normalene må peke samme vei for å være «samme vegg»
VINKELRETT_M = 0.6      # sentrene innenfor 0,6 m vinkelrett på veggen
TERSKEL = 0.05          # overlapp over 5 % av minste vindu er feil
RUTE = 3.0              # romlig rutenett for å slippe O(n^2) (overlapp krever sentre nær hverandre)


def overlapp(a, b):
    """Overlappbrøk (av minste vindus flate) for to vinduer, eller 0 hvis de ikke er på samme vegg/ikke rører."""
    xa, ya, za, txa, tya, nxa, nya, wa, ha = a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]
    xb, yb, zb, nxb, nyb, wb, hb = b[0], b[1], b[2], b[5], b[6], b[7], b[8]
    if nxa * nxb + nya * nyb < DOT_SAMME_VEGG:   # ikke samme vegg (ulik retning)
        return 0.0
    dx, dy = xb - xa, yb - ya
    if abs(dx * nxa + dy * nya) > VINKELRETT_M:  # for langt fra hverandre vinkelrett på veggen
        return 0.0
    langs = dx * txa + dy * tya                  # b sitt senter langs veggen, relativt a
    ox = min(wa / 2, langs + wb / 2) - max(-wa / 2, langs - wb / 2)   # vannrett overlapp langs veggen
    oz = min(za + ha / 2, zb + hb / 2) - max(za - ha / 2, zb - hb / 2)  # loddrett overlapp
    if ox <= 0 or oz <= 0:
        return 0.0
    minflate = min(wa * ha, wb * hb)
    return (ox * oz) / minflate if minflate > 0 else 0.0


def ruter(vinduer):
    """byggindeks+vindu-liste -> rutenett {(cx,cy): [(bygg_i, vind_k, v)]}."""
    rute = {}
    for bi, vs in vinduer:
        for k, v in enumerate(vs):
            c = (math.floor(v[0] / RUTE), math.floor(v[1] / RUTE))
            rute.setdefault(c, []).append((bi, k, v))
    return rute


def main():
    bygg = data('bygg')
    # alle vinduer med byggindeks, hopp over skjulte bygg og bygg uten vind
    vinduer = [(i, b.get('vind') or []) for i, b in enumerate(bygg) if not b.get('skjul') and b.get('vind')]
    rute = ruter(vinduer)

    per_vegg = []   # (bygg-id, k1, k2, prosent)
    mellom = []     # (id1, id2, k1, k2, prosent)
    sett = set()
    naboer = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for (cx, cy), her in rute.items():
        kandidater = []
        for dx, dy in naboer:
            kandidater += rute.get((cx + dx, cy + dy), [])
        for bi, k, v in her:
            for bj, l, w in kandidater:
                if (bi, k) == (bj, l):
                    continue
                nøkkel = (min((bi, k), (bj, l)), max((bi, k), (bj, l)))
                if nøkkel in sett:
                    continue
                sett.add(nøkkel)
                f = overlapp(v, w)
                if f <= TERSKEL:
                    continue
                pros = round(f * 100, 1)
                if bi == bj:
                    per_vegg.append((bygg[bi]['id'], k, l, pros))
                else:
                    mellom.append((bygg[bi]['id'], bygg[bj]['id'], k, l, pros))

    ok = not per_vegg and not mellom
    linjer = []
    if ok:
        n = sum(len(vs) for _, vs in vinduer)
        linjer.append(f"0 overlapp over 5 % i {n} vinduer ({len(vinduer)} bygg)")
    else:
        linjer.append(f"{len(per_vegg)} par per vegg, {len(mellom)} par mellom hus, over 5 % overlapp")
        # grupper per bygg for lesbarhet, verste først
        from collections import defaultdict
        pv = defaultdict(list)
        for bid, k, l, p in per_vegg:
            pv[bid].append((p, k, l))
        for bid in sorted(pv, key=lambda b: -max(p for p, _, _ in pv[b])):
            par = sorted(pv[bid], reverse=True)
            linjer.append(f"- {bid}: {len(par)} par per vegg, verst {par[0][0]} % (vindu {par[0][1]} og {par[0][2]})")
        mh = defaultdict(list)
        for id1, id2, k, l, p in mellom:
            mh[tuple(sorted((id1, id2)))].append(p)
        for par in sorted(mh, key=lambda t: -max(mh[t])):
            ps = mh[par]
            linjer.append(f"- mellom {par[0]} og {par[1]}: {len(ps)} par, verst {max(ps)} %")

    return rapport('48_vinduer_ikke_oppaa_hverandre', ok, linjer)


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
