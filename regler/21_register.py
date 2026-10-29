"""Regel: registeret stemmer med kartet (verktoy/register.py, kilder/register/).
Fasiten for hva som skal finnes i Gamlebyen er kommunekartet (FKB-omriss), Matrikkelen (bygningsnummer) og Kartverkets
adresser. Regelen regner registeret på nytt fra kildene (leser ikke en lagret fil), og er rød når
- en adresse i Gamlebyen ikke hører til et modellhus
- et kommunehus i Gamlebyen ikke har modellhus, uten unntak med grunn i kilder/register/unntak.json
- en adresse i Gamlebyen ikke har huskort, eller kortet står i et annet hus enn adressepunktet (verktoy/register.py kort)
- en adresse i randsonen ikke har hus og ikke står i unntak.json med grunn
- avgrensningen i register.py har glidd fra kommunekart.i_gamlebyen
Til kontroll (ikke rødt): bygningsnumre som ikke er id på huset sitt, flere bygningsnumre i ett omriss."""
from _felles import *
import sys
sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import register, kommunekart  # noqa: E402

L = register.last()
reg = register.bygg_register(L)
av = register.avstem(L, reg)
T, H = av['tall'], av['hull']
U = json.load(open(os.path.join(ROT, 'kilder', 'register', 'unntak.json'), encoding='utf8'))
feil, info = [], []

def unntatt(r):
    if r['kommune_id'] in U['hus']: return U['hus'][r['kommune_id']]['grunn'] if isinstance(U['hus'][r['kommune_id']], dict) else U['hus'][r['kommune_id']]
    for q in U['regler']:
        if 'areal_under' in q and r['areal'] < q['areal_under']: return q['grunn']
    return None

uten = [r for r in reg['bygg'] if r['modell_id'] is None]
mangler = [r for r in uten if not unntatt(r)]
for r in mangler:
    feil.append(f"- kommunehus uten modellhus: {r['kommune_id']} ({r['areal']} m², bygningsnr {r['bygningsnumre'] or '–'}, ved {r['naermeste_gate']})")
brukt = {r['kommune_id'] for r in reg['bygg']}
for k in U['hus']:
    if k not in brukt: info.append(f"- unntak {k} finnes ikke lenger i registeret (kommunekartet endret?)")
    elif next(r for r in reg['bygg'] if r['kommune_id'] == k)['modell_id']: info.append(f"- unntak {k} trengs ikke lenger (har modellhus)")
for x in H.get('adresse_uten_bygg', []):
    feil.append(f"- adresse uten modellhus: {x['adresse']} ({x['grunn']})")
UA = U.get('adresser', {})
for x in H.get('randsone_adresse_uten_bygg', []):
    if x['adresse'] not in UA: feil.append(f"- adresse i randsonen uten hus og uten unntak: {x['adresse']} ({x['grunn']})")
uten_hus = {x['adresse'] for x in H.get('randsone_adresse_uten_bygg', [])}
for t in UA:
    if t not in uten_hus: info.append(f"- unntak for adressen {t} trengs ikke lenger (har hus, eller finnes ikke)")
for x in H.get('adresse_uten_kort', []) + H.get('randsone_adresse_uten_kort', []):
    feil.append(f"- adresse uten huskort: {x['adresse']} (hus {x['modell_id']}; kjør verktoy/register.py kort)")
# avgrensningen: register.omraade må gi de samme kommunehusene som kommunekart.i_gamlebyen
K, G = L['K'], set(L['G'])
G2 = {j for j, k in enumerate(K) if L['RAMME'].contains(k) and L['R'].contains(k.representative_point())}
if G != G2: feil.append(f"- avgrensningen i register.omraade har glidd fra kommunekart.i_gamlebyen ({len(G ^ G2)} hus ulikt)")

for x in H.get('id_ikke_bnr', []):
    info.append(f"- id {x['modell_id']} i {x['kommune_id']}, men Matrikkelen har {x['bygningsnumre']} der ({x['grunn']})")
for x in H.get('kort_paa_annet_bygg', []) + H.get('randsone_kort_paa_annet_bygg', []):
    feil.append(f"- kortet for {x['adresse']} står på {', '.join(x['kortet_paa'])}, adressepunktet er i {x['adressepunktet_i']}")
for x in H.get('kort_paa_flere_bygg', []):
    info.append(f"- {x['adresse']} har kort på flere hus: {', '.join(x['bygg'])}")
for x in H.get('flere_bygningsnumre_i_ett_kommunehus', []):
    info.append(f"- {x['kommune_id']}: Matrikkelen har {x['bygningsnumre']} i ett omriss (hus {x['modell_id']})")
info.append(f"- unntatt: {len(uten) - len(mangler)} kommunehus uten modellhus ({U['regler'][0]['grunn'][:40]} …)")
info.append(f"- randsonen (utenfor kommunekartets ramme): {T['adresser_i_randsonen_utenfor_kartrammen']} adresser, "
            f"{T['randsone_adresser_med_bygg']} med hus, {T['randsone_adresser_med_kort']} med kort; "
            f"{len(uten_hus)} uten hus, unntatt i unntak.json")
info.append(f"- Street View: {T['streetview_lest']} lest, {T['streetview_usikker']} usikre, {T['streetview_mangler_med_modellhus']} ikke lest (gå-lista: kilder/register/streetview-mangler.json)")
hode = (f"{T['kommunehus_i_gamlebyen']} kommunehus i Gamlebyen ({T['kommunehus_med_modellhus']} med modellhus), "
        f"{T['bygningsnumre_i_kommunehusene']} bygningsnumre, {T['adresser_i_gamlebyen']} adresser ({T['adresser_med_bygg']} med hus, "
        f"{T['adresser_med_kort_paa_samme_bygg'] + T['adresser_med_kort_paa_annet_bygg']} med kort), {T['modellhus_i_gamlebyen']} modellhus")
rapport('21_register', not feil, [hode] + feil + (['', 'Til kontroll:'] + info if info else []))
