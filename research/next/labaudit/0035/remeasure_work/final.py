"""Consolidated computation for qids 2644/2653/2662 (basketball displacement 0.4s->0.9s, camera 0035b)."""
import numpy as np
cx,cy,f=640,360,711.; R=0.116
def u(x,y):
    v=np.array([x-cx,y-cy,f]); return v/np.linalg.norm(v)
# ball centres measured (x render SAM2 mask ellipse centres; b render edge-fit agrees within 1px)
rest=(828.7,279.9)                       # frames 0-10, static
p09={21:(677.6,386.3),21.5:(672.35,391.65),21.6:(671.3,392.7),22:(667.1,397.0)}
u1=u(*rest); c1=u1[2]
# Route 1: apparent size, k calibrated on static basketballs in 0052x/0053x (ToF = front surface)
k_eqd=166.1; k_minor=166.75
r1_eqd=k_eqd/(54.7*c1**1.5)-R; r1_min=k_minor/(54.3*c1)-R
# Route 2: floor plane fitted to the four depth labels read as floor-behind ranges + baseboard orthogonality
n=np.array([0.144,0.815,0.562]); n/=np.linalg.norm(n); hf=1.681
r1_plane=(hf-R)/(n@u1)-R
print('rest surface range: size(eqd)=%.3f size(minor)=%.3f plane=%.3f'%(r1_eqd,r1_min,r1_plane))
fb1=hf/(n@u1)
for r1,name in [(r1_eqd,'S eqd'),(r1_min,'S minor'),(r1_plane,'S plane'),(fb1,'F floor-behind')]:
    print(name,'%.3f'%r1,' '.join('fr%.1f:%.1f'%(fr,100*np.linalg.norm(r1*u1-2.7777*u(*p))) for fr,p in p09.items()))
rc=(hf-R)/(n@u1)
print('physical centre-centre:',' '.join('fr%.1f:%.1f'%(fr,100*np.linalg.norm(rc*u1-(hf-R)/(n@u(*p))*u(*p))) for fr,p in p09.items()))
