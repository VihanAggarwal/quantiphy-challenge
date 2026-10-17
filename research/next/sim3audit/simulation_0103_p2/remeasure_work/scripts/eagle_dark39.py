from vio import *
import cv2, numpy as np
from chord import solve_f
fr=load('0039')
# rough linear path guess
k0=np.array([18,33,48]); x0=np.array([360,686,1035.]); y0=np.array([625,712,790.])
cx=np.polyfit(k0,x0,1); cy=np.polyfit(k0,y0,1)
out=[]
for k in range(6,66):
    gx,gy=np.polyval(cx,k),np.polyval(cy,k)
    x1,y1=int(gx-70),int(gy-70)
    sub=fr[k][max(0,y1):y1+140,max(0,x1):x1+140].astype(int)
    m=(sub.max(axis=2)<70).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4])
    if st[i,4]<300: continue
    out.append([k,cen[i][0]+max(0,x1),cen[i][1]+max(0,y1),st[i,4]])
out=np.array(out)
np.savetxt(W+'eagle_0039_dark.txt',out,fmt='%.2f')
k=out[:,0]
sel=(k<=58)&~((k>=20)&(k<=29))   # avoid person overlap
w=2*np.pi/25.5
A=np.c_[np.ones(sel.sum()),k[sel],np.sin(w*k[sel]),np.cos(w*k[sel])]
ax=np.linalg.lstsq(A,out[sel,1],rcond=None)[0]; ay=np.linalg.lstsq(A,out[sel,2],rcond=None)[0]
p1=(ax[0]+ax[1]*24,ay[0]+ay[1]*24); p2=(ax[0]+ax[1]*48,ay[0]+ay[1]*48)
print('p1',np.round(p1,1),'p2',np.round(p2,1),'px/frame',round(ax[1],2),round(ay[1],2))
print('f from eagle chord 11.84:',round(solve_f(11.84,p1,p2,179.2691,177.1009,(768,768)),1))
print(out[::4])
