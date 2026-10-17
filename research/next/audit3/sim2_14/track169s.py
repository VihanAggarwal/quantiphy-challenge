import cv2, numpy as np, sys
c=cv2.VideoCapture(sys.argv[1]); i=0; out=[]
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    X0,Y0=1200,40
    roi=255-g[Y0:740,X0:1560].astype(np.int32)
    m=(roi>25).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    out.append((i,x+X0,y+Y0,w,h,a,xs.mean()+X0,ys.mean()+Y0))
    i+=1
np.savetxt(sys.argv[2],np.array(out),fmt='%.3f')
