import cv2, numpy as np
from quadfit import quad_from_mask
img = cv2.imread('g_0014x_00.png').astype(float)
x0, y0, x1, y1 = 610, 370, 700, 450
roi = img[y0:y1, x0:x1]
B, G, R = roi[..., 0], roi[..., 1], roi[..., 2]
res = {}
for th in [-10, 0, 10]:
    soft = np.clip(((B - R) - th) / 20 + 0.5, 0, 1) * (B > 140)
    mask = soft
    q = quad_from_mask(mask, x0, y0)
    res[th] = q
    print('th', th, np.round(q, 2).tolist())
np.save('book14_quad.npy', res[0])
