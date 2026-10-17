import numpy as np
tr=np.load('plane_simulation_0231.npy')
ok=~np.isnan(tr[:,1]); t=tr[ok,0]; x=tr[ok,3]; y=tr[ok,4]
xl=tr[ok,1]
sF=0.714/24/8.88
sel=(t>=15)&(t<=32)
t=t[sel]; x=x[sel]; y=y[sel]; xl=xl[sel]
# smooth position with quintic poly then differentiate
for nm,X in [('cx',x),('Ledge',xl)]:
    px=np.polyfit(t,X,4); py=np.polyfit(t,y,4)
    for T in [24,30]:
        # backward-difference speed of smooth path
        p=lambda tt: np.array([np.polyval(px,tt),np.polyval(py,tt)])
        v=lambda tt: np.linalg.norm(p(tt)-p(tt-1))*24*sF
        print(nm,'t=%.2f speed %.2f m/s  acc(bwd) %.2f  acc(central over +-2f) %.2f'%(T/24,v(T),(v(T)-v(T-1))*24,(v(T+2)-v(T-2))/4*24))
