import numpy as np, sys
from dyn import *
from lmb import lsqb
hyp=sys.argv[1]; dts=[float(x) for x in sys.argv[2].split(',')]
tvid=CAP/25.
ta0=anch_t.copy()
if hyp=='ceil': ta0=np.ceil(anch_t*25-1e-9)/25
if hyp=='floor': ta0=np.floor(anch_t*25+1e-9)/25
if hyp=='vid25':
    ta0=np.interp(anch_t*25,np.arange(len(CAP)),CAP)/25.
if hyp=='video24':  # label time on 24fps video clock -> capture time via CAP interp
    ta0=np.interp(anch_t*24,np.arange(len(CAP)),CAP)/25.
p0=np.load('dyn2_anchdt.npy')[:14]
for dt in dts:
    ta=ta0+dt
    def resid(Pm):
        tg,X,Vv=simulate(Pm[:,:11])
        Xi=sample(tg,X,Vv,tvid)+Pm[:,None,11:14]*tvid[None,:,None]; u,v=project(Xi)
        Xa=sample(tg,X,Vv,ta)+Pm[:,None,11:14]*ta[None,:,None]
        ra=(np.linalg.norm(Xa,axis=2)-R-anch_d[None])/0.01
        return np.concatenate([u-U[None],v-V[None],((Pm[:,1]-638)/2.)[:,None],((Pm[:,2]-229)/2.)[:,None],ra],1)
    p,r=lsqb(resid,p0,iters=150)
    n=len(U); px=(r[:2*n]**2).mean()**.5; an=r[2*n+2:]
    print(hyp,'dt=%+.3f  px_rms=%.3f anchor_rms_cm=%.2f total=%.1f  resid=%s'%(dt,px,np.sqrt((an**2).mean()),(r**2).sum(),np.round(an,2)),flush=True)
    p0=p
