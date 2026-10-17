from common import *
# soccer ball in ax: non-green, bright/dark-neutral ball pixels, region below the person
for k in [0,4,8,12,16,20,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]:
    im=frames('ax')[k].astype(np.int32)
    d=np.abs(im-np.array([0,255,0])).sum(2); m=(d>150).astype(np.uint8)
    hsv=cv2.cvtColor(frames('ax')[k],cv2.COLOR_BGR2HSV)
    ball=(m>0)&(hsv[...,1]<70)  # low saturation (white/black/grey ball); excludes skin, green
    reg=np.zeros_like(m); reg[540:720,0:330]=1
    ball=(ball&(reg>0)).astype(np.uint8)
    ball=cv2.morphologyEx(ball,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    ball=cv2.morphologyEx(ball,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(ball)
    if n<2: print(k,'none'); continue
    i=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==i)
    pts=np.stack([xs,ys],1).astype(np.float32); hull=cv2.convexHull(pts)
    (ex,ey),(ea,eb),ang=cv2.fitEllipse(hull)
    (cx,cy),r=cv2.minEnclosingCircle(pts)
    print(k,cap(k),'cent=(%.1f,%.1f) bb x[%d,%d] y[%d,%d] w=%d h=%d ell=(%.1f,%.1f) %.1fx%.1f A=%d'%(xs.mean(),ys.mean(),xs.min(),xs.max(),ys.min(),ys.max(),xs.max()-xs.min()+1,ys.max()-ys.min()+1,ex,ey,max(ea,eb),min(ea,eb),st[i,4]))
