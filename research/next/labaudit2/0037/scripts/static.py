"""Static re-check on the x-render median (black background): column/row extents of cup, poker tower, tape, jar.
Route A: extent_px * stated range / f (label-style: clicks at the two ends, ToF at the clicks ~ stated range).
Route B: plane (PnP f=711/735) for the bottom point + vertical line (height) or the axis range (tape diameter).
Writes img/static_crops.png for viewing."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0037/scripts')
from common import frames, OUT, CX, CY
PL = json.load(open(OUT + '/plane.json'))


def colext(x0, x1, y0, y1, fg=None):
    m = fg[y0:y1, x0:x1]
    rows = np.where(m.any(1))[0]; cols = np.where(m.any(0))[0]
    return x0 + cols.min(), x0 + cols.max(), y0 + rows.min(), y0 + rows.max()


def vert_extent(x, y0, y1, fg=None):
    col = np.where(fg[y0:y1, x])[0]
    return y0 + col.min(), y0 + col.max()


def plane_pt(u, v, f, hoff=0.0):
    pl = PL[str(f)]; n = np.array(pl['n_up'])
    r = np.array([(u - CX) / f, (v - CY) / f, 1.0])
    return r * ((-pl['h'] + hoff) / (n @ r))


def height_on_vertical(ub, vb, ut, vt, f):
    """bottom point on the plane; height where the ray through (ut,vt) meets the vertical line through it"""
    pl = PL[str(f)]; n = np.array(pl['n_up'])
    B = plane_pt(ub, vb, f)
    d = np.array([(ut - CX) / f, (vt - CY) / f, 1.0])
    # minimise |s d - (B + t n)|
    A = np.stack([d, -n], 1); s, t = np.linalg.lstsq(A, B, rcond=None)[0]
    return t, np.linalg.norm(B)


if __name__ == '__main__':
    fr = frames('x')
    med = np.median(np.stack(fr[::2]), axis=0).astype(np.uint8)
    gray = med.max(2).astype(float)
    fg = gray > 40
    crops = []
    # cup: columns ~ 735-815, rows 360-510 ; measure central column top and bottom
    for name, (x0, x1, y0, y1), rng in (('cup', (730, 820, 360, 515), 0.845), ('poker', (650, 730, 400, 505), 0.905),
                                         ('tape', (505, 605, 425, 485), 1.038), ('jar', (435, 505, 395, 495), 1.008)):
        a = colext(x0, x1, y0, y1, fg)
        xc = int((a[0] + a[1]) / 2)
        vt, vb = vert_extent(xc, y0, y1, fg)
        print(f'{name}: bbox x {a[0]}-{a[1]} (w {a[1]-a[0]+1}px) y {a[2]}-{a[3]} (h {a[3]-a[2]+1}px); centre column {xc}: top {vt} bottom {vb}')
        print(f'   route A (stated {rng}): height {(vb - vt + 1) * rng / 711 * 100:.2f} cm (f711) {(vb - vt + 1) * rng / 735 * 100:.2f} (f735); '
              f'width {(a[1] - a[0] + 1) * rng / 711 * 100:.2f} cm (f711)')
        for f in (711, 735):
            H, Rb = height_on_vertical(xc, vb, xc, vt, f)
            print(f'   route B plane f{f}: height {H*100:.2f} cm, bottom-front range {Rb:.3f}')
        c = med[y0 - 10:y1 + 10, x0 - 10:x1 + 10]
        crops.append(cv2.resize(c, (c.shape[1] * 3, c.shape[0] * 3), interpolation=cv2.INTER_NEAREST))
    H = max(c.shape[0] for c in crops)
    cv2.imwrite(OUT + '/img/static_crops.png', np.hstack([np.pad(c, ((0, H - c.shape[0]), (0, 4), (0, 0))) for c in crops]))
