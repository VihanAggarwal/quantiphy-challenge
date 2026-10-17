import cv2, sys
p,out,f=sys.argv[1],sys.argv[2],int(sys.argv[3]); x0,y0,x1,y1=[int(v) for v in sys.argv[4].split(',')]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
cap=cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
c=im[y0:y1,x0:x1]; c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST if sc>1 else cv2.INTER_AREA)
cv2.imwrite(out,c)
