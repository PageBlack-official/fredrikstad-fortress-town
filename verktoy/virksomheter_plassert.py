"""Håndplasserte virksomheter og fløyer (31.10, Tøihuset): legges oppå data/virksomheter.json og data/adresser.json etter
adresser.py koble og register.py kort. Idempotent: egne linjer tas ut og legges inn på nytt.

  kilder/virksomheter-plassert.json
    plassert  {orgnr, bygg_id, grunn}   virksomheten (fra Enhetsregisteret) står i denne fløya, ikke der adressepunktet er
    steder    {id, navn, bygg_id, hele_bygget?, kilde}   steder uten oppføring i Enhetsregisteret med adresse i Gamlebyen;
              hele_bygget: plassen i bygget er ikke kjent, så huskortet viser stedet på alle fløyene («Også i bygget»)
  Bygg delt i fløyer (husdeling «felles_tak», felt «floyer»): adressen står på alle fløyene.

Kjør: python3 verktoy/virksomheter_plassert.py"""
import json, os, sys
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag

KILDE = 'kilder/virksomheter-plassert.json'


def skriv(navn, rader):
    with open(os.path.join(ROT, 'data', navn + '.json'), 'w', encoding='utf8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rader) + '\n]\n')


def main():
    hp = json.load(open(os.path.join(ROT, KILDE), encoding='utf8'))
    B = {b['id']: b for b in datalag.alle()['bygg'] if not b.get('skjul')}
    V = [v for v in datalag.les('virksomheter') if not v.get('id', '').startswith('sted-')]
    A = [a for a in datalag.les('adresser') if a.get('kilde') != KILDE]
    n = 0
    for p in hp.get('plassert', []):
        if p['bygg_id'] not in B: print('finnes ikke:', p['bygg_id']); continue
        for v in V:
            if v.get('orgnr') == p['orgnr'] and v['bygg_id'] != p['bygg_id']:
                v.update(bygg_id=p['bygg_id'], kilde_plass=KILDE); n += 1
            elif v.get('orgnr') == p['orgnr']:
                v['kilde_plass'] = KILDE
    for st in hp.get('steder', []):
        if st['bygg_id'] not in B: print('finnes ikke:', st['bygg_id']); continue
        V.append({k: st[k] for k in ('id', 'bygg_id', 'navn', 'hele_bygget', 'kilde') if k in st}); n += 1
    m = 0
    for b in B.values():
        for a in [a for a in A if a['bygg_id'] in (b.get('floyer') or []) and a['bygg_id'] != b['id']]:
            if not any(x['bygg_id'] == b['id'] and x['adresse'] == a['adresse'] for x in A):
                A.append(dict(a, bygg_id=b['id'], kilde=KILDE)); m += 1
    skriv('virksomheter', V); skriv('adresser', A)
    print(f"{n} virksomheter plassert for hånd eller lagt til, {m} adresser lagt på fløyer")


if __name__ == '__main__':
    main()
