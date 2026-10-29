#!/usr/bin/env python3
"""Registeret: fasiten for hva som skal finnes i Gamlebyen, ett bygg per kommunehus, koblet til statens nøkler.

    python3 verktoy/register.py              bygger kilder/register/gamlebyen.json, avstemming.json og streetview-mangler.json
    python3 verktoy/register.py streetview   bare streetview-mangler.json (gå-lista for Street View-runden)
    python3 verktoy/register.py kort         huskort (data/adresser.json): nye for adresser uten kort, og kort som står på et annet
                                             hus enn adressepunktet flyttes dit (bare bygg_id); kjøres etter verktoy/adresser.py koble
    python3 verktoy/register.py kort --tørt  viser bare hva som ville blitt lagt til
    python3 verktoy/register.py ark          kontrollark rapport/register/oversikt.png (ikke i git: omrissene er kommunekartet)
    python3 verktoy/register.py hent         henter alle adresser i Gamlebyen-avgrensningen fra Kartverkets adresse-API
                                             (punktsøk, alle postnumre) til kilder/register/adresser-omraade.json

Kilder (alle åpne, ingenting gjettes):
  kommunehus     kilder/kommunekart (FKB-omriss, verktoy/kommunekart.py), avgrenset til Gamlebyen slik grunnmur.py gjør
                 (kommunekart.i_gamlebyen: festningsbyen + 12 m rundt gml-husene, bare hus helt innenfor kartrammen)
  bygningsnummer kilder/matrikkel-bygningspunkt.json (Kartverket, Matrikkelen; status RA/GR/BR/BF regnes ikke, som kommunekart.py)
  adresser       kilder/adresser.json (Kartverkets adresse-API, postnummer 1632) + kilder/register/adresser-omraade.json
                 (samme API, punktsøk over avgrensningen: husene ytterst i avgrensningen har postnummer 1630, 1606 og 1672)
  modellen       data/bygg.json + data/rettelser.json (datalag.alle)
  kort           data/adresser.json (huskortet i src/16_interaksjon.js slår opp adressene på byggets id)
  Street View    kilder/streetview/avlesning.json (hus som er lest av) og hopp.json (lest, men usikkert hus)

Koblingsreglene (samme avstander som verktoy/adresser.py og grunnmur.py, så svarene er like):
  matrikkelpunkt -> kommunehus   punktet står i omrisset (eller inntil NAER_PKT m utenfor, nærmeste)
  modellhus      -> kommunehus   minst halve modellhuset ligger i kommunehuset, eller modellhuset dekker minst halve kommunehuset
  adresse        -> modellhus    adressepunktet står i fotavtrykket, ellers nærmeste innen NAER_ADR m (adresser.py: NAER)
Boligareal og bruksareal finnes ikke i de åpne dataene (Matrikkelens bygningspunkt har bare nummer, type, status og
kulturminne; arealene krever innlogging i Matrikkelen/Se eiendom). Registeret har derfor bare fotavtrykket (FKB-omrisset).
"""
import json, math, os, sys
from collections import defaultdict, Counter
import shapely
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union, nearest_points

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, kommunekart  # noqa: E402

UT = os.path.join(ROT, 'kilder', 'register')
NAER_PKT = 4.0        # m, som grunnmur.py: NAER
NAER_ADR = 8.0        # m, som adresser.py: NAER (adressepunktet står ofte ved inngangen, utenfor veggen)
DEL = 0.5             # som grunnmur.py: KAPASITET_DEL
IKKE_STAAENDE = ('RA', 'GR', 'BR', 'BF')   # rammetillatelse, igangsatt, revet/brent, bortfalt: ikke et hus som står
# Matrikkelens bygningstyper (Kartverkets kodeliste, de som finnes i Gamlebyen) -> ord til kort og register
BYGNINGSTYPE = {
    111: 'enebolig', 112: 'enebolig med hybel', 113: 'våningshus', 121: 'tomannsbolig', 122: 'tomannsbolig', 123: 'tomannsbolig',
    124: 'tomannsbolig', 131: 'rekkehus', 133: 'kjedehus', 135: 'terrassehus', 136: 'andre småhus', 141: 'store boligbygg',
    142: 'store boligbygg', 143: 'store boligbygg', 144: 'store boligbygg', 145: 'store boligbygg', 146: 'store boligbygg',
    151: 'bo- og servicesenter', 152: 'studenthjem', 159: 'annen bygning for bofellesskap', 161: 'fritidsbolig', 162: 'helårsbolig brukt som fritidsbolig',
    163: 'våningshus brukt som fritidsbolig', 171: 'seterhus/koie', 172: 'skogs- og utmarkskoie', 181: 'garasje/uthus til bolig',
    182: 'garasje/uthus til fritidsbolig', 183: 'naust/båthus', 193: 'boligbrakker', 199: 'annen boligbygning',
    211: 'fabrikkbygning', 212: 'verkstedbygning', 214: 'bygning for renseanlegg', 216: 'bygning for vannforsyning', 219: 'annen industribygning',
    221: 'kraftstasjon', 223: 'transformatorstasjon', 229: 'annen energiforsyningsbygning', 231: 'lagerhall', 232: 'kjøle- og fryselager',
    233: 'silobygning', 239: 'annen lagerbygning', 241: 'hus for dyr/landbrukslager', 243: 'veksthus', 244: 'driftsbygning fiske',
    245: 'naust/redskapshus for fiske', 248: 'annen fiskeri- og fangstbygning', 249: 'annen landbruksbygning',
    311: 'kontor- og administrasjonsbygning', 312: 'bankbygning/posthus', 313: 'mediebygning', 319: 'annen kontorbygning',
    321: 'kjøpesenter/varehus', 322: 'butikkbygning', 323: 'bensinstasjon', 329: 'annen forretningsbygning', 330: 'messe- og kongressbygning',
    411: 'ekspedisjonsbygning (fly)', 412: 'terminalbygning', 415: 'godsterminal', 416: 'postterminal', 419: 'annen ekspedisjons- og terminalbygning',
    429: 'annen telekommunikasjonsbygning', 431: 'parkeringshus', 439: 'annen garasje-/hangarbygning', 441: 'trafikktilsynsbygning',
    449: 'annen veg- og trafikktilsynsbygning', 511: 'hotellbygning', 512: 'motellbygning', 519: 'annen hotellbygning', 521: 'hospits/pensjonat',
    522: 'vandrerhjem', 523: 'appartement', 524: 'campinghytte/utleiehytte', 529: 'annen bygning for overnatting', 531: 'restaurantbygning/kafé',
    532: 'sentralkjøkken/kantine', 533: 'gatekjøkken/kioskbygning', 539: 'annen restaurantbygning', 611: 'lekepark', 612: 'barnehage',
    613: 'barneskole', 614: 'ungdomsskole', 615: 'kombinert barne- og ungdomsskole', 616: 'videregående skole', 619: 'annen skolebygning',
    621: 'universitet/høgskole', 623: 'laboratoriebygning', 629: 'annen undervisningsbygning', 641: 'museum/kunstgalleri', 642: 'bibliotek/mediatek',
    643: 'zoologisk/botanisk hage', 649: 'annen museums- og bibliotekbygning', 651: 'idrettshall', 652: 'ishall', 653: 'svømmehall',
    654: 'tribune og idrettsgarderobe', 655: 'helsestudio', 659: 'annen idrettsbygning', 661: 'kinobygning/teaterbygning/opera',
    662: 'samfunnshus/grendehus', 663: 'diskotek', 669: 'annet kulturhus', 671: 'kirke/kapell', 672: 'bedehus/menighetshus',
    673: 'krematorium/gravkapell', 674: 'synagoge/moské', 675: 'kloster', 679: 'annen bygning for religiøse aktiviteter',
    719: 'sykehus', 721: 'sykehjem', 722: 'bo- og behandlingssenter', 723: 'rehabiliteringsinstitusjon', 729: 'annet sykehjem',
    731: 'klinikk/legekontor/helsesenter', 732: 'helse- og sosialsenter', 739: 'annen primærhelsebygning', 819: 'fengselsbygning',
    821: 'politistasjon', 822: 'brannstasjon/ambulansestasjon', 823: 'fyrstasjon', 824: 'stasjon for radarovervåkning',
    825: 'tilfluktsrom/bunker', 829: 'annen beredskapsbygning', 830: 'monument', 840: 'offentlig toalett',
}


