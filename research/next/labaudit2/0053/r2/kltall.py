import cv2,numpy as np,json,sys
T=json.load(open('bintrack.json'))
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
src=sys.argv[1]; ref=int(sys.argv[2])
FX=frames('captured_0053x'); FP=frames(src)
def binmask(i):
    F=FX[i].astype(float); gr=F[...,1]-np.maximum(F[...,0],F[...,2]); m=(gr<125).astype(np.uint8)
    yy,xx=np.mgrid[0:720,0:1280]; m[(xx-985.9)**2+(yy-369.6)**2<38**2]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    t=T[i]; k=lab[int(t['cy']),int(t['cx'])]
    if k==0: k=1+np.argmax(st[1:,4])
    return (lab==k).astype(np.uint8)
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in FP]
M=[binmask(i) for i in range(48)]
m=cv2.erode(M[ref],np.ones((7,7),np.uint8))
p0=cv2.goodFeaturesToTrack(G[ref],300,0.005,4,mask=m,blockSize=5).reshape(-1,2)
N=len(p0); track=np.full((48,N,2),np.nan); track[ref]=p0
for direction in [1,-1]:
    pts=p0.copy().reshape(-1,1,2).astype(np.float32); alive=np.ones(N,bool)
    i=ref
    while 0<=i+direction<48:
        j=i+direction
        p1,st,_=cv2.calcOpticalFlowPyrLK(G[i],G[j],pts,None,winSize=(15,15),maxLevel=3)
        pb,st2,_=cv2.calcOpticalFlowPyrLK(G[j],G[i],p1,None,winSize=(15,15),maxLevel=3)
        fb=np.linalg.norm((pb-pts).reshape(-1,2),axis=1)
        q=p1.reshape(-1,2)
        inside=M[j][np.clip(q[:,1].astype(int),0,719),np.clip(q[:,0].astype(int),0,1279)]>0
        alive&=(st.ravel()==1)&(st2.ravel()==1)&(fb<0.8)&inside
        track[j][alive]=q[alive]
        pts=p1; i=j
print('alive per frame',[int((~np.isnan(track[k,:,0])).sum()) for k in range(48)])
np.save(f'track_{src}_{ref}.npy',track)
