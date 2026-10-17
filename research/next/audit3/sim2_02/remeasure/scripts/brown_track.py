import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=860
F=frames('simulation_0240',Y0,1070)[:49]
rows=[]
for k in range(49):
    f=F[k][:,100:560]
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    B,G,R=[f[...,i].astype(int) for i in range(3)]
    m=((hsv[...,1]>105)&(hsv[...,0]<=20)&(R-G>35)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    i=1+np.argmax(st[1:,4]); M=(lab==i)
    ys,xs=np.nonzero(M)
    # torso band rows 935-965 (abs)
    band=M[935-Y0:965-Y0]
    bx=np.nonzero(band.any(axis=0))[0]
    # per-row extents in band, median
    lefts=[np.nonzero(r)[0].min() for r in band if r.any()]
    rights=[np.nonzero(r)[0].max() for r in band if r.any()]
    by,bxx=np.nonzero(band)
    rows.append((k,100+xs.mean(),100+np.median(lefts),100+np.median(rights),100+bxx.mean(),100+xs.min(),100+xs.max(),Y0+ys.min(),Y0+ys.max(),M.sum()))
A=np.array(rows)
np.set_printoptions(suppress=True,precision=1,linewidth=160)
print(A[::4])
k=A[:,0]
for j,name in [(1,'centroid all'),(2,'rump edge band'),(3,'front edge band'),(4,'band centroid'),(5,'xmin'),(6,'xmax (head)')]:
    p=np.polyfit(k,A[:,j],1); r=A[:,j]-np.polyval(p,k)
    print(f'{name:16s} slope {p[0]:.3f} resid {r.std():.2f}  half1 {np.polyfit(k[:25],A[:25,j],1)[0]:.3f} half2 {np.polyfit(k[24:],A[24:,j],1)[0]:.3f}')
np.savetxt('brown_track.txt',A,fmt='%.2f')