def til_lonlat(x, y):
    """Modellmeter -> grader (omvendt av datalag.til_modell)."""
    R = datalag._R; mx = x / datalag._S + datalag._MX0; my = y / datalag._S + datalag._MY0
    return math.degrees(mx / R), math.degrees(2 * math.atan(math.exp(my / R)) - math.pi / 2)


def kid(k):
    """Kommunehusets nøkkel i registeret: tyngdepunktet i modellmeter (0,1 m). Plassen i PDF-en er ikke fast (nytt uttak av
    kommunekartet gir ny rekkefølge); tyngdepunktet er det så lenge kommunen ikke måler huset på nytt."""
    c = k.centroid
    return f'fkb-{c.x:.1f}_{c.y:.1f}'


def poly(x):
    P = Polygon(x['p'], [r for r in (x.get('ph') or []) if len(r) > 2])
    return P if P.is_valid else P.buffer(0)


def omraade(dek):
    """Gamlebyen-avgrensningen som flate, regnet nøyaktig som kommunekart.i_gamlebyen (den gir bare indekser). Brukes til
    adresser og modellhus som ikke har et kommunehus. Endres i_gamlebyen, må denne følge med (regel 21 sammenligner dem)."""
    ps = []
    for x in datalag.alle(raa=True)['bygg']:
        if x.get('gml') and len(x['p']) >= 3:
            P = Polygon(x['p']); ps.append(P if P.is_valid else P.buffer(0))
    indre = [P for P in ps if -260 < P.centroid.x < 290 and -270 < P.centroid.y < 320]
    return unary_union(indre).convex_hull.buffer(30).union(unary_union(ps).buffer(12)), dek.buffer(-0.3)


def festningsbyen():
    """Festningsbyen innenfor vollene (+30 m), den indre delen av omraade(): gå-lista tar den først."""
    ps = [Polygon(x['p']).buffer(0) for x in datalag.alle(raa=True)['bygg'] if x.get('gml') and len(x['p']) >= 3]
    return unary_union([P for P in ps if -260 < P.centroid.x < 290 and -270 < P.centroid.y < 320]).convex_hull.buffer(30)


# ---------------------------------------------------------------- lasting
def adr_nokkel(a):
    return (a['kommunenummer'], a['adressekode'], a['nummer'], a['bokstav'] or '')


