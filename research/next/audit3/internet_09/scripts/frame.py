import cv2,sys
# usage: frame.py vid frame out [scale] [x0 y0 x1 y1]
vid,fi,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.25
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{vid}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,f=c.read()
if len(sys.argv)>8:
    x0,y0,x1,y1=map(int,sys.argv[5:9]); f=f[y0:y1,x0:x1]
f=cv2.resize(f,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
cv2.imwrite(out,f)
