import cv2, numpy as np, sys
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0053.mp4'
c=cv2.VideoCapture(P); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
F=np.array(F); print(F.shape)
bg=np.median(F[::2],axis=0).astype(np.uint8)
cv2.imwrite(sys.argv[1]+'/bg53.png',cv2.resize(bg,(960,540)))
res=[]
for i,im in enumerate(F):
    d=np.abs(im.astype(np.int16)-bg.astype(np.int16)).max(2)
    m=(d>45).astype(np.uint8)
    m[:300]=0  # ignore canopy leaves at top
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append(None); continue
    # largest components
    idx=np.argsort(-st[1:,4])[:6]+1
    keep=[k for k in idx if st[k,4]>400]
    if not keep: res.append(None); continue
    big=keep[0]
    x,y,w,h,a=st[big]
    # union of components overlapping big's x-range +-80
    xs=[];ys=[];xe=[];ye=[]
    for k in keep:
        X,Y,W,H,A=st[k]
        if X< x+w+80 and X+W> x-80:
            xs.append(X);ys.append(Y);xe.append(X+W);ye.append(Y+H)
    res.append((min(xs),min(ys),max(xe),max(ye)))
for i,r in enumerate(res):
    print(i,r)
