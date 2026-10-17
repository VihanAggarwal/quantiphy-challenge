import cv2, sys, os
# usage: fr.py clip frame [x0 y0 x1 y1] [scale] [out]
clip=sys.argv[1]; f=int(sys.argv[2])
p='/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%clip
cap=cv2.VideoCapture(p)
cap.set(cv2.CAP_PROP_POS_FRAMES,f)
ok,im=cap.read()
if len(sys.argv)>6:
    x0,y0,x1,y1=map(int,sys.argv[3:7]); im=im[y0:y1,x0:x1]
s=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
if s!=1.0: im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC if s>1 else cv2.INTER_AREA)
out=sys.argv[8] if len(sys.argv)>8 else '/home/user/quantiphy-challenge/research/next/sim3sweep/group1/crops/%s_%d.png'%(clip,f)
cv2.imwrite(out,im); print(out, im.shape)
