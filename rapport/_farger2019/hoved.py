"""Fargeregister fra 2019-brosjyren. Del A: hus med kvartaltegning (eksakt geometri). Del B: resten,
innpasset mot 2015-vektorflatene (samme tegning) og farget fra 2019-JPG-en.
Skriver soc/rapport/farger2019.json, farger2019.md, farger2019-kontrollark.png."""
import sys, os, json, math, collections
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HER)
sys.path.insert(0, os.path.join(HER, '..', '_farger'))
from felles2019 import *
import felles as F15
from shapely.geometry import Polygon, Point
from PIL import ImageDraw, ImageFont

UT = os.path.join(ROT, 'soc/rapport')
im19 = last_2019()
H19, W19 = im19.shape[:2]
b = last_bygg()
KV = json.load(open(os.path.join(HER, 'kvartal.json')))

# ---------- CMYK/RGB i kvartaltegningene -> 2019-RGB (oppslag fra de sikre prøvene, ellers naiv formel)
def bygg_oppslag():
    d = collections.defaultdict(list)
    for r in KV.values():
        for v in r['vegger'] + r['tak']:
            if v['farge2019'] and v['andel'] > 0.5 and v['px'] > 150:
                d[tuple(v['cmyk'])].append(v['farge2019'])
    tab = {}
    for c, l in d.items():
        arr = np.array(l)
        med = np.median(arr, axis=0)
        ok = [x for x in l if naer(x, med, 12)]
        if len(ok) >= 2 or (len(ok) == 1 and len(l) == 1 and naer(cmyk2rgb(c), med, 40)):
            tab[c] = tuple(int(v) for v in np.median(np.array(ok), axis=0))
    return tab

OPPSLAG = bygg_oppslag()


def kv_rgb(c):
    c = tuple(c)
    if c in OPPSLAG:
        return OPPSLAG[c], True
    return cmyk2rgb(c), False


def samme_kulor(a, b_, tol=0.06):
    v1 = np.array(a, float) / max(1, sum(a)); v2 = np.array(b_, float) / max(1, sum(b_))
    return np.abs(v1 - v2).max() <= tol


# ---------- Del A: kvartalhus
def flate_farge(v):
    """Beste farge for én flate: kvartalfarge K bekreftet av 2019, ellers 2019-dominant, ellers K.
    Returnerer (farge, status, K, vekt)."""
    K, sikker_k = kv_rgb(v['cmyk'])
    d = tuple(v['farge2019']) if v['farge2019'] else None
    if d and naer(d, K, 15):
        return d, 'enig', K, 1.0
    if d and v['andel'] >= 0.45 and v['px'] >= 120:
        return d, 'uenig-2019', K, 0.6
    if sikker_k:
        return K, 'uenig-kvartal', K, 0.3
    return (d if d else K), 'usikker', K, 0.2


def er_hvit(c):
    return min(c) > 225


