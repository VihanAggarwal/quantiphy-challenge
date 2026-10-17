import numpy as np, sys
from frame3d import axes
from sweep import to3d
f=3575; vzf=18.49/24
V,S,U=axes(f)
# reference = fin-top midpoint from point sweeps
XL=to3d((1378,821),0.008866,f,vzf)[0]; XR=to3d((1950,712),0.008146,f,vzf)[0]
ref=(XL+XR)/2
for c in sys.argv[1:]:
    D=np.load(f'dense3d_{c}.npy')
    X=D[:,:3]; p=D[:,3:5]; cm=D[:,5]
    loc=np.c_[(X-ref)@V,(X-ref)@S,(X-ref)@U]
    ok=cm<0.15
    print(c,'n',ok.sum())
    o=np.argsort(loc[ok,0])
    L=loc[ok][o]; P=p[ok][o]
    print(' rearmost:'); 
    for k in range(0,40,4): print('   fore %.2f span %.2f up %.2f px (%d,%d)'%(L[k,0],L[k,1],L[k,2],P[k,0],P[k,1]))
    print(' frontmost:')
    for k in range(1,40,4): print('   fore %.2f span %.2f up %.2f px (%d,%d)'%(L[-k,0],L[-k,1],L[-k,2],P[-k,0],P[-k,1]))
    print(' span pct', np.percentile(loc[ok,1],[0.1,1,99,99.9]))
