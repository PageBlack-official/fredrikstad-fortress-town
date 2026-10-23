"""Fargeregister fra trykkfila (vektor, metode A) med lokal innpassing per hus."""
import sys, os, json, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from felles import *
from PIL import ImageDraw

UT = os.path.join(ROT, 'soc/rapport')
T = Trykk(); b = last_bygg()
korr, pairs = lag_korreksjon(T, b)
H, W = T.im.shape[:2]

# ---- 1. etikettbilde: hver piksel -> flateindeks (øverste), små/mørke flater (vinduer, streker) utelatt
lab = Image.new('I', (W, H), 0)
dr = ImageDraw.Draw(lab)
order = sorted(range(len(T.polys)), key=lambda i: T.seq[i])
for i in order:
    pg = T.polys[i]; f = T.fills[i]
    if pg.area < 400: continue
    if max(f) < 110 and pg.area < 4000: continue
    geoms = [pg] if pg.geom_type == 'Polygon' else list(pg.geoms)
    for g in geoms:
        if g.area < 400: continue
        dr.polygon([tuple(q) for q in g.exterior.coords], fill=i + 1)
        for ring in g.interiors:  # hull tegnes ikke; godt nok for flate husflater
            pass
LAB = np.asarray(lab, dtype=np.int32)
FILL = np.array([(0, 0, 0)] + T.fills, dtype=np.int16)


def er_bakgrunn(c):
    r, g, bb = (int(v) for v in c)
    if max(r, g, bb) < 75: return True                       # svart/strek
    if g > r + 12 and g > bb + 4: return True                 # grønt (plen, trær)
    if bb > r + 35: return True                               # vann
    if abs(r - g) <= 8 and abs(g - bb) <= 8 and r >= bb and 85 <= r <= 140: return True  # varm/nøytral gategrå
    if abs(r - 99) <= 6 and abs(g - 100) <= 6 and abs(bb - 102) <= 6: return True       # mørk gate
    return False


BAKGRUNN = np.array([True] + [er_bakgrunn(f) for f in T.fills])


def farger_i(pts):
    """Flate-indekser i punktene (0 = ingen)."""
    pts = np.asarray(pts)
    x = np.clip(np.round(pts[:, 0]).astype(int), 0, W - 1)
    y = np.clip(np.round(pts[:, 1]).astype(int), 0, H - 1)
    return LAB[y, x]


def klynger(cnt, tol=8):
    """Slår sammen farger innen ±tol; returnerer [(farge, antall)] sortert."""
    ut = []
    for col, n in cnt.most_common():
        for k in ut:
            if naer(col, k[0], tol):
                k[1] += n; break
        else:
            ut.append([col, n])
    ut.sort(key=lambda k: -k[1])
    return [(tuple(c), n) for c, n in ut]


def innpass(P, h):
    """Søk translasjon (dx,dy) som legger fotavtrykket på husflater. Returnerer (dx,dy,score,pts)."""
    pg = Polygon(P)
    if not pg.is_valid: pg = pg.buffer(0)
    pts0 = np.array(rutenett(pg, steg=max(6.0, min(12.0, math.sqrt(pg.area) / 8)), inn=3.0))
    best = None
    R = 48; steg = 6
    for dy in range(-R - int(4 * h), R + 1, steg):      # trykket kan ligge både over og under
        for dx in range(-R, R + 1, steg):
            idx = farger_i(pts0 + (dx, dy))
            hus = (idx > 0) & (~BAKGRUNN[idx])
            sc = hus.mean() - 0.00006 * (dx * dx + dy * dy)
            if best is None or sc > best[2]:
                best = (dx, dy, sc, hus.mean())
    dx, dy = best[0], best[1]
    # finjustering ±4
    for ddy in range(-4, 5, 2):
        for ddx in range(-4, 5, 2):
            idx = farger_i(pts0 + (dx + ddx, dy + ddy))
            hus = (idx > 0) & (~BAKGRUNN[idx])
            sc = hus.mean() - 0.00006 * ((dx + ddx) ** 2 + (dy + ddy) ** 2)
            if sc > best[2]:
                best = (dx + ddx, dy + ddy, sc, hus.mean())
    return best, pts0


