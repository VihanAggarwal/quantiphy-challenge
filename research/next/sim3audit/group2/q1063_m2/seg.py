from load import frames; import numpy as np, cv2, json
F=frames(); bg=cv2.imread('bg.png').astype(int)
res=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(int)-bg).sum(2)
    m=(d>45).astype(np.uint8)
    m[:, :500]=0; m[1250:]=0; m[:900]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append(None); continue
    k=1+np.argmax(st[1:,4])
    # merge components near the largest
    x,y,w,h,a=st[k]
    keep=np.zeros(n,bool)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>8 and xj<x+w+40 and xj+wj>x-40 and yj<y+h+40 and yj+hj>y-40: keep[j]=True
    mm=keep[lab]
    ys,xs=np.nonzero(mm)
    res.append(dict(i=i,x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),cx=float(xs.mean()),cy=float(ys.mean()),area=int(mm.sum())))
json.dump(res,open('birdbox.json','w'))
for r in res: print(r)
