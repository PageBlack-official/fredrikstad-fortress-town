#!/usr/bin/env python3
"""Benker og gjerder til 3D-kartet over Gamlebyen. Gjør alt på nytt:

    python3 hent.py            henter OSM på nytt (api.openstreetmap.org), bygger alt
    python3 hent.py --cache    bruker _cache/map.osm fra forrige kjøring

Inn:
  tegnet2019.json            gjerder/murer/hekker lest med øynene i 2019-trykket (fasit for HVA og HVOR), i 2019-px
  OSM (api.openstreetmap.org/api/0.6/map, boks lat 59.198-59.210, lon 10.940-10.965):
                             barrier=fence|wall|hedge|retaining_wall (ways), amenity=bench, leisure=picnic_table (nodes)
  soc/data/gjerder.json, murer.json, bygg.json, veier.json, vann.json (bare lest)
Ut (i denne mappa):
  gjerder-forslag.json       NYE gjerdelinjer, samme format som data/gjerder.json (liste av polylinjer [[x,y],...])
  gjerder-kilde.json         én rad per linje i gjerder-forslag.json (samme rekkefølge): kilde, sikkerhet, type
  benker.json                [{x, y, retning_grader, kilde, ...}]
  kontrollark.png            2019-utsnitt og flyfoto side om side, 6 områder
  tall.json                  tallene rapport.md bygger på
Røres ikke: soc/src, soc/data.

Overpass (overpass-api.de) svarer ikke gjennom proxyen i skallet (forbindelsen kuttes), derfor OSM-API-et direkte.
Det gir alt i boksen (ca. 5,7 MB), og vi filtrerer selv.
"""
import json, math, os, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from PIL import Image, ImageDraw, ImageFont

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))
import proj  # noqa: E402

SOC = proj.SOC
ROT = proj.ROT
DATA = SOC / 'data'
BOKS = (10.940, 59.198, 10.965, 59.210)  # w, s, e, n
CACHE = HER / '_cache'
NAER_EKSISTERENDE = 4.0   # m: en trykklinje regnes som «finnes» hvis snittavstanden til en eksisterende gjerde-/murlinje er mindre


def les(navn):
    return json.load(open(DATA / f'{navn}.json'))


# ---------------------------------------------------------------- OSM
def hent_osm(bruk_cache):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / 'map.osm'
    if not (bruk_cache and f.exists()):
        url = 'https://api.openstreetmap.org/api/0.6/map?bbox=%s,%s,%s,%s' % BOKS
        req = urllib.request.Request(url, headers={'User-Agent': 'pageblack-smartoldtown'})
        f.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    r = ET.parse(f).getroot()
    tid = r.find('bounds')
    noder = {n.get('id'): (float(n.get('lon')), float(n.get('lat'))) for n in r.findall('node')}
    barrierer, benker = [], []
    for e in r:
        t = {k.get('k'): k.get('v') for k in e.findall('tag')}
        if e.tag == 'way' and t.get('barrier') in ('fence', 'wall', 'hedge', 'retaining_wall', 'city_wall'):
            p = [proj.ll2xy(*noder[n.get('ref')]) for n in e.findall('nd') if n.get('ref') in noder]
            barrierer.append(dict(id=e.get('id'), t=t, p=p))
        if e.tag == 'node' and (t.get('amenity') == 'bench' or t.get('leisure') == 'picnic_table'):
            lon, lat = float(e.get('lon')), float(e.get('lat'))
            benker.append(dict(id=e.get('id'), t=t, lon=lon, lat=lat, xy=proj.ll2xy(lon, lat)))
    return barrierer, benker, f.stat().st_size


# ---------------------------------------------------------------- hjelpere
def snittavstand(a, b, n=10):
    """snitt av avstanden fra n punkter langs a til linja b"""
    a = LineString(a); b = LineString(b)
    return float(np.mean([b.distance(a.interpolate(s, normalized=True)) for s in np.linspace(0, 1, n)]))


def nermeste(linje, kandidater):
    best = (1e9, None)
    for i, k in enumerate(kandidater):
        d = snittavstand(linje, k)
        if d < best[0]:
            best = (d, i)
    return best


def peiling(dx, dy):
    """kompasskurs i grader (0 = nord, 90 = øst) for vektoren (dx øst, dy nord)"""
    return (math.degrees(math.atan2(dx, dy)) + 360) % 360


