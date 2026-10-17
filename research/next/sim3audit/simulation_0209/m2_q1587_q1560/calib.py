import numpy as np
from cam import *
P={'FL':(749,825),'FR':(1868.6,631.4),'BR':(1583,549.5),'BL':(577.5,691)}
order=['FL','FR','BR','BL']
def cost(f,th):
    Q=[on_plane(*P[k],1.0,f,th)[:2] for k in order]
    c=0; angs=[]
    for i in range(4):
        a=Q[i-1]-Q[i]; b=Q[(i+1)%4]-Q[i]
        ang=np.degrees(np.arccos(a@b/np.linalg.norm(a)/np.linalg.norm(b))); angs.append(ang); c+=(ang-90)**2
    L1=np.linalg.norm(Q[1]-Q[0]); L2=np.linalg.norm(Q[2]-Q[3])
    return c,angs,L1/L2
best=None
for f in range(2500,2800,5):
    for thd in np.arange(12.0,15.0,0.05):
        c,angs,r=cost(f,np.radians(thd))
        if best is None or c<best[0]: best=(c,f,thd,angs,r)
print('best rectangle fit',best)
# vertical VP constraint: vV gives pitch for each f
vA,vB,vV=np.load('vps.npy')
for f in [2600,2652,2700]:
    print(f,'pitch from vertical VP',np.degrees(np.arctan(f/(vV[1]-CY))))
