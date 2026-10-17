import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
v=sys.argv[1]
F=frames(v)
G=[f.astype(np.float32) for f in F]
print(len(F),F[0].shape)
med=np.median(np.stack(G[::2]),axis=0)
g=cv2.cvtColor(med.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
# lane marking rows: rows with bright pixels
rowsum=(g>120).sum(axis=1)
ys=np.where(rowsum>20)[0]
print('bright rows', ys)
# per column groups: compute y-centroid of dashes in each x band
for xa in range(0,1280,160):
    band=(g[:,xa:xa+160]>120)
    rs=band.sum(axis=1)
    yy=np.where(rs>5)[0]
    if len(yy)==0: continue
    groups=np.split(yy,np.where(np.diff(yy)>3)[0]+1)
    cents=[ (gg*rs[gg]).sum()/rs[gg].sum() for gg in groups]
    print(xa, np.round(cents,1), np.round(np.diff(cents),1))
