import cv2, numpy as np, json, math
ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/soc'
UT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/trearbeid'
im = cv2.imread(ROT + '/kilder/flyfoto-google-2026-10-23.jpg')
Hh, Ww = im.shape[:2]
V = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 2].astype(np.float32)
k = json.load(open(ROT + '/kilder/flyfoto-google-2026-10-23.json')); a = k['anker']; ax, ay = a['px']; kx, ky = a['modell_xy']; mpp = a['m_per_px_oversikt']; F = a['forstorrelse']; O = a['forskyvning']
MPP = mpp / F
def px(x, y): return (F * (ax + (x - kx) / mpp) + O, F * (ay - (y - ky) / mpp) + O)
bygg = json.load(open(ROT + '/data/bygg.json'))
alle = np.zeros((Hh, Ww), np.uint8)
for x in bygg:
    P = np.array([px(*q) for q in x['p']], np.int32); cv2.fillPoly(alle, [P], 1)
fri = (1 - cv2.dilate(alle, np.ones((3, 3), np.uint8))) & (V > 12).astype(np.uint8)
kand = [x for x in bygg if x.get('gml') and x.get('h') and not x.get('skjul')]
R = 70
items = []
for x in kand:
    P = np.array([px(*q) for q in x['p']], np.int32)
    cx, cy = P.mean(0).astype(int)
    if cx - R < 0 or cy - R < 0 or cx + R >= Ww or cy + R >= Hh: continue
    m = np.zeros((2 * R, 2 * R), np.uint8); cv2.fillPoly(m, [P - [cx - R, cy - R]], 1)
    if m.sum() < 300 or m.sum() > 6000: continue
    items.append((x, m, fri[cy - R:cy + R, cx - R:cx + R], V[cy - R:cy + R, cx - R:cx + R]))
print('brukt', len(items))
def skift(m, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]]); return cv2.warpAffine(m, M, (2 * R, 2 * R), flags=cv2.INTER_NEAREST)
def maal(th, d=6):
    dx, dy = d * math.cos(math.radians(th)), d * math.sin(math.radians(th)); vals = []
    for x, m, f, v in items:
        s = skift(m, dx, dy) & f
        if s.sum() > 20: vals.append(v[s > 0].mean())
    return float(np.median(vals))
res = sorted([(th, maal(th)) for th in range(0, 360, 10)], key=lambda t: t[1])
print('mørkeste (bildevinkel, grader fra +x, y ned):', res[:4], 'lyseste', res[-2:])
th = res[0][0]
res2 = sorted([(t, maal(t)) for t in range(th - 15, th + 16, 3)], key=lambda t: t[1]); th = res2[0][0]; print('forfinet', res2[:3])
ux, uy = math.cos(math.radians(th)), math.sin(math.radians(th))
ratios = []
for x, m, f, v in items:
    prof = []
    for d in range(2, 60, 2):
        s = skift(m, d * ux, d * uy) & f
        prof.append(v[s > 0].mean() if s.sum() > 20 else np.nan)
    prof = np.array(prof)
    if np.isnan(prof[:5]).any(): continue
    base = prof[0]; lys = np.nanmax(prof[5:]) if not np.isnan(prof[5:]).all() else None
    if lys is None or lys - base < 25: continue
    terskel = base + 0.5 * (lys - base)
    idx = np.where(prof > terskel)[0]
    if len(idx) == 0: continue
    L = (2 + 2 * idx[0]) * MPP
    ratios.append((L / x['h'], x['h'], L, x.get('navn') or x.get('adr') or ''))
ratios.sort()
print('n', len(ratios))
for r_ in ratios: print('  L/h=%.2f h=%.1f L=%.1f %s' % r_)
med = float(np.median([r_[0] for r_ in ratios])); print('median L/h', med, 'solhøyde', math.degrees(math.atan(1 / med)))
json.dump({'bildevinkel_grader': th, 'ux': ux, 'uy': uy, 'L_per_h': med, 'n': len(ratios)}, open(UT + '/sol.json', 'w'))
