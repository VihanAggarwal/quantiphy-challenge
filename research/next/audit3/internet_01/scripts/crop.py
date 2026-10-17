import cv2, numpy as np, sys
# usage: crop.py video frame x0 y0 x1 y1 scale gridstep out
V,f,x0,y0,x1,y1,s,gs,out=sys.argv[1:10]
f,x0,y0,x1,y1,gs=map(int,(f,x0,y0,x1,y1,gs)); s=float(s)
c=cv2.VideoCapture(V); c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
cr=im[y0:y1,x0:x1].copy()
cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC if s>1 else cv2.INTER_AREA)
for x in range((x0//gs+1)*gs,x1,gs):
    X=int((x-x0)*s); col=(0,255,255) if x%(gs*5)==0 else (0,160,0)
    cv2.line(cr,(X,0),(X,8 if x%(gs*5) else 20),col,1)
    if x%(gs*5)==0: cv2.putText(cr,str(x),(X+2,30),0,0.45,col,1)
for y in range((y0//gs+1)*gs,y1,gs):
    Y=int((y-y0)*s); col=(0,255,255) if y%(gs*5)==0 else (0,160,0)
    cv2.line(cr,(0,Y),(8 if y%(gs*5) else 20,Y),col,1)
    if y%(gs*5)==0: cv2.putText(cr,str(y),(22,Y+4),0,0.45,col,1)
cv2.imwrite(out,cr)
