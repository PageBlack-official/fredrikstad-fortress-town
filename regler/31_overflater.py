"""Regel: overflatene i Gamlebyen (innenfor vollene og vollene selv) stemmer med ortofoto 2024 og kommunekartet.
Måles per piksel (0,25 m) der ortofotoet ser bakken (ikke hus, trekrone, skygge, takutstikk, vann):
  - gruppe (belagt / grønt / bed) i modellens bakke ovenfra = gruppen i fotoet: krav >= 95 %
  - type på belagt mark (brostein / asfalt / grus) = typen klassifisert fra fotoet: krav >= 95 %
  - prøvepunktene dømt med øyet i ortofotoet (kilder/bakke-maalt.json «prover»): modellens type = dommen, krav >= 95 %
  - dekning: hele Gamlebyen er tegnet (ingen bar bakgrunn utenfor hus og vann): krav >= 99 %
Fasit og modell kommer fra verktoy/bakke.py (bakkekart, modell). Bevis: rapport/31_overflater.jpg (ikke i git: ortofotoet),
rødt = modellen har annen gruppe enn fotoet, gult = annen belagt type."""
import os, sys, cv2, numpy as np
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy')); sys.path.insert(0, ROT)
import bakke as B, datalag
if not os.path.exists(os.path.join(B.F.ORTO, 'ortofoto-2024.json')) or not os.path.exists(B.KK.PDF):
    rapport('31_overflater', False, ['ortofotoet eller kommunekartet mangler lokalt (verktoy/flater.py hent; kommunekart.pdf fra Vegar)']); raise SystemExit
d = datalag.alle(); dom = B.domene(); R = B.ramme(dom); M = B.MPP
fk, f, _ = B.bakkekart(d, R, M)
m = B.modell(R, M, d)
inn = B.maske([dom], R, M) > 0
gf, gm = B.gruppe(fk), B.gruppe(m)
s = inn & (f['sett'] > 0) & (gf != 5) & (gm != 5) & (gf != 4) & (gm != 4) & (gf > 0) & (gm > 0)
enig = (gf == gm) & s
a_gr = enig.sum() / max(1, s.sum())
bb = s & (gf == 1) & (gm == 1)
tm = m.copy(); tm[tm == B.K['belagt']] = B.K['brostein']   # veibånd uten flatetype = brostein (grunnen i byen)
et = bb & (fk == tm)
a_ty = et.sum() / max(1, bb.sum())
# prøvepunktene
pr = B.maalt().get('prover', [])
treff = []
for x, y, typ in pr:
    r, c = int((R[3] - y) / M), int((x - R[0]) / M)
    mv = int(tm[r, c]); mt = B.NAVN.get(mv, '?')
    ok = (mt == typ) or (typ in ('gress', 'plen') and mt in ('gress', 'plen'))
    treff.append((ok, x, y, typ, mt))
a_pr = sum(t[0] for t in treff) / max(1, len(treff))
# dekning
bunn = inn & (fk != B.K['hus']) & (fk != B.K['vann'])
a_dk = (bunn & (m != 0)).sum() / max(1, bunn.sum())
# per gruppe
navn = {1: 'belagt', 2: 'grønt', 3: 'bed'}
tab = []
for a in (1, 2, 3):
    n = (s & (gf == a)).sum()
    if n: tab.append(f"- fotoet {navn[a]}: {n * M * M:.0f} m², modellen enig {((s & (gf == a) & (gm == a)).sum() / n):.1%}"
                     + ''.join(f", {navn[b]} {((s & (gf == a) & (gm == b)).sum() * M * M):.0f} m²" for b in (1, 2, 3) if b != a and (s & (gf == a) & (gm == b)).any()))
ok = a_gr >= 0.95 and a_ty >= 0.95 and a_pr >= 0.95 and a_dk >= 0.99
lin = [f"gruppe {a_gr:.1%} (krav 95 %), belagt type {a_ty:.1%} (krav 95 %), prøvepunkter {a_pr:.0%} av {len(treff)} (krav 95 %), dekning {a_dk:.2%} (krav 99 %)",
       f"målt på {s.sum() * M * M:.0f} m² bakke som ortofotoet ser, i Gamlebyen ({inn.sum() * M * M:.0f} m² med hus og vann)", ''] + tab
bom = [t for t in treff if not t[0]]
if bom: lin += ['', 'Prøvepunkter der modellen bommer (x, y, dømt, modell):'] + [f"- ({x:.1f}, {y:.1f}) {t} / {mt}" for _, x, y, t, mt in bom]
# bevis
im = (f['orto'] * 0.6).astype(np.uint8)
im[s & ~enig] = (0, 0, 255); im[bb & ~et] = (0, 220, 255)
im = cv2.resize(im, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
cv2.putText(im, 'regel 31: rodt = annen gruppe enn ortofotoet, gult = annen belagt type (ortofoto 2024, bare kontroll)', (8, im.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
cv2.imwrite(os.path.join(ROT, 'rapport', '31_overflater.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 80])
rapport('31_overflater', ok, lin, 'rapport/31_overflater.jpg')
