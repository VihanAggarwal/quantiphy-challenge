import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from vel import orig, buildall
xa,xb,lab=buildall(); idx={l:i for i,l in enumerate(lab)}
n=len(xa)
for fb in [620,650,680,711,740,770,800,850,900]:
    R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
    accs=[]
    for nm in 'WG':
        ks=[k for k in range(27,36) if (nm,k) in idx]
        T=np.array([orig(k)/25 for k in ks]); P=np.array([X[idx[(nm,k)]] for k in ks])
        M=np.c_[np.ones_like(T),T,T**2]; cf=np.linalg.lstsq(M,P,rcond=None)[0]; accs.append(2*cf[2])
    gm=(accs[0]+accs[1])/2; s_g=9.81/np.linalg.norm(gm); up=-gm/np.linalg.norm(gm)
    O=np.array([X[idx[('O',k)]] for k in range(12,27)]); d=O[-1]-O[0]
    tilt=np.degrees(np.arcsin(abs(d@up)/np.linalg.norm(d)))
    ra=np.linalg.norm(X,axis=1); rb=np.linalg.norm(X@R.T+t,axis=1)
    w,g=idx[('W',24)],idx[('G',24)]
    sa=[(3.0735+.0335)/ra[w],(3.039+.0335)/ra[g]]; sb=[(1.235+.0335)/rb[w],(1.331+.0335)/rb[g]]
    o12=idx[('O',12)]; o24=idx[('O',24)]
    sO=[(2.3557+.116)/ra[o12],(1.81+.116)/ra[o24]]
    rms=np.sqrt((res**2).sum(1).mean())
    print(f'fb={fb}: rms={rms:.2f}px s_grav={s_g:.3f} s_aLab(W,G)={sa[0]:.3f},{sa[1]:.3f} s_bLab(W,G)={sb[0]:.3f},{sb[1]:.3f} s_aLab(O12,O24)={sO[0]:.3f},{sO[1]:.3f} bball-track tilt vs horizontal={tilt:.1f}deg')
