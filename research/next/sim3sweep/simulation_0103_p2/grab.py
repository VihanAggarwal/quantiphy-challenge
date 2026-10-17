import cv2, sys, numpy as np
# usage: grab.py clip frame out [x0 y0 x1 y1 scale]
clip=sys.argv[1]; fr=int(sys.argv[2]); out=sys.argv[3]
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%clip)
cap.set(cv2.CAP_PROP_POS_FRAMES, fr)
ok,img=cap.read()
if len(sys.argv)>4:
    x0,y0,x1,y1=map(int,sys.argv[4:8]); s=float(sys.argv[8]) if len(sys.argv)>8 else 1
    img=img[y0:y1,x0:x1]
    if s!=1: img=cv2.resize(img,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST if s>1 else cv2.INTER_AREA)
cv2.imwrite(out,img)
