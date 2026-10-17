import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('simulation_0134')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
# toast: template from frame 42 region; find toast bbox via difference from frame 0? toast at rest visible above toaster.
# toaster extents in frame 0: red mask
hsv=cv2.cvtColor(F[0],cv2.COLOR_BGR2HSV)
h,s,v=[hsv[...,k].astype(int) for k in range(3)]
red=((h<10)|(h>170))&(s>100)
ys,xs=np.where(red)
print('red body x',xs.min(),xs.max(),'y',ys.min(),ys.max())
# toast top edge per frame: column band at toast centre x
cols=slice(470,560)
for i in [0,38,39,40,41,42,43,44,45,46,47,48,50,55,59]:
    prof=G[i][:, cols].mean(axis=1)
    print(i, end=' ')
# template track
T=G[42][700:960, 470:640]  # guess
