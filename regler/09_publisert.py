"""Regel (23.10): det som er publisert, er den versjonen vi tror. Henter GitHub Pages og artefaktbygget (publiser/gamle-fredrikstad.html)
og sammenligner «Versjon N» i meta-beskrivelsen med VERSJON. Grunn: publiser.sh stoppet stille 23.10 (gh-pages fantes lokalt), og Pages
stod på v27 hele kvelden mens vi målte ytelse på «v28». Regelen kjøres etter publisering (kjor.py tar den med; rød til det er publisert)."""
import os, re, urllib.request
from _felles import *
PAGES = 'https://pageblack-official.github.io/fredrikstad-fortress-town/'
onsket = open(os.path.join(ROT, 'VERSJON')).read().strip()
linjer = []; ok = True
def versjon_i(html):
    m = re.search(r'Versjon (\d+(?:\.\d+)?)\.', html); return m.group(1) if m else None
try:
    with urllib.request.urlopen(urllib.request.Request(PAGES, headers={'Cache-Control': 'no-cache'}), timeout=20) as r: v = versjon_i(r.read().decode('utf8', 'replace'))
    linjer.append(f'- Pages: versjon {v} (ønsket {onsket})'); ok = ok and v == onsket
except Exception as e:
    linjer.append(f'- Pages: kunne ikke hentes ({e})'); ok = False
art = os.path.join(ROT, '..', 'publiser', 'gamle-fredrikstad.html')
if os.path.exists(art):
    v = versjon_i(open(art, encoding='utf8').read()); linjer.append(f'- artefaktbygg: versjon {v}'); ok = ok and v == onsket
else:
    linjer.append('- artefaktbygg: fil mangler'); ok = False
rapport('09_publisert', ok, linjer)
