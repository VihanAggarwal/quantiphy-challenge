import cv2,numpy as np,sys
clip=sys.argv[1]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{clip}.mp4')
G=[]
while True:
    ok,f=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
G=np.array(G); N=len(G)
med=np.median(G[1::2],axis=0).astype(np.float32)
start=1
m=(np.abs(G[start].astype(np.float32)-med)>15).astype(np.uint8)
m[:85]=0;m[-85:]=0
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); mm=(lab==k).astype(np.uint8)
mm=cv2.morphologyEx(mm,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
mm=cv2.dilate(mm,np.ones((7,7),np.uint8))
cv2.imwrite(f'frames/mask_{clip}.png',cv2.resize(mm*255,(1280,720)))
p0=cv2.goodFeaturesToTrack(G[start],maxCorners=3000,qualityLevel=0.002,minDistance=4,mask=mm*255,blockSize=5)
pts=p0.reshape(-1,2).astype(np.float32)
lk=dict(winSize=(15,15),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,0.01))
tr=np.full((len(pts),N,2),np.nan,np.float32); tr[:,start]=pts
alive=np.ones(len(pts),bool); cur=pts.copy()
for i in range(start+1,N):
    nx,s1,_=cv2.calcOpticalFlowPyrLK(G[i-1],G[i],cur,None,**lk)
    bk,s2,_=cv2.calcOpticalFlowPyrLK(G[i],G[i-1],nx,None,**lk)
    ok=(s1[:,0]==1)&(s2[:,0]==1)&(np.linalg.norm(bk-cur,axis=1)<0.4)
    alive&=ok; cur=nx; tr[alive,i]=nx[alive]
T=tr[alive]
mot=np.linalg.norm(T[:,-1]-T[:,start],axis=1)
T=T[mot>100]
np.save(f'tracks3_{clip}.npy',T)
print(clip,'kept',len(T),'of',len(pts))
