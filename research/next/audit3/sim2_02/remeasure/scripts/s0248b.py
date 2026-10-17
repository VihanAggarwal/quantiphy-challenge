import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
F=frames('simulation_0248',n=49)
np.set_printoptions(suppress=True,precision=2,linewidth=160)
bg=np.median(F,axis=0).astype(np.int16)
out=[]
for k in range(49):
    f=F[k].astype(np.int16)
    hsv=cv2.cvtColor(F[k],cv2.COLOR_BGR2HSV).astype(int)
    m=(hsv[...,1]>45).astype(np.uint8)
    # rabbit window: rows 590-645, columns near rabbit
    xs_guess=1030+6.0*k
    x0=int(xs_guess-60); x1=int(xs_guess+60)
    sub=m[590:645,x0:x1]
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub)
    if n<2: continue
    i=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[i]
    out.append((k,x0+x,590+y,w,h,a,x0+cen[i][0],590+cen[i][1]))
A=np.array(out)
print(A[::6])
kk=A[:,0]
print('rabbit cx slope',np.polyfit(kk,A[:,6],1),'xmin',np.polyfit(kk,A[:,1],1)[0],'xmax',np.polyfit(kk,A[:,1]+A[:,3],1)[0])
print('w med',np.median(A[:,3]),'mean',A[:,3].mean(),'p90',np.percentile(A[:,3],90),'h med',np.median(A[:,4]),'bottom med',np.median(A[:,2]+A[:,4]-1))
# save a few crops
outs=[]
for k in [0,12,24,36]:
    xs=int(1030+6.0*k)
    c=F[k][585:645,xs-50:xs+50]
    outs.append(cv2.resize(c,None,fx=5,fy=5,interpolation=cv2.INTER_CUBIC))
cv2.imwrite('rab0248.png',np.vstack(outs))
