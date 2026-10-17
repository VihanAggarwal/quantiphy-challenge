"""Ball diameter: static ball (video 10-17, no motion blur) at its plane range; moving ball at the stated ranges.
Widths from the horizontal half-maximum crossings of a whiteness profile (row through the ball centre)."""
import numpy as np, json, cv2, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0039/scripts')
from frames import load
OUT = '/home/user/quantiphy-challenge/research/next/labaudit2/0039'
F, CX, CY = 711.0, 640.0, 360.0
pl = json.load(open(f'{OUT}/plane.json')); n = np.array(pl['n_vp']); H0 = pl['h_vp']
T = json.load(open(f'{OUT}/track2.json'))
def ray(p): r = np.array([(p[0] - CX) / F, (p[1] - CY) / F, 1.0]); return r / np.linalg.norm(r)
def hmw(prof):
    """full width at half max between the background (ends) and the peak (sub-pixel)"""
    bg = np.median(np.r_[prof[:6], prof[-6:]]); pk = np.percentile(prof, 95); thr = (bg + pk) / 2
    idx = np.nonzero(prof > thr)[0]; a, b = idx.min(), idx.max()
    xa = a - 1 + (thr - prof[a - 1]) / (prof[a] - prof[a - 1]); xb = b + (prof[b] - thr) / (prof[b] - prof[b + 1])
    return xb - xa, (xa + xb) / 2
for rend in ['0039', '0039s']:
    fr = load(rend); tr = {int(k): v for k, v in T[rend].items()}
    st = np.median(fr[10:18], axis=0).astype(np.uint8)
    for lab, img, (u, v), rngs in [('static f10-17', st, tr[14]['cf'][:2], None), ('f24', fr[24], tr[24]['cf'][:2], 1.014 + 0.02), ('f36', fr[36], tr[36]['cf'][:2], 0.737 + 0.02)]:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(float)
        wh = hsv[..., 2] - hsv[..., 1]
        u0, v0 = int(round(u)), int(round(v))
        ws = []
        for dv in (-1, 0, 1):
            w, c = hmw(wh[v0 + dv, u0 - 40:u0 + 41]); ws.append(w)
        w = max(ws)
        if rngs is None:
            # static ball: centre on the plane 2 cm above the table
            r = (H0 - 0.02) / (n @ ray((u, v))); rngs = r
            rr = [(H0 * f - 0.02) / (n @ ray((u, v))) for f in (0.98, 1.02)]
            extra = f' (h+-2%: {rr[0]:.3f}-{rr[1]:.3f})'
        else: extra = ''
        print(f'{rend} {lab}: centre px ({u:.1f},{v:.1f}) half-max width {w:.2f} px; centre range {rngs:.4f}{extra} -> D = {w * rngs / F * 100:.2f} cm')
