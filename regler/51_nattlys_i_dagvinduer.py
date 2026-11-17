"""Regel 51 (PAG-1651, Vegar 17.11: «nattvinduene er feil plassert»): nattlyset skal ligge i glasset slik dagvinduet tegner det.

Tegner samme gatekamera to ganger, kl. 13:00 og kl. 22:30 (verktoy/dagnatt.mjs, standpunktene i
kilder/gate/nattlys-standpunkter.json: Voldportgaten 75/73/Therese M, seks hus fra en tilfeldig stikkprøve og Isegranhuset
med rutenettvinduer). Hvert varmt lysende punkt om natta må være glass om dagen (blågrått og mørkere enn veggen), med én
piksels slingring i kanten. Rød hvis mer enn 3 % av lyset i ett bilde havner utenfor et dagvindu: på karm, foring, sprosser,
dørblad eller vegg. Før PAG-1651 tente en lyshetsterskel alt mørkt i vindusplata (brun karm, dører): 14–62 % utenfor.

Regelen leser bildene, ikke koden, så den fanger lys fra alle lag (vindusinstansene i src/07 og de tegnede vinduene i src/05).
Gml-husene med LOD-bleket glass er ikke med: dagglasset deres er for lyst til å skilles fra veggen på farge."""
import subprocess, os, json
from _felles import ROT, rapport
from PIL import Image
import numpy as np
import cv2

GRENSE = 3.0   # prosent av nattlyset i ett bilde som får ligge utenfor dagglasset
ut = os.path.join(ROT, 'rapport', '_nattlys'); os.makedirs(ut, exist_ok=True)
punkter = os.path.join(ROT, 'kilder', 'gate', 'nattlys-standpunkter.json')
r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'dagnatt.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), punkter, ut],
                   capture_output=True, text=True, cwd=ROT, timeout=1800)


def maal(navn):
    D = np.asarray(Image.open(os.path.join(ut, navn + '_dag.png')).convert('RGB')).astype(np.float32) / 255
    N = np.asarray(Image.open(os.path.join(ut, navn + '_natt.png')).convert('RGB')).astype(np.float32) / 255
    lys = (N[..., 0] > 0.75) & (N[..., 1] > 0.6) & (N[..., 0] - N[..., 2] > 0.18)          # varmt nattlys
    glass = (D[..., 2] - D[..., 0] > 0.03) & (D.mean(-1) < 0.62)                            # dagglass: blågrått og mørkt
    glass = cv2.dilate(glass.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0              # én piksels slingring i kanten
    lys[:60] = False                                                                        # knappene oppe til venstre
    feil = lys & ~glass
    # bevis: dag | natt | rødt der lyset ligger utenfor dagglasset
    m = (N * 255).astype(np.uint8).copy(); m[feil] = (255, 0, 0)
    Image.fromarray(np.concatenate([(D * 255).astype(np.uint8), m], 1)).resize((1280, 360)).save(os.path.join(ut, navn + '_dagnatt.png'))
    return int(lys.sum()), int(feil.sum())


linjer, ok, verst = [], True, None
for p in json.load(open(punkter)):
    try:
        n, f = maal(p['navn'])
    except FileNotFoundError:
        ok = False; linjer.append(f"- {p['navn']}: ikke tegnet ({(r.stderr or r.stdout).strip()[-200:]})"); continue
    pst = 100 * f / max(n, 1)
    if pst > GRENSE: ok = False
    if verst is None or pst > verst[1]: verst = (p['navn'], pst)
    linjer.append(f"- {p['navn']}: {n} px nattlys, {f} utenfor dagglasset ({pst:.1f} %){'  <- FEIL' if pst > GRENSE else ''}")
hode = f"verst {verst[0]} {verst[1]:.1f} % (krav: høyst {GRENSE:.0f} % av nattlyset utenfor dagvinduene)" if verst else 'ingen bilder'
rapport('51_nattlys_i_dagvinduer', ok, [hode, ''] + linjer, f'rapport/_nattlys/{verst[0]}_dagnatt.png' if verst else None)
