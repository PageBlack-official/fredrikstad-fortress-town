#!/usr/bin/env python3
"""Sluttkontroll for OPPGAVE4 (Vegars dom 09.11 kl. 14:58, runde 3).

`ferdig_sjekk.py` måler bare at feltene er FYLT, og ga exit 0 på et sett der bare 13 av 26 holdt.
Dette skriptet måler i stedet det som KAN TELLES i Vegars ord, mot det BYGDE datasettet
(`ut/server/data/by.json`, ikke `kilder/ferdig.json`). Hver sjekk siterer ordene den springer ut av,
så en som leser kan etterprøve at kravet er Vegars og ikke agentens.

    python3 verktoy/rett/dom_sjekk.py [sti-til-by.json]

Exit 0 bare når ALT holder:
  Del B tellbart:
    nr 1  (bnr-193867952, 10 Voldgaten): rekkefølgen i begge etasjer.
    nr 6  (bnr-193867855, Torvgaten 67): to vinduer nede og to vinduer i 2. etg.
    nr 7  (bnr-193867626, 26/27 Kirkegaten): taket skal ha to piper.
    nr 8  (bnr-193867634, Vollmesterboligen): 7 vinduer, 2 piper, 1 takvindu.
    nr 14 (bnr-13416419, 22 Bings gate): fire vinduer per rad, de to midterste doble, to rader.
  Del A uendret, byte for byte (mot verktoy/rett/del_a_frys.json): nr 2, 9, 12, 13.
"""
import json, os, sys
import numpy as np

ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROT)
sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import vegger as VG

VINDU, DOR, PORT, OKSOYE = 0, 1, 2, 3
TN = {VINDU: 'V', DOR: 'D', PORT: 'P', OKSOYE: 'O'}

sti = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROT, 'ut', 'server', 'data', 'by.json')
D = json.load(open(sti, encoding='utf8'))
BY = {b['id']: b for b in D['bygg']}
OMG = VG.Omgivelser(D['bygg'], D['veier'], D['gardsrom'])

feil = []            # liste av (hus, melding)
def krev(hus, ok, melding):
    if not ok:
        feil.append((hus, melding))
    return ok


def fasader(x):
    """Vinduer/dører/porter per vegg: {vegg_k: [(s, typ, sill_z, bredde), ...]} sortert s (venstre->høyre)."""
    V = VG.vegger(x, OMG, slaa_sammen=True)
    rad = {}
    for v in (x.get('vind') or []):
        k, _ = VG.naermeste_vegg(V, np.array(v[:2]))
        if k is None:
            continue
        s = float(np.dot(np.array(v[:2]) - V[k]['a'], V[k]['u']))
        rad.setdefault(k, []).append((s, int(v[9]), round(v[2] - v[8] / 2, 2), round(v[7], 2)))
    for k in rad:
        rad[k].sort()
    return V, rad


def hovedfasade(x):
    """Veggen Vegar leste fra gata: flest elementer, deretter lengst."""
    V, rad = fasader(x)
    if not rad:
        return []
    k = max(rad, key=lambda k: (len(rad[k]), V[k]['L']))
    return rad[k]


def etasjer(els):
    """Grupper elementene i etasjer etter sylleøyde; returner liste av rader (nederst først), hver sortert på s."""
    if not els:
        return []
    syller = sorted(set(round(e[2], 1) for e in els))
    grenser, forrige = [], None
    for z in syller:
        if forrige is not None and z - forrige > 1.0:       # ny etasje når syllen hopper mer enn 1 m
            grenser.append((forrige + z) / 2)
        forrige = z
    def etg(z):
        return sum(1 for g in grenser if z > g)
    rader = {}
    for e in els:
        rader.setdefault(etg(e[2]), []).append(e)
    return [sorted(rader[i]) for i in sorted(rader)]


def typer(rad):
    return [e[1] for e in rad]


def vinduer(rad):
    return [e for e in rad if e[1] == VINDU]


# ---------------------------------------------------------------- Del B (tellbart)

# Nr 1, bnr-193867952, 10 Voldgaten. Vegar:
#  «1 etg. ... to vinduer med sprosser helt til venstre, så dør, to vinduer med sprosser så dør,
#   ett vindue med sprosser, stor port.»  -> V V D V V D V P
#  «2 etg. ... tre vinduer med sprosser + tre vinduer med sprosser, så ett vindu og så et
#   dobbelvindu over port-døren.»          -> 8 vinduer (3+3+1+dobbel), ingen dør/port, dobbel = bredest, ytterst.
def sjekk_nr1():
    h = 'nr 1 (bnr-193867952)'
    x = BY.get('bnr-193867952')
    if not krev(h, x is not None, 'huset mangler i bygde data'):
        return
    rader = etasjer(hovedfasade(x))
    if not krev(h, len(rader) >= 2, f'fant ikke to etasjer på gatefasaden (fant {len(rader)})'):
        return
    ned, opp = rader[0], rader[1]
    krev(h, typer(ned) == [VINDU, VINDU, DOR, VINDU, VINDU, DOR, VINDU, PORT],
         '1. etg skal være V V D V V D V P (to vinduer, dør, to vinduer, dør, ett vindu, stor port), '
         f'er {"".join(TN[t] for t in typer(ned))}')
    vo = vinduer(opp)
    krev(h, len(vo) == 8 and all(e[1] == VINDU for e in opp),
         f'2. etg skal være 8 vinduer uten dør/port (3+3+1+dobbelvindu), er {"".join(TN[e[1]] for e in opp)}')
    if len(vo) == 8:
        bredder = [e[3] for e in vo]
        krev(h, vo[-1][3] == max(bredder) and vo[-1][3] >= 1.5 * np.median(bredder[:-1]),
             'det ytterste vinduet i 2. etg skal være et dobbelvindu (bredest, over port-døren)')


