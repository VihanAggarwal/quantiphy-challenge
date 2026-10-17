import numpy as np, cv2
from reg import *
from rock_reg import footprint
zs=-0.6
Q=footprint(zs)
poly=Q[:,:2].astype(np.float32)
for f4 in [3420,3500]:
 for d4 in [0.0,0.36,0.7]:
  F=frame_of('C4',f=f4,d=d4)
  Cb=F['C']
  res=[]
  for (u,vt,vb) in [(959,460,578),(900,474,575)]:
    dt=F['M']@F['cam'].ray(u,vt); dbm=F['M']@F['cam'].ray(u,vb)
    inside=[]
    for t in np.linspace(80,220,1401):
        p=Cb+t*dt/np.linalg.norm(dt[:2])
        if cv2.pointPolygonTest(poly,(float(p[0]),float(p[1])),False)>=0: inside.append((t,p[2]-zs))
    pb=None
    for t in np.linspace(80,220,1401):
        p=Cb+t*dbm/np.linalg.norm(dbm[:2])
        if p[2]<=zs: pb=(t,p[0],p[1]); break
    res.append('u=%d top-ray over footprint d %.0f..%.0f h %.2f..%.2f | base-ray hits sand d %.0f'%(u,inside[0][0],inside[-1][0],inside[0][1],inside[-1][1],pb[0]))
  print(f4,d4,' || '.join(res))
