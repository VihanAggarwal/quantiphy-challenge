import cv2,numpy as np,sys,json
clip=sys.argv[1]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{clip}.mp4')
G=[]
while True:
    ok,f=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
G=np.array(G)
N=len(G)
med=np.median(G[1::2],axis=0).astype(np.float32)
def mask(i):
    if clip=='0303':
        m=(G[i]<110)
    else:
        m=np.abs(G[i].astype(np.float32)-med)>30
    m[:85]=0;m[-85:]=0
    m=m.astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # choose component with smallest y centroid among big ones (plane above shadow)
    big=[k for k in range(1,n) if st[k,4]>2000]
    k=min(big,key=lambda k:cen[k,1]) if clip=='0305' else max(big,key=lambda k:st[k,4])
    mm=(lab==k).astype(np.uint8)
    mm=cv2.dilate(mm,np.ones((5,5),np.uint8))
    return mm
start=1
m0=mask(start)
er=cv2.erode(m0,np.ones((9,9),np.uint8))
p0=cv2.goodFeaturesToTrack(G[start],maxCorners=1500,qualityLevel=0.001,minDistance=4,mask=er*255)
pts=p0.reshape(-1,2).astype(np.float32)
lk=dict(winSize=(21,21),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,0.01))
tr=np.full((len(pts),N,2),np.nan,np.float32); tr[:,start]=pts
alive=np.ones(len(pts),bool)
cur=pts.copy()
for i in range(start+1,N):
    nx,st,_=cv2.calcOpticalFlowPyrLK(G[i-1],G[i],cur,None,**lk)
    bk,st2,_=cv2.calcOpticalFlowPyrLK(G[i],G[i-1],nx,None,**lk)
    fb=np.linalg.norm(bk-cur,axis=1)
    ok=(st[:,0]==1)&(st2[:,0]==1)&(fb<0.3)
    alive&=ok
    cur=nx
    tr[alive,i]=nx[alive]
np.save(f'tracks2_{clip}.npy',tr[alive])
print(clip,'tracks alive full length',alive.sum(),'of',len(pts))
