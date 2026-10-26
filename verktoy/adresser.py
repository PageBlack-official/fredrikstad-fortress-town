#!/usr/bin/env python3
"""Adresser og virksomheter per bygg, koblet på byggets faste id (se datalag.py).

  python3 verktoy/adresser.py hent    henter offisielle adresser (Kartverket, CC BY 4.0) og virksomheter (Brønnøysund, NLOD)
                                      for postnumrene i POSTNR til kilder/
  python3 verktoy/adresser.py koble   skriver data/adresser.json og data/virksomheter.json (bygg_id -> adresse, gnr/bnr, virksomheter)

Dette er verktøyet byverten (agenten) kjører når registrene endrer seg: henting og kobling er adskilt, og koblingen gir samme
svar for samme kilder. Virksomheter som ikke vender mot besøkende, vises ikke i kartet (BESOK), men ligger i kilden.
"""
import json, os, re, sys, urllib.request, urllib.parse, datetime

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT)
from datalag import til_modell, les  # noqa: E402
sys.path.insert(0, os.path.join(ROT, 'verktoy'))
from matrikkel import inni, avstand  # noqa: E402

POSTNR = ['1632']                 # Gamle Fredrikstad
NAER = 8.0                        # meter: adressepunkt like utenfor fotavtrykket (punktet står ofte ved inngangen)
# næringskoder (to første sifre) for steder en besøkende går inn i: butikk, overnatting, servering, museum og historiske steder.
# Kunstnere, foreninger og konsulenter står ofte registrert på hjemmeadressen; de vises ikke før de legger seg inn selv.
BESOK = {'47', '55', '56', '91'}
UA = {'User-Agent': 'pageblack-smartoldtown'}


def _hent(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))


def hent():
    adr, virk = [], []
    for pn in POSTNR:
        side = 0
        while True:
            d = _hent('https://ws.geonorge.no/adresser/v1/sok?' + urllib.parse.urlencode(
                {'postnummer': pn, 'treffPerSide': 1000, 'side': side, 'utkoordsys': 4258}))
            adr += d['adresser']
            if d['metadata']['viserTil'] >= d['metadata']['totaltAntallTreff']:
                break
            side += 1
        side = 0
        while True:
            d = _hent('https://data.brreg.no/enhetsregisteret/api/underenheter?' + urllib.parse.urlencode(
                {'beliggenhetsadresse.postnummer': pn, 'size': 1000, 'page': side}))
            virk += d.get('_embedded', {}).get('underenheter', [])
            if side + 1 >= d['page']['totalPages']:
                break
            side += 1
    dato = datetime.date.today().isoformat()
    json.dump({'kilde': 'ws.geonorge.no/adresser/v1', 'lisens': 'CC BY 4.0, Kartverket', 'hentet': dato, 'adresser': adr},
              open(os.path.join(ROT, 'kilder', 'adresser.json'), 'w', encoding='utf8'), ensure_ascii=False)
    json.dump({'kilde': 'data.brreg.no/enhetsregisteret', 'lisens': 'NLOD, Brønnøysundregistrene', 'hentet': dato, 'underenheter': virk},
              open(os.path.join(ROT, 'kilder', 'virksomheter.json'), 'w', encoding='utf8'), ensure_ascii=False)
    print(f'{len(adr)} adresser, {len(virk)} virksomheter hentet')


def norm(t):
    return re.sub(r'\s+', ' ', (t or '').lower().replace('gt.', 'gaten').replace('gate ', 'gaten ')).strip()


def visningsnavn(navn):
    """Brønnøysund skriver med store bokstaver; kartet viser navnet slik et skilt ville gjort. «AS» og avdelingsledd tas bort."""
    n = re.sub(r'\s+(AS|ASA|DA|ANS)\b.*$', '', navn).strip()
    n = re.sub(r'\s+AVD\.?\s.*$', '', n).strip()
    return ' '.join(w if len(w) <= 2 and w.isupper() and w in ('IL',) else w.capitalize() for w in n.lower().split()).replace('Cafe', 'Café')


def koble():
    bygg = les('bygg')
    adr = json.load(open(os.path.join(ROT, 'kilder', 'adresser.json'), encoding='utf8'))['adresser']
    virk = json.load(open(os.path.join(ROT, 'kilder', 'virksomheter.json'), encoding='utf8'))['underenheter']
    flater = [(b['id'], b['p']) for b in bygg if len(b.get('p') or []) >= 3 and not b.get('skjul')]
    ut_adr, adr_til_bygg = [], {}
    for a in sorted(adr, key=lambda a: (a['adressenavn'] or '', a['nummer'] or 0, a['bokstav'] or '')):
        x, y = til_modell(a['representasjonspunkt']['lon'], a['representasjonspunkt']['lat'])
        treff = [bid for bid, p in flater if inni(x, y, p)]
        if not treff:
            n = min(((avstand(x, y, p), bid) for bid, p in flater), default=(1e9, None))
            treff = [n[1]] if n[0] <= NAER else []
        if not treff:
            continue
        adr_til_bygg[norm(a['adressetekst'])] = treff[0]
        ut_adr.append({'bygg_id': treff[0], 'adresse': a['adressetekst'], 'gnr': a['gardsnummer'], 'bnr': a['bruksnummer']})
    ut_virk, uten = [], []
    for v in sorted(virk, key=lambda v: v['navn']):
        kode = (v.get('naeringskode1') or {}).get('kode', '')
        if kode[:2] not in BESOK or re.search(r'KONKURSBO|TVANGSAVVIKLINGSBO|AVVIKLINGSBO', v['navn']) or v.get('nedleggelsesdato'):
            continue
        if (v.get('organisasjonsform') or {}).get('kode') == 'ENK' and not v.get('antallAnsatte'):
            continue                                  # enkeltpersonforetak uten ansatte: personnavn på en adresse, ikke et sted å besøke
        tekst = norm(' '.join((v.get('beliggenhetsadresse') or {}).get('adresse') or []))
        bid = adr_til_bygg.get(tekst)
        if not bid:
            uten.append(v['navn']); continue
        if any(r['bygg_id'] == bid and norm(r['navn']).replace('-', ' ') == norm(visningsnavn(v['navn'])).replace('-', ' ') for r in ut_virk):
            continue                                  # samme sted registrert to ganger (f.eks. med og uten AS)
        ut_virk.append({'id': 'org-' + v['organisasjonsnummer'], 'bygg_id': bid, 'navn': visningsnavn(v['navn']), 'registrert': v['navn'], 'orgnr': v['organisasjonsnummer'],
                        'bransje': (v.get('naeringskode1') or {}).get('beskrivelse', ''), 'ansatte': v.get('antallAnsatte') or 0})
    for navn, rader in (('adresser', ut_adr), ('virksomheter', ut_virk)):
        with open(os.path.join(ROT, 'data', navn + '.json'), 'w', encoding='utf8') as f:
            f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rader) + '\n]\n')
    print(f'{len(ut_adr)} adresser koblet til {len({r["bygg_id"] for r in ut_adr})} bygg; '
          f'{len(ut_virk)} besøksrettede virksomheter i {len({r["bygg_id"] for r in ut_virk})} bygg; '
          f'{len(uten)} besøksrettede uten bygg i kartet (utenfor vollene eller ukjent adresse)')


if __name__ == '__main__':
    {'hent': hent, 'koble': koble}[sys.argv[1] if len(sys.argv) > 1 else 'koble']()
