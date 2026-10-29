#!/usr/bin/env python3
"""Målte bygghøyder for Gamlebyen fra Kartverkets høydemodeller (DOM1 - DTM1), sammenlignet med 3D-kartet.

Kjør:  python3 rapport/hoyder/hent.py            (fra soc/)
       python3 rapport/hoyder/hent.py --ny        (laster ned DOM/DTM på nytt)

Leser data/bygg.json (rører den ikke), skriver til rapport/hoyder/:
  kilder/dom1_25832.tif, kilder/dtm1_25832.tif   rådata fra Kartverkets WCS (CC BY 4.0)
  hoyder.json, kontrollark.png, tall.json (mellomtall til rapporten)

Metode
  1. Modellmeter -> lon/lat (Web Mercator-skala ved origo, slik src/00_oppsett.js gjør) -> UTM 32N (EPSG:25832, WCS-ets egen projeksjon).
  2. DOM og DTM 1 m hentes én gang for hele Gamlebyen (+60 m kant) og lagres som GeoTIFF.
  3. Origo er bare kjent til ±3 m (KILDER.md). Forskyvningen finnes ved å flytte alle omriss rundt i 0,5 m-steg og velge den som
     best treffer pikslene med DOM-DTM > 3 m. Forskyvningen brukes for alle hus.
  4. For hvert hus: piksler med senter inne i omrisset krympet 1 m (0,5 m / 0 m for små hus, flagget). p50 og p90 av DOM-DTM.
  5. Kartets egen overflate regnes ut piksel for piksel på samme måte som 07_vinduer-dører-og-porter.js bygger taket:
     vegg h + takflatens z * 0,82 (tak2), min(z*0,82, 7,5) (sk), saltak-prisme rise=min(kortside*0,48, 7,5) (tk/r),
     pyramide for deler, og kirka som i 06_kirka (vegg 9,5, møne +8,2, tårn 34). Så p50 og p90 av kartets overflate.
  6. Kalibrering på husene med pålitelig tegnet høyde: målt = a*kart + b (p50, p90 og møne), og målt takhelning mot kartets 0,82.
     Begge sider er meter over bakken i de samme pikslene, så kalibreringen brukes som kontroll, ikke som skalering
     (a ble 0,44 med r 0,46: tegnehøydene bærer lite informasjon, og å dele på a ville forsterke støy).
  7. Forslag: kartets tak beholdes, veggen settes så overflaten treffer målingen best piksel for piksel:
     h_forslag = median(DOM-DTM - kartets tak over vegg). I tillegg h_med_maalt_takhelning, om takhelningen rettes til målt verdi.
  8. Stikkprøver (kirka, Infanterikasernen, et uthus): snitt-profiler i stikkprover.png.
"""
import json, math, os, sys, urllib.request
import numpy as np
import shapely
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from pyproj import Transformer
import tifffile

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(os.path.dirname(HER))
sys.path.insert(0, os.path.join(ROT, 'regler'))
from _felles import gamleby  # noqa: E402

KILDER = os.path.join(HER, 'kilder'); os.makedirs(KILDER, exist_ok=True)
ORIGO = (10.952745, 59.202835)
WCS = {
    'dom': ('https://wcs.geonorge.no/skwms1/wcs.hoyde-dom-nhm-25832', 'nhm_dom_topo_25832'),
    'dtm': ('https://wcs.geonorge.no/skwms1/wcs.hoyde-dtm-nhm-25832', 'nhm_dtm_topo_25832'),
}
SLOPE, CAP = 0.82, 7.5          # fra 07_vinduer-dører-og-porter.js
KANT = 60                       # meter rundt Gamlebyen

# ---------- koordinater ----------
_t4326_3857 = Transformer.from_crs(4326, 3857, always_xy=True)
_t3857_utm = Transformer.from_crs(3857, 25832, always_xy=True)
_tutm_3857 = Transformer.from_crs(25832, 3857, always_xy=True)
X0, Y0 = _t4326_3857.transform(*ORIGO)
S = 1 / math.cos(math.radians(ORIGO[1]))      # mercator-enheter per modellmeter ved origo


