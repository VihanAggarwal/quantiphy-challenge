import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from tplane import *
f=711.; n,cP,_,_,_=pose(f); nv,_=plane_from_vps(f); nv=nv if nv@n>0 else -nv
for lab,(A,B) in {'tip incl metal':((434.3,440.1),(502.1,435.3)),'body only':((440.0,439.7),(502.1,435.3))}.items():
    for N,nn in [(n,'PnP-n'),(nv,'VP-n')]:
        for c,cn in [(0.895,'label'),(cP,'metric')]:
            XA=inter(*A,N,c-0.005,f); XB=inter(*B,N,c-0.005,f)
            print(f'{lab:15s} {nn} {cn:6s} len {100*np.linalg.norm(XA-XB):.2f}  ranges {np.linalg.norm(XA):.3f} {np.linalg.norm(XB):.3f}')
    print(f'{lab:15s} single depth 1.6725: {100*np.linalg.norm(bp(*A,1.6725)-bp(*B,1.6725)):.2f}')
