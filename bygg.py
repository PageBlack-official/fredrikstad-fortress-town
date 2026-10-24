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

# ---- data: én JSON per emne -> ett objekt ----
data = {}
for fil in sorted(os.listdir(os.path.join(ROT, 'data'))):
    if fil.endswith('.json'):
        data[fil[:-5]] = json.load(open(os.path.join(ROT, 'data', fil), encoding='utf8'))
versjon = les('VERSJON').strip()
# ---- rettelseslaget: data/rettelser.json legges oppå grunndataene ved hvert bygg, én linje per rettelse (hva, hvem, når, hvorfor).
# Grunndataene er generert og kan lages på nytt; rettelsene overlever. Operasjoner: sett (felt = verdi), skjul (bygg skjules med grunn).
rettelser = data.pop('rettelser', [])
for r in rettelser:
    emne, i, op = r['emne'], r.get('i'), r['op']
    if emne not in data or i is None or i >= len(data[emne]):
        raise SystemExit(f"rettelse peker på noe som ikke finnes: {r}")
    if op == 'sett':
        data[emne][i][r['felt']] = r['verdi']
    elif op == 'skjul':
        data[emne][i]['skjul'] = f"{r.get('hvem','?')} {r.get('dato','?')}: {r.get('grunn','')}"
    else:
        raise SystemExit(f"ukjent rettelse-operasjon: {op}")
# høyden er grunnlaget for alt som står på huset: endres h (rettelse), flyttes piper og arker like mye, og vinduer som ikke
# lenger får plass under gesimsen (overkant over h − 0,3 m) tas ut. Ellers svever pipene og vinduene sitter i taket (24.10).
grunn = json.loads(les('data/bygg.json'))
for i, x in enumerate(data['bygg']):
    h0, h1 = grunn[i].get('h', 0), x.get('h', 0); f = x.get('th', 0.82) / 0.82   # takhøyden skaleres med helningen
    if abs(h1 - h0) < 0.05 and abs(f - 1) < 0.01: continue
    flytt = lambda z: round(h1 + (z - h0) * f, 2) if z > h0 else round(z + h1 - h0, 2)   # over gesims: følger taket; under: følger veggen
    if x.get('piper'): x['piper'] = [[q[0], q[1], flytt(q[2])] + q[3:] for q in x['piper']]
    if x.get('arker'): x['arker'] = [[q[0], q[1], flytt(q[2])] + q[3:] for q in x['arker']]
    if x.get('vind'): x['vind'] = [v for v in x['vind'] if v[2] + v[8] / 2 <= x['h'] - 0.3]
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