def hent():
    """Alle adresser i Gamlebyen-avgrensningen (+ NAER_ADR m), uansett postnummer, fra Kartverkets adresse-API (punktsøk)."""
    import urllib.request, urllib.parse, datetime
    R, RAMME = omraade(kommunekart.dekning())
    O = R.buffer(NAER_ADR)
    c = O.centroid; lon, lat = til_lonlat(c.x, c.y)
    rad = int(max(Point(c).distance(Point(q)) for q in O.exterior.coords) + 50) if O.geom_type == 'Polygon' else 2000
    ut, side = [], 0
    while True:
        url = 'https://ws.geonorge.no/adresser/v1/punktsok?' + urllib.parse.urlencode(
            {'lat': f'{lat:.6f}', 'lon': f'{lon:.6f}', 'radius': rad, 'treffPerSide': 1000, 'side': side, 'utkoordsys': 4258})
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'pageblack-smartoldtown'}), timeout=120))
        for a in d['adresser']:
            q = Point(datalag.til_modell(a['representasjonspunkt']['lon'], a['representasjonspunkt']['lat']))
            if O.contains(q):
                a.pop('meterDistanseTilPunkt', None); ut.append(a)
        if d['metadata']['viserTil'] >= d['metadata']['totaltAntallTreff']:
            break
        side += 1
    ut.sort(key=lambda a: (a['adressenavn'] or '', a['nummer'] or 0, a['bokstav'] or ''))
    os.makedirs(UT, exist_ok=True)
    skriv(os.path.join(UT, 'adresser-omraade.json'), {'kilde': 'ws.geonorge.no/adresser/v1/punktsok', 'lisens': 'CC BY 4.0, Kartverket',
          'hentet': datetime.date.today().isoformat(), 'omraade': f'Gamlebyen-avgrensningen + {NAER_ADR} m (verktoy/register.py omraade)',
          'adresser': ut})
    print(f'{len(ut)} adresser i avgrensningen; postnumre: {dict(Counter(a["postnummer"] for a in ut))}')


def last():
    D = datalag.alle()
    B = D['bygg']
    K = kommunekart.omriss(); DEK = kommunekart.dekning()
    G = kommunekart.i_gamlebyen(K, DEK)
    R, RAMME = omraade(DEK)
    M = json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json'), encoding='utf8'))
    pkt = [dict(p, P=Point(datalag.til_modell(*p['lonlat']))) for p in M['punkter'] if p['status'] not in IKKE_STAAENDE]
    A = json.load(open(os.path.join(ROT, 'kilder', 'adresser.json'), encoding='utf8'))
    alle_a = list(A['adresser']); sett = {adr_nokkel(a) for a in alle_a}
    sti_o = os.path.join(UT, 'adresser-omraade.json')
    if os.path.exists(sti_o):
        for a in json.load(open(sti_o, encoding='utf8'))['adresser']:
            if adr_nokkel(a) not in sett:
                alle_a.append(a); sett.add(adr_nokkel(a))
    adr = [dict(a, P=Point(datalag.til_modell(a['representasjonspunkt']['lon'], a['representasjonspunkt']['lat']))) for a in alle_a]
    SV = json.load(open(os.path.join(ROT, 'kilder', 'streetview', 'avlesning.json'), encoding='utf8'))
    hopp = json.load(open(os.path.join(ROT, 'kilder', 'streetview', 'hopp.json'), encoding='utf8'))
    kort = datalag.les('adresser')
    return dict(D=D, B=B, K=K, G=G, DEK=DEK, R=R, RAMME=RAMME, pkt=pkt, adr=adr, SV=SV, hopp=hopp, kort=kort,
                M_hentet=M['hentet'], A_hentet=A['hentet'])


def adresse_til_bygg(adr, B, synlige):
    """Adressepunkt -> modellhus (id), som verktoy/adresser.py koble: inni fotavtrykket, ellers nærmeste innen NAER_ADR m."""
    P = {i: poly(B[i]) for i in synlige}
    tre_i = list(P); tre = shapely.STRtree([P[i] for i in tre_i])
    ut = {}
    for k, a in enumerate(adr):
        inni = [tre_i[int(j)] for j in tre.query(a['P']) if P[tre_i[int(j)]].contains(a['P'])]
        if inni:
            i = min(inni, key=lambda i: P[i].area)          # minste hus som rommer punktet (et uthus inni et gårdsrom-omriss)
            ut[k] = (B[i]['id'], 0.0)
            continue
        j = tre.nearest(a['P']); i = tre_i[int(j)]; d = P[i].distance(a['P'])
        ut[k] = (B[i]['id'], round(d, 1)) if d <= NAER_ADR else (None, round(d, 1))
    return ut


# ---------------------------------------------------------------- Street View-lista
def _bearing(a, b):
    return round((math.degrees(math.atan2(b[0] - a[0], b[1] - a[1])) + 360) % 360)


def _gatelinjer(D):
    g = defaultdict(list)
    for v in D['veier']:
        n = (v.get('t') or {}).get('name')
        if n and len(v['p']) >= 2:
            g[n].append(shapely.LineString(v['p']))
    return {n: unary_union(ls) for n, ls in g.items()}


def _utsiktspunkt(gate, mål, gater):
    """Punktet på gatas midtlinje nærmest huset, og retningen derfra mot huset (til pano_url)."""
    L = gater.get(gate)
    if L is None or L.is_empty:
        return None, None
    q = nearest_points(L, mål)[0]
    return (q.x, q.y), _bearing((q.x, q.y), (mål.x, mål.y))


def gaa_rekkefolge(grupper, start):
    """Gatene i en gå-rekkefølge: fra startgata, alltid til den gata som har et hus nærmest der du står (grådig), og
    husene i hver gate langs gata fra den enden som er nærmest. Gir én sammenhengende runde uten å gå samme gate to ganger."""
    igjen = dict(grupper); ut = []
    her = None
    navn = start if start in igjen else min(igjen)
    while igjen:
        if her is not None:
            navn = min(igjen, key=lambda n: min(Point(r['_xy']).distance(Point(her)) for r in igjen[n]))
        rader = igjen.pop(navn)
        xy = [r['_xy'] for r in rader]
        if len(xy) > 1:                                     # hovedretningen til gata: lengste avstand mellom to hus
            a, b = max(((p, q) for p in xy for q in xy), key=lambda t: (t[0][0] - t[1][0]) ** 2 + (t[0][1] - t[1][1]) ** 2)
            ux, uy = b[0] - a[0], b[1] - a[1]
            rader.sort(key=lambda r: r['_xy'][0] * ux + r['_xy'][1] * uy)
            if her is not None and Point(rader[-1]['_xy']).distance(Point(her)) < Point(rader[0]['_xy']).distance(Point(her)):
                rader.reverse()
        ut.append((navn, rader)); her = rader[-1]['_xy']
    return ut


