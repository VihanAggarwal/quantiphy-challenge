import numpy as np, itertools
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
ball=ray(985.9,369.6)*(2.925+0.116)
book=ray(665,614)*2.082
cup=ray(565,425)*2.516
binp=ray(797.8,379.4)*2.73
N=np.load('normals.npy')
def solve(P,h):
    # n.P_i + H = h_i, |n|=1 ; 3 points -> plane through points shifted... solve via plane fit to points P_i with offsets
    # parametrize n by pitch,roll ; grid search
    best=None
    for pitch in np.arange(20,60,0.1):
        for roll in np.arange(-20,20,0.1):
            p,r=np.radians(pitch),np.radians(roll)
            n=np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
            d=[n@Pi for Pi in P]; Hs=[hi-di for hi,di in zip(h,d)]
            err=np.std(Hs)
            if best is None or err<best[0]: best=(err,pitch,roll,np.mean(Hs),n)
    return best
for hb,hc in itertools.product([0.02,0.035],[0.05,0.08]):
    e,p,r,H,n=solve([ball,book,cup],[0.116,hb,hc])
    print(f'book {hb} cup {hc}: pitch {p:.1f} roll {r:.1f} H {H:.3f} resid {e:.4f}  bin click height {n@binp+H:.3f}')
for nm,n in zip(['horizon','vertVP'],N):
    p=np.degrees(np.arcsin(-n[2])); r=np.degrees(np.arcsin(n[0]/np.cos(np.radians(p))))
    print(nm,'pitch',p,'roll',r)