# ---------------------------------------------------------------- gjerder
def gjerder(barrierer):
    G = les('gjerder'); M = les('murer'); B = les('bygg')
    hus = [Polygon(b['p']).buffer(0) for b in B if b.get('p') and len(b['p']) > 2]
    eksist = [('gjerder.json', i, g) for i, g in enumerate(G)] + [('murer.json', i, m['p']) for i, m in enumerate(M)]
    T = json.load(open(HER / 'tegnet2019.json'))['linjer']
    forslag, kilde, alle = [], [], []
    for t in T:
        p = proj.fra2019(t['px'])
        if t.get('flytt_m'):  # justering etter flyfoto, ført i tegnet2019.json med grunn
            p = p + np.array(t['flytt_m'])
        L = LineString(p)
        ihus = sum(L.intersection(h).length for h in hus)
        # regel: et gjerde stopper ved husveggen. Husene i trykket står på mønehøyde, så en linje som i
        # trykket går «inn til huset» havner inne i fotavtrykket. Klipp bort delene inne i hus, behold lengste bit.
        if ihus > 0.5:
            rest = L
            for h in hus:
                if rest.intersects(h):
                    rest = rest.difference(h)
            biter = [rest] if rest.geom_type == 'LineString' else list(getattr(rest, 'geoms', []))
            biter = [b for b in biter if b.length > 2]
            if biter:
                L = max(biter, key=lambda b: b.length)
                p = np.array(L.coords)
        p = np.round(p, 2)
        d, i = nermeste(p, [e[2] for e in eksist])
        rad = dict(id=t['id'], type=t['type'], sikkerhet=t['sikkerhet'], lengde_m=round(L.length, 1),
                   naermeste=f'{eksist[i][0]}[{eksist[i][1]}]', avstand_m=round(d, 1), inne_i_hus_m=round(ihus, 1),
                   status='finnes' if d < NAER_EKSISTERENDE else 'ny', merknad=t['merknad'], p=p.tolist())
        alle.append(rad)
        if rad['status'] == 'ny':
            forslag.append(p.tolist())
            kilde.append(dict(i=len(forslag) - 1, id=t['id'], kilde='2019-trykket (kilder2019/brosjyre2019-3.jpg), lest med øynene',
                              px2019=t['px'], type=t['type'], farge_i_trykket=t['farge_i_trykket'], sikkerhet=t['sikkerhet'],
                              flytt_m=t.get('flytt_m'), flytt_grunn=t.get('flytt_grunn'),
                              inne_i_hus_m=rad['inne_i_hus_m'], merknad=t['merknad']))
    # OSM-gjerder/hekker som ikke finnes i data/ fra før
    osm_rader = []
    for b in barrierer:
        if len(b['p']) < 2:
            continue
        d, i = nermeste(b['p'], [e[2] for e in eksist])
        rad = dict(id='osm' + b['id'], barrier=b['t'].get('barrier'), lengde_m=round(LineString(b['p']).length, 1),
                   avstand_m=round(d, 1), status='finnes' if d < NAER_EKSISTERENDE else 'ny',
                   sentrum=np.round(np.mean(b['p'], 0)).tolist())
        osm_rader.append(rad)
        if rad['status'] == 'ny' and b['t'].get('barrier') in ('fence', 'hedge'):
            forslag.append(np.round(b['p'], 2).tolist())
            kilde.append(dict(i=len(forslag) - 1, id='osm' + b['id'], kilde=f"OpenStreetMap way {b['id']} (barrier={b['t'].get('barrier')})",
                              type=b['t'].get('barrier'), sikkerhet='middels (OSM, ikke i trykket)',
                              osm_tagger=b['t'], merknad='Utenfor trykkets utsnitt' if not i_trykket(np.mean(b['p'], 0)) else ''))
    # eksisterende gjerder: hva støtter dem?
    trykklinjer = [r['p'] for r in alle]
    eks = []
    for i, g in enumerate(G):
        L = LineString(g)
        d_t = min(snittavstand(g, t) for t in trykklinjer)
        ihus = sum(L.intersection(h).length for h in hus)
        eks.append(dict(i=i, lengde_m=round(L.length, 1), naer_trykklinje_m=round(d_t, 1), inne_i_hus_m=round(ihus, 1)))
    return forslag, kilde, alle, osm_rader, eks


# ---------------------------------------------------------------- benker
_IM19 = None


def i_trykket(xy):
    """True hvis punktet faller på land innenfor kartet i 2019-trykket (ikke vann, ikke tegnforklaring/utenfor)."""
    global _IM19
    if _IM19 is None:
        _IM19 = np.asarray(Image.open(ROT / 'kilder2019' / 'brosjyre2019-3.jpg').convert('RGB')).astype(int)
    q = proj.til2019([xy])[0]
    H, W = _IM19.shape[:2]
    x, y = int(round(q[0])), int(round(q[1]))
    if not (0 <= x < W and 0 <= y < H) or (x > 1330 and y > 1450):
        return False
    r, g, b = np.median(_IM19[max(0, y - 3):y + 4, max(0, x - 3):x + 4].reshape(-1, 3), axis=0)
    vann = b > r + 40 and g > r + 30 and r < 140   # turkis/blått i akvarellen
    return not vann


