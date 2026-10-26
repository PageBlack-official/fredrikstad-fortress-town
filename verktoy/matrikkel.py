#!/usr/bin/env python3
"""Kobler hvert bygg i kartet til statens nøkkel: bygningsnummeret i Matrikkelen (Kartverket, CC BY 4.0).

  python3 verktoy/matrikkel.py hent    henter bygningspunktene rundt Gamlebyen til kilder/matrikkel-bygningspunkt.json
  python3 verktoy/matrikkel.py koble   gir byggene id og matrikkelfelt (data/bygg.json) og fører nye id-er i kilder/id-register.txt

Koblingen kan kjøres på nytt når som helst: et bygg som har id, beholder den. Nye bygg får neste id.
Hvorfor bygningsnummer: det er nøkkelen kommunen, Forsvarsbygg, meglere og Riksantikvaren bruker, og det er det samme
i alle norske byer. Se datalag.py for hele ID-regelen.
"""
import json, os, sys, urllib.request, xml.etree.ElementTree as ET, datetime

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
from datalag import til_modell, les  # noqa: E402

WFS = 'https://wfs.geonorge.no/skwms1/wfs.matrikkelen-bygningspunkt'
BBOX = (59.193, 10.935, 59.212, 10.970)        # lat/lon, litt romsligere enn kartet
KILDE = os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json')
REGISTER = os.path.join(ROT, 'kilder', 'id-register.txt')
NAER = 4.0                                     # meter: punkt like utenfor fotavtrykket (punktet er satt for hånd i matrikkelen)
NS = {'app': 'http://skjema.geonorge.no/SOSI/produktspesifikasjon/Matrikkelen-Bygningspunkt/20211101',
      'gml': 'http://www.opengis.net/gml/3.2', 'wfs': 'http://www.opengis.net/wfs/2.0'}


def hent():
    q = (f"?service=WFS&version=2.0.0&request=GetFeature&typeNames=app:Bygning&count=10000"
         f"&srsName=urn:ogc:def:crs:EPSG::4326&bbox={BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]},urn:ogc:def:crs:EPSG::4326")
    xml = urllib.request.urlopen(urllib.request.Request(WFS + q, headers={'User-Agent': 'pageblack-smartoldtown'}), timeout=120).read()
    rot = ET.fromstring(xml)
    t = lambda e, n: (e.findtext('app:' + n, namespaces=NS) or None)
    pkt = []
    for e in rot.iter('{%s}Bygning' % NS['app']):
        lat, lon = map(float, e.find('.//gml:pos', NS).text.split())
        bruk = e.findall('.//app:Bruksenhet', NS)
        pkt.append({'bygningsnummer': int(t(e, 'bygningsnummer')), 'uuid': t(e, 'uuidBygning'), 'status': t(e, 'bygningsstatus'),
                    'type': int(t(e, 'bygningstype') or 0), 'kulturminne': t(e, 'harKulturminne') == 'true',
                    'sefrak': t(e, 'harSefrakminne') == 'true', 'naringsgruppe': t(e, 'naringsgruppe'),
                    'adresser': sorted({b.findtext('app:adresseId', namespaces=NS) for b in bruk} - {None}),
                    'matrikkelenheter': sorted({b.findtext('app:matrikkelenhetId', namespaces=NS) for b in bruk} - {None}),
                    'oppdatert': (t(e, 'oppdateringsdato') or '')[:10], 'lonlat': [lon, lat]})
    if not pkt:
        raise SystemExit('ingen bygningspunkt i svaret; sjekk tjenesten før noe skrives')
    pkt.sort(key=lambda p: p['bygningsnummer'])
    json.dump({'kilde': WFS, 'lisens': 'CC BY 4.0, Kartverket (Matrikkelen)', 'hentet': datetime.date.today().isoformat(),
               'bbox_latlon': BBOX, 'punkter': pkt}, open(KILDE, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print(f'{len(pkt)} bygningspunkt -> {os.path.relpath(KILDE, ROT)}')


def inni(x, y, poly):
    ut = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ut = not ut
    return ut


def avstand(x, y, poly):
    best = 1e9
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x2 - x1, y2 - y1
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1)))
        best = min(best, ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5)
    return best


