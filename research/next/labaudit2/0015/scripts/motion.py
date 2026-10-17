# Label-style emulation for v(0.6) and v(2.6): clicked toy centre per capture frame, back-projected at the toy range,
# forward difference on the 25 fps capture clock (video k -> capture k+1 for 12..35, k+3 for >=60).
import numpy as np
from common import F, CX, CY, cap
def P(u,v,Z):  # point at depth Z on the click ray
    return np.array([(u-CX)/F*Z,(v-CY)/F*Z,Z])
# centre definitions (u,v) per video frame
C={
 # toss-1 release: video 14 = capture 15 (t=0.60), video 15 = capture 16
 'r_manual_visible': {14:(450,232.5),15:(447,214.5),16:(445,200)},   # mid of visible top/bottom, 3x grid (x and o agree)
 'r_top_plus_46'   : {14:(448.5,192+46),15:(447,169+46),16:(442.5,152+46)},  # top edge (x render) + half flight length
 'r_top_only'      : {14:(448.5,192),15:(447,169),16:(442.5,152)},
 # catch: video 62 = capture 65 (t=2.60), video 63 = capture 66
 'c_seg_o_centroid': {61:(434.6,284.7),62:(433.7,307.5),63:(430.4,325.3),64:(428.5,340.1)},
 'c_seg_o_bbox'    : {61:(432.0,280.5),62:(434.0,309.5),63:(432.0,327.5),64:(432.0,343.5)},
 'c_seg_x_centroid': {61:(439.8,270.8),62:(430.8,307.0),63:(429.4,324.2),64:(426.8,339.7)},
 'c_manual_x'      : {61:(438,277),62:(436,310),63:(432,327),64:(430,342)},
 'c_manual_o'      : {61:(437,275),62:(437,308),63:(433,328),64:(433,342)},
 'c_topbot_o'      : {62:(436,(272+345)/2),63:(433,(288+370)/2)},
}
def fwd(c,k,Z): return np.linalg.norm(P(*c[k+1],Z)-P(*c[k],Z))*25*100/(cap(k+1)-cap(k))
print('deterministic label-style speeds (cm/s), Z = toy depth')
for name,c in C.items():
    k=14 if name.startswith('r_') else 62
    row=[f'{fwd(c,k,Z):6.1f}' for Z in (2.10,2.20,2.30)]
    extra=''
    if k==62 and 61 in c: extra=f'   backward(61->62) at Z2.2: {fwd(c,61,2.2):6.1f}   central: {0.5*(fwd(c,61,2.2)+fwd(c,62,2.2)):6.1f}'
    if k==14 and 16 in c: extra=f'   next step(15->16) at Z2.2: {fwd(c,15,2.2):6.1f}'
    print(f'{name:18s} k={k}  Z2.10/2.20/2.30: {" ".join(row)}{extra}')
# Monte Carlo of the label process: click sigma 2 px, ToF (range) sigma 0/1/2/3 cm, optional true depth motion dZ per frame
rng=np.random.default_rng(0)
def mc(c,k,Z,sz,dZ=0.0,n=20000):
    out=[]
    u0,v0=c[k]; u1,v1=c[k+1]
    p0=P(u0,v0,Z); p1=P(u1,v1,Z+dZ)
    r0=np.linalg.norm(p0); r1=np.linalg.norm(p1)
    uu0=u0+rng.normal(0,2,n); vv0=v0+rng.normal(0,2,n); uu1=u1+rng.normal(0,2,n); vv1=v1+rng.normal(0,2,n)
    rr0=r0+rng.normal(0,sz,n); rr1=r1+rng.normal(0,sz,n)
    def bp(u,v,r):
        d=np.stack([(u-CX)/F,(v-CY)/F,np.ones_like(u)],1); d/=np.linalg.norm(d,axis=1,keepdims=True); return d*r[:,None]
    L=np.linalg.norm(bp(uu1,vv1,rr1)-bp(uu0,vv0,rr0),axis=1)*25*100/(cap(k+1)-cap(k))
    return np.median(L),L.mean(),np.percentile(L,[16,84])
print('\nMC label distribution (median, mean, 16-84%), Z=2.2')
for name,k in [('r_manual_visible',14),('r_top_plus_46',14),('c_manual_x',62),('c_manual_o',62),('c_seg_o_bbox',62)]:
    for sz in (0.0,0.01,0.02,0.03):
        for dZ in (0.0,0.02):
            m,mu,q=mc(C[name],k,2.2,sz,dZ)
            print(f'{name:18s} sigma_z {sz:.2f} dZ/frame {dZ:.2f}: median {m:6.1f} mean {mu:6.1f}  [{q[0]:6.1f},{q[1]:6.1f}]')
