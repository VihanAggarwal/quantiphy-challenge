import cv2,numpy as np
f=cv2.imread('img/cx_48.png').astype(float)
g=f.sum(2); m=g>60
def topb(xs):
    pts=[]
    for x in xs:
        col=np.nonzero(m[300:700,x])[0]; 
        # subpixel: interpolate threshold crossing
        y=300+col[0]; pts.append((x, y-0.5))
    return np.array(pts,float)
def fit(p): # y = a x + b
    A=np.c_[p[:,0],np.ones(len(p))]; sol,res,_,_=np.linalg.lstsq(A,p[:,1],rcond=None); 
    r=p[:,1]-A@sol; return sol, r.std()
back=fit(topb(range(480,900,4)))
left=fit(topb(range(225,425,4)))
right=fit(topb(range(940,1120,4)))
# front band top edge: vertical gradient of luminance within the table, look for strongest negative change (bright top -> dark band)
L=cv2.cvtColor(cv2.imread('img/cx_48.png'),cv2.COLOR_BGR2GRAY).astype(float)
L=cv2.GaussianBlur(L,(1,5),0)
pts=[]
for x in range(240,1120,4):
    yb=int(np.polyval(back[0],x)) if False else None
    col=L[500:640,x]; d=np.diff(col)
    # expected near line from (210,539) to (1140,589)
    ye=539+(x-210)*(50/930.)
    lo=int(ye-12-500); hi=int(ye+12-500)
    k=lo+np.argmin(d[lo:hi]); pts.append((x,500+k+0.5))
front=fit(np.array(pts))
print('back',back,'left',left,'right',right,'front',front)
def inter(l1,l2):
    a1,b1=l1[0]; a2,b2=l2[0]; x=(b2-b1)/(a1-a2); return x,a1*x+b1
for n,(l1,l2) in {'BL':(back,left),'BR':(back,right),'FL':(front,left),'FR':(front,right)}.items():
    print(n, inter(l1,l2))
