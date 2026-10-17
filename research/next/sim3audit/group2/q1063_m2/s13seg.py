import cv2, numpy as np, json
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0013.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
bg=cv2.imread('s13/bg.png').astype(int)
res=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(int)-bg).sum(2); m=(d>45).astype(np.uint8)
    m[:550]=0; m[900:]=0; m[:, :700]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    keep=np.zeros(n,bool)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>8 and xj<x+w+30 and xj+wj>x-30 and yj<y+h+30 and yj+hj>y-30: keep[j]=True
    mm=keep[lab]; ys,xs=np.nonzero(mm)
    res.append(dict(i=i,x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),cx=float(xs.mean()),cy=float(ys.mean())))
    print(i,res[-1])
json.dump(res,open('s13/box.json','w'))
