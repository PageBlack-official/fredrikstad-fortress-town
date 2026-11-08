#!/usr/bin/env python3
"""Veggfarge-kandidater fra Street View-bilder som alt finnes (rapport/gate/sv*/). Samme ord og regler som verktoy/rett/FARGER.md:
ett ord fra lista, fargen veggen er malt i (ikke vinduer, dører, tak), bare bilder fra 2016 eller senere (fargeregelen, LESMEG), bare sikre lesninger.

Slik: veggen fra kartet projiseres inn i bildet (panoramaets posisjon, heading, pitch og fov; fov i lenka er LODDRETT). Små felt midt på veggen
som står fri i kartet måles i Lab. Felt med tekstur, mørke (vinduer), himmel og løv tas ut. Største fargeklynge er veggen. Ordet settes av kulør og lyshet.
Skriptet er et filter, ikke en dom: uavhengig kontroll 08.11 ga 7 avvik på 31 hus. Hver kandidat skal ses på kontaktarket før den flettes inn (rapport/farger/OPPGAVE.md).
Er noe uklart (lite vegg å se, to like store klynger, lyshet mellom hvit og grå i sol, kulør på grensen) blir det ikke kandidat. Grønn og blå blir aldri
kandidater: løv og himmel gir de samme tallene; slike hus må ses av et øye.
Står det to kulører på samme hus, er ingen av dem sikre (huset har én veggfarge i modellen, jf. 715 den 07.11).

    python3 verktoy/rett/farge_kandidater.py [id ...] [--liste rapport/farger/husliste.json] --ut <fil.json> [--ark <kontaktark.jpg>] [--status <status.json>] [--avvist <fil med bildenavn>] [--flett kilder/gate/farger-rett.json]
Utdata: samme format som kilder/gate/farger-rett.json (sider med kilde «rettet fasade 07.11»).
--flett legger nye sider til i den fila uten å røre de gamle (farger_inn.py bytter ut ALLE sider med det merket, så den må få hele fila).
Env SV_ROT: mappa med sv*/ (standard rapport/gate i dette treet)."""
import argparse, glob, json, math, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw
ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, vegger as VG, tak_farge as T  # noqa: E402
from streetview_farger import VEGG, fra_ord  # noqa: E402

MERKE = 'rettet fasade 07.11'
MIN_AAR = 2016
OYE = 2.5            # kamerahøyde over bakken (samme tall som sv_rett_plan.py)
SV_ROT = os.environ.get('SV_ROT') or os.path.join(ROT, 'rapport', 'gate')
# Terskler. Rør dem bare sammen med verktoy/rett/test_farge_kandidater.py: testen skal være grønn etterpå.
MIN_FELT, MIN_DEKNING, MIN_ANDEL = 18, 0.20, 0.60
KUL_R = 7.0           # radius i a*/b* for «samme kulør»
SKIFT = 1.5           # meter: samme måling flyttet så langt til hver side må gi samme kulør. Ellers står vi kanskje på nabohuset (Googles posisjon)
UI = [(0, 0, 410, 150), (0, 590, 200, 720), (1200, 0, 1280, 720), (0, 700, 1280, 720)]   # Googles knapper og kort i et 1280×720-skudd
INNER = (0.18, 0.82)  # andel av veggen vi måler på: Googles posisjon kan ligge 3–5 m feil, så endene kan være nabohuset
MAKS_TEKSTUR = 8.0    # std av L* i et felt; umalt tegl ligger høyere enn puss, men under vindu og løv


def lab_til_rgb(lab):
    p = np.float32([[lab]])
    return [int(round(max(0, min(1, float(v))) * 255)) for v in cv2.cvtColor(p, cv2.COLOR_LAB2RGB)[0, 0]]


