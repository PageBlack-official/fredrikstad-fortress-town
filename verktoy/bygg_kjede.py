"""Kjeden for byggene i fast rekkefølge (LESMEG: «Byggene: kjeden»). Hvert steg flytter sine rettelser bakerst, så
rekkefølgen avgjør hvem som vinner: grunnmur < id < høyde < regler < Street View < tegning < ortofoto-tak < merknader.

    python3 verktoy/bygg_kjede.py            alt etter grunnmur.py (grunnmuren tar ~8 min; kjør den selv når omrissene endres)
    python3 verktoy/bygg_kjede.py --grunnmur alt, også grunnmur.py
"""
import subprocess, sys, os
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEG = [['verktoy/grunnmur.py'], ['verktoy/id_flytt.py'], ['-I', 'rapport/hoyder/hent.py'], ['-I', 'rapport/hoyder/legg_inn.py'],
        ['verktoy/vinduer_regler.py'], ['verktoy/streetview_fasader.py'], ['verktoy/streetview_farger.py'],
        ['verktoy/fasade_tegning.py', 'legg_inn'], ['verktoy/tak_fra_ortofoto.py'], ['verktoy/vegg_nye.py'], ['verktoy/bygg_merknader.py']]
for s in STEG:
    if s[0] == 'verktoy/grunnmur.py' and '--grunnmur' not in sys.argv:
        continue
    r = subprocess.run([sys.executable] + s, cwd=ROT, capture_output=True, text=True)
    siste = (r.stdout.strip().splitlines() or [''])[-1]
    print(f"{'OK  ' if r.returncode == 0 else 'FEIL'} {' '.join(s):40s} {siste[:150]}")
    if r.returncode:
        print(r.stderr[-1500:]); sys.exit(1)
