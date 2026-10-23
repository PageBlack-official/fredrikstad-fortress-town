"""Regel (23.10, skjerpet samme dag): tegnekvaliteten er den samme i fart og i ro.
Oppløsning, hjørneskygge (aoN) og strek (ssN) skal ikke avhenge av om kartet beveger seg; bare maskinen (maalYtelse) får senke dem, og da for godt.
Vegar så skyggene bli pikslete under dra og skarpe ved slipp, på Mac og mobil. Det var to tilstander. Nå er det én.
"""
import re
from _felles import *
src = ''.join(open(os.path.join(ROT, 'src', f), encoding='utf8').read() for f in sorted(os.listdir(os.path.join(ROT, 'src'))) if f.endswith('.js'))
linjer = []
m = re.search(r'post\.settSkala\((.*?)\); post\.setAO\((.*?)\); post\.setSS\((.*?)\);', src)
ok = m is not None
if m:
    for navn, arg in zip(('settSkala', 'setAO', 'setSS'), m.groups()):
        avhenger = bool(re.search(r'stille|anim|kamFlytt|Beveg', arg))
        linjer.append(f"{navn}({arg}) {'avhenger av bevegelse' if avhenger else 'uavhengig av bevegelse'}")
        ok = ok and not avhenger
else:
    linjer.append('fant ikke kvalitetslinja i oppdater()')
for ord in ('skalaBeveg', 'aoBeveg', 'PIX_BEVEG'):
    if ord in src:
        ok = False; linjer.append(f"'{ord}' finnes fortsatt i kilden (to tilstander)")
rapport('05_kvalitet_bare_kamera', ok, linjer)
