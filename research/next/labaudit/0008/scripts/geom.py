import numpy as np
f=711.; cx=640.; cy=360.
def ray(p):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/corners_captured_0008_10.npy')
BL,BR,FR,FL=C
def line(a,b): return np.cross([*a,1],[*b,1])
vpLR=np.cross(line(FL,BL),line(FR,BR)); vpBF=np.cross(line(BL,BR),line(FL,FR))
d1=np.array([vpLR[0]-cx*vpLR[2],vpLR[1]-cy*vpLR[2],f*vpLR[2]]); d1/=np.linalg.norm(d1)
d2=np.array([vpBF[0]-cx*vpBF[2],vpBF[1]-cy*vpBF[2],f*vpBF[2]]); d2/=np.linalg.norm(d2)
print('d1(depth dir)',d1,'d2(width dir)',d2,'cos',d1@d2)
n=np.cross(d1,d2); n/=np.linalg.norm(n)
if n[1]>0: n=-n   # normal pointing up (image y down => up is -y)
print('normal',n, 'tilt of camera axis vs plane: angle between optical axis and plane = %.1f deg'%np.degrees(np.arcsin(abs(n[2]))))
# plane: n.X = -h  (camera height h above plane along n)  -> points X = t*ray, n.(t ray) = -h
def onplane(p,h):
    r=ray(p); t=-h/(n@r); return t*r
for h in [1.0]:
    P=[onplane(c,h) for c in C]
    L=lambda a,b: np.linalg.norm(P[a]-P[b])
    print('h=1 sides back %.3f right %.3f front %.3f left %.3f diag %.3f %.3f'%(L(0,1),L(1,2),L(2,3),L(3,0),L(0,2),L(1,3)))
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy',n)
