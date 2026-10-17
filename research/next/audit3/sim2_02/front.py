import cv2, numpy as np, sys
def load(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); F=[]
    while True:
        ok,im=c.read()
        if not ok: break
        F.append(im)
    return F
A=load('0236'); B=load(sys.argv[1]); thr=int(sys.argv[2]) if len(sys.argv)>2 else 40
res=[]
for i in range(49):
    d=np.abs(A[i].astype(np.int16)-B[i].astype(np.int16)).sum(2)
    m=(d>thr).astype(np.uint8); m[:850]=0; m[1080:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    L=sorted([(int(st[k,4]),int(st[k,0]),int(st[k,1]),int(st[k,0]+st[k,2]),int(st[k,1]+st[k,3]),round(cen[k,0],1),round(cen[k,1],1)) for k in range(1,n) if st[k,4]>100],reverse=True)
    res.append(L[:3])
    if i in (0,12,24,36,48): print(i,L[:4])
    if i==24:
        vis=B[i][850:1100, 150:1000].copy(); vis[m[850:1100,150:1000]>0]=(0,0,255)
        cv2.imwrite(f'mask_{sys.argv[1]}_24.png',vis)
import json; json.dump(res,open(f'front_{sys.argv[1]}.json','w'))
