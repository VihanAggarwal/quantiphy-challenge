import cv2, numpy as np, sys
vid,fi,x0,y0,x1,y1,sc,out=sys.argv[1],int(sys.argv[2]),*map(int,sys.argv[3:8]),sys.argv[8]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
for i in range(fi+1): ok,im=cap.read()
c=cv2.resize(im[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
for x in range((x0//10+1)*10,x1,10):
    X=(x-x0)*sc; cv2.line(c,(X,0),(X,8 if x%50 else 20),(0,0,255),1)
    if x%50==0: cv2.putText(c,str(x),(X+2,30),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for y in range((y0//10+1)*10,y1,10):
    Y=(y-y0)*sc; cv2.line(c,(0,Y),(8 if y%50 else 20,Y),(0,0,255),1)
    if y%50==0: cv2.putText(c,str(y),(22,Y+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(out,c)
