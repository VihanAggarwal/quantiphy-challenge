import cv2, numpy as np, json, sys
v = sys.argv[1]; thr = int(sys.argv[2]) if len(sys.argv)>2 else 35
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg = cv2.imread('scripts/bg_corr.png').astype(np.float32)
tr = json.load(open(f'scripts/{v}_track.json'))
out=[]
for i,f in enumerate(fr):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    d = np.abs(f.astype(np.float32)-bg).max(2)
    x,y,w,h = tr[i]['bbox']
    sub = (hsv[y:y+h, x:x+w, 2] < thr) & (d[y:y+h,x:x+w] > 35)
    sub = cv2.morphologyEx(sub.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
    n,lab,st,cen = cv2.connectedComponentsWithStats(sub)
    if n<2: out.append(None); continue
    k = 1+np.argmax(st[1:,4])
    ys,xs = np.nonzero(lab==k)
    rows = np.bincount(ys)
    good = np.nonzero(rows>=2)[0]
    ylow = y+good.max(); ytop = y+good.min()
    # lowest points of left/right halves
    xm = np.median(xs)
    lowL = y+ys[xs<xm].max(); lowR = y+ys[xs>=xm].max()
    xl = x+xs[ys==ys[xs<xm].max()].mean(); xr = x+xs[ys==ys[xs>=xm].max()].mean()
    out.append(dict(i=i, ytop=int(ytop), ylow=int(ylow), lowL=int(lowL), lowR=int(lowR), xl=float(xl), xr=float(xr)))
json.dump(out, open(f'scripts/{v}_feet.json','w'))
for r in out: print(r)
