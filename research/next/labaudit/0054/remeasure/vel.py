import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from pts import *
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)   # 25->24 fps conversion drops orig frames 12 and 37
def buildall():
    A=[];B=[];lab=[]
    for nm,da,db in [('W',aW,bW),('G',aG,bG),('O',aO,bO)]:
        for k in sorted(set(da)&set(db)):
            A.append(da[k]);B.append(db[k]);lab.append((nm,k))
    return np.array(A,float),np.array(B,float),lab
if __name__=="__main__":
    xa,xb,lab=buildall(); idx={l:i for i,l in enumerate(lab)}
    rW=rG=0.0335
    for fb in [650,670,690,711]:
        R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
        ra=np.linalg.norm(X,axis=1); rb=np.linalg.norm(X@R.T+t,axis=1)
        w,g=idx[('W',24)],idx[('G',24)]
        # scale from labels (surface range + radius = centre range)
        obs=np.array([3.0735+rW,3.039+rG,1.235+rW,1.331+rG]); mod=np.array([ra[w],ra[g],rb[w],rb[g]])
        s_lab=(obs@mod)/(mod@mod)
        # scale from gravity: fit quadratic to frames 27..35 per ball, in orig-frame time (1/25 s)
        accs=[]
        for nm in 'WG':
            ks=[k for k in range(27,36) if (nm,k) in idx]
            T=np.array([orig(k)/25 for k in ks]); P=np.array([X[idx[(nm,k)]] for k in ks])
            M=np.c_[np.ones_like(T),T,T**2]
            cf=np.linalg.lstsq(M,P,rcond=None)[0]; acc=2*cf[2]
            accs.append(acc)
        gdir=(accs[0]/np.linalg.norm(accs[0])+accs[1]/np.linalg.norm(accs[1])); gdir/=np.linalg.norm(gdir)
        s_g=[9.81/np.linalg.norm(a) for a in accs]
        print(f'fb={fb}: s_lab={s_lab:.3f} (resid {np.round(s_lab*mod-obs,3)}), s_grav W={s_g[0]:.3f} G={s_g[1]:.3f}, angle between W/G acc dirs={np.degrees(np.arccos(np.dot(accs[0],accs[1])/np.linalg.norm(accs[0])/np.linalg.norm(accs[1]))):.1f}deg')
        for s,sn in [(s_lab,'lab'),(np.mean(s_g),'grav')]:
            line=[]
            for nm in 'WG':
                for k in [34,35,36,37,38]:
                    if (nm,k) in idx and (nm,k+1) in idx:
                        d=np.linalg.norm(X[idx[(nm,k+1)]]-X[idx[(nm,k)]])*s
                        dt=(orig(k+1)-orig(k))/25
                        line.append(f'{nm}{k}->{k+1}: {d/dt:.2f}m/s(true dt) {d*24:.2f}(x24)')
            print('  scale',sn,'%.3f'%s,' | '.join(line))
        # heights along gravity (relative)
        s=s_lab
        for nm in 'WG':
            h=[(k,round(float(-(X[idx[(nm,k)]]@gdir)*s),3)) for k in range(24,39) if (nm,k) in idx]
            print('  height(up, rel) ',nm,h)