def streetview_mangler(L, reg=None):
    """Alle adresser i Gamlebyen og alle bygg med bygningsnummer i Gamlebyen som ikke er lest av i Street View
    (ikke i avlesning.json; de i hopp.json er lest, men usikre, og står med egen merknad). Gatevis, i gå-rekkefølge."""
    reg = reg or bygg_register(L)
    D = L['D']; gater = _gatelinjer(D); FEST = festningsbyen()
    plass = {b['id']: i for i, b in enumerate(L['B'])}
    rader = []
    for r in reg['bygg'] + reg['modell_uten_kommunehus']:
        if r['streetview'] == 'lest':
            continue
        if r['modell_id'] is None:
            continue
        b = L['B'][plass[r['modell_id']]]
        c = poly(b).representative_point()
        adr = r['adresser']
        gate = adr[0].rsplit(' ', 1)[0] if adr else r.get('naermeste_gate')
        if not adr and not r['bygningsnumre']:
            continue                                        # verken adresse eller bygningsnummer: ikke et hus å lese av
        vp, hd = _utsiktspunkt(gate, c, gater)
        lon, lat = til_lonlat(c.x, c.y)
        rad = {'modell_id': r['modell_id'], 'adresser': adr, 'navn': b.get('navn'), 'bygningsnummer': r['bygningsnumre'][:1] or None,
               'bygningstype': r.get('bygningstype'), 'kulturminne': r.get('kulturminne'), 'bygg_lonlat': [round(lon, 6), round(lat, 6)],
               'status': 'usikker (hopp.json): ' + L['hopp'][r['modell_id']] if r['streetview'] == 'usikker' else 'ikke lest',
               '_xy': (c.x, c.y)}
        if vp:
            vlon, vlat = til_lonlat(*vp)
            rad['pano_url'] = (f'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={vlat:.7f},{vlon:.7f}'
                               f'&heading={hd}&pitch=8&fov=70')
        else:
            rad['pano_url'] = None
        rad['_gate'] = gate or '(uten gate)'
        rad['sone'] = ('randsone' if r.get('innenfor_kartrammen') is False else
                       'festningsbyen' if FEST.contains(Point(rad['_xy'])) else 'gamlebyen')
        rader.append(rad)
    ordnet = []
    her = 'Færgeportgaten'                                  # fergeleiet: der de fleste kommer inn i byen
    for sone in ('festningsbyen', 'gamlebyen', 'randsone'):  # innenfor vollene først, så resten av avgrensningen, randsonen sist
        grupper = defaultdict(list)
        for r in rader:
            if r['sone'] == sone:
                grupper[r['_gate']].append(r)
        if grupper:
            ordnet += [(n, rr, sone) for n, rr in gaa_rekkefolge(grupper, start=her)]
            her = ordnet[-1][0]
    ut = {'_om': ('Hus og adresser i Gamlebyen som ikke er lest av i Street View (kilder/streetview/avlesning.json), gatevis i '
                  'gå-rekkefølge (grådig: nærmeste gate etter forrige, husene langs gata). pano_url: punktet på gatas midtlinje '
                  'nærmest huset, heading mot huset. «usikker»: lest, men hopp.json sier det er tvil om det var riktig hus. '
                  'Med: hus med adresse eller bygningsnummer (pb-hus uten adresse er murer/skur og står ikke her). '
                  'Sone: festningsbyen (innenfor vollene) først, så resten av Gamlebyen-avgrensningen, randsonen (husene utenfor '
                  'kommunekartets ramme) til slutt. '
                  'Laget av verktoy/register.py; Google-bildene skal aldri inn i repoet, bare tall og ord i avlesning.json.'),
          'antall': len(rader), 'gater': []}
    for navn, rr, sone in ordnet:
        for r in rr:
            r.pop('_xy'); r.pop('_gate'); r.pop('sone')
        ut['gater'].append({'gate': navn, 'sone': sone, 'antall': len(rr), 'hus': rr})
    for sone in ('festningsbyen', 'gamlebyen', 'randsone'):
        ut['antall_' + sone] = sum(g['antall'] for g in ut['gater'] if g['sone'] == sone)
    os.makedirs(UT, exist_ok=True)
    skriv(os.path.join(UT, 'streetview-mangler.json'), ut)
    print(f"streetview-mangler: {len(rader)} hus i {len(ordnet)} gater")
    return ut


def skriv(sti, obj):
    with open(sti, 'w', encoding='utf8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')


# ---------------------------------------------------------------- registeret
def kilder_per_bygg(rettelser):
    """Siste grunn per (id, felt) i rettelseslaget, og id-ene som er nye (op ny)."""
    siste = {}
    for r in rettelser:
        if r['emne'] == 'bygg' and r['op'] == 'sett':
            siste[(r['id'], r['felt'])] = r.get('grunn', '')
    return siste, datalag.nye_ider(rettelser)


def hoydekilde(b, siste, nye):
    g = siste.get((b['id'], 'h'))
    if g:
        return 'Kartverket DOM−DTM' if g.startswith('Kartverket') else g[:80]
    if b['id'] in nye:
        return 'første gjetning (DOM−DTM p50 − 1 m, grunnmur.py)'
    if b.get('tegnet_h'):
        return 'tegning (tegnet_h/1,72)'
    return 'OSM/grunndata'


def fasadekilde(b):
    f = b.get('fasade_kilde')
    return {'kvartaltegning': 'kvartaltegning', 'streetview': 'streetview', 'antatt': 'regel'}.get(f, 'ingen' if not b.get('vind') else str(f))


def fargekilde(b, siste, nye):
    if b.get('farge_kilde'):
        return b['farge_kilde']
    g = siste.get((b['id'], 'vegg'))
    if g:
        return g[:80]
    if b['id'] in nye:
        return 'nøytral (nytt hus, ikke valgt)'
    return 'trykkfila 2015 (grunndata)' if b.get('gml') else 'grunndata (OSM)'


