import cv2, numpy as np, sys
vid=sys.argv[1]; out=sys.argv[2]
c=cv2.VideoCapture(vid); i=0; rows=[]
while True:
    ok,f=c.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>=5)&(hsv[...,0]<=22)&(hsv[...,1]>120)&(hsv[...,2]>120)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        # include all comps near the main one (windshield splits mask)
        sel=[j for j in range(1,n) if st[j,4]>20 and abs(cen[j,0]-cen[k,0])<0.08*f.shape[1] and abs(cen[j,1]-cen[k,1])<0.3*f.shape[0]]
        mm=np.isin(lab,sel); ys,xs=np.nonzero(mm)
        rows.append((i,xs.min(),ys.min(),xs.max(),ys.max(),xs.mean(),ys.mean(),mm.sum()))
    else: rows.append((i,-1,-1,-1,-1,-1,-1,0))
    i+=1
np.savetxt(out,np.array(rows),fmt='%.3f')
