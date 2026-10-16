import cv2, sys
# usage: crop.py frame x0 y0 x1 y1 scale out
f,x0,y0,x1,y1,s,out=sys.argv[1:8]
im=cv2.imread(f)
c=im[int(y0):int(y1),int(x0):int(x1)]
c=cv2.resize(c,None,fx=float(s),fy=float(s),interpolation=cv2.INTER_CUBIC)
cv2.imwrite(out,c)
