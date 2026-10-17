import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i=0; out=[]
while True:
    ok,f=c.read()
    if not ok: break
    f=cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,vv=[hsv[...,k].astype(int) for k in range(3)]
    red=(((h<12)|(h>168))&(s>90)&(vv>70)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(red)
    if n>1:
        k=1+np.argmax(st[1:,4])
        out.append((i,cen[k][0],cen[k][1],st[k][4]))
    i+=1
o=np.array(out)
print(np.round(o,1))
print('steps',np.round(np.diff(o[:,1]),1))
