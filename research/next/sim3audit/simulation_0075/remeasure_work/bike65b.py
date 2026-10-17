from common import *
from geom import *
from curbs import inter
V=load('simulation_0065')
bg=np.median(V.astype(np.float32),axis=0)
L=np.load('lines65.npy',allow_pickle=True).item()
vpM=np.mean([inter(L['M_nearR'],L['M_farL']),inter(L['M_nearR'],L['M_nearL']),inter(L['M_farL'],L['M_farR']),inter(L['M_nearL'],L['M_farR'])],0)
vpC=inter(L['C_nearR'],L['C_farR'])
res=[]
for i in range(72):
    diff=np.abs(V[i].astype(np.float32)-bg).max(2)
    x0=int(895-0.55*i)-70; x1=x0+140
    m=(diff[150:800,x0:x1]>35).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append((i,np.nan,np.nan)); continue
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    ys,xs=np.nonzero(lab==k)
    yb=ys.max(); xb=xs[ys>=yb-1].mean()
    res.append((i,xb+x0,yb+150, st[k,cv2.CC_STAT_AREA]))
res=np.array(res)
np.save('bike65_bottom.npy',res)
for r in res[::3]: print(np.round(r,1))