def bygg_register(L):
    B, K, G, pkt, adr = L['B'], L['K'], L['G'], L['pkt'], L['adr']
    siste, nye = kilder_per_bygg(datalag.les('rettelser'))
    synlige = [i for i, b in enumerate(B) if not b.get('skjul') and len(b.get('p') or []) >= 3]
    P = {i: poly(B[i]) for i in synlige}
    plass = {b['id']: i for i, b in enumerate(B)}
    R, RAMME = L['R'], L['RAMME']
    gater = _gatelinjer(L['D'])

    # matrikkelpunkt -> kommunehus (alle kommunehus, så et punkt ikke havner i Gamlebyen-huset ved siden av)
    ktre = shapely.STRtree(K)
    pkt_k = {}
    for n, p in enumerate(pkt):
        inni = [int(j) for j in ktre.query(p['P']) if K[int(j)].contains(p['P'])]
        if inni:
            pkt_k[n] = min(inni, key=lambda j: K[j].area)
        else:
            j = int(ktre.nearest(p['P']))
            if K[j].distance(p['P']) <= NAER_PKT:
                pkt_k[n] = j
    k_pkt = defaultdict(list)
    for n, j in pkt_k.items():
        k_pkt[j].append(n)

    # modellhus -> kommunehus
    k_mod = defaultdict(list); mod_k = defaultdict(list)
    for i in synlige:
        for j in ktre.query(P[i]):
            j = int(j); a = P[i].intersection(K[j]).area
            if a > DEL * P[i].area or a > DEL * K[j].area:
                k_mod[j].append(i); mod_k[i].append(j)

    # adresse -> modellhus
    a_b = adresse_til_bygg(adr, B, synlige)
    b_adr = defaultdict(list)
    for k, (bid, d) in a_b.items():
        if bid:
            b_adr[bid].append(k)

    kort_ids = defaultdict(list); kort_alle = [(r['bygg_id'], r['adresse']) for r in L['kort']]
    for r in L['kort']:
        kort_ids[r['bygg_id']].append(r['adresse'])

    def gate_naer(c):
        best = min(((L_.distance(c), n) for n, L_ in gater.items()), default=(1e9, None))
        return best[1]

    def sv_status(bid):
        if bid in L['hopp']:
            return 'usikker'
        return 'lest' if bid in L['SV'] else 'mangler'

    def modellfelt(i):
        b = B[i]
        return {'modell_id': b['id'], 'navn': b.get('navn'), 'hoydekilde': hoydekilde(b, siste, nye), 'h': b.get('h'),
                'fasadekilde': fasadekilde(b), 'fargekilde': fargekilde(b, siste, nye), 'streetview': sv_status(b['id']),
                'kort': bool(kort_ids.get(b['id']))}

    rader = []
    for j in G:
        mods = k_mod.get(j, []); ns = sorted(k_pkt.get(j, []), key=lambda n: pkt[n]['bygningsnummer'])
        c = K[j].representative_point()
        rad = {'kommune_id': kid(K[j]), 'areal': round(K[j].area, 1), 'bygningsnumre': [pkt[n]['bygningsnummer'] for n in ns],
               'bygningstype': ', '.join(sorted({BYGNINGSTYPE.get(pkt[n]['type'], str(pkt[n]['type'])) for n in ns})) or None,
               'kulturminne': any(pkt[n]['kulturminne'] for n in ns), 'sefrak': any(pkt[n]['sefrak'] for n in ns)}
        if len(mods) == 1:
            rad.update(modellfelt(mods[0]))
        elif mods:
            # flere modellhus i ett kommunehus: den som dekker mest er hovedhuset, resten listes
            hoved = max(mods, key=lambda i: P[i].intersection(K[j]).area)
            rad.update(modellfelt(hoved)); rad['ogsaa_modell'] = [B[i]['id'] for i in mods if i != hoved]
        else:
            rad.update({'modell_id': None, 'streetview': 'mangler', 'kort': False})
        ids = [rad['modell_id']] + rad.get('ogsaa_modell', [])
        rad['adresser'] = sorted({adr[k]['adressetekst'] for bid in ids if bid for k in b_adr.get(bid, [])},
                                 key=lambda t: (t.rsplit(' ', 1)[0], int(''.join(ch for ch in t.rsplit(' ', 1)[-1] if ch.isdigit()) or 0), t))
        rad['naermeste_gate'] = gate_naer(c)
        rader.append(rad)

    # modellhus i Gamlebyen uten kommunehus (kirka, Kaserna, portbygg, hus rammen kutter …)
    i_reg = {r['modell_id'] for r in rader} | {x for r in rader for x in r.get('ogsaa_modell', [])}
    uten_k = []
    for i in synlige:
        b = B[i]
        if b['id'] in i_reg or not R.contains(P[i].representative_point()):
            continue
        r = {'kommune_id': None, 'areal': round(P[i].area, 1), 'bygningsnumre': [m['bygningsnummer'] for m in (b.get('matrikkel') or [])],
             'bygningstype': None, 'kulturminne': any(m.get('kulturminne') for m in (b.get('matrikkel') or [])),
             'innenfor_kartrammen': RAMME.contains(P[i]), 'kommunehus': [kid(K[j]) for j in mod_k.get(i, [])]}
        r.update(modellfelt(i))
        r['adresser'] = sorted({adr[k]['adressetekst'] for k in b_adr.get(b['id'], [])})
        r['naermeste_gate'] = gate_naer(P[i].representative_point())
        uten_k.append(r)

    # adressene: alle i kilden, med kobling og om de hører til Gamlebyen
    reg_ids = {r['modell_id'] for r in rader + uten_k if r['modell_id']} | {x for r in rader for x in r.get('ogsaa_modell', [])}
    k_ids = {r['modell_id'] for r in rader if r['modell_id']} | {x for r in rader for x in r.get('ogsaa_modell', [])}
    fredet_inni = {r['modell_id'] for r in uten_k if r['innenfor_kartrammen']}
    adr_rader = []
    for k, a in enumerate(adr):
        bid, d = a_b[k]
        # sone: «gamlebyen» = i avgrensningen og innenfor kommunekartets ramme (fasiten); «randsone» = i avgrensningen, men
        # utenfor rammen (huset står i modellen, kommunekartet dekker det ikke); «utenfor» = utenfor avgrensningen
        # Sonen følger huset adressen hører til (et hus rammen kutter, er ikke målt av kommunen, selv om adressepunktet er innenfor)
        ramme = L['DEK'].contains(a['P'])
        if bid in k_ids or bid in fredet_inni:
            sone = 'gamlebyen'
        elif bid in reg_ids:
            sone = 'randsone'
        elif R.buffer(NAER_ADR).contains(a['P']):
            sone = 'gamlebyen' if L['RAMME'].contains(a['P']) else 'randsone'
        else:
            sone = 'utenfor'
        adr_rader.append({'adresse': a['adressetekst'], 'postnummer': a['postnummer'], 'gnr': a['gardsnummer'], 'bnr': a['bruksnummer'],
                          'lonlat': [round(a['representasjonspunkt']['lon'], 6), round(a['representasjonspunkt']['lat'], 6)],
                          'sone': sone, 'innenfor_kartrammen': ramme,
                          'modell_id': bid, 'avstand_m': d, 'kort': a['adressetekst'] in kort_ids.get(bid, []),
                          'kort_paa': sorted(b_ for b_, t in kort_alle if t == a['adressetekst'])})
    return {'bygg': rader, 'modell_uten_kommunehus': uten_k, 'adresser': adr_rader,
            '_intern': dict(k_pkt=k_pkt, pkt=pkt, k_mod=k_mod, b_adr=b_adr, a_b=a_b, kort_ids=kort_ids, synlige=synlige)}




