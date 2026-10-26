"""Regel: bakkeflatene stemmer med ortofoto 2024 (Fredrikstad kommune, kilder/ortofoto-2024; hent med verktoy/flater.py hent).
- plener (grønt) har gress/vegetasjon under seg: minst 35 % grønt av det åpne (minus hus og parkering), eller feltet
  bekreftet (sett med egne øyne, med grunn i rettelsene: skygge, trær, blekt aprilgress)
- gresset i gårdsrommene er grønt i ortofotoet (minst 50 %), og det som er igjen som belagt, er ikke mest grønt (under 50 %)
- belagte flater (parkering, grus, heller, asfalt) er ikke grønne (under 30 %)
- hver parkeringsplass i kommunens lag med 10 plasser eller mer har en målt flate, eller en grunn i kilder/flater-maalt.json (uten_flate)
- advarsel (ikke feil): grønne felt over 60 m² inne i brosteinsflaten som kartet tegner som brostein
Bevis: rapport/15_flater.jpg (ortofoto, rødt = feil, gult = advarsel, grønt = plen/gress som kartet tegner, blått = parkering)."""
import os, sys, json, cv2, numpy as np
from _felles import *
sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import flater as F

if not os.path.exists(os.path.join(F.ORTO, 'ortofoto-2024.json')) or not any(f.endswith('.jpg') for f in os.listdir(F.ORTO)):
    rapport('15_flater', False, ['ortofotoet mangler: kjør python3 verktoy/flater.py hent (flisene ligger ikke i git, lisensen er ikke avklart)']); raise SystemExit
import datalag
d = datalag.alle(); hindre = F.hindre_paa_bakken(d)
X0, Y0, X1, Y1 = F.OMRAADE
inne = lambda p: all(X0 + 2 <= q[0] <= X1 - 2 and Y0 + 2 <= q[1] <= Y1 - 2 for q in p)
feil, adv, linjer, tegn = [], [], [], []   # tegn: (polygon, farge, tykkelse)
def andel(p, hin):
    a, _, m2 = F.maal_flate(p, hin); return a, m2

# plener
n = 0
for g in d['gront']:
    if g.get('skjul') or not inne(g['p']): continue
    a, m2 = andel(g['p'], hindre); n += 1
    ok = a >= 0.35 or m2 < 40
    tegn.append((g['p'], (60, 220, 60) if ok else (0, 200, 255) if g.get('bekreftet') else (0, 0, 255), 2))
    if not ok and g.get('bekreftet'): adv.append(f"- plen {g['id']}: {a:.0%} grønt, bekreftet med grunn i rettelsene")
    elif not ok: feil.append(f"- plen {g['id']} ({g['t'].get('name') or next(iter(g['t'].values()))}): {a:.0%} grønt av {m2:.0f} m²")
linjer.append(f"{n} plener innenfor ortofotoet målt")
# gårdsrom
for g in d['gardsrom']:
    if g.get('skjul'): continue
    gress = g.get('gress') if 'gress' in g else ([g['p']] if g['typ'] == 'gress' else [])
    for p in gress:
        a, m2 = andel(p, hindre)
        tegn.append((p, (60, 220, 60) if a >= 0.5 else (0, 0, 255), 1))
        if a < 0.5 and m2 >= 20: feil.append(f"- gårdsrom {g['id']}: gressflate på {m2:.0f} m² er bare {a:.0%} grønn")
    rest, _ = andel(g['p'], hindre + gress)
    if rest >= 0.5: feil.append(f"- gårdsrom {g['id']}: det som tegnes belagt, er {rest:.0%} grønt")
