import cv2, numpy as np, sys
sys.path.insert(0,'.')
from uniq import load, dup_mask
name=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6])
keep=dup_mask(name)
frames=load(name,seg=True)
frames=[frames[i] for i in keep]
print('unique frames',len(frames))
g0=frames[0]
mask=np.zeros_like(g0); mask[y0:y1,x0:x1]=255
mask&=((g0<235).astype(np.uint8)*255)
p0=cv2.goodFeaturesToTrack(g0,400,0.01,5,mask=mask)
pts=p0.copy(); traj=[p0.reshape(-1,2)]; prev=g0; alive=np.ones(len(p0),bool)
for k in range(1,len(frames)):
    p1,st,err=cv2.calcOpticalFlowPyrLK(prev,frames[k],pts,None,winSize=(21,21),maxLevel=3)
    alive&=st.ravel()==1; traj.append(p1.reshape(-1,2)); pts=p1; prev=frames[k]
T=np.array(traj)[:,alive,:]
med=np.median(T-T[0],axis=1)
step=np.diff(med,axis=0)
print('per-frame step mean',step.mean(0),'std',step.std(0))
v=np.polyfit(np.arange(len(frames)),med,1)[0]
print('px/uframe',v,'|v|',np.hypot(*v),'px/s@24',np.hypot(*v)*24)
# mean position
print('mean pos of tracked pts frame0',T[0].mean(0), 'frame24',T[24].mean(0) if len(T)>24 else None)
