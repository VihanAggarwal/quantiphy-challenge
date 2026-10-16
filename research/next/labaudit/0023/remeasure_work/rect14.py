import numpy as np, cv2
lL, lR, lB, lF = np.load('t14_lines.npy')
BL, BR, FR, FL = np.load('t14_corners.npy')
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
v1 = inter(lL, lR); v2 = inter(lB, lF)
print('VP side', v1, 'VP front/back', v2)
for (cx, cy) in [(640, 360), (630, 350), (650, 370)]:
    p = np.array([cx, cy])
    f2 = -(v1 - p) @ (v2 - p)
    print('pp', cx, cy, 'f_est', np.sqrt(f2) if f2 > 0 else f2)
def rectify(f, cx, cy, corners):
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.]])
    Ki = np.linalg.inv(K)
    d1 = Ki @ np.r_[v1, 1]; d1 /= np.linalg.norm(d1)
    d2 = Ki @ np.r_[v2, 1]; d2 /= np.linalg.norm(d2)
    n = np.cross(d1, d2); n /= np.linalg.norm(n)
    # plane n.X = 1 (arbitrary scale); intersect rays
    P = []
    for c in corners:
        r = Ki @ np.r_[c, 1]
        P.append(r / (n @ r))
    return np.array(P), n, np.degrees(np.arccos(abs(d1 @ d2)))
for f in [690, 711, 730]:
    P, n, ang = rectify(f, 640, 360, [BL, BR, FR, FL])
    sides = [np.linalg.norm(P[i] - P[(i + 1) % 4]) for i in range(4)]
    print('f', f, 'angle between VP dirs %.1f' % ang, 'back %.4f right %.4f front %.4f left %.4f' % tuple(sides),
          'ratio side/front %.3f' % ((sides[1] + sides[3]) / (sides[0] + sides[2])))
