import numpy as np,sys
c=np.array([1280.,720.])
R=np.load('recon.npy',allow_pickle=True).item()
f=float(sys.argv[1]) if len(sys.argv)>1 else 3530.
fps=float(sys.argv[2]) if len(sys.argv)>2 else 24.
ref=24
for k,d in R.items():
    e=d['e'];n=d['n'];T=d['T']
    v=np.array([(e[0]-c[0])/f,(e[1]-c[1])/f,1.]); vh=v/np.linalg.norm(v)
    Vz=22.16*vh[2]/fps   # per frame
    # horizon through e, roll 0
    a=(e[1]-c[1])/f
    up=np.array([0,-1,a]); up/=np.linalg.norm(up)
    s=np.cross(vh,up); s/=np.linalg.norm(s)
    upo=np.cross(s,vh)
    # 3D at ref frame using fitted position: use observed position at ref
    x=T[:,ref]
    Z=Vz*(n+ref)
    P=np.stack([(x[:,0]-c[0])/f*Z,(x[:,1]-c[1])/f*Z,Z],1)
    fo=P@vh; la=P@s; hu=P@upo
    print(k,'f',f,'fps',fps,'Vz m/s',(Vz*fps).round(2),'fore extent',(fo.max()-fo.min()).round(2),'lat extent',(la.max()-la.min()).round(2),'up extent',(hu.max()-hu.min()).round(2))
    o=np.argsort(fo)
    print('  rearmost 5 (fore,lat,up,px):')
    for j in o[:5]: print('   ',fo[j].round(2),la[j].round(2),hu[j].round(2),x[j].round(0),'rms',d['rms'][j].round(2))
    print('  foremost 5:')
    for j in o[-5:]: print('   ',fo[j].round(2),la[j].round(2),hu[j].round(2),x[j].round(0),'rms',d['rms'][j].round(2))
    np.save(f'P3_{k}.npy',np.stack([fo,la,hu],1))