def synlige_kanter(P):
    """Kanter med utovervendt normal som peker nedover i bildet (mot betrakteren)."""
    pg = Polygon(P)
    ring = list(pg.exterior.coords)
    # orientering: shapely exterior kan være begge veier; bruk signert areal
    s = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]): s += x0 * y1 - x1 * y0
    cw = s < 0  # i bildekoordinater (y ned) er "cw" i skjermen = positiv i matte
    ut = []
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        ex, ey = x1 - x0, y1 - y0
        L = math.hypot(ex, ey)
        if L < 6: continue
        nx, ny = (ey, -ex) if cw else (-ey, ex)   # utover
        if ny > 0.25 * L:                          # peker nedover
            ut.append(((x0, y0), (x1, y1), L, (nx / L, ny / L)))
    return ut


def vegg_sample(P, h, takfarger):
    """Farger på veggflatene under de synlige kantene: gå nedover fra kanten, hopp over takfargene,
    ta første løp av en annen husfarge (vinduer/streker hoppes over). Gruppert i to retninger."""
    kanter = synlige_kanter(P)
    grp = {'v': collections.Counter(), 'h': collections.Counter()}
    for (x0, y0), (x1, y1), L, (nx, ny) in kanter:
        g = 'v' if nx < 0 else 'h'
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
            mx, my = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
            run = collections.Counter(); bak = 0; forbi_tak = False
            for d in range(2, 2 + int(14 * h) + 40, 2):
                yy = int(my + d); xx = int(mx)
                if not (0 <= yy < H and 0 <= xx < W): break
                idx = int(LAB[yy, xx])
                if idx == 0 or BAKGRUNN[idx]:
                    bak += 1
                    if sum(run.values()) >= 3 or bak > 6: break
                    continue
                f = tuple(int(v) for v in FILL[idx])
                if any(naer(f, tf, 10) for tf in takfarger):
                    if sum(run.values()) >= 3: break   # ny takflate under veggen = nabohus
                    forbi_tak = True; continue
                run[f] += 1
            if run:
                col = run.most_common(1)[0][0]
                grp[g][col] += L / 10.0
    return grp


