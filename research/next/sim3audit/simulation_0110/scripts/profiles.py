"""Body-of-revolution profiles: predict silhouette h/w and near-rim band/w vs view angle th (from disk axis),
then solve (th, thickness scale) to match measured h/w and band/w. Orthographic, unit radius R=1 (w=2)."""
import numpy as np
from math import *
rho=np.linspace(0,1,4001)
def EF(r):  # Evans-Fung full thickness / R
    return np.sqrt(np.clip(1-r**2,0,None))*(0.207+2.003*r**2-1.123*r**4)
def torus(r, tt):  # circular tube of radius tt/2 at Rc=1-tt/2, flat-ish dimple at fraction 0.3*tt
    rc=1-tt/2; z=np.where(np.abs(r-rc)<=tt/2, np.sqrt(np.clip((tt/2)**2-(r-rc)**2,0,None)), 0)
    return 2*np.maximum(z, 0.3*tt/2*np.ones_like(r)*(r<rc))
def ellip_rim(r, tt, a):  # elliptical rim section: axial half tt/2, radial half a (fraction of R), centered at 1-a
    rc=1-a; z=np.where(np.abs(r-rc)<=a, (tt/2)*np.sqrt(np.clip(1-((r-rc)/a)**2,0,None)), 0)
    return 2*np.maximum(z, 0.3*tt/2*(r<rc))
def predict(full, th):
    zt=full/2; c,s=cos(th),sin(th)
    H=np.max(rho*c+zt*s)              # half-height of silhouette
    g=-rho*c+zt*s                     # near-side top-surface projection
    # crest contour = local max on rim (exclude r near 0 region if monotone)
    i=np.argmax(g[rho>0.3])+np.sum(rho<=0.3)
    up=g[i]
    # is it a genuine local max (contour visible)? require g decreasing inward from it
    return 2*H/2, (H+up)/2, rho[i]   # h/w, band/w, crest rho
meas_hw=0.540; meas_bw=0.262
print('measured h/w=%.3f band/w=%.3f'%(meas_hw,meas_bw))
fams={'EF':lambda k: k*EF(rho)}
for tt in [None]:
    pass
res=[]
def solve(name, mk, kgrid):
    best=None
    for k in kgrid:
        prof=mk(k)
        for thd in np.arange(55,80,0.1):
            hw,bw,cr=predict(prof,radians(thd))
            e=(hw-meas_hw)**2+(bw-meas_bw)**2
            if best is None or e<best[0]: best=(e,k,thd,hw,bw,cr,prof.max()/2)
    e,k,thd,hw,bw,cr,TD=best
    print('%-22s th=%.1f  T/D=%.3f  T=%.3f m (D=1.65)  fit hw=%.3f bw=%.3f rms=%.4f crest_rho=%.2f'%(name,thd,TD,TD*1.65,hw,bw,sqrt(e/2),cr))
solve('Evans-Fung scaled', lambda k: k*EF(rho), np.arange(0.5,1.5,0.01))
solve('torus', lambda k: torus(rho,k), np.arange(0.3,0.9,0.005))
for a in [0.15,0.2,0.25,0.3,0.35]:
    solve('ellip rim a=%.2f'%a, lambda k,a=a: ellip_rim(rho,k,a), np.arange(0.3,0.9,0.005))
