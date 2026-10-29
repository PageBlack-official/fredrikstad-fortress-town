"""Street View-farger inn i rettelseslaget.

Kilde: kilder/streetview/avlesning.json (lest av i Vegars Chrome 29.10.2026; bare tekst, ingen Google-bilder).
Vegars regel 29.10: «Det trenger ikke å være perfekt» – et grønt hus skal være grønt, ikke gult.
Derfor går ordet foran RGB-tallet: tallene er pikselmedianer fra skjermbilder og blir mørke i skygge og motlys.
Fargene er flate kartfarger i samme lyshet som 2019-trykket, ikke målte farger.

Kjør:  python3 verktoy/streetview_farger.py        (skriver linjene, erstatter forrige kjøring)
       python3 verktoy/streetview_farger.py --tørt (viser bare)
"""
import json, re, sys, colorsys, datetime, pathlib
ROT = pathlib.Path(__file__).resolve().parent.parent
KILDE = ROT / 'kilder/streetview/avlesning.json'
RETT = ROT / 'data/rettelser.json'
GRUNN = 'Street View (Vegars Chrome 29.10.2026), ordet foran RGB'

# Ordbok: første treff vinner, så det spesifikke står øverst. Kartfarger, lyse og flate som i trykket.
VEGG = [
    (r'rå.*tegl|tegl.*umalt|umalt.*tegl|^rød tegl|umalt murstein', (184, 98, 78)),
    (r'naturstein|bruddstein|granitt|gråstein', (168, 164, 156)),
    (r'hvitkalket|kalket|hvitmalt', (242, 240, 232)),
    (r'laks|rosa(?!hvit)|gråfiolett|fiolett', (226, 170, 160)),
    (r'vinrød', (150, 62, 66)),
    (r'oksiderød|rødbrun|dyp rød|mørk rød|\brød\b', (176, 74, 62)),
    (r'fersken|aprikos', (250, 200, 160)),
    (r'oransjebrun|okerbrun|gyllen brun', (214, 150, 84)),
    (r'sennep|okergul|\boker\b', (232, 184, 92)),
    (r'gråbeige|greige|beige', (214, 206, 190)),
    (r'lys grå|varm grå|kald grå', (196, 198, 196)),
    (r'kremgul|sandgul|gul|elfenben|sand', (246, 222, 160)),
    (r'grågrønn|grønn', (150, 172, 140)),
    (r'blågrå|\bblå\b', (178, 196, 206)),
    (r'antrasitt|mørk grå|gråbrun', (104, 104, 102)),
    (r'middels grå|ubehandlet|gråbeis|betong|grå', (176, 176, 172)),
    (r'krem|off-white|offwhite|rosahvit|hvit', (242, 240, 232)),
]
TAK = [
    (r'lys grå', (150, 150, 148)),
    (r'rødbrun|brunrød|rød/brun|oksid', (168, 84, 66)),
    (r'oransje', (214, 106, 76)),
    (r'^rød|^tegl', (196, 92, 72)),
    (r'mørk brun|brungrå|betongstein|grå/brun', (96, 84, 76)),
    (r'sort|svart|antrasitt|mørk grå|brunsort|båndtekk|blikk', (70, 70, 72)),
    (r'tegl|\brød', (196, 92, 72)),
    (r'kobber', (120, 170, 150)),
    (r'grå|papp|bølge', (150, 150, 148)),
    (r'mørk', (84, 82, 80)),
]

def fra_ord(tekst, tabell):
    """Første del av teksten (før komma, parentes, tankestrek eller semikolon) leses først, så hele."""
    t = (tekst or '').lower().strip()
    if not t or t.startswith('ikke synlig') or t.startswith('todelt'):
        return None
    første = re.split(r'[,(;–]| over ', t)[0].strip()
    for del_ in (første, t):
        for mønster, rgb in tabell:
            if re.search(mønster, del_):
                return list(rgb)
    return None
def fra_tall(rgb, lys):
    """Reserve når ordet ikke treffer: løft lysheten der avlesningen sier skygge/motlys."""
    if not rgb:
        return None
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in rgb])
    if lys and re.search('skygge|motlys|overskyet', lys):
        v = min(0.92, v + 0.25)
    return [round(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]

def main():
    tørt = '--tørt' in sys.argv
    avl = json.loads(KILDE.read_text())
    rett = json.loads(RETT.read_text())
    sys.path.insert(0, str(ROT)); import datalag
    egen = {b['id'] for b in datalag.alle()['bygg'] if b.get('kirke')}  # kirka har egen modell med egne farger
    dato = datetime.date.today().isoformat()
    nye, rapport = [], []
    for id_, a in avl.items():
        if id_ in egen:
            rapport.append((id_, 'egen modell (kirka) – fargene står i src/06'))
            continue
        if a.get('sikkerhet') == 'ikke synlig':
            rapport.append((id_, 'ikke synlig – tegningen gjelder'))
            continue
        v, t = a.get('vegg') or {}, a.get('tak') or {}
        vegg = fra_ord(v.get('farge'), VEGG) or fra_tall(v.get('rgb'), v.get('lys'))
        tak = fra_ord(t.get('farge'), TAK)
        for felt, verdi in (('vegg', vegg), ('tak', tak)):
            if verdi:
                nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': felt, 'verdi': verdi, 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
                nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': felt + 's', 'verdi': None, 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
        if vegg or tak:
            nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': 'farge_kilde', 'verdi': f"Street View ({a.get('bilde_dato') or 'ukjent dato'}, sikkerhet {a.get('sikkerhet')})", 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
        rapport.append((id_, f"vegg {v.get('farge')!r} → {vegg} | tak {t.get('farge')!r} → {tak}"))
    for id_, linje in rapport:
        print(id_.ljust(16), linje)
    if tørt:
        return
    rett = [r for r in rett if r.get('grunn') != GRUNN] + nye
    RETT.write_text(json.dumps(rett, ensure_ascii=False, separators=(',', ':')).replace('},{', '},\n{'))
    print(f'{len(nye)} linjer skrevet')

if __name__ == '__main__':
    main()
