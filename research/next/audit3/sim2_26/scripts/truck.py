import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0187')
bg0=F[0].astype(float); bgL=F[59].astype(float)
fr=[];rr=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(float)-bg0).sum(2)
    m=d[300:900]>45
    cols=np.nonzero(m.sum(0)>8)[0]
    cols=cols[cols>40]
    front=cols.max() if len(cols) else -1
    d2=np.abs(f.astype(float)-bgL).sum(2)
    m2=d2[300:900]>45
    c2=np.nonzero(m2.sum(0)>8)[0]
    c2=c2[c2<1880]
    rear=c2.min() if len(c2) else -1
    fr.append(front); rr.append(rear)
    print(i,front,rear)
