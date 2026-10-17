import numpy as np, cv2, json, sys
from load import load
vid = sys.argv[1] if len(sys.argv) > 1 else '0311'
ref = int(sys.argv[2]) if len(sys.argv) > 2 else 30
fr = load(vid)
G = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
F = np.stack([f for f in fr[::4]])
bg = np.median(F, axis=0).astype(np.uint8)
def mask(i):
    d = np.abs(fr[i].astype(np.int16) - bg.astype(np.int16)).max(axis=2)
    m = (d > 30).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    m = cv2.erode(m, np.ones((15,15),np.uint8))
    return m
m = mask(ref)
pts = cv2.goodFeaturesToTrack(G[ref], 400, 0.01, 10, mask=m*255, blockSize=7)
N = len(pts)
lk = dict(winSize=(21,21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT, 50, 0.01))
T = np.full((len(G), N, 2), np.nan)
T[ref] = pts[:,0]
for direction in (1, -1):
    cur = pts.copy(); alive = np.ones(N, bool)
    i = ref
    while 0 <= i + direction < len(G):
        j = i + direction
        nxt, st, err = cv2.calcOpticalFlowPyrLK(G[i], G[j], cur, None, **lk)
        back, st2, _ = cv2.calcOpticalFlowPyrLK(G[j], G[i], nxt, None, **lk)
        fb = np.linalg.norm(back - cur, axis=2)[:,0]
        ok = (st[:,0]==1) & (st2[:,0]==1) & (fb < 0.3)
        # must stay on moving object
        mj = mask(j)
        xy = np.round(nxt[:,0]).astype(int)
        inside = (xy[:,0]>=0)&(xy[:,0]<mj.shape[1])&(xy[:,1]>=0)&(xy[:,1]<mj.shape[0])
        onobj = np.zeros(N,bool); onobj[inside] = mj[xy[inside,1], xy[inside,0]] > 0
        alive &= ok & inside
        T[j][alive] = nxt[alive,0]
        cur = nxt; i = j
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/tracks_%s_%d.npy' % (vid, ref), T)
valid = ~np.isnan(T[:,:,0])
print('N', N, 'valid per frame', valid.sum(1).tolist())
