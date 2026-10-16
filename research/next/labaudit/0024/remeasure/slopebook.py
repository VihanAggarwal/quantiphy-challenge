import sys; sys.path.insert(0,'.')
from linefit import *
import cv2
g=load('med_slope.png')
segs={'top':((760,352.7),(838,353.1)),'bot':((728,380.5),(800,384.6)),'left':((750,355),(724,377)),'right':((840,356.5),(810,382))}
L={}
for k,(a,b) in segs.items():
    l,pts,sd=fitline(g,a,b,half=4,n=30,trim=0.12,verbose=True)
    L[k]=l
C={'TL':inter(L['top'],L['left']),'TR':inter(L['top'],L['right']),'BL':inter(L['bot'],L['left']),'BR':inter(L['bot'],L['right'])}
for k,v in C.items(): print(k, v.round(2))
np.save('slopebook_corners.npy',np.array([C[k] for k in ['TL','TR','BR','BL']]))
img=cv2.imread('med_slope.png')
s=8;x0,y0=710,340
c=cv2.resize(img[y0:395,x0:860],None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
for k,l in L.items():
    if abs(l[1])>abs(l[0]):
        xs=np.array([710,860.]); ys=-(l[0]*xs+l[2])/l[1]
    else:
        ys=np.array([340,395.]); xs=-(l[1]*ys+l[2])/l[0]
    cv2.line(c,(int((xs[0]-x0)*s),int((ys[0]-y0)*s)),(int((xs[1]-x0)*s),int((ys[1]-y0)*s)),(0,0,255),1)
for k,v in C.items(): cv2.circle(c,(int((v[0]-x0)*s),int((v[1]-y0)*s)),6,(255,0,0),1)
cv2.imwrite('ov_slopebook.png',c)
