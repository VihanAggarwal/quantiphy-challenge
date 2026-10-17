import numpy as np, json
exec(open('fit3d.py').read().split("for name,imax in")[0])
def surf(u,v,rc,r): return ray(u,v)*(rc-r)
out={}
for name,imax in (('white',37),('green',36)):
  for ua in (True,False):
    s,I,J,uv,P=fit(name,imax,ua)
    rr=rad[name]
    tt=lambda j: np.array([(j-25)/25.])
    Pc=lambda j: traj(s.x,tt(j))[0]
    # physical speed at c37.5 and c38.5
    V=lambda j: s.x[3:6]+9.8*down*(j-25)/25.
    print('==',name,'anchor' if ua else 'free')
    for j in (37,37.5,38,38.5): print('   phys |v| at c%.1f = %.3f'%(j,np.linalg.norm(V(j))))
    # Label A: clicks at video36 (c38) & video37 (c39) with fitted range
    d={int(i):(u,v) for i,(u,v) in zip(I,uv)}
    u38,v38=d[36]
    S38=surf(u38,v38,np.linalg.norm(Pc(38)),rr)
    if name=='white':
        u39,v39=d[37]; S39=surf(u39,v39,np.linalg.norm(Pc(39)),rr)
        print('   A c38->c39 click+fit-range: %.3f m/s ; pure-fit centers: %.3f'%(np.linalg.norm(S39-S38)*25, np.linalg.norm(Pc(39)-Pc(38))*25))
    # Label B: c37 (interp from fit) -> c38
    S37=Pc(37)*(1-rr/np.linalg.norm(Pc(37)))
    print('   B c37->c38 fit c37 + click c38: %.3f ; pure-fit: %.3f'%(np.linalg.norm(S38-S37)*25,np.linalg.norm(Pc(38)-Pc(37))*25))
    # Also c36->c38 /2 (video 35->36), centred difference style
    u36,v36=d[35]; S36=surf(u36,v36,np.linalg.norm(Pc(36)),rr)
    print('   (c36->c38)/2 clicks: %.3f'%(np.linalg.norm(S38-S36)*25/2))
    out[(name,ua)]=s.x
np.save(OUT+'fitparams.npy',{str(k):v for k,v in out.items()},allow_pickle=True)
