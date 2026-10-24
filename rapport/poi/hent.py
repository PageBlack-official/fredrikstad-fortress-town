#!/usr/bin/env python3
"""Henter POI-data for Gamlebyen-kartet og skriver steder.json + kontrollark.png.
Kjør: python3 hent.py   (fra hvilken som helst katalog). Kilder: Fredrikstad kommune ArcGIS, Entur, OSM Overpass.
Modellkoordinater: Web Mercator rundt origo, delt på 1/cos(lat0) slik at 1 enhet = 1 meter på bakken ved lat0:
  mx = R*lon_rad ; my = R*ln(tan(pi/4 + lat_rad/2))
  x = (mx-mx0)*cos(lat0) ; y = (my-my0)*cos(lat0)   (x øst, y nord)
"""
import json, math, os, sys, time, datetime, urllib.request, urllib.parse
from pathlib import Path
HERE = Path(__file__).resolve().parent
SOC = HERE.parent.parent
LON0, LAT0 = 10.952745, 59.202835
R = 6378137.0
BOX = dict(s=59.198, n=59.210, w=10.940, e=10.965)
HENTET = datetime.date.today().isoformat()
FEIL = []

def merc(lon, lat):
    return R*math.radians(lon), R*math.log(math.tan(math.pi/4+math.radians(lat)/2))
MX0, MY0 = merc(LON0, LAT0)
S = math.cos(math.radians(LAT0))
def xy(lon, lat):
    mx, my = merc(lon, lat)
    return round((mx-MX0)*S, 2), round((my-MY0)*S, 2)
def dist(lon, lat):
    x, y = xy(lon, lat); return math.hypot(x, y)

def http(url, data=None, headers=None, timeout=60):
    h = {"User-Agent": "pageblack-smartoldtown"}; h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

steder = []
def add(id, type, navn, lon, lat, kilde, kilde_url, lisens, felt):
    x, y = xy(lon, lat)
    steder.append(dict(id=id, type=type, navn=navn, lon=round(lon, 6), lat=round(lat, 6), x=x, y=y,
                       kilde=kilde, kilde_url=kilde_url, hentet=HENTET, lisens=lisens, felt=felt))

# ---------- Parkering (kommunen) ----------
ARC = "https://arcgis.fredrikstad.kommune.no/server/rest/services/TekniskDrift/Parkering/MapServer"
ARC_LIS = "Ikke oppgitt i tjenesten (data.norge.no: «ingen vilkår»); bekreft med kart@fredrikstad.kommune.no"
def parkering():
    # sirkel 500 m utenfor Gamlebyen-boksen er dekket av en rektangel med 500 m margin
    dlat = 500/111320; dlon = 500/(111320*math.cos(math.radians(LAT0)))
    env = f"{BOX['w']-dlon},{BOX['s']-dlat},{BOX['e']+dlon},{BOX['n']+dlat}"
    for lag, kind in ((1, "plass"), (0, "automat")):
        q = dict(where="1=1", geometry=env, geometryType="esriGeometryEnvelope", inSR=4326, outSR=4326,
                 spatialRel="esriSpatialRelIntersects", outFields="*", f="geojson", returnGeometry="true")
        url = f"{ARC}/{lag}/query?" + urllib.parse.urlencode(q)
        try:
            d = http(url)
        except Exception as e:
            FEIL.append(f"parkering lag {lag}: {e}"); continue
        for f in d.get("features", []):
            g = f.get("geometry") or {}
            p = f["properties"]
            if g.get("type") == "Point": lon, lat = g["coordinates"][:2]
            elif g.get("type") in ("Polygon", "MultiPolygon", "LineString"):
                c = g["coordinates"]
                while isinstance(c[0][0], list): c = [pt for ring in c for pt in ring] if isinstance(c[0][0][0], (int, float)) is False else c[0]
                lon = sum(pt[0] for pt in c)/len(c); lat = sum(pt[1] for pt in c)/len(c)
            else: continue
            felt = {k: p.get(k) for k in ("ANTALL", "PRIS", "ELBIL", "KOMMENTAR", "EASYPARK", "TYPE", "AUTOMATNR", "LENKE") if p.get(k) not in (None, "")}
            felt["lag"] = f"{kind} (lag {lag})"
            navn = p.get("NAVN") or (f"Automat {p.get('AUTOMATNR')}" if kind == "automat" else "Parkering")
            add(f"parkering-{lag}-{p['OBJECTID']}", "parkering", navn, lon, lat, f"Fredrikstad kommune ArcGIS TekniskDrift/Parkering lag {lag}",
                f"{ARC}/{lag}", ARC_LIS, felt)

