import cv2,numpy as np,json,sys
T=json.load(open('bintrack.json'))
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
FX=frames('captured_0053x'); FP=frames(sys.argv[1] if len(sys.argv)>1 else 'captured_0053')
def binmask(i):
    F=FX[i].astype(float); gr=F[...,1]-np.maximum(F[...,0],F[...,2]); m=(gr<125).astype(np.uint8)
    yy,xx=np.mgrid[0:720,0:1280]; m[(xx-985.9)**2+(yy-369.6)**2<38**2]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    t=T[i]; k=lab[int(t['cy']),int(t['cx'])]
    if k==0: k=1+np.argmax(st[1:,4])
    return (lab==k).astype(np.uint8)
a,b=int(sys.argv[2]) if len(sys.argv)>2 else 10, int(sys.argv[3]) if len(sys.argv)>3 else 34
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in FP]
m=cv2.erode(binmask(a),np.ones((7,7),np.uint8))
p0=cv2.goodFeaturesToTrack(G[a],200,0.01,4,mask=m,blockSize=5)
pts=p0.copy(); alive=np.ones(len(pts),bool)
for i in range(a,b):
    p1,st,err=cv2.calcOpticalFlowPyrLK(G[i],G[i+1],pts,None,winSize=(15,15),maxLevel=3)
    pb,st2,_=cv2.calcOpticalFlowPyrLK(G[i+1],G[i],p1,None,winSize=(15,15),maxLevel=3)
    fb=np.linalg.norm((pb-pts).reshape(-1,2),axis=1)
    mm=binmask(i+1)
    inside=np.array([mm[int(min(max(q[1],0),719)),int(min(max(q[0],0),1279))] for q in p1.reshape(-1,2)])>0
    alive&=(st.ravel()==1)&(st2.ravel()==1)&(fb<0.7)&inside
    pts=p1
x0=p0.reshape(-1,2)[alive]; x1=pts.reshape(-1,2)[alive]
print('tracked',alive.sum(),'of',len(alive))
np.save(f'klt_{a}_{b}.npy',np.stack([x0,x1]))
