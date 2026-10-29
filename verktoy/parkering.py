#!/usr/bin/env python3
"""Parkeringen i og rundt Gamlebyen: kommunens parkeringslag er fasit for hvilke plasser som finnes, kommunens nettsider for regler og
priser, ortofoto 2024 for hvor raden ligger.

    python3 verktoy/parkering.py hent    henter kommunens tre lag på nytt (kilder/parkering-kommunen.json) og sier hva som er endret
    python3 verktoy/parkering.py lag     data/parkering.json (én post per plass i lag 1 innenfor området)
    python3 verktoy/parkering.py ark     kontrollark rapport/torvet/parkering.png (kommunens punkter og de målte flatene, med kategori)
    python3 verktoy/parkering.py ark orto  det samme på ortofoto 2024: rapport/torvet/parkering-orto.jpg (bare lokalt)

Kilder (alle i kilder/):
  parkering-kommunen.json  TekniskDrift/Parkering lag 0 automater, 1 plasser, 2 soner (rådata, med kodelistene)
  parkering-regler.json    regler og 2026-priser skrevet av fra kommunens sider, med URL
  parkering-maalt.json     flater målt i ortofotoet for plasser som ikke er målt i flater-maalt.json, «samme_rad» og «uten_flate» (grunn)
  flater-maalt.json        flatene fra bakkeflatearbeidet 27.10 (leses, endres ikke her)
Antall skrives aldri på gjetning: står ANTALL tomt i laget, mangler «antall» i posten og «antall_kilde» sier at det er ukjent.
Kategoriene leses av TYPE, navn og kommentar med reglene i KATEGORI under (ingen håndplukking), så en ny plass i laget blir riktig
uten ny kode. id = parkering-1-<OBJECTID>, kommunens nøkkel.
"""
import json, math, os, re, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag

KILDER = os.path.join(ROT, 'kilder')
LES = lambda n: json.load(open(os.path.join(KILDER, n), encoding='utf8'))
OMRAADE = (-448, -448, 832, 576)          # samme som verktoy/flater.py (vollene og et belte rundt)
LAG1 = 'Fredrikstad kommune, TekniskDrift/Parkering lag 1'

# kategori: (navn, test på (TYPE-tekst, navn, kommentar) i små bokstaver). En plass kan ha flere.
KATEGORI = [
    ('hc', lambda t, n, k: 'forflytningshemmede' in t),
    ('el-lading', lambda t, n, k: 'el-bil' in t or 'kwt' in k or 'lading' in k),
    ('beboer', lambda t, n, k: 'beboer' in n or 'p-kort' in n or 'gyldig avtale' in k),
    ('buss', lambda t, n, k: 'buss' in k or 'buss' in n),
    ('bobil', lambda t, n, k: 'bobil' in t or 'bobil' in k or 'bobil' in n),
    ('avgift', lambda t, n, k: any(s in t for s in ('grønn sone', 'rød sone', 'gul sone')) or 'avgift' in k or 'sone' in k and 'grønn' in k),
    ('tidsbegrenset', lambda t, n, k: bool(re.search(r'forbudt over|maks \d', k))),
]


def kategorier(post):
    t, n, k = (post.get('type') or '').lower(), (post.get('navn') or '').lower(), (post.get('merknad') or '').lower()
    kat = [navn for navn, test in KATEGORI if test(t, n, k)]
    if 'ingen avgift' in (str(post.get('automat') or '') + ' ' + k).lower() and 'avgift' in kat:
        kat.remove('avgift')                      # f.eks. Skolegata: TYPE grønn sone, men AUTOMATNR «Ingen avgift»
    if 'gratis i 3' in k and 'tidsbegrenset' not in kat:
        kat.append('tidsbegrenset')
    return kat


def regler_tekst(post, kat, R):
    """Regler/tider i klartekst: kommunens kommentar på plassen + sonen (pris, avgiftstid, sesong) fra kommunens sider."""
    deler = []
    if post.get('merknad'):
        deler.append('Kommunen: «' + re.sub(r'\s+', ' ', post['merknad']).strip() + '»')
    k = (post.get('merknad') or '').lower(); t = (post.get('type') or '').lower()
    if 'avgift' in kat:
        sesong = 'rød sone' in k and 'grønn sone' in k
        deler.append(f"Grønn sone: {R['soner']['grønn']['pris']}; {R['soner']['grønn']['avgiftstid']}")
        if sesong:
            deler.append(f"Rød sone om sommeren (01.06.–31.08.): {R['soner']['rød']['pris']}")
        elif 'rød sone' in t:
            deler.append(f"Rød sone: {R['soner']['rød']['pris']}")
        deler.append('EasyPark: +15 %')
    if 'hc' in kat:
        deler.append('Reservert for kjøretøy med parkeringstillatelse for forflytningshemmede (kommunens lenke på plassen)')
    if 'beboer' in kat:
        deler.append('Bare for beboere/næring med avtaleparkering (1600 kr per år for beboere) i den tiden skiltet sier')
    if 'gratis i 3' in k:
        deler.append(R['kongsten']['tekst'].strip('«»'))
    return '. '.join(deler)


