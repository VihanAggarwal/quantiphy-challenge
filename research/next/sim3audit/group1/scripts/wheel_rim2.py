import numpy as np
res=np.load('scripts/rim_polar.npy')
rs=np.arange(60,118,0.25)
from numpy import gradient
out=[]
for adeg in range(360):
    p=np.convolve(res[adeg], np.ones(5)/5, mode='same')
    d=gradient(p)
    # rim band: dark; inner edge = strongest negative gradient (light->dark going outward) in r 70..97
    m1=(rs>72)&(rs<97); m2=(rs>92)&(rs<114)
    i1=np.argmin(np.where(m1,d,9e9)); i2=np.argmax(np.where(m2,d,-9e9))
    out.append((adeg, rs[i1], d[i1], rs[i2], d[i2]))
out=np.array(out)
np.save('scripts/rim_edges.npy', out)
for row in out[::5]:
    print('%3d  inner r=%.2f (g=%.1f)   outer r=%.2f (g=%.1f)'%tuple(row))
