from common import *
import numpy as np, json
from lsq import least_squares
M=json.load(open(OUT+'ax_moments.json'))
cap=lambda i: int(np.floor(i*25/24+0.5))
f=711.; cx,cy=640.,360.
down=np.load(OUT+'down.npy')
obs={'white':[], 'green':[]}
for r in M: obs[r['obj']].append((r['i'],r['x'],r['y'],r['Dmin']))
obs['green'].append((24,599.5,291.9,np.nan))
for k in obs: obs[k]=sorted(obs[k])
def proj(P): return np.c_[f*P[:,0]/P[:,2]+cx, f*P[:,1]/P[:,2]+cy]
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
anchor={'white':3.0735,'green':3.039}
rad={'white':0.0365,'green':0.0335}
def traj(p,t,g=9.8,gd=down):
    P0=p[:3]; V0=p[3:6]
    return P0[None]+V0[None]*t[:,None]+0.5*g*gd[None]*t[:,None]**2
def fit(name, imax, use_anchor=True, g=9.8, gd=down, tref=25):
    o=[x for x in obs[name] if x[0]<=imax]
    I=np.array([x[0] for x in o]); J=np.array([cap(i) for i in I]); uv=np.array([[x[1],x[2]] for x in o])
    t=(J-tref)/25.
    rc=anchor[name]+rad[name]
    def res(p):
        P=traj(p,t,g,gd); r=(proj(P)-uv).ravel()
        if use_anchor:
            r=np.r_[r, (np.linalg.norm(traj(p,np.array([(25-tref)/25.]),g,gd)[0])-rc)*200]
        return r
    k0=int(np.argmin(abs(J-25))); P24=ray(*uv[k0])*rc
    p0=np.r_[P24,[-1,-3,-2]]
    s=least_squares(res,p0)
    P=traj(s.x,t,g,gd)
    return s,I,J,uv,P
for name,imax in (('white',37),('green',36)):
    for ua in (True,False):
        s,I,J,uv,P=fit(name,imax,ua)
        r=(proj(P)-uv)
        print(name,'anchor' if ua else 'free','rms px',np.sqrt((r**2).mean()).round(2),'P(c25)',s.x[:3].round(3),'range',np.linalg.norm(s.x[:3]).round(3),'V0',s.x[3:].round(2))
        if ua:
            for k in range(len(I)):
                print('   v%d c%d uv=(%.1f,%.1f) res=(%.1f,%.1f) Z=%.3f rng=%.3f h_below_cam=%.3f'%(I[k],J[k],uv[k,0],uv[k,1],r[k,0],r[k,1],P[k,2],np.linalg.norm(P[k]),P[k]@down))