def benker(rå):
    V = les('veier'); W = les('vann')
    stier = [LineString(v['p']) for v in V if len(v['p']) > 1]
    vann = [Polygon(w['p']).buffer(0) for w in W if len(w['p']) > 2]
    minx, miny = -470, -450; maxx, maxy = 530, 470   # modellens byggutstrekning + litt
    ut, utenfor = [], []
    for b in rå:
        x, y = b['xy']
        t = b['t']
        if not (minx < x < maxx and miny < y < maxy):
            utenfor.append(dict(id=b['id'], x=round(x, 1), y=round(y, 1), grunn='utenfor modellens område'))
            continue
        pt = Point(x, y)
        # retning: mot nærmeste vann hvis det er nærmere enn 15 m, ellers mot nærmeste vei/sti
        dv, vq = 1e9, None
        for w in vann:
            d = w.exterior.distance(pt)
            if d < dv:
                dv, vq = d, w.exterior.interpolate(w.exterior.project(pt))
        ds, sq = 1e9, None
        for s in stier:
            d = s.distance(pt)
            if d < ds:
                ds, sq = d, s.interpolate(s.project(pt))
        if dv < 15 and dv < ds + 10:
            mål, grunn = vq, f'antatt: mot vannet ({dv:.0f} m)'
        else:
            mål, grunn = sq, f'antatt: mot nærmeste vei/sti ({ds:.0f} m)'
        dx, dy = mål.x - x, mål.y - y
        retning = round(peiling(dx, dy)) if math.hypot(dx, dy) > 0.2 else None
        typ = 'benk' if t.get('amenity') == 'bench' else 'piknikbord'
        ekstra = {k: v for k, v in t.items() if k in ('backrest', 'material', 'colour', 'seats', 'covered', 'description', 'check_date')}
        ut.append(dict(x=round(x, 2), y=round(y, 2), retning_grader=retning,
                       kilde=f"OpenStreetMap node {b['id']} ({'amenity=bench' if typ == 'benk' else 'leisure=picnic_table'})",
                       type=typ, retning_kilde=grunn, i_trykket=bool(i_trykket((x, y))), osm=ekstra,
                       lon=round(b['lon'], 7), lat=round(b['lat'], 7)))
    return ut, utenfor


# ---------------------------------------------------------------- kontrollark
OMRADER = [  # navn, senter (modell m), halv bredde (m)
    ('A  Tøihusgaten og Tøihusparken', (-110, -110), 70),
    ('B  Kasernegaten', (-68, -2), 34),
    ('C  Hagen ved 20 og Voldgaten', (45, -100), 55),
    ('D  Kirkegaten/Raadhusgaten mot nord', (60, 110), 85),
    ('E  Østvollen: 29-31 og Vollportgaten', (225, 120), 90),
    ('F  Sørvollen og Laboratoriegaten', (-60, -200), 120),
]


def tegn_panel(img, til, senter, halv, G, M, forslag, kilde, bnk, PW, PH, skala_px_per_m):
    """klipper ut et område rundt senter fra img (via projeksjon til) og tegner lagene"""
    c = til([senter])[0]
    s = skala_px_per_m
    w, h = halv * s * 2.0, halv * s * 2.0 * PH / PW
    box = (int(c[0] - w / 2), int(c[1] - h / 2), int(c[0] + w / 2), int(c[1] + h / 2))
    ut = img.crop(box).resize((PW, PH), Image.LANCZOS).convert('RGB')
    k = PW / (box[2] - box[0])
    d = ImageDraw.Draw(ut, 'RGBA')
    f = lambda P: [((q[0] - box[0]) * k, (q[1] - box[1]) * k) for q in til(P)]
    for m in M:
        d.line(f(m['p']), fill=(70, 70, 70, 200), width=3)
    for g in G:
        d.line(f(g), fill=(150, 150, 150, 230), width=4)
    fnt = ImageFont.load_default()
    for p, kk in zip(forslag, kilde):
        q = f(p)
        usikker = kk['sikkerhet'] in ('lav', 'usikker')
        if usikker:   # stiplet
            for a, b in zip(q[:-1], q[1:]):
                n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 8))
                for j in range(0, n, 2):
                    t0, t1 = j / n, min(1, (j + 1) / n)
                    d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(230, 0, 0, 255), width=4)
        else:
            d.line(q, fill=(230, 0, 0, 255), width=4)
        d.text((q[0][0] + 4, q[0][1] - 12), kk['id'], fill=(230, 0, 0), font=fnt, stroke_width=2, stroke_fill=(255, 255, 255))
    for b in bnk:
        q = f([(b['x'], b['y'])])[0]
        if b['retning_grader'] is not None:
            a = math.radians(b['retning_grader'])
            e = f([(b['x'] + 2.5 * math.sin(a), b['y'] + 2.5 * math.cos(a))])[0]
            d.line([q, e], fill=(0, 70, 255, 255), width=2)
        d.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], fill=(0, 70, 255, 255), outline=(255, 255, 255, 255))
    return ut


