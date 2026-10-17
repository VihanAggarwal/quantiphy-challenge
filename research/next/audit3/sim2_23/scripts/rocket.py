import cv2, numpy as np, sys
v=sys.argv[1]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
f0=fr[0].astype(int)
th=np.deg2rad(39.08)
d=np.array([-np.cos(th), -np.sin(th)])  # up-left direction (image y down)
for i,f in enumerate(fr):
    diff=np.abs(f.astype(int)-f0).max(2)
    m=(diff>40).astype(np.uint8)
    m[:, :]=m
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    ys,xs=np.nonzero(lab==k)
    p=xs*d[0]+ys*d[1]
    q=-xs*d[1]+ys*d[0]
    print(i, 'area',st[k,4],'bbox',st[k,:4].tolist(),'along min/max %.1f %.1f len %.1f'%(p.min(),p.max(),p.max()-p.min()),'perp %.1f..%.1f'%(q.min(),q.max()))
