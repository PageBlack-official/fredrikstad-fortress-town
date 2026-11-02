"""Regel (02.11, avvik A15): ingen brostein tegnes oppå brosteinsgrunnen.
Rett skjøt i brosteinen over Torvet og stripete bånd langs gatene: brosteinsflater (flater typ brostein, parkeringsfelt i
brostein) og brosteinsbånd i veiene lå et par centimeter over brosteinsgrunnen (src/04), og streken (src/01) tegnet kantene.
Rettelsen er i src/03 (iBrostein/alleIBrostein), src/08 (veibåndene) og src/17 (flatene). Regelen er rød når
  - koden i src/08 eller src/17 ikke hopper over brostein som ligger i brosteinsflaten,
  - iBrostein ikke er definert (src/03).
Den rapporterer hvor mange flater og veibiter dette gjelder i dataene.
"""
import glob, re, sys
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402
from shapely.geometry import Polygon, Point  # noqa: E402
src = {os.path.basename(f)[:2]: open(f, encoding='utf8').read() for f in glob.glob(os.path.join(ROT, 'src', '*.js'))}
feil, linjer = [], []
if 'function iBrostein' not in src['03'] or 'function alleIBrostein' not in src['03']: feil.append('FEIL src/03: iBrostein/alleIBrostein mangler')
if not re.search(r"B===buf\.B && alleIBrostein", src['08']): feil.append('FEIL src/08: brosteinsbånd i veiene tegnes oppå brosteinsgrunnen')
if not re.search(r"f\.typ==='brostein' && alleIBrostein\(f\.p\)", src['17']): feil.append('FEIL src/17: brosteinsflater tegnes oppå brosteinsgrunnen')
d = datalag.alle(); B = Polygon(d['brostein']).buffer(0)
n_f = sum(1 for f in d['flater'] if not f.get('skjul') and f['typ'] == 'brostein' and all(B.contains(Point(q)) for q in f['p']))
n_v = sum(1 for v in d['landskap']['veier'] if v.get('flate') == 'brostein' and all(B.contains(Point(q[:2])) for q in v['p']))
linjer.append(f"{n_f} brosteinsflater og {n_v} brosteinsveier ligger i brosteinsflaten og tegnes ikke (grunnen er brostein)")
if "f.typ==='brostein'?0.05" not in src['17']: feil.append('FEIL src/17: brosteinsflater utenfor grunnen ligger ikke i grunnens høyde (5 cm)')
if not re.search(r"B===buf\.B \? hTer\(P\[k\]\[0\]\+nx,P\[k\]\[1\]\+ny\)\+0\.05", src['08']): feil.append('FEIL src/08: brosteinsbånd ligger ikke i grunnens høyde (5 cm)')
rapport('45_brostein_paa_brostein', not feil, [f"{len(feil)} feil"] + feil + linjer)
