from vio import *
import cv2, sys
v=sys.argv[1]; thr=int(sys.argv[2]) if len(sys.argv)>2 else 40
fr=load(v); g=fr.astype(np.int16)
med=np.median(g[::3],axis=0).astype(np.int16)
for k in range(0,len(fr),3):
    d=np.abs(g[k]-med).max(axis=2)
    m=(d>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    bl=[(int(st[i,4]),round(cen[i][0],1),round(cen[i][1],1),int(st[i,2]),int(st[i,3]), int(g[k][lab==i].mean())) for i in range(1,n) if st[i,4]>25]
    print(k, sorted(bl,reverse=True)[:4])