class Kart:
    def __init__(self):
        from shapely.geometry import Polygon
        from shapely.strtree import STRtree
        A = datalag.alle(); self.A = A
        self.B = {x['id']: x for x in A['bygg']}
        self.omg = VG.Omgivelser(A['bygg'], A['veier'], A['gardsrom'])
        self.bygg = [b for b in A['bygg'] if b.get('p') and len(b['p']) > 2 and not b.get('skjul')]
        self.poly = [Polygon(b['p']).buffer(0) for b in self.bygg]
        self.tre = STRtree(self.poly)
        self._v = {}
        f = os.path.join(ROT, 'kilder', 'gate', 'sv_skudd.json')
        self.skudd = {f"{s['id']}-{s['del_']}": s for s in json.load(open(f, encoding='utf8'))} if os.path.exists(f) else {}

    def vegger(self, id_):
        if id_ not in self._v:
            self._v[id_] = VG.vegger(self.B[id_], self.omg, slaa_sammen=True)
        return self._v[id_]

    def fri(self, P, q, id_):
        from shapely.geometry import LineString
        ls = LineString([(float(P[0]), float(P[1])), (float(q[0]), float(q[1]))])
        for i in self.tre.query(ls):
            if self.bygg[i]['id'] != id_ and self.poly[i].intersects(ls):
                return False
        return True

    def vegg_av(self, r):
        """(a, c) i modellmeter for bildet, eller None. sv/ er tatt per gatevegg-bit (sv_skudd.json); sv_rett*/ per veggindeks."""
        id_, del_ = r['bilde'].rsplit('-', 1)
        if id_ not in self.B: return None
        if r['mappe'] == 'sv':
            s = self.skudd.get(r['bilde'])
            return (np.array(s['a'], float), np.array(s['b'], float)) if s and s.get('a') and s.get('b') else None
        w = self.vegger(id_)
        return (np.array(w[int(del_)]['a'], float), np.array(w[int(del_)]['c'], float)) if int(del_) < len(w) else None


def les_bilder(rot=None):
    """Alle bilder som finnes, med kameraet de er tatt med. Bare 2016 og senere."""
    ut = []
    for d in sorted(glob.glob(os.path.join(rot or SV_ROT, 'sv*'))):
        if not os.path.isdir(d): continue
        for f in sorted(glob.glob(os.path.join(d, 'hent-*.json'))):
            for k, v in json.load(open(f, encoding='utf8')).items():
                jpg = os.path.join(d, k + '.jpg'); aar = T.sv_aar(v.get('dato'))
                if not v.get('pano') or not aar or aar < MIN_AAR or not os.path.exists(jpg): continue
                ut.append({'bilde': k, 'id': k.rsplit('-', 1)[0], 'mappe': os.path.basename(d), 'fil': jpg, 'pano': v['pano'], 'dato': v['dato'], 'aar': aar,
                           'lat': v['lat'], 'lon': v['lon'], 'heading': v['heading'], 'fov': v['fov'], 'pitch': v.get('pitch') or 93})
    return ut


def kamera(r, W, H):
    hd, t = math.radians(r['heading']), math.radians(r['pitch'] - 90)
    f0 = np.array([math.sin(hd), math.cos(hd), 0.0]); oppe = np.array([0.0, 0.0, 1.0])
    return {'P': np.array(datalag.til_modell(r['lon'], r['lat']) + (OYE,), float), 'hoyre': np.array([math.cos(hd), -math.sin(hd), 0.0]),
            'f': f0 * math.cos(t) + oppe * math.sin(t), 'u': -f0 * math.sin(t) + oppe * math.cos(t), 'F': (H / 2) / math.tan(math.radians(r['fov']) / 2), 'W': W, 'H': H}


def til_bilde(c, q):
    d = q - c['P']; z = float(d @ c['f'])
    if z < 1: return None
    return (c['W'] / 2 + c['F'] * float(d @ c['hoyre']) / z, c['H'] / 2 - c['F'] * float(d @ c['u']) / z, z)


