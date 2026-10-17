import cv2,numpy as np,json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0053x.mp4')
res=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    F=f.astype(float)
    gr=F[...,1]-np.maximum(F[...,0],F[...,2])
    al=np.clip(1-gr/250,0,1)
    al[690:,1020:]=0   # watermark
    # blue-ish object: b > r
    blue=(F[...,0]>F[...,2]+20)&(al>0.5)
    m=(al>0.5).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # pick component overlapping most blue pixels
    best=None;bs=0
    for k in range(1,n):
        s=(blue&(lab==k)).sum()
        if s>bs: bs=s;best=k
    comp=(lab==best)
    # if ball merged, remove orange pixels (r > b+30)
    orange=(F[...,2]>F[...,0]+40)&(F[...,2]>F[...,1]+10)
    yy,xx=np.mgrid[0:720,0:1280]; disk=(xx-985.9)**2+(yy-369.6)**2<36**2
    obj=comp&~disk
    ys,xs=np.nonzero(obj)
    a=al*obj
    cxw=(a*np.arange(1280)[None,:]).sum()/a.sum(); cyw=(a*np.arange(720)[:,None]).sum()/a.sum()
    x0,y0,w,h=cv2.boundingRect(obj.astype(np.uint8))
    res.append(dict(i=i,cx=cxw,cy=cyw,area=float(a.sum()),bx=x0,by=y0,bw=w,bh=h,merged=bool((comp&disk).sum()>5)))
    if i in (9,10,11,33,34,35,36):
        cv2.imwrite(f'bin_{i:02d}.png',np.where(obj[...,None],f,0)[max(y0-10,0):y0+h+10,max(x0-10,0):x0+w+10])
    i+=1
json.dump(res,open('bintrack.json','w'),indent=0)
prev=None
for r in res:
    st='' if prev is None else f"step {np.hypot(r['cx']-prev['cx'],r['cy']-prev['cy']):6.2f}"
    print(f"{r['i']:2d} cx {r['cx']:7.2f} cy {r['cy']:7.2f} area {r['area']:7.0f} bbox {r['bx']},{r['by']},{r['bw']}x{r['bh']} {'M' if r['merged'] else ''} {st}")
    prev=r
