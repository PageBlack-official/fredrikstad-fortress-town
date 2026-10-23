"""Regel (Vegar): høyden skal komme fra kvartaltegningene der de finnes.
Funn 23.10: h = tegnet_h / 1.72 for 207 hus (median, kvartiler 1.72–1.73), så høydene ER fra tegningene der tegnet_h finnes.
Det som gjenstår er husene uten tegnet høyde, som står med OSM-rundetall (3,0 / 6,0 m)."""
from _felles import *
F = 1.72
b = data('bygg'); avvik = []; runde = []
for i, x in gamleby(b):
    if x.get('skjul'): continue
    if x.get('tegnet_h') and x.get('h', 0) > 0.1 and abs(x['tegnet_h'] / F - x['h']) > 0.3: avvik.append(f"- bygg {i} ({x.get('navn') or x.get('type')}): h {x['h']} m, tegning gir {round(x['tegnet_h']/F,1)} m")
    if x.get('h') in (3.0, 6.0) and not x.get('tegnet_h'): runde.append(str(i))
rapport('02_hoyder_fra_tegning', not avvik and not runde, [f"{len(avvik)} hus avviker fra tegnet høyde; {len(runde)} hus uten tegnet høyde står med OSM-rundetall"] + avvik + ([f"- rundetall uten tegning: {', '.join(runde)}"] if runde else []))
