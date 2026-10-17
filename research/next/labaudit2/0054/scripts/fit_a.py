from common import *
from tracks import *

import sys
def model(p,ts,t0,gdir,g=9.81):
    C0=p[:3]; V=p[3:6]; dt=(ts-t0)[:,None]
    return C0+V*dt+0.5*g*gdir*dt**2
def proj(C,f=F): return np.stack([CX+f*C[:,0]/C[:,2], CY+f*C[:,1]/C[:,2]],1)
def fit(track, ks, gdir, t0=1.0, f=F, r_anchor=None, g=9.81):
    ts=np.array([tcap(k) for k in ks]); uv=np.array([track[k] for k in ks])
    def res(p):
        r=(proj(model(p,ts,t0,gdir,g),f)-uv).ravel()
        if r_anchor is not None:
            C=model(p,np.array([t0]),t0,gdir,g)[0]
            r=np.concatenate([r,[(np.linalg.norm(C)-r_anchor)*200]])
        return r
    u0=track[ks[0]]; p0=np.concatenate([ray(*u0)*3.0,[ -1,0,0]])
    s=least_squares(res,p0)
    return s.x, np.sqrt(np.mean(s.fun[:2*len(ks)]**2))
def gd(pitch_deg, roll_deg=0):
    p=np.radians(pitch_deg); r=np.radians(roll_deg)
    d=np.array([np.sin(r)*np.cos(p), np.cos(r)*np.cos(p), np.sin(p)]); return d/np.linalg.norm(d)
if __name__=='__main__':
    for name,tr,ks in [('white',A_W,list(range(24,36))+[36,37]),('green',A_G_raw,list(range(24,36))+[36])]:
        for pitch in [-2,0,1,2,4]:
            p,rms=fit(tr,ks,gd(pitch))
            C=lambda t: model(p,np.array([t]),1.0,gd(pitch))[0]
            rng=lambda t: np.linalg.norm(C(t))
            v=lambda t: np.linalg.norm(p[3:6]+9.81*gd(pitch)*(t-1.0))
            print(f'{name} pitch={pitch} rms={rms:.2f} range(1.0)={rng(1.0):.3f} r(1.52)={rng(1.52):.3f} |v|(1.0)={v(1.0):.2f} v(1.04)={v(1.04):.2f} v(1.5)={v(1.5):.2f} v(1.52)={v(1.52):.2f} fd25-26={np.linalg.norm(C(1.04)-C(1.0))*25:.2f} fd38-39={np.linalg.norm(C(1.56)-C(1.52))*25:.2f} fd37-38={np.linalg.norm(C(1.52)-C(1.48))*25:.2f}')
