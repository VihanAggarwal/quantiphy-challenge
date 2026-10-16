import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from geo import *
def bp(u,v,r): return ray(u,v)*r
Lp=(411.3,465.5); Fp=(644.4,575.4); Rp=(1140.5,489.3); Bp=(797.8,442.1)
for nm,(p1,p2) in {'L-F':(Lp,Fp),'L-R':(Lp,Rp)}.items():
    print(nm,'stated-depth dist %.1f'%(np.linalg.norm(bp(*p1,1.035)-bp(*p2,0.573))*100))
# points on table plane with range 0.573: along F->R edge and F->L edge
for t in np.linspace(0,1,21):
    P=np.array(Fp)+t*(np.array(Rp)-np.array(Fp)); X=on_plane(*P)
    if abs(np.linalg.norm(X)-0.573)<0.03: print('F->R t %.2f px %s range %.3f'%(t,np.round(P),np.linalg.norm(X)))
for t in np.linspace(0,1,21):
    P=np.array(Fp)+t*(np.array(Lp)-np.array(Fp)); X=on_plane(*P)
    if abs(np.linalg.norm(X)-0.573)<0.03: print('F->L t %.2f px %s range %.3f'%(t,np.round(P),np.linalg.norm(X)))
