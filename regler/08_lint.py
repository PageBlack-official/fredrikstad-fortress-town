"""Regel (23.10, utvidet 05.11): den sammensatte modulen OG hver modul i src/ for seg skal gjennom ESLint uten feil, og ingen modul
importerer fra en modul som kommer senere i src/main.js (da blir lasterekkefølgen sirkulær; bruk SENERE i tilstand.js). Reglene er de som har bitt oss i dag:
no-const-assign (hvitt blink), no-undef (navn som bare finnes i en annen seksjon), no-redeclare, no-dupe-keys, no-unreachable."""
import subprocess, os, re, tempfile
from _felles import *
html = open(os.path.join(ROT, 'ut', 'enkel', 'index.html'), encoding='utf8').read()
m = re.search(r'<script type="module">(.*?)</script>', html, re.S)
ok = m is not None; linjer = []
if m:
    p = os.path.join(ROT, 'ut', 'modul.js'); open(p, 'w', encoding='utf8').write(m.group(1))   # må ligge i prosjektet og kjøres derfra, ellers ignorerer eslint fila (som en advarsel)
    r = subprocess.run([os.path.join(ROT, 'node_modules', '.bin', 'eslint'), '-c', os.path.join(ROT, 'verktoy', 'eslint.config.mjs'), '--no-config-lookup', p], capture_output=True, text=True, cwd=ROT)   # eslint 9 ignorer filer utenfor arbeidsmappa
    ut = (r.stdout + r.stderr).strip()
    ok = r.returncode == 0 and 'ignored' not in ut and 'modul.js' in ut + 'modul.js'
    if 'ignored' in ut: ok = False
    linjer = ['- ' + l.strip() for l in ut.split('\n') if 'error' in l][:25] or ['- ingen feil']
else:
    linjer = ['- fant ikke modulen i ut/enkel/index.html']
# hver modul for seg: no-undef fanger navn som ikke er importert (spagetti-vakta fra omleggingen 05.11)
moduler = [f for f in os.listdir(os.path.join(ROT, 'src')) if f.endswith('.js') and f != 'sw.js']
r = subprocess.run([os.path.join(ROT, 'node_modules', '.bin', 'eslint'), '-c', os.path.join(ROT, 'verktoy', 'eslint.config.mjs'), '--no-config-lookup'] + [os.path.join('src', f) for f in moduler], capture_output=True, text=True, cwd=ROT)
if r.returncode != 0:
    ok = False; linjer += ['- src: ' + l.strip() for l in r.stdout.split('\n') if 'error' in l][:25]
else:
    linjer.append(f'- src: {len(moduler)} moduler uten feil')
orden = re.findall(r"^import '\./([^']+)';", open(os.path.join(ROT, 'src', 'main.js'), encoding='utf8').read(), re.M)
bak = []
for i, f in enumerate(orden):
    for g in re.findall(r"^import \{[^}]*\} from '\./([^']+)';", open(os.path.join(ROT, 'src', f), encoding='utf8').read(), re.M):
        if g not in orden or orden.index(g) > i: bak.append(f'{f} <- {g}')
if bak: ok = False; linjer += ['- importerer fra senere modul: ' + b for b in bak]
else: linjer.append(f'- {len(orden)} moduler i main.js, ingen importerer fra en senere')
skriver = [f'{f}: {m.group(0)}' for f in moduler if f != 'kvalitet.js' for m in re.finditer(r'\bKVAL\.\w+\s*(?:[-+*/]?=(?!=)|\+\+|--)', open(os.path.join(ROT, 'src', f), encoding='utf8').read())]
if skriver: ok = False; linjer += ['- skriver kvaliteten utenfor kvalitet.js: ' + x for x in skriver]
else: linjer.append('- bare kvalitet.js skriver KVAL')
manglende = [f for f in moduler if f not in orden and f != 'main.js']
if manglende: ok = False; linjer.append('- moduler som ikke lastes av main.js: ' + ', '.join(manglende))
rapport('08_lint', ok, linjer)
