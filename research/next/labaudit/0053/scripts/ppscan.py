import numpy as np
pts=[('book',666.4,617.9,2.082,0.018),('cup',564.3,424.0,2.516,0.06),('ball',985.8,369.6,2.925,0.116),
     ('wb62',705.4,415.3,2.815,0.008),('bag62',837.3,329.1,3.307,0.01)]
vpv=np.array([452.6,1379.1]); vpc=np.array([2194.6,121.2]); vpj=np.array([219.5,-241.0])
res=[]
for f in (680,711,740,770):
  for cx in range(440,841,20):
    for cy in range(200,521,20):
        def ray(u,v):
            d=np.array([(u-cx)/f,(v-cy)/f,1.0]); return d/np.linalg.norm(d)
        dn=ray(*vpv)
        orth=abs(dn@ray(*vpc))+abs(dn@ray(*vpj))
        X=[]
        for nm,u,v,r,zz in pts:
            p=r*ray(u,v)
            if nm=='ball': p=p+0.116*ray(u,v)
            X.append(p)
        X=np.array(X); z=np.array([p[4] for p in pts])
        h=X@dn+z; H=h.mean(); rms=np.sqrt(((h-H)**2).mean())
        res.append((rms,orth,f,cx,cy,H))
res.sort()
for r in res[:12]: print('rms %.3f orth %.3f f %d cx %d cy %d H %.3f'%r)
print('centred f711:',[r for r in res if r[2]==711 and r[3]==640 and r[4]==360])
