from load import *
import numpy as np, sys
c=sys.argv[1]
F=frames(c)
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in F]
print('dup0-1', np.abs(G[0].astype(int)-G[1].astype(int)).mean(), np.abs(G[1].astype(int)-G[2].astype(int)).mean())
Mp=np.load('masks0303_packed.npy')
H,W=G[0].shape
def mk(i): return np.unpackbits(Mp[i])[:H*W].reshape(H,W)
m=mk(1)
me=cv2.erode(m,np.ones((5,5),np.uint8))
pts=cv2.goodFeaturesToTrack(G[1],maxCorners=600,qualityLevel=0.005,minDistance=6,mask=me*255,blockSize=7)
P=np.full((len(F),len(pts),2),np.nan)
P[1]=pts[:,0]
cur=pts.astype(np.float32); alive=np.ones(len(pts),bool)
lk=dict(winSize=(21,21),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,0.01))
for i in range(2,len(F)):
    nxt,st,err=cv2.calcOpticalFlowPyrLK(G[i-1],G[i],cur,None,**lk)
    back,st2,_=cv2.calcOpticalFlowPyrLK(G[i],G[i-1],nxt,None,**lk)
    fb=np.linalg.norm(back-cur,axis=2)[:,0]
    ok=(st[:,0]==1)&(st2[:,0]==1)&(fb<0.3)
    # must be inside mask (dilated)
    mi=cv2.dilate(mk(i),np.ones((3,3),np.uint8))
    xy=np.round(nxt[:,0]).astype(int)
    inside=(xy[:,0]>=0)&(xy[:,0]<W)&(xy[:,1]>=0)&(xy[:,1]<H)
    inside[inside]=mi[xy[inside,1],xy[inside,0]]>0
    alive&=ok&inside
    P[i,alive]=nxt[alive,0]
    cur=nxt
print(c,'tracks',len(pts),'alive to end',alive.sum(), 'alive to 48', np.isfinite(P[48,:,0]).sum())
np.save(f'tracks_{c}.npy',P)
