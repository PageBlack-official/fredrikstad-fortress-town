"""Regel: hvert bygg i Gamlebyen skal ha en bygning under seg i flyfoto. Bygg uten skal ha skjul-feltet med grunn, eller bekreftet-feltet
(sett med egne øyne: huset står der, men er dekket av trær eller flyfotoet er forskjøvet), også med grunn.
Måler andel vegetasjon og åpen bakke under fotavtrykket; lager kontaktark som bevis."""
import cv2, numpy as np, math
from _felles import *
b = data('bygg'); im, px = flyfoto(); H, W = im.shape[:2]; hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
feil = []; fliser = []
for i, x in gamleby(b):
    P = np.array([px(*q) for q in x['p']], np.int32); m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [P], 1)
    if m.sum() < 10: continue
    h, s = hsv[..., 0][m == 1], hsv[..., 1][m == 1]
    gront = float(((h > 30) & (h < 90) & (s > 60)).mean())
    if gront > 0.45 and not x.get('skjul') and not x.get('bekreftet'):   # bekreftet = sett av menneske/Claude i flyfoto, med grunn i rettelser.json
        feil.append(f"- bygg {i} ({x.get('navn') or x.get('type')}): {int(gront*100)} % vegetasjon under fotavtrykket, ikke skjult")
        c = px(x['r'][0], x['r'][1]); R = 80; x0, y0 = int(c[0] - R), int(c[1] - R); fl = im[y0:y0 + 2 * R, x0:x0 + 2 * R].copy()
        cv2.polylines(fl, [P - [x0, y0]], True, (0, 80, 255), 2); cv2.putText(fl, str(i), (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1); fliser.append(cv2.resize(fl, (200, 200)))
skjulte = [f"- bygg {i} skjult: {x['skjul']}" for i, x in gamleby(b) if x.get('skjul')]
bilde = None
if fliser:
    ark = np.full((math.ceil(len(fliser) / 6) * 200, 1200, 3), 255, np.uint8)
    for k, t in enumerate(fliser): ark[(k // 6) * 200:(k // 6) * 200 + 200, (k % 6) * 200:(k % 6) * 200 + 200] = t
    bilde = 'rapport/01_bygg_finnes.png'; cv2.imwrite(os.path.join(ROT, bilde), ark)
rapport('01_bygg_finnes', not feil, [f"{len(feil)} bygg med vegetasjon under seg som ikke er skjult; {len(skjulte)} skjult med grunn"] + feil + [''] + skjulte, bilde)
