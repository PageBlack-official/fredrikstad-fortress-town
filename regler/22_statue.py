"""Regel: statuen på Torvet er tegnet etter kildene, ikke gjettet.
- data/statue.json har navn, billedhugger, år, materiale, plass, retning, figurhøyde, sokkelledd og kilde-URL-er
- retningen står vinkelrett på gatenettet (data/gatevinkel.json) innen ±5°: sokkelen står parallelt med husene rundt torget,
  slik ortofotoet og alle fotoene viser
- plassen står på åpen grunn (ikke i et hus, minst 4 m til nærmeste husvegg) og innen 1,5 m fra sokkelens midtpunkt målt i ortofoto 2024
- total høyde (sokkel + figur) innen 4,2–5,2 m: skyggen i ortofotoet (5,6 m lang mot nord-nordvest) og solhøyden gir ca. 4,7 m
- tegnekoden (src/20_statuen-paa-torvet.js) leser mål, retning og plass fra dataene
Bevis: rapport/torvet/statue.png (python3 verktoy/statue_ark.py) og rapport/torvet/statue-i-kartet.png."""
import os, re
from _felles import *
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

ORTOFOTO_MIDT = (15.3, 41.5)        # sokkelens midtpunkt lest i ortofoto 2024 (0,125 m/px), 29.10
HOYDE_SKYGGE = (4.2, 5.2)
feil, linjer = [], []
S = data('statue'); bygg = data('bygg')
gv = float(open(os.path.join(ROT, 'data', 'gatevinkel.json')).read().strip())
hus = unary_union([Polygon(b['p']).buffer(0) for b in bygg if not b.get('skjul') and len(b['p']) >= 3])
for st in S:
    n = st.get('navn', '?')
    for felt in ('navn', 'billedhugger', 'avduket', 'materiale', 'xy', 'retning', 'figur', 'sokkel', 'kilder'):
        if not st.get(felt): feil.append(f"- {n}: mangler {felt}")
    if not all(str(k).startswith(('http', 'kilder/')) for k in st.get('kilder', [])): feil.append(f"- {n}: kilde som ikke er URL eller kildefil")
    avvik = ((st.get('retning', 0) - (90 - gv)) + 45) % 90 - 45
    if abs(avvik) > 5: feil.append(f"- {n}: retningen {st.get('retning')}° står {avvik:+.0f}° på skrå mot gatenettet ({gv}°)")
    pt = Point(*st['xy'])
    if hus.contains(pt) or hus.distance(pt) < 4: feil.append(f"- {n}: står {hus.distance(pt):.1f} m fra en husvegg (krav 4 m)")
    a = pt.distance(Point(*ORTOFOTO_MIDT))
    if a > 1.5: feil.append(f"- {n}: {a:.1f} m fra sokkelen i ortofotoet")
    h = sum(l['h'] for l in st.get('sokkel', [])) + st.get('figur', {}).get('h', 0)
    if not HOYDE_SKYGGE[0] <= h <= HOYDE_SKYGGE[1]: feil.append(f"- {n}: total høyde {h:.2f} m passer ikke skyggen i ortofotoet ({HOYDE_SKYGGE[0]}–{HOYDE_SKYGGE[1]} m)")
    linjer.append(f"{n} ({st.get('billedhugger')}, {st.get('avduket')}): {h:.2f} m høy, ser mot {st.get('retning')}° ({avvik:+.1f}° fra gatenettet), "
                  f"{a:.1f} m fra sokkelen i ortofotoet, {hus.distance(pt):.1f} m til nærmeste hus")
kode = open(os.path.join(ROT, 'src', '20_statuen-paa-torvet.js'), encoding='utf8').read()
for k in ('st.sokkel', 'st.retning', 'st.xy', 'st.figur'):
    if k not in kode: feil.append(f"- tegnekoden leser ikke {k} fra dataene")
if not S: feil.append('- data/statue.json er tom')
linjer += feil
rapport('22_statue', not feil, linjer, 'rapport/torvet/statue.png')
