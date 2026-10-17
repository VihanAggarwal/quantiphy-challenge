import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames('simulation_0105')]
bg=np.median(np.stack(F[5:20]),axis=0)
rows=[]
for i in range(18,47):
    d=np.abs(F[i]-bg)
    d[900:]=0
    m=d>15
    ys,xs=np.where(m)
    if len(ys)<20: print(i,'none'); continue
    rows.append((i,ys.min(),ys.max(),xs.min(),xs.max(),ys.mean()))
    print(i,ys.min(),ys.max(),ys.max()-ys.min()+1,xs.min(),xs.max(),xs.max()-xs.min()+1, round(ys.mean(),2))
r=np.array(rows,float)
sel=(r[:,0]>=22)&(r[:,0]<=44)
for col,name in [(5,'cent'),(1,'top')]:
    p=np.polyfit(r[sel,0],r[sel,col],2)
    a=2*p[0]*24*24
    print(name,'a px/s2',a,'scale',9.8/a, 'vertex frame',-p[1]/(2*p[0]))
