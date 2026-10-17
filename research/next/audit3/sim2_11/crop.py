import cv2,sys
v,fi,x0,y0,x1,y1,s,out=sys.argv[1],int(sys.argv[2]),*map(int,sys.argv[3:7]),float(sys.argv[7]),sys.argv[8]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); cap.set(1,fi); ok,f=cap.read()
c=f[y0:y1,x0:x1]; c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
# grid ticks every 10 px
import numpy as np
for x in range(x0 - x0%10 +10, x1, 10):
    X=int((x-x0)*s); cv2.line(c,(X,0),(X,6 if x%50 else 14),(0,0,255),1)
for y in range(y0 - y0%10 +10, y1, 10):
    Y=int((y-y0)*s); cv2.line(c,(0,Y),(6 if y%50 else 14,Y),(0,0,255),1)
cv2.imwrite(out,c)
