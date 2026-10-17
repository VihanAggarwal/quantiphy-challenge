# backward-difference speeds and accelerations from a centroid track; args: track.json scale(m/px) frames... [fitrange a b]
import json, sys, numpy as np
tr = json.load(open(sys.argv[1])); scale = float(sys.argv[2]); qf = [int(x) for x in sys.argv[3].split(',')]
a, b = (int(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 else (0, 10**9)
pts = [(i, r['cx'], r['cy']) for i, r in tr if r is not None and a <= i <= b]
F = np.array([p[0] for p in pts], float); X = np.array([p[1] for p in pts]); Y = np.array([p[2] for p in pts])
fps = 24.0
for deg in (2, 3):
    px = np.polyfit(F, X, deg); py = np.polyfit(F, Y, deg)
    res = np.sqrt(np.mean((np.polyval(px, F) - X) ** 2 + (np.polyval(py, F) - Y) ** 2))
    out = []
    for q in qf:
        p1 = np.array([np.polyval(px, q), np.polyval(py, q)]); p0 = np.array([np.polyval(px, q - 1), np.polyval(py, q - 1)]); pm = np.array([np.polyval(px, q - 2), np.polyval(py, q - 2)])
        v1 = np.linalg.norm(p1 - p0) * fps * scale; v0 = np.linalg.norm(p0 - pm) * fps * scale
        out.append('f%d: v=%.3f a=%.3f' % (q, v1, (v1 - v0) * fps))
    print('deg%d rms %.2f px | ' % (deg, res) + ' | '.join(out))
# local windowed (±3 frames) linear-in-time velocity
d = dict((int(f), (x, y)) for f, x, y in zip(F, X, Y))
for q in qf:
    w = [k for k in range(q - 4, q + 3) if k in d]
    if len(w) >= 4:
        ff = np.array(w, float); xx = np.array([d[k][0] for k in w]); yy = np.array([d[k][1] for k in w])
        cx = np.polyfit(ff, xx, 2); cy = np.polyfit(ff, yy, 2)
        t = q - 0.5
        vx = np.polyval(np.polyder(cx), t); vy = np.polyval(np.polyder(cy), t)
        print('local f%d: v(t-1/2 frame)=%.3f m/s' % (q, np.hypot(vx, vy) * fps * scale))
