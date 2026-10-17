import cv2, sys, numpy as np
p=sys.argv[1]; reff=int(sys.argv[2]); boxes=[[int(v) for v in b.split(',')] for b in sys.argv[3:]]
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY))
T=[G[reff][y0:y1,x0:x1].copy() for x0,y0,x1,y1 in boxes]
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
out=[]
for f,g in enumerate(G):
    row=[f]
    for (x0,y0,x1,y1),t in zip(boxes,T):
        m=25; sx0,sy0=max(0,x0-m),max(0,y0-m)
        S=g[sy0:min(1080,y1+m), sx0:min(1920,x1+m)]
        r=cv2.matchTemplate(S,t,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r); x,y=ml
        dx=sp(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
        dy=sp(r[y-1,x],r[y,x],r[y+1,x]) if 0<y<r.shape[0]-1 else 0
        row+= [sx0+x+dx-x0, sy0+y+dy-y0, mv]
    out.append(row)
out=np.array(out); np.savetxt(sys.argv[0].replace('tm2.py','')+'../cam_%s.txt'%p[-8:-4],out,fmt='%.3f')
for r in out[::int(sys.argv[-1]) if False else 1]:
    if r[0]%3==0: print(' '.join('%.2f'%v for v in r))