def koble():
    kilde = json.load(open(KILDE, encoding='utf8'))
    bygg = les('bygg')
    register = [l.strip() for l in open(REGISTER, encoding='utf8')] if os.path.exists(REGISTER) else []
    treff = {}                                   # plass i lista -> matrikkelpunkter
    utenfor = []
    for p in kilde['punkter']:
        if p['status'] in ('RA', 'GR', 'BR', 'BF'):   # bare rammetillatelse (ikke bygd), revet/brent, flyttet: ikke et stående bygg
            continue
        x, y = til_modell(*p['lonlat'])
        hit = [i for i, b in enumerate(bygg) if len(b.get('p') or []) >= 3 and inni(x, y, b['p'])]
        if not hit:
            naer = sorted((avstand(x, y, b['p']), i) for i, b in enumerate(bygg) if len(b.get('p') or []) >= 3)
            hit = [naer[0][1]] if naer and naer[0][0] <= NAER else []
        if hit:
            treff.setdefault(min(hit, key=lambda i: len(bygg[i]['p'])), []).append(p)   # minste fotavtrykk ved overlapp
        else:
            utenfor.append(p)
    brukt = set(register)
    neste_pb = 1 + max([int(r[3:]) for r in register if r.startswith('pb-')] or [0])
    nye = []
    for i, b in enumerate(bygg):
        m = sorted(treff.get(i, []), key=lambda p: p['bygningsnummer'])
        if m:
            b['matrikkel'] = [{k: p[k] for k in ('bygningsnummer', 'uuid', 'type', 'kulturminne', 'sefrak', 'adresser', 'matrikkelenheter')} for p in m]
        else:
            b.pop('matrikkel', None)
        if b.get('id'):
            continue                             # en id endres aldri
        kandidat = f"bnr-{m[0]['bygningsnummer']}" if m else None
        if kandidat is None or kandidat in brukt:
            kandidat = f'pb-{neste_pb}'; neste_pb += 1
        b['id'] = kandidat; brukt.add(kandidat); nye.append(kandidat)
    # id først i hvert objekt, så fila er lett å lese
    bygg = [{'id': b['id'], **{k: v for k, v in b.items() if k != 'id'}} for b in bygg]
    with open(os.path.join(ROT, 'data', 'bygg.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(b, ensure_ascii=False, separators=(',', ':')) for b in bygg) + '\n]\n')
    if nye:
        with open(REGISTER, 'a', encoding='utf8') as f:
            f.write(''.join(n + '\n' for n in nye))
    gml = [b for b in bygg if b.get('gml')]
    xs = [q[0] for b in gml for q in b['p']]; ys = [q[1] for b in gml for q in b['p']]
    utenfor = [p for p in utenfor if min(xs) <= til_modell(*p['lonlat'])[0] <= max(xs) and min(ys) <= til_modell(*p['lonlat'])[1] <= max(ys)]
    print(f"{len(bygg)} bygg, {sum(1 for b in bygg if b['id'].startswith('bnr-'))} med bygningsnummer "
          f"({sum(1 for b in gml if b['id'].startswith('bnr-'))} av {len(gml)} i Gamlebyen), {len(nye)} nye id-er, "
          f"{len(utenfor)} matrikkelbygg innenfor Gamlebyen-rammen uten fotavtrykk i kartet (rapport/matrikkel-uten-fotavtrykk.json)")
    json.dump([{**p, 'xy': [round(v, 1) for v in til_modell(*p['lonlat'])]} for p in utenfor],
              open(os.path.join(ROT, 'rapport', 'matrikkel-uten-fotavtrykk.json'), 'w', encoding='utf8'), ensure_ascii=False)


if __name__ == '__main__':
    {'hent': hent, 'koble': koble}[sys.argv[1] if len(sys.argv) > 1 else 'koble']()
