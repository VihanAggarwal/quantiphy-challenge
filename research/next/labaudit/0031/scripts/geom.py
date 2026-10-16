import cv2, numpy as np
fr='/home/user/quantiphy-challenge/research/next/labaudit/0031/frames/'
f=cv2.imread(fr+'rx_48.png')
m=(f.astype(float).sum(2)>60)
g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float),(5,5),1.5)
def fit(pts):
    P=np.array(pts,float); c=P.mean(0); u,s,vt=np.linalg.svd(P-c); n=vt[1]; return np.array([n[0],n[1],-n@c])
back=[];left=[];right=[];front=[];bottom=[]
for x in range(600,820,10):
    col=np.where(m[380:560,x])[0]; back.append((x,380+col[0]-0.5))
for y in range(435,476,3):
    row=np.where(m[y,:])[0]; left.append((row[0]-0.5,y))
for y in range(435,490,3):
    row=np.where(m[y,:])[0]; right.append((row[-1]+0.5,y))
prof=[]
for x in range(510,920,10):
    if 680<x<770: continue
    col=g[472:505,x]; d=np.diff(col); k=np.argmin(d); front.append((x,472+k+0.5)); prof.append((x,np.round(col).astype(int).tolist()))
    colm=np.where(m[460:560,x])[0]
for x,p in prof[:3]: print(x,p)
L={k:fit(v) for k,v in dict(back=back,left=left,right=right,front=front).items()}
def X(a,b):
    p=np.cross(a,b); return p[:2]/p[2]
C=dict(BL=X(L['back'],L['left']),BR=X(L['back'],L['right']),FR=X(L['front'],L['right']),FL=X(L['front'],L['left']))
for k,v in C.items(): print(k,v.round(1))
for k,v in L.items(): print(k, v.round(4))
print('front pts',front)
print('right pts',right)
print('left pts',left)
np.save(fr+'../scripts/corners.npy',np.array([C['BL'],C['BR'],C['FR'],C['FL']]))
