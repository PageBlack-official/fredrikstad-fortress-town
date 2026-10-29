"""Datalaget: ett sted for hvordan kartets data leses, rettes og kobles sammen.
Brukes av bygg.py, regelsjekkene og verktøyene, så reglene for rettelser og ID-er bare finnes én gang.

ID-er (26.10.2026): hvert bygg har en fast nøkkel i feltet `id`.
  bnr-<bygningsnummer>  bygget finnes i Matrikkelen (Kartverket, CC BY 4.0). Statens nøkkel: samme nummer brukes av
                        kommunen, Forsvarsbygg, meglere og Riksantikvaren. Står det flere matrikkelbygg i samme fotavtrykk,
                        ligger alle i `matrikkel`, og det laveste nummeret er nøkkelen.
  pb-<løpenummer>       objekt uten matrikkelbygg (porter, murer, uthus OSM har og matrikkelen ikke). Løpenummeret deles
                        ut én gang og brukes aldri igjen.
Alle ID-er som noen gang er delt ut, står i kilder/id-register.txt (bare tillegg). En ID forsvinner aldri: et bygg som
ikke skal vises, skjules med grunn. Rettelser og koblinger (porter, legende) peker på ID, aldri på plass i lista.
"""
import json, math, os

ROT = os.path.dirname(os.path.abspath(__file__))
ORIGO = (10.952745, 59.202835)          # modellens (0,0): lon, lat (KILDER.md); x = øst, y = nord i meter
_R = 6378137.0


def _merc(lon, lat):
    return _R * math.radians(lon), _R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


_MX0, _MY0 = _merc(*ORIGO)
_S = math.cos(math.radians(ORIGO[1]))


def til_modell(lon, lat):
    """Grader -> modellmeter. Samme projeksjon som src/00_oppsett.js (web-mercator skalert til meter ved origo)."""
    mx, my = _merc(lon, lat)
    return (mx - _MX0) * _S, (my - _MY0) * _S


def les(navn):
    return json.load(open(os.path.join(ROT, 'data', navn + '.json'), encoding='utf8'))


def indeks(liste):
    """id -> plass i lista. Stopper hvis to objekter har samme id."""
    ut = {}
    for i, x in enumerate(liste):
        if 'id' not in x:
            continue
        if x['id'] in ut:
            raise SystemExit(f"id brukt to ganger: {x['id']} (plass {ut[x['id']]} og {i})")
        ut[x['id']] = i
    return ut


def legg_paa_rettelser(data, rettelser):
    """Rettelseslaget legges oppå grunndataene. Hver rettelse peker på id. Nyere linje vinner over eldre.
    Operasjoner:
      sett   felt = verdi på objektet med id
      skjul  objektet vises ikke (grunnen står i feltet skjul); id-en finnes fortsatt
      ny     et objekt grunndataene ikke har (verdi = hele objektet, med id). De nye legges bakerst i lista, i rekkefølgen
             de står i rettelsene, før noen sett/skjul legges på, så en rettelse kan peke på et nytt objekt uansett hvor den
             står. Står samme id i flere ny-linjer, vinner den nyeste. En ny-id kan ikke være en id grunndataene har.
             Plassene til objektene i grunndataene endres aldri (regel 02 og rapport/hoyder bruker plass i lista)."""
    oppslag = {emne: indeks(v) for emne, v in data.items() if isinstance(v, list)}
    nye = {}
    for r in rettelser:
        if r['op'] == 'ny':
            v = r.get('verdi') or {}
            if v.get('id') != r.get('id'):
                raise SystemExit(f"ny-rettelse: id i linja ({r.get('id')}) og i objektet ({v.get('id')}) er ulike")
            if r['id'] in oppslag.get(r['emne'], {}):
                raise SystemExit(f"ny-rettelse: {r['emne']} {r['id']} finnes i grunndataene (bruk sett)")
            nye.setdefault(r['emne'], {})[r['id']] = v
    for emne, obj in nye.items():
        liste = data.setdefault(emne, [])
        for id_, v in obj.items():
            oppslag.setdefault(emne, {})[id_] = len(liste)
            liste.append(json.loads(json.dumps(v)))
    for r in rettelser:
        emne, op = r['emne'], r['op']
        if op == 'ny':
            continue
        i = oppslag.get(emne, {}).get(r.get('id'))
        if i is None:
            raise SystemExit(f"rettelse peker på noe som ikke finnes: {r.get('emne')} {r.get('id')}")
        if op == 'sett':
            data[emne][i][r['felt']] = r['verdi']
        elif op == 'skjul':
            data[emne][i]['skjul'] = f"{r.get('hvem', '?')} {r.get('dato', '?')}: {r.get('grunn', '')}"
        else:
            raise SystemExit(f"ukjent rettelse-operasjon: {op}")
    return data


