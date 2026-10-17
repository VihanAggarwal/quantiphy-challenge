import numpy as np, cv2
from reg import *
from rock_reg import footprint
from rockmask import rock_mask
m1,_=rock_mask('0027_segmented',30)
def c1_bottom(x): col=np.nonzero(m1[:,int(x)])[0]; return col.max() if len(col) else np.nan
for zs in [1.0,0.0,-0.8]:
  for d2 in [53.5,54.5,55.5]:
    Q=footprint(zs,d=d2)
    for d1 in [18.0,18.5,19.0]:
        F=frame_of('C1',d=d1)
        uv,z=project(F,Q)
        # near edge: for columns, max projected y vs observed bottom
        diffs=[]
        for x in range(500,800,20):
            sel=np.abs(uv[:,0]-x)<4
            if sel.sum()==0: continue
            diffs.append(c1_bottom(x)-uv[sel,1].max())
        print('zs %.1f dC2 %.1f dC1 %.1f  Yext %.2f Xext %.2f  C1 bottom obs-proj median %.1f px'%(zs,d2,d1,np.ptp(Q[:,1]),np.ptp(Q[:,0]),np.median(diffs)))
