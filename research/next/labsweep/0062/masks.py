import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0062x.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in (0,34,48):
        g=f.astype(int).sum(2)
        m=(g>60).astype(np.uint8)
        m[690:,1000:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        print('frame',i)
        for k in range(1,n):
            if st[k,4]>200: print(k,st[k],cen[k].round(1))
    i+=1
