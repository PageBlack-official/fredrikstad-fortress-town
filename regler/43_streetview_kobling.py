"""Regel (02.11, avvik A11/A12): Street View-observasjonene som brukes, peker på huset de er brukt på.
Vegar 02.11 18:29: «Noter deg at Street view-bildene du har tatt ikke stemmer helt overens med 3d-modellene.»
verktoy/sv_kobling.py sender stråler fra kamerapunktet (pano_url) i vifte rundt retningen og sjekker at huset er det første
bildet treffer i den delen av bildet avlesningen sier (venstre/høyre/midten). 78 av 332 observasjoner (48 hus) pekte på et annet
hus. Regelen er rød når
  - dommen i kilder/streetview/kobling-geometri.json ikke er den geometrien gir nå (omriss eller avlesning endret uten ny kjøring),
  - et hus har vegg-, fasade- eller sokkelverdi fra Street View uten en godkjent observasjon (sv_kobling.les),
  - verktøyene som bruker avlesningen, leser den uten sv_kobling.les.
"""
import sys, json, glob, re
from _felles import *
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, sv_kobling  # noqa: E402

feil, linjer = [], []
d = datalag.alle()
nå = sv_kobling.dom(d)
lagret = json.load(open(sv_kobling.DOM, encoding='utf8'))['dom'] if os.path.exists(sv_kobling.DOM) else {}
ulik = [i for i in set(nå) | set(lagret) if {k: v['ok'] for k, v in nå.get(i, {}).items()} != {k: v['ok'] for k, v in lagret.get(i, {}).items()}]
if ulik: feil.append(f"FEIL kobling-geometri.json er gammel for {len(ulik)} hus (kjør verktoy/sv_kobling.py): {', '.join(sorted(ulik)[:8])}")
godkjent = sv_kobling.les(d)
slekt = sv_kobling.slektninger(d['bygg'])   # biter og fløyer arver fargen fra huset de er delt fra
for b in d['bygg']:
    if b.get('skjul'): continue
    kilder = [str(b.get('vegg_kilde') or ''), 'streetview' if b.get('fasade_kilde') == 'streetview' else '']
    if any(k.startswith('Street View 20') for k in kilder[:1]) or kilder[1]:
        if b['id'] not in godkjent and not (slekt.get(b['id'], set()) & set(godkjent)):
            feil.append(f"FEIL {b['id']} ({b.get('navn') or ''}): bruker Street View ({kilder[0][:40] or 'fasade'}) uten godkjent observasjon")
for f in ('streetview_farger.py', 'streetview_fasader.py', 'sokkel.py', 'fasadesegmenter.py', 'tak_farge.py'):
    k = open(os.path.join(ROT, 'verktoy', f), encoding='utf8').read()
    if 'sv_kobling' not in k: feil.append(f"FEIL verktoy/{f} leser avlesningen uten sv_kobling.les")
n = sum(len(v) for v in nå.values()); n_feil = sum(1 for v in nå.values() for o in v.values() if not o['ok'])
linjer.append(f"{n} observasjoner, {n_feil} peker ikke på huset ({sum(1 for v in nå.values() if any(not o['ok'] for o in v.values()))} hus); de brukes ikke")
rapport('43_streetview_kobling', not feil, [f"{len(feil)} feil"] + feil + linjer)
