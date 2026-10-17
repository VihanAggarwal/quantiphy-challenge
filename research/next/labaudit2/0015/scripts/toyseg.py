import cv2, numpy as np, sys, json
from common import load
def toymask(f, hmin=10, smin=85):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    H,S,Vv=hsv[...,0],hsv[...,1],hsv[...,2]
    brown=(H>=hmin)&(H<=26)&(S>=smin)&(Vv>=35)&(Vv<=215)
    dark=(H<=26)&(S>=110)&(Vv>=25)&(Vv<110)
    m=(brown|dark).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    return m
def blob(f, roi, seed=None, **kw):
    x0,y0,x1,y1=roi
    m=toymask(f,**kw); mm=np.zeros_like(m); mm[y0:y1,x0:x1]=m[y0:y1,x0:x1]
    n,lab,st,cen=cv2.connectedComponentsWithStats(mm)
    if n<2: return None
    if seed is None: k=1+np.argmax(st[1:,4])
    else:
        d=[np.hypot(*(cen[k]-seed)) if st[k,4]>150 else 1e9 for k in range(1,n)]; k=1+int(np.argmin(d))
    ys,xs=np.nonzero(lab==k)
    return dict(cx=float(xs.mean()),cy=float(ys.mean()),l=int(xs.min()),r=int(xs.max()),t=int(ys.min()),b=int(ys.max()),a=int(len(xs)),bx=(xs.min()+xs.max())/2,by=(ys.min()+ys.max())/2), lab==k
if __name__=='__main__':
    tag=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); roi=tuple(map(int,sys.argv[4:8])); out=sys.argv[8]
    fr=load(tag); ims=[]; prev=None
    for i in range(a,b+1):
        r=blob(fr[i],roi,seed=prev)
        if r is None: print(i,'none'); continue
        d,m=r; prev=np.array([d['cx'],d['cy']])
        print(i,{k:(round(v,1) if isinstance(v,float) else v) for k,v in d.items()})
        x0,y0,x1,y1=roi
        v=fr[i][y0:y1,x0:x1].copy(); mm=m[y0:y1,x0:x1]
        v[mm]=(0.5*v[mm]+0.5*np.array([255,0,255])).astype(np.uint8)
        cv2.circle(v,(int(d['cx']-x0),int(d['cy']-y0)),3,(0,255,0),-1)
        cv2.putText(v,str(i),(3,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1); ims.append(v)
    cols=min(len(ims),8)
    while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
    cv2.imwrite(out,np.vstack([np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]))
