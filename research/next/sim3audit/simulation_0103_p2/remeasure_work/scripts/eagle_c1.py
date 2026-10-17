from vio import *
import cv2, sys
v=sys.argv[1] if len(sys.argv)>1 else '0028_segmented'
fr=load(v)
g=fr.astype(np.int16)
med=np.median(g[::3],axis=0).astype(np.int16)
out=[]
for k in range(len(fr)):
    d=np.abs(g[k]-med).max(axis=2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: out.append([k]+[np.nan]*7); continue
    # pick blobs: list largest two
    idx=np.argsort(-st[1:,4])[:3]+1
    row=[k]
    i=idx[0]
    row+= [cen[i][0],cen[i][1],st[i][0],st[i][1],st[i][2],st[i][3],st[i][4]]
    out.append(row)
out=np.array(out,float)
np.set_printoptions(suppress=True, precision=1, linewidth=160)
print(out[::3])
np.savetxt(W+'eagle_%s.txt'%v,out,fmt='%.2f')
