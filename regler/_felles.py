"""Felles for regelsjekkene: last data, modell->flyfoto-piksel, rapportlinje."""
import json, os, math
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def data(navn, raa=False):
    """Data slik kartet viser dem: rettelser.json legges oppå (samme regler som bygg.py). raa=True gir grunndataene."""
    d = json.load(open(os.path.join(ROT, 'data', navn + '.json'), encoding='utf8'))
    if raa or navn == 'rettelser': return d
    for r in json.load(open(os.path.join(ROT, 'data', 'rettelser.json'), encoding='utf8')):
        if r['emne'] != navn: continue
        if r['op'] == 'sett': d[r['i']][r['felt']] = r['verdi']
        elif r['op'] == 'skjul': d[r['i']]['skjul'] = f"{r.get('hvem','?')} {r.get('dato','?')}: {r.get('grunn','')}"
    return d
def flyfoto():
    import cv2
    k = json.load(open(os.path.join(ROT, 'kilder', 'flyfoto-google-2026-10-23.json')))
    im = cv2.imread(os.path.join(ROT, 'kilder', 'flyfoto-google-2026-10-23.jpg'))
    a = k['anker']; ax, ay = a['px']; kx, ky = a['modell_xy']; mpp = a['m_per_px_oversikt']; F = a['forstorrelse']; O = a['forskyvning']
    def px(x, y): return (F * (ax + (x - kx) / mpp) + O, F * (ay - (y - ky) / mpp) + O)
    return im, px
def gamleby(b): return [(i, x) for i, x in enumerate(b) if x.get('gml')]
def rapport(navn, ok, linjer, bilde=None):
    os.makedirs(os.path.join(ROT, 'rapport'), exist_ok=True)
    with open(os.path.join(ROT, 'rapport', navn + '.md'), 'w', encoding='utf8') as f:
        f.write(f"# {navn}: {'OK' if ok else 'FEIL'}\n\n" + '\n'.join(linjer) + ('\n\nBevis: ' + bilde if bilde else '') + '\n')
    print(('OK   ' if ok else 'FEIL ') + navn + ('  (' + linjer[0] + ')' if linjer else ''))
    return ok