def nye_ider(rettelser, emne='bygg'):
    """Id-ene som rettelseslaget lager (op ny)."""
    return {r['id'] for r in rettelser if r['op'] == 'ny' and r['emne'] == emne}


def alle(raa=False):
    """Alle emnene i data/ som ett objekt, med rettelsene lagt oppå (raa=True gir grunndataene)."""
    data = {f[:-5]: les(f[:-5]) for f in sorted(os.listdir(os.path.join(ROT, 'data'))) if f.endswith('.json')}
    rettelser = data.pop('rettelser', [])
    if raa:
        return data
    grunn = [dict(x) for x in data['bygg']]
    return hoyden_styrer(legg_paa_rettelser(data, rettelser), grunn)


def tak_t(x, px, py):
    """Takets høyde over gesims (før takhelningen th) i punktet, fra takflatene (tak2, ellers sk); høyeste flate over punktet.
    None når huset ikke har takflater."""
    flater = x.get('tak2') or x.get('sk')
    if not flater:
        return None
    best = 0.0
    for f in flater:
        if len(f) < 3:
            continue
        xs, ys = [q[0] for q in f], [q[1] for q in f]
        if not (min(xs) - 0.05 <= px <= max(xs) + 0.05 and min(ys) - 0.05 <= py <= max(ys) + 0.05):
            continue
        inne = False                                  # punkt i polygon (strålemetoden), med 5 cm slingring i kantene
        for k in range(len(f)):
            (x1, y1), (x2, y2) = f[k][:2], f[k - 1][:2]
            if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1:
                inne = not inne
        if not inne:
            continue
        import numpy as np
        A = np.array([[q[0], q[1], 1] for q in f]); z = np.array([q[2] for q in f])
        k_ = np.linalg.lstsq(A, z, rcond=None)[0]
        best = max(best, float(k_[0] * px + k_[1] * py + k_[2]))
    return best


KNEKK = dict(t_brudd=0.9, nedre_grader=70.0, ovre_grader=25.0)   # knekktak (mansard): bratt nedre del 0,9 m inn, slakt over


def _klipp(f, a, b, c):
    """Polygonet f (punkter [x, y, z]) klippet til halvplanet a*x + b*y <= c (Sutherland–Hodgman)."""
    ut = []
    for k in range(len(f)):
        p, q = f[k - 1], f[k]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fq <= 1e-9:
            if fp > 1e-9:
                t = fp / (fp - fq); ut.append([p[i] + (q[i] - p[i]) * t for i in range(3)])
            ut.append(list(q))
        elif fp <= 1e-9:
            t = fp / (fp - fq); ut.append([p[i] + (q[i] - p[i]) * t for i in range(3)])
    return ut


