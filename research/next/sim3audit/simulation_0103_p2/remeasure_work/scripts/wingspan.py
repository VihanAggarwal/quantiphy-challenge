import numpy as np, cv2, sys
from reg import *
from vio import load
v=sys.argv[1]; cname=sys.argv[2]; D1,D2=float(sys.argv[3]),float(sys.argv[4]); trk=sys.argv[5]
over=eval(sys.argv[6]) if len(sys.argv)>6 else {}
thr=int(sys.argv[7]) if len(sys.argv)>7 else 70
F=frame_of(cname,**over)
fr=load(v)
o=np.loadtxt(W+trk)
res=[]
for row in o:
    k=int(row[0]); x,y=row[1],row[2]
    if k<4 or k>=len(fr): continue
    D=D1+(D2-D1)*(k-24)/24.0
    Pe=to_boat(F,F['cam'].pt(x,y,D)); ze=Pe[2]
    half=90
    x1,y1=int(x)-half,int(y)-half
    sub=fr[k][max(0,y1):y1+2*half,max(0,x1):x1+2*half].astype(int)
    m=(sub.max(axis=2)<thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==i)
    us=xs+max(0,x1); vs=ys+max(0,y1)
    Cb=F['C']; d=(F['cam'].ray(us,vs))@F['M'].T
    t=(ze-Cb[2])/d[:,2]; G=Cb+t[:,None]*d
    res.append((k, np.ptp(G[:,0]), np.ptp(G[:,1]), ze, st[i,4]))
res=np.array(res)
np.set_printoptions(suppress=True,precision=2,linewidth=150)
print(res)
print('max Y-extent %.2f at k=%d ; median X-extent %.2f'%(res[:,2].max(),res[res[:,2].argmax(),0],np.median(res[:,1])))
