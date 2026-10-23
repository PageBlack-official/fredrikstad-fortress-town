"""Regel (23.10): den sammensatte modulen skal gjennom ESLint uten feil. Reglene er de som har bitt oss i dag:
no-const-assign (hvitt blink), no-undef (navn som bare finnes i en annen seksjon), no-redeclare, no-dupe-keys, no-unreachable."""
import subprocess, os, re, tempfile
from _felles import *
html = open(os.path.join(ROT, 'ut', 'enkel', 'index.html'), encoding='utf8').read()
m = re.search(r'<script type="module">(.*?)</script>', html, re.S)
ok = m is not None; linjer = []
if m:
    p = os.path.join(ROT, 'ut', 'modul.js'); open(p, 'w', encoding='utf8').write(m.group(1))   # må ligge i prosjektet, ellers ignorerer eslint fila stille
    r = subprocess.run([os.path.join(ROT, 'node_modules', '.bin', 'eslint'), '-c', os.path.join(ROT, 'verktoy', 'eslint.config.mjs'), '--no-config-lookup', p], capture_output=True, text=True)
    ut = (r.stdout + r.stderr).strip()
    ok = r.returncode == 0 and 'ignored' not in ut and 'modul.js' in ut + 'modul.js'
    if 'ignored' in ut: ok = False
    linjer = ['- ' + l.strip() for l in ut.split('\n') if 'error' in l][:25] or ['- ingen feil']
else:
    linjer = ['- fant ikke modulen i ut/enkel/index.html']
rapport('08_lint', ok, linjer)
