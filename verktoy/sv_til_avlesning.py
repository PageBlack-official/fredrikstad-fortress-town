#!/usr/bin/env python3
"""Lesningene fra Street View-bildene (07.11) inn i gatevandringen.

    python3 verktoy/sv_til_avlesning.py LESEMAPPE

LESEMAPPE/*.json: lister med én lesning per bilde (felt: bilde, id, del, deler, synlig, vegg, tak, takform, etasjer, piper, takvinduer,
dorfarge, karmfarge, maalt [{type, u0, u1, v0, v1, farge?}], merknad). Bildets kamera står i rapport/gate/sv/hent-*.json.
Skriver standpunktene (sv-<id>-<del>) til kilder/gate/standpunkter.json og lesningene til kilder/gate/avlesning.json.
Vegars egne lesninger (hvem = Vegar) går foran: et hus han har lest, får ikke en lesning fra bildene. Idempotent: egne linjer
(hvem = Claude, standpunkt sv-…) byttes ut hver gang.
"""
import json, os, sys, glob, re
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROT, 'kilder', 'gate', 'avlesning.json'); S = os.path.join(ROT, 'kilder', 'gate', 'standpunkter.json')
FELT = ('vegg', 'tak', 'takform', 'etasjer', 'piper', 'takvinduer', 'dorfarge', 'karmfarge', 'hjorner', 'v_bakke', 'maalt', 'merknad')


def main(mappe):
    kam = {}
    for f in glob.glob(os.path.join(ROT, 'rapport', 'gate', 'sv', 'hent-*.json')):
        kam.update({k: v for k, v in json.load(open(f)).items() if not k.startswith('_')})
    avl = [a for a in json.load(open(A, encoding='utf8')) if not str(a.get('standpunkt', '')).startswith('sv-')]
    sp = [s for s in json.load(open(S, encoding='utf8')) if not s['navn'].startswith('sv-')]
    vegars = {a['id'] for a in avl if a.get('hvem') == 'Vegar'}
    n = hopp = usynlig = skygge = 0; tvil = []
    for f in sorted(glob.glob(os.path.join(mappe, '*.json'))):
        for r in json.load(open(f, encoding='utf8')):
            b = r['bilde']; k = kam.get(b)
            if not k or k.get('mangler'):
                continue
            if not r.get('synlig', True):
                usynlig += 1; continue
            m = (r.get('merknad') or '').lower()
            # leseren tviler på at det er riktig bygg midt i bildet (garasje, uthus, carport, annet hus): ingen lesning (07.11)
            if re.search(r'feil hus|annet hus|kan være .*som menes|usikkert om det er riktig|garasje|uthus|carport|samme hus som|trolig samme', m):
                tvil.append(b); continue
            if re.search(r'skygge|motlys', m):          # fargen fra pikslene er for mørk: veggfargen fra de andre kildene står
                r = dict(r); r.pop('vegg', None); skygge += 1
            if r['id'] in vegars:
                hopp += 1; continue
            aar_mnd = (k.get('dato') or '')
            navn = 'sv-' + b
            sp.append({'navn': navn, 'pano': k.get('pano'), 'dato': aar_mnd, 'lat': k['lat'], 'lon': k['lon'], 'heading': k['heading'],
                       'pitch': 93, 'fov': k['fov'], 'oye': 2.5, 'bredde': 1280, 'hoyde': 720})
            a = {'id': r['id'], 'standpunkt': navn, 'hvem': 'Claude', 'kilde': f'Street View {aar_mnd}, lest 07.11',
                 'del': r.get('del', 0), 'deler': r.get('deler', 1)}
            a.update({x: r[x] for x in FELT if r.get(x) not in (None, '', [])})
            avl.append(a); n += 1
    json.dump(sp, open(S, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(avl, open(A, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'{n} lesninger inn, {usynlig} bilder uten huset synlig, {len(tvil)} der leseren tviler på bygget, {skygge} uten veggfarge (skygge), {hopp} hus lest av Vegar (hans lesning gjelder)')
    json.dump(tvil, open(os.path.join(ROT, 'rapport', 'gate', 'tvil.json'), 'w'))


if __name__ == '__main__':
    main(sys.argv[1])