def knekktak(tak2, th):
    """Knekktak (mansard) av et vanlig tak: hver takflate (z = t, avstand inn fra takfoten, lineær over flaten) deles langs
    t = t_brudd; høyden blir bratt (nedre_grader) opp til bruddet og slak (ovre_grader) over. Høydene lagres slik kartet
    tegner dem (z·th), så alle verktøy og src/07 tegner knekktaket uten egen kode."""
    import math
    tb, k1, k2 = KNEKK['t_brudd'], math.tan(math.radians(KNEKK['nedre_grader'])), math.tan(math.radians(KNEKK['ovre_grader']))
    def z(t): return (k1 * t if t <= tb else k1 * tb + k2 * (t - tb)) / th
    ut = []
    for f in tak2:
        if len(f) < 3:
            continue
        import numpy as np
        A = np.array([[q[0], q[1], 1.0] for q in f]); kz = np.linalg.lstsq(A, np.array([q[2] for q in f]), rcond=None)[0]
        a, b, c0 = float(kz[0]), float(kz[1]), float(kz[2])
        if abs(a) + abs(b) < 1e-9:
            ut.append([[q[0], q[1], z(q[2])] for q in f]); continue
        for del_ in (_klipp(f, a, b, tb - c0), _klipp(f, -a, -b, -(tb - c0))):
            if len(del_) >= 3:
                ut.append([[round(q[0], 3), round(q[1], 3), round(z(a * q[0] + b * q[1] + c0), 3)] for q in del_])
    return ut


def hoyden_styrer(data, grunn):
    """Høyden er grunnlaget for alt som står på huset (24.10).
    Piper og arker står på taket: høyden deres regnes alltid fra takflatene og husets høyde (h + t·th, samme formel som kartet
    tegner taket med), så de følger med når h, th eller taket endres, uansett om posisjonen kommer fra grunndata eller rettelse
    (29.10: arker havnet på −2,08 m fordi en rettelse var regnet mot ny høyde og så flyttet en gang til). Hus uten takflater
    flyttes som før, med høydeendringen. Vinduer som ikke lenger får plass under gesimsen (overkant over h - 0,3 m) tas ut."""
    for j, x in enumerate(data['bygg']):
        g = grunn[j] if j < len(grunn) else x
        if x.get('takform') == 'knekk' and x.get('tak2') and not x.get('_knekk'):
            x['tak2'] = knekktak(x['tak2'], x.get('th') or 0.82); x['_knekk'] = True
        h0, h1 = g.get('h', 0), x.get('h', 0); th = x.get('th', 0.82); f = th / 0.82
        CAP = 7.5 * th / 0.82 if not x.get('tak2') else 1e9
        for felt in ('piper', 'arker'):
            if not x.get(felt):
                continue
            ny = []
            for q in x[felt]:
                t = tak_t(x, q[0], q[1])
                if t is not None:
                    z = round(h1 + min(t * th, CAP), 2)
                elif abs(h1 - h0) >= 0.05 or abs(f - 1) >= 0.01:
                    z = round(h1 + (q[2] - h0) * f, 2) if q[2] > h0 else round(q[2] + h1 - h0, 2)
                else:
                    z = q[2]
                ny.append([q[0], q[1], z] + list(q[3:]))
            x[felt] = ny
        if abs(h1 - h0) < 0.05 and abs(f - 1) < 0.01:
            continue
        if x.get('vind') and x['vind'] is g.get('vind'):   # vinduer satt med egen rettelse er allerede lest mot målt høyde (v33)
            x['vind'] = [v for v in x['vind'] if v[2] + v[8] / 2 <= x['h'] - 0.3]
    return data


def koble_til_plass(data):
    """Koblinger lagres som id (bygg_id). Tegnekoden i src/ jobber med plass i lista, så bygget får plassen her, ved bygging."""
    plass = indeks(data['bygg'])
    for emne in ('porter', 'legende'):
        for x in data.get(emne, []):
            bid = x.get('bygg_id')
            if bid is None:
                x['bygg'] = None
                continue
            if bid not in plass:
                raise SystemExit(f"{emne} peker på bygg som ikke finnes: {bid}")
            x['bygg'] = plass[bid]
    return data


def skriv_rettelser(rettelser):
    """Én linje per rettelse (lett å lese og å se i git). Alle verktøy som lager rettelser, skriver med denne."""
    with open(os.path.join(ROT, 'data', 'rettelser.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rettelser) + '\n]\n')
