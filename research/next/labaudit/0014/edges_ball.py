import cv2, numpy as np
from vel import track
for R in ['rs','rx','ro']:
    bg=np.median(np.stack([cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32) for i in range(36,49)]),0)
    tr=track(R)
    out=[]
    for i in range(11,18):
        im=cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32)
        d=np.abs(im-bg).sum(2)
        cx=int(round(tr[i][0]))
        col=d[260:480,cx-3:cx+4].mean(1)
        pk=np.percentile(col,98); thr=pk/2
        ins=np.where(col>thr)[0]
        top=ins.min()+260
        # horizontal edges at the centre row
        cy=int(round(tr[i][1]))
        row=d[cy-2:cy+3,490:610].mean(0); pkr=np.percentile(row,98); ins2=np.where(row>pkr/2)[0]
        out.append((i,top,round(tr[i][1],1),ins2.min()+490,ins2.max()+490))
    print(R,out)
