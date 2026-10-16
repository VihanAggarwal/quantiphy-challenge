import numpy as np, json
rows=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0010/track_s.json'))
f=711.0; c0=np.array([640.0,360.0]); D=0.07
t=np.arange(49)/24.0
u=np.array([r['u'] for r in rows]); v=np.array([r['v'] for r in rows]); Dx=np.array([r['Dx'] for r in rows])
def frame(p):
    ga,gb,psi=p[4],p[5],p[6]
    g=np.array([np.sin(ga)*np.cos(gb), np.cos(ga), np.sin(ga)*np.sin(gb)])  # roughly +Y (down in camera)
    a=np.cross(g,[0,0,1.0]); a/=np.linalg.norm(a); b=np.cross(g,a)
    h=np.cos(psi)*a+np.sin(psi)*b
    return g,h
def theta(p,tt):
    th0,w,ph,eps=p[7],p[8],p[9],p[10]
    x=w*tt+ph
    return th0*np.cos(x)+eps*(np.cos(3*x)-np.cos(x)*0)  # eps: anharmonic 3rd harmonic
def pos(p,tt):
    q=p[:3]; L=p[3]; g,h=frame(p); th=theta(p,tt)
    return q[None,:]+L*(np.cos(th)[:,None]*g[None,:]+np.sin(th)[:,None]*h[None,:])
def pred(p,tt=t):
    P=pos(p,tt); uu=c0[0]+f*P[:,0]/P[:,2]; vv=c0[1]+f*P[:,1]/P[:,2]
    rng=np.linalg.norm(P,axis=1); dd=f*D/P[:,2]
    return uu,vv,dd
def resid(p):
    uu,vv,dd=pred(p)
    return np.r_[(uu-u)/0.7,(vv-v)/0.7,(dd-Dx)/1.0]
def lm(p,it=300):
    lam=1e-2
    r=resid(p); cost=r@r
    for k in range(it):
        J=np.zeros((len(r),len(p)))
        for j in range(len(p)):
            dp=np.zeros(len(p)); dp[j]=1e-6*max(1,abs(p[j]))
            J[:,j]=(resid(p+dp)-r)/dp[j]
        A=J.T@J; g=J.T@r
        while True:
            step=np.linalg.solve(A+lam*np.diag(np.diag(A)+1e-12),-g)
            pn=p+step; rn=resid(pn); cn=rn@rn
            if cn<cost: p,r,cost=pn,rn,cn; lam=max(lam/3,1e-9); break
            lam*=4
            if lam>1e9: return p,cost
    return p,cost
best=None
for w0 in [5.0,5.1,5.2]:
  for ph0 in np.linspace(0,2*np.pi,8,endpoint=False):
    for psi0 in [0.0,np.pi/2,np.pi,-np.pi/2]:
        p0=np.array([0.0,-0.19,1.46,0.34,0.0,0.0,psi0,0.6,w0,ph0,0.0])
        p,cost=lm(p0,60)
        if best is None or cost<best[1]: best=(p,cost)
p,cost=lm(best[0],400)
uu,vv,dd=pred(p)
print('cost',cost,'rms u,v,D px',np.sqrt(np.mean((uu-u)**2)),np.sqrt(np.mean((vv-v)**2)),np.sqrt(np.mean((dd-Dx)**2)))
q=p[:3]; L=p[3]; g,h=frame(p)
print('pivot',q,'pivot pix',c0+f*q[:2]/q[2],'L',L,'theta0 deg',np.degrees(p[7]),'eps',p[10],'omega',p[8],'T',2*np.pi/p[8])
print('gravity dir in cam',g,' camera tilt below horizontal (deg)',np.degrees(np.arcsin(g[2])) if True else '')
T=2*np.pi/p[8]; th0=abs(p[7])
k=1+th0**2/16+11*th0**4/3072
print('L from period (g=9.8, ampl corr)',9.8*T**2/(4*np.pi**2)/k**2)
fine=np.linspace(0,2,20001)
P=pos(p,fine)
V=np.gradient(P,fine,axis=0); A=np.gradient(V,fine,axis=0)
for tq in [0.3,0.6,0.9,1.2,1.5,1.8]:
    i=int(round(tq*10000))
    fw=[np.linalg.norm(pos(p,np.array([tq+dt]))[0]-pos(p,np.array([tq]))[0])/dt for dt in (1/24,1/25)]
    print(f't={tq}: |v|={np.linalg.norm(V[i]):.3f} |a|={np.linalg.norm(A[i]):.3f}  fwd1frame24={fw[0]:.3f} fwd25={fw[1]:.3f}  range={np.linalg.norm(P[i]):.3f}')
# turning points
sp=np.linalg.norm(V,axis=1)
from itertools import groupby
mins=[fine[i] for i in range(1,len(fine)-1) if sp[i]<sp[i-1] and sp[i]<sp[i+1]]
print('turning times',np.round(mins,3))
json.dump(dict(p=p.tolist()),open('/home/user/quantiphy-challenge/research/next/labaudit/0010/pendfit.json','w'))
