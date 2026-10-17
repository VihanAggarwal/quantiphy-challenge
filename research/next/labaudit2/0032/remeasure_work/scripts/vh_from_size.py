import numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/'
f=711.; cx=640.; cy=360.
for tag in ('a','ax'):
    C=np.load(base+'circ_%s.npy'%tag); C=C[C[:,0]>=36]
    u,v,r=C[:,1],C[:,2],C[:,3]
    # on-axis-equivalent size: r * (range/Z) ~ r*sqrt(1+((u-cx)/f)^2+((v-cy)/f)^2)
    lat=np.sqrt(1+((u-cx)/f)**2+((v-cy)/f)**2)
    for b in (0.0,0.5,1.0):
        y=(r-b/2)*lat
        A=np.c_[v,np.ones_like(v)]
        co,res,_,_=np.linalg.lstsq(A,y,rcond=None)
        vh=-co[1]/co[0]
        # bootstrap
        rng=np.random.default_rng(0); vs=[]
        for _ in range(2000):
            k=rng.integers(0,len(v),len(v))
            c2,_,_,_=np.linalg.lstsq(A[k],y[k],rcond=None); vs.append(-c2[1]/c2[0])
        print(tag,'diam bias %.1f px -> v_h = %.1f  (boot 16-84%%: %.1f..%.1f)'%(b,vh,*np.percentile(vs,[16,84])))
