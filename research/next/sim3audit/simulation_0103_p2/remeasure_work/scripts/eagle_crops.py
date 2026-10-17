from vio import *
import cv2, sys
v=sys.argv[1]
pts=eval(sys.argv[2])  # dict frame->(x,y)
half=int(sys.argv[3]) if len(sys.argv)>3 else 50
scale=int(sys.argv[4]) if len(sys.argv)>4 else 3
tiles=[]
fr=load(v)
for k,(x,y) in sorted(pts.items()):
    f=fr[k]; H,Wd=f.shape[:2]
    x0=max(0,int(x)-half); y0=max(0,int(y)-half)
    c=f[y0:y0+2*half, x0:x0+2*half].copy()
    c=cv2.resize(c,(2*half*scale,2*half*scale),interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(k),(3,15),0,0.5,(0,0,255),1)
    tiles.append(c)
while len(tiles)%6: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+6]) for i in range(0,len(tiles),6)]
cv2.imwrite(W+'frames/eaglecrops_%s.png'%v,np.vstack(rows))
