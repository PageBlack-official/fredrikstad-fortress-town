"""Fasadesegmenter (30.10, natt/fasade2): hus med én kropp (sammenhengende møne i Kartverkets DOM, ett bygningsnummer i
Matrikkelen) der Vegars 2015-tegning viser flere fasader på samme vegg, hver med egen farge og egen vindusrytme.

Avgjørelsen (hovedagenten 30.10): kroppen og taket forblir ett hus (Kartverket/DOM vinner for geometri). Veggen deles i segmenter
langs fasaden, med farge per segment etter fargeregelen og vinduer etter tegningen; brannmurlinjen mellom to segmenter tegnes
som en tynn loddrett kant (src/07).

Data: kilder/fasadesegmenter.json, «dom»: {id: {godkjent, grunn}} = forslagene fra finn sett på kontaktarket (tegningens flater
per segment omrisset); bare godkjente hus og hus satt for hånd legges inn (finn gir mange falske: takflater, smale biter,
gavlvegger fra nabohuset når frihånden avviker). «hus»: per hus og vegg: {a, b (veggens ender i modellmeter, som da tegningen ble lest), side,
segmenter: [{fra_m, til_m, tegning_rgb, flater (stiene i .ai-fila)}]}. «for_haand»: true på et hus = funnet eller rettet for hånd;
finn rører det ikke. Rettelsen på bygget heter «fasadesegmenter»: [{a, b, segmenter: [{fra_m, til_m, vegg, kilde, aar}]}];
veggen slås opp på nytt i dagens omriss hver gang (nærmeste vegg med samme retning), så den tåler ny grunnmur og husdeling.

    python3 verktoy/fasadesegmenter.py finn [tegning ...]   leser tegningene (kontrollørens kamera, rapport/kontroll/_arbeid)
    python3 verktoy/fasadesegmenter.py kobling [tegning ...] legger segmentveggene uten fasadeavlesning inn i kilder/fasade-kobling.json
                                                             (så fasade_tegning.py les_for_haand leser vinduene på dem)
    python3 verktoy/fasadesegmenter.py                      rettelsene (idempotent; i kjeden etter vegg_nye.py)
    python3 verktoy/fasadesegmenter.py --tørt               viser bare

Fargeregelen per segment (LESMEG «Fargene»): Street View 2016+ > tegningen > Street View før 2015. Street View-siden som ser
veggen (streetview_fasader.gatevegg) gir farge til segmentet der siktlinja (heading fra kamerapunktet) treffer veggen; har siden
flere fasader («fasader»: [{rgb|farge}, …] fra venstre, sett fra kameraet) og like mange segmenter, får hvert segment sin.
Samme kulør i Street View og tegning: tegningens farge (som streetview_farger.py).

Segmentet finnes slik: tegningens flater som ligger på modellveggen i tegningens projeksjon (minst 70 % av bredden innenfor
veggen, og enten minst 60 % av flaten inne i veggflaten eller en vegg med loddrette sidekanter (fasade_tegning.er_vegg) med
bunnen innen 12 pt fra veggens bunnlinje; papir, strek, vinduer og flater under 4 % av veggen telles ikke; hver flate til én
vegg i hele tegningen: den beste), x-utstrekningen målt i meter langs veggen. Flater oppå hverandre (sokkel + vegg) er ett segment med
fargen til den største. Grensene måles i andel av den tegnede fasaden (frihånd: den er lengre eller kortere enn
modellveggen). Segmentene må dekke minst 60 % av veggen (ellers er registreringen for usikker) og være minst 1,2 m.
"""
import json, math, os, sys, datetime
import numpy as np
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
from shapely.geometry import Polygon, LineString

KILDE = os.path.join(ROT, 'kilder', 'fasadesegmenter.json')
GRUNN = 'fasadesegmenter fra kvartaltegningene (verktoy/fasadesegmenter.py, 30.10)'
# landemerkene har egne agenter og egen kode (rådhuset, Voldporten, kirka, Tøihuset): ikke segmenter her
IKKE = {'bnr-193972012', 'bnr-193869548', 'bnr-193867529', 'bnr-193870279'}
IKKE_TEGNINGER = {'kirke', 'Toihuset'}
MIN_SEG = 1.2
MIN_DEKNING = 0.6
NYERE_ENN = 2016


