import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
Y0=1000
F=frames('simulation_0240',Y0,1080)[:49].astype(np.float32)
bg=np.median(F,axis=0)
W=110; H=F.shape[1]
def crop(k,cx):
    M=np.float32([[1,0,-(cx-W/2)],[0,1,0]])
    return cv2.warpAffine(F[k],M,(W,H),flags=cv2.INTER_LINEAR), cv2.warpAffine(bg,M,(W,H),flags=cv2.INTER_LINEAR)
cx=np.array([614.6+6.2*k+5 for k in range(49)])
for it in range(3):
    crops=[crop(k,cx[k]) for k in range(49)]
    mean=np.mean([c[0] for c in crops],axis=0)
    # refine: match each frame's diff-weighted crop to mean via template on central region
    T=mean[20:70,25:85]
    new=[]
    for k in range(49):
        big,_=crop(k,cx[k])
        r=cv2.matchTemplate(big[20:70],T,cv2.TM_CCOEFF_NORMED)[0]
        i=np.argmax(r)
        if 0<i<len(r)-1:
            d=(r[i-1]-r[i+1])/(2*(r[i-1]-2*r[i]+r[i+1]))
        else: d=0
        new.append(cx[k]+(i+d-25))
    cx=np.array(new)
    print('iter',it,'slope',np.polyfit(np.arange(49),cx,1))
np.save if False else None
crops=[crop(k,cx[k]) for k in range(49)]
mean=np.mean([c[0] for c in crops],axis=0)
dmean=np.mean([np.abs(c[0]-c[1]).sum(axis=2) for c in crops],axis=0)
np.savetxt('rab_cx.txt',cx,fmt='%.2f')
cv2.imwrite('rab_mean.png',cv2.resize(np.clip(mean,0,255).astype(np.uint8),None,fx=6,fy=6,interpolation=cv2.INTER_CUBIC))
dm=np.clip(dmean*1.5,0,255).astype(np.uint8)
cv2.imwrite('rab_dmean.png',cv2.resize(dm,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST))
# measure on mean image: tan score and dmean
B,G,R=mean[...,0],mean[...,1],mean[...,2]
for name,img in [('dmean',dmean),('R-G',R-G)]:
    for rows in [(30,45),(35,50),(40,55),(28,58)]:
        prof=img[rows[0]:rows[1]].max(axis=0)
        lo=np.median(np.r_[prof[:10],prof[-10:]]); hi=np.percentile(prof,90)
        thr=(lo+hi)/2
        on=np.nonzero(prof>thr)[0]
        runs=np.split(on,np.nonzero(np.diff(on)>2)[0]+1); run=max(runs,key=len)
        a,b=run.min(),run.max()
        L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]); Rr=b+(thr-prof[b])/(prof[b+1]-prof[b])
        print(name,'rows',[r+Y0 for r in rows],'L',round(L,1),'R',round(Rr,1),'len',round(Rr-L,1))
print('--- fractional thresholds on dmean (rows 1028-1062)')
for fr in (0.15,0.25,0.35,0.5):
    prof=dmean[28:62].max(axis=0)
    lo=np.median(np.r_[prof[:10],prof[-10:]]); hi=np.percentile(prof,95)
    thr=lo+fr*(hi-lo)
    on=np.nonzero(prof>thr)[0]
    runs=np.split(on,np.nonzero(np.diff(on)>2)[0]+1); run=max(runs,key=lambda r: len(r))
    a,b=run.min(),run.max()
    L=a-1+(thr-prof[a-1])/(prof[a]-prof[a-1]); Rr=b+(thr-prof[b])/(prof[b+1]-prof[b])
    print(fr,'L',round(L,1),'R',round(Rr,1),'len',round(Rr-L,1))
# per-frame on aligned diff maps
lens={fr:[] for fr in (0.25,0.35,0.5)}
for c in crops:
    d=np.abs(c[0]-c[1]).sum(axis=2); d=cv2.GaussianBlur(d,(3,3),0)
    prof=d[28:62].max(axis=0)
    lo=np.median(np.r_[prof[:10],prof[-10:]]); hi=np.percentile(prof,95)
    for fr in lens:
        thr=lo+fr*(hi-lo); on=np.nonzero(prof>thr)[0]
        runs=np.split(on,np.nonzero(np.diff(on)>3)[0]+1)
        # run that overlaps center region 35-70
        cand=[r for r in runs if r.max()>40 and r.min()<65]
        if not cand: continue
        r=max(cand,key=len); a,b=r.min(),r.max()
        lens[fr].append(b-a+1)
for fr in lens: print('per-frame aligned diff frac',fr,'median',np.median(lens[fr]),'mean',np.mean(lens[fr]))
