import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0054{v}.mp4')
i=0
prev=None
while True:
    ok,f=c.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>=3)&(hsv[...,0]<=20)&(hsv[...,1]>=110)&(hsv[...,2]>=60)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for k in range(1,n):
        a=st[k,4]
        if a<200: continue
        w,h=st[k,2],st[k,3]
        fill=a/(w*h)
        if fill<0.5 or max(w,h)/min(w,h)>1.6: continue
        if best is None or a>best[0]: best=(a,k)
    if best:
        k=best[1]; x,y,w,h,a=st[k]
        cnt,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        (cx,cy),r=cv2.minEnclosingCircle(cnt[0])
        req=np.sqrt(a/np.pi)
        print(i, f'cx={cen[k][0]:.1f} cy={cen[k][1]:.1f} w={w} h={h} req={req:.1f} mec=({cx:.1f},{cy:.1f},{r:.1f})')
    else: print(i,'none')
    i+=1