# ---------------------------------------------------------------- avstemming
def avstem(L, reg):
    """Telling og hull. Hvert hull har en grunn regnet ut fra kildene; ingenting rettes her."""
    I = reg['_intern']; B = L['B']; pkt = I['pkt']
    plass = {b['id']: i for i, b in enumerate(B)}
    rader, uten_k, adr = reg['bygg'], reg['modell_uten_kommunehus'], reg['adresser']
    gml_adr = [a for a in adr if a['sone'] == 'gamlebyen']
    rand_adr = [a for a in adr if a['sone'] == 'randsone']
    bnr_i = sorted({n for r in rader for n in r['bygningsnumre']})
    modell_i = {r['modell_id'] for r in rader + uten_k if r['modell_id']} | {x for r in rader for x in r.get('ogsaa_modell', [])}
    hull = defaultdict(list)
    for r in rader:
        if r['modell_id'] is None:
            hull['kommunehus_uten_modellhus'].append({'kommune_id': r['kommune_id'], 'areal': r['areal'], 'bygningsnumre': r['bygningsnumre'],
                                                      'naermeste_gate': r['naermeste_gate'],
                                                      'grunn': 'under 6 m² (grunnmur.py MINSTE)' if r['areal'] < 6 else 'ikke lagt inn av grunnmur.py'})
        if r.get('ogsaa_modell'):
            hull['flere_modellhus_i_ett_kommunehus'].append({'kommune_id': r['kommune_id'], 'modell': [r['modell_id']] + r['ogsaa_modell'],
                                                             'grunn': 'grunnmur.py deler omrisset mellom modellhusene (bevisst, id-ene beholdes)'})
        if len(r['bygningsnumre']) > 1:
            hull['flere_bygningsnumre_i_ett_kommunehus'].append({'kommune_id': r['kommune_id'], 'modell_id': r['modell_id'], 'bygningsnumre': r['bygningsnumre'],
                                                                 'grunn': 'Matrikkelen har flere bygg der kommunekartet tegner ett omriss (sammenbygde hus/tilbygg); id er det laveste nummeret i modellens matrikkelfelt'})
        if r['modell_id'] and r['bygningsnumre']:
            b = B[plass[r['modell_id']]]
            mine = {m['bygningsnummer'] for m in (b.get('matrikkel') or [])}
            ok_id = r['modell_id'].startswith('bnr-') and int(r['modell_id'][4:]) in set(r['bygningsnumre'])
            if not ok_id:
                andre = [f'bnr-{n}' for n in r['bygningsnumre'] if f'bnr-{n}' in plass]
                hull['id_ikke_bnr'].append({'kommune_id': r['kommune_id'], 'modell_id': r['modell_id'], 'bygningsnumre': r['bygningsnumre'],
                                            'modellens_matrikkel': sorted(mine), 'nummeret_brukt_av': andre,
                                            'grunn': ('pb-id, men kommunehuset har bygningsnummer' if r['modell_id'].startswith('pb-')
                                                      else 'bnr-id er et annet bygningsnummer enn det som står i omrisset')
                                                     + ('; nummeret er id på et annet modellhus (byttet om?)' if andre else '')})
    # bygningsnumre: samme nummer brukt som id på flere, og numre i Gamlebyen uten bygg
    k_av_bnr = defaultdict(list)
    for r in rader:
        for n in r['bygningsnumre']:
            k_av_bnr[n].append(r['kommune_id'])
    for n, ks in k_av_bnr.items():
        if len(ks) > 1:
            hull['bygningsnummer_i_flere_kommunehus'].append({'bygningsnummer': n, 'kommune_id': ks})
    # punkter i Gamlebyen-området som ikke står i noe kommunehus
    k_pkt_alle = {n for v in I['k_pkt'].values() for n in v}
    for n, p in enumerate(pkt):
        if n in k_pkt_alle or not L['R'].contains(p['P']):
            continue
        bid = f"bnr-{p['bygningsnummer']}"
        hull['bygningspunkt_uten_kommunehus'].append({'bygningsnummer': p['bygningsnummer'], 'bygningstype': BYGNINGSTYPE.get(p['type'], p['type']),
                                                      'status': p['status'], 'modell_id': bid if bid in plass else None,
                                                      'grunn': ('utenfor kartrammen (kommunekartet dekker ikke punktet)' if not L['DEK'].contains(p['P'])
                                                                else 'punktet står ikke i et FKB-omriss (lite bygg kommunekartet ikke tegner, eller punktet er satt på tomta)')})
    # adressene
    for a in gml_adr + rand_adr:
        pre = '' if a['sone'] == 'gamlebyen' else 'randsone_'
        if a['modell_id'] is None:
            hull[pre + 'adresse_uten_bygg'].append({'adresse': a['adresse'], 'avstand_m': a['avstand_m'],
                                                    'grunn': f"nærmeste modellhus {a['avstand_m']} m unna (grense {NAER_ADR} m)"})
        elif not a['kort_paa']:
            hull[pre + 'adresse_uten_kort'].append({'adresse': a['adresse'], 'modell_id': a['modell_id']})
        elif not a['kort']:
            hull[pre + 'kort_paa_annet_bygg'].append({'adresse': a['adresse'], 'adressepunktet_i': a['modell_id'], 'kortet_paa': a['kort_paa'],
                                                      'grunn': 'kortet ble koblet før grunnmur.py delte/la til hus (adresser.py koble bruker grunndataene); verktoy/register.py kort flytter det'})
    for t, n in Counter(r['adresse'] for r in L['kort']).items():
        if n > 1:
            hull['kort_paa_flere_bygg'].append({'adresse': t, 'bygg': sorted(r['bygg_id'] for r in L['kort'] if r['adresse'] == t)})
    per_adr = Counter(a['adresse'] for a in gml_adr)
    for t, n in per_adr.items():
        if n > 1:
            hull['adresse_to_ganger_i_kilden'].append({'adresse': t, 'antall': n})
    # modellhus med flere adresser er normalt (gårdsrekker); listes til kontroll
    fler = [(r['modell_id'], r['adresser']) for r in rader + uten_k if len(r['adresser']) > 1]
    tall = {
        'kommunehus_i_gamlebyen': len(rader),
        'kommunehus_med_modellhus': sum(1 for r in rader if r['modell_id']),
        'bygningsnumre_i_kommunehusene': len(bnr_i),
        'kommunehus_med_bygningsnummer': sum(1 for r in rader if r['bygningsnumre']),
        'bygningspunkt_i_gamlebyen_uten_kommunehus': len(hull['bygningspunkt_uten_kommunehus']),
        'adresser_i_kildene': len(adr),
        'adresser_i_gamlebyen': len(gml_adr),
        'adresser_i_randsonen_utenfor_kartrammen': len(rand_adr),
        'adresser_utenfor_avgrensningen': len(adr) - len(gml_adr) - len(rand_adr),
        'adresser_med_bygg': sum(1 for a in gml_adr if a['modell_id']),
        'adresser_med_kort_paa_samme_bygg': sum(1 for a in gml_adr if a['kort']),
        'adresser_med_kort_paa_annet_bygg': sum(1 for a in gml_adr if a['kort_paa'] and not a['kort']),
        'randsone_adresser_med_bygg': sum(1 for a in rand_adr if a['modell_id']),
        'randsone_adresser_med_kort': sum(1 for a in rand_adr if a['kort_paa']),
        'modellhus_i_gamlebyen': len(modell_i) - sum(1 for r in uten_k if not r['innenfor_kartrammen']),
        'modellhus_i_randsonen': sum(1 for r in uten_k if not r['innenfor_kartrammen']),
        'modellhus_uten_kommunehus_innenfor_rammen': [r['modell_id'] + (f" ({r['navn']})" if r['navn'] else '') for r in uten_k if r['innenfor_kartrammen']],
        'modellhus_med_flere_adresser': len(fler),
        'streetview_lest': sum(1 for r in rader + uten_k if r['streetview'] == 'lest'),
        'streetview_usikker': sum(1 for r in rader + uten_k if r['streetview'] == 'usikker'),
        'streetview_mangler_med_modellhus': sum(1 for r in rader + uten_k if r['streetview'] == 'mangler' and r['modell_id']),
        'streetview_mangler_i_randsonen': sum(1 for r in uten_k if r['streetview'] == 'mangler' and not r['innenfor_kartrammen']),
    }
    return {'tall': tall, 'hull': {k: v for k, v in hull.items()}, 'modellhus_med_flere_adresser': [{'modell_id': m, 'adresser': a} for m, a in fler],
            'utenfor_avgrensningen': sorted(Counter(a['adresse'].rsplit(' ', 1)[0] for a in adr if a['sone'] == 'utenfor').items())}


