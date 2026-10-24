"""Regel (24.10): ytelsestrinn 2 (mobil som sliter) skal tegne det samme bildet som trinn 0, bare grovere. Vegar fanget på mobilen
at trekronene forsvant ved innzooming: trinn 2 kastet skyggekartet (dispose + null) og fikk det bygd på nytt, og da ble både skyggene
og kronene borte. Testen tegner et nærbilde på mobilflate med ?nivaa=0 og ?nivaa=2 og krever at kronegrønt og skyggemørkt er omtrent likt."""
import subprocess, os, re
from _felles import *
from PIL import Image
import numpy as np
ut = os.path.join(ROT, 'rapport', '_mobiltrinn'); os.makedirs(ut, exist_ok=True)
def tegn(nivaa):
    p = os.path.join(ut, f'nivaa{nivaa}.png')
    env = {**os.environ, 'MOBIL': '1', 'DPR': '2', 'EKSTRA': f'&nivaa={nivaa}'}
    for forsok in range(2):   # bilde-mobil venter selv til kameraet står; sjekkes likevel (mpp ≈ 0,11 m/px ved zoom 4)
        r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'bilde-mobil.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), p, '40', '4', '40', '-20', '390', '844'], capture_output=True, text=True, cwd=ROT, env=env)
        m = re.search(r'"mpp":([\d.]+)', r.stdout)
        if m and abs(float(m.group(1)) - 0.110) < 0.01: break
    return np.asarray(Image.open(p).convert('RGB')).astype(int)
def kroner(a): r, g, b = a[..., 0], a[..., 1], a[..., 2]; return int(((g > r + 20) & (g > b + 20) & (g > 90) & (g < 200)).sum())
a, b = tegn(0), tegn(2)
ka, kb = kroner(a), kroner(b)
avvik = abs(np.asarray(a) - np.asarray(b)).max(axis=2); store = int((avvik > 60).sum())
ok = kb >= 0.7 * ka and store < 0.03 * avvik.size
rapport('10_mobiltrinn_tegner_likt', ok, [f'- kronegrønt trinn 0: {ka} px, trinn 2: {kb} px', f'- piksler med avvik over 60: {store} av {avvik.size}'])
