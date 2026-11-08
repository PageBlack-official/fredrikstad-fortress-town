#!/usr/bin/env python3
"""Test av farge_kandidater.py mot veggfarger som er kjent (kilder/gate/farger-rett.json, lest med øyet 07.11 og godkjent):
de 5 husene i TEST skal gi riktig kulørfamilie (T.familie av ordet, regelen «feil kulør er ikke lov»), og hele fasiten (2016+) skal ikke ha feil blant de sikre.
    SV_ROT=<mappe med sv*/> python3 verktoy/rett/test_farge_kandidater.py [kontaktark.jpg]   (exit 1 ved feil)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import farge_kandidater as FK

ROT = FK.ROT
TEST = ['bnr-193868142-3', 'bnr-193987370-3', 'bnr-193868029-0', 'pb-59-2', 'bnr-6275990-8']   # hvit, terrakotta, okerbrun, laks, oksiderød

fasit = {}
for g in json.load(open(os.path.join(ROT, 'kilder', 'gate', 'farger-rett.json'), encoding='utf8')):
    s = g['side']
    if FK.T.sv_aar(s['bilde_dato']) >= FK.MIN_AAR:
        fasit[s['retning'].split('verktoy/rett, ')[1].rstrip(')')] = s
K = FK.Kart()
rader, ark = [], []
for r in FK.les_bilder():
    s = fasit.get(r['bilde'])
    if not s or s['pano_url'] != f"{r['lat']}, {r['lon']} h {r['heading']}": continue
    m = FK.les_en(K, r); r['m'] = m; ark.append((r, m))
    rett = FK.familie_av_ord(s['vegg_farge']); les = FK.familie_av_ord(m['ord']) if m.get('ord') else None
    rader.append((r['bilde'], s['vegg_farge'], rett, m.get('ord'), les, m))
n_sikre = n_feil = 0
print('bilde'.ljust(20), 'kjent'.ljust(16), 'lest'.ljust(16), 'dom')
for b, o, rett, lo, les, m in sorted(rader, key=lambda x: (x[0] not in TEST, x[0])):
    dom = ('TREFF' if les == rett else 'FEIL') if lo else 'usikker'
    n_sikre += bool(lo); n_feil += dom == 'FEIL'
    print(('* ' if b in TEST else '  ') + b.ljust(18), f'{o} ({rett})'.ljust(22), f'{lo or "-"} ({les or "-"})'.ljust(22), dom.ljust(8), m.get('lab'), m.get('lys'), m.get('andel'), m.get('tekstur'), m.get('grunn', ''))
tr5 = sum(1 for b, o, rett, lo, les, m in rader if b in TEST and les == rett)
print(f'\ntesthusene: {tr5}/{len(TEST)} treff. Hele fasiten 2016+: {len(rader)} bilder, {n_sikre} sikre, {n_feil} feil kulør, {len(rader) - n_sikre} usikre (går til nye bilder eller øyet).')
# Del 2, uavhengig kontroll: hus der veggfargen er lest for hånd i Vegars Chrome 29.10 (vegg_kilde «Street View 2016+ (ord)») og som IKKE er med i fasiten over.
# Tersklene er aldri stilt mot disse.
import re
ord2 = {}
for x in K.B.values():
    m = re.match(r'Street View (20\d\d) \(([^)]*)', x.get('vegg_kilde') or '')
    if m and int(m.group(1)) >= FK.MIN_AAR and x.get('gml') and not x.get('skjul') and FK.fra_ord(m.group(2), FK.VEGG): ord2[x['id']] = m.group(2)
for b in fasit: ord2.pop(b.rsplit('-', 1)[0], None)
bilder = [r for r in FK.les_bilder() if r['id'] in ord2]
per = {}
for r in bilder:
    m = FK.les_en(K, r)
    if m.get('ord'): per.setdefault(r['id'], []).append((r, m))
ark2 = []; t = {'ett': [0, 0], 'to': [0, 0]}
for i, v in per.items():
    if len({FK.familie_av_ord(m['ord']) for _, m in v}) != 1: continue        # samme regel som kandidater(): to kulører på ett hus = ikke sikker
    g = 'to' if len({r['pano'] for r, _ in v}) >= 2 else 'ett'; r, m = v[0]
    hand = FK.fra_ord(ord2[i], FK.VEGG); les = FK.fra_ord(m['ord'], FK.VEGG); ok = FK.T.samme_kulor(hand, les)
    t[g][0] += 1; t[g][1] += not ok
    if not ok: print('  AVVIK', g, r['bilde'].ljust(18), 'for hånd:', ord2[i][:30], ' lest:', m['ord'], m['lab'], m['lys']); ark2.append((r, m))
print(f"uavhengig kontroll, per hus ({len(ord2)} hus lest for hånd 29.10, {len(bilder)} bilder; «samme kulør» = T.samme_kulor):")
print(f"  ett panorama: {t['ett'][0]} hus, {t['ett'][1]} avvik. To eller flere panoramaer: {t['to'][0]} hus, {t['to'][1]} avvik.")
if len(sys.argv) > 1: FK.ark(ark + ark2, sys.argv[1])
sys.exit(0 if tr5 >= 4 and n_feil == 0 else 1)
