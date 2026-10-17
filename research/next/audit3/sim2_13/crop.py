import cv2, numpy as np, sys
c=sys.argv[1]; f=int(sys.argv[2]); x0,x1,y0,y1=[int(v) for v in sys.argv[3].split(',')]; sc=float(sys.argv[4]) if len(sys.argv)>4 else 1
tag=sys.argv[5] if len(sys.argv)>5 else ''
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
cr=im[y0:y1,x0:x1].copy()
cr=cv2.resize(cr,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
# tick marks every 50 px of original coords
for x in range((x0//50+1)*50,x1,50):
    X=int((x-x0)*sc); cv2.line(cr,(X,0),(X,12 if x%100 else 25),(0,0,255),1)
    if x%100==0: cv2.putText(cr,str(x),(X+2,24),0,0.45,(0,0,255),1)
for y in range((y0//50+1)*50,y1,50):
    Y=int((y-y0)*sc); cv2.line(cr,(0,Y),(12 if y%100 else 25,Y),(0,255,255),1)
    if y%100==0: cv2.putText(cr,str(y),(2,Y-2),0,0.45,(0,255,255),1)
cv2.imwrite(f'research/next/audit3/sim2_13/img/crop_{c}_{f}{tag}.png',cr)
