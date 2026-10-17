import cv2, numpy as np, sys
from masks import load, mask
c=sys.argv[1] if len(sys.argv)>1 else '0304'
fr=load(c)
gr=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
# check frame 0 duplicate
print('diff01',np.abs(gr[0].astype(int)-gr[1]).mean(),'diff12',np.abs(gr[1].astype(int)-gr[2]).mean())
m,_=mask(fr[1])
er=cv2.erode(m,np.ones((25,25),np.uint8))
pts=cv2.goodFeaturesToTrack(gr[1],3000,0.005,10,mask=er)
pts=pts.reshape(-1,2)
lk=dict(winSize=(31,31),maxLevel=4,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.01))
T=len(gr)
tr=np.full((len(pts),T,2),np.nan); tr[:,1]=pts
ok=np.ones(len(pts),bool)
cur=pts.astype(np.float32)
for t in range(2,T):
    nxt,st,_=cv2.calcOpticalFlowPyrLK(gr[t-1],gr[t],cur,None,**lk)
    back,st2,_=cv2.calcOpticalFlowPyrLK(gr[t],gr[t-1],nxt,None,**lk)
    fb=np.linalg.norm(back-cur,axis=1)
    ok&=(st.ravel()==1)&(st2.ravel()==1)&(fb<0.3)
    tr[:,t]=nxt; cur=nxt
tr=tr[ok]
print('kept',ok.sum(),'of',len(ok))
np.save(f'tracks_{c}.npy',tr.astype(np.float32))
