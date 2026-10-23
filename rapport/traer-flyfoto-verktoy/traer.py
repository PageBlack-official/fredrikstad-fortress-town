"""Treregister fra flyfoto: segmenter kroner, mål diameter og skygge, filtrer mot hus/vann/vei, skriv rapportfiler."""
import cv2, numpy as np, json, math, base64, os, sys
from collections import Counter
ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/soc'
UT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/trearbeid'
RAP = ROT + '/rapport'
im = cv2.imread(ROT + '/kilder/flyfoto-google-2026-10-23.jpg'); Hh, Ww = im.shape[:2]
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); H, S, V = [hsv[..., i].astype(np.float32) for i in range(3)]
b, g, r = [im[..., i].astype(np.float32) for i in range(3)]
k = json.load(open(ROT + '/kilder/flyfoto-google-2026-10-23.json')); a = k['anker']; ax, ay = a['px']; kx, ky = a['modell_xy']; mpp = a['m_per_px_oversikt']; F = a['forstorrelse']; O = a['forskyvning']
MPP = mpp / F  # meter per piksel (0,39)
def px(x, y): return (F * (ax + (x - kx) / mpp) + O, F * (ay - (y - ky) / mpp) + O)
def inv(u, v): return (kx + ((u - O) / F - ax) * mpp, ky - ((v - O) / F - ay) * mpp)
sol = json.load(open(UT + '/sol.json')); ux, uy = sol['ux'], sol['uy']; ELEV = math.atan(1 / sol['L_per_h'])

# ---- 1. masker ----
valid = (V > 12).astype(np.uint8)
valid_er = cv2.erode(valid, np.ones((9, 9), np.uint8))
exg = 2 * g - r - b
veg = ((H > 30) & (H < 95) & (S > 45) & (exg > 10) & (valid > 0)).astype(np.uint8)
mu = cv2.blur(V, (7, 7)); mu2 = cv2.blur(V * V, (7, 7)); std = np.sqrt(np.maximum(mu2 - mu * mu, 0))
stds = cv2.GaussianBlur(std, (0, 0), 2.5)
Vs = cv2.GaussianBlur(V, (0, 0), 3)
ker = lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))
veg_er = cv2.erode(veg, ker(7))
tre = ((stds > 11) & (veg_er > 0) & (Vs < 125)).astype(np.uint8)
tre = cv2.morphologyEx(tre, cv2.MORPH_OPEN, ker(5))
tre = cv2.dilate(tre, ker(5)) & veg
tre = cv2.morphologyEx(tre, cv2.MORPH_CLOSE, ker(5))
n, lab, st, cen = cv2.connectedComponentsWithStats(tre)
tre[np.isin(lab, np.where(st[:, cv2.CC_STAT_AREA] < 40)[0])] = 0

# ---- utelukkelser: hus, vann, kjørevei ----
bygg = json.load(open(ROT + '/data/bygg.json')); vann = json.load(open(ROT + '/data/vann.json')); land = json.load(open(ROT + '/data/landskap.json'))
hus = np.zeros((Hh, Ww), np.uint8)
for x in bygg:
    if x.get('skjul'): continue
    P = np.array([px(*q) for q in x['p']], np.int32); cv2.fillPoly(hus, [P], 1)
hus = cv2.dilate(hus, ker(5))  # ca 1 m utenfor veggen
sjo = np.zeros((Hh, Ww), np.uint8)
for x in vann:
    P = np.array([px(*q) for q in x['p']], np.int32); cv2.fillPoly(sjo, [P], 1)
vei = np.zeros((Hh, Ww), np.uint8)
for v_ in land['veier']:
    if v_.get('k') != 'kjore': continue
    P = np.array([px(q[0], q[1]) for q in v_['p']], np.int32).reshape(-1, 1, 2)
    cv2.polylines(vei, [P], False, 1, max(2, int(round(v_['w'] / MPP * 0.8))))