def vurder_kvartal(bi, x):
    r = KV[str(bi)]
    # vegger: grupper etter retning, vektet med piksler
    grp = {'v': collections.Counter(), 'h': collections.Counter()}
    enig = uenig = 0
    for v in r['vegger']:
        col, status, K, vekt = flate_farge(v)
        if col is None:
            continue
        w = max(20, min(v['px'], 1500)) * vekt
        grp[v['retning']][col] += w
        if status == 'enig': enig += 1
        elif status.startswith('uenig'): uenig += 1
    kand = []
    for g in ('v', 'h'):
        kl = klynger(grp[g])
        if kl:
            kand.append(kl[0][0])
    vegg = veggs = None
    if len(kand) == 2:
        a, c = kand
        vegg, veggs = (a, c) if sum(a) >= sum(c) else (c, a)
        if naer(vegg, veggs, 10) or not samme_kulor(vegg, veggs, 0.08):
            # ulik kulør: to ulike hus i koblingen eller ulike materialer -> ta den med mest vekt
            tot = {k: sum(grp[g][k] for g in grp) for k in (a, c)}
            vegg = max(tot, key=tot.get); veggs = None
    elif len(kand) == 1:
        vegg = kand[0]
    # tak: vektet med kontakt*px
    tcnt = collections.Counter(); tenig = tuenig = 0
    for t in r['tak']:
        col, status, K, vekt = flate_farge(t)
        if col is None or er_hvit(col) and len(r['tak']) > 1 and any(not er_hvit(flate_farge(q)[0] or (255, 255, 255)) for q in r['tak']):
            continue
        tcnt[col] += max(5, min(t['px'], 2000)) * max(1.0, min(t['kontakt'], 40.0)) * vekt
        if status == 'enig': tenig += 1
        elif status.startswith('uenig'): tuenig += 1
    tk = klynger(tcnt)
    tak = taks = None
    if tk:
        tak = tk[0][0]
        for col, n in tk[1:]:
            if samme_kulor(tak, col) and sum(col) < sum(tak) - 30:
                taks = col; break
        if taks is None and sum(tak) < 450:
            # hovedflaten er mørk: er det skyggesiden? (skyggen trenger ikke ha samme kulør, jf. Infanterikasernen)
            for col, n in tk[1:]:
                if sum(col) > sum(tak) + 30 and n >= 0.25 * tk[0][1] and not er_hvit(col):
                    tak, taks = col, tak; break
    return vegg, veggs, tak, taks, {'vegg_enig': enig, 'vegg_uenig': uenig, 'tak_enig': tenig, 'tak_uenig': tuenig, 'n_vegg': len(r['vegger']), 'n_tak': len(r['tak'])}


def klynger(cnt, tol=8):
    ut = []
    for col, n in cnt.most_common():
        for k in ut:
            if naer(col, k[0], tol):
                k[1] += n; break
        else:
            ut.append([col, n])
    ut.sort(key=lambda k: -k[1])
    return [(tuple(c), n) for c, n in ut]


# ---------- Del B: 2015-vektorflatene som geometri, 2019 som farge
T = F15.Trykk()
M2T = Modell2Trykk(b)
H15, W15 = T.im.shape[:2]
lab = Image.new('I', (W15, H15), 0)
dr = ImageDraw.Draw(lab)
for i in sorted(range(len(T.polys)), key=lambda i: T.seq[i]):
    pg = T.polys[i]; f = T.fills[i]
    if pg.area < 400 or (max(f) < 110 and pg.area < 4000):
        continue
    for g in ([pg] if pg.geom_type == 'Polygon' else list(pg.geoms)):
        if g.area >= 400:
            dr.polygon([tuple(q) for q in g.exterior.coords], fill=i + 1)
LAB = np.asarray(lab, dtype=np.int32)
del lab


def er_bakgrunn15(c):
    r, g, bb = (int(v) for v in c)
    if max(r, g, bb) < 75: return True
    if g > r + 12 and g > bb + 4: return True
    if bb > r + 35: return True
    if abs(r - g) <= 8 and abs(g - bb) <= 8 and r >= bb and 85 <= r <= 140: return True
    if abs(r - 99) <= 6 and abs(g - 100) <= 6 and abs(bb - 102) <= 6: return True
    return False

BAK = np.array([True] + [er_bakgrunn15(f) for f in T.fills])
_farge_cache = {}


def flate2019(i):
    """2019-farge for 2015-flate i (1-basert etikett)."""
    if i in _farge_cache:
        return _farge_cache[i]
    pg = T.polys[i - 1]
    geoms = [pg] if pg.geom_type == 'Polygon' else list(pg.geoms)
    alle = []
    for g in geoms:
        p19 = px2019(np.array(g.exterior.coords))
        pix, n = median_i_polygon(im19, p19, inn=1.0)
        if pix is not None:
            alle.append(pix)
    if not alle:
        _farge_cache[i] = (None, 0.0); return _farge_cache[i]
    col, andel = dominant(np.concatenate(alle))
    _farge_cache[i] = (col, andel)
    return _farge_cache[i]


def idx_i(pts):
    pts = np.asarray(pts)
    x = np.clip(np.round(pts[:, 0]).astype(int), 0, W15 - 1)
    y = np.clip(np.round(pts[:, 1]).astype(int), 0, H15 - 1)
    return LAB[y, x]


