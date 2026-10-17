import json, numpy as np
res = json.load(open('track140.json'))
pts = np.array([[r['i'], r['cx'], r['cy']] for r in res if r and r['area'] > 100])
t = pts[:,0]/24.0; X = pts[:,1]; Y = pts[:,2]
def circfit(X, Y):
    A = np.c_[2*X, 2*Y, np.ones_like(X)]; b = X**2+Y**2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, yc = c[0], c[1]; R = np.sqrt(c[2] + xc**2 + yc**2); return xc, yc, R
keep = np.ones(len(t), bool)
for it in range(6):
    xc, yc, R = circfit(X[keep], Y[keep])
    ang = np.unwrap(np.arctan2(Y-yc, X-xc))
    w, a0 = np.polyfit(t[keep], ang[keep], 1)
    am = a0 + w*t
    xm, ym = xc + R*np.cos(am), yc + R*np.sin(am)
    e = np.hypot(xm-X, ym-Y)
    keep = e < max(3*np.median(e[keep]), 6)
print('n', keep.sum(), len(t), 'rms', np.sqrt(np.mean(e[keep]**2)), 'radial rms', np.std(np.hypot(X-xc,Y-yc)[keep]-R))
print('center', xc, yc, 'R', R, 'w deg/s', np.rad2deg(w), 'px speed', R*w)
for tt in [0, 0.5, 1.0, 99/24]:
    a = a0 + w*tt; print(tt, xc + R*np.cos(a), yc + R*np.sin(a))
print('arc deg over 99 frames', np.rad2deg(w*99/24), 'arc px', R*w*99/24)
cf = np.polyfit(t[keep], ang[keep], 2); print('angular accel deg/s^2', np.rad2deg(cf[0]*2), 'w at 0,2,4', [np.rad2deg(np.polyval(np.polyder(cf), tt)) for tt in (0,2,4)])
rr = np.hypot(X-xc, Y-yc); print('radius vs t slope px/s', np.polyfit(t[keep], rr[keep], 1))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/circ.npy', np.array([xc,yc,R,a0,w]))
