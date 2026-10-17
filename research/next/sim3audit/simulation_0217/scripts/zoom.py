import cv2, numpy as np, sys
v=sys.argv[1]; i=int(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7]); out=sys.argv[8]
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
cap.set(1,i); ok,f=cap.read()
c=f[y0:y1,x0:x1].copy()
c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
step=10 if (x1-x0)<300 else 50
for x in range((x0//step+1)*step,x1,step):
    X=int((x-x0)*s); cv2.line(c,(X,0),(X,8),(0,0,255),1)
    if x%(step*5)==0: cv2.putText(c,str(x),(X+2,20),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,255),1); cv2.line(c,(X,0),(X,c.shape[0]),(0,0,255),1)
for y in range((y0//step+1)*step,y1,step):
    Y=int((y-y0)*s); cv2.line(c,(0,Y),(8,Y),(255,0,0),1)
    if y%(step*5)==0: cv2.putText(c,str(y),(10,Y-2),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,0,0),1); cv2.line(c,(0,Y),(c.shape[1],Y),(255,0,0),1)
cv2.imwrite(out,c)
