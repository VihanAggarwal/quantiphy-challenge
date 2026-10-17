import cv2, sys, numpy as np
p=sys.argv[1]; boxes=[[int(v) for v in b.split(',')] for b in sys.argv[2:]]  # x0,y0,x1,y1 template in frame0
cap=cv2.VideoCapture(p); f=0; T=None
while True:
    ok,im=cap.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    if T is None: T=[g[y0:y1,x0:x1].copy() for x0,y0,x1,y1 in boxes]
    res=[]
    for (x0,y0,x1,y1),t in zip(boxes,T):
        m=20; sx0,sy0=max(0,x0-m),max(0,y0-m)
        S=g[sy0:y1+m, sx0:x1+m]
        r=cv2.matchTemplate(S,t,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
        # subpixel
        x,y=ml
        def sp(a,b,c): d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
        dx=sp(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
        dy=sp(r[y-1,x],r[y,x],r[y+1,x]) if 0<y<r.shape[0]-1 else 0
        res.append((sx0+x+dx-x0, sy0+y+dy-y0, mv))
    if f%5==0: print(f, ' '.join('%.2f,%.2f(%.2f)'%r for r in res))
    f+=1
