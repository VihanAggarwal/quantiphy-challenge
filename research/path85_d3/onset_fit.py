"""Fit the fall onset t0 of the falling object in clips whose prior states 'acceleration ... before T = 9.8':
the object's image row (centroid of its moving blob, found against the clip's last frame) vs time, fitted with
y = y0 + c * max(t - t0, 0)^2 over the first frames. Test frames only."""
from common import *
import cv2, sys
t = test_df()
def track(v, nmax=12):
    r = t[t.video_id == v].iloc[0]
    cap = cv2.VideoCapture(r.video_path); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.int16))
    last = fr[-1]
    ys = []
    for i in range(min(nmax, len(fr))):
        m = np.abs(fr[i] - last) > 30
        # restrict to the region occupied by the object in frame 0..i: use the frame-0 vs last mask bbox columns
        ys.append(m)
    m0 = ys[0]
    yy, xx = np.nonzero(m0)
    x0, x1 = np.percentile(xx, 2), np.percentile(xx, 98)
    out = []
    for i, m in enumerate(ys):
        sub = m[:, int(x0):int(x1) + 1]
        rows = np.nonzero(sub.sum(axis=1) > 3)[0]
        # the object blob nearest the top: take the first connected run of rows
        if not len(rows): out.append(np.nan); continue
        runs = np.split(rows, np.nonzero(np.diff(rows) > 3)[0] + 1)
        top = runs[0]
        w = sub[top].sum(axis=1)
        out.append(float((top * w).sum() / w.sum()))
    return np.array(out), r.fps
for v in sys.argv[1:] or ['simulation_0202', 'simulation_0205', 'simulation_0206', 'simulation_0209']:
    y, fps = track(v)
    tt = np.arange(len(y)) / fps
    ok = np.isfinite(y)
    best = None
    for t0 in np.arange(-0.15, 0.2, 0.002):
        X = np.c_[np.ones(ok.sum()), np.maximum(tt[ok] - t0, 0) ** 2]
        coef, *_ = np.linalg.lstsq(X, y[ok], rcond=None)
        rr = float(np.sqrt(np.mean((X @ coef - y[ok]) ** 2)))
        if best is None or rr < best[0]: best = (rr, t0, coef)
    rr, t0, coef = best
    print(v, 'fps', fps, 'y', np.round(y, 1).tolist())
    print('   fit t0 = %.4f s (%.2f frames), c=%.0f px/s^2, resid rms %.2f px' % (t0, t0 * fps, coef[1], rr))
