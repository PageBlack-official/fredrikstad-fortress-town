"""Regel (24.10, lys-og-bevegelse pkt. 2): animerte kameraflytt bruker én felles kurve (glid: eksponentiell inn og ut) og lander uten bråstopp.
Sjekkes i kilden: ingen easeTo/panBy med egne kurver utenom glid/glidUt, dobbeltklikk-zoomen er vår egen (MapLibres 300 ms er slått av),
og kurven er eksponentiell (siste 10 % av tida flytter under 3 % av veien)."""
import os, re, math
from _felles import *
src = ''.join(open(os.path.join(ROT, 'src', f), encoding='utf8').read() for f in sorted(os.listdir(os.path.join(ROT, 'src'))) if re.match(r'\d\d_.*\.js$', f))
linjer = []; ok = True
egne = [l for l in src.split('\n') if re.search(r'\.(easeTo|panBy|flyTo)\(', l) and 'easing' in l and not re.search(r'easing:\s*(glid|glidUt|GLID)', l)]
if egne: ok = False; linjer.append(f'- {len(egne)} flytt med egen kurve: ' + egne[0].strip()[:90])
else: linjer.append('- alle animerte flytt bruker glid/glidUt')
if 'map.doubleClickZoom.disable()' not in src: ok = False; linjer.append('- MapLibres dobbeltklikk-zoom (300 ms, bråstopp) er ikke slått av')
else: linjer.append('- dobbeltklikk-zoom er vår egen (800 ms, glid)')
glid = lambda t: 0 if t <= 0 else 1 if t >= 1 else (2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2)
hale = 1 - glid(0.9); start = glid(0.1)
if hale > 0.03 or start > 0.03: ok = False
linjer.append(f'- kurven: siste 10 % av tida flytter {hale*100:.1f} % av veien, første 10 % flytter {start*100:.1f} % (krav under 3 %)')
rapport('11_kamera_glir', ok, linjer)
