import cv2, numpy as np, sys, json
def load(v):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    fr = []
    while True:
        ok, im = c.read()
        if not ok: break
        fr.append(im)
    return np.array(fr)
def comps(v, thr=30, minarea=150, frames=None, roi=None):
    F = load(v)
    bg = np.median(F, axis=0).astype(np.int16)
    out = {}
    for i in (frames if frames is not None else range(len(F))):
        d = np.abs(F[i].astype(np.int16) - bg).max(axis=2)
        m = (d > thr).astype(np.uint8)
        if roi is not None:
            x0,y0,x1,y1 = roi; mm = np.zeros_like(m); mm[y0:y1,x0:x1] = m[y0:y1,x0:x1]; m = mm
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7,7),np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        L = [(int(st[k,0]),int(st[k,1]),int(st[k,2]),int(st[k,3]),int(st[k,4]),float(cen[k,0]),float(cen[k,1])) for k in range(1,n) if st[k,4]>=minarea]
        out[i] = sorted(L, key=lambda t: t[5])
    return out, F, bg
if __name__ == '__main__':
    v = sys.argv[1]; thr = int(sys.argv[2]) if len(sys.argv)>2 else 30
    out, F, bg = comps(v, thr)
    for i in [0,12,24,36,48]:
        print(i, out[i])
