"""Regel (02.11, avvik A8): ingen to bakkeflater med ulikt utseende kjemper om samme dybde, og veiene ligger på terrenget.
Vegar 02.11 18:26: «"tagger" som glitcher. De står å vibrerer når jeg scroller.»
Årsaken: bakken er mange lag nesten i samme høyde (brostein 5 cm, gangveier 7 cm, flater 9 cm, kjøreveier 10 cm, parkering 12 cm,
gress 28 cm). På avstand er dybdebufferen grovere enn centimeterne, så lagene z-kjempet og flimret i fart; 139 kryss mellom veier
av ulik flatetype og 2 overlapp mellom flater av ulik type lå i nøyaktig samme høyde. På vollene skar rette veibiter (punkter med
opptil 30 m mellomrom) gjennom terrenget, som stakk opp som takker (Mellomporten).
Rettelsen: src/03 BAKKELAG/bakkelag() gir hvert lag og hver farge i laget sin egen polygonOffset; src/08 deler veiene opp og legger
dem på terrenget. Regelen er rød når
  - et bakkemateriale ikke har lag (stoneMat, plenMat, terMat, veiene i src/08, flatene i src/17),
  - to ulike utseender har samme (lag, underlag),
  - veibåndet i src/08 ikke legges på terrenget (hAt i kantene) eller ikke deles opp,
  - en flatetype eller veiflate i dataene ikke har et underlag.
"""
import sys, re, glob
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402

feil, linjer = [], []
src = {os.path.basename(f)[:2]: open(f, encoding='utf8').read() for f in glob.glob(os.path.join(ROT, 'src', '*.js'))}
krav = [('04', r'bakkelag\(stoneMat,\s*BAKKELAG\.brostein\)', 'brosteinen'), ('04', r'bakkelag\(plenMat,\s*BAKKELAG\.gress\)', 'gresset'),
        ('08', r'bakkelag\(terMat,\s*BAKKELAG\.terreng\)', 'terrenget'), ('08', r'bakkelag\(mm,\s*BAKKELAG\.vei,\s*under\)', 'veiene'),
        ('17', r'bakkelag\(flateMat\(FARGE\[k\]\)', 'flatene'), ('08', r'hAt\(P\[k\]\[0\]\+nx', 'veikantene på terrenget'),
        ('08', r'Math\.ceil\(Math\.hypot\(c\[0\]-a\[0\],c\[1\]-a\[1\]\)/steg\)', 'veibitene delt opp')]
for fil, mønster, hva in krav:
    if not re.search(mønster, src.get(fil, '')): feil.append(f"FEIL src/{fil}: {hva} mangler (bakkelag/terreng)")
    else: linjer.append(f"ok   src/{fil}: {hva}")
# lag og underlag per utseende
lag = {'terreng': (0, 0), 'brostein': (0, 0)}
m = re.search(r"\[\[buf\.K,.*?\]\]\.forEach", src.get('08', ''), re.S)
for navn, u in re.findall(r"\[buf\.([KGHU]),mat\(\[[0-9, ]+\],false\),([0-9])\]", m.group(0) if m else ''):
    lag['vei_' + navn] = (1, int(u))
m = re.search(r"\{(asfalt:[0-9][^}]*)\}\[k\]", src.get('17', ''))
under17 = dict((k, int(v)) for k, v in re.findall(r"(\w+):([0-9])", m.group(1))) if m else {}
for t in ('asfalt', 'grus', 'heller', 'bed'): lag['flate_' + t] = (2, under17.get(t, -1))
lag['parkering'] = (3, 0); lag['gress'] = (4, 0)
if set(lag) >= {'vei_K', 'vei_G', 'vei_H', 'vei_U'}: linjer.append('ok   fire veiflater med eget underlag')
else: feil.append('FEIL src/08: veiflatene mangler underlag')
sett = {}
for k, v in lag.items():
    if v[1] < 0: feil.append(f"FEIL {k} har ikke underlag"); continue
    if v in sett and not ({k, sett[v]} <= {'terreng', 'brostein'}): feil.append(f"FEIL {k} og {sett[v]} har samme lag og underlag {v}")
    sett.setdefault(v, k)
d = datalag.alle()
typer = {f['typ'] for f in d['flater'] if not f.get('skjul')} - {'gress', 'brostein'}
for t in sorted(typer):
    if 'flate_' + t not in lag: feil.append(f"FEIL flatetypen {t} i dataene har ikke underlag i src/17")
rapport('42_bakkelag', not feil, [f"{len(feil)} feil; {len(lag)} bakkeutseender med lag"] + feil + linjer + [f"- {k}: lag {v[0]}, underlag {v[1]}" for k, v in sorted(lag.items(), key=lambda x: x[1])])
