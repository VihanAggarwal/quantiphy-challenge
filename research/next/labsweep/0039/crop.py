import cv2, numpy as np, sys
# usage: crop.py vid frames x0 y0 w h zoom out
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
x0,y0,w,h,z=map(int,sys.argv[3:8]); out=sys.argv[8]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
i=0; tiles=[]
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames:
        t=cv2.resize(f[y0:y0+h,x0:x0+w],None,fx=z,fy=z,interpolation=cv2.INTER_NEAREST)
        # grid every 10 px
        for gx in range(0,w,10):
            cv2.line(t,(gx*z,0),(gx*z,h*z),(0,255,255) if (x0+gx)%50==0 else (0,120,120),1)
        for gy in range(0,h,10):
            cv2.line(t,(0,gy*z),(w*z,gy*z),(0,255,255) if (y0+gy)%50==0 else (0,120,120),1)
        cv2.putText(t,f'{i} ({x0},{y0})',(5,20),0,0.6,(0,0,255),2)
        tiles.append(t)
    i+=1
cv2.imwrite(out,np.hstack(tiles) if len(tiles)<=3 else np.vstack([np.hstack(tiles[k:k+3]) for k in range(0,len(tiles),3)]) )
