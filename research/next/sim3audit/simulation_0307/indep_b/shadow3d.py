import numpy as np
from frame3d import axes
from sweep import to3d, E, C
f=3590; vzf=18.49/24; i=24
V,S,U=axes(f)
D=np.load('shadow_q.npy',allow_pickle=True).item()
XL=to3d((1378,821),0.008866,f,vzf,iref=i)[0]; XR=to3d((1950,712),0.008146,f,vzf,iref=i)[0]; ref=(XL+XR)/2
G={}
for k,(p,v) in D.items():
    q=np.mean([a[0] for a in v]); c=min(a[1] for a in v)
    Z=vzf*(1/q+i); X=np.array([(p[0]-C[0])*Z/f,(p[1]-C[1])*Z/f,Z])-ref
    G[k]=X
    print('%-11s fore %7.2f span %7.2f up %7.2f  cost %.2f'%(k,X@V,X@S,X@U,c))
np.save('shadow3d.npy',G,allow_pickle=True)
