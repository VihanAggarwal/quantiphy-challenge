import cv2, numpy as np, sys
vid=sys.argv[1]
c=cv2.VideoCapture(vid)
i=0; out=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    X0,Y0=1240,60
    roi=g[Y0:720,X0:1520]
    m=(roi>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    wts=roi[ys,xs].astype(float)
    cx=(xs*wts).sum()/wts.sum()+X0; cy=(ys*wts).sum()/wts.sum()+Y0
    out.append((i,x+X0,y+Y0,w,h,a,xs.mean()+X0,ys.mean()+Y0,cx,cy))
    i+=1
np.savetxt(sys.argv[2],np.array(out),fmt='%.3f')
