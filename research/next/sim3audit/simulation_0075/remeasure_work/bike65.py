from common import *
from geom import *
from curbs import inter
V=load('simulation_0065')
bg=cv2.imread('fr/bg_simulation_0065.png').astype(np.float32)
# better background: per-pixel median over frames excluding bike; use max-diff approach: background from frames far in time
L=np.load('lines65.npy',allow_pickle=True).item()
vpM=np.mean([inter(L['M_nearR'],L['M_farL']),inter(L['M_nearR'],L['M_nearL']),inter(L['M_farL'],L['M_farR']),inter(L['M_nearL'],L['M_farR'])],0)
vpC=inter(L['C_nearR'],L['C_farR'])
f=2140; pp=(1079.5,539.5)
Kinv,d1,d2,up=make_cam(f,pp,vpM,vpC)
res=[]
for i in range(72):
    fr=V[i].astype(np.float32)
    # background for bike: use frame i-20 or i+20 (bike moved away)
    j=i+25 if i<40 else i-25
    diff=np.abs(fr-V[j].astype(np.float32)).max(2)
    # bike column region: around line from (890,620) at f0 to (855,290) at f71
    x0=int(895-0.5*i)-60; x1=x0+120
    m=diff[150:800,x0:x1]>40
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append((i,np.nan,np.nan)); continue
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    ys,xs=np.nonzero(lab==k)
    yb=ys.max(); xb=xs[ys>=yb-1].mean()
    res.append((i,xb+x0,yb+150))
res=np.array(res)
np.save('bike65_bottom.npy',res)
for r in res[::5]: print(r)
