import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
f=cv2.imread(f'{out}/captured_0028x_10.png')
def c(x0,y0,x1,y1,s,name):
    z=cv2.resize(f[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    for k in range(0,(x1-x0),10):
        cv2.line(z,(k*s,0),(k*s,6),(0,0,255),1)
    for k in range(0,(y1-y0),10):
        cv2.line(z,(0,k*s),(6,k*s),(0,0,255),1)
    cv2.imwrite(name,z)
c(450,410,600,530,5,'tc_left.png')
c(830,410,980,530,5,'tc_right.png')
