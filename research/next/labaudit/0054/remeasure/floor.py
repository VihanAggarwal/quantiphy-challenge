import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from vel import orig, buildall
xa,xb,lab=buildall(); idx={l:i for i,l in enumerate(lab)}
for fb in [670,711]:
    R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
    accs=[];fits={}
    for nm in 'WG':
        ks=[k for k in range(27,36) if (nm,k) in idx]
        T=np.array([orig(k)/25 for k in ks]); P=np.array([X[idx[(nm,k)]] for k in ks])
        M=np.c_[np.ones_like(T),T,T**2]; cf,_,_,_=np.linalg.lstsq(M,P,rcond=None)
        resid=P-M@cf
        accs.append(2*cf[2]); fits[nm]=(cf,np.sqrt((resid**2).sum(1).mean()))
    up=-(accs[0]+accs[1]); up/=np.linalg.norm(up)
    s_g=9.81/np.linalg.norm((accs[0]+accs[1])/2)
    hO=[X[idx[('O',k)]]@up for k in range(12,27)]
    print(f'fb {fb}: s_grav(mean acc)={s_g:.3f}; fit rms (unit) W {fits["W"][1]*s_g*1000:.1f}mm G {fits["G"][1]*s_g*1000:.1f}mm')
    print('  basketball centre heights (unit*s_g, m):',np.round(np.array(hO)*s_g,3))
    hb=np.median(hO)
    for nm,k in [('G',36),('G',37),('G',38),('W',37),('W',38)]:
        dh=(X[idx[(nm,k)]]@up-hb)
        print(f'  {nm}{k}: height above basketball-centre plane = {dh*s_g:.3f} m (s_grav) ; implied s if equal to -0.0825: {-0.0825/dh:.3f}')
    # extrapolate ballistic fits to floor: time when height = basketball plane - 0.0825
    for nm in 'WG':
        cf=fits[nm][0]
        for tt in np.arange(1.40,1.62,0.02):
            pass
