import cv2, numpy as np, sys
vid=sys.argv[1]
c=cv2.VideoCapture(vid); i=0
while True:
    ok,f=c.read()
    if not ok: break
    b,g,r=[f[...,k].astype(int) for k in range(3)]
    green=(g>150)&(r<120)&(b<120)
    m=(~green).astype(np.uint8)
    m[690:,:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(int(st[k,4]),np.round(cen[k],1).tolist(),st[k,:4].tolist()) for k in range(1,n) if 20<=st[k,4]<5000]
    print(i, comps)
    i+=1