# terreng (voller)
TER = land['terreng']; MB = np.frombuffer(base64.b64decode(TER['m']), np.uint8); HK = np.frombuffer(base64.b64decode(TER['h']), np.uint8)
nx, ny, G = TER['nx'], TER['ny'], TER['g']; off = TER.get('off', 0)
bits = np.unpackbits(MB)[:nx * ny]
TH = np.full(nx * ny, round(off * 20), np.float32); TH[bits == 1] = HK[:int(bits.sum())]
TH = TH.reshape(ny, nx) / 20 - off
def hAt(x, y):
    fx, fy = (x - TER['x0']) / G, (y - TER['y0']) / G; i, j = int(math.floor(fx)), int(math.floor(fy))
    if i < 0 or j < 0 or i >= nx - 1 or j >= ny - 1: return 0.0
    tx, ty = fx - i, fy - j
    return float((TH[j, i] * (1 - tx) + TH[j, i + 1] * tx) * (1 - ty) + (TH[j + 1, i] * (1 - tx) + TH[j + 1, i + 1] * tx) * ty)

# ---- 2. enkeltkroner: topper i avstandstransformen, Voronoi-celler rundt toppene, k-means for store rester ----
dist = cv2.distanceTransform(tre, cv2.DIST_L2, 5)
dsm = cv2.GaussianBlur(dist, (0, 0), 1.5)
MIN_AVST = int(round(3.5 / MPP))  # ca 3,5 m mellom kronesentre
dil = cv2.dilate(dsm, ker(MIN_AVST * 2 + 1))
peaks = ((dsm >= dil - 1e-3) & (dsm > 0.8 / MPP) & (tre > 0)).astype(np.uint8)
npk, pklab = cv2.connectedComponents(peaks)
_, vlab = cv2.distanceTransformWithLabels(1 - peaks, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
# pikseletikett -> toppkomponent
pix_to_comp = np.zeros(vlab.max() + 1, np.int32)
pys, pxs = np.nonzero(peaks); pix_to_comp[vlab[pys, pxs]] = pklab[pys, pxs]
cell = pix_to_comp[vlab]; cell[tre == 0] = 0
# trepiksler lenger enn 7 m fra en topp: egne felt
dtp = cv2.distanceTransform(1 - peaks, cv2.DIST_L2, 5)
rest = ((tre > 0) & (dtp > 7.0 / MPP)).astype(np.uint8)
cell[rest > 0] = 0
regs = {}
ys, xs = np.nonzero(cell > 0)
for lbl, y, x in zip(cell[ys, xs], ys, xs): regs.setdefault(int(lbl), []).append((x, y))
nr, rlab = cv2.connectedComponents(rest)
ys, xs = np.nonzero(rlab > 0)
for lbl, y, x in zip(rlab[ys, xs], ys, xs): regs.setdefault(-int(lbl), []).append((x, y))
A_TYP = math.pi * (3.8 ** 2) / MPP ** 2  # typisk krone 7,6 m i diameter, i piksler
kroner = []  # (px-liste, delt)
for lbl, pts in regs.items():
    P = np.array(pts, np.float32)
    D = 2 * math.sqrt(len(P) / math.pi) * MPP
    if D > 11.0:
        kk = max(2, int(round(len(P) / A_TYP)))
        _, labs, cents = cv2.kmeans(P, kk, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5), 3, cv2.KMEANS_PP_CENTERS)
        for i in range(kk): kroner.append((P[labs.ravel() == i], True))
    else: kroner.append((P, False))
print('topper', npk - 1, 'celler', len(regs), 'kroner', len(kroner), 'dekket px', sum(len(p) for p, _ in kroner), 'av', int(tre.sum()))

