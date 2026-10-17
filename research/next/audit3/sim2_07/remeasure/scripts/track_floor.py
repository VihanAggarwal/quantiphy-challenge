import cv2, numpy as np, sys, json
vid=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
# background: per-pixel median over all frames (ball moves fast)
bg=np.median(np.stack(fr),axis=0).astype(np.float32)
res=[]
for i,f in enumerate(fr):
    d=bg[...,0]-f[...,0].astype(np.float32)
    m=(d>25).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    if a<50 or x<2 or x+w>f.shape[1]-2: continue
    x0,y0,x1,y1=max(0,x-4),max(0,y-4),x+w+4,y+h+4
    W=np.clip(d[y0:y1,x0:x1],0,None); core=np.median(W[W>0.7*W.max()]); Wt=np.clip(W-0.3*core,0,None)
    yy,xx=np.mgrid[y0:y1,x0:x1]
    res.append((i,float((Wt*xx).sum()/Wt.sum()),float((Wt*yy).sum()/Wt.sum()),float(2*np.sqrt((W>=core/2).sum()/np.pi))))
R=np.array(res); t=R[:,0]/24; x=R[:,1]
print(vid,'frames',int(R[0,0]),'-',int(R[-1,0]),'y mean',R[:,2].mean().round(2),'eqd median',np.median(R[:,3]).round(2))
for deg in (2,3):
    p=np.polyfit(t,x,deg); r=x-np.polyval(p,t); print(' deg',deg,'rms',r.std().round(3),'a(t) at 0.5,1,1.5:',[round(np.polyval(np.polyder(p,2),q),1) for q in (0.5,1,1.5)],'v:',[round(np.polyval(np.polyder(p),q),1) for q in (0.5,1,1.5)])
# quadratic drag model: v' = -c v^2 -> v=v0/(1+c v0 t), x=x0+ln(1+c v0 t)/c
best=None
for c_ in np.linspace(0,6e-4,601):
    for v0 in np.linspace(600,2000,1401):
        X=np.log1p(c_*v0*t)/c_ if c_>0 else v0*t
        off=(x-X).mean(); e=((x-X-off)**2).sum()
        if best is None or e<best[0]: best=(e,c_,v0)
e,c_,v0=best
print(' quad-drag fit: c=%.3e /px v0=%.1f rms=%.3f'%(c_,v0,np.sqrt(e/len(t))), 'decel at 0.5,1,1.5:',[round(c_*(v0/(1+c_*v0*q))**2,1) for q in (0.5,1,1.5)])
json.dump(res,open(f'track_{vid}.json','w'))
