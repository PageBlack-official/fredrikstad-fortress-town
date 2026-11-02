"""Regel (02.11, avvik A13): ingen fri vegg på minst 3 m står uten vinduer, med mindre en kilde sier at den er blank.
Vegar via koordinator 02.11: «En blank vegg på et hus som har vinduer på de andre sidene er feil.»
Årsaken: fasadeverktøyene ga vinduer bare til vegger de hadde en kilde for (tegningen, Street View) eller til hus merket «antatt»;
hus fra tegningen med vegger tegningen ikke viser (bnr-16308102, Voldporten, bnr-194006187, Det nye rådhus …) og hus uten
fasadekilde (bnr-193972306, bnr-193972446) fikk blanke vegger. verktoy/blanke_vegger.py gir dem vinduer i husets egen rytme.
Regelen kjører samme sjekk som verktøyet (blanke_vegger.beregn) på dataene slik kartet viser dem, og er rød når den finner noe.
Blank etter kilde (tegningen, merknad, Street View) teller ikke. Rød også når et vindu står over takfoten uten å høre til en ark
(rader lest mot en eldre høyde, datalag.hoyden_styrer tar dem ut).
"""
import sys
from _felles import *
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import blanke_vegger as BV  # noqa: E402

nye, logg = BV.beregn()
feil = [f"FEIL {i} ({n or ''}): {v} blanke frie vegger" for i, n, v, _ in logg]
k = open(os.path.join(ROT, 'verktoy', 'bygg_kjede.py'), encoding='utf8').read()
if 'blanke_vegger.py' not in k: feil.append('FEIL verktoy/blanke_vegger.py står ikke i kjeden')
import datalag, math  # noqa: E402
# vinduer over takfoten (A13): rader fra en eldre høyde som står i lufta over gesimsen
over = []
for b in datalag.alle()['bygg']:
    if b.get('skjul') or b.get('kirke'): continue
    ark = b.get('arker') or []
    n = sum(1 for v in (b.get('vind') or []) if v[9] != 3 and v[2] + v[8] / 2 > b['h'] - 0.1 and not any(math.hypot(v[0] - a[0], v[1] - a[1]) < 1.5 for a in ark))
    if n: over.append(f"FEIL {b['id']} ({b.get('navn') or ''}): {n} vinduer over takfoten")
feil += over
rapport('44_ingen_blanke_vegger', not feil, [f"{len(logg)} hus med blanke frie vegger uten kilde"] + feil)
