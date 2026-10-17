from util import *
import sys
v=sys.argv[1]
fr=frames(v); st=np.stack([f[600:800].astype(np.int16) for f in fr])  # band rows 600-800
bg=np.median(st,axis=0)
for i in range(0,len(fr),3):
    d=np.abs(st[i]-bg).max(axis=2)>35
    ys,xs=np.nonzero(d)
    if len(xs)<50: print(i,'none'); continue
    # column counts
    cols=np.nonzero(d.sum(0)>=2)[0]; rows=np.nonzero(d.sum(1)>=2)[0]
    print(i, len(xs), 'x',cols.min(),cols.max(),cols.max()-cols.min(),'y',rows.min()+600,rows.max()+600)
