"""Takfarge fra ortofoto 2024 på hus som ellers står med standardfarge (nye bygg fra kommunekartet uten Street View-farge).
Pikslene inne i omrisset (0,6 m inn fra kanten, så takfot og naboer ikke teller) tas som median og legges på nærmeste av
takfargene i verktoy/streetview_farger.py (samme kartpalett); er spredningen stor (trær over taket), hoppes huset over og listes.
Veggen ses ikke fra lufta: den står nøytral til Street View eller tegningen gir en farge (punkt 9: «usikker på det bak: flyfoto»).

    python3 verktoy/tak_fra_ortofoto.py [--tørt]       (etter streetview_farger.py)
"""
import json, os, sys, colorsys
import numpy as np, cv2
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROT); sys.path.insert(0, os.path.join(ROT, 'verktoy'))
import datalag, flater as FL
from shapely.geometry import Polygon
GRUNN = 'takfarge fra ortofoto 2024 (verktoy/tak_fra_ortofoto.py)'
PALETT = {'rød tegl': (196, 92, 72), 'rødbrun tegl': (168, 84, 66), 'oransje tegl': (214, 106, 76), 'mørk brun': (96, 84, 76),
          'svart/antrasitt': (70, 70, 72), 'mørk': (84, 82, 80), 'grå': (150, 150, 148), 'lys grå': (176, 176, 172), 'grønn (kobber/mose)': (120, 170, 150)}
# fotofarger (median i ortofotoet, sol) for hver kartfarge, målt på hus med kjent takfarge i Street View
FOTO = {'rød tegl': (170, 100, 85), 'rødbrun tegl': (130, 85, 75), 'oransje tegl': (185, 120, 90), 'mørk brun': (95, 85, 78),
        'svart/antrasitt': (60, 60, 62), 'mørk': (80, 80, 80), 'grå': (130, 130, 130), 'lys grå': (175, 175, 172), 'grønn (kobber/mose)': (110, 130, 105)}


def klasse(rgb):
    """Fotofarge -> kartfarge etter kulør (hue), metning og lyshet: grå/blågrå tak (skifer, blikk, papp) etter lyshet, varme
    kulører med metning som tegl, umettede varme som grå (betongstein, falmet). Grønt leses ikke som tak (trær over)."""
    h, s, v = colorsys.rgb_to_hsv(*(np.asarray(rgb) / 255))
    if s < 0.12 or 0.5 < h < 0.75:                       # grått eller blågrått
        return 'svart/antrasitt' if v < 0.3 else 'mørk' if v < 0.42 else 'grå' if v < 0.66 else 'lys grå'
    if h < 0.11 or h > 0.95:                              # rødt, oransje, brunt
        if s < 0.24: return 'grå' if v > 0.5 else 'mørk brun'
        if v < 0.5: return 'rødbrun tegl' if s > 0.35 else 'mørk brun'
        return 'oransje tegl' if h > 0.06 and s > 0.4 else 'rød tegl'
    if h < 0.17 and s < 0.3:                              # gulgrått (falmet, betong)
        return 'grå' if v < 0.72 else 'lys grå'
    if 0.38 < h <= 0.5 and s < 0.35:                      # blågrønt: kobber
        return 'grønn (kobber/mose)'
    return None                                           # grønt: trær eller mose, ikke en takfarge


def main(tørt=False):
    ret = [r for r in datalag.les('rettelser') if r.get('grunn') != GRUNN]
    raa = datalag.alle(raa=True); grunn = [dict(x) for x in raa['bygg']]
    # tilstanden uten vegg_nye.py sine linjer (de kommer etter i kjeden og skriver om farge_kilde)
    uten = [r for r in ret if not r.get('grunn', '').startswith('veggfarge til nye hus')]
    d = datalag.hoyden_styrer(datalag.legg_paa_rettelser(raa, uten), grunn)
    nye, logg = [], []
    for x in d['bygg']:
        if x.get('skjul') or not (x.get('farge_kilde') or '').startswith('standard'):
            continue
        P = Polygon(x['p']); I = P.buffer(-0.6)
        if I.is_empty or I.area < 2:
            logg.append(f"{x['id']}: for lite til å måle"); continue
        x0, y0, x1, y1 = P.bounds
        im, px = FL.ortofoto(x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.125)
        m = np.zeros(im.shape[:2], np.uint8)
        for g in getattr(I, 'geoms', [I]):
            cv2.fillPoly(m, [np.array([px(*q) for q in g.exterior.coords], np.int32)], 1)
        v = im[m > 0][:, ::-1].astype(float)     # BGR -> RGB
        if len(v) < 30:
            logg.append(f"{x['id']}: for få piksler"); continue
        med = np.median(v, axis=0); spr = float(np.median(np.abs(v - med).sum(axis=1)))
        hsv = colorsys.rgb_to_hsv(*(med / 255))
        gronn = med[1] > med[0] + 8 and med[1] > med[2]
        if spr > 90 or gronn:
            logg.append(f"{x['id']}: hoppet over (spredning {spr:.0f}{', grønt: trær over taket' if gronn else ''})"); continue
        navn = klasse(med)
        if navn is None:
            logg.append(f"{x['id']}: hoppet over (foto {med.astype(int).tolist()} er grønt: trær over taket)"); continue
        logg.append(f"{x['id']}: foto {med.astype(int).tolist()} spredning {spr:.0f} -> {navn}")
        for felt, verdi in (('tak', list(PALETT[navn])), ('taks', None), ('farge_kilde', f"tak: ortofoto 2024 ({navn}); vegg: standard, ikke sett")):
            nye.append({"emne": "bygg", "id": x['id'], "op": "sett", "felt": felt, "verdi": verdi, "hvem": "Claude", "dato": "2026-10-29", "grunn": GRUNN})
    for l in logg: print(l)
    if not tørt: datalag.skriv_rettelser(ret + nye)
    print(f"{len(nye) // 3} tak fikk farge fra ortofotoet, {len(logg) - len(nye) // 3} hoppet over")


if __name__ == '__main__':
    main('--tørt' in sys.argv)
