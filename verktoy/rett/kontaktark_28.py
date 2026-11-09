#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontaktark med alle 28 husene (steg 5 i OPPGAVE3).

Stabler bevis-jpgene (Street View | før | etter) fra rapport/ferdig/<id>.jpg i et
rutenett med adresse under hvert hus. Rekkefølgen følger kilder/gate/ferdig-kandidater.json.
Adresser og status leses fra kilder/ferdig.json (feltet adr / status).

NB: arket inneholder Street View og skal ALDRI git add-es. Det skrives til
rapport/ferdig/sot-dom-28.jpg (kopieres til Dropbox for hånd) og skal ikke stages.

    python3 verktoy/rett/kontaktark_28.py [ut.jpg]

Standard ut: rapport/ferdig/sot-dom-28.jpg
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KOLONNER = 4
BOKS_B = 760       # bredde på bildeboksen per hus
BOKS_H = 230       # høyde på bildeboksen per hus (bevisstripa letterboxes inn)
TEKST_H = 54       # høyde på adressebåndet under hvert bilde
MARG = 24          # marg mellom celler og rundt arket
TITTEL_H = 70
HVIT = (255, 255, 255)
SORT = (20, 20, 20)
GRA = (120, 120, 120)
VEGAR = (176, 74, 62)  # markør for trenger_vegar


def finn_font(storrelse):
    for sti in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ):
        if os.path.exists(sti):
            try:
                return ImageFont.truetype(sti, storrelse)
            except Exception:
                pass
    return ImageFont.load_default()


def tekstbredde(tegner, tekst, font):
    try:
        b = tegner.textbbox((0, 0), tekst, font=font)
        return b[2] - b[0]
    except Exception:
        return tegner.textlength(tekst, font=font)


def main():
    ut = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROT, "rapport/ferdig/sot-dom-28.jpg")

    kand = json.load(open(os.path.join(ROT, "kilder/gate/ferdig-kandidater.json")))
    ferdig = json.load(open(os.path.join(ROT, "kilder/ferdig.json")))
    if isinstance(ferdig, dict) and "hus" in ferdig:
        fmap = {h["id"]: h for h in ferdig["hus"]}
    elif isinstance(ferdig, list):
        fmap = {h.get("id"): h for h in ferdig}
    else:
        fmap = ferdig

    rader = (len(kand) + KOLONNER - 1) // KOLONNER
    celle_b = BOKS_B + MARG
    celle_h = BOKS_H + TEKST_H + MARG
    bredde = KOLONNER * celle_b + MARG
    hoyde = TITTEL_H + rader * celle_h + MARG

    ark = Image.new("RGB", (bredde, hoyde), HVIT)
    tegner = ImageDraw.Draw(ark)
    f_tittel = finn_font(34)
    f_adr = finn_font(22)
    f_liten = finn_font(16)

    tegner.text((MARG, MARG), "Smart Old Town – 28 hus (Street View | før | etter)",
                font=f_tittel, fill=SORT)

    for i, k in enumerate(kand):
        _id = k["id"]
        f = fmap.get(_id, {})
        adr = (f.get("adr") or k.get("adr") or "").strip()
        status = f.get("status", "")
        kol = i % KOLONNER
        rad = i // KOLONNER
        x0 = MARG + kol * celle_b
        y0 = TITTEL_H + rad * celle_h

        # bevisstripa, letterboxet inn i boksen
        jpg = os.path.join(ROT, "rapport/ferdig/%s.jpg" % _id)
        if os.path.exists(jpg):
            im = Image.open(jpg).convert("RGB")
            s = min(BOKS_B / im.width, BOKS_H / im.height)
            nb, nh = max(1, int(im.width * s)), max(1, int(im.height * s))
            im = im.resize((nb, nh), Image.LANCZOS)
            px = x0 + (BOKS_B - nb) // 2
            py = y0 + (BOKS_H - nh) // 2
            ark.paste(im, (px, py))
        else:
            tegner.rectangle([x0, y0, x0 + BOKS_B, y0 + BOKS_H], outline=GRA)
            tegner.text((x0 + 8, y0 + 8), "mangler bilde", font=f_adr, fill=GRA)

        # ramme rundt bildeboksen
        tegner.rectangle([x0, y0, x0 + BOKS_B, y0 + BOKS_H], outline=GRA)

        # adresse under
        ty = y0 + BOKS_H + 8
        vis = adr if adr else _id
        # kutt om for bredt
        while tekstbredde(tegner, vis, f_adr) > BOKS_B - 10 and len(vis) > 4:
            vis = vis[:-2]
        tegner.text((x0 + 2, ty), vis, font=f_adr, fill=SORT)
        under = _id
        if status == "trenger_vegar":
            under = "%s  –  til Vegar" % _id
            tegner.text((x0 + 2, ty + 26), under, font=f_liten, fill=VEGAR)
        else:
            tegner.text((x0 + 2, ty + 26), under, font=f_liten, fill=GRA)

    os.makedirs(os.path.dirname(ut), exist_ok=True)
    ark.save(ut, "JPEG", quality=90)
    print("skrev", ut, "(%dx%d, %d hus)" % (bredde, hoyde, len(kand)))


if __name__ == "__main__":
    main()
