#!/usr/bin/env python3
"""Steder i Gamlebyen til søket og kategoriene (Vegar 05.11: «parkering, steder å spise, kultur»): data/steder.json.

Kilder (KILDER.md):
  - OpenStreetMap via Overpass (ODbL, «© OpenStreetMap-bidragsytere»): spisesteder, kafeer, barer, butikker, museer, kultur,
    overnatting, toaletter, severdigheter. Råsvaret ligger i kilder/osm-steder.json (hentet <dato>, se feltet «hentet»).
  - Fredrikstad kommune, TekniskDrift/Parkering: parkeringsplassene (data/parkering.json, allerede i kartet).
  - Brønnøysundregistrene: virksomhetene med adresse i et bygg (data/virksomheter.json).
  - Kartbrosjyren til Visit Fredrikstad (2015): severdighetene med nummer (data/legende.json).
  - Fredrikstad kommune, Kulturminneplanen (BSU/Kulturminneplan_kommunekart/MapServer/19, «Alle kulturminner samlet», tips fra Vegar
    05.11): kulturminnene med verdi (nasjonal/regional/lokal), vern og lenke til kommunens vedlegg. Råsvaret: kilder/kulturminner.json.
    python3 verktoy/steder.py kulturminner henter det på nytt.
Hvert sted kobles til bygget det står i (punktet i grunnrisset), så kortet kan vise det og kameraet kan fly dit.

  python3 verktoy/steder.py hent     henter OSM-svaret (Overpass) til kilder/osm-steder.json
  python3 verktoy/steder.py bygg     lager data/steder.json fra kildene
Regel 47 passer på at hvert sted har kategori, plass i modellen og kilde.
"""
import json, math, os, re, sys, datetime, urllib.request, urllib.parse
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
import datalag

BBOX = (59.198, 10.940, 59.212, 10.966)   # sør, vest, nord, øst: Gamlebyen med Isegran, Cicignon og kaia
SPORRING = ('[out:json][timeout:90];(' + ''.join(f'nwr({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}){f};' for f in [
    '[amenity~"restaurant|cafe|bar|pub|fast_food|ice_cream|toilets|museum|arts_centre|theatre|cinema|library|place_of_worship|community_centre|events_venue|townhall"]',
    '[tourism]', '[shop]', '[historic]', '[leisure~"park|marina"]', '[craft]']) + ');out center tags;')

# kategoriene i søket, i rekkefølgen de vises
KATEGORIER = [
    ('spise', 'Spise og drikke'), ('kultur', 'Kultur og museer'), ('se', 'Severdigheter'), ('kulturminne', 'Kulturminner'), ('handle', 'Butikker og verksteder'),
    ('sove', 'Overnatting'), ('parkering', 'Parkering'), ('toalett', 'Toalett'),
]

def kategori_osm(t):
    a, tu, h = t.get('amenity', ''), t.get('tourism', ''), t.get('historic', '')
    if a in ('restaurant', 'cafe', 'bar', 'pub', 'fast_food', 'ice_cream'): return 'spise'
    if a == 'toilets': return 'toalett'
    if a in ('museum', 'arts_centre', 'theatre', 'cinema', 'library', 'community_centre', 'events_venue') or tu in ('museum', 'gallery'): return 'kultur'
    if tu in ('hotel', 'guest_house', 'hostel', 'apartment', 'motel', 'camp_site'): return 'sove'
    if t.get('shop') or t.get('craft'): return 'handle'
    if tu in ('attraction', 'viewpoint', 'artwork') or h or a == 'place_of_worship' or t.get('leisure') == 'park': return 'se'
    return None

