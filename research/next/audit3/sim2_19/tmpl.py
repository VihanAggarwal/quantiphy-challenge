import cv2, numpy as np
def subpix(r, loc):
    x,y=loc
    def p(a,b,c):
        d=a-2*b+c
        return 0.0 if d==0 else 0.5*(a-c)/d
    dx=p(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
    dy=p(r[y-1,x],r[y,x],r[y+1,x]) if 0<y<r.shape[0]-1 else 0
    return x+dx,y+dy
def track(fr, f0, box, f1, pred_dx, search=60, gray=True):
    x0,y0,x1,y1=box
    a=fr[f0]; b=fr[f1]
    if a.ndim==3: a=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); b=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
    T=a[y0:y1,x0:x1].astype(np.float32)
    sx0=int(x0+pred_dx-search); sy0=max(0,y0-search)
    sx1=int(x1+pred_dx+search); sy1=min(b.shape[0],y1+search)
    sx0=max(0,sx0); sx1=min(b.shape[1],sx1)
    S=b[sy0:sy1,sx0:sx1].astype(np.float32)
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    _,mv,_,ml=cv2.minMaxLoc(r)
    px,py=subpix(r,ml)
    return sx0+px-x0, sy0+py-y0, mv