def kontrollark(forslag, kilde, bnk):
    G = les('gjerder'); M = les('murer')
    i19 = Image.open(ROT / 'kilder2019' / 'brosjyre2019-3.jpg')
    ifl = Image.open(SOC / 'kilder' / 'flyfoto-google-2026-10-23.jpg')
    PW, PH = 620, 520
    fnt = ImageFont.load_default()
    rader = []
    for navn, senter, halv in OMRADER:
        a = tegn_panel(i19, proj.til2019, senter, halv, G, M, forslag, kilde, bnk, PW, PH, 3.3)
        b = tegn_panel(ifl, proj.tilfly, senter, halv, G, M, forslag, kilde, bnk, PW, PH, 2 / 0.78)
        r = Image.new('RGB', (PW * 2 + 10, PH + 26), (255, 255, 255))
        r.paste(a, (0, 26)); r.paste(b, (PW + 10, 26))
        dd = ImageDraw.Draw(r)
        dd.text((6, 6), f'{navn}   (venstre: 2019-trykket, høyre: flyfoto 2026; {2*halv} m bredt)', fill=(0, 0, 0), font=fnt)
        rader.append(r)
    leg = Image.new('RGB', (PW * 2 + 10, 40), (255, 255, 255))
    d = ImageDraw.Draw(leg)
    d.line([(10, 20), (50, 20)], fill=(150, 150, 150), width=4); d.text((56, 14), 'dagens gjerder.json', fill=(0, 0, 0), font=fnt)
    d.line([(200, 20), (240, 20)], fill=(70, 70, 70), width=3); d.text((246, 14), 'dagens murer.json', fill=(0, 0, 0), font=fnt)
    d.line([(380, 20), (420, 20)], fill=(230, 0, 0), width=4); d.text((426, 14), 'foreslått (heltrukket = høy/middels, stiplet = lav/usikker)', fill=(0, 0, 0), font=fnt)
    d.ellipse([800, 15, 810, 25], fill=(0, 70, 255)); d.text((816, 14), 'benk (OSM), strek = antatt retning', fill=(0, 0, 0), font=fnt)
    d.text((1060, 14), 'Husene i trykket står på mønehøyde', fill=(0, 0, 0), font=fnt)
    # to kolonner med tre rader
    W = rader[0].width; H = rader[0].height
    ark = Image.new('RGB', (W * 2 + 20, H * 3 + 20 + 40), (255, 255, 255))
    ark.paste(leg, (0, 0))
    for j, r in enumerate(rader):
        ark.paste(r, ((j % 2) * (W + 20), 40 + (j // 2) * (H + 10)))
    ark.save(HER / 'kontrollark.png', optimize=True)
    return ark.size


# ---------------------------------------------------------------- main
def main():
    bruk_cache = '--cache' in sys.argv
    barrierer, rå_benker, osm_bytes = hent_osm(bruk_cache)
    forslag, kilde, alle, osm_rader, eks = gjerder(barrierer)
    bnk, utenfor = benker(rå_benker)
    json.dump(forslag, open(HER / 'gjerder-forslag.json', 'w'), ensure_ascii=False)
    json.dump(kilde, open(HER / 'gjerder-kilde.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(bnk, open(HER / 'benker.json', 'w'), ensure_ascii=False, indent=1)
    size = kontrollark(forslag, kilde, bnk)
    tall = dict(osm_bytes=osm_bytes, trykklinjer=alle, osm_barrierer=osm_rader, eksisterende_gjerder=eks,
                forslag=len(forslag), benker=len(bnk), benker_i_trykket=sum(b['i_trykket'] for b in bnk),
                benker_utenfor=utenfor, kontrollark=size)
    json.dump(tall, open(HER / 'tall.json', 'w'), ensure_ascii=False, indent=1)
    print(f"gjerdeforslag: {len(forslag)}  (trykklinjer {len(alle)}, av dem nye {sum(r['status']=='ny' for r in alle)})")
    print(f"OSM-barrierer: {len(osm_rader)}, nye: {sum(r['status']=='ny' for r in osm_rader)}")
    print(f"benker: {len(bnk)} i modellområdet ({tall['benker_i_trykket']} på land i trykket), {len(utenfor)} utenfor")
    print('kontrollark', size)


if __name__ == '__main__':
    main()
