# saturation profile along the toy long axis (PCA of s>70 mask) through the centroid
import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
for pref in ('0020','0020s'):
  for i in (14,15,16):
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png')
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(float)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    m=((h>=20)&(h<=60)&(s>70)&(v>60)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); c=cen[k]
    keep=[j for j in range(1,n) if st[j,4]>15 and np.hypot(*(cen[j]-c))<60]
    ys,xs=np.nonzero(np.isin(lab,keep)); P=np.c_[xs,ys].astype(float); mu=P.mean(0)
    _,_,Vt=np.linalg.svd(P-mu); ax=Vt[0]; nr=Vt[1]
    # average saturation over a 9-px wide band along axis
    ts=np.arange(-45,46)
    prof=[]
    for t in ts:
        vals=[]
        for w in range(-4,5):
            x,y=mu+t*ax+w*nr
            vals.append(cv2.getRectSubPix(s.astype(np.float32),(1,1),(float(x),float(y)))[0,0])
        prof.append(np.max(vals))
    prof=np.array(prof)
    bg=np.median(np.r_[prof[:8],prof[-8:]]); pk=np.percentile(prof,90)
    out=[]
    for frac in (0.3,0.5,0.7):
        thr=bg+frac*(pk-bg); idx=np.nonzero(prof>thr)[0]
        out.append('%.0f%%: %d px'%(frac*100,ts[idx[-1]]-ts[idx[0]]))
    print(pref,i,'axis',ax.round(2),'bg %.0f peak %.0f'%(bg,pk),' | '.join(out))
