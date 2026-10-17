# Track the ping-pong ball in each render: diff from temporal median, largest blob near prediction.
import cv2, numpy as np, json, sys
R = sys.argv[1] if len(sys.argv)>1 else 'x'
p = '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4' % ('' if R=='o' else R)
c = cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr)
med=np.median(fr,axis=0).astype(np.int16)
res=[]
prev=None
for i,f in enumerate(fr):
    d=np.abs(f.astype(np.int16)-med).max(axis=2)
    m=(d>35).astype(np.uint8)
    m[685:,1000:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        a=st[k,4]
        if a<30: continue
        if R=='o' and cen[k,0]<560 and i>2: continue
        sc=a
        if prev is not None:
            dist=np.hypot(cen[k,0]-prev[0],cen[k,1]-prev[1])
            if dist>150: continue
            sc=a-2*dist
        if best is None or sc>best[0]: best=(sc,k)
    if best is None:
        res.append(None); print(i,'none'); continue
    k=best[1]; x,y,w,h,a=st[k]
    mk=(lab==k)
    ys,xs=np.nonzero(mk)
    # weighted centroid by diff
    wts=d[ys,xs].astype(float)
    cx=(xs*wts).sum()/wts.sum(); cy=(ys*wts).sum()/wts.sum()
    prev=(cen[k,0],cen[k,1])
    res.append(dict(f=i,cx=float(cen[k,0]),cy=float(cen[k,1]),wcx=float(cx),wcy=float(cy),x=int(x),y=int(y),w=int(w),h=int(h),area=int(a)))
    print(i,'c(%.1f,%.1f) w(%.1f,%.1f) bb %d,%d %dx%d a%d'%(cen[k,0],cen[k,1],cx,cy,x,y,w,h,a))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0033/track_%s.json'%R,'w'),indent=0)
