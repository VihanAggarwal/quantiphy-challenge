from util import *
for v in ['simulation_0194','simulation_0193']:
    fr=frames(v,gray=True)
    n=len(fr)
    bg=np.median(np.stack([fr[i] for i in range(0,n,2)]),axis=0).astype(np.float32)
    P=[]
    for i in range(n):
        d=fr[i].astype(np.float32)-bg
        # outermost moon: mask far from centre
        yy,xx=np.mgrid[:1080,:1920]; r=np.hypot(xx-958,yy-543)
        dd=d.copy(); dd[(r<380)|(r>450)]=0
        m=(dd>15).astype(np.uint8)
        nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if nl<2: continue
        k=1+np.argmax(st[1:,4]); P.append((i,cen[k][0],cen[k][1],st[k,4]))
    P=np.array(P)
    xc,yc=958.0,543.0
    ang=np.unwrap(np.arctan2(P[:,2]-yc,P[:,1]-xc)); R=np.hypot(P[:,1]-xc,P[:,2]-yc)
    w=np.polyfit(P[:,0],ang,1)[0]
    print(v,'n',len(P),'R',R.mean(),'omega rad/f',w,'px/s',abs(w)*R.mean()*30,'area',np.median(P[:,3]))
    sc=0.627/(abs(w)*R.mean()*30)
    print(' scale',sc,'orbit diam',2*R.mean()*sc)
    # Jupiter diameter: threshold at half between bg and planet
    f0=fr[0].astype(np.float32)
    row=f0[543,800:1120]; col=f0[380:710,958]
    for name,p,off in (('row',row,800),('col',col,380)):
        base=np.median(np.r_[p[:30],p[-30:]]); pk=np.percentile(p,90); half=(base+pk)/2
        on=np.where(p>half)[0]; print(' Jup',name,'half-max extent',on.max()-on.min()+1, 'base',base,'pk',pk)
    m=(f0>np.median(f0)+25).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4])
    print(' Jup bbox',st[k], 'eqdiam',2*np.sqrt(st[k,4]/np.pi), 'diam m', 2*np.sqrt(st[k,4]/np.pi)*sc)
