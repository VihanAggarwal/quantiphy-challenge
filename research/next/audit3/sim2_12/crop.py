import cv2, sys
p,out=sys.argv[1],sys.argv[2]
i0=int(sys.argv[3]); x0,y0,x1,y1=[int(v) for v in sys.argv[4].split(',')]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
cap=cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_FRAMES,i0)
ok,f=cap.read()
c=f[y0:y1,x0:x1]
if sc!=1: c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
cv2.imwrite(out,c)
