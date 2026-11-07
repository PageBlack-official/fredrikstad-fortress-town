#!/usr/bin/env python3
"""Fasader tegnet av fra rettede Street View-bilder (07.11, Vegar: «nesten alle byggene har feil plassert vinduer og dører»).

Metoden: fasadens fire hjørner leses i Street View-bildet (bunn/takfot, venstre/høyre), bildet rettes ut til et rett-forfra-bilde
av veggen med kjent lengde (kartets vegg) og høyde (husets takfot), og vinduer, dører og porter leses der i meter: avstand fra
venstre hjørne (s) og høyde over bakken (z). Ingen kameraposisjon inngår, så Googles posisjonsfeil (3–5 m) betyr ingenting.
Bare fasader som er godkjent etter å ha blitt sett side om side med Street View tas med.

Kilde: kilder/gate/rett-*.json, lister med {bilde, id, vegg, venstre:[x,y], hoyre:[x,y], lengde, h, godkjent, elementer:
[{type: vindu|dor|port|butikk|oksoye, s0, s1, z0, z1, bue?, farge?}]}. Kjøres sist i kjeden (etter gate_avlesning): vinduene på
den leste veggen byttes ut, de andre veggene står. Idempotent (egne linjer byttes ut).
    python3 verktoy/fasade_rett.py [--tørt]"""
import json, os, sys, glob
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vinduer_regler as VR, vegger as VG  # noqa: E402
import gate_avlesning as GA  # noqa: E402
GRUNN = 'Fasade fra rettet Street View-bilde (verktoy/fasade_rett.py)'
# port: src/07 tegner typ 2 alltid med rundbue; en rett port (garasjeport, dobbel tredør) tegnes som bred dør (typ 1).
# Bare port med «bue»: 1 blir typ 2 (08.11 natt: garasjeportene ble buede i modellen).
TYP = {'vindu': 0, 'butikk': 0, 'dor': 1, 'port': 2, 'oksoye': 3}

def main(tørt):
    kilder = []
    for f in sorted(glob.glob(os.path.join(ROT, 'kilder', 'gate', 'rett-*.json'))):
        kilder += [r for r in json.load(open(f, encoding='utf8')) if r.get('godkjent')]
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = {x['id']: x for x in d['bygg']}
    omg = VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])
    per_hus = {}
    for r in kilder: per_hus.setdefault(r['id'], []).append(r)
    nye, logg = [], []
    dato = __import__('datetime').date.today().isoformat()
    for id_, rr in per_hus.items():
        # hus med eget fasadeverktøy (datalag.EGNE_FASADER, f.eks. Kaserna) eies av det verktøyet (regel 37)
        if id_ in datalag.EGNE_FASADER: logg.append(f'{id_}: eget verktøy ({datalag.EGNE_FASADER[id_]}), hoppet over'); continue
        x = B.get(id_)
        if x is None: logg.append(f'{id_}: finnes ikke'); continue
        P = np.array(x['p'], float); V = VG.vegger(x, omg, slaa_sammen=True)
        lest = set(); ny = []
        for r in rr:
            a, c = np.array(r['venstre'], float), np.array(r['hoyre'], float); L = float(np.linalg.norm(c - a)); u = (c - a) / L
            w = V[r['vegg']]; n = np.array(w['n'], float); lest.add(r['vegg'])
            for e in r['elementer']:
                s0, s1, z0, z1 = (float(e[k]) for k in ('s0', 's1', 'z0', 'z1'))
                # det rettede bildet slutter ved takfoten, så karmen kan leses helt opp til den; datalag fjerner vinduer
                # som når over h - 0,1 (A13). Karmen kappes 0,15 m under takfoten (07.11: 2. etg forsvant på Kirkegata 26).
                z1 = min(z1, float(x['h']) - 0.15)
                if s1 - s0 < 0.25 or z1 - z0 < 0.25: continue
                el = VR.element(P, a + u * (s0 + s1) / 2, round(s1 - s0, 2), n, round((z0 + z1) / 2, 2), round(s1 - s0, 2), round(z1 - z0, 2), (2 if e['type'] == 'port' and e.get('bue') else TYP.get(e['type'], 0) if e['type'] != 'port' else 1))
                if e.get('bue'): el[10] = int(e['bue'])
                if e.get('farge'): el.append(e['farge'])
                ny.append(el)
        resten = [e for e in (x.get('vind') or []) if VG.naermeste_vegg(V, np.array(e[:2]))[0] not in lest]
        vind = GA.hjorne_inn(P, resten + ny)
        nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': 'vind', 'verdi': vind, 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
        # eget felt: fasade_kilde beskriver resten av huset (tegning/streetview/antatt) og styrer de andre verktøyene og regel 03
        nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': 'fasade_rett', 'verdi': sorted(lest), 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
        logg.append(f'{id_}: {len(ny)} elementer på {len(lest)} vegg(er), {len(resten)} på andre vegger')
    print('\n'.join(logg)); print(f'{len(per_hus)} hus med rettet fasade')
    if not tørt: datalag.skriv_rettelser(ret + nye)

if __name__ == '__main__':
    main('--tørt' in sys.argv)
