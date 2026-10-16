import cv2, numpy as np
fr='/home/user/quantiphy-challenge/research/next/labaudit/0029/frames/'
f=cv2.imread(fr+'rx_48.png')
m=(f.astype(float).sum(2)>60)
g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float),(5,5),1.5)
def fit(pts):  # returns line a x + b y + c = 0 via total least squares
    P=np.array(pts,float); c=P.mean(0); u,s,vt=np.linalg.svd(P-c); n=vt[1]; return np.array([n[0],n[1],-n@c])
back=[];left=[];right=[];front=[]
for x in range(600,900,10):
    col=np.where(m[380:560,x])[0]; back.append((x,380+col[0]-0.5))
for y in range(468,532,4):
    row=np.where(m[y,:])[0]; left.append((row[0]-0.5,y))
for y in range(480,566,4):
    row=np.where(m[y,:])[0]; right.append((row[-1]+0.5,y))
for x in range(260,1100,20):
    col=g[500:620,x]; d=np.diff(col); k=np.argmin(d); front.append((x,500+k+0.5))
L={k:fit(v) for k,v in dict(back=back,left=left,right=right,front=front).items()}
def X(a,b):
    p=np.cross(a,b); return p[:2]/p[2]
C=dict(BL=X(L['back'],L['left']),BR=X(L['back'],L['right']),FR=X(L['front'],L['right']),FL=X(L['front'],L['left']))
for k,v in C.items(): print(k,v.round(1))
for k,v in L.items(): print(k, v.round(4))
print('right pts',right)
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/corners.npy',np.array([C['BL'],C['BR'],C['FR'],C['FL']]))
