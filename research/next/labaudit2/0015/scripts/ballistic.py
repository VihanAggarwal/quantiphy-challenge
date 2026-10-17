# 3D ballistic fit of toy features on the 25 fps capture clock; scale from g = 9.8 m/s^2
import json, numpy as np
from lsq import least_squares
from common import F, CX, CY, cap
g=9.8
def down(pitch_deg, roll_deg=0.0):
    p=np.radians(pitch_deg); r=np.radians(roll_deg)
    # camera looking down by pitch p: world down expressed in camera frame (x right, y down, z forward)
    d=np.array([0.0, np.cos(p), -np.sin(p)])
    # roll about z
    R=np.array([[np.cos(r),-np.sin(r),0],[np.sin(r),np.cos(r),0],[0,0,1]])
    return R@d
def fit(frames, uv, pitch=0.0, fix_vz=None):
    t=np.array([cap(k) for k in frames])/25.0; t0=t.mean(); tt=t-t0
    uv=np.asarray(uv,float); gv=g*down(pitch)
    def proj(p):
        P=p[:3][None]+p[3:6][None]*tt[:,None]+0.5*gv[None]*tt[:,None]**2
        return np.c_[F*P[:,0]/P[:,2]+CX, F*P[:,1]/P[:,2]+CY], P
    def res(p):
        if fix_vz is not None: p=np.r_[p[:5],fix_vz]
        return (proj(p)[0]-uv).ravel()
    Z0=2.2; u0,v0=uv.mean(0)
    p0=np.array([(u0-CX)/F*Z0,(v0-CY)/F*Z0,Z0,0,0,0])
    if fix_vz is not None: p0=p0[:5]
    s=least_squares(res,p0)
    p=s.x if fix_vz is None else np.r_[s.x,fix_vz]
    uvh,P=proj(p)
    return p, P, np.sqrt(np.mean(s.fun**2)), t
if __name__=='__main__':
    gx=json.load(open('../gtrack_x.json'))
    tops={}
    for line in open('../tops_x.txt'):
        a=line.split(); tops[int(a[0])]=int(a[3])
    for name,rng in [('toss1',range(17,23)),('toss2',range(53,59))]:
        fr=[k for k in rng]; 
        for feat in ['c','top','bot','bbox']:
            if feat=='c': uv=[(gx[str(k)]['cx'],gx[str(k)]['cy']) for k in fr]
            elif feat=='top': uv=[(gx[str(k)]['cx'],gx[str(k)]['t']) for k in fr]
            elif feat=='bot': uv=[(gx[str(k)]['cx'],gx[str(k)]['b']) for k in fr]
            else: uv=[((gx[str(k)]['l']+gx[str(k)]['r'])/2,(gx[str(k)]['t']+gx[str(k)]['b'])/2) for k in fr]
            for pitch in [0.0,3.0,-3.0]:
                for fz in [None,0.0]:
                    p,P,rms,t=fit(fr,uv,pitch,fz)
                    rng_=np.linalg.norm(P,axis=1)
                    print(f'{name} {feat:4s} pitch {pitch:+.0f} vz {"free" if fz is None else "0":4s}: Z {P[:,2].mean():.3f} range {rng_.mean():.3f} V=({p[3]:+.2f},{p[4]:+.2f},{p[5]:+.2f}) rms {rms:.2f}px')
    # long top-only fits (vertical image coordinate only matters)
    for name,rng in [('toss1top',range(15,23)),('toss2top',range(50,60))]:
        fr=list(rng); uv=[(440.0,tops[k]) for k in fr]
        for pitch in [0.0]:
            p,P,rms,t=fit(fr,uv,pitch,0.0)
            print(f'{name} pitch {pitch}: Z {P[:,2].mean():.3f} rms {rms:.2f}', 'res', np.round(np.array([F*q[1]/q[2]+CY for q in P])-np.array([u[1] for u in uv]),1))
