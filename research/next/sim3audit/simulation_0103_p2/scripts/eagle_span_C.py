import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from track import *
fr=frames('simulation_0044')
stack=np.stack([fr[i].astype(np.float32) for i in sorted(fr)]); bg=np.median(stack,0)
d_w=np.array([-0.403,0.915]); d_f=np.array([0.915,0.403])
res=[]
prev=(347,618)
for i in sorted(fr):
    if i>58: break
    diff=np.abs(stack[i]-bg).sum(2)
    # eagle near predicted position: x approx 118+10.3*i
    cx=118+10.3*i; cy=551+2.75*i
    x0,x1=int(cx-45),int(cx+45); y0,y1=int(cy-45),int(cy+45)
    sub=diff[y0:y1,x0:x1]
    for thr in [40,70]:
        m=(sub>thr).astype(np.uint8)
        n,l,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: continue
        # keep components within 30 px of the largest's centroid
        k=1+np.argmax(st[1:,4]); c0=cen[k]
        keep=np.zeros_like(m,bool)
        for kk in range(1,n):
            if st[kk,4]>=3 and np.hypot(*(cen[kk]-c0))<35: keep|=(l==kk)
        ys,xs=np.where(keep)
        pw=xs*d_w[0]+ys*d_w[1]; pf=xs*d_f[0]+ys*d_f[1]
        res.append((i,thr,pw.max()-pw.min()+1,pf.max()-pf.min()+1,keep.sum()))
R=np.array(res)
for thr in [40,70]:
    S=R[R[:,1]==thr]
    print('thr',thr,'span along wing axis: max %.1f, 90pct %.1f; per-frame:'%(S[:,2].max(),np.percentile(S[:,2],90)))
    print(' '.join('%d:%.0f'%(a,b) for a,b in zip(S[:,0],S[:,2])))
