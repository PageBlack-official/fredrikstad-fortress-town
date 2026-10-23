import cv2, numpy as np, json, math, sys
ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/soc'
UT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/trearbeid'
im = cv2.imread(ROT + '/kilder/flyfoto-google-2026-10-23.jpg')
k = json.load(open(ROT + '/kilder/flyfoto-google-2026-10-23.json')); a = k['anker']; ax, ay = a['px']; kx, ky = a['modell_xy']; mpp = a['m_per_px_oversikt']; F = a['forstorrelse']; O = a['forskyvning']
MPP = mpp / F
def px(x, y): return (F * (ax + (x - kx) / mpp) + O, F * (ay - (y - ky) / mpp) + O)
ut = json.load(open(UT + '/kroner_raa.json'))
gamle = json.load(open(ROT + '/data/traer.json'))
# beskjær til gyldig bilde
V = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 2]
ys, xs = np.nonzero(V > 12); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
crop = im[y0:y1, x0:x1].copy()
for p in gamle:
    u, v = px(p[0], p[1]); u, v = int(u - x0), int(v - y0)
    if 0 <= u < crop.shape[1] and 0 <= v < crop.shape[0]: cv2.circle(crop, (u, v), 2, (0, 0, 255), -1)
for t in ut:
    u, v = t['px']; u, v = int(u - x0), int(v - y0); rr = max(2, int(t['D'] / 2 / MPP))
    col = (60, 220, 60) if t['sik'] >= 0.7 else (0, 220, 255)
    cv2.circle(crop, (u, v), rr, col, 2)
sc = min(1.0, 2000 / max(crop.shape[:2]))
crop = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
cv2.putText(crop, 'gronn = hoy sikkerhet, gul = lav; rode prikker = dagens traer.json', (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
out = sys.argv[1] if len(sys.argv) > 1 else UT + '/kontrollark.png'
cv2.imwrite(out, crop)
# utsnitt i full oppløsning
for navn, (mx, my) in {'ost': (250, -100), 'sentrum': (-60, 60), 'nord': (60, 200), 'sor': (-100, -250)}.items():
    u, v = px(mx, my); u, v = int(u), int(v); cy0, cx0 = v - 400, u - 500
    c = im[cy0:cy0 + 800, cx0:cx0 + 1000].copy()
    for p in gamle:
        uu, vv = px(p[0], p[1]); uu, vv = int(uu - cx0), int(vv - cy0)
        if 0 <= uu < 1000 and 0 <= vv < 800: cv2.circle(c, (uu, vv), 3, (0, 0, 255), -1)
    for t in ut:
        uu, vv = t['px']; uu, vv = int(uu - cx0), int(vv - cy0); rr = max(2, int(t['D'] / 2 / MPP))
        if 0 <= uu < 1000 and 0 <= vv < 800:
            col = (60, 220, 60) if t['sik'] >= 0.7 else (0, 220, 255)
            cv2.circle(c, (uu, vv), rr, col, 2); cv2.putText(c, str(int(t['H'])), (uu - 6, vv + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.imwrite(UT + f'/ark_{navn}.jpg', c, [cv2.IMWRITE_JPEG_QUALITY, 80])
