import numpy as np
from frame3d import axes
from sweep import to3d, E, C
f=3575
V,S,U=axes(f)
for N,i1 in [(24,24),(24,25),(25,25),(25,26),(24,23)]:
    vzf=18.49/N
    XL=to3d((1378,821),0.008866,f,vzf,iref=i1)[0]; XR=to3d((1950,712),0.008146,f,vzf,iref=i1)[0]
    ref=(XL+XR)/2
    XL2=to3d((1378,821),0.008866,f,vzf,iref=i1+N)[0]; XR2=to3d((1950,712),0.008146,f,vzf,iref=i1+N)[0]
    ref2=(XL2+XR2)/2
    for name,(a,b,c) in {'aabb_centre':(-2.27,-0.1,-1.5),'fin_mid':(0,0,0),'pod_mid':(0.4,-0.2,-2.6)}.items():
        P1=ref+a*V+b*S+c*U; P2=ref2+a*V+b*S+c*U
        print(N,i1,name,'range t1 %.2f t2 %.2f  (given 102.67 / 121.83)  ratio %.4f (1.1866)'%(np.linalg.norm(P1),np.linalg.norm(P2),np.linalg.norm(P2)/np.linalg.norm(P1)))