def til_utm(xy):
    a = np.asarray(xy, float)
    return np.stack(_t3857_utm.transform(X0 + a[..., 0] * S, Y0 + a[..., 1] * S), -1)


def til_modell(E, N):
    mx, my = _tutm_3857.transform(E, N)
    return (np.asarray(mx) - X0) / S, (np.asarray(my) - Y0) / S


# ---------- nedlasting ----------
def hent(navn, bbox, ny=False):
    sti = os.path.join(KILDER, f'{navn}1_25832.tif')
    if os.path.exists(sti) and not ny:
        return sti
    url, cov = WCS[navn]
    x0, y0, x1, y1 = bbox
    q = (f'{url}?service=WCS&version=1.0.0&request=GetCoverage&coverage={cov}&crs=EPSG:25832'
         f'&bbox={x0},{y0},{x1},{y1}&width={x1 - x0}&height={y1 - y0}&format=GeoTIFF')
    print('henter', q)
    with urllib.request.urlopen(q, timeout=180) as r:
        data = r.read()
    if not data[:4] in (b'II*\x00', b'MM\x00*'):
        raise SystemExit(f'{navn}: svaret er ikke GeoTIFF: {data[:300]!r}')
    open(sti, 'wb').write(data)
    json.dump({'url': q, 'lisens': 'CC BY 4.0, © Kartverket'}, open(sti + '.json', 'w'), indent=1)
    return sti


def les(sti):
    with tifffile.TiffFile(sti) as tf:
        p = tf.pages[0]; a = p.asarray().astype('float64')
        tie = p.tags['ModelTiepointTag'].value; sc = p.tags['ModelPixelScaleTag'].value
        nod = p.tags.get('GDAL_NODATA')
    if nod is not None:
        a[a == float(nod.value)] = np.nan
    a[(a < -100) | (a > 2000)] = np.nan
    return a, (tie[3] - tie[0] * sc[0], tie[4] + tie[1] * sc[1], sc[0], sc[1])   # x venstre kant, y øvre kant, dx, dy


# ---------- kartets overflate ----------
def plan(f):
    """Plan z = a*x + b*y + c gjennom en takflate (minste kvadrater)."""
    A = np.array([[q[0], q[1], 1] for q in f]); z = np.array([q[2] for q in f])
    return np.linalg.lstsq(A, z, rcond=None)[0]


def kart_overflate(b, mx, my):
    """Kartets høyde over bakken i punktene (mx,my) (modellmeter) for bygg b, slik 05/06/07 bygger det."""
    h = b['h']; z = np.full(mx.shape, h, float)
    pts = shapely.points(mx, my)
    def flater(fl, f_z):
        for f in fl:
            if len(f) < 3: continue
            pg = Polygon([(q[0], q[1]) for q in f]).buffer(0.08)
            inn = shapely.contains(pg, pts)
            if not inn.any(): continue
            a_, b_, c_ = plan(f)
            zz = f_z(np.maximum(0, a_ * mx[inn] + b_ * my[inn] + c_))
            z[inn] = np.maximum(z[inn], zz)
    if b.get('kirke'):
        k = b['kirke']; z[:] = 9.5
        zmax = max(q[2] for f in k['skiptak'] for q in f)
        flater(k['skiptak'], lambda t: 9.5 + t * 8.2 / zmax)
        torn = Polygon(k['torn']); z[shapely.contains(torn, pts)] = 34.0
        return z
    if b.get('tak2'):
        flater(b['tak2'], lambda t: h + t * SLOPE)
    elif b.get('sk') and not b.get('flatt'):
        flater(b['sk'], lambda t: h + np.minimum(t * SLOPE, CAP))
    elif not b.get('flatt'):
        rects = b['tk'] and [r for k, r in enumerate(b['tk']) if k == 0 or min(r[2], r[3]) >= 4.5][:3] or \
            ([b['r']] if b.get('rf', 0) > 0.78 else [])
        for rx, ry, rw, rh, ang in rects:
            short = min(rw, rh)
            if short < 2.5 or short > 24: continue
            rise = min(short * 0.48, 7.5); a = math.radians(ang) + (math.pi / 2 if rw < rh else 0)
            u = (mx - rx) * math.cos(a) + (my - ry) * math.sin(a); v = -(mx - rx) * math.sin(a) + (my - ry) * math.cos(a)
            L, Sx = max(rw, rh) / 2 + 0.25, short / 2 + 0.35
            inn = (abs(u) <= L) & (abs(v) <= Sx)
            z[inn] = np.maximum(z[inn], h + rise * (1 - abs(v[inn]) / Sx))
    for dp in b.get('deler') or []:
        pg = Polygon(dp['p']); inn = shapely.contains(pg, pts)
        if not inn.any(): continue
        top, mh = dp['h'], dp.get('mh', 0)
        rh = ((top - mh) if (top - mh) <= 6 else min(5, (top - mh) * 0.3)) if dp.get('roof') == 'pyramidal' else 5 if dp.get('roof') == 'gabled' else 0
        c = pg.centroid; r = max(math.hypot(q[0] - c.x, q[1] - c.y) for q in dp['p'])
        d = np.hypot(mx[inn] - c.x, my[inn] - c.y) / r
        z[inn] = np.maximum(z[inn], top - rh * np.clip(d, 0, 1))
    return z