def les_kilde():
    if os.path.exists(KILDE):
        return json.load(open(KILDE, encoding='utf8'))
    return dict(om=__doc__.split('\n\n')[2], hus={})


def skriv_kilde(d):
    open(KILDE, 'w', encoding='utf8').write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')


def _kompass(n):
    a = (math.degrees(math.atan2(n[0], n[1])) + 360) % 360
    return ['N', 'NØ', 'Ø', 'SØ', 'S', 'SV', 'V', 'NV'][int((a + 22.5) // 45) % 8]


def finn_tegning(navn, logg=print, fin=True):
    """Segmentene i én tegning: {id: [vegg, …]} for vegger med minst to segmenter."""
    import kontroll as KT, fasade_tegning as FT, vegger as VG
    D = KT.data(); BY = {x['id']: x for x in D['bygg']}
    omg = VG.Omgivelser(D['bygg'], D['veier'], D['gardsrom'])
    K = KT.les_kamera(navn)
    F, _ = FT.flater(navn)
    # alle synlige modellvegger i tegningen
    W = []
    for i in K['bygg']:
        x = BY.get(i)
        if not x or x.get('skjul') or x.get('kirke') or i in IKKE: continue
        P = KT.P_hus(K, i); A2 = P[:, :2]
        hf = K.get('hus_forskyvning', {}).get(i)
        if fin and hf and hf['median_etter_pt'] < hf['median_pt']:       # husets egen finjustering (frihånd innen blokken, ±10 pt)
            P = P.copy(); P[:, 3] += hf['beste_forskyvning_pt']
        for w in VG.vegger(x, omg, slaa_sammen=True):
            if w['L'] < 3.0 or (A2 @ w['n'])[1] <= 1e-6: continue     # vender bort fra tegneren
            a, c = np.array(w['a'], float), np.array(w['c'], float)
            q = Polygon([KT.proj(P, *a, 0), KT.proj(P, *c, 0), KT.proj(P, *c, x['h']), KT.proj(P, *a, x['h'])]).buffer(0)
            if q.area < 4: continue
            W.append(dict(id=i, a=a, c=c, L=w['L'], u=(c - a) / w['L'], n=w['n'], P=P, q=q, felles=w['felles']))
    # hver veggflate til én vegg: mest overlapp, bunnkanten på veggens bunnlinje
    paa = {}
    for fl in F:
        fa = fl['farge']
        if min(fa) > 0.97 or (max(fa) < 0.36 and max(fa) - min(fa) < 0.07): continue      # papir, strek
        Pf = fl['ytre']
        if Pf.area < 12: continue
        x0, y0, x1, y1 = Pf.bounds; xm = 0.5 * (x0 + x1)
        g_ = Pf.intersection(LineString([(xm, -1e4), (xm, 1e4)]))
        if g_.is_empty: continue
        bunn = g_.bounds[3]; ev = FT.er_vegg(Pf)
        best = None
        for k, w in enumerate(W):
            if Pf.area < 0.04 * w['q'].area: continue
            ov = w['q'].intersection(Pf).area / Pf.area
            if ov < 0.35: continue
            xa, ya = KT.proj(w['P'], *w['a'], 0); xb, yb = KT.proj(w['P'], *w['c'], 0)
            if abs(xb - xa) < 1e-6: continue
            inne = (min(x1, max(xa, xb)) - max(x0, min(xa, xb))) / max(x1 - x0, 1e-6)
            if inne < 0.5: continue
            yb_ = ya + (yb - ya) * (min(max(xm, min(xa, xb)), max(xa, xb)) - xa) / (xb - xa)
            d = abs(bunn - yb_)
            # godtatt: nesten hele flaten inne i veggflaten, eller en vegg (loddrette sidekanter) med bunnen nær veggens bunn
            if not (ov >= 0.6 or (ev and d <= 12)): continue
            sc = ov - d / 40
            if best is None or sc > best[0]: best = (sc, k)
        if best:
            paa.setdefault(best[1], []).append(fl)
    ut = {}
    for k, fls in paa.items():
        w = W[k]; P = w['P']
        den = P[0, 0] * w['u'][0] + P[0, 1] * w['u'][1]
        if abs(den) < 1e-6: continue
        s_ = lambda xx: (xx - (P[0, 0] * w['a'][0] + P[0, 1] * w['a'][1] + P[0, 3])) / den
        T = []
        for fl in fls:
            x0, _, x1, _ = fl['ytre'].bounds
            sa, sb = sorted([s_(x0), s_(x1)])
            T.append([sa, sb, [int(round(c * 255)) for c in fl['farge']], [fl['i']], fl['ytre'].area])
        if not T: continue
        # frihånd: tegningens fasade er lengre eller kortere enn modellveggen; grensene måles i andel av den tegnede fasaden
        lo, hi = min(t[0] for t in T), max(t[1] for t in T)
        if hi - lo < 1.0: continue
        for t in T:
            t[0] = (t[0] - lo) / (hi - lo) * w['L']; t[1] = (t[1] - lo) / (hi - lo) * w['L']
        T = [t for t in T if t[1] - t[0] >= 0.3]
        T.sort()
        seg = []
        for t in T:     # oppå hverandre / mer enn 0,6 m overlapp: samme fasade (sokkel + vegg, dør tegnet som flate)
            if seg and t[0] < seg[-1][1] - 0.6:
                s0 = seg[-1]; s0[1] = max(s0[1], t[1]); s0[3] += t[3]
                if t[4] > s0[4]: s0[2] = t[2]; s0[4] = t[4]
                continue
            seg.append(list(t))
        # for korte biter slås inn i naboen med størst flate
        endret = True
        while endret and len(seg) > 1:
            endret = False
            for j, s in enumerate(seg):
                if s[1] - s[0] < MIN_SEG:
                    nb = j - 1 if j == len(seg) - 1 or (j > 0 and seg[j - 1][4] >= seg[j + 1][4]) else j + 1
                    o = seg[nb]; o[0] = min(o[0], s[0]); o[1] = max(o[1], s[1]); o[3] += s[3]
                    seg.pop(j); endret = True; break
        if len(seg) < 2: continue
        dekning = sum(s[1] - s[0] for s in seg) / w['L']
        if dekning < MIN_DEKNING:
            logg(f"  {navn} {w['id']} vegg {_kompass(w['n'])}: {len(seg)} fasader, men dekker bare {dekning:.0%} av veggen – hoppet over"); continue
        # grensene: midt mellom nabosegmentene; første fra veggens start, siste til slutten
        grenser = [0.0] + [round(0.5 * (seg[j][1] + seg[j + 1][0]), 2) for j in range(len(seg) - 1)] + [round(w['L'], 2)]
        segs = [dict(fra_m=grenser[j], til_m=grenser[j + 1], tegning_rgb=s[2], flater=s[3]) for j, s in enumerate(seg)]
        ut.setdefault(w['id'], []).append(dict(a=[round(float(v), 2) for v in w['a']], b=[round(float(v), 2) for v in w['c']],
                                               side=_kompass(w['n']), tegning=navn, dekning=round(dekning, 2), segmenter=segs))
        logg(f"  {navn} {w['id']} vegg {_kompass(w['n'])} ({w['L']:.1f} m): " + ' | '.join(f"{s['fra_m']:.1f}-{s['til_m']:.1f} {tuple(s['tegning_rgb'])}" for s in segs))
    return ut


def finn(navner, logg=print):
    import kontroll as KT
    d = les_kilde(); H = d['hus']
    for n in navner:
        if n in IKKE_TEGNINGER: continue
        if not os.path.exists(os.path.join(KT.ARB, n + '-kamera.json')):
            logg(f"  {n}: mangler kamera (kontroll.py kamera {n})"); continue
        # husene denne tegningen eide sist, og som ikke er satt for hånd, leses på nytt
        for i in [i for i, v in H.items() if v.get('tegning') == n and not v.get('for_haand')]:
            del H[i]
        # to lesninger: blokkens forskyvning alene og med husets egen finjustering; per vegg den som dekker mest
        R0, R1 = finn_tegning(n, lambda *_: None, fin=False), finn_tegning(n, logg, fin=True)
        RR = {}
        for i in set(R0) | set(R1):
            vv = {}
            for v in R0.get(i, []) + R1.get(i, []):
                kk = v['side']
                if kk not in vv or (len(v['segmenter']), v['dekning']) > (len(vv[kk]['segmenter']), vv[kk]['dekning']):
                    vv[kk] = v
            RR[i] = list(vv.values())
        for i, V in RR.items():
            if i in H and (H[i].get('for_haand') or H[i]['tegning'] != n):
                # samme hus i to tegninger: den med best dekning
                if H[i].get('for_haand') or max(v['dekning'] for v in H[i]['vegger']) >= max(v['dekning'] for v in V): continue
            H[i] = dict(tegning=n, vegger=V)
    d['laget'] = datetime.date.today().isoformat(); d['verktoy'] = 'verktoy/fasadesegmenter.py finn'
    d['hus'] = dict(sorted(H.items()))
    skriv_kilde(d)
    logg(f"{len(H)} hus med fasadesegmenter, {sum(len(v['vegger']) for v in H.values())} vegger")


def _vegg_naa(x, omg, a, b):
    """Veggen i dagens omriss som svarer til den lagrede (a, b): samme retning (innen 12°), nærmest midtpunktet (under 2 m)."""
    import vegger as VG
    a, b = np.array(a, float), np.array(b, float); u = (b - a) / max(np.linalg.norm(b - a), 1e-9); m = 0.5 * (a + b)
    best = None
    for w in VG.vegger(x, omg, slaa_sammen=True):
        if abs(float(w['u'] @ u)) < math.cos(math.radians(12)): continue
        d = abs(float((m - w['a']) @ w['n']))
        t = float((m - w['a']) @ w['u'])
        if d < 2.0 and -1 <= t <= w['L'] + 1 and (best is None or d < best[0]):
            best = (d, w)
    return best[1] if best else None


def sv_farger(x, w, omg, sv, logg):
    """Street View 2016+ på veggen w: [(s langs veggen, rgb, kilde, aar)] (s = None: hele siden har flere fasader -> liste)."""
    import streetview_fasader as SVF, streetview_farger as SF, tak_farge as T, vegger as VG
    if not sv: return []
    V = VG.vegger(x, omg, slaa_sammen=True)
    ut = []
    for sd in SVF.sider(sv):
        aar = T.sv_aar(sd.get('bilde_dato')) or T.sv_vegg_aar(sv)
        if not aar or aar < NYERE_ENN: continue
        C, heading = SVF.kamera(sd)
        if C is None: continue
        wi, _ = SVF.gatevegg(x, V, omg, C, heading, False)
        if wi is None: wi = SVF.retningsvegg(x, V, sd.get('retning'))
        if wi is None: continue
        v = V[wi]
        if abs(float(v['u'] @ w['u'])) < math.cos(math.radians(12)) or abs(float((v['a'] - w['a']) @ w['n'])) > 1.0: continue
        kilde = f"Street View {aar}"
        fas = sd.get('fasader')
        if isinstance(fas, list) and fas:
            rgbs = [f.get('rgb') or SF.fra_ord(f.get('farge'), SF.VEGG) for f in fas]
            ut.append(('flere', rgbs, kilde, aar)); continue
        rgb = SF.fra_ord(sd.get('vegg_farge'), SF.VEGG) or SF.fra_tall(sd.get('vegg_rgb'), sd.get('lys'))
        if not rgb: continue
        f = np.array([math.sin(math.radians(heading)), math.cos(math.radians(heading))])
        den = float(f @ w['n'])
        if abs(den) < 1e-6: continue
        t = float((w['a'] - C) @ w['n']) / den        # strålen C + t f treffer veggens linje
        q = C + t * f; s = float((q - w['a']) @ w['u'])
        ut.append((min(max(s, 0.0), w['L']), list(rgb), f"{kilde} ({sd.get('vegg_farge')})", aar))
    return ut


def legg_inn(tørt=False, logg=print):
    import datalag, vegger as VG, tak_farge as T
    d = les_kilde()
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    D = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, ret), grunn)
    BY = {x['id']: x for x in D['bygg']}; omg = VG.Omgivelser(D['bygg'], D['veier'], D['gardsrom'])
    avl = json.load(open(os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json'), encoding='utf8'))
    dato = datetime.date.today().isoformat(); nye = []; rapport = {}
    dom = d.get('dom', {})
    for i, h in d['hus'].items():
        x = BY.get(i)
        if not x or x.get('skjul') or i in IKKE: continue
        if not h.get('for_haand') and not (dom.get(i) or {}).get('godkjent'): continue
        ut_v = []
        for vg in h['vegger']:
            w = _vegg_naa(x, omg, vg['a'], vg['b'])
            if w is None:
                logg(f"  {i}: veggen {vg['side']} finnes ikke lenger i omrisset – hoppet over"); continue
            a0, b0 = np.array(vg['a'], float), np.array(vg['b'], float); u0 = (b0 - a0) / np.linalg.norm(b0 - a0)
            # segmentgrensene fra den lagrede veggen over på dagens vegg (punktene langs linja projiseres)
            sgn = 1 if float(u0 @ w['u']) > 0 else -1
            seg = []
            for s in vg['segmenter']:
                p0 = float((a0 + u0 * s['fra_m'] - w['a']) @ w['u']); p1 = float((a0 + u0 * s['til_m'] - w['a']) @ w['u'])
                seg.append(dict(s, _s0=min(p0, p1), _s1=max(p0, p1)))
            seg.sort(key=lambda s: s['_s0'])
            seg[0]['_s0'] = 0.0; seg[-1]['_s1'] = w['L']
            for s in seg:
                s['vegg'] = list(s['tegning_rgb']); s['kilde'] = f"kvartaltegningen {h['tegning']}"; s['aar'] = 2015
            for sv in sv_farger(x, w, omg, avl.get(i), logg):
                if sv[0] == 'flere':
                    rgbs = sv[1] if sgn > 0 else sv[1]       # fra venstre sett fra kameraet = fra venstre sett utenfra
                    if len(rgbs) == len(seg):
                        for s, c in zip(seg if True else seg, rgbs):
                            if c: s['vegg'] = list(c); s['kilde'] = sv[2] + ' (flere fasader)'; s['aar'] = sv[3]
                    continue
                s_, rgb, kilde, aar = sv
                s = next((s for s in seg if s['_s0'] <= s_ <= s['_s1']), None)
                if s is None: continue
                if T.samme_kulor(s['vegg'], rgb):
                    s['kilde'] = f"{kilde} = tegningen: tegningens farge"; s['aar'] = aar
                else:
                    s['vegg'] = rgb; s['kilde'] = f"{kilde}; tegningen har {T.familie(s['tegning_rgb'])}"; s['aar'] = aar
            ut_v.append(dict(a=[round(float(v), 2) for v in w['a']], b=[round(float(v), 2) for v in w['c']],
                             segmenter=[dict(fra_m=round(s['_s0'], 2), til_m=round(s['_s1'], 2), vegg=s['vegg'], kilde=s['kilde'], aar=s['aar']) for s in seg]))
        if ut_v:
            nye.append({"emne": "bygg", "id": i, "op": "sett", "felt": "fasadesegmenter", "verdi": ut_v, "hvem": "Claude", "dato": dato, "grunn": GRUNN})
            rapport[i] = ut_v
    for i, v in rapport.items():
        for w in v:
            logg(f"  {i}: " + ' | '.join(f"{s['fra_m']:.1f}-{s['til_m']:.1f} {tuple(s['vegg'])} [{s['kilde'][:40]}]" for s in w['segmenter']))
    logg(f"{len(rapport)} hus fikk fasadesegmenter ({sum(len(v) for v in rapport.values())} vegger, {sum(len(w['segmenter']) for v in rapport.values() for w in v)} segmenter)")
    if not tørt:
        datalag.skriv_rettelser(ret + nye)
        os.makedirs(os.path.join(ROT, 'rapport', 'fasadesegmenter'), exist_ok=True)
        json.dump(rapport, open(os.path.join(ROT, 'rapport', 'fasadesegmenter', 'segmenter.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return rapport


def kobling(navner, logg=print):
    """Segmentvegger uten fasadeavlesning i tegningen: flatene inn i kilder/fasade-kobling.json som {"f": [...], "side": "SV@k"}
    (k = veggen i vegger.vegger slått sammen), så les_for_haand leser vinduene og dørene på hver fasade."""
    import datalag, vegger as VG
    d = les_kilde(); D = datalag.alle(); BY = {x['id']: x for x in D['bygg']}; omg = VG.Omgivelser(D['bygg'], D['veier'], D['gardsrom'])
    kf = os.path.join(ROT, 'kilder', 'fasade-kobling.json'); KB = json.load(open(kf, encoding='utf8'))
    endret = set(); dom = d.get('dom', {})
    for i, h in d['hus'].items():
        n = h['tegning']
        if not h.get('for_haand') and not (dom.get(i) or {}).get('godkjent'): continue
        if navner and n not in navner: continue
        x = BY.get(i)
        if not x or n not in KB: continue
        avf = os.path.join(ROT, 'kilder', 'fasade-tegning', n + '.json')
        lest = json.load(open(avf, encoding='utf8'))['vegger'] if os.path.exists(avf) else []
        V = VG.vegger(x, omg, slaa_sammen=True)
        for vg in h['vegger']:
            w = _vegg_naa(x, omg, vg['a'], vg['b'])
            if w is None: continue
            k = next(k for k, v in enumerate(V) if np.allclose(v['a'], w['a']) and np.allclose(v['c'], w['c']))
            har = any(v_['id'] == i and abs(float((np.array(v_['a']) + np.array(v_['b'])) / 2 @ w['n'] - (w['a'] @ w['n']))) < 1.0
                      and abs(float((np.array(v_['b']) - np.array(v_['a'])) @ w['u'])) > 0.5 * w['L'] for v_ in lest)
            if har: continue
            fl = sorted(set(f for s in vg['segmenter'] for f in s['flater']))
            fam = 'SV' if 180 <= (math.degrees(math.atan2(w['n'][0], w['n'][1])) + 360) % 360 < 270 else 'SØ'
            hus = KB[n].setdefault('hus', {}).setdefault(i, [])
            ny = {"f": fl, "side": f"{fam}@{k}", "fra": 0, "til": 1, "grunn": "fasadesegmenter: tegningen viser flere fasader på veggen (verktoy/fasadesegmenter.py kobling)"}
            if not any(isinstance(e, dict) and e.get('side') == ny['side'] for e in hus):
                hus.append(ny); endret.add(n); logg(f"  {n} {i}: vegg {fam}@{k} ({vg['side']}) flater {fl}")
    if endret:
        open(kf, 'w', encoding='utf8').write(json.dumps(KB, ensure_ascii=False, indent=1) + '\n')
    logg(f"fasade-kobling: {', '.join(sorted(endret)) or 'ingen endring'}")
    return endret


if __name__ == '__main__':
    a = sys.argv[1:]
    import kontroll as KT
    if a and a[0] == 'finn':
        finn(a[1:] or KT.TEGNINGER)
    elif a and a[0] == 'kobling':
        kobling(a[1:])
    else:
        legg_inn('--tørt' in a)
