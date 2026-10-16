import numpy as np, json
vpv=np.array([452.6,1379.1])
def ray(u,v,f):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
def tc(n): return n/25 if n<=11 else ((n+1)/25 if n<=35 else (n+2)/25)
d=json.load(open('xcomps.json'))
cen={}
for n in range(48):
    b=[x for x in d[str(n)] if x['a']>4000 and not abs(x['cx']-986)<6][0]; cen[n]=(b['cx'],b['cy'])
for f in (711,730,760,800):
    dn=ray(*vpv,f); H=2.082*ray(666.4,617.9,f)@dn+0.018
    z=H-2.73*ray(*cen[10],f)@dn
    Pt={n:ray(*cen[n],f)*(H-z)/(ray(*cen[n],f)@dn) for n in cen}
    vfwd=np.linalg.norm(Pt[11]-Pt[10])/0.04
    # local linear fit n7..n13 (excluding none), velocity vector at t=0.4
    ns=list(range(6,15)); T=np.array([tc(n) for n in ns]); X=np.array([Pt[n] for n in ns])
    A=np.c_[np.ones(len(T)),T-0.4]; coef,*_=np.linalg.lstsq(A,X,rcond=None); vfit=np.linalg.norm(coef[1])
    disp=np.linalg.norm(Pt[34]-Pt[10])
    print(f,'v_fwd %.3f v_fit %.3f disp %.3f  ratio_fwd %.3f ratio_fit %.3f -> disp from prior: %.3f / %.3f'%(vfwd,vfit,disp,disp/vfwd,disp/vfit,0.9962*disp/vfwd,0.9962*disp/vfit))
