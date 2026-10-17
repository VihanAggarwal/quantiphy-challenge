import cv2, numpy as np, sys
vid=sys.argv[1]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_%s.mp4'%vid)
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    m=(g>150).astype(np.uint8)
    # mask out the static objects region (table objects): x 450-830, y 360-520
    m[350:530,460:830]=0
    m[690:,1000:]=0 # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for j in range(1,n):
        if st[j,4]>30 and (best is None or st[j,4]>st[best,4]): best=j
    if best:
        x,y,w,h,a=st[best]; print(i, 'cen %.1f %.1f bbox %d %d %d %d area %d'%(cen[best][0],cen[best][1],x,y,w,h,a))
    else: print(i,'none')
    i+=1
