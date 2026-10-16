import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from pts import *
from vel import orig
# extra correspondences after the bounce (both views separated): W 39-40 merged in b; use G/W 41.. only where a has them (a: none after 40) -> use 38 only
A=[];B=[];lab=[]
for nm,da,db in [('W',aW,bW),('G',aG,bG),('O',aO,bO)]:
    for k in sorted(set(da)&set(db)):
        A.append(da[k]);B.append(db[k]);lab.append((nm,k))
xa=np.array(A,float); xb=np.array(B,float); idx={l:i for i,l in enumerate(lab)}
fb=711.
R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
for s in [3.93,4.10,4.26]:
    print('=== scale',s)
    for nm in 'WG':
        P={k:X[idx[(nm,k)]]*s for (n2,k) in lab if n2==nm}
        ks=sorted(P)
        # pre-bounce ballistic fit (frames 27..35 + 36 for G? use 27..36 for both, check residual)
        pre=[k for k in ks if 27<=k<=36]
        T=np.array([orig(k)/25 for k in pre]); Pm=np.array([P[k] for k in pre])
        M=np.c_[np.ones_like(T),T,T**2]; cf=np.linalg.lstsq(M,Pm,rcond=None)[0]
        r=Pm-M@cf
        acc=2*cf[2]
        def pos(tt): return cf[0]+cf[1]*tt+cf[2]*tt*tt
        def vel(tt): return cf[1]+2*cf[2]*tt
        up=-acc/np.linalg.norm(acc)
        print(f' {nm}: fit 27-36 |acc|={np.linalg.norm(acc):.2f} m/s2, rms {np.sqrt((r**2).sum(1).mean())*1000:.1f} mm; speed(t=1.48)={np.linalg.norm(vel(1.48)):.2f} speed(t=1.50)={np.linalg.norm(vel(1.50)):.2f} speed(t=1.52)={np.linalg.norm(vel(1.52)):.2f}')
        for k in [36,37,38]:
            if k in P:
                dev=(P[k]-pos(orig(k)/25)); print(f'    frame {k} (orig {orig(k)}) deviation from pre-bounce parabola: {np.linalg.norm(dev)*100:.1f} cm, height rel parabola {dev@up*100:.1f} cm')
        for a0 in [34,35,36,37]:
            if a0 in P and a0+1 in P:
                d=np.linalg.norm(P[a0+1]-P[a0]); n=orig(a0+1)-orig(a0)
                # direction relative to camera-b ray
                dv=(P[a0+1]-P[a0]); rb=R@P[a0]+t*s; vb=R@dv
                ang=np.degrees(np.arccos(abs(vb@rb)/np.linalg.norm(vb)/np.linalg.norm(rb)))
                ra_=P[a0]; anga=np.degrees(np.arccos(abs(dv@ra_)/np.linalg.norm(dv)/np.linalg.norm(ra_)))
                print(f'    video {a0}->{a0+1} (orig {orig(a0)}->{orig(a0+1)}): |d|={d:.4f} m  speed true-dt={d*25/n:.2f}  x24={d*24:.2f}  [angle to b-ray {ang:.0f}deg, to a-ray {anga:.0f}deg]')
