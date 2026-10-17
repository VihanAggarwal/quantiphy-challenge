import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0021_segmented')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
rows=[]
for i,g in enumerate(G):
    sub=g[:270]
    m=(sub<150).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[(st[k],cen[k]) for k in range(1,n) if st[k][4]>40 and st[k][1]+st[k][3]<265]
    if not cands: rows.append((i,np.nan,np.nan,np.nan,np.nan,np.nan)); continue
    s,c=max(cands,key=lambda t:t[0][4])
    rows.append((i,s[0],s[0]+s[2],s[1],s[1]+s[3],c[0],c[1],s[4]))
for r in rows[::5]: print(np.round(r,1))
# camera motion: phase correlation of building region (y 300-470) vs frame 0
ref=G[0][300:470]
win=cv2.createHanningWindow(ref.shape[::-1],cv2.CV_32F)
for i in range(0,107,10):
    sh,resp=cv2.phaseCorrelate(ref,G[i][300:470],win)
    print('cam',i,np.round(sh,2),round(resp,2))
