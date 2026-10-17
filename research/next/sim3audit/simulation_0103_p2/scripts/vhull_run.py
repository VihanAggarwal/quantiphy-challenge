import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from vhull import *
np.set_printoptions(precision=2,suppress=True)
MA=rockmask('simulation_0027_segmented',24,320); MC=rockmask('simulation_0043_segmented',24,470)
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MA.npy',MA); np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/MC.npy',MC)
def wray(reg,u,v):
    d=reg.cam.ray(u,v); return reg.to_W(reg.cam.C), reg.R@d
def closest(o1,d1,o2,d2):
    w=o1-o2; a=d1@d1; b=d1@d2; c=d2@d2; dd=d1@w; e=d2@w
    s=(b*e-c*dd)/(a*c-b*b); t=(a*e-b*dd)/(a*c-b*b)
    return o1+s*d1, o2+t*d2
def person_ground(A):
    # person feet (418,411) range ~100.56 => feet z
    d=A.cam.ray(418,411); return A.to_W(A.cam.C+100.56*d)
for prm in [dict(fA=3460,pA=18.7,fC=3870,pC=53.0),dict(fA=3401,pA=18.7,fC=3800,pC=53.0),dict(fA=3517,pA=18.7,fC=3950,pC=53.0),
            dict(fA=3460,pA=17.7,fC=3870,pC=51.0),dict(fA=3460,pA=19.7,fC=3870,pC=55.0)]:
    A,C=build(prm)
    ya,xa=np.where(MA); yc,xc=np.where(MC)
    o1,d1=wray(A,xa.mean(),ya.mean()); o2,d2=wray(C,xc.mean(),yc.mean())
    p,q=closest(o1,d1,o2,d2)
    feet=person_ground(A)
    # grid
    cen=(p+q)/2
    g=0.25
    xs=np.arange(cen[0]-25,cen[0]+25,g); ys=np.arange(cen[1]-25,cen[1]+25,g); zs=np.arange(-6,14,g)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij')
    keep=carve([(A,MA),(C,MC)],(X,Y,Z),keep_right=[True,False])
    print(prm,'centroid rays meet',p,q,'| person feet W',feet)
    for zfloor in [feet[2]-0.5,feet[2],feet[2]+0.5]:
        k=keep&(Z>=zfloor)
        ii=np.where(k)
        if len(ii[0])==0: print('empty'); continue
        ex=[(xs[ii[0]].min(),xs[ii[0]].max()),(ys[ii[1]].min(),ys[ii[1]].max()),(zs[ii[2]].min(),zs[ii[2]].max())]
        print('  zfloor %.2f'%zfloor,'X %.1f..%.1f (%.2f)  Y %.1f..%.1f (%.2f)  Ztop %.2f  H %.2f'%(ex[0][0],ex[0][1],ex[0][1]-ex[0][0]+g,ex[1][0],ex[1][1],ex[1][1]-ex[1][0]+g,ex[2][1],ex[2][1]-zfloor+g),' touches grid edge?',[xs[ii[0]].min()<=xs[0],xs[ii[0]].max()>=xs[-1],ys[ii[1]].min()<=ys[0],ys[ii[1]].max()>=ys[-1]])
