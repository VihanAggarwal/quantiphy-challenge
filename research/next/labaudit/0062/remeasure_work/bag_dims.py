import numpy as np
cx=640.;cy=360.
C=np.load('bag_corners_trim.npy')
for nname in ['n_fit_711','n_cc']:
  for f in [711.,732.]:
    n=np.load(nname+'.npy')[:3]
    if nname=='n_fit_711' and f==732.: n=np.load('n_fit_free.npy')[:3]
    if nname=='n_cc' and f==732.: continue
    r=np.c_[(C[:,0]-cx)/f,(C[:,1]-cy)/f,np.ones(4)]; X=r/(r@n)[:,None]
    s=[np.linalg.norm(X[(k+1)%4]-X[k]) for k in range(4)]
    ang=[np.degrees(np.arccos(((X[(k+1)%4]-X[k])@(X[k-1]-X[k]))/np.linalg.norm(X[(k+1)%4]-X[k])/np.linalg.norm(X[k-1]-X[k]))) for k in range(4)]
    # bag centre (body) and range/h
    p=[np.r_[q,1] for q in C]; c=np.cross(np.cross(p[0],p[2]),np.cross(p[1],p[3])); c=c[:2]/c[2]
    rc=np.array([(c[0]-cx)/f,(c[1]-cy)/f,1.]); Xc=rc/(rc@n); rng=np.linalg.norm(Xc)
    hbag=3.307/rng
    # also the board-derived h
    print(nname,f,'sides LT,TR,RB,BL (h)',np.round(s,4),'angles',np.round(ang,1))
    print('   body centre px',np.round(c,1),'range/h',round(rng,4),'h_bag(range 3.307 at body centre, surface)=',round(hbag,4))
    for h in [hbag, 1.85, 1.90]:
        print('   h=%.3f: opening edge (TR/BL) %.1f / %.1f cm ; side edge (LT/RB) %.1f / %.1f cm'%(h,s[1]*h*100,s[3]*h*100,s[0]*h*100,s[2]*h*100))
