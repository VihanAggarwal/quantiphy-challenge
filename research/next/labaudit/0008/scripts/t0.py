import numpy as np, cv2
f=711.; cx=640.; cy=360.; h=0.855; R=0.116
n=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0008/scripts/normal.npy')
def ray(p):
    r=np.array([p[0]-cx,p[1]-cy,f]); return r/np.linalg.norm(r)
Cc=(-(h-R)/(n@ray((577.5,418.0))))*ray((577.5,418.0))
def closest(p):
    r=ray(p); A=np.array([[n@n,-n@r],[n@r,-r@r]]); b=np.array([-(Cc@n),-(Cc@r)])
    s,t=np.linalg.solve(A,b); return s,t,np.linalg.norm(Cc+s*n-t*r)
for i,p in [(0,(526,97)),(10,(531,99)),(20,(530,99)),(22,(520,113)),(23,(523,131)),(24,(532,157))]:
    s,t,g=closest(p); print(f'frame {i} pix {p}: vertical-line centre height above desk {100*(s+R):.1f} cm, range {t:.3f}, miss {100*g:.1f} cm')
# ToF-style: t=0 ball depth from size ratio (as R4 did): w0=128 vs w24=119..129
for w0,w1 in [(128,119),(128,124),(128,129)]:
    for mode,add in [('surf',R),('asis',0)]:
        d0=(1.401+add)*w1/w0
        X=d0*ray((526,97)); print(f'  t=0 size-ratio w0={w0} w24={w1} {mode}: centre range {d0:.3f}, height {100*(n@X+h):.1f} cm')
