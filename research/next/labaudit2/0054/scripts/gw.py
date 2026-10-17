from common import *
from tracks import *
from fit_a import fit, model, gd
# label-style: stated surface ranges at the clicked centres at capture 25 (video 24)
for cam,W,G,rW,rG in [('a',A_W[24],A_G_raw[24],3.0735,3.039),('b',B_W[24],B_G[24],1.235,1.331)]:
    d=np.linalg.norm(rW*ray(*W)-rG*ray(*G))
    dc=np.linalg.norm((rW+0.034)*ray(*W)-(rG+0.034)*ray(*G))
    lat=np.linalg.norm(ray(*W)-ray(*G))*(rW+rG)/2
    print(cam,'W',W,'G',G,'label-style dist=%.3f centres=%.3f lateral-only=%.3f'%(d,dc,lat))
# click jitter sensitivity: +-3 px each
rng=np.random.default_rng(0)
for cam,W,G,rW,rG in [('a',A_W[24],A_G_raw[24],3.0735,3.039),('b',B_W[24],B_G[24],1.235,1.331)]:
    ds=[np.linalg.norm(rW*ray(*(np.array(W)+rng.normal(0,3,2)))-rG*ray(*(np.array(G)+rng.normal(0,3,2)))) for _ in range(2000)]
    print(cam,'jitter 3px: median %.3f  p10 %.3f p90 %.3f'%(np.median(ds),np.percentile(ds,10),np.percentile(ds,90)))
# physical: from ballistic fits at t=1.0
for cam,trW,trG,ksW,ksG,g in [('a',A_W,A_G_raw,list(range(24,38)),list(range(24,37)),gd(0))]:
    pW,_=fit(trW,ksW,g); pG,_=fit(trG,ksG,g)
    print(cam,'fit centres dist at 1.0 s = %.3f'%np.linalg.norm(pW[:3]-pG[:3]))
db=np.load(OUT+'/b_down.npy')
pW,_=fit(B_W,list(range(24,39)),db); pG,_=fit(B_G,list(range(24,37)),db)
print('b fit centres dist at 1.0 s = %.3f'%np.linalg.norm(pW[:3]-pG[:3]))
