import cv2, numpy as np, sys
name=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{name}_segmented.mp4')
frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
g0=frames[0]
mask=np.zeros_like(g0); mask[y0:y1,x0:x1]=255
mask&=((g0<235).astype(np.uint8)*255)
p0=cv2.goodFeaturesToTrack(g0,400,0.01,5,mask=mask)
print('features',len(p0))
pts=p0.copy(); traj=[p0.reshape(-1,2)]
prev=g0; alive=np.ones(len(p0),bool)
for k in range(1,len(frames)):
    p1,st,err=cv2.calcOpticalFlowPyrLK(prev,frames[k],pts,None,winSize=(21,21),maxLevel=3)
    alive&=st.ravel()==1
    traj.append(p1.reshape(-1,2)); pts=p1; prev=frames[k]
T=np.array(traj)[:,alive,:]
print('alive',alive.sum())
d=T-T[0]
med=np.median(d,axis=1)
for k in range(0,len(frames),5): print(k,med[k].round(2))
fps=25
v=np.polyfit(np.arange(len(frames)),med,1)[0]
print('px/frame',v,'px/s',v*fps,'|v|px/s',np.hypot(*v)*fps)
