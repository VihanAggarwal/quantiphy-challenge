import cv2, numpy as np, sys
vid=sys.argv[1]; thr=int(sys.argv[2]) if len(sys.argv)>2 else 40
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_%s.mp4'%vid)
F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.int16))
F=np.array(F)
bg=np.median(F,axis=0)
prev=None
for i in range(len(F)):
    d=np.abs(F[i]-bg)
    m=(d>thr).astype(np.uint8)
    m[690:,1000:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[j for j in range(1,n) if st[j,4]>40]
    cands.sort(key=lambda j:-st[j,4])
    s=[]
    for j in cands[:3]:
        ys,xs=np.nonzero(lab==j)
        pts=np.stack([xs,ys],1).astype(np.float32)
        (cx,cy),(w,h),ang=cv2.minAreaRect(pts)
        s.append('c(%.1f,%.1f) a%d rect %.1fx%.1f@%.0f'%(cen[j][0],cen[j][1],st[j,4],max(w,h),min(w,h),ang))
    print(i,' | '.join(s))
