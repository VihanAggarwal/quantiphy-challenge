import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *
fr=frames('simulation_0044')
stack=np.stack([fr[i].astype(np.float32) for i in sorted(fr)])
bg=np.median(stack,0)
res={}
for i in sorted(fr):
    d=(np.abs(stack[i]-bg).sum(2)>90)&(stack[i].sum(2)<300)  # dark eagle
    d=cv2.morphologyEx(d.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(d)
    comps=sorted([(st[k][4],k) for k in range(1,n) if st[k][4]>10],reverse=True)
    res[i]=[(round(cen[k][0],1),round(cen[k][1],1),a,tuple(int(v) for v in st[k][:4])) for a,k in comps[:3]]
for i in sorted(res):
    if i%3==0: print(i,res[i])
# eagle track = component continuing the left track
tr={}
prev=None
for i in sorted(res):
    c=[r for r in res[i]]
    if not c: continue
    if prev is None:
        cand=min(c,key=lambda r:r[0])
    else:
        cand=min(c,key=lambda r:(r[0]-prev[0]-10.3)**2+(r[1]-prev[1])**2)
        if (cand[0]-prev[0]-10.3)**2+(cand[1]-prev[1])**2>15**2: continue
    tr[i]=cand; prev=cand
t=np.array(sorted(tr)); x=np.array([tr[i][0] for i in t]); y=np.array([tr[i][1] for i in t])
print(len(t), t.min(), t.max())
best=None
for per in np.arange(18,32,0.5):
    w=2*np.pi/per
    A=np.stack([np.ones_like(t),t,t**2,np.sin(w*t),np.cos(w*t)],1)
    r=np.linalg.lstsq(A,y,rcond=None)[1]
    if best is None or r[0]<best[0]: best=(r[0],per)
per=best[1]; w=2*np.pi/per; print('period',per)
A=np.stack([np.ones_like(t),t,t**2,np.sin(w*t),np.cos(w*t)],1)
cx=np.linalg.lstsq(A,x,rcond=None)[0]; cy=np.linalg.lstsq(A,y,rcond=None)[0]
ev=lambda c,tt: c[0]+c[1]*tt+c[2]*tt**2
print('resid',np.std(x-A@cx),np.std(y-A@cy))
p1=(ev(cx,24),ev(cy,24)); p2=(ev(cx,48),ev(cy,48)); print(p1,p2)
import math
for conv in ['range','z']:
    f=solve_f(p1,p2,175.3081,172.9881,11.90374239425132,540,540,conv)
    P1=P3(p1,175.3081,f,540,540,conv); P2=P3(p2,172.9881,f,540,540,conv); vv=P2-P1
    print(conv,round(f,1),np.round(vv,3),'pitch(level)',round(math.degrees(math.atan2(-vv[1],vv[2])),2))
