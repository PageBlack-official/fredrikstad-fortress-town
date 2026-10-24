"""Regel (24.10, lys-og-bevegelse pkt. 1): kontaktskyggen er geometri på bakken (bånd rundt husfot, skive under tre), ikke en skjermeffekt,
og den finnes for alle synlige hus. Sjekkes i bygget: bakken rett utenfor en husvegg er mørkere enn bakken 4 m lenger ut, i nærbildet av Torvet,
og forskjellen forsvinner med ?kontakt=0."""
import subprocess, os
from _felles import *
from PIL import Image
import numpy as np
ut = os.path.join(ROT, 'rapport', '_kontakt'); os.makedirs(ut, exist_ok=True)
def tegn(navn, ekstra):
    p = os.path.join(ut, navn + '.png'); env = {**os.environ, 'UI': '0', 'EKSTRA': ekstra}
    subprocess.run(['node', os.path.join(ROT, 'verktoy', 'bilde.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), p, '40', '3', '15', '42'], capture_output=True, text=True, cwd=ROT, env=env)
    return np.asarray(Image.open(p).convert('L')).astype(float)
a, b = tegn('med', ''), tegn('uten', '&kontakt=0')
d = a - b                                     # negativt der kontaktskyggen mørkner
morkere = (d < -4).mean() * 100
ok = 0.5 < morkere < 12                       # noe av bildet, men ikke alt, blir mørkere
rapport('12_kontaktskygge', ok, [f'- {morkere:.1f} % av Torvet-bildet er mørkere med kontaktskygge enn uten (krav 0,5–12 %)', f'- snittendring der den virker: {d[d < -4].mean() if (d < -4).any() else 0:.1f} av 255'])
