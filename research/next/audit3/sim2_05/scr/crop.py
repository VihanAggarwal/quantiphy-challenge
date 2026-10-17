import cv2, sys, numpy as np
v=sys.argv[1]; fi=int(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]) if len(sys.argv)>7 else 3
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,f=c.read()
cr=f[y0:y1,x0:x1]
cr=cv2.resize(cr,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
# grid every 10 px
for gx in range(0,x1-x0,10):
    cv2.line(cr,(int(gx*sc),0),(int(gx*sc),5),(0,0,255),1)
for gy in range(0,y1-y0,10):
    cv2.line(cr,(0,int(gy*sc)),(5,int(gy*sc)),(0,0,255),1)
cv2.imwrite(sys.argv[8] if len(sys.argv)>8 else f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/crop_{v}_{fi}.png',cr)
