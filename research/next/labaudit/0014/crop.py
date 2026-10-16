import cv2, sys
# usage: crop.py in out x0 y0 x1 y1 scale
i,o,x0,y0,x1,y1,s=sys.argv[1:8]
im=cv2.imread(i); x0,y0,x1,y1=map(int,(x0,y0,x1,y1)); s=float(s)
c=im[y0:y1,x0:x1]
c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
# draw grid every 10 px of original
for x in range(x0 - x0%10 + 10, x1, 10):
    X=int((x-x0)*s); cv2.line(c,(X,0),(X,6 if x%50 else 14),(0,0,255),1)
    if x%50==0: cv2.putText(c,str(x),(X+2,24),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for y in range(y0 - y0%10 + 10, y1, 10):
    Y=int((y-y0)*s); cv2.line(c,(0,Y),(6 if y%50 else 14,Y),(0,0,255),1)
    if y%50==0: cv2.putText(c,str(y),(16,Y+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(o,c)
