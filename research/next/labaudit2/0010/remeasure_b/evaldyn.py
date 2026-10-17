import numpy as np, sys
from dyn import *
p=np.load(sys.argv[1]); scale=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
tg,X,Vv=simulate(p[None,:11])
tv=CAP/25.
Xi=sample(tg,X,Vv,tv)[0]; u,v=project(Xi)
print('per-frame px resid u:',np.round(u-U,1)); print('v:',np.round(v-V,1))
for dt in [-0.04,-0.03,-0.02,-0.01,0,0.01,0.02]:
    Xa=sample(tg,X,Vv,anch_t+dt)[0]; rng=np.linalg.norm(Xa,axis=1)-R
    print('dt=%+.2f pred'%dt,np.round(rng,3),'resid cm',np.round((rng-anch_d)*100,1),'rms %.2f'%(np.sqrt(np.mean((rng-anch_d)**2))*100))
# turning time: min speed near 0.7
sp=np.linalg.norm(Vv[0],axis=1); m=(tg>0.5)&(tg<0.9); print('near-turn time',tg[m][np.argmin(sp[m])],'range',np.linalg.norm(X[0][m][np.argmin(sp[m])])-R)
m=(tg>1.7)&(tg<2.1); print('near-turn2 time',tg[m][np.argmin(sp[m])])
m=(tg>1.1)&(tg<1.5); print('far-turn time',tg[m][np.argmin(sp[m])])
# label-style quantities on capture frames 15,16,17
caps=np.array([14,15,16,17,18])
Xc=sample(tg,X,Vv,caps/25.)[0]
d=Xc/np.linalg.norm(Xc,axis=1,keepdims=True)
S=(np.linalg.norm(Xc,axis=1)-R)[:,None]*d   # surface points along centre rays
for name,Q in [('centre',Xc),('surface',S)]:
    v=np.linalg.norm(np.diff(Q,axis=0),axis=1)*25
    a_s=np.diff(v)*25; a_v=np.linalg.norm(np.diff(Q,2,axis=0),axis=1)*625
    print(name,'fwd speeds caps14..17:',np.round(v,3),' scalar acc:',np.round(a_s,2),' vector acc:',np.round(a_v,2))
i=np.argmin(np.abs(tg-0.6)); print('physical at 0.6: speed %.3f'%np.linalg.norm(Vv[0,i]))
# physical acceleration at 0.6
acc=np.gradient(Vv[0],H,axis=0); vhat=Vv[0,i]/np.linalg.norm(Vv[0,i])
print('physical |a| %.3f tangential %.3f'%(np.linalg.norm(acc[i]),acc[i]@vhat))
print('ranges at caps',caps,np.round(np.linalg.norm(Xc,axis=1)-R,4))
