"""captured_0062: floor plane from depth anchors of flat objects, then rectified extents of flat objects.
Test inputs only (frames + depth_info)."""
import sys, cv2, numpy as np
sys.path.insert(0, 'research/next/labstatic')
from frames import read_all
from xmask import comps
CX, CY = 640.0, 360.0

def dvec(u, v, f):
    return np.array([(u - CX) / f, (v - CY) / f, 1.0])

def solve_floor(anchors, f):
    """anchors: list of (u, v, range, height_above_floor). Grid search over pitch th and height h."""
    best = None
    for th in np.radians(np.arange(0, 60, 0.05)):
        dn = np.array([0, np.cos(th), np.sin(th)])
        # for each anchor, h_i = dn . X_i + height_i  where X_i = range * d/|d|
        hs = []
        for u, v, r, hgt in anchors:
            d = dvec(u, v, f); X = r * d / np.linalg.norm(d)
            hs.append(dn @ X + hgt)
        hs = np.array(hs)
        err = hs.std()
        if best is None or err < best[0]:
            best = (err, th, hs.mean(), hs)
    return best

def to_floor(u, v, f, th, h, hgt=0.0):
    dn = np.array([0, np.cos(th), np.sin(th)])
    d = dvec(u, v, f)
    t = (h - hgt) / (dn @ d)
    return t * d

def rect_extent(mask, f, th, h, hgt=0.0):
    ys, xs = np.nonzero(mask)
    # contour points only
    cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)[:, 0, :]
    pts = np.array([to_floor(u, v, f, th, h, hgt) for u, v in c])
    # floor 2D basis
    dn = np.array([0, np.cos(th), np.sin(th)])
    e1 = np.array([1.0, 0, 0]); e2 = np.cross(dn, e1); e2 /= np.linalg.norm(e2)
    p2 = np.c_[pts @ e1, pts @ e2].astype(np.float32)
    (cx, cy), (w, hh), ang = cv2.minAreaRect(p2)
    return max(w, hh), min(w, hh), ang

if __name__ == '__main__':
    for f in (711.0, 722.0):
        fr = read_all('captured_0062x')
        out34, lab34 = comps('captured_0062x', 34)
        out0, lab0 = comps('captured_0062x', 0)
        def find(out, x, y):
            return min(out, key=lambda o: (o['cx'] - x) ** 2 + (o['cy'] - y) ** 2)
        bag = find(out34, 838, 329); wb = find(out34, 705, 415); box = find(out34, 516, 495); mario = find(out34, 635, 624); bin_ = find(out34, 338, 157)
        anchors = [(bag['cx'], bag['cy'], 3.307, 0.01), (wb['cx'], wb['cy'], 2.815, 0.02)]
        err, th, h, hs = solve_floor(anchors, f)
        print(f'f={f}: pitch {np.degrees(th):.2f} deg, height {h:.3f} m, resid {err:.4f}')
        # check other anchors: implied height above floor of box / mario / trashbin clicked points
        dn = np.array([0, np.cos(th), np.sin(th)])
        for nm, o, r in (('box', box, 2.082), ('mario', mario, 2.016), ('bin', bin_, 2.303)):
            d = dvec(o['cx'], o['cy'], f); X = r * d / np.linalg.norm(d)
            print(f'   {nm}: clicked point {h - dn @ X:+.3f} m above floor')
        for nm, o, lab, hgt in (('bag', bag, lab34, 0.01), ('whiteboard@34', wb, lab34, 0.02), ('box', box, lab34, 0.0)):
            L, W, a = rect_extent(lab == o['i'], f, th, h, hgt)
            print(f'   {nm}: rectified {L*100:.1f} x {W*100:.1f} cm')

def fit_plane(anchors, f):
    """General plane n.X = h through anchor points lifted by their heights (least squares, n unit)."""
    X = []
    for u, v, r, hgt in anchors:
        d = dvec(u, v, f); X.append(r * d / np.linalg.norm(d))
    X = np.array(X); hg = np.array([a[3] for a in anchors])
    best = None
    for th in np.radians(np.arange(10, 80, 0.1)):
        for ro in np.radians(np.arange(-15, 15.01, 0.25)):
            n = np.array([np.sin(ro) * np.cos(th), np.cos(ro) * np.cos(th), np.sin(th)])
            hs = X @ n + hg
            e = hs.std()
            if best is None or e < best[0]:
                best = (e, th, ro, hs.mean(), hs - hs.mean())
    return best
