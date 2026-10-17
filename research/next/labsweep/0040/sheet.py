import cv2, numpy as np, sys
vid=sys.argv[1]; fr=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1=[int(v) for v in sys.argv[3].split(',')]
sc=float(sys.argv[4]); ncol=int(sys.argv[5]); out=sys.argv[6]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_%s.mp4'%vid)
i=0; tiles=[]
while True:
    ok,f=c.read()
    if not ok: break
    if i in fr:
        t=cv2.resize(f[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST if sc>1 else cv2.INTER_AREA)
        cv2.putText(t,str(i),(5,20),0,0.6,(0,0,255),2)
        tiles.append(t)
    i+=1
while len(tiles)%ncol: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+ncol]) for k in range(0,len(tiles),ncol)]
cv2.imwrite(out,np.vstack(rows))
