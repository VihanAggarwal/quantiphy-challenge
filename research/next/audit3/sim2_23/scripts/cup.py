import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>105)&(hsv[...,0]<135)&(hsv[...,1]>120)&(hsv[...,2]>25)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); i+=1; continue
    k=1+np.argmax(st[1:,4])
    if st[k,4]<200: print(i,'small'); i+=1; continue
    ys,xs=np.nonzero(lab==k)
    # principal axis
    cov=np.cov(np.vstack([xs,ys])); w,V=np.linalg.eigh(cov); ax=V[:,1]
    ang=np.degrees(np.arctan2(ax[1],ax[0]))%180
    print(i, st[k].tolist(), 'cen %.1f %.1f'%tuple(cen[k]), 'axis %.1f'%ang)
    i+=1
