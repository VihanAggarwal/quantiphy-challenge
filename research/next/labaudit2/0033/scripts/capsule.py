# Fit a capsule (segment p0-p1, radius r) to the ball mask by maximising IoU (coarse-to-fine random search).
import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0033/scripts')
from geo import *
R=sys.argv[1] if len(sys.argv)>1 else 'x'
p='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4'%('' if R=='o' else R)
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr); med=np.median(fr,axis=0).astype(np.int16)
T=load_track(R)
H,W=720,1280
yy,xx=np.mgrid[0:H,0:W]
def capsule_mask(p0,p1,r,box):
    x0,y0,x1,y1=box
    X=xx[y0:y1,x0:x1].astype(float); Y=yy[y0:y1,x0:x1].astype(float)
    d=p1-p0; L2=d@d+1e-9
    t=np.clip(((X-p0[0])*d[0]+(Y-p0[1])*d[1])/L2,0,1)
    D=np.hypot(X-(p0[0]+t*d[0]),Y-(p0[1]+t*d[1]))
    return D<=r
out={}
rng=np.random.default_rng(0)
frames=[int(a) for a in sys.argv[2].split(',')] if len(sys.argv)>2 else sorted(T)
for k in frames:
    e=T[k]
    d=np.abs(fr[k].astype(np.int16)-med).max(axis=2)
    m=(d>35).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    kk=np.argmin([np.hypot(cen[j,0]-e['cx'],cen[j,1]-e['cy']) if j>0 else 1e9 for j in range(n)])
    mk=(lab==kk)
    x,y,w,h=st[kk,:4]; pad=40
    box=(max(x-pad,0),max(y-pad,0),min(x+w+pad,W),min(y+h+pad,H))
    M=mk[box[1]:box[3],box[0]:box[2]]
    ys,xs=np.nonzero(mk); P=np.c_[xs,ys].astype(float); mu=P.mean(0)
    C=np.cov((P-mu).T); ev,V=np.linalg.eigh(C); a=V[:,1]
    pr=(P-mu)@a; L=np.percentile(pr,99.5)-np.percentile(pr,0.5)
    r0=np.sqrt(ev[0])*2.0
    best=None
    def score(p0,p1,r):
        S=capsule_mask(p0,p1,r,box)
        inter=(S&M).sum(); uni=(S|M).sum(); return inter/uni
    p0=mu-a*max(L/2-r0,0); p1=mu+a*max(L/2-r0,0); r=r0
    s=score(p0,p1,r); best=(s,p0,p1,r)
    for it in range(1500):
        sc=3.0 if it<600 else (1.0 if it<1200 else 0.4)
        q0=best[1]+rng.normal(0,sc,2); q1=best[2]+rng.normal(0,sc,2); rr=best[3]+rng.normal(0,sc*0.5)
        if rr<3: continue
        s=score(q0,q1,rr)
        if s>best[0]: best=(s,q0,q1,rr)
    s,p0,p1,r=best
    if p0[1]>p1[1]: p0,p1=p1,p0
    mid=(p0+p1)/2
    out[k]=dict(p0=p0.tolist(),p1=p1.tolist(),r=float(r),iou=float(s),mid=mid.tolist(),cap=cap(k))
    print(k,'c%d'%cap(k),'IoU %.3f r %.1f (d %.1f) p0 (%.1f,%.1f) p1 (%.1f,%.1f) mid (%.1f,%.1f) len %.1f'%(s,r,2*r,p0[0],p0[1],p1[0],p1[1],mid[0],mid[1],np.linalg.norm(p1-p0)))
json.dump(out,open(BASE+'capsule_%s.json'%R,'w'),indent=0)
