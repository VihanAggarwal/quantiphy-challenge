import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
vid=sys.argv[1]
F=frames(vid,n=49)
bg=np.median(F,axis=0)
np.set_printoptions(suppress=True,precision=2,linewidth=160)
recs=[]
for k in range(49):
    D=np.abs(F[k].astype(np.int16)-bg.astype(np.int16)).sum(axis=2)
    m=(D>float(sys.argv[2]) if len(sys.argv)>2 else D>30).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[i,4],i) for i in range(1,n) if st[i,4]>150]
    comps.sort(reverse=True)
    recs.append([(st[i],cen[i]) for a,i in comps[:4]])
# print summary for frame 0 and 48
for k in [0,24,48]:
    print(k,[(tuple(s),tuple(np.round(c,1))) for s,c in recs[k]])
