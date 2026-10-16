import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from pts import *
def buildall(use_O=True):
    A=[];B=[];lab=[]
    sets=[('W',aW,bW),('G',aG,bG)]+([('O',aO,bO)] if use_O else [])
    for nm,da,db in sets:
        for k in sorted(set(da)&set(db)):
            A.append(da[k]);B.append(db[k]);lab.append((nm,k))
    return np.array(A,float),np.array(B,float),lab
xa,xb,lab=buildall(True); n=len(xa)
idx={l:i for i,l in enumerate(lab)}
for fb in [500,550,600,650,700,711,750,800,900]:
    R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
    ra=np.linalg.norm(X,axis=1); rb=np.linalg.norm(X@R.T+t,axis=1)
    w,g=idx[('W',24)],idx[('G',24)]
    print('fb=%d rms a=%.2f b=%.2f | ratio rA/rB W24=%.3f G24=%.3f (label surf 2.489/2.283; centre 2.425/2.237)'%(fb,np.sqrt((res[:n]**2).sum(1).mean()),np.sqrt((res[n:]**2).sum(1).mean()),ra[w]/rb[w],ra[g]/rb[g]))
R,t,fb,X,res=solve(xa,xb,fit_fb=True)
ra=np.linalg.norm(X,axis=1); rb=np.linalg.norm(X@R.T+t,axis=1)
w,g=idx[('W',24)],idx[('G',24)]
print('FIT fb=%.1f rms a=%.2f b=%.2f ratio W=%.3f G=%.3f'%(fb,np.sqrt((res[:n]**2).sum(1).mean()),np.sqrt((res[n:]**2).sum(1).mean()),ra[w]/rb[w],ra[g]/rb[g]))
for l,r1,r2 in zip(lab,res[:n],res[n:]):
    if np.hypot(*r1)>1.5 or np.hypot(*r2)>1.5: print('  big',l,r1.round(1),r2.round(1))
