from load import load
import numpy as np, cv2, json
fr=load()
N=len(fr)
bg=np.median(np.stack(fr[96:114:2]),axis=0).astype(np.float32)
# rough cup body box from bg diff restricted to rows 700-1000 with strong threshold, use 20th-80th pct cols
box={}
for i in range(N):
    d=np.abs(fr[i].astype(np.float32)-bg)[700:1000]
    col=(d>45).mean(0)
    xs=np.where(col>0.6)[0]
    if len(xs)>30: box[i]=(int(np.percentile(xs,2)),int(np.percentile(xs,98)))
ref=100
R=fr[ref]
m=np.zeros_like(R); m[590:1075,5:1915]=255; m[60:520,5:1915]=255
p0=cv2.goodFeaturesToTrack(R,3000,0.005,10,mask=m,blockSize=9)
print('features',len(p0))
res={}
for i in range(40,N):
    q,st,_=cv2.calcOpticalFlowPyrLK(R,fr[i],p0,None,winSize=(41,41),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.01))
    pb,st2,_=cv2.calcOpticalFlowPyrLK(fr[i],R,q,None,winSize=(41,41),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.01))
    ok=(st[:,0]==1)&(st2[:,0]==1)&(np.linalg.norm(pb-p0,axis=2)[:,0]<0.2)
    x=p0[:,0,0]
    if i in box:
        x0,x1=box[i]; ok&=~((x>x0-550)&(x<x1+300))
    # exclude string band rows 500-600 in frames with string
    y=p0[:,0,1]
    if i<=75: ok&=~((y>480)&(y<600))
    A,inl=cv2.estimateAffinePartial2D(p0[ok],q[ok],method=cv2.RANSAC,ransacReprojThreshold=0.6,maxIters=5000,confidence=0.999)
    inl=inl[:,0].astype(bool)
    P=p0[ok][inl][:,0]; Q=q[ok][inl][:,0]
    s=np.hypot(A[0,0],A[1,0]); th=np.degrees(np.arctan2(A[1,0],A[0,0]))
    # displacement of reference points
    f=lambda X,Y: A@np.array([X,Y,1.0])-np.array([X,Y])
    xs=P[:,0]
    res[i]=A.tolist()
    print(i,'n %4d'%inl.sum(),'xr %4d-%4d'%(xs.min(),xs.max()),'s %.5f th %+.3f'%(s,th),'d(410,620) %+.2f %+.2f'%tuple(f(410,620)),'d(1580,620) %+.2f %+.2f'%tuple(f(1580,620)),'d(960,800) %+.2f %+.2f'%tuple(f(960,800)), 'box',box.get(i))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/sim.json','w'))
