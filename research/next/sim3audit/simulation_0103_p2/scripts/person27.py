import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from vhull import *
from footprint import to_ground
fr=frames('simulation_0027_segmented')
tr={}
for i in sorted(fr):
    m=fgmask(fr[i]); m[:320]=False; m[:, :350]=False; m[:, 520:]=False
    n,l,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n<2: continue
    k=1+np.argmax(st[1:,4]); ys,xs=np.where(l==k)
    # feet: lowest 4 rows mean x
    yb=ys.max(); sel=ys>=yb-3
    tr[i]=(xs[sel].mean(), yb+0.5, xs.mean(), ys.mean(), ys.min(), yb)
t=np.array(sorted(tr)); F=np.array([tr[i] for i in t])
# smooth with linear fit over windows to remove gait
def lin(col,a,b):
    s=(t>=a)&(t<=b); c=np.polyfit(t[s],F[s,col],1); return c
for col,name in [(0,'feet x'),(1,'feet y'),(2,'cx'),(3,'cy')]:
    c=np.polyfit(t,F[:,col],1); print(name,'slope px/frame %.3f'%c[0], 'resid %.2f'%np.std(F[:,col]-np.polyval(c,t)))
cxf=np.polyfit(t,F[:,0],1); cyf=np.polyfit(t,F[:,1],1)
p1=(np.polyval(cxf,24),np.polyval(cyf,24)); p2=(np.polyval(cxf,48),np.polyval(cyf,48))
print('feet t1',np.round(p1,1),'t2',np.round(p2,1),'height px (mask, head missing)',np.mean(F[:,5]-F[:,4]))
for prm in [dict(fA=3460,pA=18.7,fC=3870,pC=53.0),dict(fA=3401,pA=18.7,fC=3870,pC=53.0),dict(fA=3517,pA=18.7,fC=3870,pC=53.0),dict(fA=3460,pA=17.7,fC=3870,pC=53.0),dict(fA=3460,pA=19.7,fC=3870,pC=53.0)]:
    A,C=build(prm)
    out=[]
    for z0 in [-1.0,0.0,1.1]:
        G1=to_ground(A,*p1,z0); G2=to_ground(A,*p2,z0); out.append('z0 %.1f: speed %.3f (dX %.2f dY %.2f) range_feet %.1f'%(z0,np.linalg.norm(G2-G1),*(G2-G1)[:2],np.linalg.norm(G1-A.to_W(A.cam.C))))
    print(prm['fA'],prm['pA'],' | '.join(out))
