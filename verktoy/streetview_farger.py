"""Street View-farger inn i rettelseslaget, etter fargeregelen (30.10, Vegar; se verktoy/tak_farge.py):

  VEGG: nyeste kilde vinner. Street View fra 2016 eller senere går foran tegningen (2015) og 2019-trykket; Street View før 2015
        (de fleste bildene i Gamlebyen er fra august 2010) er ELDRE enn tegningen og brukes bare der tegningen ikke har huset
        (det gjør verktoy/vegg_nye.py). Året leses av tak_farge.sv_vegg_aar (veggteksten, sidene, bildedatoen).
  TAK:  aldri herfra: ortofoto 2024 og tegningen (verktoy/tak_farge.py).

Kilde: kilder/streetview/avlesning.json (lest av i Vegars Chrome 29.10.2026; bare tekst, ingen Google-bilder).
Ordet går foran RGB-tallet: tallene er pikselmedianer fra skjermbilder og blir mørke i skygge og motlys.
Fargene er flate kartfarger i samme lyshet som trykket. Har tegningen samme kulør som ordet, får huset tegningens farge
(Vegars palett; «tilnærmet riktig er nok, feil kulør er ikke lov»).

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
    (r'laksoransje|rødoransje|\boransje\b', (232, 140, 84)),   # oransje er hovedordet i «laksoransje» (987370, Street View 2024; tegningen oransje)
    (r'terrakotta', (206, 112, 82)),        # terrakotta er oransjerød, ikke oksiderød («rødbrun/terrakotta» 867952, «laksrød/terrakotta»)
    (r'gråfiolett|rosa-grå|rosagrå', (204, 192, 198)),   # grå med et rosa/fiolett skjær, ikke laks (867928, Street View 2019)
    (r'laks|rosa(?!hvit)|fiolett', (226, 170, 160)),
    (r'vinrød', (150, 62, 66)),
    (r'^(mørk )?brun\b', (146, 104, 80)),          # brunt panel ("brun", "brun/rødbrun", "brun/treverk"): brunt, ikke rustrødt (867715 i Street View 2024)
    (r'oksiderød|rødbrun|dyp rød|mørk rød|\brød\b', (176, 74, 62)),
    (r'fersken|aprikos', (250, 200, 160)),
    (r'oransjebrun|okerbrun|gyllen brun', (214, 150, 84)),
    (r'sennep|okergul|\boker\b', (232, 184, 92)),
    (r'gråbeige|greige|beige', (214, 206, 190)),
    (r'lys grå|varm grå|kald grå', (196, 198, 196)),
    (r'kremgul|sandgul|gul|elfenben|sand', (246, 222, 160)),
    (r'grågrønn|grønn', (150, 172, 140)),
    (r'blågrå|blå\b|duebla', (178, 196, 206)),
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

NYERE_ENN = 2016      # Street View fra dette året og senere er nyere enn tegningen (2015) og går foran den


def main():
    tørt = '--tørt' in sys.argv
    avl = json.loads(KILDE.read_text())
    sys.path.insert(0, str(ROT)); sys.path.insert(0, str(ROT / 'verktoy')); import datalag, tak_farge as T
    rett = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    B = T.tilstand_uten_regelen(rett)
    TF = T.tegning_farger(B, rett)
    egen = {b['id'] for b in B if b.get('kirke')}  # kirka har egen modell med egne farger (src/06)
    dato = datetime.date.today().isoformat()
    nye, rapport = [], []
    for id_, a in avl.items():
        if id_ in egen:
            rapport.append((id_, 'egen modell (kirka) – fargene står i src/06')); continue
        if a.get('sikkerhet') == 'ikke synlig':
            rapport.append((id_, 'ikke synlig – tegningen gjelder')); continue
        v = a.get('vegg') or {}
        aar = T.sv_vegg_aar(a)
        if not aar or aar < NYERE_ENN:
            rapport.append((id_, f"Street View {aar or 'uten dato'}: eldre enn tegningen – vegg_nye.py avgjør")); continue
        vegg = fra_ord(v.get('farge'), VEGG) or fra_tall(v.get('rgb'), v.get('lys'))
        if not vegg:
            rapport.append((id_, f"vegg {v.get('farge')!r}: ingen farge lest")); continue
        tegn = (TF.get(id_) or {}).get('vegg')
        umalt_tegl = re.search(r'tegl|murstein', str(v.get('farge')).lower()) and not re.search(r'kalket|malt(?! ?\))|hvit|puss', re.split(r'[,(;]', str(v.get('farge')).lower())[0]) \
            and not re.search(r'\bmalt\b', str(v.get('farge')).lower())
        if tegn and umalt_tegl and T.familie(tegn[0]) in ('oransje', 'rød', 'brun'):
            # umalt tegl males ikke om: tegningen (2015) så den samme mursteinen, og Vegars farge for den (lys tegl/fersken på
            # Kongens magasin og Tøihuset, rødlig på kasernen) gjelder. Ellers blir tegl-vegg og teglstak samme rødfarge.
            farge, kilde = list(tegn[0]), f"Street View {aar} ({v.get('farge')}): umalt tegl = {tegn[1]}: tegningens farge"
        elif tegn and T.samme_kulor(tegn[0], vegg):
            farge, kilde = list(tegn[0]), f"Street View {aar} ({v.get('farge')}) = {tegn[1]}: tegningens farge"
        else:
            farge, kilde = vegg, f"Street View {aar} ({v.get('farge')})" + (f"; tegningen har {T.familie(tegn[0])} ({tegn[1]})" if tegn else '')
        for felt, verdi in (('vegg', farge), ('veggs', None), ('vegg_kilde', kilde), ('vegg_aar', aar)):
            nye.append({'emne': 'bygg', 'id': id_, 'op': 'sett', 'felt': felt, 'verdi': verdi, 'hvem': 'Claude', 'dato': dato, 'grunn': GRUNN})
        rapport.append((id_, f"vegg {v.get('farge')!r} ({aar}) → {farge} [{kilde[:70]}]"))
    for id_, linje in rapport:
        print(id_.ljust(16), linje)
    print(f"{len(nye) // 4} vegger fra Street View {NYERE_ENN} eller senere")
    if tørt:
        return
    datalag.skriv_rettelser(rett + nye)


if __name__ == '__main__':
    main()