# Nr 6, bnr-193867855, Torvgaten 67. Vegar:
#  «Det hvite huset har to vinduer nede og to vinduer i 2 etg. ... Den røde porten er riktig plassert.»
def sjekk_nr6():
    h = 'nr 6 (bnr-193867855)'
    x = BY.get('bnr-193867855')
    if not krev(h, x is not None, 'huset mangler i bygde data'):
        return
    rader = etasjer(hovedfasade(x))
    if not krev(h, len(rader) >= 2, f'fant ikke to etasjer på gatefasaden (fant {len(rader)})'):
        return
    ned, opp = len(vinduer(rader[0])), len(vinduer(rader[1]))
    krev(h, ned == 2 and opp == 2, f'skal være to vinduer nede og to vinduer i 2. etg, er {ned} nede / {opp} oppe')
    porter = sum(1 for v in (x.get('vind') or []) if int(v[9]) == PORT)
    krev(h, porter >= 1, 'den røde porten skal stå (Vegar: «riktig plassert»)')


# Nr 7, bnr-193867626, 26/27 Kirkegaten. Vegar: «Taket skal ha to piper»
def sjekk_nr7():
    h = 'nr 7 (bnr-193867626)'
    x = BY.get('bnr-193867626')
    if not krev(h, x is not None, 'huset mangler i bygde data'):
        return
    n = len(x.get('piper') or [])
    krev(h, n == 2, f'taket skal ha to piper, har {n}')


# Nr 8, bnr-193867634, Vollmesterboligen, 5 Voldgaten. Vegar:
#  «Det skal være 7 vinduer på og to piper på det bygget, og et takvindu på kortveggen.»
def sjekk_nr8():
    h = 'nr 8 (bnr-193867634)'
    x = BY.get('bnr-193867634')
    if not krev(h, x is not None, 'huset mangler i bygde data'):
        return
    vind = len(vinduer(hovedfasade(x)))
    krev(h, vind == 7, f'det skal være 7 vinduer på langfasaden, er {vind}')
    piper = len(x.get('piper') or [])
    krev(h, piper == 2, f'det skal være to piper, er {piper}')
    tv = len(x.get('takvinduer') or [])
    krev(h, tv == 1, f'det skal være ett takvindu på kortveggen, er {tv}')


# Nr 14, bnr-13416419, 22 Bings gate. Vegar:
#  «bildet viser fire vinduer med sprosser der vinduene i midten oppe og nede er dobbelvinduer»
#  + huset skal ha to etasjer slik bildet viser.
def sjekk_nr14():
    h = 'nr 14 (bnr-13416419)'
    x = BY.get('bnr-13416419')
    if not krev(h, x is not None, 'huset mangler i bygde data'):
        return
    rader = etasjer(hovedfasade(x))
    if not krev(h, len(rader) >= 2, f'huset skal ha to etasjer (to vindusrekker), fant {len(rader)}'):
        return
    for navn, rad in (('nederst', rader[0]), ('øverst', rader[1])):
        vs = vinduer(rad)
        if not krev(h, len(vs) == 4, f'{navn} rad skal ha fire vinduer, har {len(vs)}'):
            continue
        b = [e[3] for e in vs]                       # sortert på s (venstre->høyre)
        midt, kant = (b[1] + b[2]) / 2, (b[0] + b[3]) / 2
        krev(h, midt > kant * 1.3,
             f'{navn}: de to midterste vinduene skal være dobbelvinduer (bredere enn ytterkantene), '
             f'bredder {b}')


# ---------------------------------------------------------------- Del A (uendret, byte for byte)
# Vegar: nr 2, 9, 12, 13 er «Korrekt» og skal ikke røres.
def sjekk_del_a():
    frys = json.load(open(os.path.join(ROT, 'verktoy', 'rett', 'del_a_frys.json'), encoding='utf8'))
    for i, ref in frys.items():
        na = json.dumps(BY.get(i), ensure_ascii=False, sort_keys=True)
        nb = json.dumps(ref, ensure_ascii=False, sort_keys=True)
        krev('Del A ' + i, na == nb, 'huset er endret – Del A skal stå byte for byte urørt')


for fn in (sjekk_nr1, sjekk_nr6, sjekk_nr7, sjekk_nr8, sjekk_nr14, sjekk_del_a):
    fn()

if feil:
    print(f'DOM IKKE OPPFYLT — {len(feil)} avvik:')
    for hus, m in feil:
        print(f'  ✗ {hus}: {m}')
    sys.exit(1)
print('DOM OPPFYLT — alle tellbare krav i Vegars ord holder, Del A urørt.')
sys.exit(0)
