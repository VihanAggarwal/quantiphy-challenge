from common import *
from tracks import *
from fit_a import fit, model, gd, proj
for name,tr,ks in [('white',A_W,list(range(24,38))),('green',A_G_raw,list(range(24,37)))]:
  for pitch in [0,1,2]:
    g=gd(pitch)
    p,rms=fit(tr,ks,g)
    print(name,'pitch',pitch,'rms %.2f'%rms)
    for k in range(33,41):
        t=tcap(k); C=model(p,np.array([t]),1.0,g)[0]; uv=proj(C[None])[0]
        h=C@g  # height-down coordinate
        obs=tr.get(k)
        print('  k=%d cap=%d pred=(%.1f,%.1f) obs=%s  down=%.3f  r=%.3f'%(k,cap(k),uv[0],uv[1],obs,h,np.linalg.norm(C)))
    # time when the 'down' coordinate reaches floor height H (unknown): print down at capture 37..40
