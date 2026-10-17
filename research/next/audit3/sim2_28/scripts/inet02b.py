import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0002_segmented')
out=[]
for i,f in enumerate(F):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,v=[hsv[...,k].astype(int) for k in range(3)]
    red=(((h<15)|(h>165))&(s>80)&(v>60)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(red)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    if st[k][4]<300: continue
    x,y,w,hh,a=st[k]
    # full car (non-black) component containing red blob
    nb=(f.max(axis=2)>40).astype(np.uint8)
    n2,lab2,st2,cen2=cv2.connectedComponentsWithStats(nb)
    kk=lab2[int(cen[k][1]),int(cen[k][0])]
    X,Y,W,H,A=st2[kk]
    out.append((i,x,x+w,y,y+hh,cen[k][0],X,X+W,Y,Y+H,cen2[kk][0]))
o=np.array(out,float)
for r in o: print(r.round(1))
