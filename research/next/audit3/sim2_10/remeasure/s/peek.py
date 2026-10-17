import cv2, sys
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_10/remeasure/'
vid,fr,x0,x1,y0,y1,sc,out=sys.argv[1],int(sys.argv[2]),*map(int,sys.argv[3:7]),float(sys.argv[7]),sys.argv[8]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%vid)
c.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=c.read()
if not ok:
    c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%vid)
    for i in range(fr+1): ok,f=c.read()
cr=f[y0:y1,x0:x1]
cv2.imwrite(W+out, cv2.resize(cr,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST if sc>=2 else cv2.INTER_AREA))
