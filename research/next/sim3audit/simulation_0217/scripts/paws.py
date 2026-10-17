import numpy as np, sys
sys.path.insert(0,'scripts')
from cam import *
B=np.load('dogbox.npy')
for r in B[::3]:
    i,x0,x1,y0,y1=r[:5]
    print(int(i), 'bottom y',y1)
