#!/usr/bin/env python3
"""Sokkelen (kjeller/natursteinsetasje) fra Street View-avlesningen (02.11, avvik A10).

    python3 verktoy/sokkel.py          rettelser «sokkel» for husene der avlesningen beskriver sokkelen (idempotent; --tørt viser bare)

Kilde: kilder/streetview/avlesning.json, sider[].kjeller_sokkel og materialet (02.11: «1. etg naturstein» = etasje, «murt naturstein» = hele;
høyden for dem regnes av datalag.sokkel_etasje), (fritekst lest av i Street View 29.10, f.eks. «grov grå/rosa
natursteinsokkel ca. 1.2 m med kjellervinduer», «grå pusset sokkel ca. 0.4 m»). Regelen:
- materialet: naturstein/granitt/gråstein/kvader/bruddstein -> type «naturstein» (tegnes med steinmønster i src/05),
  pusset -> «puss» (flat farge). Står bare «grå» eller «lav», er materialet ukjent og huset hoppes over.
- høyden: «ca. X m» i teksten; ellers «høy» 1,2 m, «lav» 0,4 m, ellers 0,6 m. Aldri høyere enn vegghøyden minus 1 m.
- fargen: grå (standard), grå/rosa, lys/gul, mørk — tegningens dempede toner, ikke fotografi.
Merknadene (kilder/bygg-merknader.json, f.eks. Artillerigårdens natursteinsetasje på 3,1 m) og hus med eget fasadeverktøy
(datalag.EGNE_FASADER) går foran: verktøyet står i kjeden før bygg_merknader.py og hopper over EGNE_FASADER.
"""
import json, os, re, sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag  # noqa: E402

GRUNN = 'sokkel fra Street View-avlesningen (verktoy/sokkel.py, 02.11)'
STEIN = re.compile(r'naturstein|granitt|gråstein|kvader|bruddstein', re.I)
PUSS = re.compile(r'pusset', re.I)
# første etasje i stein: «1. etg kvader/bruddstein», «tegl over grov natursteinsmur», «natursteinsetasje», «naturstein (hele 1. etg)»
ETASJE = re.compile(r'1\. ?etg[^,;]*(naturstein|kvader|bruddstein|granitt)|(naturstein|kvader|bruddstein)[^,;]*1\. ?etg|natursteinsetasje|over grov natursteinsmur', re.I)
# hele veggen i stein: materialet er naturstein (ikke sokkel)
HELE = re.compile(r'^\s*(murt |grå )?(naturstein|bruddstein|gråstein)|naturstein \(grov kvader\)', re.I)
FARGER = {  # (farge, skygge)
    'naturstein': ([174, 168, 160], [118, 114, 110]),
    'naturstein_rosa': ([180, 166, 160], [122, 112, 110]),
    'naturstein_lys': ([192, 184, 166], [130, 124, 112]),
    'naturstein_mork': ([140, 134, 128], [96, 92, 88]),
    'puss': ([188, 184, 176], [128, 126, 120]),
}


def les_sokkel(tekst):
    """Fritekst -> (type, h, fargenøkkel) eller None."""
    t = tekst.lower()
    if STEIN.search(t): typ = 'naturstein'
    elif PUSS.search(t) and 'sokkel' in t: typ = 'puss'
    else: return None
    m = re.search(r'ca\.?\s*([0-9]+(?:[.,][0-9]+)?)\s*m\b', t)
    h = float(m.group(1).replace(',', '.')) if m else (1.2 if 'høy' in t else 0.4 if 'lav' in t else 0.6)
    if typ == 'puss': nok = 'puss'
    elif 'rosa' in t: nok = 'naturstein_rosa'
    elif 'lys' in t or 'gul' in t: nok = 'naturstein_lys'
    elif 'mørk' in t: nok = 'naturstein_mork'
    else: nok = 'naturstein'
    return typ, h, nok


def beregn(d=None):
    d = d or datalag.alle(); BY = {x['id']: x for x in d['bygg']}
    sys.path.insert(0, os.path.join(ROT, 'verktoy')); import sv_kobling
    A = sv_kobling.les(d)   # bare observasjoner som peker på huset (avvik A12)
    ut = {}
    for i, rec in A.items():
        if i not in BY or i in datalag.EGNE_FASADER or BY[i].get('skjul'): continue
        # hele etasjen eller hele veggen i stein (materialet sier det): høyden regnes av datalag.sokkel_etasje
        mat = ' '.join(str(o.get(k) or '') for o in [rec] + list(rec.get('sider') or []) for k in ('materiale', 'vegg_materiale')).lower()
        vf = ' '.join(str((o.get('vegg') or {}).get('farge') if isinstance(o.get('vegg'), dict) else o.get('vegg_farge') or '') for o in [rec] + list(rec.get('sider') or [])).lower()
        etasje = bool(ETASJE.search(mat) or ETASJE.search(vf))
        hele = not etasje and bool(HELE.search(mat)) and not re.search(r'sokkel|over|kalket|puss', mat)
        if etasje or hele:
            nok = 'naturstein_rosa' if 'rosa' in mat + vf else 'naturstein'
            f, sk = FARGER[nok]
            for j in (BY[i].get('floyer') or [i]):
                if j in BY and not BY[j].get('skjul'):
                    ut[j] = {'farge': f, 'skygge': sk, 'type': 'naturstein', ('etasje' if etasje else 'hele'): True}
            continue
        beste = None
        tekster = [s.get('kjeller_sokkel') for s in rec.get('sider') or []] + [m for m in re.split(r'[,;]', mat) if 'sokkel' in m]
        for tk in tekster:
            if not isinstance(tk, str): continue
            r = les_sokkel(tk)
            if r and (beste is None or r[1] > beste[1]): beste = r
        if not beste: continue
        typ, h, nok = beste
        h = round(min(h, max(0.0, float(BY[i].get('h') or 0) - 1.0)), 2)
        if h < 0.25: continue
        f, sk = FARGER[nok]
        for j in (BY[i].get('floyer') or [i]):   # bygg i fløyer (Tøihuset): samme sokkel på alle fløyene
            if j in BY and not BY[j].get('skjul'): ut[j] = {'h': h, 'farge': f, 'skygge': sk, 'type': typ}
    return ut


def main(tørt=False):
    ut = beregn()
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    ret += [{'emne': 'bygg', 'id': i, 'op': 'sett', 'felt': 'sokkel', 'verdi': v, 'hvem': 'Claude', 'dato': '2026-11-02', 'grunn': GRUNN}
            for i, v in sorted(ut.items())]
    if not tørt: datalag.skriv_rettelser(ret)
    n = sum(1 for v in ut.values() if v['type'] == 'naturstein'); ne = sum(1 for v in ut.values() if v.get('etasje')); nh = sum(1 for v in ut.values() if v.get('hele'))
    print(f"{len(ut)} hus fikk sokkel fra Street View: {n} naturstein ({ne} hel etasje, {nh} hele veggen), {len(ut) - n} puss")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
