import numpy as np
cx,cy=640,360; R=0.116
def u(x,y,f):
    v=np.array([x-cx,y-cy,f]); return v/np.linalg.norm(v)
def KT(l,f): return np.array([f*l[0],f*l[1],cx*l[0]+cy*l[1]+l[2]])
lL=np.array([0.5362,1,-517.84]); lR=np.array([-0.19881,1,-71.728])
labels=[('bb0.9',(671.3,392.7),2.7777),('bb1.4',(533.4,462.0),2.602),('so0.9',(611.7,480.6),2.477),('so1.4',(689.2,488.8),2.373)]
th=np.radians(np.linspace(1,89,441)); ph=np.radians(np.linspace(0,180,901))
TH,PH=np.meshgrid(th,ph,indexing='ij')
N=np.stack([np.sin(TH)*np.cos(PH),np.sin(TH)*np.sin(PH),np.cos(TH)],-1)
for f in [700.,711.,722.]:
    U=np.array([u(*p,f) for _,p,_ in labels]); L=np.array([l for *_,l in labels])
    # floor-behind: L_i = hf/(n.u_i)  -> hf_i = L_i*(n.u_i); best hf = mean; residual = spread
    D=N@U.T   # (...,4)
    H=D*L
    hf=H.mean(-1)
    rel=(H/hf[...,None]-1)
    cost_lab=(rel**2).mean(-1)
    a=KT(lL,f); b=KT(lR,f)
    dL=np.cross(np.broadcast_to(a,N.shape),N); dR=np.cross(np.broadcast_to(b,N.shape),N)
    r_orth=(dL*dR).sum(-1)/np.linalg.norm(dL,axis=-1)/np.linalg.norm(dR,axis=-1)
    u1=u(828.7,279.9,f)
    for wname,cost in [('labels only',cost_lab),('labels+orth',cost_lab+ (r_orth*0.05)**2)]:
        j=np.unravel_index(np.argmin(cost),cost.shape); n=N[j]; h=hf[j]
        rest_c=(h-R)/(n@u1); 
        # also distribution: take all normals with cost < 2x min
        ok=cost<max(2*cost[j],cost[j]+1e-5)
        rc_all=(hf[ok]-R)/(N[ok]@u1)
        print('f=%.0f %-12s n=%s hf=%.3f relres=%s orth=%.3f | rest centre=%.3f surf=%.3f  (range over near-opt normals: %.3f-%.3f)'%(f,wname,np.round(n,3),h,np.round(rel[j],4),r_orth[j],rest_c,rest_c-R,rc_all.min()-R,rc_all.max()-R))
