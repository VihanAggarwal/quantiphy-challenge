import cv2,numpy as np,sys
k=int(sys.argv[1]); x0,y0,x1,y1=map(int,sys.argv[2:6]); sc=float(sys.argv[6]); out=sys.argv[7]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0054.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=c.read()
t=f[y0:y1,x0:x1].copy()
t=cv2.resize(t,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
for yy in range((y0//20+1)*20,y1,20):
    Y=int((yy-y0)*sc); cv2.line(t,(0,Y),(12 if yy%100 else 30,Y),(0,0,255),1)
    if yy%100==0: cv2.putText(t,str(yy),(32,Y+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for xx in range((x0//20+1)*20,x1,20):
    X=int((xx-x0)*sc); cv2.line(t,(X,0),(X,12 if xx%100 else 30),(255,0,0),1)
    if xx%100==0: cv2.putText(t,str(xx),(X+2,42),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,0,0),1)
cv2.imwrite(out,t); print(t.shape)
