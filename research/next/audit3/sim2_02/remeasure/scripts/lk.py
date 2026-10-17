import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
def lk_track(vid, box, n=49, y0=0, y1=None, minmove=0.8):
    F=frames(vid,y0,y1)[:n]
    G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in F]
    x0,yy0,x1,yy1=box
    mask=np.zeros_like(G[0]); mask[yy0-y0:yy1-y0,x0:x1]=255
    p=cv2.goodFeaturesToTrack(G[0],400,0.01,3,mask=mask)
    pts=[p.reshape(-1,2)]; st_all=np.ones(len(p),bool)
    cur=p
    for k in range(1,n):
        nxt,st,err=cv2.calcOpticalFlowPyrLK(G[k-1],G[k],cur,None,winSize=(15,15),maxLevel=3)
        back,st2,_=cv2.calcOpticalFlowPyrLK(G[k],G[k-1],nxt,None,winSize=(15,15),maxLevel=3)
        fb=np.linalg.norm((back-cur).reshape(-1,2),axis=1)
        st_all &= (st.ravel()==1)&(st2.ravel()==1)&(fb<0.5)
        pts.append(nxt.reshape(-1,2)); cur=nxt
    P=np.array(pts)  # n x m x 2
    return P, st_all
