import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import comps
from ba import *
from pts import *
from vel import buildall
xa,xb,lab=buildall(); idx={l:i for i,l in enumerate(lab)}
def width(v,i,near):
    cs=comps(v,i,minA=100)
    c=min(cs,key=lambda c: np.hypot(*(c['c']-np.array(near))))
    if np.hypot(*(c['c']-np.array(near)))>6: return None
    ys,xs=np.where(c['mask']); P=np.c_[xs,ys].astype(float); P-=P.mean(0)
    w,V=np.linalg.eigh(np.cov(P.T))
    minor=P@V[:,0]; major=P@V[:,1]
    # width perpendicular to main axis: use extent of central slab (|major| small) to avoid blur tails
    sl=np.abs(major)<max(2,0.25*np.ptp(major))
    wmin=np.ptp(minor[sl])+1
    return wmin, np.ptp(major)+1, c['A']
fb=711
for fbv in [670,711]:
    R,t,_,X,res=solve(xa,xb,fb0=fbv,fit_fb=False)
    for nm,da,db in [('W',aW,bW),('G',aG,bG)]:
        for k in range(25,36):
            if (nm,k) not in idx: continue
            Xk=X[idx[(nm,k)]]; ra=np.linalg.norm(Xk); rb=np.linalg.norm(R@Xk+t)
            wa=width('ax',k,da[k]); wb=width('bx',k,db[k])
            if wa is None or wb is None: print(nm,k,'skip'); continue
            # implied scale s for a 6.7cm ball: D = s*r*w/f  => s = 0.067*f/(r*w)
            sa=0.067*711/(ra*wa[0]); sb=0.067*fbv/(rb*wb[0])
            print(f'fb{fbv} {nm}{k}: a width {wa[0]:.1f}px (len {wa[1]:.0f}) b width {wb[0]:.1f}px (len {wb[1]:.0f}) -> scale for 6.7cm: a {sa:.2f}  b {sb:.2f}')
