import cv2,numpy as np,sys
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
v=sys.argv[1]
img=cv2.imread(f'{W}/{v}_medA.png'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float)
pts=[]
for y in range(357,384):
    xc=841-1.25*(y-356); x0=int(round(xc-4)); p=g[y,x0:x0+9]; i=int(np.argmin(p))
    if 0<i<len(p)-1:
        den=p[i-1]-2*p[i]+p[i+1]; d=(p[i-1]-p[i+1])/(2*den) if den!=0 else 0
        pts.append((x0+i+d,y))
P=np.array(pts); A=np.c_[P[:,1],np.ones(len(P))]
for it in range(3):
    k,b=np.linalg.lstsq(A,P[:,0],rcond=None)[0]; r=P[:,0]-A@[k,b]; keep=np.abs(r)<max(0.8,2.5*r.std()); P=P[keep]; A=A[keep]
print(v,'right edge x=%.4f y + %.2f sd %.2f n %d'%(k,b,r.std(),len(P)))
E=np.load(f'{W}/{v}_bookedges.npy'); E=np.vstack([E[:3],[[k,b]]]); np.save(f'{W}/{v}_bookedges.npy',E)
(kb,bb),(kl,bl),(kf,bf),(kr,br)=E
def ix(kh,bh,kv,bv): y=(kh*bv+bh)/(1-kh*kv); return np.array([kv*y+bv,y])
C=dict(BL=ix(kb,bb,kl,bl),FL=ix(kf,bf,kl,bl),FR=ix(kf,bf,kr,br),BR=ix(kb,bb,kr,br))
print({k:np.round(c,2) for k,c in C.items()})
np.save(f'{W}/{v}_bookcorners.npy',np.array([C['FL'],C['FR'],C['BR'],C['BL']]))
