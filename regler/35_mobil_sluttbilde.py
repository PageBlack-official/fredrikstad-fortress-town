"""Regel (02.11): stående telefon ender introen på Vegars sluttbilde, uansett versjon.
Vegar 02.11 13:23, med skjermbilde fra iPhone: «Uansett versjon vil jeg at denne stillingen skal være siste frame på mobilvisningen».
Torvet med statuen midt i bildet, Det gamle rådhus bak, kirka oppe til høyre, elva nederst: asimut 193, faktor 1,22, sentrum [12,67], høyde 40°.
Skjermbildet hans ligger i rapport/mobil-sluttbilde/fasit.png. Endres bare etter ny dom fra ham.
"""
import re
from _felles import *
src = ''.join(open(os.path.join(ROT, 'src', f), encoding='utf8').read() for f in sorted(os.listdir(os.path.join(ROT, 'src'))) if f.endswith('.js'))
krav = [
    ('asimut 193', r"az0'\)\|\|\(STAAENDE \? 193 :"),
    ('faktor 1,22', r"z0'\)\|\|\(STAAENDE \? 1\.22 :"),
    ('sentrum [12,67]', r"MOBIL_START=\[12,67\]"),
    ('sentrum brukes på stående skjerm', r"STAAENDE \? MOBIL_START"),
    ('høyde 40° på stående skjerm', r"innerWidth/innerHeight<0\.8 \? 40 :"),
    ('stående = bredde/høyde < 0,8', r"const STAAENDE=innerWidth/innerHeight<0\.8;"),
]
linjer = []; ok = True
for navn, mønster in krav:
    funnet = re.search(mønster, src) is not None
    linjer.append(f"{'ok  ' if funnet else 'FEIL'} {navn}"); ok = ok and funnet
fasit = os.path.join(ROT, 'rapport', 'mobil-sluttbilde', 'fasit.png')
if not os.path.exists(fasit): ok = False; linjer.append('FEIL fasitbildet mangler')
rapport('35_mobil_sluttbilde', ok, linjer)
