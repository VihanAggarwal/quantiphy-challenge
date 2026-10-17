import cv2, numpy as np
from common import load, cap
fr=load('x')
for i in list(range(8,26))+list(range(48,68)):
    f=fr[i]; nw=(f.astype(int).min(axis=2)<215)
    band=nw[:, 405:520]
    rows=np.nonzero(band.sum(1)>=4)[0]
    top=rows.min() if len(rows) else -1
    # toy top region: columns within band having nonwhite at row top..top+10
    cols=np.nonzero(band[top:top+12].sum(0)>0)[0]+405 if top>=0 else []
    print(i, cap(i), 'top', top, 'xspan', (cols.min(),cols.max()) if len(cols) else None)
