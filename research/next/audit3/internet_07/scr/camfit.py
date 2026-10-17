import cv2, sys, numpy as np
p=sys.argv[1]; reff=int(sys.argv[2]); f0,f1=[int(v) for v in sys.argv[3].split(',')]; out=sys.argv[4]
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
bg=np.median(np.stack([G[i] for i in range(reff-6,reff+1,2)]),0).astype(np.uint8) if reff>=6 else G[reff]
R=G[reff]
pts=cv2.goodFeaturesToTrack(R,3000,0.005,12,blockSize=7)
print('npts',len(pts))
res=[]
for f in range(f0,f1+1):
    g=G[f]
    # mask moving object: large diff to bg
    d=cv2.absdiff(g,bg); m=(d>25).astype(np.uint8)
    m=cv2.dilate(cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)),np.ones((61,61),np.uint8))
    q,st,err=cv2.calcOpticalFlowPyrLK(R,g,pts,None,winSize=(31,31),maxLevel=3)
    back,st2,_=cv2.calcOpticalFlowPyrLK(g,R,q,None,winSize=(31,31),maxLevel=3)
    fb=np.linalg.norm(back-pts,axis=2).ravel()
    P=pts.reshape(-1,2); Q=q.reshape(-1,2)
    ok=(st.ravel()==1)&(fb<0.5)
    xi=np.clip(Q[:,0].astype(int),0,1919); yi=np.clip(Q[:,1].astype(int),0,1079)
    ok&=(m[yi,xi]==0)
    xi=np.clip(P[:,0].astype(int),0,1919); yi=np.clip(P[:,1].astype(int),0,1079)
    ok&=(m[yi,xi]==0)
    A,inl=cv2.estimateAffinePartial2D(P[ok],Q[ok],method=cv2.RANSAC,ransacReprojThreshold=1.0)
    s=np.hypot(A[0,0],A[1,0]); th=np.degrees(np.arctan2(A[1,0],A[0,0]))
    n=int(inl.sum())
    # residual stats
    res.append([f,A[0,0],A[0,1],A[0,2],A[1,0],A[1,1],A[1,2],s,n])
    if f%2==0: print(f,'n=%d s=%.5f rot=%.3f tx=%.2f ty=%.2f  shift@x=200:%.2f @960:%.2f @1700:%.2f'%(n,s,th,A[0,2],A[1,2],(A@[200,800,1])[0]-200,(A@[960,800,1])[0]-960,(A@[1700,800,1])[0]-1700))
np.savetxt(out,np.array(res),fmt='%.6f')
