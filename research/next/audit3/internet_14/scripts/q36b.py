import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0036.mp4')
k=0
s=4
while True:
    ok,im=c.read()
    if not ok: break
    if k<33: k+=1; continue
    sm=cv2.resize(im,None,fx=1/s,fy=1/s,interpolation=cv2.INTER_AREA).astype(int)
    b,g,r=sm[...,0],sm[...,1],sm[...,2]
    skin=(((r-b)>25)&(r>90)).astype(np.uint8)
    skin=cv2.morphologyEx(skin,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    H,W=skin.shape
    yy,xx=np.mgrid[0:H,0:W]
    # top hand: skin pixels with  y < 0.85*x - something?  separate by line: top hand region = upper-right of line through (0,1300/4)...
    # use connected comps: top hand comp touches top edge (y=0) at x>700/4
    n,lab,st,cen=cv2.connectedComponentsWithStats(skin)
    top=[i for i in range(1,n) if st[i,1]==0 and st[i,4]>20]
    out=f"{k}: "
    if top:
        m=np.isin(lab,top); ys,xs=np.nonzero(m)
        d=(-xs+ys)  # extreme toward down-left
        j=np.argmax(d); out+=f"TOP area{m.sum()} fingertip({xs[j]*s},{ys[j]*s}) cen({xs.mean()*s:.0f},{ys.mean()*s:.0f}) "
    # bill: non-skin, darker than background: background ~ bright; use grey value < 175 and saturation low
    gray=(b+g+r)/3
    hsv=cv2.cvtColor(sm.astype(np.uint8),cv2.COLOR_BGR2HSV)
    bill=((gray<200)&(skin==0)&(hsv[...,1]<90)).astype(np.uint8)
    bill=cv2.morphologyEx(bill,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n2,lab2,st2,cen2=cv2.connectedComponentsWithStats(bill)
    if n2>1:
        i=1+np.argmax(st2[1:,4]); ys,xs=np.nonzero(lab2==i)
        u=xs*0.819-ys*0.574
        j=np.argmax(u)
        out+=f"| BILL area{st2[i,4]} rightend({xs[j]*s},{ys[j]*s}) cen({xs.mean()*s:.0f},{ys.mean()*s:.0f})"
    print(out)
    k+=1