# ---- vann fra fotoet (OSM-vannpolygonene dekker også bankene, se rapport) ----
foto_vann = ((H > 85) & (H < 135) & (S > 40) & (V < 150) & (stds < 8) & (valid > 0)).astype(np.uint8)
foto_vann = cv2.morphologyEx(foto_vann, cv2.MORPH_OPEN, ker(7))
def flytt_ut(mask, maks_m):
    """For punkter inne i masken: nærmeste piksel utenfor, hvis den er nærmere enn maks_m. Returnerer funksjon (u,v)->(u,v) eller None."""
    d, lab = cv2.distanceTransformWithLabels(mask, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    zy, zx = np.nonzero(mask == 0); tab = np.zeros((lab.max() + 1, 2), np.int32); tab[lab[zy, zx]] = np.stack([zx, zy], 1)
    def f(u, v):
        if mask[v, u] == 0: return (u, v)
        if d[v, u] * MPP > maks_m: return None
        nu, nv = tab[lab[v, u]]; du, dv = nu - u, nv - v; n = math.hypot(du, dv) + 1e-6
        return (int(round(nu + du / n * 1.0 / MPP)), int(round(nv + dv / n * 1.0 / MPP)))  # 1 m videre ut
    return f
ut_hus = flytt_ut(hus, 2.5); ut_vei = flytt_ut(vei, 3.0); ut_vann = flytt_ut(cv2.dilate(foto_vann, ker(5)), 3.0)

# ---- 3. per krone ----
def skygge_hoyde(cx, cy, rpx):
    """Følg skyggeretningen fra kronekanten; lengde på mørk bakke. Returnerer H eller None."""
    V_mork = 95
    d = rpx; steg = 0.7
    while d < rpx + 35 / MPP:
        u, v = int(round(cx + ux * d)), int(round(cy + uy * d))
        if u < 0 or v < 0 or u >= Ww or v >= Hh or valid[v, u] == 0: return None
        if tre[v, u] or hus[v, u] or foto_vann[v, u]: return None  # skyggen lander på annen krone/hus/vann
        if V[v, u] > V_mork: break
        d += steg
    Lfar = d * MPP; rm = rpx * MPP
    if Lfar - rm < 1.0: return None  # ingen skygge å se
    hc = (Lfar - rm / math.sin(ELEV)) * math.tan(ELEV)
    return hc + rm
ut = []; bort = Counter()
for P, delt in kroner:
    A = len(P)
    if A < 40: bort['for liten (< 6 m2)'] += 1; continue
    cx, cy = P.mean(0)
    D = 2 * math.sqrt(A / math.pi) * MPP
    rpx = D / 2 / MPP
    u, v = int(cx), int(cy)
    if valid_er[v, u] == 0: bort['i kanten av fotoet'] += 1; continue
    flyttet = False
    for f, navn in ((ut_hus, 'i hus'), (ut_vann, 'i vann'), (ut_vei, 'i kjørevei')):
        p2 = f(u, v)
        if p2 is None: u = None; bort[navn] += 1; break
        if p2 != (u, v): flyttet = True; u, v = p2
    if u is None: continue
    mx, my = inv(u, v)
    hull = cv2.convexHull(P.reshape(-1, 1, 2)); Ah = cv2.contourArea(hull) + 1
    komp = A / Ah
    Vm = float(V[P[:, 1].astype(int), P[:, 0].astype(int)].mean())
    Hs = skygge_hoyde(cx, cy, rpx)
    Hd = 1.2 * D
    if Hs is not None and 0.6 * D <= Hs <= 2.2 * D: Hh_ = 0.5 * Hs + 0.5 * Hd; kilde = 'skygge+diameter'
    else: Hh_ = Hd; kilde = 'diameter'
    Hh_ = max(3.0, Hh_)
    s = (D / 2.3 + Hh_ / 2.4) / 2
    s = min(7.5, max(1.6, s))
    sik = 1.0
    if delt: sik -= 0.3
    if D < 3.5: sik -= 0.3
    if komp < 0.6: sik -= 0.2
    if Vm > 112: sik -= 0.2
    if kilde == 'diameter': sik -= 0.1
    if flyttet: sik -= 0.1
    sik = round(max(0.1, sik), 2)
    ut.append(dict(x=round(float(mx), 1), y=round(float(my), 1), s=round(s, 2), bakke=round(max(0.0, hAt(mx, my)), 2), sik=sik, D=round(D, 1), H=round(Hh_, 1), Hs=(round(Hs, 1) if Hs else None), kilde=kilde, delt=delt, flyttet=flyttet, Vm=round(Vm), komp=round(komp, 2), px=(float(u), float(v))))
print('kroner', len(ut), 'delt', sum(1 for t in ut if t['delt']), 'skygge', sum(1 for t in ut if t['kilde'] != 'diameter'), 'flyttet', sum(1 for t in ut if t['flyttet']))
print('bort', dict(bort))
json.dump(ut, open(UT + '/kroner_raa.json', 'w'))
json.dump(dict(bort), open(UT + '/bort.json', 'w'))
np.save(UT + '/tre_mask.npy', tre)
