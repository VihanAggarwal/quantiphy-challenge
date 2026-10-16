import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0033/scripts')
from plane import ray
tr=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/track_x_raw.json'))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033x.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr); med=np.median(fr,axis=0).astype(np.int16)
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
out={}
for k in range(4,38):
    d=np.abs(fr[k].astype(np.int16)-med).max(axis=2).astype(float)
    for thr in (40,80,120):
        m=(d>thr).astype(np.uint8); m[690:]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: continue
        j=1+np.argmax(st[1:,4]); ys,xs=np.where(lab==j)
        cov=np.cov(np.c_[xs,ys].T); ev,evec=np.linalg.eigh(cov)
        dmin=4*np.sqrt(ev[0]); dmaj=4*np.sqrt(ev[1])
        out.setdefault(k,{})[thr]=(xs.mean(),ys.mean(),dmin,dmaj)
for k in sorted(out):
    print(k,orig(k),' '.join('thr%d c(%.1f,%.1f) min %.1f maj %.1f'%(t,*out[k][t]) for t in out[k]))
json.dump({k:{t:list(v) for t,v in out[k].items()} for k in out},open('/home/user/quantiphy-challenge/research/next/labaudit/0033/size_x.json','w'))
