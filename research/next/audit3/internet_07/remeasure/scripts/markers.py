from load import load
import numpy as np, cv2
fr=[f.astype(np.float32) for f in load()]
def sub(r):
    # subpixel peak via parabola
    _,mv,_,ml=cv2.minMaxLoc(r); x,y=ml
    dx=dy=0
    if 0<x<r.shape[1]-1:
        a,b,c=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(a-c)/(a-2*b+c)
    if 0<y<r.shape[0]-1:
        a,b,c=r[y-1,x],r[y,x],r[y+1,x]; dy=0.5*(a-c)/(a-2*b+c)
    return x+dx,y+dy,mv
T={'L':(580,660,370,450),'R':(580,670,1545,1615)}
ref=60
out={}
for k,(y0,y1,x0,x1) in T.items():
    t=fr[ref][y0:y1,x0:x1] if k=='R' else fr[100][y0:y1,x0:x1]
    for i in range(len(fr)):
        S=fr[i][y0-25:y1+25,x0-25:x1+25]
        r=cv2.matchTemplate(S,t,cv2.TM_CCOEFF_NORMED)
        x,y,mv=sub(r)
        out.setdefault(i,{})[k]=(x-25,y-25,mv)
for i in range(40,114):
    L=out[i]['L'];R=out[i]['R']
    print(i,'L %+.2f %+.2f %.2f'%L,' R %+.2f %+.2f %.2f'%R)
