from common import *
from geom import *
from curbs import inter
V=load('simulation_0066')
bg=np.median(V.astype(np.float32),axis=0)
L=np.load('lines66.npy',allow_pickle=True).item()
vp1=inter(L['R1_right'],L['R1_left_near']); vp2=inter(L['R2_top'],L['R2_bot'])
diff_all=None
res=[]
for i in range(0,72):
    d=np.abs(V[i].astype(np.float32)-bg).max(2)
    m=(d>40).astype(np.uint8)
    m[:200]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # van: white blob; choose component with brightest mean & large area near predicted
    best=None
    for k in range(1,n):
        if st[k,cv2.CC_STAT_AREA]<2000: continue
        ys,xs=np.nonzero(lab==k)
        bright=V[i][ys,xs].mean()
        if bright>170 and (best is None or st[k,cv2.CC_STAT_AREA]>best[0]): best=(st[k,cv2.CC_STAT_AREA],k,xs,ys)
    if best is None: continue
    _,k,xs,ys=best
    res.append((i,xs.min(),xs.max(),ys.min(),ys.max(),len(xs)))
res=np.array(res); np.save('van66_blob.npy',res)
for r in res[::4]: print(r)
