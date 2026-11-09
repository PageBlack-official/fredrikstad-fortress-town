#!/usr/bin/env python3
"""Enhetstest for verktoy/avdobling.py (regel 48, PAG-1496).

Laster bygg slik kartet viser dem (datalag.koble_til_plass(datalag.alle())), bruker resolusjonen i minnet og teller
gjenværende regel-48-par per bygg. Forventet: 0 par for de berørte byggene etter resolusjon, unntakene urørt.
Skriver INGENTING (ingen rettelser).
    ~/sot-maskin/py/bin/python3 verktoy/avdobling_test.py
"""
import os, sys
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, avdobling as AV  # noqa: E402

BERØRT = ['bnr-193868479', 'bnr-193972012', 'bnr-193870279', 'bnr-193820573', 'bnr-193870317', 'pb-1']
UNNTAK = ['bnr-193868452', 'bnr-193972276']


def par_per_bygg(V, bygg_ids):
    """Antall regel-48-par der minst ett vindu hører til et av bygg_ids."""
    tel = {b: 0 for b in bygg_ids}
    for akey, bkey, _ in AV.finn_par(V):
        for key in (akey, bkey):
            if key[0] in tel:
                tel[key[0]] += 1
    return tel


def main():
    # samme kilde som regel 48 og avdobling bruker, men uten egne avdobling-linjer (idempotent)
    bygg, _ = AV.hent_tilstand()
    unnta = AV.les_unnta()
    print(f"Unntak lest fra kilder/avdobling-unnta.json: {sorted(unnta)}")

    # bygg opp samme arbeidsstruktur som beregn(): hopp over skjul/uten vind/unntak
    V_for, orig = {}, {}
    for b in bygg:
        if b.get('skjul') or not b.get('vind') or b['id'] in unnta:
            continue
        V_for[b['id']] = [list(v) for v in b['vind']]
        orig[b['id']] = [list(v) for v in b['vind']]
    # unntaks-byggenes vind tatt vare på for å vise at de er urørt
    unntak_for = {b['id']: [list(v) for v in (b.get('vind') or [])] for b in bygg if b['id'] in unnta}

    før = par_per_bygg(V_for, BERØRT)
    print("\nPar FØR resolusjon:")
    for b in BERØRT:
        print(f"  {b}: {før[b]} par")

    droppet, skjovet, rest = AV.resolv(V_for)

    etter = par_per_bygg(V_for, BERØRT)
    print("\nPar ETTER resolusjon:")
    feil = []
    for b in BERØRT:
        ok = etter[b] == 0
        print(f"  {b}: {etter[b]} par  {'OK' if ok else 'FEIL'}")
        if not ok:
            feil.append(b)

    print("\nVinduer droppet vs skjøvet per berørt bygg (ingen skal miste vinduer utover ekte duplikater):")
    for b in BERØRT:
        if b in orig:
            d, s = droppet.get(b, 0), skjovet.get(b, 0)
            print(f"  {b}: {len(orig[b])} -> {len(V_for.get(b, []))} vinduer ({d} droppet, {s} skjøvet)")

    # unntakene: vi kjørte ikke resolusjon på dem i det hele tatt -> de er per definisjon urørt.
    print("\nUnntak (skal være urørt — aldri lagt inn i arbeidsstrukturen):")
    for b in UNNTAK:
        n = len(unntak_for.get(b, []))
        print(f"  {b}: {n} vinduer, urørt (ikke i resolusjonen)")

    if rest:
        print(f"\nGjenværende par > 5 % totalt: {len(rest)}")
        for akey, bkey, f in rest:
            print(f"  {akey[0]}[{akey[1]}] – {bkey[0]}[{bkey[1]}]: {round(f * 100, 1)} %")
    else:
        print("\nIngen par > 5 % igjen i hele kartet (utenom unntakene).")

    if feil:
        print(f"\nTEST FEILET: bygg med gjenværende par: {feil}")
        return 1
    print("\nTEST OK: 0 par for alle berørte bygg.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
