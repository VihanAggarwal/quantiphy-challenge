"""Ball centre range at the table-bounce frames if the ball (r=2 cm) touches the table plane.
Plane from rectified corners (scale s=1.00 and s calibrated on the stated credit-card range)."""
import json, numpy as np, cv2
F, CX, CY = 711.0, 640.0, 360.0
K = np.array([[F, 0, CX], [0, F, CY], [0, 0, 1.]])
img = np.array([[210, 538], [1138, 587], [917.8, 467.1], [448.5, 448.8]], float)
obj = np.array([[0, 0, 0], [.76, 0, 0], [.76, .603, 0], [0, .603, 0]], float)
ok, rv, t = cv2.solvePnP(obj, img, K, None, flags=cv2.SOLVEPNP_IPPE)
Rm = cv2.Rodrigues(rv)[0]; n = Rm[:, 2]; t = t.ravel(); d0 = n @ t
if d0 < 0: n, d0 = -n, -d0     # n.X = d0 on the plane, n points away from camera side (down)
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
def on_plane(u, v, s=1.0, h=0.0):
    r = ray(u, v); return (s * d0 - h) / (n @ r) * r
card = np.linalg.norm(on_plane(563, 540)); s_card = 0.69 / card
print('camera height above table', d0, 'normal', n.round(4), 'card range on plane', round(card, 3), 'scale', round(s_card, 3))
tr = {int(k): v for k, v in json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0040/track_x.json')).items()}
for i in (32, 33, 34, 40, 41, 42):
    u, v = tr[i]['u'], tr[i]['v']
    for s in (1.0, s_card):
        X = on_plane(u, v, s, 0.02)
        print(f'f{i} ({u:.0f},{v:.0f}) s={s:.3f}: centre-on-bounce range {np.linalg.norm(X):.3f}; size-range {F*0.04/(tr[i]["minor"]*ray(u,v)[2]):.3f}')
# height above table of the ball at stated anchors
for (u, v, rr, lab) in [(754.0, 357.8, 0.7045, 't=1.5 stated'), (1180.7, 479.4, 0.627, 't=2.0 stated')]:
    X = rr * ray(u, v)
    for s in (1.0, s_card):
        print(lab, f's={s:.3f} height of ball centre above table plane: {(s*d0 - n @ X)*100:.1f} cm')
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0040/plane.npy', np.r_[n, d0, s_card])
