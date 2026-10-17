import cv2,numpy as np,sys
v=sys.argv[1]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f[550:800,0:1100].copy())   # cat region rows
F=np.array(F)
bg=np.median(F,axis=0).astype(np.int16)
res=[]
for i,f in enumerate(F):
    g=f.astype(np.int16)
    d=np.abs(g-bg).sum(2)
    dark=(f.astype(int).sum(2)<150)
    m=((d>40)&dark).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    # merge components near largest
    x,y,w,h,a=st[k]
    sel=np.zeros_like(m)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>15 and xj<x+w+30 and xj+wj>x-30 and yj<y+h+30 and yj+hj>y-30: sel|=(lab==j)
    ys,xs=np.nonzero(sel)
    res.append((i,xs.min(),xs.max(),ys.min()+550,ys.max()+550,len(xs)))
for r in res: print(*r, 'w',r[2]-r[1]+1,'h',r[4]-r[3]+1)
np.save('/dev/null',0)
