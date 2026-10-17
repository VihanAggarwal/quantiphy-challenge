import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=1000
F=frames('simulation_0240',Y0,1080)[:49].astype(np.int16)
bg=np.median(F,axis=0)
np.set_printoptions(suppress=True,precision=1,linewidth=160)
def lowest(k,xa,xb,thr):
    D=np.abs(F[k,:,xa:xb]-bg[:,xa:xb]).sum(axis=2)
    m=(D>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    rows=np.nonzero(m.sum(axis=1)>=2)[0]
    return Y0+rows.max() if len(rows) else np.nan
for thr in (40,60,90):
    b=[lowest(k,int(150+3.21*k),int(345+3.21*k),thr) for k in range(49)]
    w=[lowest(k,int(385+5.94*k),int(630+5.94*k),thr) for k in range(49)]
    print('thr',thr,'brown lowest med',np.nanmedian(b),'p75',np.nanpercentile(b,75),' white med',np.nanmedian(w),'p75',np.nanpercentile(w,75))
    print('  brown',np.array(b)[::3]); print('  white',np.array(w)[::3])
