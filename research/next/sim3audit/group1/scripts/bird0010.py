import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0010_segmented.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f.astype(np.int16))
st=np.stack(fr); med=np.median(st,0)
res=[]
for i,f in enumerate(fr):
    d=np.abs(f-med).max(2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,s,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(s[1:,4]); x,y,w,h,a=s[k]
    ys,xs=np.nonzero(lab==k)
    # dark bird pixels only
    gray=cv2.cvtColor(fr[i].astype(np.uint8),cv2.COLOR_BGR2GRAY)
    dk=(lab==k)&(gray<90)
    yy,xx=np.nonzero(dk)
    res.append((i,x,y,w,h,a,xx.mean(),yy.mean(), xx.min(), xx.max()))
res=np.array(res,float)
np.save('scripts/bird0010.npy',res)
for r in res: print('%2d bbox x=%4d y=%4d w=%3d h=%3d area=%5d  cen=(%.1f,%.1f) xr=[%d,%d]'%tuple(r))
dx=np.diff(res[:,6]); print('per-frame dx', np.round(dx,1))
