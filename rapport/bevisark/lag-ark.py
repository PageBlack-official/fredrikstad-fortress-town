"""Bevisark: setter sammen tegning + modell forfra + modell bakfra til ett PNG per tegning.
Bruk: python3 -I lag-ark.py <views.json> <tegningsmappe> <modellmappe> <utmappe> <bygg.json>
Skriver også statistikk.json til utmappen (for bevisark.md).
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

views_f, tegn_dir, mod_dir, ut_dir, bygg_f = sys.argv[1:6]
views = json.load(open(views_f))
bygg = json.load(open(bygg_f))
os.makedirs(ut_dir, exist_ok=True)
DATO = "23.10.2026"

def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

F_T, F_S = font(30), font(20)
COL_W, COL_H, GAP, TOP = 1000, 700, 20, 120

def fit(im, w, h, bg=(255, 255, 255)):
    im = im.convert("RGB")
    s = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    c = Image.new("RGB", (w, h), bg)
    c.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return c

stat = {}
for v in views:
    n = v["n"]
    bl = v["bygg"]
    teg = Image.open(os.path.join(tegn_dir, n + ".png"))
    fp = os.path.join(mod_dir, n + "-forfra.png")
    bp = os.path.join(mod_dir, n + "-bakfra.png")
    mangler = []
    paneler = [fit(teg, COL_W, COL_H)]
    for p, lab in ((fp, "forfra"), (bp, "bakfra")):
        if os.path.exists(p):
            paneler.append(fit(Image.open(p), COL_W, COL_H))
        else:
            mangler.append(lab)
            c = Image.new("RGB", (COL_W, COL_H), (235, 235, 235))
            ImageDraw.Draw(c).text((40, 40), "modellbilde mangler (" + lab + ")", fill=(80, 80, 80), font=F_S)
            paneler.append(c)
    W = 3 * COL_W + 4 * GAP
    H = TOP + COL_H + GAP + 40
    ark = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(ark)
    d.text((GAP, 15), f"Bevisark {n}", fill=(0, 0, 0), font=F_T)
    idx = ", ".join(str(i) for i in bl)
    d.text((GAP, 58), f"Bygg koblet ({len(bl)}): {idx}", fill=(40, 40, 40), font=F_S)
    d.text((GAP, 86), f"Dato {DATO}  ·  kamera senter ({v['cx']}, {v['cy']}) zoom {v['zoom']}  ·  venstre: strektegning  ·  midten: modell forfra (az 40)  ·  høyre: modell bakfra (az 220)", fill=(90, 90, 90), font=F_S)
    for i, p in enumerate(paneler):
        ark.paste(p, (GAP + i * (COL_W + GAP), TOP))
    for i, lab in enumerate(["Tegning", "Modell forfra (az 40)", "Modell bakfra (az 220)"]):
        d.text((GAP + i * (COL_W + GAP), TOP + COL_H + 8), lab, fill=(0, 0, 0), font=F_S)
    ark.save(os.path.join(ut_dir, n + ".png"), optimize=True)

    s = dict(navn=n, antall=len(bl), kvartaltegning=0, tegnet_h=0, vind=0, piper=0, arker=0, mangler_bilde=mangler)
    for i in bl:
        b = bygg[i]
        s["kvartaltegning"] += b.get("fasade_kilde") == "kvartaltegning"
        s["tegnet_h"] += b.get("tegnet_h") is not None
        s["vind"] += len(b.get("vind") or [])
        s["piper"] += len(b.get("piper") or [])
        s["arker"] += len(b.get("arker") or [])
    stat[n] = s
    print("ark", n, s)
json.dump(stat, open(os.path.join(ut_dir, "statistikk.json"), "w"), ensure_ascii=False, indent=1)