TYPE_NAVN = {'restaurant': 'Restaurant', 'cafe': 'Kafé', 'bar': 'Bar', 'pub': 'Pub', 'fast_food': 'Gatekjøkken', 'ice_cream': 'Iskrem',
             'museum': 'Museum', 'arts_centre': 'Kunstsenter', 'theatre': 'Teater', 'cinema': 'Kino', 'library': 'Bibliotek',
             'gallery': 'Galleri', 'hotel': 'Hotell', 'guest_house': 'Gjestehus', 'hostel': 'Vandrerhjem', 'apartment': 'Leilighet',
             'toilets': 'Toalett', 'place_of_worship': 'Kirke', 'attraction': 'Severdighet', 'viewpoint': 'Utsiktspunkt', 'artwork': 'Kunstverk',
             'city_gate': 'Byport', 'memorial': 'Minnesmerke', 'castle': 'Festning', 'monument': 'Monument', 'public_bookcase': 'Bokskap',
             'community_centre': 'Kulturhus', 'events_venue': 'Arrangementssted', 'camp_site': 'Camping', 'park': 'Park', 'marina': 'Småbåthavn',
             'yes': 'Historisk bygg', 'building': 'Historisk bygg', 'fort': 'Festningsverk', 'ruins': 'Ruin', 'cannon': 'Kanon', 'boundary_stone': 'Grensestein'}
BUTIKK = {'clothes': 'Klær', 'gift': 'Gaver og interiør', 'hairdresser': 'Frisør', 'art': 'Kunst', 'antiques': 'Antikk', 'bakery': 'Konditori',
          'bicycle': 'Sykkelverksted', 'jeweller': 'Smykker', 'convenience': 'Dagligvare', 'supermarket': 'Dagligvare', 'shoemaker': 'Skomaker',
          'wool': 'Garn', 'kiosk': 'Kiosk', 'books': 'Bøker', 'second_hand': 'Bruktbutikk', 'interior_decoration': 'Interiør', 'florist': 'Blomster'}
UTELATT_BUTIKK = {'funeral_directors', 'trade', 'doityourself'}   # ikke steder en besøkende leter etter

