from common import *
from tracks import *
from fit_a import fit, model, gd, proj
dvp=np.load(OUT+'/b_down.npy')
def gr(p,r):
    p=np.radians(p); r=np.radians(r); return np.array([np.sin(r)*np.cos(p),np.cos(r)*np.cos(p),np.sin(p)])
for gname,g in [('vp',dvp),('r1',gr(29.9,-6.5))]:
  for name,tr,ks,kb in [('green',B_G,list(range(24,37)),37),('white',B_W,list(range(24,38)),38)]:
    p,rms=fit(tr,ks,g)
    C=lambda t: model(p,np.array([t]),1.0,g)[0]
    print(gname,name,'rms %.2f'%rms)
    for k in [35,36,37,38]:
        uv=proj(C(tcap(k))[None])[0]; print('   k=%d cap=%d pred=(%.1f,%.1f) obs=%s down=%.3f r=%.3f'%(k,cap(k),uv[0],uv[1],tr.get(k),C(tcap(k))@g,np.linalg.norm(C(tcap(k)))))
    if name=='green':
        C38=C(1.52); Vh=p[3:6]-(p[3:6]@g)*g
        d39=ray(*tr[37]); Ch=C38+Vh*0.04; s=Ch@d39; P39=s*d39
        print('   horiz-continuity r39=%.3f down39=%.3f (C38 down %.3f) v38-39=%.2f  v37-38=%.2f'%(s,P39@g,C38@g,np.linalg.norm(P39-C38)*25,np.linalg.norm(C(1.52)-C(1.48))*25))
