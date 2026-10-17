import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
H=17.8
for tag in ('0032','0032x'):
    R=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/white_rows_%s.npy'%tag)
    sel=R[:,0]>=36
    j=R[sel,0]; c=j+1  # capture idx
    u=R[sel,1]; v=R[sel,2]
    print('==',tag)
    for deg in (1,2):
        pu=np.polyfit(c,u,deg); pv=np.polyfit(c,v,deg)
        ru=u-np.polyval(pu,c); rv=v-np.polyval(pv,c)
        print(' deg',deg,'resid sd u %.2f v %.2f'%(ru.std(),rv.std()))
        for cc in (37,38,39,43,48):
            p0=on_plane(np.polyval(pu,cc),np.polyval(pv,cc),H-2); p1=on_plane(np.polyval(pu,cc+1),np.polyval(pv,cc+1),H-2)
            # label-style: surface point along ray
            q0=p0*(1-2.0/np.linalg.norm(p0)); q1=p1*(1-2.0/np.linalg.norm(p1))
            print('   cap %d->%d phys %.1f label-style %.1f cm/s  (range %.1f)'%(cc,cc+1,np.linalg.norm(p1-p0)*25,np.linalg.norm(q1-q0)*25,np.linalg.norm(p0)))
    # linear 3D fit directly
    P=np.array([on_plane(a,b,H-2) for a,b in zip(u,v)])
    A=np.c_[np.ones(len(c)),c]
    coef,_,_,_=np.linalg.lstsq(A,P,rcond=None)
    print(' linear 3D fit velocity', coef[1]*25, 'speed %.1f'%(np.linalg.norm(coef[1])*25))
    A2=np.c_[np.ones(len(c)),c-37,(c-37)**2]
    coef2,_,_,_=np.linalg.lstsq(A2,P,rcond=None)
    for cc in (37,37.5,38,40,43):
        vel=(coef2[1]+2*coef2[2]*(cc-37))*25
        print(' quad 3D fit speed at cap %.1f: %.1f'%(cc,np.linalg.norm(vel)))
