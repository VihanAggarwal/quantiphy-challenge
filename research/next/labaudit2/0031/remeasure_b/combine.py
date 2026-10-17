import cv2, numpy as np, json
f=775.
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
E={t:json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/edge_%s.json'%t)) for t in 'asx'}
P=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/corners.npy')
W,D=60.3,76.0
obj=np.array([[-W/2,D,0],[W/2,D,0],[W/2,0,0],[-W/2,0,0]],float)
K=np.array([[f,0,640],[0,f,360],[0,0,1]])
ok,rv,tv=cv2.solvePnP(obj,P,K,None,flags=cv2.SOLVEPNP_IPPE)
Rm,_=cv2.Rodrigues(rv); C=(-Rm.T@tv).ravel()
Rb={'t':3.35,'w':2.0}
def ray(u,v):
    d=np.array([(u-640)/f,(v-360)/f,1.]); return d/np.linalg.norm(d)
def robust_line(x,y,it=5):
    w=np.ones_like(y)
    for _ in range(it):
        p=np.polyfit(x,y,1,w=w); r=y-np.polyval(p,x); s=1.4826*np.median(np.abs(r))+1e-6
        w=np.clip(1.5*s/np.maximum(np.abs(r),1e-9),0,1)
    return p
for b,lo,hi in (('t',22,43),('t',28,43),('t',33,43),('w',22,50),('w',30,50),('w',36,46)):
    rows=[]
    for k in range(49):
        vals=[E[t][k][b] for t in 'asx' if b in E[t][k]]
        if not vals: continue
        c=cap(k)
        if c<lo or c>hi: continue
        u=np.median([v[0] for v in vals]); v=np.median([v[1] for v in vals]); r=np.median([v[2] for v in vals])
        d=ray(u,v)
        Rc_s=Rb[b]/np.sin(np.arctan(r/f*d[2]))   # first-order off-axis correction
        dw=Rm.T@d; s=(Rb[b]-C[2])/dw[2]
        Pg=(s-Rb[b])*d; Ps=(Rc_s-Rb[b])*d   # surface point along centre ray (label-style)
        rows.append((c,*Pg,*Ps))
    A=np.array(rows); c=A[:,0]
    vg=25*np.linalg.norm([robust_line(c,A[:,j])[0] for j in (1,2,3)])
    vs=25*np.linalg.norm([robust_line(c,A[:,j])[0] for j in (4,5,6)])
    print('%s [%d-%d] label-style surface-point speed: ground-route %.1f cm/s, size-route %.1f cm/s  (n=%d)'%(b,lo,hi,vg,vs,len(c)))
