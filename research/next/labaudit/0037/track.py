import cv2, numpy as np, sys
v=sys.argv[1] if len(sys.argv)>1 else 'x'
fr=[cv2.imread('frames/v%s_%02d.png'%(v,i)) for i in range(49)]
med=np.median(np.stack(fr[::2]),axis=0).astype(np.float32)
out=[]
for i,f in enumerate(fr):
    d=np.abs(f.astype(np.float32)-med).sum(2)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((d>60)&(hsv[...,2]>150)&(hsv[...,1]<70)).astype(np.uint8)
    m[:200]=0; m[600:]=0; m[:,1000:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,l,st,c=cv2.connectedComponentsWithStats(m)
    if n<2: out.append((i,None)); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    out.append((i,(round(c[k][0],1),round(c[k][1],1),w,h,a)))
for o in out: print(o)
