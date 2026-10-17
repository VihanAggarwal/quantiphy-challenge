import cv2, sys
c=sys.argv[1]; fr=int(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
name=sys.argv[8] if len(sys.argv)>8 else f'{c}_f{fr}_{x0}_{y0}'
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,fr)
ok,f=cap.read()
cr=f[y0:y1,x0:x1].copy()
# grid lines every 20 px (in source coords) with labels every 100
import numpy as np
cr=cv2.resize(cr,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
for xx in range((x0//20+1)*20, x1, 20):
    X=int((xx-x0)*sc); col=(0,0,255) if xx%100==0 else (0,255,255)
    cv2.line(cr,(X,0),(X,6 if xx%100 else 14),col,1)
    if xx%100==0: cv2.putText(cr,str(xx),(X+2,24),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for yy in range((y0//20+1)*20, y1, 20):
    Y=int((yy-y0)*sc); col=(0,0,255) if yy%100==0 else (0,255,255)
    cv2.line(cr,(0,Y),(6 if yy%100 else 14,Y),col,1)
    if yy%100==0: cv2.putText(cr,str(yy),(16,Y+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_01/png/{name}.png',cr)
