"""Regel (28.10, Vegar: «trærnes skygge tegnes på nytt hver gang jeg flytter meg»): skyggekartet dekker alltid mer enn bildet
(R >= 1,4·r), tegnes ikke på nytt når kameraet står i ro, og et dra innenfor marginen tegner det ikke på nytt. Sjekkes i bygget
(hodeløs Chrome) ved tre zoomnivåer. Bakgrunn: v31.1 rundet trinnet opp, så dekningen ble mindre enn bildet og «zoom» tegnet
kartet hvert bilde; skyggene kuttet i kanten av dekningen, og kanten fulgte kameraet."""
import subprocess, os, json
from _felles import *
ut = os.path.join(ROT, 'rapport', '_skygge'); os.makedirs(ut, exist_ok=True)
p = os.path.join(ut, 'dra.json')
r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'skygge-dra-test.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), p], capture_output=True, text=True, cwd=ROT, timeout=900)
if not os.path.exists(p):
    rapport('19_skyggekart_stabilt', False, ['- testen krasjet: ' + (r.stderr.strip()[-200:] or r.stdout.strip()[-200:])]); raise SystemExit
d = json.load(open(p)); ok = True; linjer = []
for navn, v in d['res'].items():
    feil = []
    if v['dekning'] < 1.4: feil.append(f"dekning {v['dekning']} (krav >= 1,4)")
    if v['iRo']: feil.append(f"tegnet på nytt i ro: {v['iRo']}")
    if v['dra']: feil.append(f"tegnet på nytt under dra: {v['dra']}")
    if feil: ok = False
    linjer.append(f"- {navn}: R {v['R']:.0f} m, bilde {v['r']:.0f} m, dekning {v['dekning']}; i ro {v['iRoBilder']} bilder, dra {v['draBilder']} bilder" + (' – FEIL ' + '; '.join(feil) if feil else ' – ingen ny tegning'))
if d['feil']: ok = False; linjer.append('- JS-feil: ' + d['feil'][0][:120])
rapport('19_skyggekart_stabilt', ok, linjer)
