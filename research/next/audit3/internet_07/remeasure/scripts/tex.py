from load import load
import numpy as np, cv2, json
fr=load(gray=False)
C=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/centers.json'))
fs=np.arange(55,80)
x=np.array(C['lo']['c']); xr=np.array(C['lo']['cR']); cen=np.where(np.isnan(x),xr,x)
cen={int(f):c for f,c in zip(fs,cen)}
def sub(r):
    _,mv,_,ml=cv2.minMaxLoc(r); X,Y=ml
    dx=dy=0
    if 0<X<r.shape[1]-1:
        a,b,c=r[Y,X-1],r[Y,X],r[Y,X+1]; dx=0.5*(a-c)/(a-2*b+c)
    if 0<Y<r.shape[0]-1:
        a,b,c=r[Y-1,X],r[Y,X],r[Y+1,X]; dy=0.5*(a-c)/(a-2*b+c)
    return X+dx,Y+dy,mv
img=[cv2.GaussianBlur(f.astype(np.float32),(0,0),1.0) for f in fr]
res={}
for half in (120,150):
  for k in (1,2,3):
    out=[]
    for i in range(56,80-k):
        c=cen[i]; c2=cen[i+k]
        x0=int(round(c-half)); x1=int(round(c+half))
        if x0<5 or x1>1915: continue
        y0,y1=600,990
        T=img[i][y0:y1,x0:x1]
        pad=20
        sx0=int(round(x0+(c2-c)))-pad; sx1=sx0+(x1-x0)+2*pad
        if sx0<0 or sx1>1920: continue
        S=img[i+k][y0-8:y1+8,sx0:sx1]
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        X,Y,mv=sub(r)
        d=sx0+X-x0; dy=Y-8
        out.append((i,d,dy,mv))
    res[(half,k)]=out
    print('half',half,'k',k,' '.join('%d:%.2f(%.3f,%.1f)'%(i,d,mv,dy) for i,d,dy,mv in out))
json.dump({f'{h}_{k}':v for (h,k),v in res.items()},open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/tex.json','w'),default=float)