def lag():
    k = LES('parkering-kommunen.json'); R = LES('parkering-regler.json'); mine = LES('parkering-maalt.json')
    bakke = LES('flater-maalt.json')
    kode = lambda felt, v: None if v is None else k['koder'].get(felt, {}).get(str(v), v)
    from flater import rad
    x0, y0, x1, y1 = OMRAADE; ut = []
    dobbel = set(bakke['parkering']) & set(mine['parkering'])
    if dobbel:
        raise SystemExit(f'målt to steder (flater-maalt.json og parkering-maalt.json): {sorted(dobbel)}')
    for f in k['lag']['plasser']:
        p = f['properties']; x, y = datalag.til_modell(*f['geometry']['coordinates'])
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            continue
        pid = f"parkering-1-{p['OBJECTID']}"
        post = {'id': pid, 'navn': p.get('NAVN'), 'x': round(x, 1), 'y': round(y, 1), 'type': kode('TYPE', p.get('TYPE')),
                'antall': p.get('ANTALL'),
                'antall_kilde': f"{LAG1}, ANTALL" if p.get('ANTALL') is not None else f"ukjent: ANTALL er tomt i {LAG1}",
                'pris_laget': kode('PRIS', p.get('PRIS')), 'elbil': kode('ELBIL', p.get('ELBIL')),
                'automat': p.get('AUTOMATNR'), 'easypark': kode('EASYPARK', p.get('EASYPARK')), 'merknad': p.get('KOMMENTAR'),
                'lenke': p.get('LENKE'), 'kilde': LAG1, 'kilde_url': f"{k['url']}/1 (OBJECTID {p['OBJECTID']})", 'hentet': k['hentet']}
        post['kategori'] = kategorier(post)
        post['regler'] = regler_tekst(post, post['kategori'], R)
        post['regler_kilde'] = [R['kilder'][n] for n in ('gamlebyen', 'priser', 'avtaleparkering')]
        fl = bakke['parkering'].get(pid) or mine['parkering'].get(pid)
        if fl:
            post['p'] = fl['p'] if 'p' in fl else rad(fl['linje'], fl['bredde']); post['flate'] = fl.get('flate', 'asfalt')
            post['maalt'] = fl.get('grunn', 'ortofoto 2024')
        elif pid in mine.get('samme_rad', {}):
            post['samme_rad'] = mine['samme_rad'][pid]['rad']; post['uten_flate'] = mine['samme_rad'][pid]['grunn']
        elif pid in bakke.get('uten_flate', {}) or pid in mine.get('uten_flate', {}):
            post['uten_flate'] = bakke.get('uten_flate', {}).get(pid) or mine['uten_flate'][pid]
        ut.append({a: b for a, b in post.items() if b is not None and b != []})
    kjente = {u['id'] for u in ut}
    ukjente = (set(bakke['parkering']) | set(mine['parkering']) | set(mine.get('uten_flate', {})) | set(mine.get('samme_rad', {}))) - kjente
    if ukjente:
        raise SystemExit(f'målt/forklart for plasser som ikke finnes i kommunens lag: {sorted(ukjente)}')
    ut.sort(key=lambda u: int(u['id'].split('-')[-1]))
    with open(os.path.join(ROT, 'data', 'parkering.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(u, ensure_ascii=False, separators=(',', ':')) for u in ut) + '\n]\n')
    n = len(ut); m = sum(1 for u in ut if 'p' in u); g = sum(1 for u in ut if 'uten_flate' in u)
    print(f'{n} plasser, {m} med målt flate, {g} uten flate med grunn, {n - m - g} uten noe;',
          f"{sum(1 for u in ut if 'antall' in u)} med antall ({sum(u.get('antall', 0) for u in ut)} plasser), {sum(1 for u in ut if 'antall' not in u)} ukjent antall")
    return ut


def hent():
    """Kommunens lag på nytt; skriver kilder/parkering-kommunen.json og sier hvilke plasser som er nye, borte eller endret."""
    fil = os.path.join(KILDER, 'parkering-kommunen.json')
    gammel = json.load(open(fil, encoding='utf8')) if os.path.exists(fil) else {'lag': {}}
    import flater
    flater.hent.__globals__['hent_fliser'] = lambda *a, **kw: None    # bare parkeringen, ikke ortofotoet
    flater.hent()
    ny = json.load(open(fil, encoding='utf8'))
    for lag_, liste in ny['lag'].items():
        A = {f['properties']['OBJECTID']: f for f in gammel['lag'].get(lag_, [])}; B = {f['properties']['OBJECTID']: f for f in liste}
        print(f"{lag_}: {len(B)} (nye {sorted(set(B) - set(A))}, borte {sorted(set(A) - set(B))}, endret {sorted(i for i in set(A) & set(B) if A[i] != B[i])})")


FARGE = {'hc': (230, 120, 0), 'el-lading': (0, 170, 0), 'beboer': (160, 60, 200), 'buss': (0, 140, 200), 'bobil': (0, 140, 200),
         'avgift': (40, 70, 230), 'tidsbegrenset': (0, 170, 200)}


def ark(orto=False):
    """rapport/torvet/parkering.png: uten ortofoto (lisensen er ikke avklart, så arket kan ligge i repoet): kartets husomriss (data/bygg),
    målte parkeringsflater (fylt), kommunens punkter (sirkel)
    farget etter første kategori, med kommunens nummer, antall og sonekode. To utsnitt: Gamlebyen og Kongsten/Cicignon."""
    import cv2, numpy as np
    d = datalag.alle(); P = d['parkering']
    def tegn(x0, y0, x1, y1, mpp, tittel):
        W, H = int((x1 - x0) / mpp), int((y1 - y0) / mpp); im = np.full((H, W, 3), 248, np.uint8)
        px = lambda x, y: (int((x - x0) / mpp), int((y1 - y) / mpp))
        if orto:                                  # kontroll mot fotoet: bare lokalt (.gitignore), lisensen er ikke avklart
            import flater
            im = cv2.resize(flater.ortofoto(x0, y0, x1, y1, mpp)[0], (W, H))
        else:
            for b in d['bygg']:
                if not b.get('skjul'): cv2.fillPoly(im, [np.array([px(*a) for a in b['p']], np.int32)], (215, 215, 215))
        for p in P:
            if p.get('p'):
                c = FARGE.get((p.get('kategori') or ['avgift'])[0], (90, 90, 90))[::-1]
                ov = im.copy(); cv2.fillPoly(ov, [np.array([px(*a) for a in p['p']], np.int32)], c); im[:] = cv2.addWeighted(ov, 0.45, im, 0.55, 0)
                cv2.polylines(im, [np.array([px(*a) for a in p['p']], np.int32)], True, c, 1)
        for p in P:
            c = FARGE.get((p.get('kategori') or ['?'])[0], (90, 90, 90))[::-1]; q = px(p['x'], p['y'])
            if not (0 <= q[0] < W and 0 <= q[1] < H): continue
            cv2.circle(im, q, 5, c, -1 if p.get('p') else 2)
            lab = f"{p['id'].split('-')[-1]} {p.get('antall', '?')}" + (f" {p['easypark']}" if p.get('easypark') else '')
            cv2.putText(im, lab, (q[0] + 6, q[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (30, 30, 30), 1, cv2.LINE_AA)
        cv2.putText(im, tittel, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
        return im
    a = tegn(-170, -200, 260, 280, 0.5, 'Gamlebyen: nr antall(?=ukjent) EasyPark-kode; fylt = maalt flate, ring = bare kommunens punkt')
    b = tegn(-448, 230, -48, 590, 0.5, 'Cicignon og Tolboden'); c = tegn(232, -330, 632, 30, 0.5, 'Kongsten og Kongstenhallen')
    h = max(a.shape[0], b.shape[0] + c.shape[0])
    pad = lambda im, hh: np.vstack([im, np.full((hh - im.shape[0], im.shape[1], 3), 255, np.uint8)])
    ark_ = np.hstack([pad(a, h), pad(np.vstack([b, c]), h)])
    y = h - 14 * (len(FARGE) + 1)
    for i, (n, f) in enumerate(FARGE.items()):
        cv2.circle(ark_, (14, y + 14 * i), 5, f[::-1], -1); cv2.putText(ark_, n, (24, y + 14 * i + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    os.makedirs(os.path.join(ROT, 'rapport', 'torvet'), exist_ok=True)
    ut = os.path.join(ROT, 'rapport', 'torvet', 'parkering-orto.jpg' if orto else 'parkering.png'); cv2.imwrite(ut, ark_); print(ut, ark_.shape)


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else 'lag'
    ark(orto='orto' in sys.argv[2:]) if k == 'ark' else {'hent': hent, 'lag': lag}[k]()
