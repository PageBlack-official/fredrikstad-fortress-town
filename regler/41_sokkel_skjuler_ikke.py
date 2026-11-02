"""Regel (02.11, avvik A9/A10): sokkelen skjuler ikke vinduer og dører, løftes med huset, og naturstein tegnes som stein.
Vegar 02.11 18:26: «Artellerigården er synket i jorden som default og så dukker opp vinduer og dører når man klikker på den.»
Årsaken: src/19 tegnet en egen «granittsokkel» 16 cm utenfor veggen for alle hus med feltet sokkel (laget for Kasernens 1,1 m).
Artillerigården har en natursteinsetasje på 3,1 m (merknad fra Vegars kvartalskontroll), så båndet dekket hele første etasje, og
båndet lå i en egen gruppe som ikke ble løftet når huset ble klikket. Regelen er rød når
  - sokkelen tegnes et annet sted enn i huset selv (src/07), dvs. et src-fil utenom 07 bruker b.sokkel / .sokkel.h,
  - sokkelen i src/07 står like langt eller lenger ut fra veggen enn vinduene (vindusData),
  - et vindu eller en dør i sokkelhøyden står mer enn 0,1 m fra veggen (inne i eller utenfor sokkelen),
  - et hus har sokkel med type naturstein uten at src/07 gir steinmønsteret (mat(..., {stein})),
  - kildene sier at første etasje (eller hele veggen) er stein, og steinen er lavere enn underkant av andre etasjes vinduer
    (eller veggen): et bånd under vinduene (A10 gjenåpnet 02.11, Artillerigården).
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
        from shapely.geometry import Polygon as _P, Point as _Pt
        dmin = _P(p).exterior.distance(_Pt(v[0], v[1]))
        if dmin > 0.1:
            feil.append(f"FEIL {b['id']}: vindu/dør i sokkelen står {dmin:.2f} m fra veggen ({v[:3]})"); break
linjer.append(f"{n_sokkel} hus med sokkel og vinduer, {n_vind} vinduer/dører i sokkelhøyden sjekket")
# steinetasje (A10 gjenåpnet 02.11): der kildene sier at hele første etasje (eller hele veggen) er stein, skal steinen gå fra bakken
# til underkant av vinduene i andre etasje (eller hele veggen), ikke være et bånd under vinduene i første etasje
sys.path.insert(0, os.path.join(ROT, 'verktoy')); import sokkel as SO, json as _j
krav = {i: v for i, v in SO.beregn(d).items() if v.get('etasje') or v.get('hele')}
for m in _j.load(open(os.path.join(ROT, 'kilder', 'bygg-merknader.json'), encoding='utf8'))['hus']:
    sk = (m.get('sett') or {}).get('sokkel') or {}
    if sk.get('etasje') or sk.get('hele'): krav[m['id']] = sk
BY = {b['id']: b for b in d['bygg']}
for i, k in sorted(krav.items()):
    b = BY.get(i)
    if not b or b.get('skjul'): continue
    s_ = b.get('sokkel') or {}
    if k.get('hele'): maal = float(b['h'])
    else:
        rad = sorted((v[2], v[8]) for v in (b.get('vind') or []) if v[9] == 0 and v[8] >= 0.8)
        rader = []
        for z, vh in rad:
            if rader and z - rader[-1][0][0] <= 1.0: rader[-1].append((z, vh))
            else: rader.append([(z, vh)])
        rader = [r for r in rader if len(r) >= 2] or rader
        maal = min(z - vh / 2 for z, vh in rader[1]) if len(rader) >= 2 else float(b['h'])
    hs = float(s_.get('h') or 0)
    ok_ = s_.get('type') == 'naturstein' and hs >= maal - 0.05
    (feil if not ok_ else linjer).append(f"{'FEIL' if not ok_ else 'ok  '} {i} ({b.get('navn') or ''}): stein {hs:.2f} m, {'hele veggen' if k.get('hele') else 'til andre etasjes vinduer'} {maal:.2f} m")
rapport('41_sokkel_skjuler_ikke', not feil, [f"{len(feil)} feil"] + feil + linjer)
