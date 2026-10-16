import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from ba import *
from pts import *
from vel import orig, buildall
xa,xb,lab=buildall(); idx={l:i for i,l in enumerate(lab)}
for fb in [670,711]:
    R,t,_,X,res=solve(xa,xb,fb0=fb,fit_fb=False)
    ra=np.linalg.norm(X,axis=1); rb=np.linalg.norm(X@R.T+t,axis=1)
    w,g=idx[('W',24)],idx[('G',24)]
    obs=np.array([3.0735+.0335,3.039+.0335,1.235+.0335,1.331+.0335]); mod=np.array([ra[w],ra[g],rb[w],rb[g]])
    s=(obs@mod)/(mod@mod)
    print('fb',fb,'s_lab',round(s,3))
    ks=sorted(k for (nm,k) in lab if nm=='O')
    for k in ks:
        P=X[idx[('O',k)]]*s
        line=f'  O{k} rangeA={np.linalg.norm(P):.3f} (surf {np.linalg.norm(P)-0.116:.3f}) rangeB={np.linalg.norm(R@P+t*s):.3f} (surf {np.linalg.norm(R@P+t*s)-0.116:.3f})'
        if ('O',k+1) in idx:
            d=np.linalg.norm(X[idx[('O',k+1)]]-X[idx[('O',k)]])*s
            line+=f'  step->{k+1}: {d:.4f} m, v(true dt)={d/((orig(k+1)-orig(k))/25):.2f}  v(x24)={d*24:.2f}'
        print(line)
    # orange displacement 0.5->1.0
    for a0,a1 in [(12,24),(11,23),(12,23)]:
        if ('O',a0) in idx and ('O',a1) in idx:
            print('  disp O',a0,a1, np.linalg.norm(X[idx[('O',a1)]]-X[idx[('O',a0)]])*s)
