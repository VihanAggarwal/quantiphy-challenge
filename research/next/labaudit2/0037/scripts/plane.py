"""Table plane in camera coords from the m2 PnP (table corners on the x-render median; 76.0 x 60.3 cm).
Prints the up-normal (camera y down) and camera height above the table top for several f. Saves plane.json."""
import sys, json, numpy as np, cv2
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/m2')
from cyl import pose
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0037'
res = {}
for f in (711, 725, 735):
    K, rv, tv, err = pose(f)
    R, _ = cv2.Rodrigues(rv)
    # table frame: z axis = table normal (sign: camera side positive)
    nz = R[:, 2]                     # table z-axis in camera coords
    cam = -R.T @ tv.ravel()          # camera in table coords
    if cam[2] < 0:
        nz = -nz; h = -cam[2]
    else:
        h = cam[2]
    # plane: points X (camera coords) with nz.X = nz.(R*0+tv) ... table top passes through tv (origin)
    d0 = nz @ tv.ravel()             # nz.X = d0 for table points; camera (X=0) is at height h on +nz side => d0 = -h
    res[f] = dict(n_up=nz.tolist(), h=float(h), d0=float(d0), reproj=float(err))
    print(f, 'n_up(cam)', nz.round(4), 'h=%.4f d0=%.4f reproj %.2f px tilt %.2f deg' % (h, d0, err, np.degrees(np.arccos(abs(nz[1])))))
json.dump(res, open(OUT + '/plane.json', 'w'), indent=1)
