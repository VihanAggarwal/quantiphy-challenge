from common import *
import sys
def draw(img, lines, col=(0,0,255)):
    im=img.copy()
    for ln in lines:
        a,b,c=ln
        if abs(b)>abs(a):
            xs=np.array([0,2159.]); ys=-(a*xs+c)/b
        else:
            ys=np.array([0,1079.]); xs=-(b*ys+c)/a
        cv2.line(im,(int(xs[0]),int(ys[0])),(int(xs[1]),int(ys[1])),col,1,cv2.LINE_AA)
    return im
