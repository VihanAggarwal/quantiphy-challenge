import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0117')
bg=np.median(np.stack(F),axis=0)
ys=[];ts=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(float)-bg).sum(2)
    m=(d>30).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i,x,y,w,h,a,np.round(cen[k],1))
    if y>2 and y+h<1915: ys.append(cen[k][1]); ts.append(i)
ts=np.array(ts);ys=np.array(ys)
p=np.polyfit(ts/24.0,ys,2); print('fit',p,'acc px/s2',2*p[0],'scale',9.8/(2*p[0]))
r=ys-np.polyval(p,ts/24.0); print('rms',r.std())
