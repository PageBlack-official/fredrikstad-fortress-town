"""Registrerer 2019-JPG-en mot 2015-rasteret (ORB + RANSAC, similaritet). Lagrer 2015px -> 2019px (2x3)."""
import cv2, numpy as np, os
ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad'
a = cv2.imread(os.path.join(ROT, 'kilder2019/brosjyre2019-3.jpg'), cv2.IMREAD_GRAYSCALE)
b = cv2.imread(os.path.join(ROT, 'pdf/side300-1.png'), cv2.IMREAD_GRAYSCALE)
orb = cv2.ORB_create(12000)
ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(b, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
m = sorted(bf.match(db, da), key=lambda x: x.distance)[:5000]
pb = np.float32([kb[x.queryIdx].pt for x in m]); pa = np.float32([ka[x.trainIdx].pt for x in m])
M, inl = cv2.estimateAffinePartial2D(pb, pa, method=cv2.RANSAC, ransacReprojThreshold=1.5)
res = (np.c_[pb, np.ones(len(pb))] @ M.T) - pa
r = np.hypot(res[:, 0], res[:, 1])[inl.ravel() > 0]
s = np.hypot(M[0, 0], M[1, 0]); rot = np.degrees(np.arctan2(M[1, 0], M[0, 0]))
print('2015px -> 2019px:', M.tolist(), 'skala %.5f rot %.4f° inliers %d/%d residual median %.2f p90 %.2f px' % (s, rot, inl.sum(), len(m), np.median(r), np.percentile(r, 90)))
np.save(os.path.join(ROT, 'soc/rapport/_farger2019/reg2015til2019.npy'), M)