def innpass(P, h):
    pg = Polygon(P)
    if not pg.is_valid: pg = pg.buffer(0)
    pts0 = np.array(F15.rutenett(pg, steg=max(6.0, min(12.0, math.sqrt(pg.area) / 8)), inn=3.0))
    best = None; R = 48; steg = 6
    for dy in range(-R - int(4 * h), R + 1, steg):
        for dx in range(-R, R + 1, steg):
            idx = idx_i(pts0 + (dx, dy)); hus = (idx > 0) & (~BAK[idx])
            sc = hus.mean() - 0.00006 * (dx * dx + dy * dy)
            if best is None or sc > best[2]: best = (dx, dy, sc, hus.mean())
    dx, dy = best[0], best[1]
    for ddy in range(-4, 5, 2):
        for ddx in range(-4, 5, 2):
            idx = idx_i(pts0 + (dx + ddx, dy + ddy)); hus = (idx > 0) & (~BAK[idx])
            sc = hus.mean() - 0.00006 * ((dx + ddx) ** 2 + (dy + ddy) ** 2)
            if sc > best[2]: best = (dx + ddx, dy + ddy, sc, hus.mean())
    return best, pts0


def synlige_kanter(P):
    pg = Polygon(P); ring = list(pg.exterior.coords)
    s = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:]))
    cw = s < 0; ut = []
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        ex, ey = x1 - x0, y1 - y0; L = math.hypot(ex, ey)
        if L < 6: continue
        nx, ny = (ey, -ex) if cw else (-ey, ex)
        if ny > 0.25 * L: ut.append(((x0, y0), (x1, y1), L, (nx / L, ny / L)))
    return ut


def vegg_sample(P, h, takidx):
    kanter = synlige_kanter(P)
    grp = {'v': collections.Counter(), 'h': collections.Counter()}
    for (x0, y0), (x1, y1), L, (nx, ny) in kanter:
        g = 'v' if nx < 0 else 'h'
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
            mx, my = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
            run = collections.Counter(); bak = 0
            for d in range(2, 2 + int(14 * h) + 40, 2):
                yy = int(my + d); xx = int(mx)
                if not (0 <= yy < H15 and 0 <= xx < W15): break
                idx = int(LAB[yy, xx])
                if idx == 0 or BAK[idx]:
                    bak += 1
                    if sum(run.values()) >= 3 or bak > 6: break
                    continue
                if idx in takidx:
                    if sum(run.values()) >= 3: break
                    continue
                run[idx] += 1
            if run:
                grp[g][run.most_common(1)[0][0]] += L / 10.0
    return grp


def vurder_fallback(i, x):
    P = M2T.px(x['p'])
    c0 = P.mean(axis=0)
    if not (0 <= c0[0] < W15 and 0 <= c0[1] < H15 * 0.83):
        return None, {'merknad': 'ikke i trykket (utenfor arket)', 'px2019': [int(v) for v in px2019(c0)]}
    best, pts0 = innpass(P, x['h'])
    dx, dy, sc, dekning = best
    Pa = P + (dx, dy)
    idx = idx_i(pts0 + (dx, dy))
    cnt = collections.Counter(int(j) for j in idx if j > 0 and not BAK[j])
    px19 = [int(v) for v in px2019(Pa.mean(axis=0))]
    if dekning < 0.35 or not cnt:
        return None, {'merknad': 'ikke i trykket (ingen husflate der fotavtrykket lander)', 'px2019': px19, 'dekning': round(float(dekning), 2)}
    # takflater = flatene med flest punkter; 2019-farge per flate
    tcnt = collections.Counter()
    takidx = set()
    for j, n in cnt.most_common(4):
        col, andel = flate2019(j)
        if col is None: continue
        takidx.add(j); tcnt[col] += n
    tk = klynger(tcnt)
    if not tk:
        return None, {'merknad': 'ikke i trykket (takflaten uleselig i 2019)', 'px2019': px19, 'dekning': round(float(dekning), 2)}
    tak = tk[0][0]; taks = None
    for col, n in tk[1:]:
        if samme_kulor(tak, col) and sum(col) < sum(tak) - 30 and n >= 0.12 * sum(k[1] for k in tk):
            taks = col; break
    if taks is None and sum(tak) < 450 and len(tk) > 1 and samme_kulor(tak, tk[1][0]) and sum(tk[1][0]) > sum(tak) + 30 and tk[1][1] >= 0.12 * sum(k[1] for k in tk):
        tak, taks = tk[1][0], tak
    grp = vegg_sample(Pa, x['h'], takidx)
    kand = []
    for g in ('v', 'h'):
        c2 = collections.Counter()
        for j, w in grp[g].items():
            col, andel = flate2019(j)
            if col is not None: c2[col] += w
        kl = klynger(c2)
        if kl: kand.append(kl[0][0])
    vegg = veggs = None
    if len(kand) == 2:
        a, c = kand
        vegg, veggs = (a, c) if sum(a) >= sum(c) else (c, a)
        if naer(vegg, veggs, 10) or not samme_kulor(vegg, veggs): veggs = None
    elif len(kand) == 1:
        vegg = kand[0]
    merk = []; sik = 'middels'
    if dekning < 0.6: merk.append('bare %d%% av fotavtrykket på husflate' % round(100 * dekning)); sik = 'lav'
    if math.hypot(dx, dy) > 40: merk.append('flyttet %d px (2015-px) for å treffe huset' % round(math.hypot(dx, dy))); sik = 'lav'
    if vegg is None: merk.append('ingen synlig vegg funnet'); sik = 'lav'
    return (vegg, veggs, tak, taks), {'px2019': px19, 'dekning': round(float(dekning), 2), 'sikkerhet': sik, 'merknad': '; '.join(merk) if merk else 'fotavtrykk innpasset mot 2015-vektor, farge lest i 2019'}


