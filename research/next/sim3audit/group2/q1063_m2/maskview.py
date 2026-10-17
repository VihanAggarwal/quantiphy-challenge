from load import frames; import numpy as np, cv2, json, sys
F=frames(); bg=cv2.imread('bg.png').astype(int)
ids=[int(a) for a in sys.argv[2].split(',')]; thr=int(sys.argv[3]) if len(sys.argv)>3 else 40
T=json.load(open('track.json'))
tiles=[];info=[]
for i in ids:
    t=T[i]; cx=int((t['x0']+t['x1'])/2); cy=int((t['y0']+t['y1'])/2); hw,hh=95,60
    x0,y0=cx-hw,cy-hh
    crop=F[i][y0:y0+2*hh,x0:x0+2*hw].astype(int); d=np.abs(crop-bg[y0:y0+2*hh,x0:x0+2*hw]).sum(2)
    m=(d>thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mm=(lab==k).astype(np.uint8)
    ys,xs=np.nonzero(mm)
    L=np.argmin(xs); R=np.argmax(xs)
    info.append((i,(xs[L]+x0,ys[L]+y0),(xs[R]+x0,ys[R]+y0)))
    c=cv2.resize(F[i][y0:y0+2*hh,x0:x0+2*hw],None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC)
    cnt,_=cv2.findContours(cv2.resize(mm,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(c,cnt,-1,(0,0,255),1)
    for (px,py) in [(xs[L],ys[L]),(xs[R],ys[R])]: cv2.circle(c,(int(px*4+2),int(py*4+2)),6,(0,255,255),2)
    cv2.putText(c,f'{i} org=({x0},{y0})',(10,25),0,0.7,(255,255,0),2)
    tiles.append(c)
while len(tiles)%2: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(sys.argv[1],np.vstack([np.hstack(tiles[k:k+2]) for k in range(0,len(tiles),2)]))
for r in info: print(r)
