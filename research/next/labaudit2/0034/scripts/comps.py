import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0034/scripts')
from frames import read
v=sys.argv[1]
fr=read(v)
for i,im in enumerate(fr):
    h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    H=h[...,0]; S=h[...,1]; V=h[...,2]
    m=((S>80)&(V>60)&(H>=25)&(H<=42)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for k in range(1,n):
        x,y,w,hh,a=st[k]
        if a<80: continue
        out.append((int(a),round(cen[k][0],1),round(cen[k][1],1),int(w),int(hh)))
    out.sort(reverse=True)
    print(i,out[:4])
