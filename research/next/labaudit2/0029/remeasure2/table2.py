import cv2,numpy as np,json
def mask(fr): return cv2.imread(f'img/cx_{fr:02d}.png').astype(float).sum(2)>60
def topb(m,xs):
    pts=[]
    for x in xs:
        col=np.nonzero(m[300:700,x])[0]; pts.append((x, 300+col[0]-0.5))
    return np.array(pts,float)
def fit(p):
    A=np.c_[p[:,0],np.ones(len(p))]; sol=np.linalg.lstsq(A,p[:,1],rcond=None)[0]; r=p[:,1]-A@sol; return sol, r.std(), np.abs(r).max()
m0=mask(0); m48=mask(48); m24=mask(24)
back=fit(topb(m0,range(500,890,4)))
back24=fit(topb(m48,range(600,890,4)))
left=fit(topb(m0,range(225,425,4)))
right=fit(topb(m48,range(940,1120,4)))
L=cv2.cvtColor(cv2.imread('img/cx_48.png'),cv2.COLOR_BGR2GRAY).astype(float)
pts=[]
for x in range(240,1120,4):
    col=L[500:640,x]; d=np.diff(col); ye=539+(x-210)*(50/930.)
    lo=int(ye-12-500); hi=int(ye+12-500); k=lo+np.argmin(d[lo:hi]); pts.append((x,500+k+0.5))
front=fit(np.array(pts))
print('back',back,'back48',back24,'left',left,'right',right,'front',front)
def inter(l1,l2):
    a1,b1=l1[0]; a2,b2=l2[0]; x=(b2-b1)/(a1-a2); return [x,a1*x+b1]
C={n:inter(l1,l2) for n,(l1,l2) in {'BL':(back,left),'BR':(back,right),'FL':(front,left),'FR':(front,right)}.items()}
print(C); json.dump(C,open('corners.json','w'))