def hent():
    data = urllib.parse.urlencode({'data': SPORRING}).encode()
    for url in ('https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers={'User-Agent': 'Gamlebyen-kart/1.0'}), timeout=120)
            j = json.loads(r.read()); j['hentet'] = datetime.date.today().isoformat(); j['url'] = url
            json.dump(j, open(os.path.join(ROT, 'kilder', 'osm-steder.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
            print('hentet', len(j['elements']), 'fra', url); return
        except Exception as e:
            print('feil', url, e)
    sys.exit('Overpass svarte ikke')

def i_polygon(x, y, p):
    inn = False; j = len(p) - 1
    for i in range(len(p)):
        xi, yi = p[i]; xj, yj = p[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi: inn = not inn
        j = i
    return inn

def bygg_for(x, y, bygg):
    for b in bygg:
        if b.get('skjul') or not b.get('p'): continue
        if i_polygon(x, y, b['p']): return b['id']
    return None

def bygg():
    osm = json.load(open(os.path.join(ROT, 'kilder', 'osm-steder.json'), encoding='utf8'))
    data = datalag.alle()
    bygg = data['bygg']
    global UT
    xs = [p[0] for b in bygg if b.get('p') and not b.get('skjul') for p in b['p']]; ys = [p[1] for b in bygg if b.get('p') and not b.get('skjul') for p in b['p']]
    UT = (min(xs) - 25, max(xs) + 25, min(ys) - 25, max(ys) + 25)
    enkel = lambda n: ''.join(c for c in __import__('unicodedata').normalize('NFD', n.lower()) if c.isalnum())
    steder, sett = [], set()
    for e in osm['elements']:
        t = e.get('tags', {}); navn = t.get('name')
        lat, lon = (e.get('lat'), e.get('lon')) if e['type'] == 'node' else (e.get('center', {}).get('lat'), e.get('center', {}).get('lon'))
        k = kategori_osm(t)
        if lat is None or not k: continue
        if not navn and k not in ('toalett',): continue
        x, y = datalag.til_modell(lon, lat)
        butikk = t.get('shop') or t.get('craft')
        if butikk in UTELATT_BUTIKK: continue
        x, y = datalag.til_modell(lon, lat)
        if not (UT[0] <= x <= UT[1] and UT[2] <= y <= UT[3]): continue   # bare det kartet tegner (utenfor papirkanten ville nåla stått på blankt papir)
        typ = t.get('amenity') or t.get('tourism') or t.get('historic') or t.get('leisure')
        typnavn = BUTIKK.get(butikk, 'Butikk') if butikk and k == 'handle' else TYPE_NAVN.get(typ, (typ or '').replace('_', ' ').capitalize())
        s = {'id': f"osm-{e['type'][0]}{e['id']}", 'navn': navn or 'Toalett', 'kategori': k, 'type': typnavn,
             'x': round(x, 1), 'y': round(y, 1), 'bygg_id': bygg_for(x, y, bygg),
             'kilde': 'OpenStreetMap', 'kilde_url': f"https://www.openstreetmap.org/{e['type']}/{e['id']}", 'hentet': osm.get('hentet')}
        for felt, osmfelt in (('aapent', 'opening_hours'), ('nettside', 'website'), ('telefon', 'phone'), ('adresse', None)):
            if osmfelt and t.get(osmfelt): s[felt] = t[osmfelt]
        if t.get('contact:website') and 'nettside' not in s: s['nettside'] = t['contact:website']
        if t.get('addr:street'): s['adresse'] = f"{t['addr:street']} {t.get('addr:housenumber', '')}".strip()
        if t.get('cuisine'): s['mat'] = t['cuisine'].replace(';', ', ').replace('_', ' ')
        if t.get('wheelchair') in ('yes', 'limited'): s['rullestol'] = t['wheelchair']
        if k == 'se' and enkel(s['navn']) == 'gamlebyen': continue   # hele byen er ikke et sted i byen
        # samme navn i samme bygg eller innen 60 m = ett sted (OSM har noen dobbelt, f.eks. «Cube8 Cafe» og «CUBE8 CAFÉ»); det med bygg vinner
        lik = next((o for o in steder if o['kilde'] == 'OpenStreetMap' and enkel(o['navn']) == enkel(s['navn']) and k != 'toalett'
                    and ((s['bygg_id'] and o['bygg_id'] == s['bygg_id']) or math.hypot(o['x'] - x, o['y'] - y) < 60)), None)
        if lik:
            if not lik['bygg_id'] and s['bygg_id']: steder[steder.index(lik)] = {**s, **{f: lik[f] for f in ('aapent', 'nettside', 'telefon') if lik.get(f) and not s.get(f)}}
            continue
        steder.append(s)
    # parkeringen fra kommunen (samme data som kartet tegner)
    for p in data.get('parkering', []):
        if p.get('skjul') or p.get('x') is None or not (UT[0] <= p['x'] <= UT[1] and UT[2] <= p['y'] <= UT[3]): continue
        steder.append({'id': p['id'], 'navn': p.get('navn') or 'Parkering', 'kategori': 'parkering', 'type': p.get('type') or 'Parkering',
                       'x': p['x'], 'y': p['y'], 'bygg_id': None, 'merknad': p.get('merknad'), 'easypark': p.get('easypark'),
                       'kilde': p.get('kilde'), 'kilde_url': p.get('kilde_url'), 'hentet': p.get('hentet')})
    # severdighetene fra kartbrosjyren: bare de som ikke alt står i OSM med samme navn
    kjente = {enkel(s['navn']) for s in steder}; kjente_bygg = {s['bygg_id'] for s in steder if s['bygg_id'] and s['kategori'] in ('se', 'kultur')}
    for l in data.get('legende', []):
        if not l.get('xy') or enkel(l['navn']) in kjente or (l.get('bygg_id') and l['bygg_id'] in kjente_bygg): continue
        steder.append({'id': f"legende-{l['nr']}", 'navn': l['navn'], 'kategori': 'se', 'type': 'Severdighet', 'x': l['xy'][0], 'y': l['xy'][1],
                       'bygg_id': l.get('bygg_id'), 'nr': l['nr'], 'kilde': 'Kartbrosjyren til Visit Fredrikstad (2015)'})
    # kulturminnene fra kommunens kulturminneplan
    km = json.load(open(os.path.join(ROT, 'kilder', 'kulturminner.json'), encoding='utf8')) if os.path.exists(os.path.join(ROT, 'kilder', 'kulturminner.json')) else {'features': []}
    for f in km['features']:
        a, gm = f['attributes'], f.get('geometry') or {}
        if gm.get('x') is None or not a.get('NAVN'): continue
        x, y = datalag.til_modell(gm['x'], gm['y'])
        if not (UT[0] <= x <= UT[1] and UT[2] <= y <= UT[3]): continue
        rens = lambda t: re.sub(r'\s+', ' ', re.sub(r'(\w)- (?=[a-zæøå])', r'\1', (t or '').replace('\n', ' '))).strip()   # orddeling og linjeskift fra kommunens tabell
        a = {k: rens(v) if isinstance(v, str) else v for k, v in a.items()}
        verdi = a.get('VERDI'); vern = a.get('ANNEN_VERNEFORM') or a.get('EKSISTERENDE_VERN')
        flere = sum(1 for g in km['features'] if (g['attributes'].get('NAVN') or '').strip() == f['attributes']['NAVN'].strip()) > 1
        steder.append({'id': f"km-{a.get('JOIN_') or a['OBJECTID']}", 'navn': f"{a['NAVN']} – {a.get('GRUPPE', '').split(' og ')[0].lower()}" if flere else a['NAVN'], 'kategori': 'kulturminne', 'type': (a.get('GRUPPE') or 'Kulturminne'),
                       'x': round(x, 1), 'y': round(y, 1), 'bygg_id': bygg_for(x, y, bygg),
                       'merknad': ' · '.join(t for t in [a.get('TYPE'), f'Verdi: {verdi}' if verdi else '', f'Vern: {vern}' if vern else ''] if t and not t.startswith('Se også')),
                       'nettside': a.get('URL'), 'kilde': 'Fredrikstad kommune, kulturminneplanen', 'kilde_url': km.get('url'), 'hentet': km.get('hentet')})
    steder.sort(key=lambda s: ([k for k, _ in KATEGORIER].index(s['kategori']), s['navn'].lower()))
    ut = {'kategorier': [{'id': k, 'navn': n} for k, n in KATEGORIER], 'steder': steder,
          'kilder': {'osm': f"© OpenStreetMap-bidragsytere (ODbL), hentet {osm.get('hentet')}", 'parkering': 'Fredrikstad kommune', 'brosjyre': 'Visit Fredrikstad 2015'}}
    json.dump(ut, open(os.path.join(ROT, 'data', 'steder.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print('steder', len(steder), dict(Counter(s['kategori'] for s in steder)), 'i bygg', sum(1 for s in steder if s['bygg_id']))

def kulturminner():
    url = 'https://arcgis.fredrikstad.kommune.no/server/rest/services/BSU/Kulturminneplan_kommunekart/MapServer/19/query?' + urllib.parse.urlencode({
        'where': '1=1', 'geometry': f'{BBOX[1]},{BBOX[0]},{BBOX[3]},{BBOX[2]}', 'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
        'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'outSR': 4326, 'returnGeometry': 'true', 'f': 'json'})
    j = json.loads(urllib.request.urlopen(url, timeout=60).read()); j['hentet'] = datetime.date.today().isoformat(); j['url'] = url.split('/query')[0]
    json.dump(j, open(os.path.join(ROT, 'kilder', 'kulturminner.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0); print('kulturminner', len(j['features']))

if __name__ == '__main__':
    {'hent': hent, 'bygg': bygg, 'kulturminner': kulturminner}[sys.argv[1] if len(sys.argv) > 1 else 'bygg']()
