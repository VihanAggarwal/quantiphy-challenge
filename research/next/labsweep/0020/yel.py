import cv2, numpy as np, sys
vid=sys.argv[1]
c=cv2.VideoCapture(vid); i=0
while True:
    ok,f=c.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>=18)&(hsv[...,0]<=38)&(hsv[...,1]>=90)&(hsv[...,2]>=120)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k,4],cen[k],st[k,:4]) for k in range(1,n) if st[k,4]>=15]
    comps.sort(key=lambda x:-x[0])
    print(i, [(a, np.round(b,1).tolist(), s.tolist()) for a,b,s in comps[:3]])
    i+=1
