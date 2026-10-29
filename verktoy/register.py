#!/usr/bin/env python3
"""Registeret: fasiten for hva som skal finnes i Gamlebyen, ett bygg per kommunehus, koblet til statens nøkler.

    python3 verktoy/register.py              bygger kilder/register/gamlebyen.json, avstemming.json og streetview-mangler.json
    python3 verktoy/register.py streetview   bare streetview-mangler.json (gå-lista for Street View-runden)
    python3 verktoy/register.py kort         legger til huskort (data/adresser.json) for adresser som mangler kort; rører aldri
                                             en rad som finnes (kjøres etter verktoy/adresser.py koble, som skriver fila på nytt)
    python3 verktoy/register.py kort --tørt  viser bare hva som ville blitt lagt til

Kilder (alle åpne, ingenting gjettes):
  kommunehus     kilder/kommunekart (FKB-omriss, verktoy/kommunekart.py), avgrenset til Gamlebyen slik grunnmur.py gjør
                 (kommunekart.i_gamlebyen: festningsbyen + 12 m rundt gml-husene, bare hus helt innenfor kartrammen)
  bygningsnummer kilder/matrikkel-bygningspunkt.json (Kartverket, Matrikkelen; status RA/GR/BR/BF regnes ikke, som kommunekart.py)
  adresser       kilder/adresser.json (Kartverkets adresse-API, postnummer 1632)
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


# ---------------------------------------------------------------- lasting
def last():
    D = datalag.alle()
    B = D['bygg']
    K = kommunekart.omriss(); DEK = kommunekart.dekning()
    G = kommunekart.i_gamlebyen(K, DEK)
    R, RAMME = omraade(DEK)
    M = json.load(open(os.path.join(ROT, 'kilder', 'matrikkel-bygningspunkt.json'), encoding='utf8'))
    pkt = [dict(p, P=Point(datalag.til_modell(*p['lonlat']))) for p in M['punkter'] if p['status'] not in IKKE_STAAENDE]
    A = json.load(open(os.path.join(ROT, 'kilder', 'adresser.json'), encoding='utf8'))
    adr = [dict(a, P=Point(datalag.til_modell(a['representasjonspunkt']['lon'], a['representasjonspunkt']['lat']))) for a in A['adresser']]
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
    D = L['D']; gater = _gatelinjer(D)
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
        rader.append(rad)
    grupper = defaultdict(list)
    for r in rader:
        grupper[r['_gate']].append(r)
    ordnet = gaa_rekkefolge(grupper, start='Færgeportgaten')
    ut = {'_om': ('Hus og adresser i Gamlebyen som ikke er lest av i Street View (kilder/streetview/avlesning.json), gatevis i '
                  'gå-rekkefølge (grådig: nærmeste gate etter forrige, husene langs gata). pano_url: punktet på gatas midtlinje '
                  'nærmest huset, heading mot huset. «usikker»: lest, men hopp.json sier det er tvil om det var riktig hus. '
                  'Laget av verktoy/register.py; Google-bildene skal aldri inn i repoet, bare tall og ord i avlesning.json.'),
          'antall': len(rader), 'gater': []}
    for navn, rr in ordnet:
        for r in rr:
            r.pop('_xy'); r.pop('_gate')
        ut['gater'].append({'gate': navn, 'antall': len(rr), 'hus': rr})
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

    kort_ids = defaultdict(list)
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
        rad = {'kommune_id': f'k-{j}', 'areal': round(K[j].area, 1), 'bygningsnumre': [pkt[n]['bygningsnummer'] for n in ns],
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
             'innenfor_kartrammen': RAMME.contains(P[i]), 'kommunehus': [f'k-{j}' for j in mod_k.get(i, [])]}
        r.update(modellfelt(i))
        r['adresser'] = sorted({adr[k]['adressetekst'] for k in b_adr.get(b['id'], [])})
        r['naermeste_gate'] = gate_naer(P[i].representative_point())
        uten_k.append(r)

    # adressene: alle i kilden, med kobling og om de hører til Gamlebyen
    reg_ids = {r['modell_id'] for r in rader + uten_k if r['modell_id']} | {x for r in rader for x in r.get('ogsaa_modell', [])}
    adr_rader = []
    for k, a in enumerate(adr):
        bid, d = a_b[k]
        i_omr = R.contains(a['P'])
        adr_rader.append({'adresse': a['adressetekst'], 'gnr': a['gardsnummer'], 'bnr': a['bruksnummer'],
                          'lonlat': [round(a['representasjonspunkt']['lon'], 6), round(a['representasjonspunkt']['lat'], 6)],
                          'i_gamlebyen': bool(i_omr or (bid in reg_ids)), 'innenfor_kartrammen': L['DEK'].contains(a['P']),
                          'modell_id': bid, 'avstand_m': d, 'kort': a['adressetekst'] in kort_ids.get(bid, [])})
    return {'bygg': rader, 'modell_uten_kommunehus': uten_k, 'adresser': adr_rader,
            '_intern': dict(k_pkt=k_pkt, pkt=pkt, k_mod=k_mod, b_adr=b_adr, a_b=a_b, kort_ids=kort_ids, synlige=synlige)}


if __name__ == '__main__':
    arg = sys.argv[1:]
    L = last()
    if arg[:1] == ['streetview']:
        streetview_mangler(L)
