import cv2, numpy as np
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/pnp2.py').read().split("for f in [711,750,780,800]")[0])
uc_px=(570.5,542.0)
for f in [690,711,730,750]:
    K,R,t,err=solve(f)
    a=R[:,0]
    u=np.linalg.solve(K,[uc_px[0],uc_px[1],1.]); u/=np.linalg.norm(u)
    Xc=68.67*u
    for L in [8.56]:
        P=[K@(Xc+s*L/2*a) for s in (-1,1)]
        P=[p[:2]/p[2] for p in P]
        print('f=%d card px length %.1f  endpoints'%(f,np.linalg.norm(P[1]-P[0])),np.round(P,1), 'a=',a.round(3))
# vanishing point of table-y dir
l=np.array([0.9375,-0.3481,327.6,493.1]); r=np.array([0.8808,0.4736,1030.0,527.4])
A=np.array([[l[0],-r[0]],[l[1],-r[1]]]); s=np.linalg.solve(A,r[2:]-l[2:]); print('VP y-dir',l[2:]+s[0]*l[:2])
f_=np.array([0.9985,0.0550,682.1,561.6]); b=np.array([0.9992,0.0397,673.8,457.2])
A=np.array([[f_[0],-b[0]],[f_[1],-b[1]]]); s=np.linalg.solve(A,b[2:]-f_[2:]); print('VP x-dir',f_[2:]+s[0]*f_[:2])
