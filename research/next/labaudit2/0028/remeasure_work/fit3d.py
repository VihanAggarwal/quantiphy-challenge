import numpy as np, json
import sys; sys.path.insert(0,"research/next/labaudit2/0028/remeasure_work"); from lm import least_squares
W='research/next/labaudit2/0028/remeasure_work'
tr=json.load(open(f'{W}/track_captured_0028x.json'))
f=711.; g=9.81
def cap(k): return k + (k>=12) + (k>=36)
def fit(frames, cx=640., cy=360., pitch=0.0):
    t=np.array([cap(k) for k in frames],float)/25.
    t0=t[0]; t=t-t0
    u=np.array([tr[k]['cx'] for k in frames]); v=np.array([tr[k]['cy'] for k in frames])
    gc=g*np.array([0,np.cos(pitch),np.sin(pitch)])
    def model(p):
        P0=p[:3]; V=p[3:6]
        P=P0[None]+V[None]*t[:,None]+0.5*gc[None]*t[:,None]**2
        return cx+f*P[:,0]/P[:,2], cy+f*P[:,1]/P[:,2], P
    def res(p):
        a,b,_=model(p); return np.r_[a-u,b-v]
    best=None
    for Z0 in [1.0,1.4,1.8]:
        for Vz in [-1,0,1]:
            p0=np.array([(u[0]-cx)*Z0/f,(v[0]-cy)*Z0/f,Z0,0,-1,Vz])
            r=least_squares(res,p0)
            if best is None or r.cost<best.cost: best=r
    a,b,P=model(best.x)
    rms=np.sqrt(np.mean(res(best.x)**2))
    return best.x, rms, P, t+t0
for name,frames in [('arc2',list(range(27,36))),('arc2b',list(range(28,35))),('arc3',list(range(37,46))),('arc3b',list(range(38,45))),('arc1',list(range(22,26)))]:
    for cy in [360.,351.]:
        p,rms,P,t=fit(frames,cy=cy)
        print(name,'cy',cy,'rms %.2f'%rms,'P0',np.round(p[:3],3),'V',np.round(p[3:],3), 'Z range %.3f..%.3f'%(P[0,2],P[-1,2]))
