"""Regel (02.11, avvik A9/A10): sokkelen skjuler ikke vinduer og dører, løftes med huset, og naturstein tegnes som stein.
Vegar 02.11 18:26: «Artellerigården er synket i jorden som default og så dukker opp vinduer og dører når man klikker på den.»
Årsaken: src/19 tegnet en egen «granittsokkel» 16 cm utenfor veggen for alle hus med feltet sokkel (laget for Kasernens 1,1 m).
Artillerigården har en natursteinsetasje på 3,1 m (merknad fra Vegars kvartalskontroll), så båndet dekket hele første etasje, og
båndet lå i en egen gruppe som ikke ble løftet når huset ble klikket. Regelen er rød når
  - sokkelen tegnes et annet sted enn i huset selv (src/07), dvs. et src-fil utenom 07 bruker b.sokkel / .sokkel.h,
  - sokkelen i src/07 står like langt eller lenger ut fra veggen enn vinduene (vindusData),
  - et vindu eller en dør i sokkelhøyden står mer enn 0,1 m fra veggen (inne i eller utenfor sokkelen),
  - et hus har sokkel med type naturstein uten at src/07 gir steinmønsteret (mat(..., {stein})).
"""
import sys, re, glob, math
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402

feil, linjer = [], []
src = {os.path.basename(f): open(f, encoding='utf8').read() for f in glob.glob(os.path.join(ROT, 'src', '*.js'))}
for navn, k in src.items():
    if navn.startswith('07_'): continue
    if re.search(r'b\.sokkel|\.sokkel\.h', k):
        feil.append(f"FEIL {navn} tegner sokkelen utenfor huset (løftes ikke, kan dekke vinduene)")
k07 = next(v for n, v in src.items() if n.startswith('07_'))
m_s = re.search(r'utvidPoly\(pts,\s*([0-9.]+)\)\),\{depth:Math\.min\(b\.sokkel\.h', k07)
m_v = re.search(r'setPosition\(x\+nx\*([0-9.]+)', k07)
if not m_s or not m_v:
    feil.append('FEIL fant ikke sokkelens eller vinduenes avstand fra veggen i src/07')
else:
    s_ut, v_ut = float(m_s.group(1)), float(m_v.group(1))
    (feil if s_ut >= v_ut else linjer).append(f"{'FEIL' if s_ut >= v_ut else 'ok  '} sokkelen står {s_ut} m ut, vinduene {v_ut} m (vinduene må stå foran)")
if "stein:b.sokkel.type==='naturstein'" not in k07:
    feil.append('FEIL src/07 gir ikke sokkelen steinmønster for type naturstein')
d = datalag.alle()
n_sokkel = n_vind = 0
for b in d['bygg']:
    s = b.get('sokkel')
    if not s or b.get('skjul') or not b.get('vind'): continue
    n_sokkel += 1
    p = b['p']; n = len(p)
    for v in b['vind']:
        if v[2] - v[8] / 2 > s['h']: continue
        n_vind += 1
        dmin = min(abs((v[0] - p[i][0]) * (p[(i + 1) % n][1] - p[i][1]) - (v[1] - p[i][1]) * (p[(i + 1) % n][0] - p[i][0]))
                   / max(1e-9, math.hypot(p[(i + 1) % n][0] - p[i][0], p[(i + 1) % n][1] - p[i][1])) for i in range(n))
        if dmin > 0.1:
            feil.append(f"FEIL {b['id']}: vindu/dør i sokkelen står {dmin:.2f} m fra veggen ({v[:3]})"); break
linjer.append(f"{n_sokkel} hus med sokkel og vinduer, {n_vind} vinduer/dører i sokkelhøyden sjekket")
rapport('41_sokkel_skjuler_ikke', not feil, [f"{len(feil)} feil"] + feil + linjer)
