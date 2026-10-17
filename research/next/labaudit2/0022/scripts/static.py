"""Table top size, route A: plane orientation from the corner quadrilateral's vanishing points (aspect free),
scale from the stated ball ranges (ball centre 2 cm above the top, surface range = centre range - 0.02).
Route B: PnP plane with 76.0 x 60.3 (circular for size; reported for the scale check only)."""
import sys, json, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0022/scripts')
from common import *
P = json.load(open(f'{B}/plane.json')); T = json.load(open(f'{B}/track.json'))
FL, FR, NR, NL = [np.array(c) for c in P['corners']]
h = lambda p: np.array([p[0], p[1], 1.0])
for f in (705.0, 711.0, 716.0, 722.0):
    K = np.array([[f, 0, CX], [0, f, CY], [0, 0, 1]]); Ki = np.linalg.inv(K)
    v1 = np.cross(np.cross(h(FL), h(FR)), np.cross(h(NL), h(NR)))   # far/near edge direction
    v2 = np.cross(np.cross(h(FL), h(NL)), np.cross(h(FR), h(NR)))   # side edge direction
    d1 = Ki @ v1; d1 /= np.linalg.norm(d1); d2 = Ki @ v2; d2 /= np.linalg.norm(d2)
    n = np.cross(d1, d2); n /= np.linalg.norm(n)
    orth = abs(d1 @ d2)
    def X(p, dist):  # point on the plane n.X = dist
        r = Ki @ h(p); return dist / (n @ r) * r
    corners = [X(c, 1.0) for c in (FL, FR, NR, NL)]
    far = np.linalg.norm(corners[1] - corners[0]); near = np.linalg.norm(corners[2] - corners[3])
    left = np.linalg.norm(corners[3] - corners[0]); right = np.linalg.norm(corners[2] - corners[1])
    for k, R, lab in [(14, 1.751, 't0.6'), (19, 1.687, 't0.8'), (29, 1.526, 't1.2')]:
        r = ray(*T['o'][k][:2], f=f)
        # ball centre at range R+0.02 along the ray; table plane is 2 cm farther along the normal
        Cb = (R + 0.02) * r; dist_ball = n @ Cb; dist_tab = dist_ball + 0.02 * np.sign(dist_ball)
        s = dist_tab
        print(f'f {f:.0f} |d1.d2| {orth:.3f} anchor {lab}: long {0.5*(far+near)*s*100:.1f} (far {far*s*100:.1f} near {near*s*100:.1f}) '
              f'short {0.5*(left+right)*s*100:.1f} (L {left*s*100:.1f} R {right*s*100:.1f}) aspect {(far+near)/(left+right):.3f}')
