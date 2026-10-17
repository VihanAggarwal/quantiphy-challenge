import cv2,sys
# usage: grab.py clip frame out.png [scale] [x0 y0 x1 y1]
clip,fr,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=c.read()
if len(sys.argv)>8:
    x0,y0,x1,y1=map(int,sys.argv[5:9]); f=f[y0:y1,x0:x1]
f=cv2.resize(f,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
cv2.imwrite(out,f); print(f.shape)
