import sys, numpy as np, json; sys.path.insert(0,'scripts')
from models import M
d=json.load(open('xcomps.json'))
cen={}
for n in range(48):
    b=[x for x in d[str(n)] if x['a']>4000 and not abs(x['cx']-986)<6][0]; cen[n]=(b['cx'],b['cy'])
def tc(n): return n/25 if n<=11 else ((n+1)/25 if n<=35 else (n+2)/25)
for m in M:
    X10=m.P(*cen[10],2.73); r10=np.linalg.norm(X10)
    # size route: true range ratio k (raw 1.150, off-axis corrected per model)
    c10=m.ray(*cen[10])[2]; c34=m.ray(*cen[34])[2]
    kraw=1.150; kcorr=kraw/((c34/c10)**1.5)
    sz=[np.linalg.norm(r10*k*m.ray(*cen[34])-X10) for k in (kcorr,kraw)]
    z=m.H-X10@m.dn
    Pt={n:m.fp(*cen[n],z) for n in cen}
    vf=np.linalg.norm(Pt[11]-Pt[10])/0.04
    ns=list(range(6,15)); T=np.array([tc(n) for n in ns]); X=np.array([Pt[n] for n in ns])
    A=np.c_[np.ones(len(T)),T-0.4]; coef,*_=np.linalg.lstsq(A,X,rcond=None); vfit=np.linalg.norm(coef[1])
    dA=np.linalg.norm(Pt[34]-Pt[10])
    pri=[0.9962*dA/vf,0.9962*dA/vfit]
    tab=np.linalg.norm(m.fp(595.5,299.3,0.01)-m.fp(782.3,419.5,0.01))
    allr=[dA,sz[0],sz[1],pri[0],pri[1],tab]
    print('%-26s click %.3f | size %.3f-%.3f (kcorr %.3f) | prior %.3f-%.3f | tab %.3f | median %.3f'%(m.name,dA,sz[0],sz[1],kcorr,pri[0],pri[1],tab,np.median(allr)))
