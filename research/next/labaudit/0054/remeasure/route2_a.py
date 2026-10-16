# Route 2: camera-a-only ballistic fit. Gravity = +y in camera a (all wall seams exactly vertical in a => no pitch/roll),
# |g| = 9.81 sets the metric scale (no labels, no camera b). Timing: orig 25 fps, video frames 12 and 36 skip one orig frame.
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
import numpy as np
from pts import aW,aG
from vel import orig
from ba import lm
F=711.; C=np.array([640.,360.])
gvec=np.array([0,9.81,0.])
def proj(P): return F*P[:,:2]/P[:,2:3]+C
def fit(track,ks,k0):
    tau=np.array([(orig(k)-orig(k0))/25 for k in ks]); obs=np.array([track[k] for k in ks],float)
    def model(p): 
        P0=p[:3]; V0=p[3:6]
        return P0[None]+V0[None]*tau[:,None]+0.5*gvec[None]*tau[:,None]**2
    def res(p): return (proj(model(p))-obs).ravel()
    u,v=track[k0]; d=np.array([u-C[0],v-C[1],F]); d/=np.linalg.norm(d)
    best=None
    for z0 in [2.0,2.5,3.0,3.5,4.0]:
        p0=np.r_[d*z0,[0,-1,-1.]]
        p,r=lm(res,p0,iters=200)
        c=(r**2).sum()
        if best is None or c<best[0]: best=(c,p,r)
    c,p,r=best
    return p,np.sqrt((r.reshape(-1,2)**2).sum(1).mean()),model,tau
for nm,tr,ks in [('W',aW,list(range(25,38))),('G',aG,list(range(25,37)))]:
    k0=ks[0]
    p,rms,model,tau=fit(tr,ks,k0)
    P0=p[:3];V0=p[3:6]
    def pos(t): return P0+V0*t+0.5*gvec*t*t
    def vel(t): return V0+gvec*t
    t24=(orig(24)-orig(k0))/25
    print(f'{nm}: rms {rms:.2f}px; range at video24 (t=1.0) = {np.linalg.norm(pos(t24)):.3f} m centre (label surf+r = {3.0735+0.0335 if nm=="W" else 3.039+0.0335:.3f})')
    for k in [35,36,37]:
        tk=(orig(k)-orig(k0))/25
        print(f'   video {k} (orig {orig(k)}): pred px {np.round(proj(pos(tk)[None])[0],1)} obs {tr.get(k)}')
    t38=(38-orig(k0))/25; t39=(39-orig(k0))/25; t37=(37-orig(k0))/25; t15=(1.5*25-orig(k0))/25
    print(f'   orig38->39 fd speed x25 = {np.linalg.norm(pos(t39)-pos(t38))*25:.2f} (parabola, valid only if no bounce)')
    print(f'   orig37->38 fd speed x25 = {np.linalg.norm(pos(t38)-pos(t37))*25:.2f}; instantaneous at t=1.50 s: {np.linalg.norm(vel(t15)):.2f}')
    print(f'   height drop from video24 to orig38: {pos(t38)[1]-pos(t24)[1]:.3f} m; P(orig38)={pos(t38).round(3)}')
print('--- G post-bounce position at orig 39 (video 37) from camera a ray + parabola horizontal position')
ks=list(range(25,37)); p,rms,model,tau=fit(aG,ks,25)
P0=p[:3];V0=p[3:6]
pos=lambda t: P0+V0*t+0.5*gvec*t*t
t38=(38-orig(25))/25; t39=(39-orig(25))/25
Q=pos(t39); u,v=aG[37]; d=np.array([u-C[0],v-C[1],F]); d/=np.linalg.norm(d)
# point on ray closest to vertical line through Q (x=Qx,z=Qz): minimise (lam*dx-Qx)^2+(lam*dz-Qz)^2
lam=(d[0]*Q[0]+d[2]*Q[2])/(d[0]**2+d[2]**2); P39=lam*d
print('  P39',P39.round(3),' parabola P39',Q.round(3),' P38',pos(t38).round(3))
print('  G orig38->39 fd speed x25 = %.2f  (x24 = %.2f)'%(np.linalg.norm(P39-pos(t38))*25,np.linalg.norm(P39-pos(t38))*24))
# impact time: when parabola reaches the bounce height = P39 y + small; report y of P39 vs parabola
for frac in np.linspace(0,1,11):
    tt=t38+frac/25
    pass
# floor height in camera a from basketball labels: y of basketball centre + 0.116
