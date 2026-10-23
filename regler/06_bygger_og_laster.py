"""Regel: begge byggene (enkel og server) skal bygges og laste i nettleseren uten JS-feil."""
import subprocess, os
from _felles import *
ok = True; linjer = []
for modus in ('enkel', 'server'):
    r = subprocess.run(['python3', os.path.join(ROT, 'bygg.py'), modus], capture_output=True, text=True); ok &= r.returncode == 0; linjer.append('- ' + r.stdout.strip().split('\n')[-1])
r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'last-test.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html')], capture_output=True, text=True)
linjer.append('- ' + r.stdout.strip()); ok &= 'feil: []' in r.stdout and 'lastet: true' in r.stdout
rapport('06_bygger_og_laster', ok, linjer)