ROOF_HINT = None
forslag = {}
treff_tak = treff_vegg = n_kal_tak = n_kal_vegg = 0
for i, x in enumerate(b):
    if x.get('skjul'):
        forslag[str(i)] = {'merknad': 'skjult (' + x['skjul'] + ')', 'sikkerhet': 'lav'}
        continue
    P = np.array([korr(q) for q in T.px(x['p'])])
    c0 = P.mean(axis=0)
    if not (0 <= c0[0] < W and 0 <= c0[1] < H * 0.83):
        forslag[str(i)] = {'merknad': 'ikke i trykket (utenfor arket)', 'sikkerhet': 'lav', 'px': [round(float(c0[0])), round(float(c0[1]))]}
        continue
    best, pts0 = innpass(P, x['h'])
    dx, dy, sc, dekning = best
    Pa = P + (dx, dy)
    idx = farger_i(pts0 + (dx, dy))
    cnt = collections.Counter()
    for j in idx:
        if j > 0 and not BAKGRUNN[j]:
            cnt[tuple(int(v) for v in FILL[j])] += 1
    kl = klynger(cnt)
    rec = {'px': [round(float(Pa[:, 0].mean())), round(float(Pa[:, 1].mean()))], 'skift': [int(dx), int(dy)], 'dekning': round(float(dekning), 2)}
    if dekning < 0.35 or not kl:
        rec.update({'merknad': 'ikke i trykket (ingen husflate der fotavtrykket lander; skjult bak trær/andre hus eller ikke tegnet)', 'sikkerhet': 'lav'})
        forslag[str(i)] = rec
        continue
    tak = kl[0][0]
    taks = None
    for col, n in kl[1:]:
        v1 = np.array(tak, float) / max(1, sum(tak)); v2 = np.array(col, float) / max(1, sum(col))
        if n >= 0.12 * sum(k[1] for k in kl) and sum(col) < sum(tak) - 30 and np.abs(v1 - v2).max() <= 0.06:
            taks = col; break
    if taks is None and sum(kl[0][0]) < 450 and len(kl) > 1 and sum(kl[1][0]) > sum(tak) + 30 and kl[1][1] >= 0.12 * sum(k[1] for k in kl):
        tak, taks = kl[1][0], kl[0][0]   # hovedflaten er skyggesiden (som Tøihuset)
    grp = vegg_sample(Pa, x['h'], [tak] + ([taks] if taks else []))
    kv = klynger(grp['v']); kh = klynger(grp['h'])
    vegg = veggs = None
    cand = [k[0][0] for k in (kv, kh) if k]
    if len(cand) == 2:
        a, bb_ = cand
        vegg, veggs = (a, bb_) if sum(a) >= sum(bb_) else (bb_, a)
        if naer(vegg, veggs, 10): veggs = None
        elif veggs is not None:
            # samme kulør? sammenlign normaliserte kanaler
            v1 = np.array(vegg, float) / max(1, sum(vegg)); v2 = np.array(veggs, float) / max(1, sum(veggs))
            if np.abs(v1 - v2).max() > 0.06: veggs = None
    elif len(cand) == 1:
        vegg = cand[0]
    # veggfargen skal ikke være takfargen (fotavtrykk-feil); flagg
    merk = []
    sik = 'høy'
    if dekning < 0.6: sik = 'middels'; merk.append('bare %d%% av fotavtrykket på husflate' % round(100 * dekning))
    if math.hypot(dx, dy) > 40: sik = 'middels' if sik == 'høy' else 'lav'; merk.append('flyttet %d px for å treffe huset' % round(math.hypot(dx, dy)))
    if kl[0][1] < 0.5 * sum(k[1] for k in kl): merk.append('takflaten er ikke ensfarget i trykket (%s)' % ', '.join('%s×%d' % (k[0], k[1]) for k in kl[:3]))
    if vegg is None: merk.append('ingen synlig vegg funnet'); sik = 'lav' if sik == 'lav' else 'middels'
    rec.update({'tak': list(tak), 'sikkerhet': sik})
    if taks: rec['taks'] = list(taks)
    if vegg: rec['vegg'] = list(vegg)
    if veggs: rec['veggs'] = list(veggs)
    rec['merknad'] = '; '.join(merk) if merk else 'lest av trykket'
    forslag[str(i)] = rec
    # kalibrering mot dagens trykkfarger (veggs/taks finnes)
    if x.get('taks'):
        n_kal_tak += 1
        if naer(tak, x['tak']) or naer(tak, x['taks']) or (taks and (naer(taks, x['taks']) or naer(taks, x['tak']))): treff_tak += 1
    if x.get('veggs') and vegg:
        n_kal_vegg += 1
        if naer(vegg, x['vegg']) or naer(vegg, x['veggs']) or (veggs and (naer(veggs, x['veggs']) or naer(veggs, x['vegg']))): treff_vegg += 1

json.dump(forslag, open(os.path.join(UT, 'farger.forslag.json'), 'w'), ensure_ascii=False, indent=1)
print('kalibrering tak %d/%d = %.0f%%' % (treff_tak, n_kal_tak, 100 * treff_tak / max(1, n_kal_tak)))
print('kalibrering vegg %d/%d = %.0f%%' % (treff_vegg, n_kal_vegg, 100 * treff_vegg / max(1, n_kal_vegg)))
print('med tak', sum(1 for r in forslag.values() if 'tak' in r), 'uten', sum(1 for r in forslag.values() if 'tak' not in r))
print(collections.Counter(r['sikkerhet'] for r in forslag.values()))
