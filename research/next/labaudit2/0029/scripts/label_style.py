# label-style forward differences on the 25 fps capture clock with several models for the unknown next-frame ToF
import numpy as np, json
from geom import ray
f=711.
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json'))
RT=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/routes3d.json'))
o=T['o']; x=T['x']
uv={k:np.array([(o[k]['cx']+x[k]['cx'])/2,(o[k]['cy']+x[k]['cy'])/2]) for k in range(49)}
rng={nm:{int(k):np.linalg.norm(v) for k,v in P.items()} for nm,P in RT.items()}
P3={nm:{int(k):np.array(v) for k,v in P.items()} for nm,P in RT.items()}
r=0.0335
anch={24:0.901,30:1.144,38:1.027}       # video frame -> stated surface range
capn={24:25,30:31,38:40}
def unit(p): d=ray(*p,f); return d/np.linalg.norm(d)
def lin_interp(k_next):
    # linear interpolation in capture time between stated anchors (extrapolate with last segment)
    cap=lambda k: k+(k>=12)+(k>=36)
    ks=sorted(anch); ns=[cap(k) for k in ks]; ds=[anch[k] for k in ks]
    n=cap(k_next)
    if n<=ns[1]: return ds[0]+(ds[1]-ds[0])*(n-ns[0])/(ns[1]-ns[0])
    return ds[1]+(ds[2]-ds[1])*(n-ns[1])/(ns[2]-ns[1])
bias={nm:np.mean([anch[k]-(rng[nm][k]-r) for k in anch]) for nm in rng}
print('mean ToF minus route surface range at anchors:',{k:round(100*v,1) for k,v in bias.items()},'cm')
def models(k):
    d0=anch[k]; k1=k+1; out={}
    out['lin_interp']=lin_interp(k1)
    for nm in rng:
        out[nm+'_persist']=d0+(rng[nm][k1]-rng[nm][k])
        out[nm+'_meanbias']=rng[nm][k1]-r+bias[nm]
    # smoothed size trend (quadratic fit over a window) for the size route
    ks=[j for j in range(k-4,k+6) if j in rng['C_size'] and not (j<=30<k1 and False)]
    return out
def lab(k,d1,p0=None,p1=None):
    p0=uv[k] if p0 is None else p0; p1=uv[k+1] if p1 is None else p1
    return 25*100*np.linalg.norm(d1*unit(p1)-anch[k]*unit(p0))
for k,name in [(24,'v(1.0) n25->26 = video 24->25'),(30,'v(hit 1.24) n31->32 = video 30->31'),(38,'v(1.6) n40->41 = video 38->39')]:
    print('\n==',name,' pixel step',(uv[k+1]-uv[k]).round(1))
    for m,d1 in models(k).items():
        print('  %-20s d_next=%.3f (delta %+.1f cm)  label-style v = %.1f cm/s'%(m,d1,100*(d1-anch[k]),lab(k,d1)))
    for nm in P3:
        print('  physical FD %-14s %.1f cm/s'%(nm,25*100*np.linalg.norm(P3[nm][k+1]-P3[nm][k])))
    # sensitivity: v as function of radial delta
    print('  v vs radial delta (cm):',' '.join('%+d:%.0f'%(dd,lab(k,anch[k]+dd/100)) for dd in [-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7]))
