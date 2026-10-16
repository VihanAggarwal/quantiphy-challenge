import sys; sys.path.insert(0,'.')
from linefit import *
g=load('med_end.png')
segs={'top':((765,359.8),(848,361)),'bot':((622,472),(698,491)),'left':((622,459),(740,368)),'right':((720,483),(848,373))}
L={}
for k,(a,b) in segs.items():
    l,pts,sd=fitline(g,a,b,half=6,verbose=True)
    L[k]=l
    print(k, l, sd)
C={'TL':inter(L['top'],L['left']),'TR':inter(L['top'],L['right']),'BL':inter(L['bot'],L['left']),'BR':inter(L['bot'],L['right'])}
for k,v in C.items(): print(k, v.round(2))
np.save('board_lines.npy',np.array([L[k] for k in ['top','bot','left','right']]))
img=cv2.imread('med_end.png')
s=3;x0,y0=580,330
c=cv2.resize(img[y0:510,x0:880],None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
for k,l in L.items():
    xs=np.array([580,880.]);
    if abs(l[1])>abs(l[0]):
        ys=-(l[0]*xs+l[2])/l[1]
    else:
        ys=np.array([330,510.]); xs=-(l[1]*ys+l[2])/l[0]
    cv2.line(c,(int((xs[0]-x0)*s),int((ys[0]-y0)*s)),(int((xs[1]-x0)*s),int((ys[1]-y0)*s)),(0,0,255),1)
for k,v in C.items(): cv2.circle(c,(int((v[0]-x0)*s),int((v[1]-y0)*s)),4,(255,0,0),1)
cv2.imwrite('ov_board.png',c)
