#!/usr/bin/env python3
"""Setter sammen kartet fra kilden. Ingen tekstbytte i ferdig HTML; alt kommer fra data/, src/ og assets/.

  python3 bygg.py enkel   -> ut/enkel/index.html   (én fil med data og teksturer inni; til artefakt/e-post)
  python3 bygg.py server  -> ut/server/            (index.html + data/by.json + assets/ + manifest + sw.js; til server og app)
"""
import base64, json, os, re, shutil, sys, hashlib

ROT = os.path.dirname(os.path.abspath(__file__))
MODUS = sys.argv[1] if len(sys.argv) > 1 else 'enkel'
UT = os.path.join(ROT, 'ut', MODUS)
os.makedirs(UT, exist_ok=True)

def les(p): return open(os.path.join(ROT, p), encoding='utf8').read()

# ---- data: alt går gjennom datalag.py (rettelser på id, høyden som styrer piper/arker/vinduer, koblinger), samme som regelsjekkene ----
sys.path.insert(0, ROT)
import datalag
data = datalag.koble_til_plass(datalag.alle())
rettelser = datalag.les('rettelser')
versjon = les('VERSJON').strip()
data['logg'].append(f'bygd fra kilde, versjon {versjon}, modus {MODUS}, {len(rettelser)} rettelser lagt oppå')
datatekst = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# ---- js: seksjonene i rekkefølge ----
js = '\n'.join(les('src/' + f) for f in sorted(os.listdir(os.path.join(ROT, 'src'))) if re.match(r'\d\d_.*\.js$', f))   # bare de nummererte seksjonene; sw.js er tjenestearbeideren og hører ikke hjemme i siden (lint fant den 23.10)

def tekstur(fil):
    if MODUS == 'enkel':
        b = open(os.path.join(ROT, 'assets', fil), 'rb').read()
        return "'data:image/png;base64," + base64.b64encode(b).decode() + "'"
    return f"'assets/{fil}'"
js = re.sub(r"__TEKSTUR\('([^']+)'\)", lambda m: tekstur(m.group(1)), js)

if MODUS == 'server':
    # data hentes som egen fil, så siden er liten og dataene kan mellomlagres av tjenestearbeideren
    js = js.replace("const DATA = JSON.parse(document.getElementById('bydata').textContent);",
                    "const DATA = await (await fetch('data/by.json')).json();")
    os.makedirs(os.path.join(UT, 'data'), exist_ok=True)
    open(os.path.join(UT, 'data', 'by.json'), 'w', encoding='utf8').write(datatekst)
    shutil.copytree(os.path.join(ROT, 'assets'), os.path.join(UT, 'assets'), dirs_exist_ok=True)
    datascript = ''
else:
    datascript = f'<script id="bydata" type="application/json">{datatekst}</script>'

importmap = les('src/importmap.json').strip()
html = les('src/mal.html')
html = (html.replace('{{MAPLIBRE_CSS}}', les('assets/maplibre-gl-6.14.0.css').strip())
            .replace('{{STIL}}', les('src/stil.css').strip())
            .replace('{{KROPP}}', les('src/kropp.html').strip())
            .replace('{{IMPORTMAP}}', importmap)
            .replace('{{DATA}}', datascript)
            .replace('{{JS}}', js)
            .replace('{{VERSJON}}', versjon)
            .replace('{{APP}}', '<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="ikon-192.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Gamlebyen"><meta name="theme-color" content="#e2e1d6">' if MODUS == 'server' else '')
            .replace('{{SW}}', "<script>if('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(()=>{});</script>" if MODUS == 'server' else ''))
open(os.path.join(UT, 'index.html'), 'w', encoding='utf8').write(html)

if MODUS == 'server':
    shutil.copy(os.path.join(ROT, 'src', 'manifest.webmanifest'), UT)
    sw = les('src/sw.js').replace('{{VERSJON}}', versjon + '-' + hashlib.md5(datatekst.encode()).hexdigest()[:8])
    open(os.path.join(UT, 'sw.js'), 'w', encoding='utf8').write(sw)
    for ikon in ('ikon-192.png', 'ikon-512.png'):
        if os.path.exists(os.path.join(ROT, 'assets', ikon)):
            shutil.copy(os.path.join(ROT, 'assets', ikon), UT)

print('bygd', MODUS, '->', os.path.join(UT, 'index.html'), f'{os.path.getsize(os.path.join(UT, "index.html"))//1000} kB', 'versjon', versjon)
