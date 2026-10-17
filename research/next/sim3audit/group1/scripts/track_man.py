import cv2, numpy as np, sys, json, os
def load(v):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
A = load('simulation_0141'); B = load('simulation_0143')
if not os.path.exists('scripts/bg_corr.png'):
    bg = np.median(np.stack(A[::2]+B[::2]).astype(np.float32),0)
    cv2.imwrite('scripts/bg_corr.png', bg.astype(np.uint8))
bg = cv2.imread('scripts/bg_corr.png').astype(np.float32)
for v, fr in [('simulation_0141',A),('simulation_0143',B)]:
    res=[]
    for i,f in enumerate(fr):
        d = np.abs(f.astype(np.float32)-bg).max(2)
        m = (d>35).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
        n,lab,st,cen = cv2.connectedComponentsWithStats(m)
        if n<2: res.append(None); continue
        k = 1+np.argmax(st[1:,cv2.CC_STAT_AREA])
        x,y,w,h,a = st[k]
        ys,xs = np.nonzero(lab==k)
        rows = np.bincount(ys, minlength=f.shape[0])
        tops = np.nonzero(rows>=3)[0]
        res.append(dict(i=i, bbox=[int(x),int(y),int(w),int(h)], area=int(a), top=int(tops.min()), cx=float(xs.mean())))
        cv2.imwrite(f'frames/mask_{v[-4:]}_{i:03d}.png', (lab==k).astype(np.uint8)*255) if i%12==0 else None
    json.dump(res, open(f'scripts/{v}_track.json','w'))
    print(v)
    for r in res[::3]: print(r)