# belagte flater
for f in [x for x in d.get('flater', []) if x['typ'] != 'gress' and not x.get('skjul')] + [p for p in d.get('parkering', []) if p.get('p') and not p.get('skjul')]:
    hin = [b['p'] for b in d['bygg'] if b.get('p') and not b.get('skjul')]
    a, m2 = andel(f['p'], hin)
    ok = a < 0.3
    tegn.append((f['p'], (255, 120, 0) if ok else (0, 0, 255), 2))
    if not ok: feil.append(f"- {f['id']} ({f.get('navn') or f.get('typ')}): {a:.0%} grønt under en belagt flate")
# parkering mot kommunens lag
P = d.get('parkering', [])
mangler = [p for p in P if (p.get('antall') or 0) >= 10 and not p.get('p') and not p.get('uten_flate')]
for p in mangler: feil.append(f"- {p['id']} {p.get('navn')} ({p['antall']} plasser): ingen målt flate og ingen grunn")
linjer.append(f"parkering: {len(P)} plasser fra kommunens lag i området, {sum(1 for p in P if p.get('p'))} med målt flate "
              f"({sum(p.get('antall') or 0 for p in P if p.get('p'))} av {sum(p.get('antall') or 0 for p in P)} oppgitte plasser), "
              f"{sum(1 for p in P if p.get('uten_flate'))} uten flate med grunn")
# grønt inne i brosteinsflaten som tegnes som brostein
bro = d['brostein']; xs = [q[0] for q in bro]; ys = [q[1] for q in bro]; M = 0.5
im, px = F.ortofoto(min(xs) - 5, min(ys) - 5, max(xs) + 5, max(ys) + 5, M)
gr = F.gront_maske(im) & F._maske([bro], px, im.shape)
tegnet_gront = [g['p'] for g in d['gront'] if not g.get('skjul')] + [q for g in d['gardsrom'] if not g.get('skjul') for q in (g.get('gress') if 'gress' in g else ([g['p']] if g['typ'] == 'gress' else []))]
gr &= 1 - F._maske(hindre + tegnet_gront, px, im.shape)
gr = cv2.morphologyEx(gr, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
k, lab, st, sen = cv2.connectedComponentsWithStats(gr)
for i in range(1, k):
    m2 = st[i, cv2.CC_STAT_AREA] * M * M
    if m2 < 60: continue
    x = min(xs) - 5 + sen[i][0] * M; y = max(ys) + 5 - sen[i][1] * M
    adv.append(f"- grønt felt på {m2:.0f} m² ved ({x:.0f}, {y:.0f}) tegnes som brostein (trær over brostein, eller plen som mangler)")
    c, _ = cv2.findContours((lab == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tegn.append(([[min(xs) - 5 + (q[0][0] + .5) * M, max(ys) + 5 - (q[0][1] + .5) * M] for q in c[0]], (0, 220, 255), 2))
# bevisbilde
bim, bpx = F.ortofoto(-300, -360, 560, 460, 0.6)
for p, farge, t in tegn:
    cv2.polylines(bim, [np.array([bpx(*q[:2]) for q in p], np.int32)], True, farge, t, cv2.LINE_AA)
for p in P:
    if not p.get('p'): cv2.circle(bim, tuple(int(v) for v in bpx(p['x'], p['y'])), 4, (255, 255, 0) if p.get('uten_flate') or not (p.get('antall') or 0) >= 10 else (0, 0, 255), 1)
cv2.putText(bim, 'regel 15: ortofoto 2024 (Fredrikstad kommune, bare kontroll). Rodt = feil, gult = gront som tegnes som brostein', (8, bim.shape[0] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
bilde = 'rapport/15_flater.jpg'; cv2.imwrite(os.path.join(ROT, bilde), bim, [cv2.IMWRITE_JPEG_QUALITY, 80])
rapport('15_flater', not feil, [f"{len(feil)} avvik, {len(adv)} advarsler; " + linjer[0]] + linjer[1:] + [''] + (['Avvik:'] + feil if feil else []) + ([''] + ['Advarsler (bekreftede plener, og grønt som tegnes som brostein; sjekk i kontrollarkene rapport/flater/):'] + adv if adv else []), bilde)