def legg_til_kort(L, tørt=False):
    """Huskort for adresser (Gamlebyen og randsonen) som har et modellhus, men ingen rad i data/adresser.json. Raden får samme
    form som verktoy/adresser.py lager (bygg_id, adresse, gnr, bnr) + kilde. Kortet viser da adressen, og fra huset selv navnet
    (tegnforklaringen), bygningsnummeret og kulturminne (matrikkelfeltet). Byggeår finnes ikke i Matrikkelens bygningspunkt.
    Rader som finnes, beholder innholdet; bare bygg_id følger adressepunktet (kortet står i huset punktet står i)."""
    reg = bygg_register(L)
    # Kortet følger adressepunktet: står en adresse sitt kort på et annet hus enn det punktet står i (koblet før grunnmur.py
    # delte eller la til hus), flyttes raden dit. Bare bygg_id endres; resten av raden (og rekkefølgen) står.
    hus = {a['adresse']: a['modell_id'] for a in reg['adresser'] if a['sone'] != 'utenfor' and a['modell_id']}
    flyttet = []
    for r in L['kort']:
        ny_id = hus.get(r['adresse'])
        if ny_id and r['bygg_id'] != ny_id:
            flyttet.append((r['adresse'], r['bygg_id'], ny_id)); r['bygg_id'] = ny_id
    for t, a, b in flyttet:
        print(f'  ~ {t}: {a} -> {b} (adressepunktet står i {b})')
    finnes = {r['adresse'] for r in L['kort']}
    nye = []
    for a in reg['adresser']:
        if a['sone'] == 'utenfor' or not a['modell_id'] or a['adresse'] in finnes:
            continue
        nye.append({'bygg_id': a['modell_id'], 'adresse': a['adresse'], 'gnr': a['gnr'], 'bnr': a['bnr'],
                    'kilde': 'verktoy/register.py kort (Kartverkets adresse-API, adressepunktet i huset)'})
        finnes.add(a['adresse'])
    for r in nye:
        print(f"  + {r['adresse']} -> {r['bygg_id']}")
    print(f'{len(nye)} nye kort, {len(flyttet)} flyttet' + (' (tørt, ikke skrevet)' if tørt else ''))
    if tørt or not (nye or flyttet):
        return nye
    rader = L['kort'] + nye
    with open(os.path.join(ROT, 'data', 'adresser.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rader) + '\n]\n')
    return nye


def lag(L):
    reg = bygg_register(L)
    av = avstem(L, reg)
    os.makedirs(UT, exist_ok=True)
    meta = {'_om': ('Fasiten for hva som skal finnes i Gamlebyen (verktoy/register.py). Ett element per kommunehus (FKB-omriss i '
                    'kommunekartet innenfor Gamlebyen-avgrensningen til grunnmur.py), koblet til Matrikkelens bygningspunkt, '
                    'Kartverkets adresser og modellens id. Boligareal/bruksareal finnes ikke i åpne data (krever innlogging); '
                    'areal er fotavtrykket.'),
            'kilder': {'kommunekart': 'kilder/kommunekart/kommunekart.pdf (lokalt)', 'matrikkel': f"kilder/matrikkel-bygningspunkt.json (hentet {L['M_hentet']})",
                       'adresser': f"kilder/adresser.json (hentet {L['A_hentet']})", 'streetview': 'kilder/streetview/avlesning.json'}}
    reg.pop('_intern')
    skriv(os.path.join(UT, 'gamlebyen.json'), dict(meta, **reg))
    skriv(os.path.join(UT, 'avstemming.json'), av)
    for k, v in av['tall'].items():
        print(f'  {k}: {v}')
    for k, v in av['hull'].items():
        print(f'  hull {k}: {len(v)}')
    return reg, av


def ark(L):
    """Kontrollark rapport/register/oversikt.png (bare lokalt: omrissene er kommunekartet): kommunehusene farget etter status,
    modellhusene som strek, adressepunktene som prikker (svart = kort på samme hus, blå = kort lagt til av register.py kort,
    oransje = kort på nabohuset, rød = uten hus eller kort), og hvert nytt kort med adressen skrevet ved punktet."""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    reg = bygg_register(L); I = reg['_intern']; B = L['B']; K = L['K']
    nye = {r['adresse'] for r in L['kort'] if r.get('kilde', '').startswith('verktoy/register.py')}
    fig, ax = plt.subplots(figsize=(24, 24), dpi=110)
    def tegn(P, **kw):
        for g in getattr(P, 'geoms', [P]):
            x, y = g.exterior.xy; ax.fill(x, y, **kw)
    for j, r in zip(L['G'], reg['bygg']):
        farge = '#bfe3bf' if r['modell_id'] else ('#dddddd' if r['areal'] < 6 else '#ff6060')
        if r.get('ogsaa_modell') or any(x['kommune_id'] == r['kommune_id'] for x in []):
            farge = '#ffe08a'
        tegn(K[j], fc=farge, ec='#555555', lw=0.4)
    plass = {b['id']: i for i, b in enumerate(B)}
    for i in I['synlige']:
        P = poly(B[i])
        if L['R'].contains(P.representative_point()):
            x, y = P.exterior.xy; ax.plot(x, y, color='#1b3a6b', lw=0.5)
    for a in reg['adresser']:
        if a['sone'] == 'utenfor':
            continue
        x, y = datalag.til_modell(*a['lonlat'])
        if not a['modell_id'] or not a['kort_paa']:
            c = 'red'
        elif a['adresse'] in nye:
            c = '#0050ff'
        elif not a['kort']:
            c = 'orange'
        else:
            c = 'black'
        ax.plot(x, y, 'o', color=c, ms=4 if c == 'black' else 7)
        if c != 'black':
            ax.annotate(a['adresse'], (x, y), fontsize=6, color=c, xytext=(3, 3), textcoords='offset points')
    x0, y0, x1, y1 = L['R'].bounds
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal')
    ax.set_title('Register: grønn = kommunehus med modellhus, gul = flere modellhus i ett, grå = under 6 m², rød = mangler; '
                 'strek = modellhus; prikk svart = kort, blå = nytt kort, oransje = kort på nabohus, rød = mangler')
    os.makedirs(os.path.join(ROT, 'rapport', 'register'), exist_ok=True)
    sti = os.path.join(ROT, 'rapport', 'register', 'oversikt.png'); fig.savefig(sti, bbox_inches='tight'); print(sti)


def main():
    arg = sys.argv[1:]
    if arg[:1] == ['hent']:
        hent(); return
    L = last()
    if arg[:1] == ['streetview']:
        streetview_mangler(L); return
    if arg[:1] == ['hent']:
        hent(); return
    if arg[:1] == ['kort']:
        legg_til_kort(L, tørt='--tørt' in arg); return
    if arg[:1] == ['ark']:
        ark(L); return
    lag(L)
    streetview_mangler(L)


if __name__ == '__main__':
    main()