# ---------- kjør
forslag = {}
stat = collections.Counter()
for i, x in enumerate(b):
    key = str(i)
    if x.get('skjul'):
        forslag[key] = {'vegg': None, 'tak': None, 'veggs': None, 'taks': None, 'kilde': None, 'sikkerhet': 'lav', 'px2019': None, 'merknad': 'ikke i trykket (skjult: %s)' % x['skjul']}
        stat['skjult'] += 1; continue
    if not x.get('p'):
        forslag[key] = {'vegg': None, 'tak': None, 'veggs': None, 'taks': None, 'kilde': None, 'sikkerhet': 'lav', 'px2019': None, 'merknad': 'ikke i trykket (uten fotavtrykk)'}
        stat['uten p'] += 1; continue
    rec = None
    if key in KV:
        vegg, veggs, tak, taks, info = vurder_kvartal(i, x)
        c0 = M2T.px(np.mean(x['p'], axis=0)); px19 = [int(v) for v in px2019(c0)]
        merk = []
        kilde = '2019+kvartaltegning'
        if info['vegg_uenig'] > info['vegg_enig']:
            merk.append('vegg: 2019 og kvartaltegning uenige på %d av %d flater; 2019 valgt der den er tydelig' % (info['vegg_uenig'], info['n_vegg']))
        if tak is None:
            # tak via fallback
            fb, finfo = vurder_fallback(i, x)
            if fb and fb[2]:
                tak, taks = fb[2], fb[3]; merk.append('tak fra innpassing (ingen takflate grenser til veggen i kvartaltegningen)')
                kilde = '2019'
            else:
                merk.append('tak ikke funnet')
        elif info['tak_uenig'] > info['tak_enig']:
            merk.append('tak: 2019 og kvartaltegning uenige på %d av %d flater' % (info['tak_uenig'], info['n_tak']))
        sik = 'høy'
        if tak is None or vegg is None: sik = 'lav'
        elif merk: sik = 'middels'
        elif info['vegg_enig'] == 0 and info['tak_enig'] == 0: sik = 'middels'; merk.append('ingen flate der 2019 og kvartaltegning er enige')
        rec = {'vegg': list(vegg) if vegg else None, 'tak': list(tak) if tak else None, 'veggs': list(veggs) if veggs else None, 'taks': list(taks) if taks else None,
               'kilde': kilde, 'sikkerhet': sik, 'px2019': px19, 'merknad': '; '.join(merk) if merk else 'kvartaltegningens flater lagt på 2019-bildet; farger enige'}
        stat['kvartal'] += 1
    else:
        fb, finfo = vurder_fallback(i, x)
        if fb is None:
            rec = {'vegg': None, 'tak': None, 'veggs': None, 'taks': None, 'kilde': None, 'sikkerhet': 'lav', 'px2019': finfo.get('px2019'), 'merknad': finfo['merknad']}
            stat['ikke i trykket'] += 1
        else:
            vegg, veggs, tak, taks = fb
            rec = {'vegg': list(vegg) if vegg else None, 'tak': list(tak) if tak else None, 'veggs': list(veggs) if veggs else None, 'taks': list(taks) if taks else None,
                   'kilde': '2019', 'sikkerhet': finfo['sikkerhet'], 'px2019': finfo['px2019'], 'merknad': finfo['merknad']}
            stat['fallback'] += 1
    forslag[key] = rec

