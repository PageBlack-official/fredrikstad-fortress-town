"""Regel: statuer og skulpturer (data/statue.json) er tegnet etter kildene, ikke gjettet.
- hver post har navn, billedhugger, plass og kilde-URL-er; poster som tegnes har også år, materiale, retning, figur (form og høyde) og sokkel
- en post som ikke tegnes (tegnes: false), har en grunn (f.eks. plassen er bare kommunens registerpunkt og ses ikke i ortofotoet)
- kontroll.ortofoto_xy: plassen står innen 1,5 m fra midtpunktet målt i ortofoto 2024; plassen er på åpen grunn (ikke i et hus)
- kontroll.gatenett: retningen står vinkelrett på gatenettet (data/gatevinkel.json) innen ±5° (Frederik II: sokkelen parallell med husene)
- kontroll.hoyde: høyden i alt (sokkel + figur) ligger i intervallet som skyggen i ortofotoet gir
- tegnekoden (src/20_statuen-paa-torvet.js) leser mål, retning og plass fra dataene, og har en figur for hver form i dataene
Bevis: rapport/torvet/statue.png (python3 verktoy/statue_ark.py) og rapport/torvet/statue-i-kartet.png."""
import os, re
from _felles import *
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

feil, linjer = [], []
S = data('statue'); bygg = data('bygg')
gv = float(open(os.path.join(ROT, 'data', 'gatevinkel.json')).read().strip())
hus = unary_union([Polygon(b['p']).buffer(0) for b in bygg if not b.get('skjul') and len(b['p']) >= 3])
kode = open(os.path.join(ROT, 'src', '20_statuen-paa-torvet.js'), encoding='utf8').read()
for st in S:
    n = st.get('navn', '?'); tegnes = st.get('tegnes', True)
    for felt in ('navn', 'billedhugger', 'xy', 'kilder') + (('avduket', 'materiale', 'retning', 'figur', 'sokkel') if tegnes else ('grunn',)):
        if not st.get(felt): feil.append(f"- {n}: mangler {felt}")
    if not all(str(k).startswith(('http', 'kilder/')) for k in st.get('kilder', [])): feil.append(f"- {n}: kilde som ikke er URL eller kildefil")
    if not tegnes:
        linjer.append(f"{n} ({st.get('billedhugger')}): tegnes ikke – {st.get('grunn')}"); continue
    form = st.get('figur', {}).get('form')
    if not re.search(r'\b' + re.escape(str(form)) + r'\s*\(', kode): feil.append(f"- {n}: tegnekoden har ingen figur «{form}»")
    K = st.get('kontroll', {}); pt = Point(*st['xy']); tekst = []
    if hus.contains(pt): feil.append(f"- {n}: står inne i et hus")
    if 'ortofoto_xy' in K:
        a = pt.distance(Point(*K['ortofoto_xy'])); tekst.append(f"{a:.1f} m fra ortofotomålingen")
        if a > 1.5: feil.append(f"- {n}: {a:.1f} m fra plassen målt i ortofotoet")
    if K.get('gatenett'):
        avvik = ((st.get('retning', 0) - (90 - gv)) + 45) % 90 - 45; tekst.append(f"{avvik:+.1f}° fra gatenettet")
        if abs(avvik) > 5: feil.append(f"- {n}: retningen {st.get('retning')}° står {avvik:+.0f}° på skrå mot gatenettet ({gv}°)")
    h = sum(l['h'] for l in st.get('sokkel', [])) + st.get('figur', {}).get('h', 0)
    if 'hoyde' in K and not K['hoyde'][0] <= h <= K['hoyde'][1]:
        feil.append(f"- {n}: høyden {h:.2f} m passer ikke skyggen i ortofotoet ({K['hoyde'][0]}–{K['hoyde'][1]} m)")
    linjer.append(f"{n} ({st.get('billedhugger')}, {st.get('avduket')}): {h:.2f} m høy, ser mot {st.get('retning')}°, " + ', '.join(tekst))
for k in ('st.sokkel', 'st.retning', 'st.xy', 'st.figur'):
    if k not in kode: feil.append(f"- tegnekoden leser ikke {k} fra dataene")
if not S: feil.append('- data/statue.json er tom')
linjer += feil
rapport('22_statue', not feil, linjer, 'rapport/torvet/statue.png')
