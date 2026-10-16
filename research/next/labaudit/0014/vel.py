import numpy as np, cv2
from tplane import N, onplane
from geo import bp
# ball pixel track from background differencing (centroid of blob) for each render
def track(R):
    bg=np.median(np.stack([cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32) for i in range(36,49)]),0)
    out={}
    for i in range(0,22):
        im=cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32)
        d=np.abs(im-bg).sum(2)
        d[:, :500]=0; d[:, 600:]=0; d[:270]=0; d[480:]=0
        m=(d>60).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<=1: continue
        k=1+np.argmax(st[1:,4])
        # weighted centroid of diff inside component
        ys,xs=np.where(lab==k); w=d[ys,xs]
        out[i]=(float((xs*w).sum()/w.sum()), float((ys*w).sum()/w.sum()), st[k][:4].tolist())
    return out
TL=(500,314);TR=(593,304);BR=(609,407);BL=(509,422)
def boardplane(c=0.89):
    bm=((BL[0]+BR[0])/2,(BL[1]+BR[1])/2+1.5); tm=((TL[0]+TR[0])/2,(TL[1]+TR[1])/2-1.5)
    P1=onplane(BL[0]-1,BL[1]+1,c); P2=onplane(BR[0]+1,BR[1]+1,c); T=bp(*tm,1.854)
    n=np.cross(P2-P1,T-P1); n/=np.linalg.norm(n)
    if n@P1>0: n=-n   # n points toward camera
    return n, n@P1, P1,P2,T
def onboard(u,v,n,d,off):
    ray=np.array([(u-640)/711,(v-360)/711,1.0])
    # plane n.X = d + off (offset toward camera means n.X larger since n toward camera... )
    s=(d+off)/(n@ray); return s*ray
if __name__=='__main__':
    import sys
    for R in ['rs','rx','ro']:
        tr=track(R)
        print(R,{k:(round(v[0],1),round(v[1],1)) for k,v in tr.items()})