# ---------- skyggetoner fra palettpar: der tak/vegg er funnet uten skygge, bruk paret som er vanligst for samme lysfarge
def palettpar(felt, sfelt):
    par = collections.defaultdict(collections.Counter)
    for r in forslag.values():
        if r.get(felt) and r.get(sfelt):
            par[tuple(r[felt]) // 1 if False else tuple(r[felt])][tuple(r[sfelt])] += 1
    # slå sammen nøkler innen ±8
    ut = []
    for k, c in par.items():
        for u in ut:
            if naer(k, u[0], 8):
                u[1].update(c); break
        else:
            ut.append([k, collections.Counter(c)])
    return [(k, c.most_common(1)[0][0], sum(c.values()), c.most_common(1)[0][1]) for k, c in ut]

for felt, sfelt in (('tak', 'taks'), ('vegg', 'veggs')):
    par = palettpar(felt, sfelt)
    for r in forslag.values():
        if r.get(felt) and not r.get(sfelt):
            for k, sk, n, nk in par:
                if n >= 3 and nk >= 0.6 * n and naer(r[felt], k, 8):
                    r[sfelt] = list(sk)
                    r['merknad'] += '; %s utledet fra palettpar (%d hus)' % (sfelt, n)
                    break

json.dump(forslag, open(os.path.join(UT, 'farger2019.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({str(k): v for k, v in OPPSLAG.items()}, open(os.path.join(HER, 'cmyk-oppslag.json'), 'w'), indent=1)
print(stat)

# ---------- kalibrering
def kal(tol=15):
    nt = tt = nv = tv = 0; strict_t = 0
    for i, x in enumerate(b):
        r = forslag[str(i)]
        if x.get('taks') and x.get('tak') and r.get('tak'):
            nt += 1
            if naer(r['tak'], x['tak'], tol) or naer(r['tak'], x['taks'], tol) or (r.get('taks') and (naer(r['taks'], x['taks'], tol) or naer(r['taks'], x['tak'], tol))): tt += 1
            if naer(r['tak'], x['tak'], tol): strict_t += 1
        if x.get('veggs') and x.get('vegg') and r.get('vegg'):
            nv += 1
            if naer(r['vegg'], x['vegg'], tol) or naer(r['vegg'], x['veggs'], tol) or (r.get('veggs') and (naer(r['veggs'], x['veggs'], tol) or naer(r['veggs'], x['vegg'], tol))): tv += 1
    return nt, tt, strict_t, nv, tv

for tol in (12, 15):
    nt, tt, st, nv, tv = kal(tol)
    print('tol', tol, 'tak %d/%d = %.0f%% (streng tak=tak: %.0f%%)  vegg %d/%d = %.0f%%' % (tt, nt, 100 * tt / max(1, nt), 100 * st / max(1, nt), tv, nv, 100 * tv / max(1, nv)))
# per kilde
for kilde in ('2019+kvartaltegning', '2019'):
    nt = tt = 0
    for i, x in enumerate(b):
        r = forslag[str(i)]
        if r.get('kilde') == kilde and x.get('taks') and r.get('tak'):
            nt += 1
            if naer(r['tak'], x['tak'], 15) or naer(r['tak'], x['taks'], 15) or (r.get('taks') and naer(r['taks'], x['taks'], 15)): tt += 1
    print(kilde, 'tak', tt, '/', nt)
print(collections.Counter(r['sikkerhet'] for r in forslag.values()))