# ---------- Entur ----------
ENT = "https://api.entur.io/journey-planner/v3/graphql"
ENT_H = {"ET-Client-Name": "pageblack-smartoldtown", "Content-Type": "application/json"}
def gql(q):
    return http(ENT, json.dumps({"query": q}).encode(), ENT_H)
SP = """id name latitude longitude transportMode transportSubmode
 quays { id name publicCode latitude longitude lines { id publicCode name transportMode authority { id name } } }"""
def entur():
    try:
        near = gql('{nearest(latitude:%f,longitude:%f,maximumDistance:700,filterByPlaceTypes:[stopPlace],maximumResults:40){edges{node{distance place{... on StopPlace{%s}}}}}}' % (LAT0, LON0, SP))
        sps = {e["node"]["place"]["id"]: e["node"]["place"] for e in near["data"]["nearest"]["edges"] if e["node"]["place"]}
        for need in ("NSR:StopPlace:2448", "NSR:StopPlace:63038"):
            if need not in sps:
                r = gql('{stopPlace(id:"%s"){%s}}' % (need, SP)); sps[need] = r["data"]["stopPlace"]
    except Exception as e:
        FEIL.append(f"Entur: {e}"); return
    for sid, sp in sps.items():
        if not sp: continue
        lines_all = {}
        for q in sp["quays"]:
            for l in q["lines"]: lines_all[l["id"]] = l
        er_ferje = sid == "NSR:StopPlace:2448" or sp.get("transportMode") in (["water"], "water") or any(str(l["publicCode"]) in ("803", "805") for l in lines_all.values())
        typ = "ferje" if er_ferje else "buss"
        if typ == "buss" and dist(sp["longitude"], sp["latitude"]) > 600 and sid != "NSR:StopPlace:63038": continue
        add(sid.replace("NSR:StopPlace:", "entur-sp-"), typ, sp["name"], sp["longitude"], sp["latitude"], "Entur Journey Planner v3 / NSR",
            "https://developer.entur.org/pages-journeyplanner-journeyplanner", "NLOD",
            dict(stopplace=sid, linjer=sorted({f"{l['publicCode']} {l['name']}" for l in lines_all.values()}),
                 mode_oppgitt=sp.get("transportMode")))
        for q in sp["quays"]:
            if q["latitude"] is None: continue
            add(q["id"].replace("NSR:Quay:", "entur-quay-"), typ, f"{sp['name']} {q.get('publicCode') or ''}".strip(), q["longitude"], q["latitude"],
                "Entur Journey Planner v3 / NSR", "https://developer.entur.org/pages-journeyplanner-journeyplanner", "NLOD",
                dict(quay=q["id"], stopplace=sid, plattform=q.get("publicCode"),
                     linjer=sorted({f"{l['publicCode']} {l['name']}" for l in q["lines"]}),
                     autoritet=sorted({(l.get("authority") or {}).get("name", "") for l in q["lines"]}),
                     merknad=("mode rapporteres som BUS av Entur; ferje avgjort på stoppested/linje 803/805" if typ == "ferje" else None)))

