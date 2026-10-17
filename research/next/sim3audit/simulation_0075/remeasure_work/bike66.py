from common import *
from geom import *
from curbs import inter
V=load('simulation_0066')
bg=np.median(V.astype(np.float32),axis=0)
L=np.load('lines66.npy',allow_pickle=True).item()
vp1=inter(L['R1_right'],L['R1_left_near']); vp2=inter(L['R2_top'],L['R2_bot'])
# predicted bike path: from (1035,437) at f14 to (1162,558) at f38 -> per frame (5.3,5.0)
res=[]
for i in range(72):
    cxp=1035+5.3*(i-14); cyp=437+5.04*(i-14)
    x0=int(cxp-60); y0=int(cyp-110)
    if x0<0 or y0<0 or x0+120>2160 or y0+140>1080: continue
    diff=np.abs(V[i,y0:y0+140,x0:x0+120].astype(np.float32)-bg[y0:y0+140,x0:x0+120]).max(2)
    m=(diff>30).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    ys,xs=np.nonzero(lab==k); yb=ys.max(); xb=xs[ys>=yb-1].mean()
    res.append((i,xb+x0,yb+y0,st[k,cv2.CC_STAT_AREA]))
res=np.array(res); np.save('bike66.npy',res)
print(len(res))
for f in [835,857.6,880]:
    Kinv,d1,d2,up=make_cam(f,(1079.5,539.5),vp1,vp2)
    P=np.array([ground_pt(Kinv,up,(x,y)) for _,x,y,_ in res]); 
    t=res[:,0]/24
    for lo,hi in [(14,60),(14,38),(38,62)]:
        m=(res[:,0]>=lo)&(res[:,0]<=hi)
        A=np.c_[t[m],np.ones(m.sum())]
        c1=np.linalg.lstsq(A,P[m]@d1,rcond=None)[0]; c2=np.linalg.lstsq(A,P[m]@d2,rcond=None)[0]
        vH=np.hypot(c1[0],c2[0]); r=P[m]@d1-A@c1
        print(f,lo,hi,m.sum(),'vH %.4f'%vH,'H(5.33) %.3f H(5.406) %.3f'%(5.33/vH,5.406/vH),'rms %.4f'%r.std())
