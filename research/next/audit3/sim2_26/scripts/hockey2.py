import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0126')
for i in [0,3,6,10,30,60,71]:
    f=F[i]
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,v=[hsv[...,k].astype(int) for k in range(3)]
    red=(((h<=6)|(h>=170))&(s>110)).astype(np.uint8)
    red=cv2.morphologyEx(red,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(red)
    out=[]
    for k in range(1,n):
        x,y,w,hh,a=st[k]
        if a>3000: out.append((x,y,w,hh,a,round(cen[k][0],1),round(cen[k][1],1)))
    print(i,out)
save(F[30][1300:1560,580:850],'v0126_handle.png',2)
