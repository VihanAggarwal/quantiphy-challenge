import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0119')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float) for f in F]
# frame differences consecutive
for i in range(1,48,4):
    d=np.abs(G[i]-G[i-1]); m=(d>25).astype(np.uint8)
    ys,xs=np.nonzero(m)
    print(i, len(xs), (xs.min(),xs.max(),ys.min(),ys.max()) if len(xs) else '')
