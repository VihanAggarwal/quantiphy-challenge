# quick independent check: per-car axis-row profile edges (front/rear), mirror-tip y extents, template velocity
import cv2, numpy as np, sys, json
p=sys.argv[1]; rows=[int(v) for v in sys.argv[2].split(',')]  # approx axis rows of top car, bottom car
cap=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
bgv=np.median(np.stack([fr[i] for i in range(0,len(fr),6)]),axis=0).astype(np.float32)
def dist(f): return np.sqrt(((f.astype(np.float32)-bgv)**2).sum(axis=2))
out={}
for ci,r0 in enumerate(rows):
    xs_front=[];xs_rear=[]
    for i,f in enumerate(fr):
        d=dist(f)
        band=d[r0-25:r0+26].max(axis=0)   # max over a band of rows through the body
        band=cv2.GaussianBlur(band.reshape(1,-1),(1,1),0).ravel()
        on=np.nonzero(band>60)[0]
        if len(on)==0: xs_front.append(np.nan); xs_rear.append(np.nan); continue
        # biggest run
        runs=np.split(on,np.nonzero(np.diff(on)>8)[0]+1); run=max(runs,key=len)
        xs_front.append(run[0]); xs_rear.append(run[-1])
    xf=np.array(xs_front,float); xr=np.array(xs_rear,float)
    c=(xf+xr)/2; L=xr-xf+1
    t=np.arange(len(fr)); ok=(t>=3)&np.isfinite(c)&(xf>5)&(xr<1914)
    vel=np.polyfit(t[ok],c[ok],1)
    out[ci]=dict(c=c.tolist(),L=L.tolist(),vel=vel.tolist())
    print('car',ci,'vel px/f',round(vel[0],3),'c(24)',c[24],'fit',round(np.polyval(vel,24),1),'c(48)',c[48],'fit',round(np.polyval(vel,48),1),'L at f1,24,48',L[1],L[24],L[48],'minL',np.nanmin(L[ok]))
    # width: mirror tips: column through car centre region; y extent of d>60 within x window
    for i in (1,24,48):
        d=dist(fr[i]); xa,xb=int(xf[i]),int(xr[i])
        if not np.isfinite(xf[i]): continue
        col=d[max(r0-110,0):r0+110, xa:xb+1].max(axis=1)
        on=np.nonzero(col>60)[0]
        runs=np.split(on,np.nonzero(np.diff(on)>3)[0]+1)
        # run containing r0
        rr=[q for q in runs if (q[0]<=110<=q[-1])]
        if rr: print('   f',i,'width px',rr[0][-1]-rr[0][0]+1,'yrange',rr[0][0]+r0-110,rr[0][-1]+r0-110)
json.dump(out,open(sys.argv[3],'w'))
