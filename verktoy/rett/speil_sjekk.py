#!/usr/bin/env python3
"""Fanger speilvendte fasader (RUNDE3E, 14.11). s leses fra bildets venstre (veggen sett forfra fra utsiden), men
hvis venstre/hoyre i en rett-*.json står i motsatt rekkefølge av det kameraet så, la fasade_rett elementene speilvendt
langs veggen (Majoren bnr-193868622 v2: render viste port-butikk-dør-vindu der SV viser vindu-dør-butikk-port).

Hard sjekk (exit 1 ved brudd) mot FASIT fra Street View, lest ut av det BYGDE modellen (kjør etter bygg_kjede):
  ANKER: Majoren-porten er helt til høyre i SV (portrom til høyre, s8,5-11,8 av 12,2 m). Da MÅ porten (typ 2) i
  byggets vind ligge på utsidens høyre halvdel av vegg 2. Står den til venstre, er fasaden speilvendt.

I tillegg en opplysende skanning: hvilke godkjente rett-vegger er forfra-vendt bakvendt i rådataene (venstre/hoyre
byttet), dvs. (n × u)_z < 0 for u = (hoyre - venstre). Disse er avhengige av at fasade_rett normaliserer retningen.

    python3 verktoy/rett/speil_sjekk.py
"""
import json, os, sys, glob
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG  # noqa: E402

MAJOREN, MAJ_VEGG = 'bnr-193868622', 2


def _modell():
    raa = datalag.alle(raa=True)
    ret = list(datalag.les('rettelser'))
    grunn = [dict(x) for x in raa['bygg']]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    B = {x['id']: x for x in d['bygg']}
    return B, VG.Omgivelser(d['bygg'], d['veier'], d['gardsrom'])


def main():
    B, omg = _modell()
    feil = []

    # opplysende: rådata-retning per godkjent vegg (fasade_rett snur disse ved (n x u)_z < 0)
    bakvendt = []
    for f in sorted(glob.glob(os.path.join(ROT, 'kilder', 'gate', 'rett-*.json'))):
        for r in json.load(open(f, encoding='utf8')):
            if not r.get('godkjent'):
                continue
            x = B.get(r['id'])
            if x is None:
                continue
            V = VG.vegger(x, omg, slaa_sammen=True)
            if r['vegg'] >= len(V):
                continue
            n = np.array(V[r['vegg']]['n'], float)
            u = np.array(r['hoyre'], float) - np.array(r['venstre'], float)
            if n[0] * u[1] - n[1] * u[0] < 0:
                bakvendt.append(f'{os.path.basename(f)} {r["id"]} v{r["vegg"]}')

    # ANKER mot fasit: Majoren-porten på utsidens høyre halvdel av vegg 2 i det bygde modellen
    x = B.get(MAJOREN)
    if x is None:
        feil.append(f'{MAJOREN} finnes ikke i modellen')
    else:
        V = VG.vegger(x, omg, slaa_sammen=True)
        w = V[MAJ_VEGG]; n = np.array(w['n'], float)
        hoyre_akse = np.array([-n[1], n[0]])           # skjerm-x vokser mot utsidens høyre
        a, c = np.array(w['a'], float), np.array(w['c'], float)
        midt = float(((a + c) / 2) @ hoyre_akse)
        def paa_veggen(e):
            return VG.naermeste_vegg(V, np.array(e[:2]))[0] == MAJ_VEGG
        # porten er den bredeste åpningen (dør/port, typ 1/2) nede på veggen; den flate Majoren-porten er typ 1 (ingen bue)
        aapninger = [e for e in (x.get('vind') or []) if len(e) > 9 and int(e[9]) in (1, 2) and e[2] < 2.5 and paa_veggen(e)]
        if not aapninger:
            feil.append('Majoren: ingen dør/port på vegg 2 i byggets vind')
        else:
            port = max(aapninger, key=lambda e: e[7])     # bredeste = portrommet
            px = float(np.array(port[:2]) @ hoyre_akse)
            if px <= midt:
                feil.append(f'Majoren: portrommet (b={port[7]} m) ligger på utsidens VENSTRE halvdel av vegg 2 '
                            f'(skjerm-x {px:.2f} <= midt {midt:.2f}) — fasaden er speilvendt mot Street View (port skal være til høyre)')

    if bakvendt:
        print('Rett-vegger forfra-bakvendt i rådata (normaliseres av fasade_rett):')
        for m in bakvendt:
            print('  ~', m)
    if feil:
        print('SPEILVENDT FASADE:')
        for m in feil:
            print('  -', m)
        sys.exit(1)
    print(f'OK: Majoren-porten står på utsidens høyre halvdel (fasit), {len(bakvendt)} vegger normalisert av fasade_rett')


if __name__ == '__main__':
    main()
