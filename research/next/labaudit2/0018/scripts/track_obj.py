"""Per-object centroids, v20..40: x-render matte and o-render background difference (bg = median of v0..10 for the
lower region, which is empty then; for the held region the object is present, so only frames after it leaves use bg)."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fx = frames('x'); fo = frames('')
# background for o render: per-pixel median over frames where objects are elsewhere
bg_late = np.median(fo[44:49].astype(np.float32), 0)   # objects on floor / ball rebound; upper/mid regions empty
bg_early = np.median(fo[0:10].astype(np.float32), 0)   # objects held; fall region empty
# object windows (x0,x1) in which each object stays
win = dict(box=(455, 515), soccer=(505, 575), tennis=(730, 780), pine=(830, 900))
out = {}
for name, (x0, x1) in win.items():
    rows = []
    for k in range(20, 41):
        mx = (np.abs(fx[k].astype(int) - 255).max(2) > 30)
        sub = np.zeros_like(mx); sub[150:715, x0:x1] = mx[150:715, x0:x1]
        n, lab, st, cen = cv2.connectedComponentsWithStats(sub.astype(np.uint8))
        best = None
        for i in range(1, n):
            if st[i, 4] < 60: continue
            # skip components touching the person's arm region: prefer compact component
            if best is None or st[i, 4] > st[best, 4]: best = i
        r = dict(k=k)
        if best is not None:
            x, y, w, h, a = st[best]; r.update(xc=float(cen[best][0]), yc=float(cen[best][1]), w=int(w), h=int(h), a=int(a), ytop=int(y), ybot=int(y + h - 1))
        # o-render bg difference vs early bg (valid once object below its held position)
        d = np.abs(fo[k].astype(np.float32) - bg_early).sum(2)
        m = np.zeros(d.shape, bool); m[290:715, x0:x1] = d[290:715, x0:x1] > 45
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n2, lab2, st2, cen2 = cv2.connectedComponentsWithStats(m)
        if n2 > 1:
            i = 1 + np.argmax(st2[1:, 4])
            if st2[i, 4] > 60:
                r.update(oxc=float(cen2[i][0]), oyc=float(cen2[i][1]), oh=int(st2[i, 3]), ow=int(st2[i, 2]))
        rows.append(r)
    out[name] = rows
json.dump(out, open(OUT + 'track_obj.json', 'w'), indent=0)
for name, rows in out.items():
    print('==', name)
    for r in rows:
        print(r['k'], *(f"{key}={r[key]:.1f}" if isinstance(r.get(key), float) else f"{key}={r.get(key)}" for key in ['xc', 'yc', 'w', 'h', 'ytop', 'ybot', 'oxc', 'oyc', 'ow', 'oh']))
