from common import *
from tracks import *
from fit_a import fit, model, gd
db=np.load(OUT+'/b_down.npy')
def gr(p,r):
    p=np.radians(p); r=np.radians(r); return np.array([np.sin(r)*np.cos(p),np.cos(r)*np.cos(p),np.sin(p)])
R=0.0335
cases=[('a','W',A_W,list(range(24,38)),3.0735,[gd(0),gd(1),gd(2)]),('a','G',A_G_raw,list(range(24,37)),3.039,[gd(0),gd(1),gd(2)]),
       ('b','W',B_W,list(range(24,39)),1.235,[db,gr(29.9,-6.5)]),('b','G',B_G,list(range(24,37)),1.331,[db,gr(29.9,-6.5)])]
for cam,ball,tr,ks,rs,gs in cases:
    for g in gs:
        p,rms=fit(tr,ks,g)
        C=lambda t: model(p,np.array([t]),1.0,g)[0]
        r25=np.linalg.norm(C(1.0)); r26=np.linalg.norm(C(1.04)); r24=np.linalg.norm(C(0.96))
        # label-style A: stated at 25, fit-ratio-scaled surface range at 26, clicked (tracked) centres
        s=(rs)/(r25-R)
        P25=rs*ray(*tr[24]); P26=(r26-R)*s*ray(*tr[25])
        vA=np.linalg.norm(P26-P25)*25
        # B: stated at 25, unscaled fit surface range at 26
        P26b=(r26-R)*ray(*tr[25]); vB=np.linalg.norm(P26b-P25)*25
        # C: smooth physical fd from fit, and instantaneous
        vC=np.linalg.norm(C(1.04)-C(1.0))*25; vI=np.linalg.norm(p[3:6])
        # radial vs lateral split of the physical velocity at 1.0 s
        u=C(1.0)/r25; vr=p[3:6]@u
        print(f'{cam} {ball} g={np.round(g,3)} fit r25={r25:.3f} (stated+R {rs+R:.3f}) | label-style scaled={vA:.2f} unscaled={vB:.2f} | fd={vC:.2f} inst={vI:.2f} radial={vr:.2f}')
