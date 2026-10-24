"""Koordinater for benker/gjerder: modell (m) <-> 2019-trykk (px) <-> flyfoto (px) <-> lat/lon.

modell -> 2019:  _farger2019.felles2019.Modell2Trykk (affin2 + lokal korreksjon) -> px2019()
  Gjelder punkter PÅ BAKKEN (gjerder, benker). Husene er tegnet på mønehøyde og ligger forskjøvet.
modell -> flyfoto: kilder/flyfoto-google-2026-10-23.json
lat/lon -> modell: Web Mercator rundt origo skalert med cos(lat0) (samme som rapport/poi/hent.py og src/00_oppsett.js)
"""
import json, math, os, sys
import numpy as np
from pathlib import Path

HER = Path(__file__).resolve().parent
SOC = HER.parent.parent
ROT = SOC.parent
sys.path.insert(0, str(SOC / 'rapport' / '_farger2019'))
import felles2019 as F  # noqa: E402

LON0, LAT0 = 10.952745, 59.202835
R = 6378137.0


def merc(lon, lat):
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


MX0, MY0 = merc(LON0, LAT0)
S = math.cos(math.radians(LAT0))


def ll2xy(lon, lat):
    mx, my = merc(lon, lat)
    return ((mx - MX0) * S, (my - MY0) * S)


_M2T = None


def m2t():
    global _M2T
    if _M2T is None:
        _M2T = F.Modell2Trykk(F.last_bygg())
    return _M2T


def til2019(xy):
    xy = np.atleast_2d(np.asarray(xy, float))
    p300 = m2t().px(xy)
    p300 = np.atleast_2d(p300)
    return F.px2019(p300)


def fra2019(px):
    """2019-px -> modell (m), invers ved fastpunktiterasjon (korreksjonen er glatt)."""
    px = np.atleast_2d(np.asarray(px, float))
    A = F.REG[:, :2]; t = F.REG[:, 2]
    p300 = (px - t) @ np.linalg.inv(A).T
    M = m2t().M  # [x,y,1]@M = p300
    Ml = M[:2, :]; c = M[2, :]
    Minv = np.linalg.inv(Ml)
    ut = []
    for q in p300:
        xy = (q - c) @ Minv
        for _ in range(20):
            off = m2t().korr(m2t().affin(xy)) - m2t().affin(xy)
            xy = (q - off - c) @ Minv
        ut.append(xy)
    return np.array(ut)


FLY = json.load(open(SOC / 'kilder' / 'flyfoto-google-2026-10-23.json'))


def tilfly(xy):
    a = FLY['anker']
    xy = np.atleast_2d(np.asarray(xy, float))
    d = (xy - np.array(a['modell_xy'])) / a['m_per_px_oversikt'] * np.array([1, -1])
    return a['forstorrelse'] * (np.array(a['px']) + d) + a['forskyvning']


def frafly(px):
    a = FLY['anker']
    px = np.atleast_2d(np.asarray(px, float))
    d = (px - a['forskyvning']) / a['forstorrelse'] - np.array(a['px'])
    return d * np.array([1, -1]) * a['m_per_px_oversikt'] + np.array(a['modell_xy'])
