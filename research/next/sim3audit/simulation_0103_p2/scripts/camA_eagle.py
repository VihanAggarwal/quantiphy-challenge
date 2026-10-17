import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *; from geom import *
fr=frames('simulation_0028_segmented')
stack=np.stack([fr[i].astype(np.float32) for i in sorted(fr)])
bg=np.median(stack,0)
res={}
for i in sorted(fr):
    d=np.abs(stack[i]-bg).sum(2)>60
    d=cv2.morphologyEx(d.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(d)
    comps=sorted([(st[k][4],k) for k in range(1,n) if st[k][4]>15],reverse=True)
    if comps:
        a,k=comps[0]; res[i]=(cen[k][0],cen[k][1],a,tuple(int(v) for v in st[k][:4]))
for i in sorted(res):
    if i%2==0: print(i,np.round(res[i][:2],1),res[i][2],res[i][3])
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/eagle0028.npy',np.array([[i,*res[i][:3],*res[i][3]] for i in sorted(res)]))
