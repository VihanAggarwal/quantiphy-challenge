import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0036.mp4')
k=0; s=4
while True:
    ok,im=c.read()
    if not ok: break
    sm=cv2.resize(im,None,fx=1/s,fy=1/s,interpolation=cv2.INTER_AREA).astype(int)
    b,g,r=sm[...,0],sm[...,1],sm[...,2]
    skin=(((r-b)>25)&(r>90)).astype(np.uint8)
    skin=cv2.morphologyEx(skin,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(skin)
    # bottom hand = all comps not touching top edge
    bot=[i for i in range(1,n) if st[i,1]>0 and st[i,4]>20]
    if bot:
        m=np.isin(lab,bot); ys,xs=np.nonzero(m)
        d=xs-ys; j=np.argmax(d)
        # also extreme along (0.5,-0.866) (up-ish) 
        print(k, f"area{m.sum()} upright-extreme({xs[j]*s},{ys[j]*s}) top-most({xs[np.argmin(ys)]*s},{ys.min()*s}) cen({xs.mean()*s:.0f},{ys.mean()*s:.0f})")
    k+=1
