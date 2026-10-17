import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0008_segmented')
rows=[]
for i in range(180,240):
    f=F[i]
    m=(255-f.min(axis=2)>60).astype(np.uint8)
    m[505:,700:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    for k in range(1,n):
        if st[k][4]>100 and st[k][1]>500:
            rows.append((i,st[k][0],st[k][0]+st[k][2],st[k][1],st[k][1]+st[k][3],cen[k][0]))
r=np.array(rows,float)
full=r[:,1]>2
fr=r[full,0]
for c,nm in [(1,'left'),(2,'right'),(5,'cent')]:
    p=np.polyfit(fr,r[full,c],1); print(nm,'px/frame',p[0],'px/s',p[0]*24)
print('len med',np.median(r[full,2]-r[full,1]),'height',np.median(r[full,4]-r[full,3]))
print('first full frame',fr[0])
# sailboat px speed over clip
S=[]
for i in range(0,240,6):
    f=F[i]; m=(255-f.min(axis=2)>60).astype(np.uint8); m[505:,700:]=0; m[500:]=0 if False else m[500:]
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); S.append((i,cen[k][0],st[k][0],st[k][0]+st[k][2],st[k][1]+st[k][3]))
S=np.array(S,float)
print('sail px/s', np.polyfit(S[:,0],S[:,1],1)[0]*24, 'bbox w med',np.median(S[:,3]-S[:,2]),'bottom med',np.median(S[:,4]))
