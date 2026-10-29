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


def hoyden_styrer(data, grunn):
    """Høyden er grunnlaget for alt som står på huset: endres h (rettelse), flyttes piper og arker like mye, og vinduer som
    ikke lenger får plass under gesimsen (overkant over h - 0,3 m) tas ut. Ellers svever pipene og vinduene sitter i taket (24.10)."""
    for x, g in zip(data['bygg'], grunn):
        h0, h1 = g.get('h', 0), x.get('h', 0); f = x.get('th', 0.82) / 0.82   # takhøyden skaleres med helningen
        if abs(h1 - h0) < 0.05 and abs(f - 1) < 0.01:
            continue
        flytt = lambda z: round(h1 + (z - h0) * f, 2) if z > h0 else round(z + h1 - h0, 2)   # over gesims følger taket, under veggen
        if x.get('piper'): x['piper'] = [[q[0], q[1], flytt(q[2])] + q[3:] for q in x['piper']]
        if x.get('arker'): x['arker'] = [[q[0], q[1], flytt(q[2])] + q[3:] for q in x['arker']]
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