# ---------- OSM ----------
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass.private.coffee/api/interpreter"]
QL = '[out:json][timeout:60];(nwr["amenity"~"^(restaurant|cafe|pub|toilets)$"](%(s)s,%(w)s,%(n)s,%(e)s);nwr["tourism"~"^(hotel|guest_house|museum)$"](%(s)s,%(w)s,%(n)s,%(e)s););out center tags;' % BOX
def osm():
    d = None
    for rund in range(3):
        for u in OVERPASS:
            try:
                r = http(u, urllib.parse.urlencode({"data": QL}).encode(), timeout=90)
                if "elements" in r: d = r; break
            except Exception as e:
                FEIL.append(f"Overpass {u}: {str(e)[:80]}")
        if d: break
        time.sleep(10)
    if not d:
        FEIL.append("OSM: ingen Overpass-speil svarte; restaurant/overnatting/museum/toalett uten OSM"); return
    for el in d["elements"]:
        t = el.get("tags", {})
        lon = el.get("lon") or el.get("center", {}).get("lon"); lat = el.get("lat") or el.get("center", {}).get("lat")
        if lon is None: continue
        a, tu = t.get("amenity"), t.get("tourism")
        typ = "restaurant" if a in ("restaurant", "cafe", "pub") else "overnatting" if tu in ("hotel", "guest_house") else "museum" if tu == "museum" else "toalett" if a == "toilets" else "annet"
        felt = {k: t[k] for k in ("amenity", "tourism", "cuisine", "opening_hours", "website", "phone", "fee", "wheelchair", "operator", "addr:street", "addr:housenumber") if k in t}
        add(f"osm-{el['type'][0]}{el['id']}", typ, t.get("name") or f"({typ} uten navn)", lon, lat, "OpenStreetMap via Overpass",
            f"https://www.openstreetmap.org/{el['type']}/{el['id']}", "ODbL 1.0 © OpenStreetMap-bidragsytere", felt)

# ---------- Kontrollark ----------
FARGE = dict(parkering="#ffd400", ferje="#00e5ff", buss="#ff3b30", restaurant="#ff8a00", overnatting="#b46bff",
             museum="#ff4fd8", toalett="#35ff6e", annet="#ffffff")
def ark():
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(SOC/"kilder"/"flyfoto-google-2026-10-23.jpg").convert("RGB")
    t = json.load(open(SOC/"kilder"/"flyfoto-google-2026-10-23.json"))
    a = t["anker"]; mpp = a["m_per_px_oversikt"]; f = a["forstorrelse"]; off = a["forskyvning"]
    def px(x, y):
        return (f*(a["px"][0] + (x-a["modell_xy"][0])/mpp) + off, f*(a["px"][1] - (y-a["modell_xy"][1])/mpp) + off)
    d = ImageDraw.Draw(im)
    try: fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    except Exception: fnt = ImageFont.load_default()
    n = 0
    for s in steder:
        p = px(s["x"], s["y"])
        if not (1650 <= p[0] < 3500 and 430 <= p[1] < 1980): continue
        c = FARGE[s["type"]]; r = 7
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=c, outline="black", width=2)
        lab = s["id"].replace("parkering-", "P").replace("entur-quay-", "q").replace("entur-sp-", "sp").replace("osm-", "")
        d.text((p[0]+r+2, p[1]-8), lab, fill="white", font=fnt, stroke_width=2, stroke_fill="black"); n += 1
    im = im.crop((1650, 430, 3500, 1980)); d = ImageDraw.Draw(im)  # bare flyfotoet (resten av lerretet er svart)
    y0 = 10
    for k, c in FARGE.items():
        d.rectangle([10, y0, 330, y0+24], fill="black"); d.ellipse([14, y0+4, 30, y0+20], fill=c)
        d.text((38, y0+3), f"{k} ({sum(1 for s in steder if s['type']==k)})", fill="white", font=fnt); y0 += 26
    im.save(HERE/"kontrollark.png"); return n

if __name__ == "__main__":
    parkering(); entur(); osm()
    json.dump(steder, open(HERE/"steder.json", "w"), ensure_ascii=False, indent=1)
    tall = {}
    for s in steder: tall[s["type"]] = tall.get(s["type"], 0)+1
    print(tall); print("FEIL:", FEIL)
    json.dump(dict(tall=tall, feil=FEIL), open(HERE/"hent.logg.json", "w"), ensure_ascii=False, indent=1)
    try: print("på arket:", ark())
    except Exception as e: print("ark feilet", e)