def lys_av(lab, ref):
    """sol/skygge/overskyet. Blå himmel øverst i bildet = klarvær. I klarvær er veggen i sol når det lyseste på den (karmer, hvit puss) er nesten hvitt."""
    topp = lab[:lab.shape[0] // 3]
    klart = float(((topp[:, :, 2] < -8) & (topp[:, :, 0] > 40)).mean()) >= 0.15
    if not klart: return 'overskyet'
    return 'sol' if ref >= 90 else 'skygge'


def ord_av(L, a, b, tekstur, lys):
    """Ord fra FARGER.md, eller None når tallene ikke avgjør det. Bare de ordene der kulør og lyshet alene er nok."""
    C = math.hypot(a, b); h = (math.degrees(math.atan2(b, a)) + 360) % 360
    if C < 7:   # uten kulør: hvit i sol er lys; samme vegg i skygge er grå i bildet, så midtsjiktet er usikkert
        if lys == 'sol': return 'hvit' if L >= 82 else None
        if lys == 'overskyet' and L >= 72: return 'hvit'
        return None     # grå i bildet kan være blågrå, rosa eller hvit i skygge (uavhengig kontroll 08.11): aldri kandidat
    if C < 11: return 'krem' if L >= 82 and 60 <= h <= 110 else None
    if 100 <= h < 300: return None     # grønn og blå: se modulteksten
    if L < 30: return None             # for mørkt til å skille kulør
    if h < 18 or h >= 300: return 'vinrød' if L < 50 else None
    if h < 36: return 'oksiderød' if L < 55 else ('laks' if L >= 72 else None)
    if h < 58:
        if L < 62: return 'umalt tegl' if tekstur >= 3.0 else 'terrakotta'
        return 'laks' if L >= 74 else None
    if h < 66 and L >= 74: return None     # laks eller fersken: to ulike kulørfamilier, tallene skiller dem ikke
    if h < 82:
        if L < 56: return 'okerbrun' if C >= 17 else None     # lav kulør i svakt lys kan like gjerne være umalt tegl
        if L < 74: return 'okergul'
        return 'fersken' if C >= 16 else 'beige'
    return ('kremgul' if C >= 18 else None) if L >= 62 else None


def les_en(K, r):
    """Måling av ett bilde: {'ord', 'rgb', 'lys', 'andel', 'dekning', 'felt', 'hjorner'} eller {'grunn': ...}."""
    v = K.vegg_av(r)
    if v is None: return {'grunn': 'finner ikke veggen i kartet'}
    a, c = v; L_v = float(np.linalg.norm(c - a))
    h = float(K.B[r['id']].get('h') or 0)
    if L_v < 3 or h < 3: return {'grunn': f'for liten vegg ({L_v:.1f} m × {h:.1f} m)'}
    im = np.asarray(Image.open(r['fil']).convert('RGB'), np.float32) / 255
    H, W = im.shape[:2]; lab = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)
    cam = kamera(r, W, H); e = (c - a) / L_v
    sjekket, punkter, bak = 0, [], 0
    for s in np.arange(INNER[0] * L_v, INNER[1] * L_v, 0.4):
        for z in np.arange(1.4, h - 0.6, 0.4):
            q2 = a + e * s
            p = til_bilde(cam, np.array([q2[0], q2[1], z]))
            if p is None: continue
            u, w, d = p; hv = max(3, min(14, int(round(cam['F'] * 0.16 / d))))
            if not (hv <= u < W - hv and hv <= w < H - hv) or any(x0 <= u < x1 and y0 <= w < y1 for x0, y0, x1, y1 in UI): continue
            sjekket += 1
            if not K.fri(cam['P'], q2 + (cam['P'][:2] - q2) / max(1e-6, float(np.linalg.norm(cam['P'][:2] - q2))) * 0.4, r['id']): bak += 1; continue
            punkter.append((u, w, hv, d))
    if sjekket < 30: return {'grunn': f'veggen er nesten utenfor bildet ({sjekket} felt)'}
    if bak / sjekket > 0.5: return {'grunn': 'et annet hus står foran i kartet'}
    fri = len(punkter)

    def maal(flytt):
        felt, topp = [], []
        for u, w, hv, d in punkter:
            du = cam['F'] * flytt / d
            x0, x1 = int(u + du) - hv, int(u + du) + hv
            if x0 < 0 or x1 >= W: continue
            del_ = lab[int(w) - hv:int(w) + hv, x0:x1].reshape(-1, 3)
            topp.append(float(np.percentile(del_[:, 0], 98)))
            m, sd = del_.mean(0), float(del_[:, 0].std())
            if sd > MAKS_TEKSTUR or m[0] < 20: continue
            if m[0] > 60 and m[2] < -8: continue                  # himmel
            if m[1] < -5 and m[2] > 0: continue                   # løv
            felt.append((*m, sd))
        if len(felt) < MIN_FELT or len(felt) / fri < MIN_DEKNING: return {'grunn': f'for lite ren vegg ({len(felt)} av {fri} felt)'}
        # Veggen = tettest samling av kulør (a*, b*). Lysheten er med vilje ute: samme vegg i sol og slagskygge er én farge. Ingen tilfeldig klynging.
        F = np.float32(felt); ab = F[:, 1:3]
        naer = np.linalg.norm(ab[:, None] - ab[None], axis=2) <= KUL_R
        F = F[naer[int(naer.sum(1).argmax())]]; andel = len(F) / len(felt)
        Lm, am, bm = [float(x) for x in (np.percentile(F[:, 0], 60), np.median(F[:, 1]), np.median(F[:, 2]))]
        lys = lys_av(lab, float(np.percentile(topp, 90)))
        res = {'rgb': lab_til_rgb([Lm, am, bm]), 'lys': lys, 'andel': round(andel, 2), 'dekning': round(len(felt) / fri, 2), 'felt': len(felt),
               'tekstur': round(float(np.median(F[:, 3])), 1), 'lab': [round(Lm), round(am), round(bm)]}
        if andel < MIN_ANDEL: return {**res, 'grunn': f'ingen farge dominerer ({andel:.0%})'}
        o = ord_av(Lm, am, bm, res['tekstur'], lys)
        return {**res, 'ord': o} if o else {**res, 'grunn': 'tallene avgjør ikke ordet'}

    res = maal(0.0)
    hj = [til_bilde(cam, np.array([*q, zz])) for q, zz in ((a + e * INNER[0] * L_v, 1.4), (a + e * INNER[1] * L_v, 1.4), (a + e * INNER[1] * L_v, h - 0.6), (a + e * INNER[0] * L_v, h - 0.6))]
    res['hjorner'] = [(p[0], p[1]) for p in hj if p]
    if res.get('ord'):
        sider = [m for m in (maal(SKIFT), maal(-SKIFT)) if m.get('lab')]
        lik = [math.hypot(m['lab'][1] - res['lab'][1], m['lab'][2] - res['lab'][2]) <= KUL_R * 1.5 and m.get('andel', 0) >= MIN_ANDEL for m in sider]
        if not any(lik) or (len(lik) == 2 and not all(lik) and sider[lik.index(False)].get('andel', 0) >= MIN_ANDEL):
            res['grunn'] = 'annen farge rett ved siden av: kan stå på nabohuset (' + res.pop('ord') + ')'
    return res


