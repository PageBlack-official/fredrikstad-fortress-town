"""Regel: bryggene i kartet stemmer med ortofoto 2024 (Fredrikstad kommune; hent med verktoy/vann.py hent) innen kartrammen (±860 m).
- dekning: minst 95 % av bryggene som synes i ortofotoet (kilder/brygger-maalt.json «sett», ett punkt per brygge, notert ved
  gjennomgang av fotoet) finnes i kartet (punktet ligger i eller innen 1,5 m fra en tegnet brygge)
- ingen brygge står på land: minst halvparten av hver brygge ligger over vannet i kartet (data/vann.json; en fast brygge kan
  ha landfeste, men står ute i vannet)
- fotoet bekrefter hver brygge: minst 50 % av omrisset er noe annet enn mørkt, brunt vann i ortofotoet (bryggedekk, landgang,
  båt ved brygga); for utriggerne (tynne bommer) gjelder kravet snittet, ikke hver bom
- hver brygge har fast id (br-) i kilder/id-register.txt, gyldig type og høyde over vannet som passer typen
Merk: «sett» og håndmålingene er gjort av samme hånd i samme foto; at fasiten følger virkeligheten, vises av kontrollarkene
(rapport/brygger/<område>-<for|etter>.jpg, ikke i git, lag dem med python3 verktoy/brygger.py ark)."""
import os, sys
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import datalag
import brygger as B
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

KRAV_DEKNING, MAKS_AVSTAND, KRAV_VANN, KRAV_FOTO = 0.95, 1.5, 0.5, 0.5
feil, linjer = [], []
br = datalag.alle()['brygger']
reg = {l.strip() for l in open(os.path.join(ROT, 'kilder', 'id-register.txt'), encoding='utf8') if l.strip()}
ids = [b.get('id') for b in br]
if None in ids: feil.append(f"- {ids.count(None)} brygger uten id (kjør verktoy/brygger.py maal)")
if len(set(ids)) != len(ids): feil.append('- en brygge-id er brukt to ganger')
if sorted(i for i in reg if i.startswith('br-')) != sorted(i for i in ids if i):
    feil.append('- brygge-id-ene og id-registeret sier ikke det samme (en id slettes aldri, brygga skjules med grunn)')
synlig = [b for b in br if not b.get('skjul')]
for b in synlig:
    if b['typ'] not in B.HOYDE: feil.append(f"- {b['id']}: ukjent type {b['typ']}")
    elif abs(b['z'] - B.HOYDE[b['typ']]) > 0.3: feil.append(f"- {b['id']}: høyden {b['z']} m passer ikke en {b['typ']}")
    if len(b['p']) < 3: feil.append(f"- {b['id']}: mangler omriss")
P = {b['id']: Polygon(b['p']).buffer(0) for b in synlig}

# dekning mot det som synes i fotoet
sett = [s for s in B.maalt()['sett'] if abs(s[0]) <= B.RAMME and abs(s[1]) <= B.RAMME]
alle = unary_union(list(P.values()))
mangler = [s for s in sett if alle.distance(Point(s[0], s[1])) > MAKS_AVSTAND]
dekn = 1 - len(mangler) / max(len(sett), 1)
linjer.append(f"{len(sett) - len(mangler)} av {len(sett)} brygger i ortofotoet finnes i kartet ({dekn:.0%}, krav {KRAV_DEKNING:.0%}); "
              f"{len(synlig)} brygger tegnet")
if dekn < KRAV_DEKNING: feil.append(f"- for få av bryggene i fotoet er tegnet: {dekn:.0%}")
for s in mangler: linjer.append(f"  - mangler: {s[2]} ({s[0]}, {s[1]})")

# på vannet
vann = unary_union([Polygon(v['p'], [h for h in v['h'] if len(h) > 2]).buffer(0) for v in datalag.alle()['vann'] if not v.get('skjul') and len(v['p']) > 2])
paa_land = []
for i, pg in P.items():
    a = pg.intersection(vann).area / max(pg.area, 1e-6)
    if a < KRAV_VANN: paa_land.append((i, a))
linjer.append(f"{len(P) - len(paa_land)} av {len(P)} brygger står minst {KRAV_VANN:.0%} over vannet")
for i, a in paa_land: feil.append(f"- {i} står på land: bare {a:.0%} over vannet")

# fotoet bekrefter
tynne = [b for b in synlig if B.tynn(b['p'])]; flater_ = [b for b in synlig if not B.tynn(b['p'])]
andel = {b['id']: B.foto_andel(b['p']) for b in flater_}
svake = [(b['id'], andel[b['id']]) for b in flater_ if andel[b['id']] < KRAV_FOTO]
lys = {b['id']: B.foto_bom(b['p']) for b in tynne}
usett = [(i, v) for i, v in lys.items() if v < B.BOM_LYS]
ff = sorted(andel.values())
linjer.append(f"fotoet viser brygge (ikke vann) under {len(ff) - len(svake)} av {len(ff)} brygger (median {ff[len(ff) // 2]:.0%} av flaten); "
              f"{len(tynne) - len(usett)} av {len(tynne)} tynne bommer (utriggere under 0,6 m) synes som lys linje i fotoet (krav: alle)")
for i, a in svake: feil.append(f"- {i}: fotoet viser vann under {1 - a:.0%} av brygga")
for i, v in usett: feil.append(f"- {i}: bommen synes ikke i fotoet (lyshet {v:.1f}, krav {B.BOM_LYS})")

# per område og type
linjer += ['', '| område | fast | flytebrygge | utrigger | sett i fotoet |', '|---|---|---|---|---|']
for o in list(B.OMRAADER) + ['ellers']:
    n = {t: sum(1 for b in synlig if b['omraade'] == o and b['typ'] == t) for t in B.HOYDE}
    s = sum(1 for x in sett if B.omraade(x[0], x[1]) == o)
    if sum(n.values()) or s: linjer.append(f"| {o} | {n['fast']} | {n['flytebrygge']} | {n['utrigger']} | {s} |")
rapport('18_brygger', not feil, linjer + feil, 'rapport/brygger/<område>-<for|etter>.jpg (ikke i git; python3 verktoy/brygger.py ark)')
