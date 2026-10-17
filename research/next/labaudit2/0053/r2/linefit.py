import numpy as np, json
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def proj(P): return np.stack([f*P[...,0]/P[...,2]+cx, f*P[...,1]/P[...,2]+cy],-1)
T=json.load(open('bintrack.json'))
def cap(i): return i + (1 if i>=12 else 0) + (1 if i>=36 else 0)
uv=np.array([[t['cx'],t['cy']] for t in T]); tc=np.array([cap(i) for i in range(48)])/25.
P10=2.73*ray(*uv[10])
t0=0.4
def model(p,tt):
    th,ph,v,a,j=p
    D=np.array([np.cos(ph)*np.sin(th), np.sin(ph), np.cos(ph)*np.cos(th)])
    dt=tt-t0
    s=v*dt-0.5*a*dt**2 + j*dt**3/6
    return P10[None,:]+s[:,None]*D[None,:], D
def resid(p,sel):
    P,_=model(p,tc[sel]); return (proj(P)-uv[sel]).ravel()
# simple Gauss-Newton / LM with numeric jacobian
def lm(p,sel,iters=200):
    p=np.array(p,float); lam=1e-3
    for _ in range(iters):
        r=resid(p,sel); J=np.zeros((len(r),len(p)))
        for k in range(len(p)):
            dp=np.zeros(len(p)); dp[k]=1e-6
            J[:,k]=(resid(p+dp,sel)-r)/1e-6
        H=J.T@J; g=J.T@r
        step=np.linalg.solve(H+lam*np.diag(np.diag(H)+1e-12),-g)
        if np.sum(resid(p+step,sel)**2)<np.sum(r**2): p=p+step; lam*=0.3
        else: lam*=10
    return p, np.sqrt(np.mean(resid(p,sel)**2))
for name,sel,jerk in [('all, const decel',np.arange(48),False),('all, +jerk',np.arange(48),True),('frames 3-47',np.arange(3,48),False),('frames 5-40',np.arange(5,41),False)]:
    best=None
    for th0 in np.radians([-60,-40,-20]):
        for ph0 in np.radians([-30,-15,0]):
            p0=[th0,ph0,1.0,0.3,0.0]
            if not jerk:
                # freeze jerk by wrapping
                def resid2(q,sel=sel): return resid(np.r_[q,0.],sel)
                pp=np.array(p0[:4]); 
                # reuse lm with frozen jerk
                global_resid=resid
                def lm4(p,iters=200):
                    p=np.array(p,float); lam=1e-3
                    for _ in range(iters):
                        r=resid2(p); J=np.zeros((len(r),len(p)))
                        for k in range(len(p)):
                            dp=np.zeros(len(p)); dp[k]=1e-6; J[:,k]=(resid2(p+dp)-r)/1e-6
                        H=J.T@J; g=J.T@r
                        step=np.linalg.solve(H+lam*np.diag(np.diag(H)+1e-12),-g)
                        if np.sum(resid2(p+step)**2)<np.sum(r**2): p=p+step; lam*=0.3
                        else: lam*=10
                    return np.r_[p,0.], np.sqrt(np.mean(resid2(p)**2))
                p,rms=lm4(pp)
            else:
                p,rms=lm(p0,sel)
            if best is None or rms<best[1]: best=(p,rms)
    p,rms=best
    P,D=model(p,np.array([0.4,1.4]))
    disp=np.linalg.norm(P[1]-P[0])
    print(f'{name:20s} rms {rms:.3f}px  v0.4 {p[2]:.3f} a {p[3]:.3f} jerk {p[4]:.3f} D {np.round(D,3)} range@1.4 {np.linalg.norm(P[1]):.3f} disp {disp:.3f}')
    for nm,n in [('depthfit',np.array([0.0195,-0.7941,-0.6074])),('vertVP',np.load('normals.npy')[1]),('horizon',np.load('normals.npy')[0])]:
        print(f'      angle D vs floor ({nm}) {np.degrees(np.arcsin(abs(D@n))):.1f} deg')
