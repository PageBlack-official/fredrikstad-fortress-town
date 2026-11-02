"""Regel (02.11): avvikslista er tom for åpne saker, og hver lukket sak har bevis og vakt.
Vegar 02.11 16:44: «Kan du holde styr på dette slik at ting du gjør ikke havner i glemmeboken når du driver å fikser? ... nesten er ikke lov».
Lista er kilder/avvik.json. Bevis = filer i repoet (før/etter-bilder). Vakt = navnet på en regel (regler/NN_*.py) eller test (verktoy/*) som finnes.
"""
import json, glob
from _felles import *
d = json.load(open(os.path.join(ROT, 'kilder', 'avvik.json'), encoding='utf8'))
linjer = []; ok = True
for s in d['saker']:
    if s['status'] != 'lukket':
        ok = False; linjer.append(f"åpen  {s['id']}: {s['hva'][:110]}"); continue
    mangler = [b for b in s.get('bevis', []) if not os.path.exists(os.path.join(ROT, b))]
    vakt = s.get('vakt')
    vakt_ok = bool(vakt) and (os.path.exists(os.path.join(ROT, vakt)) or bool(glob.glob(os.path.join(ROT, 'regler', vakt + '*.py'))))
    if not s.get('bevis') or mangler or not vakt_ok:
        ok = False; linjer.append(f"FEIL {s['id']} lukket uten {'bevis' if not s.get('bevis') or mangler else ''}{' og ' if (not s.get('bevis') or mangler) and not vakt_ok else ''}{'vakt' if not vakt_ok else ''}")
    else:
        linjer.append(f"ok   {s['id']} lukket ({s.get('rettet_i')}), vakt {vakt}")
rapport('36_avviksliste', ok, [f"{sum(s['status']!='lukket' for s in d['saker'])} åpne av {len(d['saker'])}"] + linjer)