# ---------- hovedløp ----------
def main():
    ny = '--ny' in sys.argv
    # husene slik kartet viser dem (rettelser lagt oppå, også nye bygg og omriss fra kommunekartet, 29.10); plassene i lista
    # er de samme som i data/bygg.json, nye bygg står bakerst
    sys.path.insert(0, ROT); import datalag
    B = datalag.alle()['bygg']
    G = [(i, b) for i, b in gamleby(B) if len(b['p']) >= 3]
    utm = {i: til_utm(b['p']) for i, b in G}
    allx = np.concatenate([u[:, 0] for u in utm.values()]); ally = np.concatenate([u[:, 1] for u in utm.values()])
    bbox = (int(allx.min()) - KANT, int(ally.min()) - KANT, int(allx.max()) + KANT, int(ally.max()) + KANT)
    dom, gt = les(hent('dom', bbox, ny)); dtm, gt2 = les(hent('dtm', bbox, ny))
    assert dom.shape == dtm.shape and np.allclose(gt, gt2), (dom.shape, dtm.shape, gt, gt2)
    ndh = dom - dtm
    x0, y1, dx, dy = gt
    H, W = ndh.shape
    cx = x0 + (np.arange(W) + 0.5) * dx; cy = y1 - (np.arange(H) + 0.5) * dy
    def piksler(pg):
        """indekser (rad, kol) for piksler med senter i polygonet pg (UTM)"""
        if pg.is_empty: return np.zeros(0, int), np.zeros(0, int)
        a, b_, c, d = pg.bounds
        c0, c1 = max(0, int((a - x0) / dx)), min(W, int((c - x0) / dx) + 2)
        r0, r1 = max(0, int((y1 - d) / dy)), min(H, int((y1 - b_) / dy) + 2)
        if c0 >= c1 or r0 >= r1: return np.zeros(0, int), np.zeros(0, int)
        XX, YY = np.meshgrid(cx[c0:c1], cy[r0:r1])
        inn = shapely.contains_xy(pg, XX, YY)
        rr, cc = np.nonzero(inn)
        return rr + r0, cc + c0

    def poly(i, b, dxy=(0, 0)):
        u = utm[i] + dxy
        hull = [til_utm(r) + dxy for r in (b.get('ph') or []) if len(r) > 2]
        pg = Polygon(u, hull)
        return pg if pg.is_valid else pg.buffer(0)

    # 3. forskyvning: omrissene mot «noe høyere enn 3 m». Står fast fra tall.json (målt 24.10 på OSM-omrissene; kommunekartet
    #    er tilpasset samme ramme) så målingene ikke flytter seg for hus som ikke er endret; --ny-forskyvning søker på nytt.
    hoy = np.nan_to_num(ndh) > 3
    fast = os.path.join(HER, 'tall.json')
    if os.path.exists(fast) and '--ny-forskyvning' not in sys.argv:
        f0 = json.load(open(fast))['forskyvning']; best = (None, f0[0], f0[1])
    else:
        best = None
        for sx in np.arange(-5, 5.01, 0.5):
            for sy in np.arange(-5, 5.01, 0.5):
                tot = inn = 0
                for i, b in G:
                    if b.get('skjul'): continue
                    rr, cc = piksler(poly(i, b, (sx, sy)).buffer(-0.5))
                    tot += len(rr); inn += hoy[rr, cc].sum()
                sk = inn / max(tot, 1)
                if best is None or sk > best[0]: best = (sk, sx, sy)
    andel0 = None
    tot = inn = 0
    for i, b in G:
        if b.get('skjul'): continue
        rr, cc = piksler(poly(i, b).buffer(-0.5)); tot += len(rr); inn += hoy[rr, cc].sum()
    andel0 = inn / tot
    if best[0] is None:
        tot = inn = 0
        for i, b in G:
            if b.get('skjul'): continue
            rr, cc = piksler(poly(i, b, (best[1], best[2])).buffer(-0.5)); tot += len(rr); inn += hoy[rr, cc].sum()
        best = (inn / tot, best[1], best[2])
    SH = (best[1], best[2])
    print(f'forskyvning øst {SH[0]:+.1f} m, nord {SH[1]:+.1f} m  (treff {andel0:.3f} -> {best[0]:.3f})')

    # 4-5. måling og kartets overflate per hus
    R, PX = {}, {}
    for i, b in G:
        pg = poly(i, b, SH)
        for krymp in (1.0, 0.5, 0.0):
            p2 = pg.buffer(-krymp) if krymp else pg
            rr, cc = piksler(p2)
            if len(rr) >= 4: break
        v = ndh[rr, cc]; ok = ~np.isnan(v)
        rr, cc, v = rr[ok], cc[ok], v[ok]
        if len(v) == 0:
            R[i] = dict(n=0, krymp=krymp); continue
        mx, my = til_modell(cx[cc] - SH[0], cy[rr] - SH[1])
        zk = kart_overflate(b, np.asarray(mx), np.asarray(my))
        rz = zk - b['h']                     # kartets tak over veggtoppen i hver piksel
        PX[i] = (v, rz)
        R[i] = dict(n=int(len(v)), krymp=krymp, p10=float(np.percentile(v, 10)), p50=float(np.percentile(v, 50)),
                    p90=float(np.percentile(v, 90)), maks=float(v.max()), lav=float((v < 2).mean()),
                    k10=float(np.percentile(zk, 10)), k50=float(np.percentile(zk, 50)), k90=float(np.percentile(zk, 90)),
                    kmaks=float(zk.max()), areal=float(pg.area))

    # 6. kalibrering mot husene der kartet har pålitelig (tegnet) høyde
    def palitelig(b):
        t = b.get('tegnet_h')
        return b.get('fasade_kilde') == 'kvartaltegning' and t and 2.5 < t / 1.72 < 15
    kal = [i for i, b in G if palitelig(b) and not b.get('skjul') and R[i].get('n', 0) >= 10 and not b.get('kirke')]
    def fit(m, k):
        m, k = np.array(m), np.array(k)
        a, c = np.polyfit(k, m, 1)
        r = m - (a * k + c); s = r.std(); ok = abs(r) < 2.5 * s          # én runde: rester over 2,5 sigma kastes
        a, c = np.polyfit(k[ok], m[ok], 1); r = m - (a * k + c)
        return dict(a=float(a), b=float(c), n=int(len(m)), n_brukt=int(ok.sum()), rms=float(np.sqrt((r[ok] ** 2).mean())),
                    snitt_diff=float((m - k).mean()), median_diff=float(np.median(m - k)), std_diff=float((m - k).std()),
                    forhold=float(np.median(m / k)), r=float(np.corrcoef(k, m)[0, 1]),
                    kastet=[int(kal[j]) for j in np.nonzero(~ok)[0]])
    F50 = fit([R[i]['p50'] for i in kal], [R[i]['k50'] for i in kal])
    F90 = fit([R[i]['p90'] for i in kal], [R[i]['k90'] for i in kal])
    F_mone = fit([R[i]['p90'] for i in kal], [R[i]['kmaks'] for i in kal])        # vegg h + full takhøyde mot p90
    # takvinkel: per hus v = vegg + s * t, der t = kartets takhøyde / 0,82 (avstand inn fra takfoten). Median s over husene.
    def helning(ids):
        ss = []
        for i in ids:
            if i not in PX or B[i].get('kirke') or B[i].get('deler'): continue
            v, rz = PX[i]; t = rz / SLOPE
            if len(v) < 40 or np.ptp(t) < 2: continue
            s_, c_ = np.polyfit(t, v, 1); ss.append(s_)
        return np.array(ss)
    s_kal = helning(kal); s_alle = helning([i for i, _ in G])
    S_TAK = float(np.median(s_alle))
    print('kalibrering p50', F50); print('kalibrering p90', F90)
    print(f'takhelning målt: median {S_TAK:.2f} (kartet bruker {SLOPE}); kalibreringshus {np.median(s_kal):.2f}, n={len(s_alle)}')

    # 7. forslag: veggen som gir best samsvar piksel for piksel når kartets tak står som i dag
    #    h_forslag = median(DOM-DTM - kartets tak over vegg). DOM-DTM er meter, kartet er meter: ingen skalering.
    ut = {}
    for i, b in G:
        r = R[i]; h0 = b['h']
        e = dict(id=b['id'], navn=b.get('navn'), h_naa=round(h0, 2))   # id: målingen følger huset, ikke plassen i lista (29.10)
        if b.get('skjul'):
            e.update(p50=r.get('p50') and round(r['p50'], 2), p90=r.get('p90') and round(r['p90'], 2), h_forslag=None, sikkerhet='ingen',
                     merknad='skjult i kartet (' + str(b.get('skjul')) + ')'); ut[i] = e; continue
        if r.get('n', 0) == 0:
            e.update(p50=None, p90=None, h_forslag=None, sikkerhet='ingen', merknad='ingen piksler'); ut[i] = e; continue
        v, rz = PX[i]
        hf = float(np.median(v - rz)); rest = v - rz - hf
        spredning = float(np.median(abs(rest)) * 1.4826)
        h_tak = float(np.median(v - rz * S_TAK / SLOPE))
        d50, d90 = r['p50'] - r['k50'], r['p90'] - r['k90']
        m = []; sik = 'høy'
        if hf < 2.0:
            sik = 'lav'; m.append(f'målt overflate ligger under kartets tak alene (vegg ville blitt {hf:.1f} m): taket i kartet er for høyt/bratt for dette huset, eller omrisset dekker et lavere tilbygg — sjekk h_med_maalt_takhelning')
            hf = 2.0
        if r['n'] < 15: sik = 'lav'; m.append(f"bare {r['n']} piksler")
        elif r['n'] < 40 and sik == 'høy': sik = 'middels'; m.append(f"{r['n']} piksler")
        if r['krymp'] < 1: m.append(f"krympet bare {r['krymp']:g} m")
        if spredning > 1.5: sik = 'lav'; m.append(f'stor rest etter tilpasning ({spredning:.1f} m): takform, trær eller nabobygg i omrisset')
        elif spredning > 0.8: sik = 'middels' if sik == 'høy' else sik; m.append(f'rest {spredning:.1f} m')
        if abs(d50 - d90) > 2.0: sik = 'lav'; m.append(f'p50 og p90 sier ulikt ({d50:+.1f}/{d90:+.1f} m)')
        if r['lav'] > 0.25: sik = 'lav'; m.append(f"{r['lav'] * 100:.0f} % av pikslene under 2 m (gårdsrom, feil omriss eller revet)")
        if r['p90'] - r['p50'] > 6: m.append('stor spredning (tårn, trær eller høyere nabobygg i omrisset)')
        if b.get('kirke'):
            m.append('kirka bygges i 06_kirka (vegg 9,5, møne 17,7, tårn 34+), ikke av h — se stikkprøve'); hf = None; sik = 'kontroll'
        if b.get('deler'): m.append('har deler (tårn); h gjelder hovedkroppen')
        if palitelig(b): m.append('kalibreringshus')
        t = b.get('tegnet_h')
        if t and t / 1.72 < 2.5: m.append(f'tegnet_h {t} gir {t / 1.72:.1f} m (umulig): målingen avgjør')
        # per hus (24.10, kveld): vegg OG takhelning tilpasses samtidig, v = h + s·t, der t er avstanden inn fra takfoten (kartets takflate / 0,82).
        # Robust: én runde der rester over 2,5 sigma kastes. Holdes innenfor fysisk rimelige grenser; ellers står fellesverdien.
        h2 = s2 = None
        if hf is not None and len(v) >= 40 and np.ptp(rz) > 1:
            t_ = rz / SLOPE; A = np.c_[np.ones_like(t_), t_]
            k_ = np.linalg.lstsq(A, v, rcond=None)[0]; rr = v - A @ k_; ok_ = abs(rr) < 2.5 * max(rr.std(), 0.2)
            k_ = np.linalg.lstsq(A[ok_], v[ok_], rcond=None)[0]
            if 0.25 <= k_[1] <= 1.1 and 2.4 <= k_[0] <= 16: h2, s2 = float(k_[0]), float(k_[1])
        if h2 is None and hf is not None: h2, s2 = max(2.4, h_tak), S_TAK
        e.update(h_per_hus=None if h2 is None else round(h2, 1), takhelning=None if s2 is None else round(s2, 2))
        e.update(p50=round(r['p50'], 2), p90=round(r['p90'], 2), kart_p50=round(r['k50'], 2), kart_p90=round(r['k90'], 2),
                 h_forslag=None if hf is None else round(hf, 1), avvik=None if hf is None else round(hf - h0, 1),
                 h_med_maalt_takhelning=None if hf is None else round(max(2.0, h_tak), 1),
                 sikkerhet=sik, n_piksler=r['n'], rest_m=round(spredning, 2), merknad='; '.join(m))
        ut[i] = e
    json.dump({str(k): v for k, v in sorted(ut.items())}, open(os.path.join(HER, 'hoyder.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(dict(bbox=bbox, forskyvning=SH, treff_for=andel0, treff_etter=best[0], kal50=F50, kal90=F90, kal_mone=F_mone,
                   takhelning=dict(kart=SLOPE, maalt_median=S_TAK, n=len(s_alle), p25=float(np.percentile(s_alle, 25)),
                                   p75=float(np.percentile(s_alle, 75)), kal_median=float(np.median(s_kal)), kal_n=len(s_kal)),
                   kal=kal, R={str(k): v for k, v in R.items()}), open(os.path.join(HER, 'tall.json'), 'w'), indent=1)
    stikk(B, utm, SH, ndh, gt, piksler, poly)
    tegn(B, G, ut, utm, SH, ndh, gt)
    print('ferdig:', len(ut), 'hus')


STIKK = [('Kirken', 4), ('Infanterikasernen', 3), ('uthus', None)]


def stikk(B, utm, SH, ndh, gt, piksler, poly):
    """Snitt-profiler tvers over tre hus: DOM-DTM mot kartet nå og med foreslått h. Skriver stikkprover.png og stikkprover.json."""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ut = json.load(open(os.path.join(HER, 'hoyder.json'), encoding='utf8'))
    x0, y1, dx, dy = gt; H, W = ndh.shape
    def sample(E, N):
        c = ((E - x0) / dx).astype(int); r = ((y1 - N) / dy).astype(int)
        ok = (c >= 0) & (c < W) & (r >= 0) & (r < H); z = np.full(E.shape, np.nan); z[ok] = ndh[r[ok], c[ok]]; return z
    # uthuset: minste hus med «uthus» i navnet og nok piksler
    kand = [int(k) for k, e in ut.items() if e.get('navn') and 'uthus' in e['navn'].lower() and e.get('h_forslag')]
    uthus = min(kand, key=lambda k: B[k] and Polygon(utm[k]).area) if kand else None
    liste = [(n, i if i is not None else uthus) for n, i in STIKK if (i if i is not None else uthus) is not None]
    fig, ax = plt.subplots(len(liste), 1, figsize=(12, 3.6 * len(liste)), dpi=110)
    res = {}
    for a, (navn, i) in zip(np.atleast_1d(ax), liste):
        b = B[i]; pg = poly(i, b, SH); mrr = pg.minimum_rotated_rectangle
        q = np.array(mrr.exterior.coords)[:4]; e1, e2 = q[1] - q[0], q[2] - q[1]
        kort = e1 if np.hypot(*e1) < np.hypot(*e2) else e2; kort = kort / np.hypot(*kort)
        c = np.array(pg.centroid.coords[0]); L = max(np.hypot(*e1), np.hypot(*e2)) / 2 + 12
        if i == 4:   # kirka: snitt gjennom tårnet og skipet langs lengste akse
            kort = (e1 if np.hypot(*e1) >= np.hypot(*e2) else e2); kort = kort / np.hypot(*kort)
        s_ = np.arange(-L, L, 0.5); E, N = c[0] + kort[0] * s_, c[1] + kort[1] * s_
        z = sample(E, N)
        mx, my = til_modell(E - SH[0], N - SH[1]); mx, my = np.asarray(mx), np.asarray(my)
        inn = shapely.contains_xy(pg, E, N)
        zk = np.where(inn, kart_overflate(b, mx, my), np.nan)
        a.plot(s_, z, c='k', lw=1.4, label='DOM − DTM (Kartverket)')
        a.plot(s_, zk, c='#d1242f', lw=1.2, label=f"kartet nå (h = {b['h']:g} m)")
        e = ut[str(i)]
        if e.get('h_forslag') is not None:
            a.plot(s_, zk + e['h_forslag'] - b['h'], c='#0969da', lw=1.2, ls='--', label=f"forslag (h = {e['h_forslag']:g} m)")
        a.axhline(0, c='#999', lw=.6); a.set_ylabel('m over terreng'); a.grid(alpha=.3); a.legend(fontsize=8, loc='upper right')
        a.set_title(f"[{i}] {b.get('navn')}: snitt {'langs' if i == 4 else 'tvers over'} huset", fontsize=10)
        # bakken rett utenfor (2-6 m fra veggen, uten andre hus) skal være ~0 hvis DTM og DOM stemmer
        ring = pg.buffer(6).difference(pg.buffer(2))
        rr, cc = piksler(ring); g = ndh[rr, cc]; g = g[~np.isnan(g)]
        rr, cc = piksler(pg.buffer(-1) if pg.buffer(-1).area > 4 else pg); v = ndh[rr, cc]; v = v[~np.isnan(v)]
        res[i] = dict(navn=b.get('navn'), h_naa=b['h'], p50=float(np.percentile(v, 50)), p90=float(np.percentile(v, 90)),
                      maks=float(v.max()), bakke_utenfor_p25=float(np.percentile(g, 25)) if len(g) else None,
                      bakke_utenfor_p10=float(np.percentile(g, 10)) if len(g) else None, areal=float(pg.area), h_forslag=e.get('h_forslag'))
        if i == 4:
            k = b['kirke']
            for del_, pts in (('skip', k['skip']), ('torn', k['torn'])):
                pp = Polygon(til_utm(pts) + SH)
                rr, cc = piksler(pp.buffer(-1)); w = ndh[rr, cc]; w = w[~np.isnan(w)]
                res[i][del_] = dict(p50=float(np.percentile(w, 50)), p90=float(np.percentile(w, 90)), maks=float(w.max()), n=int(len(w)))
    fig.tight_layout(); fig.savefig(os.path.join(HER, 'stikkprover.png')); plt.close(fig)
    json.dump(res, open(os.path.join(HER, 'stikkprover.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)


def tegn(B, G, ut, utm, SH, ndh, gt):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MP
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib import cm
    fig = plt.figure(figsize=(22, 13), dpi=110)
    a1 = fig.add_axes([0.04, 0.08, 0.36, 0.84]); a2 = fig.add_axes([0.44, 0.04, 0.50, 0.92]); ac = fig.add_axes([0.955, 0.25, 0.01, 0.5])
    rows = [(i, e) for i, e in ut.items() if e.get('h_forslag') is not None]
    farge = {'høy': '#1a7f37', 'middels': '#b08800', 'lav': '#cf222e'}
    for s in ('høy', 'middels', 'lav'):
        xs = [e['h_naa'] for i, e in rows if e['sikkerhet'] == s]; ys = [e['h_forslag'] for i, e in rows if e['sikkerhet'] == s]
        a1.scatter(xs, ys, s=22, c=farge[s], label=f'{s} ({len(xs)})', alpha=.8, edgecolors='none')
    mx = max(max(e['h_naa'], e['h_forslag']) for i, e in rows) + 1
    a1.plot([0, mx], [0, mx], c='#888', lw=1); a1.fill_between([0, mx], [-1, mx - 1], [1, mx + 1], color='#ccc', alpha=.3, lw=0)
    for i, e in rows:
        if abs(e['avvik']) >= 1.5:
            a1.annotate(str(i), (e['h_naa'], e['h_forslag']), fontsize=7, xytext=(3, 2), textcoords='offset points')
    a1.set_xlabel('h i kartet nå (vegg, m)'); a1.set_ylabel('h foreslått fra DOM−DTM (vegg, m)'); a1.set_xlim(0, mx); a1.set_ylim(0, mx)
    a1.set_title('Veggøyde: kart nå mot målt forslag (grått bånd = ±1 m; indeks merket der avviket er ≥ 1,5 m)', fontsize=10)
    a1.legend(title='sikkerhet', loc='upper left'); a1.grid(alpha=.3)
    # kart
    x0, y1, dx, dy = gt; H, W = ndh.shape
    ext = (x0, x0 + W * dx, y1 - H * dy, y1)
    a2.imshow(np.clip(np.nan_to_num(ndh), 0, 25), extent=ext, cmap='Greys', alpha=.35, origin='upper')
    norm = TwoSlopeNorm(vmin=-6, vcenter=0, vmax=6); cmap = matplotlib.colormaps['RdBu_r']
    for i, b in G:
        u = utm[i] + SH; e = ut[i]
        if e.get('h_forslag') is None:
            a2.add_patch(MP(u, closed=True, fc='none', ec='#333', lw=.6, hatch='///')); continue
        a2.add_patch(MP(u, closed=True, fc=cmap(norm(e['avvik'])), ec='#222', lw=.4, alpha=.95 if e['sikkerhet'] != 'lav' else .55))
        if abs(e['avvik']) >= 1.5:
            c = u.mean(0); a2.text(c[0], c[1], str(i), fontsize=5.5, ha='center', va='center')
    allu = np.concatenate([utm[i] for i, _ in G]) + SH
    a2.set_xlim(allu[:, 0].min() - 10, allu[:, 0].max() + 10); a2.set_ylim(allu[:, 1].min() - 10, allu[:, 1].max() + 10)
    a2.set_aspect('equal'); a2.set_title('Gamlebyen, avvik h_forslag − h_naa (blå = huset bør bli lavere, rød = høyere; blekt = lav sikkerhet; skravert = ikke vurdert). Bakgrunn: DOM−DTM', fontsize=10)
    a2.set_xlabel('UTM 32N øst (m)'); a2.set_ylabel('UTM 32N nord (m)'); a2.tick_params(labelsize=7); a2.ticklabel_format(useOffset=False, style='plain')
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ac, label='avvik (m)')
    fig.suptitle('Bygghøyder i Gamlebyen: Kartverket DOM1 − DTM1 (CC BY 4.0) mot 3D-kartet', fontsize=13)
    fig.savefig(os.path.join(HER, 'kontrollark.png')); plt.close(fig)


if __name__ == '__main__':
    main()
