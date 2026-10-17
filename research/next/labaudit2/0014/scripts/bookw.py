import cv2, numpy as np, sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
from tplane import *
BC=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/book_corners.json'))
f=711.; n,cP,_,_,_=pose(f)
def sample(img,pts):
    m=pts.astype(np.float32)
    return cv2.remap(img,m[:,0].reshape(1,-1),m[:,1].reshape(1,-1),cv2.INTER_LINEAR)[0]
for r in ['','s','x']:
    fr=load(r)
    im=np.median(np.stack([f_.astype(np.float32) for f_ in fr[30:49]]),0)
    feat=(im[...,0]-im[...,2]).astype(np.float32)  # B-R
    TR,BR,BL,TL=[np.array(p) for p in BC[r or 'o']]
    wdir=((TR-TL)+(BR-BL)); wdir/=np.linalg.norm(wdir)
    out=[]
    for fr_ in np.linspace(0.15,0.85,8):
        a=TL+(BL-TL)*fr_; b=TR+(BR-TR)*fr_; mid=(a+b)/2
        ts=np.arange(-35,35,0.25); pts=mid[None,:]+ts[:,None]*wdir[None,:]
        p=sample(feat,pts)
        inside=np.median(p[np.abs(ts)<8]); outside=np.median(np.r_[p[:20],p[-20:]])
        half=(inside+outside)/2
        # left edge: last crossing going outward from centre
        i0=np.argmin(np.abs(ts))
        li=i0
        while li>0 and p[li]>half: li-=1
        ri=i0
        while ri<len(p)-1 and p[ri]>half: ri+=1
        # subpixel
        def cross(i,j):
            return ts[i]+(half-p[i])/(p[j]-p[i])*(ts[j]-ts[i])
        tl=cross(li,li+1); tr=cross(ri-1,ri)
        A=mid+tl*wdir; Bp=mid+tr*wdir
        XA=inter(*A,n,0.895-0.0146,f); XB=inter(*B_,n,0.895-0.0146,f) if False else inter(*Bp,n,0.895-0.0146,f)
        out.append((fr_,tr-tl,100*np.linalg.norm(XA-XB), 100*np.linalg.norm(bp(*A,1.665)-bp(*Bp,1.665))))
    o=np.array(out)
    print(r or 'o','px widths',np.round(o[:,1],1),'| plane(label c) cm',np.round(o[:,2],2),'median',round(np.median(o[:,2]),2),'| single-depth 1.665 median',round(np.median(o[:,3]),2))
