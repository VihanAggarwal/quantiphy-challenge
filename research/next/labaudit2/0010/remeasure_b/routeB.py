import numpy as np
from geo import *
def sphere_track(sp,L,pu=638,pv=229,uu=U,vv=V):
    P=sp*ray(pu,pv); d=ray(uu,vv)
    b=d@P; disc=b**2-(P@P-L**2)
    return P,b,disc
if __name__=='__main__':
    for sp,L in [(1.514,0.349),(1.520,0.352),(1.507,0.347)]:
        P,b,disc=sphere_track(sp,L)
        print('sp,L',sp,L)
        for j in range(0,49):
            dd=max(disc[j],0); s1=b[j]-np.sqrt(dd); s2=b[j]+np.sqrt(dd)
            if j in range(8,24) or j in (29,43): print(' j%2d cap%2d disc=%.4f near=%.3f far=%.3f'%(j,CAP[j],disc[j],s1-R,s2-R))
