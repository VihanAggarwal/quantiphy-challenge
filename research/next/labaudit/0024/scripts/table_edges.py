import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
im=cv2.imread(D+'frames/x00.png').astype(float)
g=im.mean(2)
mask=g>25
# top boundary per column
top={}
for x in range(405,1110):
    ys=np.where(mask[380:700,x])[0]
    if len(ys): top[x]=380+ys[0]
for x in list(range(410,620,20))+list(range(860,1110,20)): print('top',x,top.get(x))
# vertical profile of brightness along columns to find surface/side boundary
for x in [420,450,500,550,600,620,700,800,900,1000,1050,1080]:
    col=g[440:640,x]
    d=np.diff(cv2.GaussianBlur(col.reshape(-1,1),(1,5),0).ravel())
    # strongest negative step (surface -> darker side) below the top
    t=top.get(x,440)
    rng=np.arange(len(d))+440
    sel=(rng>t+3)
    i=np.argmin(np.where(sel,d,0))
    print('x',x,'top',t,'side step at',rng[i],'d',round(d[i],1),'bottom',440+np.where(mask[440:640,x])[0][-1])
