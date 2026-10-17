from load import *
import numpy as np
F=frames('0303')
M=[]; stats=[]
for i,f in enumerate(F):
    m=mask0303(f)
    ys,xs=np.nonzero(m)
    stats.append((i,m.sum(),xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean()))
    M.append(np.packbits(m,axis=None))
np.save('masks0303_packed.npy',np.array(M))
for s in stats[::6]+[stats[-1]]: print(s)
