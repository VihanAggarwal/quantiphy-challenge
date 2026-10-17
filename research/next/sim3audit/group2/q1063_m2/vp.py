import numpy as np
L=np.load('lsd_house.npy')
rng=np.random.default_rng(0)
def angres(v,S):
    # v homogeneous (3,) ; residual: signed sin angle * length-weight between segment direction and midpoint->vp
    mx,my=S[:,6],S[:,7]
    dx=v[0]-mx*v[2]; dy=v[1]-my*v[2]
    sx=S[:,2]-S[:,0]; sy=S[:,3]-S[:,1]
    n=np.hypot(dx,dy)*np.hypot(sx,sy)
    return (dx*sy-dy*sx)/n   # sin of angle
def fit(S,v0):
    w=np.sqrt(S[:,4])
    f=lambda p: angres(np.array([np.cos(p[0])*np.cos(p[1]),np.cos(p[0])*np.sin(p[1]),np.sin(p[0])/1000.]),S)*w
    # param on sphere
    v0=np.array([v0[0],v0[1],v0[2]*1000.]); v0=v0/np.linalg.norm(v0); p0=[np.arcsin(v0[2]),np.arctan2(v0[1],v0[0])]
    p=np.array(p0,float)
    for it in range(60):
        r0=f(p); J=np.zeros((len(r0),2)); h=1e-6
        for k in range(2):
            dp=np.zeros(2); dp[k]=h; J[:,k]=(f(p+dp)-r0)/h
        step=np.linalg.lstsq(J,-r0,rcond=None)[0]; p=p+step
        if np.abs(step).max()<1e-12: break
    v=np.array([np.cos(p[0])*np.cos(p[1]),np.cos(p[0])*np.sin(p[1]),np.sin(p[0])/1000.])
    return v
def ransac(S,v0,thr_deg=0.6,it=500):
    best=None
    lines=np.array([np.cross([r[0],r[1],1.],[r[2],r[3],1.]) for r in S])
    for _ in range(it):
        i,j=rng.choice(len(S),2,replace=False)
        v=np.cross(lines[i],lines[j])
        if np.linalg.norm(v)==0: continue
        res=np.degrees(np.abs(np.arcsin(np.clip(angres(v,S),-1,1))))
        inl=res<thr_deg; sc=S[inl,4].sum()
        if best is None or sc>best[0]: best=(sc,inl,v)
    inl=best[1]; v=fit(S[inl],best[2])
    res=np.degrees(np.abs(np.arcsin(np.clip(angres(v,S),-1,1)))); inl=res<thr_deg
    v=fit(S[inl],v)
    return v[:2]/v[2], inl
fa=L[(L[:,6]>1020)&(L[:,6]<1560)&(L[:,5]>-7)&(L[:,5]<4)&~((L[:,6]>1440)&(L[:,7]>1240))]
vA,iA=ransac(fa,np.array([-1800,1283,1.]))
print('VA',vA,iA.sum(),'/',len(fa))
sb=L[(L[:,5]>8)&(L[:,5]<22)&(L[:,6]>1480)&(L[:,7]<1110)]
vB,iB=ransac(sb,np.array([2500,1283,1.]))
print('VB',vB,iB.sum(),'/',len(sb))
vv=L[(np.abs(L[:,5])>80)&(L[:,6]<1800)]
vV,iV=ransac(vv,np.array([950,-12000,1.]),thr_deg=0.4)
print('VV',vV,iV.sum(),'/',len(vv))
p=np.array([960.,977.])
print('f(A,B|centre)=',np.sqrt(-np.dot(vA-p,vB-p)))
def orth(a,b,c):
    M=np.array([b-c,a-c]); r=np.array([a@(b-c), b@(a-c)]); return np.linalg.solve(M,r)
o=orth(vA,vB,vV); print('orthocentre',o,'f(A,B|orth)=',np.sqrt(-np.dot(vA-o,vB-o)))
print('f(A,V|c)=',np.sqrt(-np.dot(vA-p,vV-p)),'f(B,V|c)=',np.sqrt(-np.dot(vB-p,vV-p)))
# f from horizon & vertical VP: horizon line through vA,vB; distance from p to horizon d_h, to vV d_v: f^2 = d_h*d_v
n=np.array([-(vB[1]-vA[1]), vB[0]-vA[0]]); n/=np.linalg.norm(n)
dh=abs(np.dot(p-vA,n)); dv=abs(np.dot(vV-p,n)); print('f(horizon,V)=',np.sqrt(dh*dv),'horizon dist',dh)
# bootstrap
fs=[]
for b in range(200):
    a=fa[iA][rng.integers(0,iA.sum(),iA.sum())]; bb=sb[iB][rng.integers(0,iB.sum(),iB.sum())]
    try:
        va=fit(a,np.r_[vA,1]); vb=fit(bb,np.r_[vB,1]); va=va[:2]/va[2]; vb=vb[:2]/vb[2]
        fs.append(np.sqrt(-np.dot(va-p,vb-p)))
    except Exception as e: pass
print('bootstrap f(A,B)',np.percentile(fs,[5,50,95]))
np.save('vps.npy',np.array([vA,vB,vV]))
