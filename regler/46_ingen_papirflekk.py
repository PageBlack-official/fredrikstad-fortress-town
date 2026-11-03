"""Regel (03.11, avvik A16): ingen papirfarget flekk på vollen ved Tell. Flekken (239,236,228) kom og gikk med én grads dreiing
(asimut 193 hvitt, 194 grønt). Tegner samme senter [158,-79], faktor 3, fra 193 og 194 og krever under 1 % papirfargede piksler
i midtfeltet (flekken ga 8 %). Kjøres i bygget enkel."""
import subprocess, os
from _felles import *
from PIL import Image
import numpy as np
ut = os.path.join(ROT, 'rapport', '_papirflekk'); os.makedirs(ut, exist_ok=True)
def andel(az):
    p = os.path.join(ut, f'az{az}.png')
    subprocess.run(['node', os.path.join(ROT, 'verktoy', 'bilde.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), p, str(az), '3', '158', '-79'],
                   capture_output=True, text=True, cwd=ROT, env={**os.environ, 'UI': '0'}, timeout=900)
    x = np.asarray(Image.open(p).convert('RGB')).astype(int); h, w, _ = x.shape
    r = x[int(h*.25):int(h*.75), int(w*.15):int(w*.6)]
    pap = (abs(r[..., 0]-236) < 14) & (abs(r[..., 1]-233) < 14) & (abs(r[..., 2]-225) < 16)
    return pap.mean()*100
a = {az: andel(az) for az in (193, 194)}
rapport('46_ingen_papirflekk', all(v < 1 for v in a.values()), [f'- asimut {az}: {v:.2f} % papirfarget i midtfeltet (krav under 1 %; flekken ga 8 %)' for az, v in a.items()])