def familie_av_ord(o):
    return T.familie(fra_ord(o, VEGG))


def side(r, m):
    return {'id': r['id'], 'side': {'retning': f"rettet fasade, vegg {r['bilde'].rsplit('-', 1)[1]} (verktoy/rett, {r['bilde']})", 'vegg_farge': m['ord'], 'vegg_rgb': m['rgb'], 'lys': m['lys'],
                                    'bilde_dato': r['dato'], 'pano_url': f"{r['lat']}, {r['lon']} h {r['heading']}", 'kilde': MERKE}}


def ark(rader, sti):
    B, H_ = 320, 180; kol = 4; n = max(1, len(rader))
    a = Image.new('RGB', (kol * B, ((n + kol - 1) // kol) * (H_ + 34)), 'white'); d = ImageDraw.Draw(a)
    for i, (r, m) in enumerate(rader):
        x, y = (i % kol) * B, (i // kol) * (H_ + 34)
        im = Image.open(r['fil']).convert('RGB'); sk = B / im.size[0]; im = im.resize((B, H_))
        a.paste(im, (x, y))
        if len(m.get('hjorner') or []) == 4: d.polygon([(x + p[0] * sk, y + p[1] * sk) for p in m['hjorner']], outline=(255, 0, 255))
        if m.get('ord'): d.rectangle([x, y + H_, x + 30, y + H_ + 33], fill=tuple(fra_ord(m['ord'], VEGG)))
        d.rectangle([x + 30, y + H_, x + 60, y + H_ + 33], fill=tuple(m.get('rgb') or (255, 255, 255)))
        d.text((x + 64, y + H_ + 2), f"{r['bilde']}", fill='black')
        d.text((x + 64, y + H_ + 16), f"{m.get('ord') or m.get('grunn', '')} {m.get('lys', '')} {r['dato']}"[:40], fill='black')
    os.makedirs(os.path.dirname(os.path.abspath(sti)), exist_ok=True); a.save(sti, quality=88)


def kandidater(K, bilder):
    """{id: [(r, m), ...]} med sikre lesninger, etter husregelen (to kulører på samme hus = ingen sikre)."""
    per = {}
    for r in bilder:
        try: m = les_en(K, r)
        except Exception as e: m = {'grunn': f'feil: {e}'}
        r['m'] = m
        if m.get('ord'): per.setdefault(r['id'], []).append((r, m))
    ut = {}
    for i, v in per.items():
        fam = {familie_av_ord(m['ord']) for _, m in v}
        if len(fam) != 1: continue
        # Endrer lesningen kulør på huset (mot det modellen har), må to ulike panoramaer si det samme: ett bilde kan stå på nabohuset.
        if T.familie(K.B[i].get('vegg')) not in fam and len({r['pano'] for r, _ in v}) < 2:
            for r, m in v: m['ute'] = 'endrer kulør, bare ett panorama'
            continue
        ut[i] = v
    return ut


def endrer(K, per):
    """Hus der lesningen gir en annen kulørfamilie enn modellen har: disse skal ses av et øye først."""
    return {i for i, v in per.items() if T.familie(K.B[i].get('vegg')) != familie_av_ord(v[0][1]['ord'])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ider', nargs='*'); ap.add_argument('--liste'); ap.add_argument('--ut', required=True); ap.add_argument('--ark'); ap.add_argument('--flett'); ap.add_argument('--status'); ap.add_argument('--avvist')
    x = ap.parse_args(); ider = set(x.ider)
    if x.liste: ider |= {h['id'] for h in json.load(open(x.liste, encoding='utf8'))['hus']}
    avvist = set(open(x.avvist, encoding='utf8').read().split()) if x.avvist and os.path.exists(x.avvist) else set()   # bilder øyekontrollen har underkjent
    K = Kart(); bilder = [r for r in les_bilder() if (not ider or r['id'] in ider) and r['bilde'] not in avvist]
    per = kandidater(K, bilder)
    ut = [side(r, m) for v in per.values() for r, m in v]
    os.makedirs(os.path.dirname(os.path.abspath(x.ut)), exist_ok=True)
    json.dump(ut, open(x.ut, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    if x.ark: ark(sorted([(r, m) for v in per.values() for r, m in v], key=lambda t: (t[0]['id'] not in endrer(K, per), t[0]['id'])), x.ark)
    if x.status:
        grunn = {}
        for r in bilder:
            grunn.setdefault(r['id'], []).append({'bilde': f"{r['mappe']}/{r['bilde']}", 'dato': r['dato'], 'les': r['m'].get('ord'), 'grunn': r['m'].get('ute') or r['m'].get('grunn')})
        json.dump({'fargelegges': sorted(per), 'endrer_kulor': sorted(endrer(K, per)), 'uten_sikker': {i: grunn.get(i, []) for i in sorted(ider - set(per))}},
                  open(x.status, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    if x.flett:
        gml = json.load(open(x.flett, encoding='utf8')); kjent = {(g['id'], g['side']['pano_url']) for g in gml}
        ny = [s for s in ut if (s['id'], s['side']['pano_url']) not in kjent]
        json.dump(gml + ny, open(x.flett, 'w', encoding='utf8'), ensure_ascii=False, indent=1); print(len(ny), 'nye sider flettet inn i', x.flett)
    print(f"{len(bilder)} bilder, {len(ut)} sikre sider på {len(per)} hus")


if __name__ == '__main__':
    main()
